# Changelog

## 4.0.0 - 2026-10-06

A rewrite. Earlier versions only ran on the author's machine, and on common files they produced
output larger than the input, lost data and over-reported savings. 4.0 fixes that and installs
the same way in every Claude.

### Runs in every Claude
- Claude Code plugin and marketplace (`/plugin marketplace add brnmadeira/mdmax`): skill,
  automatic conversion when Claude reads a document (PreToolUse hook on Read), and an MCP server.
- Claude Desktop extension (`mdmax.mcpb`, uv runtime: Desktop installs Python and dependencies).
- claude.ai skill (`mdmax-skill.zip`), self-contained, using only libraries the sandbox has.
- `uvx`/`pip install` from GitHub for the terminal and any MCP client.

### Conversion
- Standard-library readers for XLSX, DOCX, PPTX, ODS, ODT, ODP and EPUB; `pypdf` for PDF and
  `xlrd` for .xls are the only dependencies (both pure Python).
- Spreadsheets: computed values instead of formulas, zeros kept (were turned into empty cells),
  dates and percentages formatted, duplicate rows kept (were deleted), hidden sheets skipped by default.
- PDF: running headers, footers and page numbers removed; page ranges; scanned and mostly visual
  PDFs detected and left to Claude.
- JSON: lists of records become a table; other JSON is minified (was pretty-printed, making it larger).
- CSV/TSV: delimiter kept or chosen to avoid quoting (was converted into a larger Markdown table).
- Word headings in any language, lists, tables, links; PowerPoint titles, tables and speaker notes;
  EPUB chapters in reading order (were returned empty).
- Each table rendered as CSV or Markdown, whichever is shorter.

### Token counting
- Estimate calibrated on the current Claude tokenizer (2.2 characters per token, about 8% error).
  The old formula was off by a factor of 1,000.
- Exact counts with the free `count_tokens` endpoint (`--exact`); the old code sent a paid
  message to a model id that does not exist.
- PDFs are compared with what reading the PDF directly costs (text plus page images), not with
  the file size in bytes.
- `mdmax stats`: savings log with names and numbers only.

### Removed
- REST API, Docker image, HTML dashboard, OCR and AI summarization (lossy, and outside what a
  token-saving converter should do), and personal configuration files that had been committed.

## 3.x and earlier

See the git history. 3.1 lived on the `master` branch, kept as the tag `v3.1-archive`.
