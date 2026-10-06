"""OpenDocument formats (LibreOffice): ODS, ODT, ODP. Standard library only."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import List, Tuple

from ..tables import render_table
from . import Converted
from .ooxml import _join_blocks
from .sheets import format_number, format_percent, render_sheets
from .xmlutil import attr, child, children, has, local, read_xml

MAX_REPEAT = 10000  # guard against "repeat this row a million times" padding


def _text(el) -> str:
    """Text of an OpenDocument text element (handles spaces, tabs, line breaks)."""
    out = []
    if el.text:
        out.append(el.text)
    for node in el:
        name = local(node.tag)
        if name == "s":
            out.append(" " * int(attr(node, "c", "1") or 1))
        elif name == "tab":
            out.append("\t")
        elif name == "line-break":
            out.append("\n")
        elif name in ("note", "annotation", "bookmark", "bookmark-start", "bookmark-end"):
            pass
        else:
            out.append(_text(node))
        if node.tail:
            out.append(node.tail)
    return "".join(out)


def _cell_value(cell) -> str:
    kind = attr(cell, "value-type")
    if kind in ("float", "currency"):
        value = attr(cell, "value")
        try:
            return format_number(float(value))
        except (TypeError, ValueError):
            pass
    elif kind == "percentage":
        try:
            return format_percent(float(attr(cell, "value")))
        except (TypeError, ValueError):
            pass
    elif kind == "date":
        value = attr(cell, "date-value") or ""
        return value[:-9] if value.endswith("T00:00:00") else value.replace("T", " ")
    elif kind == "time":
        return attr(cell, "time-value") or ""
    elif kind == "boolean":
        return "TRUE" if (attr(cell, "boolean-value") or "").lower() == "true" else "FALSE"
    return "\n".join(_text(p) for p in children(cell, "p")).strip()


def _table_rows(table) -> List[List[str]]:
    rows: List[List[str]] = []

    def walk(container):
        for el in container:
            name = local(el.tag)
            if name in ("table-header-rows", "table-row-group", "table-rows"):
                walk(el)
            elif name == "table-row":
                row: List[str] = []
                pending_empty = 0
                for cell in el:
                    if local(cell.tag) not in ("table-cell", "covered-table-cell"):
                        continue
                    repeat = min(int(attr(cell, "number-columns-repeated", "1") or 1), MAX_REPEAT)
                    value = _cell_value(cell)
                    if value == "":
                        pending_empty += repeat
                        continue
                    row.extend([""] * pending_empty)
                    pending_empty = 0
                    row.extend([value] * repeat)
                if row:
                    times = min(int(attr(el, "number-rows-repeated", "1") or 1), MAX_REPEAT)
                    rows.extend([list(row) for _ in range(times)])

    walk(table)
    return rows


def _body(zf: zipfile.ZipFile, kind: str):
    if not has(zf, "content.xml"):
        raise ValueError("not a valid OpenDocument file (content.xml missing)")
    root = read_xml(zf, "content.xml")
    body = child(root, "body")
    return child(body, kind) if body is not None else None


def convert_ods(path: Path, table_format: str = "auto", include_hidden: bool = False) -> Converted:
    with zipfile.ZipFile(path) as zf:
        sheet_root = _body(zf, "spreadsheet")
    sheets: List[Tuple[str, List[List[str]]]] = []
    for table in children(sheet_root, "table") if sheet_root is not None else []:
        sheets.append((attr(table, "name", "") or "", _table_rows(table)))
    text, baseline = render_sheets(sheets, table_format)
    return Converted(text=text, baseline_text=baseline, baseline_kind="markdown-table")


def _odt_blocks(container, table_format: str, depth: int = 0) -> List[str]:
    out = []
    for el in container:
        name = local(el.tag)
        if name == "h":
            level = min(int(attr(el, "outline-level", "1") or 1), 6)
            text = " ".join(_text(el).split())
            if text:
                out.append("#" * level + " " + text)
        elif name == "p":
            text = _text(el).strip()
            if text:
                out.append(text)
        elif name == "list":
            for item in children(el, "list-item"):
                first = True
                for sub in item:
                    sub_name = local(sub.tag)
                    if sub_name in ("p", "h"):
                        text = _text(sub).strip()
                        if text:
                            out.append("  " * depth + ("- " if first else "  ") + text)
                            first = False
                    elif sub_name == "list":
                        out.extend(_odt_blocks([sub], table_format, depth + 1))
        elif name == "table":
            rendered = render_table(_table_rows(el), table_format)
            if rendered:
                out.append(rendered)
        elif name in ("section", "index-body", "table-of-content", "illustration-index-source"):
            out.extend(_odt_blocks(el, table_format, depth))
    return out


def convert_odt(path: Path, table_format: str = "auto") -> Converted:
    with zipfile.ZipFile(path) as zf:
        text_root = _body(zf, "text")
    blocks = _odt_blocks(text_root, table_format) if text_root is not None else []
    return Converted(text=_join_blocks(blocks))


def convert_odp(path: Path, table_format: str = "auto") -> Converted:
    with zipfile.ZipFile(path) as zf:
        pres = _body(zf, "presentation")
    out = []
    for number, page in enumerate(children(pres, "page") if pres is not None else [], 1):
        lines: List[str] = []
        notes: List[str] = []

        def walk(el, target):
            for node in el:
                name = local(node.tag)
                if name == "notes":
                    walk(node, notes)
                elif name == "text-box":
                    target.extend(_odt_blocks(node, table_format))
                elif name == "table":
                    rendered = render_table(_table_rows(node), table_format)
                    if rendered:
                        target.append(rendered)
                else:
                    walk(node, target)

        walk(page, lines)
        title = attr(page, "name", "") or ""
        header = f"## Slide {number}" + (f": {title}" if title and not title.lower().startswith("page") else "")
        section = [header] + lines
        if notes:
            section.append("Notes: " + " ".join(notes))
        out.append("\n".join(section))
    return Converted(text="\n\n".join(out), pages=len(out))
