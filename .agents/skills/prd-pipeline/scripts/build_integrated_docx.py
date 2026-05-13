#!/usr/bin/env python3
"""Build a lightweight integrated PRD handoff DOCX from Markdown files.

This script intentionally uses only the Python standard library. It supports
the Markdown structures commonly produced by the PRD pipeline: headings,
paragraphs, bullets, numbered lists, simple tables, and fenced code blocks.
The DOCX is a review/share artifact; the Markdown files remain the source of
truth for version control.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Part:
    title: str
    path: Path


def fail(code: str, message: str, **extra: object) -> int:
    print(json.dumps({"ok": False, "code": code, "message": message, **extra}, ensure_ascii=False), file=sys.stderr)
    return 1


def parse_part(raw: str) -> Part:
    if "=" not in raw:
        raise ValueError("--part must use TITLE=PATH")
    title, path = raw.split("=", 1)
    title = title.strip()
    path = path.strip()
    if not title or not path:
        raise ValueError("--part title and path must be non-empty")
    return Part(title=title, path=Path(path))


def paragraph(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    lines = text.splitlines() or [""]
    runs = []
    for index, line in enumerate(lines):
        if index:
            runs.append("<w:r><w:br/></w:r>")
        escaped = html.escape(line.replace("\t", "    "), quote=False)
        runs.append(f'<w:r><w:t xml:space="preserve">{escaped}</w:t></w:r>')
    return f"<w:p>{style_xml}{''.join(runs)}</w:p>"


def table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    cells = []
    max_cols = max(len(row) for row in rows)
    for row in rows:
        padded = row + [""] * (max_cols - len(row))
        cell_xml = "".join(
            "<w:tc><w:tcPr><w:tcW w:w=\"2400\" w:type=\"dxa\"/></w:tcPr>"
            + paragraph(cell.strip())
            + "</w:tc>"
            for cell in padded
        )
        cells.append(f"<w:tr>{cell_xml}</w:tr>")
    return "<w:tbl><w:tblPr><w:tblW w:w=\"0\" w:type=\"auto\"/><w:tblBorders><w:top w:val=\"single\" w:sz=\"4\"/><w:left w:val=\"single\" w:sz=\"4\"/><w:bottom w:val=\"single\" w:sz=\"4\"/><w:right w:val=\"single\" w:sz=\"4\"/><w:insideH w:val=\"single\" w:sz=\"4\"/><w:insideV w:val=\"single\" w:sz=\"4\"/></w:tblBorders></w:tblPr>" + "".join(cells) + "</w:tbl>"


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def flush_table(buffer: list[list[str]], out: list[str]) -> None:
    if buffer:
        out.append(table(buffer))
        buffer.clear()


def markdown_to_body(markdown: str) -> list[str]:
    out: list[str] = []
    table_buffer: list[list[str]] = []
    in_code = False
    code_lines: list[str] = []

    def flush_code() -> None:
        if code_lines:
            out.append(paragraph("\n".join(code_lines), "Code"))
            code_lines.clear()

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()

        if line.strip().startswith("```"):
            flush_table(table_buffer, out)
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_table(table_buffer, out)
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_table(table_buffer, out)
            level = min(len(heading.group(1)), 3)
            out.append(paragraph(heading.group(2).strip(), f"Heading{level}"))
            continue

        if "|" in line and line.strip().startswith("|") and line.strip().endswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if is_table_separator(line):
                continue
            table_buffer.append(cells)
            continue

        flush_table(table_buffer, out)

        bullet = re.match(r"^[-*]\s+(.+)$", line)
        if bullet:
            out.append(paragraph("• " + bullet.group(1).strip(), "ListParagraph"))
            continue

        numbered = re.match(r"^\d+[.)]\s+(.+)$", line)
        if numbered:
            out.append(paragraph(numbered.group(0).strip(), "ListParagraph"))
            continue

        out.append(paragraph(line))

    flush_table(table_buffer, out)
    if in_code:
        flush_code()
    return out


def document_xml(title: str, parts: Iterable[tuple[str, str]]) -> str:
    body: list[str] = [paragraph(title, "Title")]
    for part_title, content in parts:
        body.append(paragraph(part_title, "Heading1"))
        body.extend(markdown_to_body(content))
        body.append(paragraph(""))
    body.append('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(body)}</w:body></w:document>"
    )


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Calibri" w:eastAsia="Microsoft YaHei"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="36"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="28"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="360"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/><w:basedOn w:val="Normal"/><w:rPr><w:rFonts w:ascii="Consolas" w:eastAsia="Consolas"/><w:sz w:val="20"/></w:rPr></w:style>
</w:styles>"""


def write_docx(output: Path, doc_xml: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>""")
        zf.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")
        zf.writestr("word/_rels/document.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>""")
        zf.writestr("word/document.xml", doc_xml)
        zf.writestr("word/styles.xml", styles_xml())


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an integrated PRD handoff DOCX from Markdown parts.")
    parser.add_argument("--output", required=True, help="Output .docx path")
    parser.add_argument("--title", default="PRD Handoff Package", help="Document title")
    parser.add_argument("--part", action="append", required=True, help="Section in TITLE=PATH form; can be repeated")
    args = parser.parse_args()

    try:
        parts = [parse_part(raw) for raw in args.part]
    except ValueError as exc:
        return fail("invalid_part", str(exc))

    loaded: list[tuple[str, str]] = []
    missing = []
    for part in parts:
        if not part.path.exists():
            missing.append(str(part.path))
            continue
        loaded.append((part.title, part.path.read_text(encoding="utf-8")))
    if missing:
        return fail("missing_input", "one or more markdown inputs do not exist", files=missing)

    output = Path(args.output)
    if output.suffix.lower() != ".docx":
        return fail("invalid_output", "--output must end with .docx", output=str(output))

    doc_xml = document_xml(args.title, loaded)
    write_docx(output, doc_xml)
    print(json.dumps({"ok": True, "path": str(output), "parts": len(loaded)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
