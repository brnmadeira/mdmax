#!/bin/bash
# MdMax Git Commit Script
# Run this to prepare all commits for GitHub push

set -e

echo "🚀 MdMax Git Commit Script"
echo "==========================================="

# Initialize git if needed
if [ ! -d .git ]; then
    echo "📝 Initializing git repository..."
    git init
    git config user.email "brn.madeira@gmail.com"
    git config user.name "MdMax Developer"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "📋 Preparing commits..."

# Commit 1: Core code and scripts
echo ""
echo "📝 Commit 1: Core implementation"
git add scripts/*.py config.json
git commit -m "feat(core): add MdMax v2.0 implementation with 16 formats and 5-metric dashboard

- 16 file format support (PDF, XLSX, DOCX, PPTX, EPUB, JPG/PNG, SVG, etc)
- 7 compression optimizations (+5-10% additional savings)
- Advanced features: OCR, EPUB extraction, smart caching
- 5-layer metrics dashboard (ranking, projection, milestones, export, trends)
- Automatic hook integration for Claude Code
- Token economy tracking with real-time analytics
- 79.7% average compression ratio demonstrated

Co-Authored-By: brn.madeira@gmail.com"

# Commit 2: Documentation
echo ""
echo "📝 Commit 2: Professional documentation"
git add README.md AUTHORS.md CONTRIBUTING.md INSTALLATION.md FAQ.md
git commit -m "docs: add professional documentation for GitHub launch

- Updated README with hero section and benchmarks
- CONTRIBUTING guide for contributors
- INSTALLATION guide for various setups
- FAQ for common questions
- AUTHORS credits and acknowledgments

Co-Authored-By: brn.madeira@gmail.com"

# Commit 3: Version history and features
echo ""
echo "📝 Commit 3: Changelog and features documentation"
git add CHANGELOG.md MDMAX_FEATURES.md ROADMAP_7_DIAS.md
git commit -m "docs: add version history and feature documentation

- Complete CHANGELOG with v1.0, v1.5, v2.0 history
- Detailed feature guide for 5-layer metrics
- 7-day launch roadmap for GitHub preparation
- Future roadmap and development plans

Co-Authored-By: brn.madeira@gmail.com"

# Commit 4: License and legal
echo ""
echo "📝 Commit 4: License and legal files"
git add LICENSE .gitignore
git commit -m "legal: add MIT license and gitignore

- MIT License with 2026 copyright
- Comprehensive .gitignore for Python projects
- GitHub workflows and CI/CD configuration

Co-Authored-By: brn.madeira@gmail.com"

# Commit 5: GitHub templates and workflows
echo ""
echo "📝 Commit 5: GitHub templates and CI/CD"
git add .github/
git commit -m "ci: add GitHub issue templates and test workflows

- Bug report template
- Feature request template
- Pull request template
- GitHub Actions workflow for automated testing
- Support for Python 3.8 - 3.11

Co-Authored-By: brn.madeira@gmail.com"

# Commit 6: Visual assets and utilities
echo ""
echo "📝 Commit 6: Visual assets and utilities"
git add hero-screenshot.* generate_hero_png.py view_dashboard.bat
git commit -m "assets: add hero screenshots and visual assets

- Hero screenshot (1200x800px) showing before/after comparison
- PNG generator script for asset creation
- Dashboard viewer .bat script for Windows
- Professional visual assets for marketing

Co-Authored-By: brn.madeira@gmail.com"

echo ""
echo "==========================================="
echo "✅ All commits prepared successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Create repository on GitHub:"
echo "   - New repo: 'mdmax'"
echo "   - Description: 'Compress files by 79.7% + track token economy'"
echo ""
echo "2. Add remote and push:"
echo "   git remote add origin https://github.com/USERNAME/mdmax.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Enable GitHub features:"
echo "   - Issues (bug tracking)"
echo "   - Discussions (feature requests)"
echo "   - GitHub Pages (optional)"
echo ""
echo "4. Submit to marketplaces:"
echo "   - Agensi Marketplace"
echo "   - Anthropic Skills Registry"
echo "   - awesome-claude-skills"
echo ""
echo "🚀 Ready to launch!"
