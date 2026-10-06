#!/bin/sh
# Starts mdmax from the plugin folder with a working Python 3.
#   run.sh read   - PreToolUse hook for Read (event JSON on stdin)
#   run.sh setup  - SessionStart: remember the Python, install pypdf/xlrd if missing
#   run.sh mcp    - MCP server over stdio
# Any failure exits 0 without output, so a Read is never blocked.

ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
ENTRY="$ROOT/hooks/entry.py"
MODE="${1:-read}"

if [ "$MODE" = "read" ]; then
  INPUT=$(cat)
  # Cheap filter before starting Python: only documents mdmax converts.
  case "$INPUT" in
    *.[pP][dD][fF]\"*|*.[dD][oO][cC][xX]\"*|*.[pP][pP][tT][xX]\"*|*.[xX][lL][sS]\"*|*.[xX][lL][sS][xXmM]\"*|*.[oO][dD][sStTpP]\"*|*.[eE][pP][uU][bB]\"*) ;;
    *) exit 0 ;;
  esac
fi

PY=""
if [ -n "$CLAUDE_PLUGIN_DATA" ] && [ -f "$CLAUDE_PLUGIN_DATA/python" ]; then
  PY=$(cat "$CLAUDE_PLUGIN_DATA/python")
  [ -f "$PY" ] || PY=""
fi
if [ -z "$PY" ]; then
  for candidate in python3 python py; do
    if command -v "$candidate" >/dev/null 2>&1 &&
       "$candidate" -c "import sys; sys.exit(sys.version_info < (3, 9))" >/dev/null 2>&1; then
      PY="$candidate"
      break
    fi
  done
fi
[ -z "$PY" ] && exit 0

if [ "$MODE" = "read" ]; then
  printf '%s' "$INPUT" | "$PY" "$ENTRY" read
  exit 0
fi
exec "$PY" "$ENTRY" "$MODE"
