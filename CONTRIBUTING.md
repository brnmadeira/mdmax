# Contributing

Thanks for helping. A few rules keep mdmax useful:

1. **Never lose data.** A conversion may drop formatting and repetition, never content. A new
   optimization needs a test showing that every value survives.
2. **No new dependencies in the core.** It must run in the claude.ai sandbox, where nothing can
   be installed. New formats are read with the standard library when possible.
3. **Honest numbers.** Savings are measured against what Claude would really spend, and every
   estimate is marked as one. Update `BENCHMARK.md` (`python tools/benchmark.py --write`) when
   a change moves the numbers.

## Setup

```bash
pip install -e ".[test]"
pytest
```

Tests build their documents with `tests/fixtures.py`; no binary fixtures in the repository.
To check a change against real files without committing them:
`python tools/benchmark.py path/to/file.pdf path/to/sheet.xlsx`.

## Layout

- `src/mdmax/` - the package: `convert.py` (dispatch and measurement), `formats/` (one module per
  family), `tables.py`, `tokens.py`, `storage.py` (log and cache), `cli.py`, `hook.py`
  (Claude Code), `mcp_server.py`, `plugin_setup.py`.
- `skills/mdmax/` - the skill (Claude Code and claude.ai).
- `hooks/` - the Claude Code hooks (`hooks.json`, `run.sh`, `entry.py`).
- `.claude-plugin/` - plugin and marketplace manifests. `.mcp.json` - the plugin's MCP server.
- `tools/` - benchmark and the builders of the claude.ai zip and the Claude Desktop extension.

Before a pull request: `pytest`, `claude plugin validate .` if you touched the plugin, and the
two build scripts if you touched the skill or the MCP server.
