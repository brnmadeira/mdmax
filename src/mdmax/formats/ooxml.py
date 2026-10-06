"""Microsoft Office (OOXML) formats read with the standard library: XLSX, DOCX, PPTX.

They are zip files of XML parts, so no third-party package is needed. That keeps
mdmax working in places where nothing can be installed, such as the code
execution sandbox of claude.ai.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

from ..tables import render_table
from . import Converted
from .sheets import (
    BUILTIN_DATE_FORMATS,
    BUILTIN_PERCENT_FORMATS,
    format_number,
    format_percent,
    is_date_format,
    is_percent_format,
    render_sheets,
    serial_to_text,
)
from .xmlutil import attr, child, children, descendants, has, local, read_xml, rel_id, relationships

# ---------------------------------------------------------------------------
# XLSX / XLSM
# ---------------------------------------------------------------------------

_CELL_REF = re.compile(r"([A-Z]+)(\d+)")


def _col_index(ref: str) -> Optional[int]:
    m = _CELL_REF.match(ref or "")
    if not m:
        return None
    n = 0
    for ch in m.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _shared_strings(zf: zipfile.ZipFile, path: str) -> List[str]:
    if not path or not has(zf, path):
        return []
    out = []
    with zf.open(path) as fh:
        for _event, el in ET.iterparse(fh, events=("end",)):
            if local(el.tag) != "si":
                continue
            pieces = []
            for node in el:
                name = local(node.tag)
                if name == "t":
                    pieces.append(node.text or "")
                elif name == "r":
                    t = child(node, "t")
                    if t is not None:
                        pieces.append(t.text or "")
            out.append("".join(pieces))
            el.clear()
    return out


def _cell_styles(zf: zipfile.ZipFile, path: str) -> List[str]:
    """Kind of each cell style index: 'date', 'percent' or ''."""
    if not path or not has(zf, path):
        return []
    root = read_xml(zf, path)
    custom: Dict[int, str] = {}
    num_fmts = child(root, "numFmts")
    if num_fmts is not None:
        for nf in children(num_fmts, "numFmt"):
            try:
                custom[int(attr(nf, "numFmtId", "0"))] = attr(nf, "formatCode", "") or ""
            except ValueError:
                pass
    kinds = []
    xfs = child(root, "cellXfs")
    for xf in children(xfs, "xf") if xfs is not None else []:
        try:
            fid = int(attr(xf, "numFmtId", "0"))
        except ValueError:
            fid = 0
        code = custom.get(fid, "")
        if fid in BUILTIN_DATE_FORMATS or (fid in custom and is_date_format(code)):
            kinds.append("date")
        elif fid in BUILTIN_PERCENT_FORMATS or (fid in custom and is_percent_format(code)):
            kinds.append("percent")
        else:
            kinds.append("")
    return kinds


def _sheet_rows(zf, path, shared, styles, date1904, stats) -> List[List[str]]:
    rows: List[List[str]] = []
    with zf.open(path) as fh:
        for _event, el in ET.iterparse(fh, events=("end",)):
            if local(el.tag) != "row":
                continue
            cells: Dict[int, str] = {}
            position = 0
            for c in el:
                if local(c.tag) != "c":
                    continue
                idx = _col_index(c.get("r", ""))
                if idx is None:
                    idx = position
                position = idx + 1
                kind = c.get("t", "n")
                v = child(c, "v")
                raw = v.text if v is not None else None
                value = ""
                if kind == "s" and raw is not None:
                    try:
                        value = shared[int(raw)]
                    except (ValueError, IndexError):
                        value = raw
                elif kind == "inlineStr":
                    is_el = child(c, "is")
                    value = "".join(t.text or "" for t in descendants(is_el, "t")) if is_el is not None else ""
                elif kind == "b":
                    value = "TRUE" if raw == "1" else "FALSE" if raw == "0" else ""
                elif kind in ("e", "str", "d"):
                    value = raw or ""
                elif raw is not None:
                    try:
                        number = float(raw)
                        style = c.get("s")
                        style_kind = styles[int(style)] if style and int(style) < len(styles) else ""
                        if style_kind == "date":
                            value = serial_to_text(number, date1904)
                        elif style_kind == "percent":
                            value = format_percent(number)
                        else:
                            value = format_number(number)
                    except ValueError:
                        value = raw
                else:
                    f = child(c, "f")
                    if f is not None and f.text:
                        value = "=" + f.text
                        stats["formulas_without_value"] += 1
                if value != "":
                    cells[idx] = value
            if cells:
                rows.append([cells.get(i, "") for i in range(max(cells) + 1)])
            el.clear()
    return rows


def convert_xlsx(path: Path, table_format: str = "auto", include_hidden: bool = False) -> Converted:
    warnings: List[str] = []
    with zipfile.ZipFile(path) as zf:
        wb_path = "xl/workbook.xml"
        if not has(zf, wb_path):
            raise ValueError("not a valid XLSX file (xl/workbook.xml missing)")
        wb = read_xml(zf, wb_path)
        rels = relationships(zf, wb_path)
        pr = child(wb, "workbookPr")
        date1904 = pr is not None and attr(pr, "date1904", "0") in ("1", "true")
        shared_path = styles_path = ""
        for rel in rels.values():
            if rel["type"].endswith("/sharedStrings"):
                shared_path = rel["target"]
            elif rel["type"].endswith("/styles"):
                styles_path = rel["target"]
        shared = _shared_strings(zf, shared_path or "xl/sharedStrings.xml")
        styles = _cell_styles(zf, styles_path or "xl/styles.xml")
        sheets_el = child(wb, "sheets")
        sheets: List[Tuple[str, List[List[str]]]] = []
        hidden = []
        stats = {"formulas_without_value": 0}
        for sheet in children(sheets_el, "sheet") if sheets_el is not None else []:
            name = attr(sheet, "name", "") or ""
            state = attr(sheet, "state", "visible")
            if state in ("hidden", "veryHidden") and not include_hidden:
                hidden.append(name)
                continue
            rel = rels.get(rel_id(sheet) or "")
            if not rel or not has(zf, rel["target"]):
                continue
            if not rel["type"].endswith("/worksheet"):
                continue  # chart sheets and dialog sheets have no cell data
            sheets.append((name, _sheet_rows(zf, rel["target"], shared, styles, date1904, stats)))
    if hidden:
        warnings.append(f"{len(hidden)} hidden sheet(s) skipped: {', '.join(hidden)} (use --include-hidden)")
    if stats["formulas_without_value"]:
        warnings.append(
            f"{stats['formulas_without_value']} formula cell(s) had no saved result "
            "(the file was never recalculated in a spreadsheet app); shown as formulas"
        )
    text, baseline = render_sheets(sheets, table_format)
    return Converted(text=text, baseline_text=baseline, baseline_kind="markdown-table", warnings=warnings)


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------

_HEADING_NAME = re.compile(r"^heading\s*(\d)$", re.IGNORECASE)


def _docx_styles(zf: zipfile.ZipFile) -> Dict[str, int]:
    """styleId -> heading level (1-6) for heading and title styles."""
    if not has(zf, "word/styles.xml"):
        return {}
    root = read_xml(zf, "word/styles.xml")
    levels = {}
    for style in children(root, "style"):
        sid = attr(style, "styleId")
        name_el = child(style, "name")
        name = (attr(name_el, "val", "") or "") if name_el is not None else ""
        level = None
        m = _HEADING_NAME.match(name.strip())
        if m:
            level = int(m.group(1))
        elif name.strip().lower() == "title":
            level = 1
        else:
            ppr = child(style, "pPr")
            outline = child(ppr, "outlineLvl") if ppr is not None else None
            if outline is not None:
                try:
                    level = int(attr(outline, "val", "9")) + 1
                except ValueError:
                    level = None
        if sid and level and level <= 6:
            levels[sid] = level
    return levels


class _Docx:
    def __init__(self, zf: zipfile.ZipFile, table_format: str):
        self.zf = zf
        self.table_format = table_format
        self.levels = _docx_styles(zf)
        self.rels = relationships(zf, "word/document.xml")

    def inline(self, el) -> str:
        out = []
        for node in el:
            name = local(node.tag)
            if name == "t":
                out.append(node.text or "")
            elif name == "tab":
                out.append("\t")
            elif name in ("br", "cr"):
                out.append("\n")
            elif name == "noBreakHyphen":
                out.append("-")
            elif name in ("delText", "instrText", "rPr", "pPr", "del", "fldChar", "footnoteReference", "commentReference"):
                continue
            elif name == "hyperlink":
                text = self.inline(node)
                rel = self.rels.get(rel_id(node) or "")
                url = rel["target"] if rel and rel["external"] else ""
                out.append(f"[{text}]({url})" if url and text.strip() and text.strip() != url else text)
            elif name == "drawing":
                for doc_pr in descendants(node, "docPr"):
                    alt = (attr(doc_pr, "descr") or "").strip()
                    if alt:
                        out.append(f"[imagem: {alt}]")
            elif name == "txbxContent":
                out.append(" " + " ".join(self.paragraph_text(p) for p in descendants(node, "p")) + " ")
            else:
                out.append(self.inline(node))
        return "".join(out)

    def paragraph_text(self, p) -> str:
        return self.inline(p)

    def paragraph(self, p) -> str:
        text = self.paragraph_text(p).strip()
        if not text:
            return ""
        ppr = child(p, "pPr")
        if ppr is not None:
            style = child(ppr, "pStyle")
            level = self.levels.get(attr(style, "val", "") or "") if style is not None else None
            outline = child(ppr, "outlineLvl")
            if level is None and outline is not None:
                try:
                    level = int(attr(outline, "val", "9")) + 1
                except ValueError:
                    level = None
            if level and level <= 6:
                return "#" * level + " " + " ".join(text.split())
            num = child(ppr, "numPr")
            if num is not None:
                ilvl = child(num, "ilvl")
                depth = int(attr(ilvl, "val", "0") or 0) if ilvl is not None else 0
                return "  " * depth + "- " + text
        return text

    def table(self, tbl) -> str:
        rows = []
        for tr in children(tbl, "tr"):
            row = []
            for tc in children(tr, "tc"):
                parts = []
                for item in tc:
                    if local(item.tag) == "p":
                        t = self.paragraph_text(item).strip()
                        if t:
                            parts.append(t)
                    elif local(item.tag) == "tbl":
                        parts.append(self.table(item).replace("\n", " "))
                row.append(" ".join(parts))
                tcpr = child(tc, "tcPr")
                span = child(tcpr, "gridSpan") if tcpr is not None else None
                if span is not None:
                    try:
                        row.extend([""] * (int(attr(span, "val", "1")) - 1))
                    except ValueError:
                        pass
            rows.append(row)
        return render_table(rows, self.table_format)

    def blocks(self, container) -> List[str]:
        out = []
        for el in container:
            name = local(el.tag)
            if name == "p":
                text = self.paragraph(el)
                if text:
                    out.append(text)
            elif name == "tbl":
                text = self.table(el)
                if text:
                    out.append(text)
            elif name in ("sdt", "sdtContent", "customXml", "ins", "smartTag"):
                out.extend(self.blocks(el))
        return out


def convert_docx(path: Path, table_format: str = "auto") -> Converted:
    with zipfile.ZipFile(path) as zf:
        if not has(zf, "word/document.xml"):
            raise ValueError("not a valid DOCX file (word/document.xml missing)")
        doc = _Docx(zf, table_format)
        root = read_xml(zf, "word/document.xml")
        body = child(root, "body")
        blocks = doc.blocks(body) if body is not None else []
    return Converted(text=_join_blocks(blocks))


def _join_blocks(blocks: List[str]) -> str:
    """Blank line between blocks, but keep consecutive list items together."""
    out: List[str] = []
    for block in blocks:
        is_item = block.lstrip().startswith("- ")
        if out and is_item and out[-1].lstrip().startswith("- "):
            out[-1] += "\n" + block
        else:
            out.append(block)
    return "\n\n".join(out)


# ---------------------------------------------------------------------------
# PPTX
# ---------------------------------------------------------------------------

_SKIP_PLACEHOLDERS = {"sldNum", "dt", "ftr", "hdr"}


def _pptx_paragraphs(tx_body) -> List[str]:
    lines = []
    for p in children(tx_body, "p"):
        pieces = []
        for node in p:
            name = local(node.tag)
            if name in ("r", "fld"):
                t = child(node, "t")
                if t is not None:
                    pieces.append(t.text or "")
            elif name == "br":
                pieces.append("\n")
        text = "".join(pieces).strip()
        if not text:
            continue
        ppr = child(p, "pPr")
        level = int(attr(ppr, "lvl", "0") or 0) if ppr is not None else 0
        lines.append("  " * level + text)
    return lines


def _placeholder_type(sp) -> Optional[str]:
    for ph in descendants(sp, "ph"):
        return attr(ph, "type", "body") or "body"
    return None


class _Pptx:
    def __init__(self, table_format: str):
        self.table_format = table_format

    def shapes(self, tree) -> Tuple[Optional[str], List[str]]:
        title = None
        lines: List[str] = []
        for el in tree:
            name = local(el.tag)
            if name == "sp":
                ph = _placeholder_type(el)
                if ph in _SKIP_PLACEHOLDERS:
                    continue
                body = child(el, "txBody")
                if body is None:
                    continue
                paragraphs = _pptx_paragraphs(body)
                if ph in ("title", "ctrTitle") and title is None and paragraphs:
                    title = " ".join(" ".join(paragraphs).split())
                else:
                    lines.extend(paragraphs)
            elif name == "grpSp":
                sub_title, sub_lines = self.shapes(el)
                if sub_title and title is None:
                    title = sub_title
                lines.extend(sub_lines)
            elif name == "graphicFrame":
                for tbl in descendants(el, "tbl"):
                    rows = []
                    for tr in children(tbl, "tr"):
                        row = []
                        for tc in children(tr, "tc"):
                            body = child(tc, "txBody")
                            row.append(" ".join(_pptx_paragraphs(body)) if body is not None else "")
                        rows.append(row)
                    rendered = render_table(rows, self.table_format)
                    if rendered:
                        lines.append(rendered)
            elif name == "pic":
                for c_nv in descendants(el, "cNvPr"):
                    alt = (attr(c_nv, "descr") or "").strip()
                    if alt:
                        lines.append(f"[imagem: {alt}]")
        return title, lines


def convert_pptx(path: Path, table_format: str = "auto") -> Converted:
    out = []
    with zipfile.ZipFile(path) as zf:
        pres_path = "ppt/presentation.xml"
        if not has(zf, pres_path):
            raise ValueError("not a valid PPTX file (ppt/presentation.xml missing)")
        pres = read_xml(zf, pres_path)
        rels = relationships(zf, pres_path)
        reader = _Pptx(table_format)
        ids = child(pres, "sldIdLst")
        slide_paths = []
        for sld in children(ids, "sldId") if ids is not None else []:
            if attr(sld, "show", "1") == "0":
                continue
            rel = rels.get(rel_id(sld) or "")
            if rel and has(zf, rel["target"]):
                slide_paths.append(rel["target"])
        for number, slide_path in enumerate(slide_paths, 1):
            root = read_xml(zf, slide_path)
            tree = next(descendants(root, "spTree"), None)
            title, lines = reader.shapes(tree) if tree is not None else (None, [])
            notes: List[str] = []
            for rel in relationships(zf, slide_path).values():
                if rel["type"].endswith("/notesSlide") and has(zf, rel["target"]):
                    notes_root = read_xml(zf, rel["target"])
                    for sp in descendants(notes_root, "sp"):
                        if _placeholder_type(sp) == "body":
                            body = child(sp, "txBody")
                            if body is not None:
                                notes.extend(_pptx_paragraphs(body))
            header = f"## Slide {number}" + (f": {title}" if title else "")
            section = [header] + lines
            if notes:
                section.append("Notes: " + " ".join(n.strip() for n in notes))
            out.append("\n".join(section))
    return Converted(text="\n\n".join(out), pages=len(out))
