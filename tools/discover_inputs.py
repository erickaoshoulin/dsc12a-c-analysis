#!/usr/bin/env python3
"""Discover and gate the local DSC 1.2a PDF and C model.

This tool only records provenance.  It never downloads an input and never
changes the discovered PDF or C model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
from typing import Any


REQUIRED_SOURCE_FILES = ("Makefile", "codec_main.c", "dsc_codec.c")
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "dsc-rs",
    "operator_bittrue",
    "node_modules",
    "target",
    "build",
    "out",
    "__pycache__",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--timeout", type=int, default=30)
    return parser.parse_args()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def run_command(command: list[str], timeout: int) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)
    return completed.returncode, completed.stdout


def find_pdfinfo() -> str | None:
    configured = os.environ.get("PDFINFO", "").strip()
    candidates = [
        pathlib.Path(configured).expanduser() if configured else None,
        pathlib.Path(shutil.which("pdfinfo")) if shutil.which("pdfinfo") else None,
        pathlib.Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdfinfo",
        pathlib.Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/bin/pdfinfo",
    ]
    for candidate in candidates:
        if candidate and candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def pdfinfo(path: pathlib.Path, timeout: int) -> tuple[dict[str, str], str]:
    tool = find_pdfinfo()
    if not tool:
        return {}, "pdfinfo is not installed"
    code, output = run_command([tool, str(path)], timeout)
    if code != 0:
        return {}, output.strip()
    metadata: dict[str, str] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, output


def pdf_gate(path: pathlib.Path, timeout: int) -> dict[str, Any]:
    metadata, raw = pdfinfo(path, timeout)
    title = metadata.get("Title", "")
    subject = metadata.get("Subject", "")
    keywords = metadata.get("Keywords", "")
    searchable = " ".join((title, subject, keywords)).lower()
    title_version = "1.2a" in title.lower()
    version_match = "1.2a" in searchable
    display_match = "display stream compression" in searchable
    title_display_match = "display stream compression" in title.lower()
    try:
        pages = int(metadata.get("Pages", "0"))
    except ValueError:
        pages = 0
    passed = bool(path.is_file() and version_match and display_match and pages == 145)
    return {
        "status": "PASS" if passed else "FAIL",
        "path": str(path),
        "sha256": sha256_file(path) if path.is_file() else "UNKNOWN",
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "pdfinfo": metadata,
        "gate": {
            "pages_145": pages == 145,
            "title_contains_version_1_2a": title_version,
            "metadata_contains_version_1_2a": version_match,
            "title_contains_display_stream_compression": title_display_match,
            "metadata_contains_display_stream_compression": display_match,
            "note": (
                "The official local PDF puts the display-stream phrase in Subject/Keywords."
                if display_match and not title_display_match
                else ""
            ),
        },
        "pdfinfo_raw": raw,
    }


def source_gate(source_dir: pathlib.Path) -> dict[str, Any]:
    files = {name: (source_dir / name).is_file() for name in REQUIRED_SOURCE_FILES}
    passed = source_dir.is_dir() and all(files.values())
    return {
        "status": "PASS" if passed else "FAIL",
        "path": str(source_dir),
        "required_files": files,
    }


def source_hashes(source_dir: pathlib.Path) -> list[dict[str, str]]:
    result = []
    for path in sorted(
        item
        for item in source_dir.rglob("*")
        if item.is_file() and (item.suffix in {".c", ".h"} or item.name == "Makefile")
    ):
        result.append(
            {
                "path": path.relative_to(source_dir).as_posix(),
                "sha256": sha256_file(path),
            }
        )
    return result


def git_info(path: pathlib.Path) -> dict[str, Any]:
    def git(*arguments: str) -> str:
        code, output = run_command(["git", "-C", str(path), *arguments], 30)
        return output.strip() if code == 0 else "UNKNOWN"

    return {
        "root": git("rev-parse", "--show-toplevel"),
        "remote_origin": git("remote", "get-url", "origin"),
        "commit": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "status_porcelain": git("status", "--short"),
    }


def bounded_walk(root: pathlib.Path, max_depth: int = 7):
    if not root.is_dir():
        return
    base_depth = len(root.parts)
    for current, directories, files in os.walk(root):
        current_path = pathlib.Path(current)
        depth = len(current_path.parts) - base_depth
        directories[:] = sorted(
            name for name in directories if name not in SKIP_DIRS and not name.startswith(".")
        )
        if depth >= max_depth:
            directories[:] = []
        yield current_path, directories, files


def mdfind_candidates(name: str, root: pathlib.Path, timeout: int) -> list[pathlib.Path]:
    if not shutil.which("mdfind") or not root.exists():
        return []
    code, output = run_command(
        ["mdfind", "-onlyin", str(root), f'kMDItemFSName == "{name}"c'], timeout
    )
    if code != 0:
        return []
    return [pathlib.Path(line.strip()) for line in output.splitlines() if line.strip()]


def search_roots(repo_root: pathlib.Path) -> list[pathlib.Path]:
    candidates = [repo_root.resolve().parent, pathlib.Path.home() / "Desktop", pathlib.Path.home() / "Downloads"]
    result = []
    for root in candidates:
        root = root.resolve()
        if root.is_dir() and root not in result:
            result.append(root)
    return result


def source_candidate_key(source_dir: pathlib.Path, repo_root: pathlib.Path) -> tuple[int, int, int, str]:
    """Prefer an externally versioned model over an ephemeral build copy."""
    model_root = source_dir.parent
    remote_code, remote = run_command(
        ["git", "-C", str(model_root), "remote", "get-url", "origin"], 30
    )
    has_git_provenance = remote_code == 0 and bool(remote.strip())
    repo_root = repo_root.resolve()
    repo_parent = repo_root.parent
    inside_repo_parent = (
        model_root == repo_parent or repo_parent in model_root.parents
    ) and not (model_root == repo_root or repo_root in model_root.parents)
    return (
        0 if has_git_provenance else 1,
        1 if inside_repo_parent else 0,
        len(source_dir.parts),
        str(source_dir),
    )


def discover_pdf(repo_root: pathlib.Path, timeout: int) -> tuple[pathlib.Path | None, list[str]]:
    explicit = os.environ.get("DSC_SPEC_PDF", "").strip()
    if explicit:
        path = pathlib.Path(explicit).expanduser().resolve()
        return (path if pdf_gate(path, timeout)["status"] == "PASS" else None), [str(path)]
    candidates: set[pathlib.Path] = set()
    for root in search_roots(repo_root):
        candidates.update(mdfind_candidates("DSC_v1.2a.pdf", root, timeout))
        for current, _, files in bounded_walk(root):
            if "DSC_v1.2a.pdf" in files:
                candidates.add((current / "DSC_v1.2a.pdf").resolve())
    gated = [path for path in candidates if pdf_gate(path, timeout)["status"] == "PASS"]
    gated.sort(key=lambda path: (len(path.parts), str(path)))
    return (gated[0] if gated else None), [str(path) for path in sorted(candidates)]


def discover_source(repo_root: pathlib.Path, timeout: int) -> tuple[pathlib.Path | None, list[str]]:
    explicit_source = os.environ.get("DSC_SOURCE_DIR", "").strip()
    explicit_root = os.environ.get("DSC_MODEL_ROOT", "").strip()
    if explicit_source:
        source = pathlib.Path(explicit_source).expanduser().resolve()
        return (source if source_gate(source)["status"] == "PASS" else None), [str(source)]
    if explicit_root:
        root = pathlib.Path(explicit_root).expanduser().resolve()
        source = root / "source"
        return (source if source_gate(source)["status"] == "PASS" else None), [str(source)]

    candidates: set[pathlib.Path] = set()
    for root in search_roots(repo_root):
        for path in mdfind_candidates("DSC_model_20210623", root, timeout):
            source = path / "source"
            if source_gate(source)["status"] == "PASS":
                candidates.add(source.resolve())
        for current, directories, _ in bounded_walk(root):
            if current.name == "DSC_model_20210623":
                source = current / "source"
                if source_gate(source)["status"] == "PASS":
                    candidates.add(source.resolve())
                directories[:] = []
    ordered = sorted(candidates, key=lambda path: source_candidate_key(path, repo_root))
    return (ordered[0] if ordered else None), [str(path) for path in ordered]


def build_manifest(repo_root: pathlib.Path, timeout: int) -> dict[str, Any]:
    pdf_path, pdf_candidates = discover_pdf(repo_root, timeout)
    source_path, source_candidates = discover_source(repo_root, timeout)
    manifest: dict[str, Any] = {
        "schema_version": 2,
        "status": "OK",
        "do_not_edit": True,
        "discovery": {
            "preference_order": [
                "DSC_SPEC_PDF / DSC_SOURCE_DIR / DSC_MODEL_ROOT",
                "mdfind",
                "bounded search under repo parent, ~/Desktop, ~/Downloads",
            ],
            "pdf_candidates": pdf_candidates,
            "source_candidates": source_candidates,
        },
    }
    if pdf_path is None:
        manifest["status"] = "SPEC_UNAVAILABLE"
        manifest["spec"] = {
            "status": "SPEC_UNAVAILABLE",
            "reason": "No local PDF passed the DSC 1.2a metadata/page gate",
        }
    else:
        manifest["spec"] = pdf_gate(pdf_path, timeout)
    if source_path is None:
        manifest["status"] = "SOURCE_UNAVAILABLE" if manifest["status"] == "OK" else manifest["status"]
        manifest["source"] = {
            "status": "SOURCE_UNAVAILABLE",
            "reason": "No local C model source passed the Makefile/codec_main.c/dsc_codec.c gate",
        }
    else:
        source_dir = source_path.resolve()
        model_root = source_dir.parent
        hashes = source_hashes(source_dir)
        manifest["source"] = {
            "status": "PASS",
            "source_dir": str(source_dir),
            "model_root": str(model_root),
            "gate": source_gate(source_dir),
            "git": git_info(model_root),
            "source_file_hashes": hashes,
            "source_hashes_sha256": canonical_hash(hashes),
            "bittrue_smoke_script": str(model_root / "bittrue_smoke" / "run_c_baseline.sh"),
            "bittrue_smoke_available": (model_root / "bittrue_smoke" / "run_c_baseline.sh").is_file(),
        }
    return manifest


def main() -> int:
    args = parse_args()
    manifest = build_manifest(args.repo_root.resolve(), args.timeout)
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output.resolve().write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if manifest["status"] != "OK":
        print(manifest["status"], file=sys.stderr)
        return 1
    print(
        "discovered DSC inputs: "
        + manifest["spec"]["path"]
        + " and "
        + manifest["source"]["source_dir"]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
