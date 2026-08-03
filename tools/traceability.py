#!/usr/bin/env python3
"""Generate deterministic DSC specification <-> C traceability artifacts.

The PDF reader is deliberately small and dependency-free.  It reads page
objects and Flate-compressed text streams, retaining only short headings and
reference anchors; the PDF itself is never copied into the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import struct
import subprocess
import zlib
from collections import Counter, defaultdict
from typing import Any
from urllib.parse import urlparse


MN_RE = re.compile(r"\bMN_[A-Z0-9_]+\b")
SECTION_RE = re.compile(r"\bSection\s*([0-9]+(?:\.[0-9]+)*)\b", re.I)
PAGE_RE = re.compile(r"\b(?:spec\s+)?P(?:age\s*)?(\d{1,3})\b", re.I)
TABLE_RE = re.compile(r"\bTable\s*([A-Z]?-?\d+(?:-\d+)?)\b", re.I)
FIGURE_RE = re.compile(r"\bFigure\s*([A-Z]?-?\d+(?:-\d+)?)\b", re.I)

# These files are host/input/output plumbing rather than codec datapath
# evidence.  Their comments and functions stay visible to the compiler facts,
# but are not allowed to create specification links or production-code
# orphans in this report.
EXCLUDED_SOURCE_BASENAMES = {
    "cmd_parse.c",
    "cmd_parse.h",
    "codec_main.c",
    "dpx.c",
    "dpx.h",
    "hdr_dpx.c",
    "hdr_dpx.h",
    "logging.c",
    "logging.h",
    "psnr.c",
    "psnr.h",
}

CONCEPT_ALIASES = {
    "csc": {"color", "space", "conversion"},
    "mmap": {"modified", "median", "adaptive", "prediction"},
    "bp": {"block", "prediction"},
    "mpp": {"midpoint", "prediction"},
    "ich": {"indexed", "color", "history"},
    "rc": {"rate", "control"},
    "vlc": {"entropy", "encoder", "coding"},
    "vld": {"entropy", "decoder", "coding"},
    "dsu": {"delta", "size", "unit"},
    "qp": {"quantization"},
    "qlevel": {"quantization"},
    "quant": {"quantization"},
    "iq": {"inverse", "quantization"},
    "recon": {"reconstruction"},
    "flatness": {"flatness"},
    "line": {"line"},
    "storage": {"storage"},
    "mux": {"multiplex"},
    "slice": {"slice"},
}

TRACEABILITY_STOPWORDS = {
    "and",
    "code",
    "data",
    "dsc",
    "for",
    "function",
    "functions",
    "get",
    "info",
    "input",
    "main",
    "model",
    "of",
    "output",
    "process",
    "read",
    "section",
    "set",
    "size",
    "spec",
    "table",
    "the",
    "to",
    "update",
    "use",
    "used",
    "value",
    "values",
    "with",
    "write",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-manifest", required=True, type=pathlib.Path)
    parser.add_argument("--raw", required=True, type=pathlib.Path)
    parser.add_argument("--candidates", required=True, type=pathlib.Path)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    parser.add_argument("--reviewed", required=True, type=pathlib.Path)
    parser.add_argument("--library-manifest", type=pathlib.Path)
    return parser.parse_args()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def compact_text(value: str, limit: int = 240) -> str:
    value = " ".join(value.replace("\x96", "-").split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def normalize_pdf_text(value: str) -> str:
    value = compact_text(value, 500)
    value = re.sub(r"^Section(?=\d)", "Section ", value)
    value = re.sub(r"^(\d+(?:\.\d+)*)(?=[A-Za-z])", r"\1 ", value)
    value = re.sub(r"^Table(?=[A-Z0-9])", "Table ", value)
    value = re.sub(r"^Figure(?=[A-Z0-9])", "Figure ", value)
    value = re.sub(r"\s+([,.;:)])", r"\1", value)
    value = re.sub(r"([(])\s+", r"\1", value)
    return value


class PdfTextExtractor:
    def __init__(self, path: pathlib.Path):
        self.data = path.read_bytes()
        self.objects: dict[int, bytes] = {}
        self.pages: list[tuple[int, int]] = []
        self._parse_objects()
        self._parse_pages()

    def _parse_objects(self) -> None:
        pattern = re.compile(rb"(\d+)\s+(\d+)\s+obj\s*(.*?)\s*endobj", re.S)
        for match in pattern.finditer(self.data):
            number = int(match.group(1))
            body = match.group(3)
            if b"stream" not in body:
                self.objects[number] = body
                continue
            header, stream = body.split(b"stream", 1)
            stream = stream.lstrip(b"\r\n")
            length_match = re.search(rb"/Length\s+(\d+)", header)
            if length_match:
                stream = stream[: int(length_match.group(1))]
            else:
                stream = stream.split(b"endstream", 1)[0]
            if b"/FlateDecode" in header:
                try:
                    stream = zlib.decompress(stream)
                except zlib.error:
                    stream = b""
            self.objects[number] = stream

    def _parse_pages(self) -> None:
        pattern = re.compile(rb"(\d+)\s+(\d+)\s+obj\s*(.*?)\s*endobj", re.S)
        for match in pattern.finditer(self.data):
            body = match.group(3)
            if b"/Type/Page" not in body or b"/Contents" not in body:
                continue
            content = re.search(rb"/Contents\s+(\d+)\s+\d+\s+R", body)
            if content:
                self.pages.append((int(match.group(1)), int(content.group(1))))

    @staticmethod
    def _literal(token: bytes) -> str:
        output = bytearray()
        depth = 1
        index = 1
        while index < len(token) - 1 and depth:
            char = token[index]
            if char == 92:
                index += 1
                if index >= len(token):
                    break
                char = token[index]
                escapes = {ord("n"): 10, ord("r"): 13, ord("t"): 9, ord("b"): 8, ord("f"): 12}
                if char in escapes:
                    output.append(escapes[char])
                elif char in (10, 13):
                    pass
                else:
                    output.append(char)
                index += 1
                continue
            if char == 40:
                depth += 1
            elif char == 41:
                depth -= 1
                if not depth:
                    break
            output.append(char)
            index += 1
        return output.decode("latin1", "replace")

    @classmethod
    def _strings_in_array(cls, value: bytes) -> list[str]:
        result = []
        index = 0
        while index < len(value):
            if value[index] == 40:
                start = index
                depth = 1
                index += 1
                while index < len(value) and depth:
                    if value[index] == 92:
                        index += 2
                        continue
                    if value[index] == 40:
                        depth += 1
                    elif value[index] == 41:
                        depth -= 1
                    index += 1
                result.append(cls._literal(value[start:index]))
            elif value[index] == 60 and index + 1 < len(value) and value[index + 1] != 60:
                end = value.find(b">", index + 1)
                if end < 0:
                    break
                raw = re.sub(rb"\s+", b"", value[index + 1 : end])
                try:
                    result.append(bytes.fromhex(raw.decode("ascii")).decode("latin1", "replace"))
                except (ValueError, UnicodeError):
                    pass
                index = end + 1
            else:
                index += 1
        return result

    @classmethod
    def text_operations(cls, content: bytes) -> list[str]:
        operations: list[str] = []
        array_spans = []
        for match in re.finditer(rb"\[(.*?)\]\s*TJ", content, re.S):
            array_spans.append(match.span())
            pieces = cls._strings_in_array(match.group(1))
            if pieces:
                operations.append(normalize_pdf_text("".join(pieces)))
        for match in re.finditer(rb"\((?:\\.|[^\\)])*\)\s*Tj", content, re.S):
            if any(start <= match.start() < end for start, end in array_spans):
                continue
            operations.append(normalize_pdf_text(cls._literal(match.group(0).split(b"Tj", 1)[0].rstrip())))
        return [item for item in operations if item]

    def page_operations(self, page: int) -> list[str]:
        if page < 1 or page > len(self.pages):
            return []
        _, content_object = self.pages[page - 1]
        return self.text_operations(self.objects.get(content_object, b""))


def ref_ids(text: str) -> dict[str, list[str]]:
    sections = sorted({match.group(1) for match in SECTION_RE.finditer(text)})
    pages = sorted({int(match.group(1)) for match in PAGE_RE.finditer(text)})
    tables = sorted({f"Table {match.group(1).upper()}" for match in TABLE_RE.finditer(text)})
    figures = sorted({f"Figure {match.group(1).upper()}" for match in FIGURE_RE.finditer(text)})
    return {"sections": sections, "pages": pages, "tables": tables, "figures": figures}


def heading_candidates(extractor: PdfTextExtractor) -> list[dict[str, Any]]:
    candidates: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    def valid_section(identifier: str) -> bool:
        parts = identifier.split(".")
        try:
            numbers = [int(part) for part in parts]
        except ValueError:
            return False
        # The numeric body of this specification is Sections 1 through 7.
        # This rejects dates, addresses, page-content numbers, and other text
        # that happens to begin with digits while retaining nested headings.
        return 1 <= numbers[0] <= 7 and len(numbers) <= 5

    for page in range(1, len(extractor.pages) + 1):
        for text in extractor.page_operations(page):
            text = normalize_pdf_text(text)
            section = re.match(r"^(?:Section\s*)?([0-9]+(?:\.[0-9]+)*)(?:\s+)(.+)$", text)
            table = re.match(r"^Table\s*([A-Z]?-?\d+(?:-\d+)?)(?::|\s+)(.*)$", text, re.I)
            figure = re.match(r"^Figure\s*([A-Z]?-?\d+(?:-\d+)?)(?::|\s+)(.*)$", text, re.I)
            if section and valid_section(section.group(1)):
                key = ("section", section.group(1))
                candidates[key].append({"kind": "section", "identifier": section.group(1), "title": compact_text(section.group(2)), "page": page, "raw": text})
            if table:
                key = ("table", table.group(1).upper())
                candidates[key].append({"kind": "table", "identifier": table.group(1).upper(), "title": compact_text(table.group(2)), "page": page, "raw": text})
            if figure:
                key = ("figure", figure.group(1).upper())
                candidates[key].append({"kind": "figure", "identifier": figure.group(1).upper(), "title": compact_text(figure.group(2)), "page": page, "raw": text})
    result = []
    for (kind, identifier), values in sorted(candidates.items()):
        threshold = 14 if kind == "section" else 10
        selected = next((value for value in values if value["page"] >= threshold), values[0])
        anchor = dict(selected)
        anchor["anchor_id"] = f"pdf:{kind}:{identifier}"
        anchor["references"] = ref_ids(anchor["raw"])
        anchor["mn_ids"] = sorted(set(MN_RE.findall(anchor["raw"])))
        anchor["short_anchor"] = compact_text(anchor["raw"], 180)
        anchor.pop("raw", None)
        result.append(anchor)
    for page in range(1, len(extractor.pages) + 1):
        result.append(
            {
                "anchor_id": f"pdf:page:{page:03d}",
                "kind": "page",
                "identifier": f"P{page}",
                "title": "",
                "page": page,
                "references": {"sections": [], "pages": [page], "tables": [], "figures": []},
                "mn_ids": [],
                "short_anchor": f"DSC 1.2a PDF page {page}",
            }
        )
    return sorted(result, key=lambda item: (item["page"], item["kind"], item["identifier"]))


def find_external_tool(name: str) -> str | None:
    """Find the runtime-provided Poppler utility used for PDF facts."""
    found = shutil.which(name)
    if found:
        return found
    runtime_root = pathlib.Path(
        "/Users/snow/.cache/codex-runtimes/codex-primary-runtime/dependencies"
    )
    candidates = [
        runtime_root / "bin" / "override" / name,
        runtime_root / "native" / "poppler" / "poppler" / "bin" / name,
    ]
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def run_pdf_tool(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    # Poppler's bundled fonts are not on the ordinary shell search path in the
    # Codex runtime.  Supplying them makes extraction/rendering deterministic.
    fontconfig = pathlib.Path(
        "/Users/snow/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/etc/fonts/fonts.conf"
    )
    if fontconfig.is_file():
        env["FONTCONFIG_FILE"] = str(fontconfig)
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=timeout,
        check=False,
    )


def parse_pdfinfo_output(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip().lower().replace(" ", "_")] = value.strip()
    return result


def valid_layout_section(identifier: str) -> bool:
    parts = identifier.split(".")
    try:
        numbers = [int(part) for part in parts]
    except ValueError:
        return False
    return bool(numbers) and 1 <= numbers[0] <= 7 and len(numbers) <= 5


def layout_heading(line: str) -> tuple[str, str] | None:
    value = normalize_pdf_text(line.strip())
    if not value or "Page " in value or value.startswith(("Table ", "Figure ")):
        return None
    annex = re.match(r"^([A-H])\s+(.+\((?:Normative|Informative)\))\s*$", value, re.I)
    if annex:
        return annex.group(1).upper(), compact_text(annex.group(2), 300)
    match = re.match(r"^(?:Section\s+)?([0-9]+(?:\.[0-9]+){0,4})\s+(.+?)\s*$", value)
    if not match or not valid_layout_section(match.group(1)):
        return None
    title = compact_text(match.group(2), 300)
    # Ordinary prose occasionally begins with a number.  A section heading is
    # short and title-like; this excludes numeric equations and table rows.
    if len(title) < 2 or len(title) > 180 or title.endswith((".", ";")):
        return None
    return match.group(1), title


def layout_table_or_figure(line: str) -> tuple[str, str, str] | None:
    value = normalize_pdf_text(line.strip())
    match = re.match(r"^(Table|Figure)\s*([A-Z]?-?\d+(?:-\d+)?)(?::|\s+)(.*)$", value, re.I)
    if not match:
        return None
    return match.group(1).lower(), match.group(2).upper(), compact_text(match.group(3), 240)


def layout_pdf_anchors(pages: list[str], pdfinfo: dict[str, str], pdf_path: pathlib.Path) -> list[dict[str, Any]]:
    """Build short anchors from pdftotext -layout output.

    Model-note anchors retain the exact section heading that precedes the note
    on that same PDF page.  No semantic similarity is used in this stage.
    """
    section_occurrences: dict[str, list[dict[str, Any]]] = defaultdict(list)
    table_occurrences: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    note_occurrences: list[dict[str, Any]] = []
    for page_number, page_text in enumerate(pages, start=1):
        current_heading: dict[str, Any] | None = None
        for line_number, raw_line in enumerate(page_text.splitlines(), start=1):
            line = raw_line.rstrip()
            heading = layout_heading(line)
            if heading:
                identifier, title = heading
                current_heading = {
                    "identifier": identifier,
                    "title": title,
                    "page": page_number,
                    "line": line_number,
                    "raw": normalize_pdf_text(line),
                }
                section_occurrences[identifier].append(dict(current_heading))
            table_or_figure = layout_table_or_figure(line)
            if table_or_figure:
                kind, identifier, title = table_or_figure
                table_occurrences[(kind, identifier)].append(
                    {
                        "kind": kind,
                        "identifier": identifier,
                        "title": title,
                        "page": page_number,
                        "line": line_number,
                        "raw": normalize_pdf_text(line),
                    }
                )
            model_notes = sorted(set(MN_RE.findall(line)))
            if model_notes:
                for mn_id in model_notes:
                    note_occurrences.append(
                        {
                            "identifier": mn_id,
                            "page": page_number,
                            "line": line_number,
                            "raw": normalize_pdf_text(line),
                            "section": dict(current_heading) if current_heading else None,
                        }
                    )

    def choose_occurrence(values: list[dict[str, Any]], threshold: int = 14) -> dict[str, Any]:
        return next((value for value in values if value["page"] >= threshold), values[0])

    anchors: list[dict[str, Any]] = []
    for identifier, values in sorted(section_occurrences.items()):
        selected = choose_occurrence(values)
        anchors.append(
            {
                "anchor_id": f"pdf:section:{identifier}",
                "kind": "section",
                "identifier": identifier,
                "title": selected["title"],
                "page": selected["page"],
                "references": ref_ids(selected["raw"]),
                "mn_ids": sorted(
                    {
                        note["identifier"]
                        for note in note_occurrences
                        if note["section"] and note["section"]["identifier"] == identifier
                    }
                ),
                "short_anchor": compact_text(selected["raw"], 180),
                "source": "pdftotext -layout",
            }
        )
    for (kind, identifier), values in sorted(table_occurrences.items()):
        selected = choose_occurrence(values, threshold=10)
        anchors.append(
            {
                "anchor_id": f"pdf:{kind}:{identifier}",
                "kind": kind,
                "identifier": identifier,
                "title": selected["title"],
                "page": selected["page"],
                "references": ref_ids(selected["raw"]),
                "mn_ids": sorted(set(MN_RE.findall(selected["raw"]))),
                "short_anchor": compact_text(selected["raw"], 180),
                "source": "pdftotext -layout",
            }
        )
    for occurrence in note_occurrences:
        section = occurrence["section"]
        section_id = section["identifier"] if section else None
        section_anchor_id = f"pdf:section:{section_id}" if section_id else None
        anchor = {
            "anchor_id": f"pdf:model-note:{occurrence['identifier']}:p{occurrence['page']:03d}",
            "kind": "model_note",
            "identifier": occurrence["identifier"],
            "title": section["title"] if section else "",
            "page": occurrence["page"],
            "line": occurrence["line"],
            "section_id": section_id,
            "section_anchor_id": section_anchor_id,
            "references": ref_ids(" ".join([occurrence["raw"], section["raw"] if section else ""])),
            "mn_ids": [occurrence["identifier"]],
            "short_anchor": compact_text(
                f"{section_id or 'unattached'} {section['title'] if section else ''}; {occurrence['raw']}",
                220,
            ),
            "source": "pdftotext -layout",
        }
        anchors.append(anchor)
    page_count = int(pdfinfo.get("pages", len(pages)) or len(pages))
    for page_number in range(1, page_count + 1):
        anchors.append(
            {
                "anchor_id": f"pdf:page:{page_number:03d}",
                "kind": "page",
                "identifier": f"P{page_number}",
                "title": "",
                "page": page_number,
                "references": {"sections": [], "pages": [page_number], "tables": [], "figures": []},
                "mn_ids": [],
                "short_anchor": f"DSC 1.2a PDF page {page_number}",
                "source": "pdftotext -layout",
            }
        )
    return sorted(anchors, key=lambda item: (item["page"], item["kind"], item["identifier"], item.get("line", 0)))


def extract_pdf_layout(pdf_path: pathlib.Path) -> dict[str, Any]:
    pdfinfo_tool = find_external_tool("pdfinfo")
    pdftotext_tool = find_external_tool("pdftotext")
    if not pdfinfo_tool or not pdftotext_tool:
        raise RuntimeError("pdfinfo and pdftotext are required for primary PDF extraction")
    info_result = run_pdf_tool([pdfinfo_tool, str(pdf_path)])
    if info_result.returncode != 0:
        raise RuntimeError(f"pdfinfo failed: {info_result.stderr.strip()}")
    text_result = run_pdf_tool([pdftotext_tool, "-layout", str(pdf_path), "-"])
    if text_result.returncode != 0:
        raise RuntimeError(f"pdftotext -layout failed: {text_result.stderr.strip()}")
    page_text = text_result.stdout.split("\f")
    while page_text and not page_text[-1].strip():
        page_text.pop()
    info = parse_pdfinfo_output(info_result.stdout)
    anchors = layout_pdf_anchors(page_text, info, pdf_path)
    return {
        "pdfinfo_tool": pdfinfo_tool,
        "pdftotext_tool": pdftotext_tool,
        "pdfinfo": info,
        "page_count": int(info.get("pages", len(page_text)) or len(page_text)),
        "text_pages": len(page_text),
        "anchors": anchors,
        "pdf_sha256": sha256_file(pdf_path),
    }


def resolve_source_path(value: pathlib.Path | str, source_dir: pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(value)
    return path.resolve() if path.is_absolute() else (source_dir / path).resolve()


def source_relative(path: pathlib.Path, source_dir: pathlib.Path) -> str:
    try:
        return resolve_source_path(path, source_dir).relative_to(source_dir.resolve()).as_posix()
    except ValueError:
        return path.name


def code_permalink(source_file: str, line: int, end_line: int, manifest: dict[str, Any]) -> str:
    source = manifest.get("source", {})
    git = source.get("git", {})
    remote = git.get("remote_origin", "")
    commit = git.get("commit", "UNKNOWN")
    source_dir = pathlib.Path(source.get("source_dir", source_file)).resolve()
    file_path = resolve_source_path(source_file, source_dir)
    git_root_value = git.get("root", "")
    git_root = pathlib.Path(git_root_value).resolve() if git_root_value else source_dir
    try:
        relative = file_path.relative_to(git_root).as_posix()
    except ValueError:
        relative = source_relative(file_path, source_dir)
    if remote.startswith("git@github.com:"):
        remote = "https://github.com/" + remote.split(":", 1)[1]
    remote = remote.removesuffix(".git")
    parsed = urlparse(remote)
    if parsed.netloc:
        base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    else:
        base = remote
    suffix = f"#L{line}" if end_line <= line else f"#L{line}-L{end_line}"
    return f"{base}/blob/{commit}/{relative}{suffix}"


def function_for_line(
    functions: list[dict[str, Any]], file_path: pathlib.Path, source_dir: pathlib.Path, line: int
) -> dict[str, Any] | None:
    matches = []
    for function in functions:
        if resolve_source_path(function.get("source_file", ""), source_dir) != file_path.resolve():
            continue
        start = function.get("line", 0)
        end = function.get("end_line", start)
        if start <= line <= max(start, end):
            matches.append(function)
    if matches:
        return sorted(matches, key=lambda item: (item.get("line", 0), item.get("clang_usr", "")))[-1]
    following = [
        function
        for function in functions
        if resolve_source_path(function.get("source_file", ""), source_dir) == file_path.resolve()
        and function.get("line", 0) >= line
        and function.get("line", 0) - line <= 40
    ]
    if following:
        return min(following, key=lambda item: (item.get("line", 0), item.get("clang_usr", "")))
    return None


def extract_c_comments(manifest: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    source_dir = pathlib.Path(manifest["source"]["source_dir"]).resolve()
    functions = [
        function
        for function in raw.get("functions", [])
        if function.get("source_file") and not function.get("source_file", "").startswith("<external>/")
    ]
    comments = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.suffix not in {".c", ".h"}:
            continue
        if path.name in EXCLUDED_SOURCE_BASENAMES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"//[^\n]*|/\*.*?\*/", text, re.S):
            value = compact_text(match.group(0))
            start_line = text.count("\n", 0, match.start()) + 1
            end_line = text.count("\n", 0, match.end()) + 1
            mn_ids = sorted(set(MN_RE.findall(value)))
            refs = ref_ids(value)
            if not mn_ids and not any(refs.values()) and not value.startswith(("//!", "/*!", "/**", "///<")):
                continue
            function = function_for_line(functions, path, source_dir, start_line)
            comments.append(
                {
                    "comment_id": f"comment:{source_relative(path, source_dir)}:{start_line}",
                    "file": source_relative(path, source_dir),
                    "source_file": str(path),
                    "line": start_line,
                    "end_line": end_line,
                    "text": value,
                    "mn_ids": mn_ids,
                    "spec_refs": refs,
                    "function": function.get("name") if function else None,
                    "clang_usr": function.get("clang_usr") if function else None,
                    "permalink": code_permalink(str(path), start_line, end_line, manifest),
                }
            )
    tables = []
    for global_decl in raw.get("global_declarations", []):
        if not global_decl.get("is_array", global_decl.get("array_size") is not None):
            continue
        tables.append(
            {
                "name": global_decl.get("name", "UNKNOWN"),
                "type": global_decl.get("type", "UNKNOWN"),
                "file": source_relative(pathlib.Path(global_decl.get("source_file", "")), source_dir),
                "line": global_decl.get("line", 0),
                "array_size": global_decl.get("array_size"),
                "constant_values": global_decl.get("constant_values", []),
                "permalink": code_permalink(global_decl.get("source_file", ""), global_decl.get("line", 0), global_decl.get("line", 0), manifest),
            }
        )
    code_anchors = []
    for function in sorted(functions, key=lambda item: (item.get("name", ""), item.get("source_file", ""), item.get("line", 0), item.get("clang_usr", ""))):
        if pathlib.Path(function.get("source_file", "")).name in EXCLUDED_SOURCE_BASENAMES:
            continue
        code_anchors.append(
            {
                "code_anchor_id": f"code:function:{function.get('clang_usr', 'UNKNOWN')}",
                "kind": "function",
                "function": function.get("name", "UNKNOWN"),
                "clang_usr": function.get("clang_usr", "UNKNOWN"),
                "file": source_relative(pathlib.Path(function.get("source_file", "")), source_dir),
                "line": function.get("line", 0),
                "end_line": function.get("end_line", function.get("line", 0)),
                "permalink": code_permalink(function.get("source_file", ""), function.get("line", 0), function.get("end_line", function.get("line", 0)), manifest),
            }
        )
    return {"schema_version": 2, "do_not_edit": True, "comments": comments, "tables": tables, "code_anchors": code_anchors}


def tokens(value: str) -> set[str]:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    result = {item.lower() for item in re.findall(r"[A-Za-z][A-Za-z0-9]+", value)}
    for token in list(result):
        result.update(CONCEPT_ALIASES.get(token, set()))
    return result - TRACEABILITY_STOPWORDS - {"mn", "note", "figure"}


def link_key(link: dict[str, Any]) -> tuple[str, str]:
    return link.get("spec_anchor_id", ""), link.get("code_anchor_id", "")


def proposal_links(
    anchors: list[dict[str, Any]], comments: dict[str, Any], candidates: dict[str, Any], manifest: dict[str, Any]
) -> list[dict[str, Any]]:
    by_mn: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_identifier: dict[str, dict[str, Any]] = {}
    for anchor in anchors:
        identifier = str(anchor.get("identifier", "")).lower()
        if not identifier:
            continue
        by_identifier[identifier] = anchor
        if anchor.get("kind") in {"section", "table", "figure"}:
            by_identifier[f"{anchor['kind']}{identifier}".lower()] = anchor
        if anchor.get("kind") == "page":
            by_identifier[f"page{anchor['page']}".lower()] = anchor
            by_identifier[f"p{anchor['page']}".lower()] = anchor
    for anchor in anchors:
        for mn_id in anchor.get("mn_ids", []):
            by_mn[mn_id].append(anchor)
    function_by_usr = {anchor["clang_usr"]: anchor for anchor in comments["code_anchors"]}
    source_sha = manifest.get("source", {}).get("source_hashes_sha256", "UNKNOWN")
    pdf_sha = manifest.get("spec", {}).get("sha256", "UNKNOWN")
    links = []
    seen: set[tuple[str, str]] = set()

    def add(anchor: dict[str, Any], code: dict[str, Any], status: str, method: str, evidence: str) -> None:
        key = (anchor["anchor_id"], code["code_anchor_id"])
        if key in seen:
            return
        seen.add(key)
        links.append(
            {
                "link_id": f"link-{len(links) + 1:04d}",
                "status": status,
                "method": method,
                "evidence": evidence,
                "spec_anchor_id": anchor["anchor_id"],
                "spec_page": anchor["page"],
                "spec_section": anchor.get("section_id")
                if anchor.get("kind") == "model_note"
                else anchor["identifier"] if anchor["kind"] == "section" else None,
                "spec_sha256": pdf_sha,
                "code_anchor_id": code["code_anchor_id"],
                "function": code["function"],
                "clang_usr": code["clang_usr"],
                "code_file": code["file"],
                "code_line": code["line"],
                "code_permalink": code["permalink"],
                "source_hashes_sha256": source_sha,
            }
        )

    for comment in comments["comments"]:
        code = function_by_usr.get(comment.get("clang_usr"))
        if not code:
            continue
        matched = False
        for mn_id in comment.get("mn_ids", []):
            for anchor in by_mn.get(mn_id, []):
                add(anchor, code, "EXACT", "exact_mn_id", f"C comment and PDF anchor both contain {mn_id}")
                matched = True
        refs = comment.get("spec_refs", {})
        identifiers = [
            *[value.lower() for value in refs.get("sections", [])],
            *[f"section{value}".lower() for value in refs.get("sections", [])],
            *[value.lower().replace(" ", "") for value in refs.get("tables", [])],
            *[f"table{value}".lower().replace(" ", "") for value in refs.get("tables", [])],
            *[value.lower().replace(" ", "") for value in refs.get("figures", [])],
            *[f"figure{value}".lower().replace(" ", "") for value in refs.get("figures", [])],
            *[f"p{value}" for value in refs.get("pages", [])],
            *[f"page{value}" for value in refs.get("pages", [])],
        ]
        for identifier in identifiers:
            for key, anchor in by_identifier.items():
                if key == identifier or key.replace(" ", "") == identifier:
                    add(anchor, code, "EXACT", "explicit_c_reference", f"C comment explicitly references {identifier}")
                    matched = True
        if matched:
            continue
        # An unannotated C comment is not a reliable specification claim. Keep
        # it in comments.json, but do not turn coincidental prose overlap into
        # a traceability proposal.
        if not comment.get("mn_ids"):
            continue
        query = tokens(" ".join([comment.get("text", ""), comment.get("function") or "", *comment.get("mn_ids", [])]))
        scored = []
        for anchor in anchors:
            if anchor["kind"] == "page":
                continue
            overlap = query & tokens(" ".join([anchor.get("identifier", ""), anchor.get("title", "")]))
            if len(overlap) >= 2:
                scored.append((len(overlap), anchor["page"], anchor["anchor_id"], anchor, overlap))
        if scored:
            _, _, _, anchor, overlap = sorted(scored, key=lambda item: (-item[0], item[1], item[2]))[0]
            add(anchor, code, "PROPOSED", "normalized_concept_heuristic", "Shared normalized concept tokens: " + ", ".join(sorted(overlap)))

    for candidate in candidates.get("ranked_candidates", []):
        if not candidate.get("production_reachable"):
            continue
        code = function_by_usr.get(candidate.get("clang_usr"))
        if not code or any(link["code_anchor_id"] == code["code_anchor_id"] for link in links):
            continue
        query = tokens(candidate.get("name", ""))
        scored = []
        for anchor in anchors:
            if anchor["kind"] == "page":
                continue
            overlap = query & tokens(" ".join([anchor.get("identifier", ""), anchor.get("title", "")]))
            if len(overlap) >= 2:
                scored.append((len(overlap), anchor["page"], anchor["anchor_id"], anchor, overlap))
        if scored:
            _, _, _, anchor, overlap = sorted(scored, key=lambda item: (-item[0], item[1], item[2]))[0]
            add(anchor, code, "PROPOSED", "normalized_function_identifier", "Shared normalized identifier tokens: " + ", ".join(sorted(overlap)))
    return links


def parse_reviewed(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    links = []
    current: dict[str, str] | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("-"):
            if current:
                links.append(current)
            current = {}
            stripped = stripped[1:].strip()
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        value = value.strip().strip('"').strip("'")
        current[key.strip()] = value
    if current:
        links.append(current)
    return links


def apply_reviewed(
    links: list[dict[str, Any]],
    reviewed: list[dict[str, str]],
    manifest: dict[str, Any],
    anchors: list[dict[str, Any]] | None = None,
    code_anchors: list[dict[str, Any]] | None = None,
    raw_functions: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    by_key = {(item.get("spec_anchor_id", ""), item.get("code_anchor_id", "")): item for item in reviewed}
    pdf_sha = manifest.get("spec", {}).get("sha256", "UNKNOWN")
    source_sha = manifest.get("source", {}).get("source_hashes_sha256", "UNKNOWN")
    for link in links:
        review = by_key.get(link_key(link))
        if not review:
            continue
        if review.get("spec_sha256", pdf_sha) != pdf_sha or review.get("source_hashes_sha256", source_sha) != source_sha:
            link["status"] = "STALE"
            link["review_note"] = "Reviewed link provenance hashes no longer match current inputs"
        else:
            link["status"] = "REVIEWED"
            link["review_note"] = review.get("note", "human-reviewed")

    # A reviewed exact reference may be intentionally absent from the
    # heuristic proposal set (for example, a normative helper definition whose
    # C comment has no MN tag).  Materialize it here only when the reviewed
    # entry names an existing PDF anchor and an existing Clang code anchor.
    # This keeps the review surface data-driven without turning it into a
    # function selection list.
    anchor_by_id = {str(item.get("anchor_id")): item for item in (anchors or [])}
    code_by_id = {str(item.get("code_anchor_id")): item for item in (code_anchors or [])}
    # Some source files are intentionally excluded from heuristic
    # traceability (for example host/configuration plumbing).  A reviewed
    # exact link may still name one of those functions when it is a real
    # reusable, spec-defined library boundary.  Resolve that identity from
    # the immutable Clang facts rather than turning the reviewed file into a
    # function selector or broadening heuristic proposals.
    source_dir = pathlib.Path(manifest.get("source", {}).get("source_dir", "."))
    for function in raw_functions or []:
        code_id = f"code:function:{function.get('clang_usr', '')}"
        if not function.get("clang_usr") or code_id in code_by_id:
            continue
        source_file = str(function.get("source_file", ""))
        line = int(function.get("line", 0) or 0)
        end_line = int(function.get("end_line", line) or line)
        code_by_id[code_id] = {
            "code_anchor_id": code_id,
            "kind": "function",
            "function": function.get("name", "UNKNOWN"),
            "clang_usr": function.get("clang_usr", "UNKNOWN"),
            "file": source_relative(pathlib.Path(source_file), source_dir),
            "line": line,
            "end_line": end_line,
            "permalink": code_permalink(source_file, line, end_line, manifest),
        }
    existing = {link_key(link) for link in links}
    for review in reviewed:
        key = (review.get("spec_anchor_id", ""), review.get("code_anchor_id", ""))
        if key in existing or not key[0] or not key[1]:
            continue
        anchor = anchor_by_id.get(key[0])
        code = code_by_id.get(key[1])
        if not anchor or not code:
            continue
        status = (
            "REVIEWED"
            if review.get("spec_sha256", pdf_sha) == pdf_sha
            and review.get("source_hashes_sha256", source_sha) == source_sha
            else "STALE"
        )
        links.append(
            {
                "link_id": review.get("link_id") or f"reviewed-{len(links) + 1:04d}",
                "status": status,
                "method": review.get("method", "reviewed_exact_spec"),
                "evidence": review.get("evidence") or review.get("note", "human-reviewed exact specification reference"),
                "spec_anchor_id": anchor["anchor_id"],
                "spec_page": anchor["page"],
                "spec_section": anchor.get("section_id")
                if anchor.get("kind") == "model_note"
                else anchor["identifier"] if anchor.get("kind") == "section" else None,
                "spec_sha256": pdf_sha,
                "code_anchor_id": code["code_anchor_id"],
                "function": code["function"],
                "clang_usr": code["clang_usr"],
                "code_file": code["file"],
                "code_line": code["line"],
                "code_permalink": code["permalink"],
                "source_hashes_sha256": source_sha,
                "review_note": review.get("note", "human-reviewed"),
            }
        )
        existing.add(key)
    return links


def apply_library_links(
    links: list[dict[str, Any]],
    library_manifest_path: pathlib.Path | None,
    output_dir: pathlib.Path,
    anchors: list[dict[str, Any]],
    code_anchors: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Project accepted library spec links into generated traceability.

    A PASS library component is already a reviewed, content-addressed
    contract.  Reusing its EXACT_SPEC links reduces duplicate human review,
    but this projection is never a selector: it only joins an existing
    accepted contract to an existing Clang code anchor and an existing PDF
    anchor.  Stale or malformed library inputs are reported and ignored.
    """
    audit: dict[str, Any] = {
        "schema_version": 1,
        "status": "NOT_CONFIGURED",
        "manifest": str(library_manifest_path) if library_manifest_path else None,
        "manifest_sha256": None,
        "components_seen": 0,
        "components_eligible": 0,
        "links_added": 0,
        "skipped": {},
    }
    if library_manifest_path is None or not library_manifest_path.is_file():
        return links, audit

    try:
        library = json.loads(library_manifest_path.read_text(encoding="utf-8"))
        audit["manifest_sha256"] = sha256_file(library_manifest_path)
    except (OSError, json.JSONDecodeError):
        audit["status"] = "INVALID"
        audit["skipped"] = {"invalid_manifest": 1}
        return links, audit
    if not isinstance(library, dict):
        audit["status"] = "INVALID"
        audit["skipped"] = {"invalid_manifest_shape": 1}
        return links, audit

    spec_sha = manifest.get("spec", {}).get("sha256", "UNKNOWN")
    source_sha = manifest.get("source", {}).get("source_hashes_sha256", "UNKNOWN")
    if library.get("spec_hash") != spec_sha or library.get("source_hash") != source_sha:
        audit["status"] = "STALE_INPUT"
        audit["skipped"] = {"library_input_hash_mismatch": 1}
        return links, audit

    components = library.get("components") if isinstance(library.get("components"), list) else []
    audit["status"] = "PASS"
    audit["components_seen"] = len(components)
    anchor_by_id = {
        str(item.get("anchor_id")): item
        for item in anchors
        if isinstance(item, dict) and item.get("anchor_id")
    }
    code_by_usr = {
        str(item.get("clang_usr")): item
        for item in code_anchors
        if isinstance(item, dict) and item.get("clang_usr")
    }
    existing = {link_key(link) for link in links}
    skipped: Counter[str] = Counter()
    added: list[dict[str, Any]] = []

    def component_sort_key(item: Any) -> str:
        return str(item.get("contract_id", "")) if isinstance(item, dict) else ""

    for component in sorted(components, key=component_sort_key):
        if not isinstance(component, dict):
            skipped["invalid_component"] += 1
            continue
        if component.get("status") != "PASS":
            skipped["component_not_pass"] += 1
            continue
        if component.get("authority") != "EXACT_SPEC":
            skipped["component_not_exact_spec"] += 1
            continue
        contract_id = str(component.get("contract_id", ""))
        if not contract_id:
            skipped["component_missing_id"] += 1
            continue
        contract_hash = str(component.get("contract_hash", ""))
        if not contract_hash:
            skipped["component_missing_hash"] += 1
            continue
        audit["components_eligible"] += 1
        contract_paths = [
            library_manifest_path.parent / "contracts" / f"{contract_id}.json",
            output_dir / "library" / "contracts" / f"{contract_id}.json",
        ]
        contract_file = component.get("contract_file")
        if contract_file:
            contract_paths.append(output_dir / str(contract_file))
        contract_path = next((path for path in contract_paths if path.is_file()), None)
        if contract_path is None:
            skipped["contract_file_missing"] += 1
            continue
        try:
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            skipped["contract_file_invalid"] += 1
            continue
        if not isinstance(contract, dict) or contract.get("contract_id") != contract_id:
            skipped["contract_identity_mismatch"] += 1
            continue
        function = contract.get("function") if isinstance(contract.get("function"), dict) else {}
        clang_usr = str(function.get("clang_usr", ""))
        code = code_by_usr.get(clang_usr)
        if not code:
            skipped["code_anchor_missing"] += 1
            continue
        spec_links = contract.get("spec_links") if isinstance(contract.get("spec_links"), list) else []
        component_added = 0
        for spec_link in spec_links:
            if not isinstance(spec_link, dict) or spec_link.get("status") != "EXACT":
                skipped["spec_link_not_exact"] += 1
                continue
            spec_anchor_id = str(spec_link.get("anchor_id", ""))
            anchor = anchor_by_id.get(spec_anchor_id)
            if not anchor:
                skipped["spec_anchor_missing"] += 1
                continue
            key = (spec_anchor_id, str(code.get("code_anchor_id", "")))
            if key in existing:
                skipped["duplicate_link"] += 1
                continue
            link = {
                "link_id": f"library-{contract_id}-{spec_anchor_id.replace(':', '-')}",
                "status": "REVIEWED",
                "method": "accepted_library_exact_spec",
                "evidence": (
                    f"Accepted PASS library component {contract_id} carries an EXACT_SPEC "
                    f"link to {spec_anchor_id}"
                ),
                "spec_anchor_id": spec_anchor_id,
                "spec_page": anchor.get("page", spec_link.get("page")),
                "spec_section": anchor.get("section_id")
                if anchor.get("kind") == "model_note"
                else anchor.get("identifier") if anchor.get("kind") == "section" else None,
                "spec_sha256": spec_sha,
                "code_anchor_id": code.get("code_anchor_id"),
                "function": code.get("function"),
                "clang_usr": clang_usr,
                "code_file": code.get("file"),
                "code_line": code.get("line"),
                "code_permalink": code.get("permalink"),
                "source_hashes_sha256": source_sha,
                "review_note": "Projected from accepted PASS library contract; human promotion already approved the contract.",
                "library_contract_id": contract_id,
                "library_contract_hash": contract_hash,
                "library_manifest_sha256": audit["manifest_sha256"],
            }
            links.append(link)
            added.append(link)
            existing.add(key)
            component_added += 1
        if component_added == 0:
            skipped["component_no_new_links"] += 1

    audit["links_added"] = len(added)
    audit["skipped"] = dict(sorted(skipped.items()))
    return links, audit


def _comment_view(comment: dict[str, Any]) -> dict[str, Any]:
    refs = comment.get("spec_refs") if isinstance(comment.get("spec_refs"), dict) else {}
    return {
        "comment_id": comment.get("comment_id"),
        "file": comment.get("file"),
        "line": comment.get("line"),
        "end_line": comment.get("end_line"),
        "function": comment.get("function"),
        "mn_ids": sorted(str(value) for value in comment.get("mn_ids", []) if value),
        "spec_refs": {
            key: sorted(value for value in refs.get(key, []) if value is not None)
            for key in ("sections", "tables", "figures", "pages")
            if refs.get(key)
        },
        "text": compact_text(str(comment.get("text", "")), 240),
        "permalink": comment.get("permalink"),
    }


def _candidate_view(candidate: dict[str, Any] | None, rank: int | None) -> dict[str, Any] | None:
    if not candidate:
        return None
    return {
        "rank": rank,
        "score": candidate.get("score"),
        "confidence": candidate.get("confidence"),
        "eligible": candidate.get("eligible"),
        "production_reachable": candidate.get("production_reachable"),
        "contributes_to_observable_output": candidate.get("contributes_to_observable_output"),
        "bounded_computation": candidate.get("bounded_computation"),
        "purity": candidate.get("purity"),
        "timing": candidate.get("timing"),
        "role": candidate.get("role"),
        "direct_effects": candidate.get("direct_effects", {}),
        "transitive_effects": candidate.get("transitive_effects", {}),
        "evidence": [str(value) for value in candidate.get("evidence", [])],
    }


def _coverage_view(coverage: dict[str, Any] | None) -> dict[str, Any] | None:
    if not coverage:
        return None
    details = coverage.get("coverage") if isinstance(coverage.get("coverage"), dict) else {}
    return {
        "status": coverage.get("coverage_status"),
        "eligible_after_coverage": coverage.get("eligible_after_coverage"),
        "execution_count": details.get("execution_count"),
        "line_coverage_percent": details.get("line_coverage_percent"),
        "branch_coverage_percent": details.get("branch_coverage_percent"),
        "region_coverage_percent": details.get("region_coverage_percent"),
        "profile": coverage.get("profile"),
    }


def _raw_function_view(function: dict[str, Any] | None) -> dict[str, Any] | None:
    if not function:
        return None
    proposal = function.get("proposal") if isinstance(function.get("proposal"), dict) else {}
    fields_write = function.get("fields_write") if isinstance(function.get("fields_write"), list) else []
    return {
        "return_type": function.get("return_type"),
        "parameter_count": len(function.get("parameters", [])),
        "pointer_modes": [
            item.get("mode")
            for item in function.get("pointer_parameters", [])
            if isinstance(item, dict) and item.get("mode")
        ],
        "callers": sorted({str(item.get("name")) for item in function.get("callers", []) if isinstance(item, dict) and item.get("name")}),
        "callees": sorted({str(item.get("name")) for item in function.get("callees", []) if isinstance(item, dict) and item.get("name")}),
        "loop_count": function.get("loop_count", len(function.get("loops", []))),
        "unknown_facts": [str(value) for value in function.get("unknown_facts", [])],
        "proposal_category": proposal.get("category_proposal"),
        "static_mutable_state": sorted({str(value) for value in function.get("static_mutable_state", [])}),
        "fields_written": sorted({str(item.get("name")) for item in fields_write if isinstance(item, dict) and item.get("name")}),
        "effects": function.get("effects", {}),
    }


def _code_orphan_action(
    candidate: dict[str, Any] | None,
    coverage: dict[str, Any] | None,
    comments: list[dict[str, Any]],
) -> tuple[str, str]:
    direct_ref_values: set[str] = set()
    for comment in comments:
        direct_ref_values.update(str(value) for value in comment.get("mn_ids", []) if value)
        refs = comment.get("spec_refs") if isinstance(comment.get("spec_refs"), dict) else {}
        for values in refs.values():
            if isinstance(values, list):
                direct_ref_values.update(str(value) for value in values if value is not None and value != "")
    direct_refs = sorted(direct_ref_values)
    if direct_refs:
        return (
            "RESOLVE_DIRECT_SPEC_REFERENCE",
            "C comments carry direct model-note or spec-reference evidence: " + ", ".join(direct_refs),
        )
    if not candidate:
        return ("REVIEW_MISSING_CANDIDATE_FACT", "No matching tool-ranked candidate fact was available")
    if candidate.get("eligible"):
        coverage_status = (coverage or {}).get("coverage_status") or (coverage or {}).get("status")
        if not coverage or coverage_status in {None, "NO_COVERAGE_DATA", "STATIC_UNCOVERED"}:
            return ("COLLECT_COVERAGE_EVIDENCE", "Tool facts mark the function eligible, but coverage is absent or uncovered")
        if coverage.get("eligible_after_coverage"):
            return ("REVIEW_EXACT_SPEC_SCOPE", "Tool facts and coverage admit the function; exact PDF scope still needs evidence")
        return ("REVIEW_COVERAGE_OR_DOMAIN", "Static eligibility did not survive the current coverage gate")
    if candidate.get("contributes_to_observable_output") is False:
        return ("CHECK_NON_OUTPUT_SCOPE", "The discovered function is reachable but not marked as observable-output contributing")
    if candidate.get("purity") != "PURE" or candidate.get("timing") != "COMBINATIONAL":
        return ("KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY", "Tool facts show stateful, impure, or non-combinational behavior")
    if candidate.get("bounded_computation") is False:
        return ("PROVE_BOUNDED_DOMAIN", "Tool facts do not prove fixed loop bounds")
    return ("REVIEW_SPEC_SCOPE", "Reachable code lacks a deterministic exact PDF/C link")


def _anchor_reference_keys(anchor: dict[str, Any]) -> set[str]:
    identifier = str(anchor.get("identifier", ""))
    kind = str(anchor.get("kind", ""))
    normalized_identifier = re.sub(r"\s+", "", identifier).lower()
    keys = {identifier.lower(), normalized_identifier}
    if kind == "section":
        keys.update({f"section{identifier}".lower(), f"section{normalized_identifier}"})
    elif kind == "table":
        keys.update({f"table{identifier}".lower(), f"table{normalized_identifier}"})
    elif kind == "figure":
        keys.update({f"figure{identifier}".lower(), f"figure{normalized_identifier}"})
    elif kind == "page":
        keys.update({f"p{anchor.get('page')}".lower(), f"page{anchor.get('page')}".lower()})
    return {value for value in keys if value}


def _comment_references_anchor(comment: dict[str, Any], anchor: dict[str, Any]) -> bool:
    refs = comment.get("spec_refs") if isinstance(comment.get("spec_refs"), dict) else {}
    values = {
        str(value).lower()
        for key in ("sections", "tables", "figures")
        for value in refs.get(key, [])
    }
    values.update(
        {
            f"section{value}".lower()
            for value in refs.get("sections", [])
        }
    )
    values.update(
        {
            f"table{str(value).replace(' ', '')}".lower()
            for value in refs.get("tables", [])
        }
    )
    values.update(
        {
            f"figure{str(value).replace(' ', '')}".lower()
            for value in refs.get("figures", [])
        }
    )
    values.update(
        {f"p{value}".lower() for value in refs.get("pages", [])}
    )
    values.update(
        {f"page{value}".lower() for value in refs.get("pages", [])}
    )
    return bool(values & _anchor_reference_keys(anchor))


def build_orphan_triage(
    anchors: list[dict[str, Any]],
    comments_payload: dict[str, Any],
    raw: dict[str, Any],
    candidates: dict[str, Any],
    coverage: dict[str, Any] | None,
    spec_orphans: list[str],
    code_orphans: list[str],
    input_hashes: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    """Create evidence-backed next actions for unresolved traceability items.

    This is deliberately a reporting projection.  It never creates a link or
    selects a function; every identity and classification comes from the
    existing Clang, candidate, coverage, comment, or PDF-anchor facts.
    """
    code_anchors = {
        str(item.get("code_anchor_id")): item
        for item in comments_payload.get("code_anchors", [])
        if isinstance(item, dict) and item.get("code_anchor_id")
    }
    comments_by_usr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for comment in comments_payload.get("comments", []):
        if not isinstance(comment, dict):
            continue
        usr = comment.get("clang_usr")
        if usr:
            comments_by_usr[str(usr)].append(comment)
    raw_by_usr = {
        str(item.get("clang_usr")): item
        for item in raw.get("functions", [])
        if isinstance(item, dict) and item.get("clang_usr")
    }
    candidate_by_usr = {
        str(item.get("clang_usr")): item
        for item in candidates.get("functions", [])
        if isinstance(item, dict) and item.get("clang_usr")
    }
    ranked = [
        item
        for item in candidates.get("ranked_candidates", [])
        if isinstance(item, dict) and item.get("clang_usr")
    ]
    rank_by_usr = {str(item["clang_usr"]): index for index, item in enumerate(ranked, 1)}
    coverage_by_usr = {
        str(item.get("clang_usr")): item
        for item in (coverage or {}).get("functions", [])
        if isinstance(item, dict) and item.get("clang_usr")
    }

    production_code: list[dict[str, Any]] = []
    for code_id in sorted(code_orphans):
        anchor = code_anchors.get(code_id, {"code_anchor_id": code_id})
        usr = str(anchor.get("clang_usr", ""))
        candidate = candidate_by_usr.get(usr)
        coverage_fact = coverage_by_usr.get(usr)
        related_comments = sorted(
            comments_by_usr.get(usr, []),
            key=lambda item: (int(item.get("line", 0) or 0), str(item.get("comment_id", ""))),
        )
        action, rationale = _code_orphan_action(candidate, coverage_fact, related_comments)
        production_code.append(
            {
                "code_anchor_id": code_id,
                "clang_usr": anchor.get("clang_usr"),
                "function": anchor.get("function"),
                "file": anchor.get("file"),
                "line": anchor.get("line"),
                "end_line": anchor.get("end_line"),
                "permalink": anchor.get("permalink"),
                "next_action": action,
                "rationale": rationale,
                "candidate": _candidate_view(candidate, rank_by_usr.get(usr)),
                "coverage": _coverage_view(coverage_fact),
                "raw_facts": _raw_function_view(raw_by_usr.get(usr)),
                "comments": [_comment_view(item) for item in related_comments],
            }
        )

    anchor_by_id = {
        str(item.get("anchor_id")): item
        for item in anchors
        if isinstance(item, dict) and item.get("anchor_id")
    }
    spec_items: list[dict[str, Any]] = []
    for anchor_id in sorted(spec_orphans):
        anchor = anchor_by_id.get(anchor_id, {"anchor_id": anchor_id})
        mn_ids = {str(value) for value in anchor.get("mn_ids", []) if value}
        related_comments = []
        for comment in comments_payload.get("comments", []):
            if not isinstance(comment, dict):
                continue
            comment_mn_ids = {str(value) for value in comment.get("mn_ids", []) if value}
            if (mn_ids and mn_ids & comment_mn_ids) or _comment_references_anchor(comment, anchor):
                related_comments.append(comment)
        related_comments.sort(key=lambda item: (int(item.get("line", 0) or 0), str(item.get("comment_id", ""))))
        related_functions = sorted({str(item.get("function")) for item in related_comments if item.get("function")})
        if related_comments:
            action = "REPAIR_EXACT_SPEC_LINK"
            rationale = "C comments provide a direct model-note or explicit-reference lead for this PDF anchor"
        else:
            action = "REVIEW_SPEC_SCOPE"
            rationale = "No matching C comment evidence was found for this PDF anchor"
        spec_items.append(
            {
                "spec_anchor_id": anchor_id,
                "kind": anchor.get("kind"),
                "identifier": anchor.get("identifier"),
                "page": anchor.get("page"),
                "section_id": anchor.get("section_id"),
                "section_anchor_id": anchor.get("section_anchor_id"),
                "title": anchor.get("title"),
                "short_anchor": anchor.get("short_anchor"),
                "mn_ids": sorted(mn_ids),
                "next_action": action,
                "rationale": rationale,
                "related_code_functions": related_functions,
                "comments": [_comment_view(item) for item in related_comments],
            }
        )

    code_actions = Counter(item["next_action"] for item in production_code)
    spec_actions = Counter(item["next_action"] for item in spec_items)
    return {
        "schema_version": 1,
        "do_not_edit": True,
        "summary": {
            "production_code_count": len(production_code),
            "spec_anchor_count": len(spec_items),
            "production_code_next_actions": dict(sorted(code_actions.items())),
            "spec_next_actions": dict(sorted(spec_actions.items())),
        },
        "input_hashes": dict(sorted((input_hashes or {}).items())),
        "production_code": production_code,
        "spec": spec_items,
    }


def markdown_spec_to_code(payload: dict[str, Any]) -> str:
    lines = [
        "# Specification to C traceability",
        "",
        "Generated links are EXACT only when anchored by a direct MN/spec reference. "
        "Accepted PASS library contracts may also project their hash-checked EXACT_SPEC "
        "links as REVIEWED joins to existing Clang/PDF anchors; heuristic links remain "
        "PROPOSED until human review.",
        "",
    ]
    for link in payload["links"]:
        lines.extend([
            f"- `{link['status']}` `{link['spec_anchor_id']}` page {link['spec_page']} -> `{link['function']}` `{link['code_file']}:{link['code_line']}`",
            f"  - method: {link['method']}; evidence: {link['evidence']}",
            f"  - fixed C permalink: {link['code_permalink']}",
        ])
    return "\n".join(lines) + "\n"


def markdown_code_to_spec(payload: dict[str, Any]) -> str:
    lines = ["# C to specification traceability", "", ""]
    by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for link in payload["links"]:
        by_code[link["code_anchor_id"]].append(link)
    for code_id in sorted(by_code):
        first = by_code[code_id][0]
        lines.append(f"## `{first['function']}`")
        lines.append("")
        for link in by_code[code_id]:
            lines.append(f"- `{link['status']}` page {link['spec_page']} `{link['spec_anchor_id']}` ({link['method']})")
        lines.append("")
    return "\n".join(lines)


def markdown_orphan_triage(triage: dict[str, Any]) -> str:
    summary = triage.get("summary", {})
    lines = [
        "# Traceability orphan triage",
        "",
        "This is a deterministic evidence projection for human review. It does not create traceability links or select RTL targets.",
        "",
        f"- Untraced production functions: {summary.get('production_code_count', 0)}",
        f"- Untraced PDF anchors: {summary.get('spec_anchor_count', 0)}",
        "",
        "## Production C functions",
        "",
    ]
    for item in triage.get("production_code", []):
        candidate = item.get("candidate") or {}
        coverage = item.get("coverage") or {}
        source = f"{item.get('file', 'UNKNOWN')}:{item.get('line', 'UNKNOWN')}-{item.get('end_line', item.get('line', 'UNKNOWN'))}"
        lines.extend(
            [
                f"### `{item.get('function', 'UNKNOWN')}`",
                "",
                f"- Anchor: `{item.get('code_anchor_id')}`; source: `{source}`",
                f"- Next action: `{item.get('next_action')}` — {item.get('rationale')}",
                f"- Tool rank/score: `{candidate.get('rank', '—')}` / `{candidate.get('score', '—')}`; eligible: `{candidate.get('eligible', '—')}`; purity/timing: `{candidate.get('purity', '—')}` / `{candidate.get('timing', '—')}`",
                f"- Coverage: `{coverage.get('status', '—')}`; executed: `{coverage.get('execution_count', '—')}`; eligible after coverage: `{coverage.get('eligible_after_coverage', '—')}`",
            ]
        )
        for comment in item.get("comments", []):
            lines.append(f"- C evidence: `{comment.get('file')}:{comment.get('line')}` — {comment.get('text', '')}")
        lines.append("")
    lines.extend(["## PDF anchors", ""])
    for item in triage.get("spec", []):
        lines.extend(
            [
                f"### `{item.get('spec_anchor_id')}`",
                "",
                f"- Kind/page: `{item.get('kind')}` / `{item.get('page')}`; title: {item.get('title') or item.get('short_anchor') or '—'}",
                f"- Next action: `{item.get('next_action')}` — {item.get('rationale')}",
                f"- Related C functions: {', '.join(f'`{value}`' for value in item.get('related_code_functions', [])) or 'none'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.input_manifest.resolve().read_text(encoding="utf-8"))
    raw = json.loads(args.raw.resolve().read_text(encoding="utf-8"))
    candidates = json.loads(args.candidates.resolve().read_text(encoding="utf-8"))
    output = args.output_dir.resolve()
    pdf_path = pathlib.Path(manifest["spec"]["path"])
    pdf_payload = extract_pdf_layout(pdf_path)
    anchors = pdf_payload["anchors"]
    comments = extract_c_comments(manifest, raw)
    links = proposal_links(anchors, comments, candidates, manifest)
    links = apply_reviewed(
        links,
        parse_reviewed(args.reviewed.resolve()),
        manifest,
        anchors=anchors,
        code_anchors=comments["code_anchors"],
        raw_functions=raw.get("functions", []),
    )
    library_manifest_path = (
        args.library_manifest.resolve()
        if args.library_manifest
        else output / "library" / "manifest.json"
    )
    links, library_projection = apply_library_links(
        links,
        library_manifest_path,
        output,
        anchors,
        comments["code_anchors"],
        manifest,
    )
    linked_spec = {link["spec_anchor_id"] for link in links}
    linked_code = {link["code_anchor_id"] for link in links}
    spec_orphans = [anchor["anchor_id"] for anchor in anchors if anchor["kind"] != "page" and anchor["anchor_id"] not in linked_spec]
    production_usrs = {item.get("clang_usr") for item in candidates.get("functions", []) if item.get("production_reachable")}
    production_anchors = {anchor["code_anchor_id"] for anchor in comments["code_anchors"] if anchor["clang_usr"] in production_usrs}
    code_orphans = sorted(production_anchors - linked_code)
    coverage_path = output / "coverage" / "coverage.json"
    coverage = None
    if coverage_path.is_file():
        try:
            coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            coverage = None
    counts = {
        "spec_anchor_count": len(anchors),
        "heading_anchor_count": sum(anchor["kind"] in {"section", "table", "figure"} for anchor in anchors),
        "model_note_anchor_count": sum(anchor["kind"] == "model_note" for anchor in anchors),
        "pdf_model_note_ids": sorted(
            {
                mn_id
                for anchor in anchors
                if anchor["kind"] == "model_note"
                for mn_id in anchor.get("mn_ids", [])
            }
        ),
        "c_model_note_ids": sorted(
            {mn_id for comment in comments["comments"] for mn_id in comment.get("mn_ids", [])}
        ),
        "comment_count": len(comments["comments"]),
        "model_note_count": sum(bool(comment["mn_ids"]) for comment in comments["comments"]),
        "link_count": len(links),
        "exact_count": sum(link["status"] == "EXACT" for link in links),
        "proposed_count": sum(link["status"] == "PROPOSED" for link in links),
        "reviewed_count": sum(link["status"] == "REVIEWED" for link in links),
        "stale_count": sum(link["status"] == "STALE" for link in links),
        "accepted_library_link_count": sum(link.get("method") == "accepted_library_exact_spec" for link in links),
        "untraced_spec_anchor_count": len(spec_orphans),
        "untraced_production_function_count": len(code_orphans),
    }
    counts["shared_model_note_ids"] = sorted(
        set(counts["pdf_model_note_ids"]) & set(counts["c_model_note_ids"])
    )
    counts["shared_model_note_count"] = len(counts["shared_model_note_ids"])
    orphan_triage = build_orphan_triage(
        anchors,
        comments,
        raw,
        candidates,
        coverage,
        spec_orphans,
        code_orphans,
        input_hashes={
            "raw_facts": sha256_file(args.raw.resolve()),
            "candidate_facts": sha256_file(args.candidates.resolve()),
            "coverage": sha256_file(coverage_path) if coverage_path.is_file() else None,
            "library_manifest": library_projection.get("manifest_sha256"),
        },
    )
    payload = {
        "schema_version": 2,
        "do_not_edit": True,
        "spec_sha256": manifest.get("spec", {}).get("sha256", "UNKNOWN"),
        "source_hashes_sha256": manifest.get("source", {}).get("source_hashes_sha256", "UNKNOWN"),
        "counts": counts,
        "links": links,
        "orphans": {
            "spec_anchor_ids": spec_orphans,
            "production_code_anchor_ids": code_orphans,
        },
        "library_projection": library_projection,
        "orphan_triage": orphan_triage,
    }
    write_json(
        output / "spec" / "anchors.json",
        {
            "schema_version": 3,
            "do_not_edit": True,
            "pdf_sha256": payload["spec_sha256"],
            "page_count": pdf_payload["page_count"],
            "extraction": {
                "tool": "pdftotext -layout",
                "pdfinfo_tool": pdf_payload["pdfinfo_tool"],
                "pdftotext_tool": pdf_payload["pdftotext_tool"],
                "model_note_assignment": "nearest preceding section heading on the same page",
            },
            "anchors": anchors,
        },
    )
    write_json(output / "facts" / "comments.json", comments)
    write_json(output / "traceability" / "traceability.json", payload)
    (output / "traceability" / "links.proposed.yaml").write_text(render_yaml(links, generated=True), encoding="utf-8")
    output.joinpath("reports", "spec-to-code.md").write_text(markdown_spec_to_code(payload), encoding="utf-8")
    output.joinpath("reports", "code-to-spec.md").write_text(markdown_code_to_spec(payload), encoding="utf-8")
    output.joinpath("reports", "orphan-triage.md").write_text(markdown_orphan_triage(orphan_triage), encoding="utf-8")
    output.joinpath("reports", "orphans.md").write_text(
        "# Traceability orphans\n\n"
        + f"- Untraced spec anchors: {len(spec_orphans)}\n"
        + f"- Untraced production functions: {len(code_orphans)}\n\n"
        + "- Detailed deterministic triage: [orphan-triage.md](orphan-triage.md)\n\n"
        + "## Spec anchors\n\n"
        + "\n".join(f"- `{item}`" for item in spec_orphans)
        + "\n\n## Production C functions\n\n"
        + "\n".join(f"- `{item}`" for item in code_orphans)
        + "\n",
        encoding="utf-8",
    )
    manifest["pdf_extraction"] = {
        "tool": "pdftotext -layout",
        "pdfinfo_tool": pdf_payload["pdfinfo_tool"],
        "pdftotext_tool": pdf_payload["pdftotext_tool"],
        "pdfinfo": pdf_payload["pdfinfo"],
        "page_count": pdf_payload["page_count"],
        "anchor_count": len(anchors),
        "text_stream_pages": pdf_payload["text_pages"],
        "model_note_assignment": "nearest preceding section heading on the same pdftotext -layout page",
    }
    write_json(args.input_manifest.resolve(), manifest)
    print(f"traceability generated: {counts['exact_count']} exact, {counts['proposed_count']} proposed, {counts['reviewed_count']} reviewed")
    return 0


def render_yaml(links: list[dict[str, Any]], generated: bool) -> str:
    lines = ["schema_version: 1", f"do_not_edit: {'true' if generated else 'false'}", "links:"]
    for link in links:
        lines.append(f"  - link_id: {json.dumps(link['link_id'])}")
        for key in ("status", "method", "spec_anchor_id", "code_anchor_id", "spec_sha256", "source_hashes_sha256", "note"):
            if key in link:
                lines.append(f"    {key}: {json.dumps(str(link[key]))}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
