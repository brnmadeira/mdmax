"""Small helpers for the zipped-XML formats (OOXML, OpenDocument, EPUB)."""

from __future__ import annotations

import posixpath
import zipfile
from typing import Dict, Iterator, Optional
from urllib.parse import unquote
from xml.etree import ElementTree as ET


def local(tag) -> str:
    """Tag or attribute name without its namespace."""
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def attr(el, name: str, default: Optional[str] = None) -> Optional[str]:
    """Attribute by local name, whatever its namespace."""
    if name in el.attrib:
        return el.attrib[name]
    for key, value in el.attrib.items():
        if local(key) == name:
            return value
    return default


def rel_id(el) -> Optional[str]:
    """The r:id / r:embed attribute (namespace differs between transitional and strict)."""
    for key, value in el.attrib.items():
        if key.startswith("{") and "relationships" in key and local(key) in ("id", "embed"):
            return value
    return None


def children(el, name: str) -> Iterator:
    for child in el:
        if local(child.tag) == name:
            yield child


def child(el, name: str):
    for c in el:
        if local(c.tag) == name:
            return c
    return None


def descendants(el, name: str) -> Iterator:
    for d in el.iter():
        if local(d.tag) == name:
            yield d


def read_xml(zf: zipfile.ZipFile, name: str):
    with zf.open(name) as fh:
        return ET.parse(fh).getroot()


def has(zf: zipfile.ZipFile, name: str) -> bool:
    try:
        zf.getinfo(name)
        return True
    except KeyError:
        return False


def resolve(base_dir: str, target: str) -> str:
    target = unquote(target)
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(base_dir, target))


def relationships(zf: zipfile.ZipFile, part: str) -> Dict[str, dict]:
    """Relationships of a part: id -> {"target": path or URL, "type": ..., "external": bool}."""
    base_dir, name = posixpath.split(part)
    rels_name = posixpath.join(base_dir, "_rels", name + ".rels")
    if not has(zf, rels_name):
        return {}
    out = {}
    for rel in read_xml(zf, rels_name):
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target", "")
        external = rel.attrib.get("TargetMode") == "External"
        out[rid] = {
            "target": target if external else resolve(base_dir, target),
            "type": rel.attrib.get("Type", ""),
            "external": external,
        }
    return out
