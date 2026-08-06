# 📦 MdMax - Installation Guide

Choose your preferred installation method below.

---

## ⚡ Quick Install (Recommended)

### Windows (PowerShell)
```powershell
pip install mdmax
python -m mdmax init
```

### Mac/Linux (Terminal)
```bash
pip install mdmax
python -m mdmax init
```

**That's it!** MdMax automatically integrates with Claude Code.

---

## 📋 Installation Options

### Option 1: PyPI (Simplest) ⭐

Best for: Everyone (recommended)

```bash
pip install mdmax
```

**Features:**
- ✅ One-line install
- ✅ Automatic updates with `pip install --upgrade mdmax`
- ✅ Auto-setup of Claude Code hook
- ✅ Works on Windows, Mac, Linux

**Verify Installation:**
```bash
mdmax --version
# Output: MdMax v2.0.0
```

---

### Option 2: GitHub (For Developers)

Best for: Contributors, custom setup

```bash
# Clone repository
git clone https://github.com/username/mdmax.git
cd mdmax

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Optional: Install advanced features
pip install pytesseract pillow ebooklib
```

**Verify Installation:**
```bash
python scripts/quick_test_features.py
```

---

### Option 3: Claude Code Direct Import

Best for: Claude Code users only

**In Claude Code:**
1. Open Claude Code Settings
2. Go to "Skills" section
3. Click "Import Skill"
4. Paste repository URL: `https://github.com/username/mdmax.git`
5. Click "Install"

**Automatic Setup:**
- ✅ Hook automatically configured
- ✅ Dashboard command available
- ✅ Ready to use immediately

---

## 🔧 Optional Dependencies

These are **optional** - MdMax works without them with reduced functionality.

### For Image OCR (JPG/PNG Text Extraction)

```bash
pip install pytesseract pillow
```

**Then install Tesseract:**

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer
3. MdMax finds it automatically

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Test OCR:**
```bash
mdmax --test-ocr
```

---

### For E-Book Support (EPUB)

```bash
pip install ebooklib
```

No additional setup needed.

---

### For All Features (Recommended)

```bash
pip install mdmax pytesseract pillow ebooklib
```

**Then install Tesseract** (see above)

---

## ✅ Verify Installation

### Quick Test (All Users)

```bash
# Test all features
mdmax --test-all

# Expected output:
# ✅ PDF support: OK
# ✅ XLSX support: OK
# ✅ Dashboard: OK
# ✅ Hook integration: OK
# All systems ready!
```

### Full Test Suite (Developers)

```bash
cd mdmax
python -m pytest tests/
python scripts/quick_test_features.py
```

---

## 🎯 First Use

### Method 1: Automatic (Recommended)

Simply read a file in Claude Code:

```
You: "Read /path/to/document.pdf"
Claude: [MdMax automatically compresses]
Claude: [reads Markdown instead of PDF]
```

**That's all!** MdMax runs silently in the background.

### Method 2: Manual Dashboard

```bash
# View dashboard
mdmax dashboard

# View in browser
mdmax dashboard --html
```

### Method 3: Command Line

```bash
# Convert single file
mdmax convert /path/to/file.pdf

# Convert directory
mdmax convert /path/to/folder/ --recursive

# Export stats
mdmax export --format csv
mdmax export --format json
```

---

## 🐛 Troubleshooting

### "command not found: mdmax" (Mac/Linux)

**Solution:** Add to PATH
```bash
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

### "OCR not working"

**Windows:**
1. Check Tesseract installed: `where tesseract`
2. If not found, download from: https://github.com/UB-Mannheim/tesseract

**Mac:**
```bash
brew install tesseract
brew link tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### "Hook not triggering automatically"

**Solution:** Manually enable
```bash
mdmax --setup-hook

# Or in Claude Code settings:
# 1. Settings → Hooks
# 2. Find "PostToolUse"
# 3. Enable for Read tool
```

### "Cache issues / old conversions"

**Clear cache:**
```bash
mdmax --clear-cache
```

### "Permission denied" (Linux/Mac)

```bash
# Fix permissions
chmod +x ~/.local/bin/mdmax
```

---

## 📊 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|------------|
| **Python** | 3.8 | 3.10+ |
| **RAM** | 512 MB | 2+ GB |
| **Disk** | 100 MB | 500 MB |
| **OS** | Any | Windows/Mac/Linux |

---

## 🚀 Getting Started After Install

### 1. Check Dashboard
```bash
mdmax dashboard
```

### 2. Read a File (Automatic)
```
You: "Read my_document.pdf"
Claude: [MdMax handles it]
```

### 3. View Savings
```bash
mdmax dashboard
```

### 4. Export Data
```bash
mdmax export --format csv
# File saved to: ~/markdown/exports/mdmax_stats.csv
```

---

## 📱 Update MdMax

### PyPI Installation

```bash
pip install --upgrade mdmax
```

### GitHub Installation

```bash
cd mdmax
git pull origin main
pip install -e . --upgrade
```

---

## 🆘 Need Help?

**If installation fails:**

1. **Check Python version:**
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

2. **Check pip:**
   ```bash
   pip --version
   pip install --upgrade pip
   ```

3. **Report issue:**
   - Email: brn.madeira@gmail.com
   - GitHub Issues: https://github.com/username/mdmax/issues
   - Include: Python version, OS, error message

---

## 📚 Next Steps

After installation:

1. ✅ Read [QUICK START](./README.md#quick-start)
2. ✅ Explore [Features](./MDMAX_FEATURES.md)
3. ✅ Join [Discussions](https://github.com/username/mdmax/discussions)
4. ✅ Read [FAQ](./FAQ.md)

---

## 💡 Pro Tips

**Tip 1: Multiple Python Versions**
```bash
# If you have Python 3.10
python3.10 -m pip install mdmax
```

**Tip 2: Virtual Environment (Best Practice)**
```bash
python -m venv mdmax-env
source mdmax-env/bin/activate  # Windows: mdmax-env\Scripts\activate
pip install mdmax
```

**Tip 3: Auto-Updates**
```bash
pip install --upgrade pip
pip install mdmax --upgrade-strategy eager
```

**Tip 4: Check Installed Version**
```bash
pip show mdmax
# Shows version, location, dependencies
```

---

## ✅ Installation Checklist

After installing, verify:

- [ ] `mdmax --version` works
- [ ] `mdmax --test-all` passes
- [ ] Dashboard appears: `mdmax dashboard`
- [ ] Hook is enabled (auto or manual)
- [ ] Can read a PDF without errors
- [ ] Dashboard shows stats

**If all ✅:** You're ready to use MdMax!

---

## 🎉 You're Ready!

MdMax is now installed and integrated with Claude Code.

**Next:** Start reading files and watch tokens get saved! 🚀

---

**Questions?** Email: brn.madeira@gmail.com

**Enjoy saving tokens!** 💰
