"""Entry point used by hooks/run.sh: puts the plugin's copy of mdmax on the path."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
_data = os.environ.get("CLAUDE_PLUGIN_DATA")
if _data and os.path.isdir(os.path.join(_data, "lib")):
    sys.path.insert(1, os.path.join(_data, "lib"))

_mode = sys.argv[1] if len(sys.argv) > 1 else "read"
if _mode == "setup":
    from mdmax.plugin_setup import main
elif _mode == "mcp":
    from mdmax.mcp_server import main
else:
    from mdmax.hook import main

sys.exit(main())
