import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from typing import Optional


ROOT = pathlib.Path(__file__).resolve().parents[1]


def executable_from_env_or_paths(name: str, candidates: list[str]) -> Optional[str]:
    configured = os.environ.get(name, "")
    if configured and pathlib.Path(configured).is_file():
        return configured
    for candidate in candidates:
        if pathlib.Path(candidate).is_file():
            return candidate
    return shutil.which(name.lower())


LLVM_CONFIG = executable_from_env_or_paths(
    "LLVM_CONFIG",
    [
        "/opt/homebrew/opt/llvm/bin/llvm-config",
        "/usr/local/opt/llvm/bin/llvm-config",
    ],
)
LLVM_CLANGXX = executable_from_env_or_paths(
    "CLANGXX",
    [
        "/opt/homebrew/opt/llvm/bin/clang++",
        "/usr/local/opt/llvm/bin/clang++",
    ],
)
CMAKE = shutil.which("cmake")
CLANG = shutil.which("clang")


@unittest.skipUnless(
    LLVM_CONFIG and LLVM_CLANGXX and CMAKE and CLANG,
    "Clang LibTooling test dependencies are unavailable",
)
class ClangFactsTests(unittest.TestCase):
    def test_pointer_increment_through_dereference_is_write(self):
        assert LLVM_CONFIG is not None
        assert LLVM_CLANGXX is not None
        assert CMAKE is not None
        assert CLANG is not None

        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir()
            (source_dir / "fixture.c").write_text(
                "int pointer_write(int *bit_count, unsigned char *buf) {\n"
                "  (*bit_count)++;\n"
                "  return buf[0];\n"
                "}\n",
                encoding="utf-8",
            )
            compdb = root / "compile_commands.json"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "generate_compile_commands.py"),
                    "--source-dir",
                    str(source_dir),
                    "--output",
                    str(compdb),
                    "--compiler",
                    CLANG,
                ],
                check=True,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            llvm_cmake = subprocess.run(
                [LLVM_CONFIG, "--cmakedir"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            ).stdout.strip()
            clang_cmake = str(pathlib.Path(llvm_cmake).parent / "clang")
            build_dir = root / "build"
            subprocess.run(
                [
                    CMAKE,
                    "-S",
                    str(ROOT / "tools"),
                    "-B",
                    str(build_dir),
                    "-DCMAKE_BUILD_TYPE=Release",
                    f"-DCMAKE_CXX_COMPILER={LLVM_CLANGXX}",
                    f"-DLLVM_DIR={llvm_cmake}",
                    f"-DClang_DIR={clang_cmake}",
                ],
                check=True,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            subprocess.run(
                [CMAKE, "--build", str(build_dir), "--target", "dsc-clang-facts"],
                check=True,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            raw_path = root / "facts.json"
            subprocess.run(
                [
                    str(build_dir / "dsc-clang-facts"),
                    "--compdb",
                    str(compdb),
                    "--output",
                    str(raw_path),
                    "--source-root",
                    str(source_dir),
                ],
                check=True,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            payload = json.loads(raw_path.read_text(encoding="utf-8"))
            function = next(
                item for item in payload["functions"] if item["name"] == "pointer_write"
            )
            modes = {
                item["name"]: item["mode"]
                for item in function["pointer_parameters"]
            }
            self.assertEqual(modes["bit_count"], "WRITES_THROUGH")
            self.assertEqual(modes["buf"], "READ_ONLY")


if __name__ == "__main__":
    unittest.main()
