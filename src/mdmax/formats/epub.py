"""EPUB e-books: chapters in reading order, HTML converted to Markdown."""

from __future__ import annotations

import posixpath
import zipfile
from pathlib import Path

from ..textutil import decode_bytes, html_to_markdown
from . import Converted
from .xmlutil import attr, child, children, descendants, has, read_xml, resolve


def convert_epub(path: Path, table_format: str = "auto") -> Converted:
    with zipfile.ZipFile(path) as zf:
        if not has(zf, "META-INF/container.xml"):
            raise ValueError("not a valid EPUB file (META-INF/container.xml missing)")
        container = read_xml(zf, "META-INF/container.xml")
        rootfile = next(descendants(container, "rootfile"), None)
        opf_path = attr(rootfile, "full-path") if rootfile is not None else None
        if not opf_path or not has(zf, opf_path):
            raise ValueError("EPUB package document not found")
        opf = read_xml(zf, opf_path)
        base = posixpath.dirname(opf_path)
        manifest = {}
        man_el = child(opf, "manifest")
        for item in children(man_el, "item") if man_el is not None else []:
            manifest[attr(item, "id")] = (attr(item, "href", "") or "", attr(item, "media-type", "") or "")
        title = None
        meta = child(opf, "metadata")
        if meta is not None:
            t = next(descendants(meta, "title"), None)
            title = (t.text or "").strip() if t is not None else None
        chapters = []
        spine = child(opf, "spine")
        for ref in children(spine, "itemref") if spine is not None else []:
            if attr(ref, "linear", "yes") == "no":
                continue
            href, media = manifest.get(attr(ref, "idref"), ("", ""))
            if not href or "html" not in media:
                continue
            part = resolve(base, href.split("#")[0])
            if not has(zf, part):
                continue
            text = html_to_markdown(decode_bytes(zf.read(part)), table_format)
            if text.strip():
                chapters.append(text)
    body = "\n\n".join(chapters)
    if title:
        body = f"Title: {title}\n\n{body}"
    return Converted(text=body)
