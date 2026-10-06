#!/usr/bin/env python3
"""Runs mdmax from wherever this skill lives: Claude Code plugin, ~/.claude/skills,
a repository checkout, or the claude.ai upload (which bundles the code in ./lib)."""

import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for candidate in (
    os.path.join(HERE, "lib"),  # zip built by tools/build_skill_zip.py
    os.path.normpath(os.path.join(HERE, "..", "..", "..", "src")),  # plugin / repository
):
    if os.path.isdir(os.path.join(candidate, "mdmax")):
        sys.path.insert(0, candidate)
        break

# pypdf and xlrd installed by the Claude Code plugin into its data folder
for lib in glob.glob(os.path.join(os.path.expanduser("~"), ".claude", "plugins", "data", "*mdmax*", "lib")):
    sys.path.append(lib)

from mdmax.cli import main  # noqa: E402

sys.exit(main())
