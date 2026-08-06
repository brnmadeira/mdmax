# 🚀 Getting Started with MdMax

Complete step-by-step guide from zero to using MdMax.

**Time:** 5-10 minutes  
**Level:** Beginner-friendly

---

## Step 1: Install (2 minutes)

### Choose Your Method

**Easiest (Recommended):**
```bash
pip install mdmax
```

**Alternative (Claude Code):**
1. Open Claude Code Settings
2. Skills → Import
3. Paste: `https://github.com/username/mdmax.git`

**For Developers:**
```bash
git clone https://github.com/username/mdmax.git
cd mdmax
pip install -e .
```

---

## Step 2: Verify Installation (1 minute)

```bash
mdmax --version
```

Expected output:
```
MdMax v2.0.0
✅ Installation successful!
```

---

## Step 3: First Time Setup (2 minutes)

### Auto-Setup (Easiest)
```bash
mdmax init
```

This automatically:
- ✅ Configures Claude Code hook
- ✅ Creates config files
- ✅ Initializes dashboard
- ✅ Tests all features

### Manual Setup (Alternative)
```bash
mdmax --setup-hook
```

---

## Step 4: Your First Conversion (2 minutes)

### Method A: Automatic (Recommended)

**In Claude Code, simply:**
```
You: "Read C:\Documents\report.pdf"
Claude: [MdMax automatically processes it]
Claude: "I've read your report..."
```

**That's it!** No manual steps needed.

---

### Method B: Manual Dashboard

```bash
# View your savings
mdmax dashboard

# View in browser
mdmax dashboard --html
```

You'll see:
- 💰 Total tokens saved
- 📊 Breakdown by format
- 📈 30-day trends
- 🎯 Milestones reached

---

### Method C: Command Line

```bash
# Convert a single file
mdmax convert /path/to/document.pdf

# See the result
cat ~/markdown/report.md
```

---

## 📊 Real Example

### Before (Without MdMax)

```
You: Read /Downloads/quarterly_report.pdf (50MB)
Claude reads: Binary PDF → 2,850 tokens
Cost: $0.86
```

### After (With MdMax)

```
You: Read /Downloads/quarterly_report.pdf (50MB)
MdMax: Converts to Markdown → 5MB
Claude reads: Markdown → 285 tokens
Cost: $0.09
Savings: $0.77 🎉
```

---

## 🎯 Common Scenarios

### Scenario 1: Read a PDF Report

**Step 1:** Place PDF in any folder
```
~/Downloads/report.pdf
```

**Step 2:** In Claude Code
```
Read ~/Downloads/report.pdf
```

**Step 3:** MdMax handles it
- ✅ Converts to Markdown
- ✅ Tracks tokens saved
- ✅ Updates dashboard

**That's all!**

---

### Scenario 2: Analyze a Spreadsheet

**Step 1:** Place Excel file
```
~/Downloads/data.xlsx (5MB)
```

**Step 2:** Ask Claude to analyze
```
Analyze ~/Downloads/data.xlsx
```

**Step 3:** MdMax optimizes
- ✅ Compresses 70%
- ✅ Saves ~1,500 tokens
- ✅ Shows in dashboard

---

### Scenario 3: Extract Text from Image

**Step 1:** Have a screenshot
```
~/Screenshots/chart.png (8MB)
```

**Step 2:** Ask Claude
```
What's in this image? ~/Screenshots/chart.png
```

**Step 3:** MdMax extracts
- ✅ Uses OCR to read text
- ✅ Creates Markdown
- ✅ Saves 75% tokens

---

## 📈 View Your Progress

### Daily Check
```bash
mdmax dashboard
```

Shows:
```
💰 TOTAL SAVED: 512,825 tokens
📁 FILES: 23 conversions
🎯 TODAY: 45,000 tokens saved
📊 TREND: ↑ +8% vs yesterday
```

### Weekly Deep Dive
```bash
mdmax dashboard --html
```

Opens interactive dashboard with:
- 🏆 Which formats save most
- 📊 Monthly projections
- 🎯 Milestones reached
- 📈 30-day trend chart

### Export for Analysis
```bash
mdmax export --csv
# Creates: mdmax_stats_2026-08-03.csv
```

---

## 🔧 Customize (Optional)

### Adjust Compression Level

Edit `~/.mdmax/config.json`:
```json
{
  "default_mode": "ultra",  // "normal" or "ultra"
  "parallelization": {
    "workers": 3            // Increase for speed
  }
}
```

### Enable Advanced Features

```bash
# Install OCR for image text extraction
pip install pytesseract pillow

# Install EPUB support for e-books
pip install ebooklib
```

---

## 💡 Pro Tips

### Tip 1: Batch Process Folder
```bash
mdmax convert ~/Downloads/ --recursive
# Converts all files in folder
```

### Tip 2: Save Stats for Reports
```bash
mdmax export --json
# Create custom reports
```

### Tip 3: Share Dashboard
```bash
mdmax dashboard --html --share
# Get shareable link
```

### Tip 4: Monitor in Real-Time
```bash
mdmax dashboard --watch
# Updates every 5 seconds
```

---

## ❓ FAQ

**Q: Does MdMax require internet?**
A: No, everything runs locally. 100% private.

**Q: Will my files be modified?**
A: No, originals stay untouched. Conversions stored separately.

**Q: Can I disable it temporarily?**
A: Yes, `mdmax --disable` (re-enable with `mdmax --enable`)

**Q: How much disk space?**
A: ~500MB for conversions + cache (auto-cleanup after 7 days)

**Q: What about privacy?**
A: All processing local. No uploads. No tracking.

---

## 🎓 Learn More

**Read These:**
1. [Features Guide](./MDMAX_FEATURES.md) - All 5 metrics explained
2. [Installation Guide](./INSTALL_GUIDE.md) - Advanced setup
3. [FAQ](./FAQ.md) - Common questions
4. [Troubleshooting](./INSTALL_GUIDE.md#-troubleshooting) - Fix issues

---

## 🚀 Next Steps

### Right Now
- [ ] Install MdMax
- [ ] Run `mdmax --test-all`
- [ ] View dashboard: `mdmax dashboard`

### Today
- [ ] Read a PDF in Claude Code
- [ ] Check saved tokens
- [ ] Explore dashboard

### This Week
- [ ] Read 5+ files
- [ ] Review statistics
- [ ] Share with team

---

## 📊 Expected Timeline

| Timeline | What Happens |
|----------|--------------|
| **Day 1** | Save 50-100K tokens |
| **Week 1** | Save 500K+ tokens |
| **Month 1** | Save 2M+ tokens |
| **Year 1** | Save 24M+ tokens |

**At Claude pricing:** 1M tokens = $3
**Year 1 savings: ~$72** 💰

---

## 🆘 Something Not Working?

### Step 1: Check Installation
```bash
mdmax --version
mdmax --test-all
```

### Step 2: Check Hook
```bash
mdmax --status
```

### Step 3: Clear Cache
```bash
mdmax --clear-cache
```

### Step 4: Reinstall
```bash
pip uninstall mdmax
pip install --upgrade mdmax
mdmax init
```

### Step 5: Get Help
- Email: brn.madeira@gmail.com
- Issues: https://github.com/username/mdmax/issues
- Include: Python version, OS, error message

---

## 🎉 You're All Set!

MdMax is now:
- ✅ Installed
- ✅ Configured
- ✅ Running automatically
- ✅ Tracking savings

**Start saving tokens now!** 🚀

---

## 📱 Quick Command Reference

```bash
# Installation
pip install mdmax

# Verify
mdmax --version
mdmax --test-all

# Use
mdmax dashboard          # View stats
mdmax convert file.pdf   # Single file
mdmax convert ~/folder   # Entire folder

# Export
mdmax export --csv      # To CSV
mdmax export --json     # To JSON

# Maintenance
mdmax --clear-cache     # Clear old files
mdmax --setup-hook      # Reconfigure hook
mdmax --disable         # Temporarily disable
mdmax --enable          # Re-enable
```

---

**Questions?** Read [FAQ](./FAQ.md) or email: brn.madeira@gmail.com

**Happy saving!** 💰🚀
