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
from collections import defaultdict
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


def markdown_spec_to_code(payload: dict[str, Any]) -> str:
    lines = ["# Specification to C traceability", "", "Generated links are EXACT only when anchored by a direct MN/spec reference; heuristic links remain PROPOSED until human review.", ""]
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


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.input_manifest.resolve().read_text(encoding="utf-8"))
    raw = json.loads(args.raw.resolve().read_text(encoding="utf-8"))
    candidates = json.loads(args.candidates.resolve().read_text(encoding="utf-8"))
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
    linked_spec = {link["spec_anchor_id"] for link in links}
    linked_code = {link["code_anchor_id"] for link in links}
    spec_orphans = [anchor["anchor_id"] for anchor in anchors if anchor["kind"] != "page" and anchor["anchor_id"] not in linked_spec]
    production_usrs = {item.get("clang_usr") for item in candidates.get("functions", []) if item.get("production_reachable")}
    production_anchors = {anchor["code_anchor_id"] for anchor in comments["code_anchors"] if anchor["clang_usr"] in production_usrs}
    code_orphans = sorted(production_anchors - linked_code)
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
        "untraced_spec_anchor_count": len(spec_orphans),
        "untraced_production_function_count": len(code_orphans),
    }
    counts["shared_model_note_ids"] = sorted(
        set(counts["pdf_model_note_ids"]) & set(counts["c_model_note_ids"])
    )
    counts["shared_model_note_count"] = len(counts["shared_model_note_ids"])
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
    }
    output = args.output_dir.resolve()
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
    output.joinpath("reports", "orphans.md").write_text(
        "# Traceability orphans\n\n"
        + f"- Untraced spec anchors: {len(spec_orphans)}\n"
        + f"- Untraced production functions: {len(code_orphans)}\n\n"
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
