"""Builds small but realistic documents with the standard library only.

Used by the tests and by tools/benchmark.py, so both run anywhere without fixture
files in the repository.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple
from xml.sax.saxutils import escape

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_RELS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _zip(path: Path, parts: dict, first: Optional[Tuple[str, str]] = None) -> Path:
    path = Path(path)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        if first:  # EPUB requires "mimetype" first and uncompressed
            zf.writestr(zipfile.ZipInfo(first[0]), first[1], compress_type=zipfile.ZIP_STORED)
        for name, data in parts.items():
            zf.writestr(name, data)
    return path


def _rels(items: Iterable[Tuple[str, str, str]], external: Sequence[str] = ()) -> str:
    out = [f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{PKG_RELS}">']
    for rid, rtype, target in items:
        mode = ' TargetMode="External"' if rid in external else ""
        out.append(f'<Relationship Id="{rid}" Type="{R_NS}/{rtype}" Target="{escape(target)}"{mode}/>')
    out.append("</Relationships>")
    return "".join(out)


# --------------------------------------------------------------------------- XLSX

def _col(n: int) -> str:
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def make_xlsx(path, sheets: List[Tuple[str, List[list], bool]]) -> Path:
    """sheets: [(name, rows, hidden)]. Cell values: str, int, float, bool, None,
    ("date", serial), ("pct", fraction), ("f", formula, cached_value_or_None)."""
    strings: List[str] = []
    index = {}

    def sst(text: str) -> int:
        if text not in index:
            index[text] = len(strings)
            strings.append(text)
        return index[text]

    parts = {}
    wb_sheets, wb_rels = [], []
    for n, (name, rows, hidden) in enumerate(sheets, 1):
        state = ' state="hidden"' if hidden else ""
        wb_sheets.append(f'<sheet name="{escape(name)}" sheetId="{n}"{state} r:id="rId{n}"/>')
        wb_rels.append((f"rId{n}", "worksheet", f"worksheets/sheet{n}.xml"))
        xml_rows = []
        for r, row in enumerate(rows, 1):
            cells = []
            for c, value in enumerate(row):
                ref = f"{_col(c)}{r}"
                if value is None:
                    continue
                if isinstance(value, bool):
                    cells.append(f'<c r="{ref}" t="b"><v>{int(value)}</v></c>')
                elif isinstance(value, (int, float)):
                    cells.append(f'<c r="{ref}"><v>{value}</v></c>')
                elif isinstance(value, str):
                    cells.append(f'<c r="{ref}" t="s"><v>{sst(value)}</v></c>')
                elif value[0] == "date":
                    cells.append(f'<c r="{ref}" s="1"><v>{value[1]}</v></c>')
                elif value[0] == "pct":
                    cells.append(f'<c r="{ref}" s="3"><v>{value[1]}</v></c>')
                elif value[0] == "f":
                    cached = "" if value[2] is None else f"<v>{value[2]}</v>"
                    cells.append(f'<c r="{ref}"><f>{escape(value[1])}</f>{cached}</c>')
            xml_rows.append(f'<row r="{r}">{"".join(cells)}</row>')
        parts[f"xl/worksheets/sheet{n}.xml"] = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<sheetData>{"".join(xml_rows)}</sheetData></worksheet>'
        )
    k = len(sheets)
    wb_rels += [(f"rId{k + 1}", "sharedStrings", "sharedStrings.xml"), (f"rId{k + 2}", "styles", "styles.xml")]
    parts["xl/workbook.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="{R_NS}">'
        f'<sheets>{"".join(wb_sheets)}</sheets></workbook>'
    )
    parts["xl/_rels/workbook.xml.rels"] = _rels(wb_rels)
    parts["xl/sharedStrings.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        + "".join(f"<si><t>{escape(s)}</t></si>" for s in strings)
        + "</sst>"
    )
    parts["xl/styles.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<numFmts count="1"><numFmt numFmtId="164" formatCode="dd/mm/yyyy"/></numFmts>'
        '<cellXfs count="4"><xf numFmtId="0"/><xf numFmtId="14"/><xf numFmtId="164"/><xf numFmtId="10"/></cellXfs>'
        "</styleSheet>"
    )
    parts["_rels/.rels"] = _rels([("rId1", "officeDocument", "xl/workbook.xml")])
    parts["[Content_Types].xml"] = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>'
    return _zip(path, parts)


# --------------------------------------------------------------------------- DOCX

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def make_docx(path, blocks: List[tuple]) -> Path:
    """blocks: ("h", level, text) | ("p", text) | ("li", text) | ("table", rows) | ("link", text, url)."""
    body, rels = [], [("rId1", "styles", "styles.xml")]
    for block in blocks:
        kind = block[0]
        if kind == "h":
            body.append(f'<w:p><w:pPr><w:pStyle w:val="Ttulo{block[1]}"/></w:pPr><w:r><w:t>{escape(block[2])}</w:t></w:r></w:p>')
        elif kind == "p":
            body.append(f'<w:p><w:r><w:t xml:space="preserve">{escape(block[1])}</w:t></w:r></w:p>')
        elif kind == "li":
            body.append(
                '<w:p><w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr></w:pPr>'
                f'<w:r><w:t>{escape(block[1])}</w:t></w:r></w:p>'
            )
        elif kind == "link":
            rid = f"rId{len(rels) + 1}"
            rels.append((rid, "hyperlink", block[2]))
            body.append(f'<w:p><w:hyperlink r:id="{rid}"><w:r><w:t>{escape(block[1])}</w:t></w:r></w:hyperlink></w:p>')
        elif kind == "table":
            rows = "".join(
                "<w:tr>" + "".join(f"<w:tc><w:p><w:r><w:t>{escape(str(c))}</w:t></w:r></w:p></w:tc>" for c in row) + "</w:tr>"
                for row in block[1]
            )
            body.append(f"<w:tbl>{rows}</w:tbl>")
    external = [rid for rid, rtype, _ in rels if rtype == "hyperlink"]
    styles = "".join(
        f'<w:style w:type="paragraph" w:styleId="Ttulo{n}"><w:name w:val="heading {n}"/></w:style>' for n in (1, 2, 3)
    )
    parts = {
        "word/document.xml": f'<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="{W}" xmlns:r="{R_NS}"><w:body>{"".join(body)}</w:body></w:document>',
        "word/styles.xml": f'<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="{W}">{styles}</w:styles>',
        "word/_rels/document.xml.rels": _rels(rels, external),
        "_rels/.rels": _rels([("rId1", "officeDocument", "word/document.xml")]),
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
    }
    return _zip(path, parts)


# --------------------------------------------------------------------------- PPTX

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def _sp(text_lines: List[str], ph: Optional[str] = None) -> str:
    ph_xml = f'<p:nvPr><p:ph type="{ph}"/></p:nvPr>' if ph else "<p:nvPr/>"
    paras = "".join(f"<a:p><a:r><a:t>{escape(t)}</a:t></a:r></a:p>" for t in text_lines)
    return f"<p:sp><p:nvSpPr><p:cNvPr id=\"1\" name=\"s\"/><p:cNvSpPr/>{ph_xml}</p:nvSpPr><p:txBody>{paras}</p:txBody></p:sp>"


def make_pptx(path, slides: List[dict]) -> Path:
    """slides: [{"title": str, "lines": [str], "table": rows|None, "notes": str|None, "footer": str|None}]."""
    parts, pres_rels, ids = {}, [], []
    for n, slide in enumerate(slides, 1):
        shapes = [_sp([slide["title"]], "title"), _sp(slide.get("lines", []))]
        if slide.get("footer"):
            shapes.append(_sp([slide["footer"]], "ftr"))
            shapes.append(_sp([str(n)], "sldNum"))
        if slide.get("table"):
            rows = "".join(
                "<a:tr>" + "".join(f"<a:tc><a:txBody><a:p><a:r><a:t>{escape(str(c))}</a:t></a:r></a:p></a:txBody></a:tc>" for c in row) + "</a:tr>"
                for row in slide["table"]
            )
            shapes.append(f"<p:graphicFrame><a:graphic><a:graphicData><a:tbl>{rows}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>")
        parts[f"ppt/slides/slide{n}.xml"] = (
            f'<?xml version="1.0" encoding="UTF-8"?><p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R_NS}">'
            f"<p:cSld><p:spTree>{''.join(shapes)}</p:spTree></p:cSld></p:sld>"
        )
        slide_rels = []
        if slide.get("notes"):
            parts[f"ppt/notesSlides/notesSlide{n}.xml"] = (
                f'<?xml version="1.0" encoding="UTF-8"?><p:notes xmlns:p="{P}" xmlns:a="{A}">'
                f"<p:cSld><p:spTree>{_sp([str(n)], 'sldNum')}{_sp([slide['notes']], 'body')}</p:spTree></p:cSld></p:notes>"
            )
            slide_rels.append(("rId1", "notesSlide", f"../notesSlides/notesSlide{n}.xml"))
        parts[f"ppt/slides/_rels/slide{n}.xml.rels"] = _rels(slide_rels)
        pres_rels.append((f"rId{n}", "slide", f"slides/slide{n}.xml"))
        ids.append(f'<p:sldId id="{255 + n}" r:id="rId{n}"/>')
    parts["ppt/presentation.xml"] = (
        f'<?xml version="1.0" encoding="UTF-8"?><p:presentation xmlns:p="{P}" xmlns:r="{R_NS}">'
        f'<p:sldIdLst>{"".join(ids)}</p:sldIdLst></p:presentation>'
    )
    parts["ppt/_rels/presentation.xml.rels"] = _rels(pres_rels)
    parts["_rels/.rels"] = _rels([("rId1", "officeDocument", "ppt/presentation.xml")])
    parts["[Content_Types].xml"] = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>'
    return _zip(path, parts)


# --------------------------------------------------------------------------- OpenDocument

ODF_NS = (
    'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
    'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
    'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" '
    'xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" '
    'xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"'
)


def _ods_cell(value) -> str:
    if value is None:
        return "<table:table-cell/>"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<table:table-cell office:value-type="float" office:value="{value}"><text:p>{value}</text:p></table:table-cell>'
    return f'<table:table-cell office:value-type="string"><text:p>{escape(str(value))}</text:p></table:table-cell>'


def make_ods(path, sheets: List[Tuple[str, List[list]]]) -> Path:
    tables = []
    for name, rows in sheets:
        xml_rows = "".join(
            "<table:table-row>" + "".join(_ods_cell(v) for v in row)
            + '<table:table-cell table:number-columns-repeated="1000"/></table:table-row>'
            for row in rows
        )
        xml_rows += '<table:table-row table:number-rows-repeated="1048000"><table:table-cell table:number-columns-repeated="1024"/></table:table-row>'
        tables.append(f'<table:table table:name="{escape(name)}">{xml_rows}</table:table>')
    content = (
        f'<?xml version="1.0" encoding="UTF-8"?><office:document-content {ODF_NS}>'
        f"<office:body><office:spreadsheet>{''.join(tables)}</office:spreadsheet></office:body></office:document-content>"
    )
    return _zip(path, {"content.xml": content}, first=("mimetype", "application/vnd.oasis.opendocument.spreadsheet"))


def make_odt(path, blocks: List[tuple]) -> Path:
    body = []
    for block in blocks:
        if block[0] == "h":
            body.append(f'<text:h text:outline-level="{block[1]}">{escape(block[2])}</text:h>')
        elif block[0] == "p":
            body.append(f"<text:p>{escape(block[1])}</text:p>")
        elif block[0] == "li":
            body.append(f"<text:list><text:list-item><text:p>{escape(block[1])}</text:p></text:list-item></text:list>")
    content = (
        f'<?xml version="1.0" encoding="UTF-8"?><office:document-content {ODF_NS}>'
        f"<office:body><office:text>{''.join(body)}</office:text></office:body></office:document-content>"
    )
    return _zip(path, {"content.xml": content}, first=("mimetype", "application/vnd.oasis.opendocument.text"))


# --------------------------------------------------------------------------- EPUB

def make_epub(path, title: str, chapters: List[str]) -> Path:
    manifest, spine, parts = [], [], {}
    for n, html in enumerate(chapters, 1):
        parts[f"OEBPS/ch{n}.xhtml"] = f'<?xml version="1.0" encoding="UTF-8"?><html xmlns="http://www.w3.org/1999/xhtml"><head><title>c</title><style>p{{color:red}}</style></head><body>{html}</body></html>'
        manifest.append(f'<item id="c{n}" href="ch{n}.xhtml" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="c{n}"/>')
    parts["META-INF/container.xml"] = (
        '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    )
    parts["OEBPS/content.opf"] = (
        '<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0">'
        f'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>{escape(title)}</dc:title></metadata>'
        f'<manifest>{"".join(manifest)}</manifest><spine>{"".join(spine)}</spine></package>'
    )
    return _zip(path, parts, first=("mimetype", "application/epub+zip"))


# --------------------------------------------------------------------------- PDF

def _pdf_string(text: str) -> bytes:
    data = text.encode("cp1252", errors="replace")
    return b"(" + data.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)") + b")"


def make_pdf(path, pages: List[List[str]]) -> Path:
    """One list of text lines per page (an empty list makes a page without text)."""
    objects: List[bytes] = []

    def add(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    font = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    pages_id = len(objects) + 1
    objects.append(b"")  # placeholder for the page tree
    kids = []
    for lines in pages:
        ops = [b"BT", b"/F1 11 Tf", b"14 TL", b"56 800 Td"]
        for line in lines:
            ops.append(_pdf_string(line) + b" Tj T*")
        ops.append(b"ET")
        stream = b"\n".join(ops)
        content = add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        kids.append(add(
            b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 %d 0 R >> >> /Contents %d 0 R >>"
            % (pages_id, font, content)
        ))
    objects[pages_id - 1] = b"<< /Type /Pages /Kids [%s] /Count %d >>" % (
        b" ".join(b"%d 0 R" % k for k in kids), len(kids))
    catalog = add(b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id)
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, catalog, xref)
    Path(path).write_bytes(bytes(out))
    return Path(path)
