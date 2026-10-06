"""Where mdmax keeps its files: the savings log and the conversion cache.

Everything lives in ``MDMAX_HOME`` (default ``~/.mdmax``). The log stores only file
names and numbers, never document content.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from . import __version__

CACHE_MAX_AGE_DAYS = 30


def home() -> Path:
    custom = os.environ.get("MDMAX_HOME", "").strip()
    return Path(custom).expanduser() if custom else Path.home() / ".mdmax"


def _log_path() -> Path:
    return home() / "savings.jsonl"


def record(result, source: str) -> None:
    """Append one conversion to the savings log. Never raises."""
    try:
        entry = {
            "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "source": source,
            "file": result.path.name,
            "format": result.fmt,
            "tokens": result.tokens,
            "baseline": result.baseline_tokens,
            "baseline_kind": result.baseline_kind,
            "method": result.method,
        }
        path = _log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def entries() -> List[dict]:
    path = _log_path()
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def summary() -> Dict:
    rows = entries()
    by_format: Dict[str, Dict[str, int]] = defaultdict(lambda: {"files": 0, "tokens": 0, "baseline": 0, "saved": 0})
    totals = {"files": len(rows), "compared": 0, "tokens": 0, "baseline": 0, "saved": 0, "exact": 0}
    for row in rows:
        f = by_format[row.get("format", "?")]
        f["files"] += 1
        f["tokens"] += row.get("tokens") or 0
        totals["tokens"] += row.get("tokens") or 0
        if row.get("method") == "exact":
            totals["exact"] += 1
        if row.get("baseline") is not None:
            saved = row["baseline"] - (row.get("tokens") or 0)
            f["baseline"] += row["baseline"]
            f["saved"] += saved
            totals["compared"] += 1
            totals["baseline"] += row["baseline"]
            totals["saved"] += saved
    return {"totals": totals, "by_format": dict(by_format), "first": rows[0]["at"] if rows else None}


def reset() -> None:
    path = _log_path()
    if path.exists():
        path.unlink()


# ---------------------------------------------------------------------------
# Conversion cache (used by the Claude Code hook and the MCP server)
# ---------------------------------------------------------------------------

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def cache_key(path: Path, **options) -> str:
    st = path.stat()
    raw = json.dumps(
        [str(path.resolve()), st.st_size, st.st_mtime_ns, __version__, sorted(options.items())],
        ensure_ascii=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def output_name(path: Path, pages: Optional[str] = None) -> str:
    stem = _SAFE.sub("_", path.name)[:80]
    suffix = f".p{_SAFE.sub('_', pages)}" if pages else ""
    return f"{stem}{suffix}.md"


def cache_dir() -> Path:
    return home() / "cache"


def cached(key: str) -> Optional[dict]:
    meta = cache_dir() / f"{key}.json"
    if not meta.exists():
        return None
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
        if Path(data["md_path"]).exists():
            return data
    except (ValueError, KeyError, OSError):
        pass
    return None


def store(key: str, md_path: Path, result) -> dict:
    data = {
        "md_path": str(md_path),
        "tokens": result.tokens,
        "baseline": result.baseline_tokens,
        "baseline_kind": result.baseline_kind,
        "method": result.method,
        "pages": result.pages,
        "format": result.fmt,
        "warnings": result.warnings,
    }
    folder = cache_dir()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{key}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def prune_cache(max_age_days: int = CACHE_MAX_AGE_DAYS) -> None:
    folder = cache_dir()
    if not folder.exists():
        return
    limit = time.time() - max_age_days * 86400
    for item in folder.iterdir():
        try:
            if item.stat().st_mtime < limit:
                item.unlink()
        except OSError:
            continue
