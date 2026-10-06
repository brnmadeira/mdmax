"""Claude Code PreToolUse hook for the Read tool.

When Claude is about to read a PDF, Word, Excel, PowerPoint, OpenDocument or EPUB file,
the file is converted and Read is pointed at the compact text instead. Claude gets a
note saying so, and can still see the original by reading the same file again
(the second read in a session is passed through untouched).

Design rules:
* never block a Read: any problem means "do nothing" (exit 0, no output);
* never get around the user's permission rules: if a deny or ask rule could match the
  original file, the hook steps aside and the normal flow decides;
* text formats (CSV, JSON, Markdown...) are not touched, so Claude can still edit them.

Turn it off with the environment variable MDMAX_HOOK=off.
"""

from __future__ import annotations

import fnmatch
import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Iterable, List, Optional

from . import storage
from .convert import BINARY_EXTENSIONS, MissingDependency, NotConvertible, convert

MAX_PDF_PAGES_WITHOUT_RANGE = 400
# A text page has thousands of characters; posters, flyers and slide decks have a few
# hundred, and for those the page image is the content. Below this the hook steps aside.
HOOK_MIN_PDF_CHARS = 400


def _min_pdf_chars() -> int:
    try:
        return int(os.environ.get("MDMAX_HOOK_MIN_PDF_CHARS", HOOK_MIN_PDF_CHARS))
    except ValueError:
        return HOOK_MIN_PDF_CHARS


def _log(message: str) -> None:
    try:
        path = storage.home() / "hook.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + message.rstrip() + "\n")
    except Exception:
        pass


# --------------------------------------------------------------------------- permissions

def _managed_settings() -> List[Path]:
    if sys.platform == "win32":
        return [Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "ClaudeCode" / "managed-settings.json"]
    if sys.platform == "darwin":
        return [Path("/Library/Application Support/ClaudeCode/managed-settings.json")]
    return [Path("/etc/claude-code/managed-settings.json")]


def _settings_files(project: Optional[Path]) -> List[Path]:
    files = [Path.home() / ".claude" / "settings.json", Path.home() / ".claude" / "settings.local.json"]
    if project:
        files += [project / ".claude" / "settings.json", project / ".claude" / "settings.local.json"]
    return files + _managed_settings()


def _read_rules(files: Iterable[Path]) -> List[str]:
    rules: List[str] = []
    for file in files:
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        perms = data.get("permissions") or {}
        for key in ("deny", "ask"):
            for rule in perms.get(key) or []:
                if isinstance(rule, str):
                    rules.append(rule.strip())
    return rules


def _rule_may_match(rule: str, target: Path, project: Optional[Path]) -> bool:
    """Conservative: True whenever the rule could cover the file (false positives are fine)."""
    if rule in ("Read", "Read(*)", "Read(**)"):
        return True
    if not (rule.startswith("Read(") and rule.endswith(")")):
        return False
    pattern = rule[5:-1].strip().replace("\\", "/")
    for prefix in ("//", "~/", "./", "/"):
        if pattern.startswith(prefix):
            if prefix == "~/":
                pattern = str(Path.home()).replace("\\", "/") + "/" + pattern[2:]
            else:
                pattern = pattern[len(prefix):]
            break
    pattern = pattern.replace("**/", "*").replace("**", "*")
    absolute = str(target).replace("\\", "/")
    candidates = [absolute, target.name]
    if project:
        try:
            candidates.append(str(target.relative_to(project)).replace("\\", "/"))
        except ValueError:
            pass
    for cand in candidates:
        if fnmatch.fnmatch(cand.lower(), pattern.lower()) or fnmatch.fnmatch(cand.lower(), "*/" + pattern.lower()):
            return True
    return False


def _blocked_by_rules(target: Path, project: Optional[Path]) -> bool:
    return any(_rule_may_match(rule, target, project) for rule in _read_rules(_settings_files(project)))


# --------------------------------------------------------------------------- session memory

def _seen_path(session_id: str) -> Path:
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")[:80] or "nosession"
    return storage.home() / "sessions" / f"{safe}.json"


def _already_converted(session_id: str, key: str) -> bool:
    try:
        return key in json.loads(_seen_path(session_id).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False


def _remember(session_id: str, key: str) -> None:
    path = _seen_path(session_id)
    try:
        seen = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        seen = []
    seen.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(seen[-500:]), encoding="utf-8")


def _prune_sessions(max_age_days: int = 7) -> None:
    folder = storage.home() / "sessions"
    if not folder.exists():
        return
    limit = time.time() - max_age_days * 86400
    for item in folder.iterdir():
        try:
            if item.stat().st_mtime < limit:
                item.unlink()
        except OSError:
            pass


# --------------------------------------------------------------------------- main

def _within(path: Path, folder: Optional[Path]) -> bool:
    if not folder:
        return False
    try:
        path.resolve().relative_to(folder.resolve())
        return True
    except (ValueError, OSError):
        return False


def handle(event: dict) -> Optional[dict]:
    if os.environ.get("MDMAX_HOOK", "").strip().lower() in ("off", "0", "false", "no"):
        return None
    if event.get("hook_event_name") not in (None, "PreToolUse") or event.get("tool_name") != "Read":
        return None
    tool_input = dict(event.get("tool_input") or {})
    raw_path = tool_input.get("file_path")
    if not raw_path:
        return None
    original = Path(raw_path)
    ext = original.suffix.lower()
    if ext not in BINARY_EXTENSIONS or not original.is_file():
        return None
    pages = tool_input.get("pages") or None
    if pages is not None:
        pages = str(pages)
    if ext != ".pdf":
        pages = None

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or ""
    project = Path(project_dir) if project_dir else None
    if _blocked_by_rules(original, project):
        _log(f"skip (a deny/ask rule may cover it): {original}")
        return None

    key = storage.cache_key(original, pages=pages or "")
    session = str(event.get("session_id") or "")
    if session and _already_converted(session, key):
        _log(f"pass-through (second read in session): {original}")
        return None

    if ext == ".pdf" and not pages:
        from .formats.pdf import page_count

        count = page_count(original)
        if count and count > MAX_PDF_PAGES_WITHOUT_RANGE:
            return None

    info = storage.cached(key)
    skip_marker = storage.cache_dir() / f"{key}.skip"
    if info is None and skip_marker.exists():
        return None
    if info is None:
        try:
            result = convert(original, pages=pages, min_pdf_chars=_min_pdf_chars())
        except NotConvertible as exc:  # scanned or visual PDF, empty file: remember, don't retry
            _log(f"skip {original.name}: {exc}")
            skip_marker.parent.mkdir(parents=True, exist_ok=True)
            skip_marker.write_text(str(exc), encoding="utf-8")
            return None
        except (MissingDependency, ValueError) as exc:
            _log(f"skip {original.name}: {exc}")
            return None
        scratch = event.get("scratchpad_dir")
        folder = Path(scratch) / "mdmax" if scratch else storage.cache_dir()
        folder.mkdir(parents=True, exist_ok=True)
        md_path = folder / f"{key}-{storage.output_name(original, pages)}"
        md_path.write_text(result.text, encoding="utf-8")
        info = storage.store(key, md_path, result)
        storage.record(result, "hook")
        storage.prune_cache()
    if session:
        _remember(session, key)

    md_path = Path(info["md_path"])
    new_input = {k: v for k, v in tool_input.items() if k != "pages"}
    new_input["file_path"] = str(md_path)

    approx = "~" if info.get("method") != "exact" else ""
    what = f"{original.name}" + (f" (pages {pages})" if pages else "")
    note = f"mdmax: this Read shows a compact text version of {what} at {md_path}"
    if info.get("baseline") is not None and info.get("baseline_kind", "").startswith("pdf"):
        note += f": {approx}{info['tokens']:,} tokens instead of {approx}{info['baseline']:,} for the PDF with page images"
    else:
        note += f" ({approx}{info['tokens']:,} tokens)"
    note += (
        ". Images and charts are not included. To see the original, Read the same file "
        "again with the same arguments: the second read is not converted."
    )
    if info.get("warnings"):
        note += " Notes: " + "; ".join(info["warnings"]) + "."

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": new_input,
            "additionalContext": note,
        }
    }
    # The converted copy lives outside the project when there is no session scratchpad.
    # Reading the original inside the project needs no prompt, so neither should its copy.
    if not event.get("scratchpad_dir") and _within(original, project):
        output["hookSpecificOutput"]["permissionDecision"] = "allow"
        output["hookSpecificOutput"]["permissionDecisionReason"] = "mdmax: converted copy of a project file"
    return output


def main() -> int:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        event = json.loads(raw) if raw.strip() else {}
        output = handle(event)
        if output:
            sys.stdout.buffer.write(json.dumps(output, ensure_ascii=False).encode("utf-8"))
            sys.stdout.flush()
        if event.get("session_id") and int(time.time()) % 50 == 0:
            _prune_sessions()
    except Exception:
        _log("error: " + traceback.format_exc())
    return 0


if __name__ == "__main__":
    sys.exit(main())
