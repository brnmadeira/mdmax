# MDMAX Quick Start

Get up and running in 5 minutes.

---

## 1️⃣ Install

```bash
pip install mdmax
```

## 2️⃣ Verify

```bash
mdmax --version
# Output: 3.0.0 ✅
```

## 3️⃣ Convert Your First Document

```bash
mdmax convert document.pdf
```

Output: Clean Markdown → stdout

## 4️⃣ Save to File

```bash
mdmax convert document.pdf -o output.md
```

Output: `output.md` created

## 5️⃣ View Statistics

```bash
mdmax stats
```

Output: Token economy dashboard

---

## Common Workflows

### Convert Multiple Files

```bash
mdmax batch "*.pdf" -o converted/
mdmax batch "reports/**/*.xlsx" -o tables/
```

### Export Statistics

```bash
mdmax stats --export json -o report.json
mdmax stats --export csv -o report.csv
```

### Estimate Tokens Before Converting

```bash
mdmax estimate large_file.pdf
```

### Use in Python

```python
from mdmax import MdMax

converter = MdMax()
markdown = converter.convert("document.pdf")

print(converter.get_dashboard())
```

---

## Available Commands

| Command | Usage |
|---------|-------|
| `convert` | Convert single file |
| `batch` | Convert multiple files |
| `stats` | View statistics |
| `estimate` | Estimate tokens |
| `config` | Manage configuration |
| `--help` | Show all options |

---

## Next Steps

📚 **Read Documentation:**
- [README.md](README.md) — Full documentation
- [INSTALLATION.md](INSTALLATION.md) — Setup guide
- [MDMAX-SKILL.md](MDMAX-SKILL.md) — Agent Skill details
- [PHASE2_ROADMAP.md](PHASE2_ROADMAP.md) — Planned features

💡 **Tips:**
- Use `mdmax --help` for CLI options
- Enable verbose mode: `mdmax convert file.pdf -v`
- Check config: `mdmax config --show`

🐛 **Issues?**
- GitHub: https://github.com/brnmadeira/mdmax/issues
- Email: brn.madeira@gmail.com

---

Happy converting! 🚀
