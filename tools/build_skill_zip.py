"""Builds dist/mdmax-skill.zip: the skill for claude.ai (Settings > Capabilities > Skills).

The zip holds SKILL.md, the launcher and a copy of the mdmax package, because the
claude.ai sandbox cannot install packages. Only fields of the Agent Skills spec are
kept in the frontmatter (claude.ai rejects Claude Code extensions).

    python tools/build_skill_zip.py
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "mdmax"
PACKAGE = ROOT / "src" / "mdmax"
ALLOWED_FIELDS = ("name", "description", "license", "compatibility")


def skill_md_for_claude_ai() -> str:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise SystemExit("SKILL.md has no frontmatter")
    kept = [line for line in match.group(1).splitlines() if line.split(":", 1)[0].strip() in ALLOWED_FIELDS]
    body = text[match.end():]
    # ${CLAUDE_SKILL_DIR} is a Claude Code substitution; on claude.ai Claude knows the folder.
    body = body.replace('"${CLAUDE_SKILL_DIR}/scripts/mdmax_run.py"', "<skill folder>/scripts/mdmax_run.py")
    body = body.replace("`${CLAUDE_SKILL_DIR}` is the folder of this SKILL.md.", "`<skill folder>` is the folder of this SKILL.md.")
    return "---\n" + "\n".join(kept) + "\n---\n" + body


def build(out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mdmax/SKILL.md", skill_md_for_claude_ai())
        zf.write(SKILL / "scripts" / "mdmax_run.py", "mdmax/scripts/mdmax_run.py")
        for file in sorted(PACKAGE.rglob("*.py")):
            rel = file.relative_to(PACKAGE.parent).as_posix()
            zf.write(file, f"mdmax/scripts/lib/{rel}")
    return out


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "mdmax-skill.zip"
    print(build(target))
