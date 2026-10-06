"""SessionStart step of the Claude Code plugin (runs in the background).

1. Remembers which Python works, so each Read hook starts one process, not several.
2. If pypdf (PDF) or xlrd (old .xls) are missing, installs them once into the plugin's
   own data folder (``$CLAUDE_PLUGIN_DATA/lib``), the place Claude Code documents for
   plugin dependencies. Nothing is installed system-wide. Set MDMAX_NO_AUTO_INSTALL=1
   to skip it; a failed attempt is retried after a week.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PACKAGES = {"pypdf": "pypdf>=4", "xlrd": "xlrd>=2"}
RETRY_DAYS = 7


def _missing(lib: Path) -> list:
    if lib.is_dir() and str(lib) not in sys.path:
        sys.path.insert(0, str(lib))
    return [spec for name, spec in PACKAGES.items() if importlib.util.find_spec(name) is None]


def main() -> int:
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not data:
        return 0
    data_dir = Path(data)
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "python").write_text(sys.executable.replace("\\", "/"), encoding="utf-8")

    if os.environ.get("MDMAX_NO_AUTO_INSTALL", "").strip().lower() in ("1", "true", "yes", "on"):
        return 0
    lib = data_dir / "lib"
    missing = _missing(lib)
    if not missing:
        return 0
    state_file = data_dir / "setup.json"
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    if time.time() - state.get("last_attempt", 0) < RETRY_DAYS * 86400:
        return 0
    state["last_attempt"] = time.time()
    try:
        done = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
             "--no-warn-script-location", "--target", str(lib), *missing],
            capture_output=True, text=True, timeout=300,
        )
        state["result"] = "ok" if done.returncode == 0 else (done.stderr or done.stdout)[-500:]
    except Exception as exc:  # no pip, no network, timeout
        state["result"] = f"{type(exc).__name__}: {exc}"
    state_file.write_text(json.dumps(state), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
