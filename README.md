# mdmax

**Documents as compact text for Claude: fewer tokens, nothing dropped.**

[Português](README.pt-BR.md) · [Benchmark](BENCHMARK.md) · [Changelog](CHANGELOG.md)

mdmax converts PDF, Word, Excel, PowerPoint, OpenDocument, EPUB, JSON, HTML and CSV files
into compact Markdown/CSV before Claude reads them, and tells you how many tokens that saved.
It runs in Claude Code, Claude Desktop, claude.ai and the terminal, with nothing to configure.

| Document ([benchmark](BENCHMARK.md)) | Without mdmax | With mdmax | Saved |
|---|---:|---:|---:|
| PDF report, 12 pages | ~28,557 | ~9,481 | 67% |
| JSON API export, 300 records | ~23,214 | ~6,743 | 71% |
| Web page | ~4,725 | ~1,979 | 58% |
| Spreadsheet, 500 rows (vs a Markdown table) | ~17,778 | ~13,669 | 23% |
| CSV export, 1,000 rows | ~17,107 | ~14,844 | 13% |

Where the savings come from, without summarizing anything:

- **PDF**: when Claude reads a PDF it gets the text *and an image of every page*. For text
  documents the image is most of the bill; mdmax sends the text and removes running headers,
  footers and page numbers. Scanned and mostly visual PDFs (posters, flyers) are left alone,
  because there the image is the content.
- **Spreadsheets** (xlsx, xlsm, xls, ods): one CSV block per sheet, with the computed values
  (not formulas), zeros kept, dates as `2026-10-01`, percentages as `12.5%`, hidden sheets skipped
  unless asked.
- **Word, PowerPoint, OpenDocument, EPUB**: Markdown with headings, lists, tables, links, slide
  titles and speaker notes; no styling, no slide numbers or footers.
- **JSON**: lists of records become a table (keys written once), everything else is minified.
- **HTML**: text, headings, links and tables; scripts, styles and navigation markup go.
- **CSV**: re-written with the delimiter that needs the fewest quotes, empty rows and columns removed.

Every table is rendered both as CSV and as a Markdown table, and the shorter one wins.

## Install

| Where | How |
|---|---|
| **Claude Code** | `/plugin marketplace add brnmadeira/mdmax` then `/plugin install mdmax@mdmax` |
| **Claude Desktop** | download `mdmax.mcpb` from [Releases](https://github.com/brnmadeira/mdmax/releases) and open it |
| **claude.ai** | download `mdmax-skill.zip` from [Releases](https://github.com/brnmadeira/mdmax/releases), then Settings > Capabilities > Skills > Upload |
| **Terminal** | `uvx --from git+https://github.com/brnmadeira/mdmax mdmax report.pdf` or `pip install git+https://github.com/brnmadeira/mdmax` |
| **Any MCP client** | command `uvx`, arguments `--from git+https://github.com/brnmadeira/mdmax mdmax-mcp` |

Requirements: Python 3.9+. The core uses only the standard library; `pypdf` (PDF) and `xlrd`
(old .xls) are small pure-Python packages. Claude Desktop installs everything itself.

### Claude Code

The plugin brings three things:

1. **Automatic conversion.** When Claude uses Read on a PDF, Office, OpenDocument or EPUB file,
   a hook converts it and Read returns the compact text, with a note to Claude saying so.
   Reading the same file again in the session returns the original, for when Claude needs to
   see a chart. Text files (CSV, JSON, Markdown...) are never touched, so Claude can still edit them.
   The hook respects your `deny` and `ask` permission rules: if one could cover the file, it steps aside.
2. **The `mdmax` skill**, for CSV/JSON/HTML, saving a converted file, and the savings report.
3. **An MCP server** with `convert_document` and `token_savings` (needs [uv](https://docs.astral.sh/uv/)).

On the first session the plugin installs `pypdf` and `xlrd` into its own data folder
(`~/.claude/plugins/data/...`), nothing system-wide; set `MDMAX_NO_AUTO_INSTALL=1` to skip.
Turn the automatic conversion off with `MDMAX_HOOK=off`. On Windows the hook runs in Git Bash.

## Use it in the terminal

```bash
mdmax report.pdf                      # writes report.md and prints the savings
mdmax convert *.xlsx -o converted/    # several files
mdmax convert manual.pdf --pages 1-20 --stdout
mdmax stats                           # tokens saved so far, per format
mdmax doctor                          # what is installed
```

```
OK    relatorio.pdf -> relatorio.md
      12 page(s) | ~9,481 tokens | saves ~19,076 (67%) vs reading the PDF directly (text + page images, estimated) (~28,557) | [estimated]
      note: 24 repeated header/footer/page-number line(s) removed
```

## How tokens are counted

- **By default, estimated** offline at 2.2 characters per token. This was calibrated in October
  2026 against real counts from the tokenizer of Claude Opus 4.7 and later (mean error about 8%).
  Older models produce fewer tokens, so for them the numbers run high. Percentages compare two
  texts measured the same way and are more reliable than the absolute numbers. Estimates are
  marked with `~`.
- **Exactly**, with the Anthropic [`count_tokens`](https://platform.claude.com/docs/en/build-with-claude/token-counting)
  endpoint (free): `pip install "mdmax[exact]"`, set `ANTHROPIC_API_KEY`, and use `--exact` or
  `MDMAX_EXACT_TOKENS=1`. For PDFs this counts what the PDF itself costs, images included.
  `MDMAX_MODEL` picks the model (default `claude-opus-5-5`).
- OpenAI's tokenizer (`tiktoken`) is not used: it undercounts Claude tokens.

The savings log (`~/.mdmax/savings.jsonl`, or `MDMAX_HOME`) holds file names and numbers only,
never content. Everything runs on your computer; only `--exact` sends text to the Anthropic API.

## What mdmax does not do

- **Images and scanned pages**: Claude reads images directly and better than OCR would.
- **Summaries**: nothing is dropped or rewritten. Every cell, paragraph and slide is kept.
- Charts inside documents are not described; read the original page when they matter.

## Related projects

- [markitdown](https://github.com/microsoft/markitdown) (Microsoft) converts more formats, including
  audio, with optional Azure services; mdmax focuses on token cost and needs no dependencies.
- [docling](https://github.com/docling-project/docling) uses ML models for complex PDF layouts and tables.
- [ccusage](https://github.com/ryoppippi/ccusage) reports your overall Claude Code usage; mdmax reports
  what it saved on documents.
- [rtk](https://github.com/rtk-ai/rtk) trims Bash output and [caveman](https://github.com/JuliusBrussee/caveman)
  shortens answers: different sources of tokens, so they combine well with mdmax.

## Development

```bash
pip install -e ".[test]"
pytest                               # no fixture files needed: tests/fixtures.py builds them
python tools/benchmark.py --write    # updates BENCHMARK.md
python tools/build_skill_zip.py      # dist/mdmax-skill.zip (claude.ai)
python tools/build_mcpb.py           # dist/mdmax.mcpb (Claude Desktop)
claude plugin validate .             # the Claude Code marketplace and plugin
```

Pushing a tag `v*` runs the tests and attaches both files to a GitHub release.
See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, Bruno Madeira.
