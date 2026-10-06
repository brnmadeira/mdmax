---
name: mdmax
description: Converts PDF, Word, Excel, PowerPoint, OpenDocument, EPUB, CSV, JSON and HTML files into compact text before reading them, so they cost far fewer tokens, and reports the tokens saved. Use it whenever a file like that has to be read, summarized or analyzed, and when the user asks how many tokens a document costs or how much mdmax has saved.
license: MIT
allowed-tools: Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/mdmax_run.py" *) Bash(python "${CLAUDE_SKILL_DIR}/scripts/mdmax_run.py" *)
---

# mdmax

## Convert, then read the result

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/mdmax_run.py" convert "<file>" -o "<file>.md"
```

`${CLAUDE_SKILL_DIR}` is the folder of this SKILL.md. Use `python` where `python3` does not exist (Windows).

- Several files: `convert a.pdf b.xlsx -o <folder>`
- Some PDF pages only: `--pages 1-5,8`
- Hidden spreadsheet tabs: `--include-hidden`
- Exact token count with the Anthropic API: `--exact` (needs the `anthropic` package and an API key)

The command prints a summary such as `~4,210 tokens | saves ~19,290 (82%) vs reading the PDF directly`. Read the output file, then tell the user the savings in one sentence. `~` marks an estimate.

## When to read the original instead

- mdmax reports a scanned PDF (no text layer): read the PDF directly.
- The question is about charts, images or layout: read those pages of the original.
- A CSV, JSON or Markdown file you are going to edit: read the original.

## Savings so far

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/mdmax_run.py" stats
```

## Problems

- "PDF needs pypdf": `pip install pypdf`. ".xls files need xlrd": `pip install xlrd`.
- `doctor` shows what is installed.
- With the mdmax plugin in Claude Code, PDF, Office, OpenDocument and EPUB files are converted automatically when you Read them. Use this skill for CSV, JSON and HTML, to save a converted file, and for the savings report.
