# 🤝 Contributing to MdMax

We ❤️ contributions! Bug reports, features, improvements, and docs welcome.

---

## How to Contribute

### 🐛 Report a Bug

1. **Check existing issues** - Don't duplicate
2. **Create new issue** with:
   - Clear title & description
   - Python version, OS, file type
   - Steps to reproduce
   - Expected vs actual behavior

**Example:**
```
Title: OCR fails on PNG files > 10MB

Symptoms:
- Tesseract memory error
- Process hangs for 5+ min
- File: test_large.png (12MB)

Environment: Python 3.9, Windows 11, Tesseract 5.2
```

### ✨ Request a Feature

1. **Use GitHub Discussions** - Share ideas
2. **Describe use case** - Why do you need it?
3. **Provide examples** - Show the benefit

**Example:**
```
Title: Support for HTML files

Use case: Convert web articles to Markdown
Example: website.html (500KB) → article.md
Expected: ~75% compression like EPUB
```

### 💻 Code Contribution

1. **Fork & clone**
   ```bash
   git clone https://github.com/YOUR-USER/mdmax.git
   cd mdmax
   ```

2. **Create branch**
   ```bash
   git checkout -b feature/your-feature
   # or
   git checkout -b fix/bug-name
   ```

3. **Make changes**
   - Follow Python style (PEP 8)
   - Add comments for complex logic
   - Test locally

4. **Commit with clear message**
   ```bash
   git commit -m "Add HTML format support"
   git commit -m "Fix OCR memory leak"
   ```

5. **Push & open PR**
   ```bash
   git push origin feature/your-feature
   ```
   - Describe what changed & why
   - Reference related issues
   - Include testing notes

---

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- pip

### Quick Start

```bash
# Clone
git clone https://github.com/username/mdmax.git
cd mdmax

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install pytest pytest-cov pytesseract pillow ebooklib

# Test
python -m pytest tests/
python scripts/quick_test_features.py
```

---

## Code Standards

### Style
- **Python**: PEP 8 (use `black` for formatting)
- **Naming**: `snake_case` for functions/vars, `CamelCase` for classes
- **Docstrings**: One-liner for public functions

```python
def compress_markdown(markdown: str) -> str:
    """Remove unnecessary whitespace from Markdown."""
    # Implementation...
```

### Comments
- Explain **why**, not **what**
- Good: `# Stream large files to avoid memory spikes`
- Bad: `# Split file into chunks`

---

## Testing

### Run Tests
```bash
# All tests
python -m pytest

# Specific file
python -m pytest tests/test_converters.py

# With coverage
python -m pytest --cov=scripts tests/
```

### Add Tests
```python
# tests/test_myfeature.py
def test_compression_ratio():
    result = compress("test data")
    assert result.ratio > 0.5

def test_handles_empty_input():
    result = compress("")
    assert result == ""
```

---

## PR Process

### Before Submitting
- ✅ Tests pass locally
- ✅ No breaking changes
- ✅ Updated docs if needed
- ✅ Commit messages are clear

### PR Template
```markdown
## What
Brief description of change

## Why
Why this change is needed

## Testing
How to test this change

## Related Issues
Closes #123
```

---

## Getting Help

- **Questions?** → GitHub Discussions
- **Bug help?** → GitHub Issues
- **Direct?** → brn.madeira@gmail.com
- **Async?** → Email works too

---

## Recognition

All contributors get:
- ✅ Credit in CHANGELOG
- ✅ Listed in AUTHORS (if you want)
- ✅ GitHub contributor badge
- ✅ Gratitude from the community

---

## License

By contributing, you agree your code is MIT licensed.

---

**Thank you for making MdMax better!** 🚀
