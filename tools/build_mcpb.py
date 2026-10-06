"""Builds dist/mdmax.mcpb: the one-click extension for Claude Desktop.

It uses the "uv" server type: Claude Desktop installs Python and the dependencies by
itself, so the user needs nothing else. The bundle carries the mdmax package and a
small pyproject.toml with the dependencies.

    python tools/build_mcpb.py
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "mdmax"


def version() -> str:
    text = (PACKAGE / "__init__.py").read_text(encoding="utf-8")
    return re.search(r'__version__ = "([^"]+)"', text).group(1)


def manifest(ver: str) -> dict:
    sys.path.insert(0, str(ROOT / "src"))
    from mdmax.mcp_server import TOOLS

    return {
        "manifest_version": "0.4",
        "name": "mdmax",
        "display_name": "mdmax",
        "version": ver,
        "description": "Reads PDF, Office, OpenDocument, EPUB, CSV, JSON and HTML files as compact text, so Claude spends far fewer tokens on them.",
        "long_description": (
            "mdmax converts local documents into compact Markdown/CSV before Claude reads them and reports "
            "the tokens saved. PDFs are sent as text instead of text plus one image per page; spreadsheets "
            "as CSV instead of padded tables; JSON without indentation or repeated keys. No data leaves "
            "your computer."
        ),
        "author": {"name": "Bruno Madeira", "url": "https://github.com/brnmadeira"},
        "repository": {"type": "git", "url": "https://github.com/brnmadeira/mdmax"},
        "homepage": "https://github.com/brnmadeira/mdmax",
        "license": "MIT",
        "keywords": ["tokens", "pdf", "excel", "word", "markdown"],
        "server": {
            "type": "uv",
            "entry_point": "src/server.py",
            "mcp_config": {"command": "uv", "args": ["run", "--directory", "${__dirname}", "src/server.py"]},
        },
        "tools": [{"name": t["name"], "description": t["description"]} for t in TOOLS],
        "compatibility": {"platforms": ["darwin", "win32", "linux"], "runtimes": {"python": ">=3.10"}},
    }


PYPROJECT = """[project]
name = "mdmax-desktop-extension"
version = "{ver}"
requires-python = ">=3.10"
dependencies = ["pypdf>=4", "xlrd>=2"]
"""

SERVER = '''"""Claude Desktop entry point: runs the mdmax MCP server from the bundled package."""
import sys

from mdmax.mcp_server import main

sys.exit(main())
'''


def build(out: Path) -> Path:
    ver = version()
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest(ver), indent=2, ensure_ascii=False))
        zf.writestr("pyproject.toml", PYPROJECT.format(ver=ver))
        zf.writestr("src/server.py", SERVER)
        zf.write(ROOT / "LICENSE", "LICENSE")
        for file in sorted(PACKAGE.rglob("*.py")):
            zf.write(file, "src/" + file.relative_to(PACKAGE.parent).as_posix())
    return out


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "mdmax.mcpb"
    print(build(target))
