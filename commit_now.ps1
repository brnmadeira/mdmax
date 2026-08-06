# MdMax Commit Script - SIMPLE VERSION

cd "C:\Users\marke\AppData\Roaming\Claude\skills\auto-convert-to-markdown"

Write-Host "Git Commit Script - MdMax" -ForegroundColor Cyan

# Init git if needed
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git..." -ForegroundColor Yellow
    git init
    git config user.email "brn.madeira@gmail.com"
    git config user.name "MdMax Developer"
}

# Commit 1
Write-Host "Commit 1: Core implementation..." -ForegroundColor Yellow
git add scripts/*.py config.json
git commit -m "feat(core): add MdMax v2.0 with 16 formats and 5-metric dashboard"

# Commit 2
Write-Host "Commit 2: Documentation..." -ForegroundColor Yellow
git add README.md AUTHORS.md CONTRIBUTING.md INSTALLATION.md FAQ.md
git commit -m "docs: add professional documentation for GitHub launch"

# Commit 3
Write-Host "Commit 3: Changelog..." -ForegroundColor Yellow
git add CHANGELOG.md MDMAX_FEATURES.md ROADMAP_7_DIAS.md
git commit -m "docs: add version history and feature documentation"

# Commit 4
Write-Host "Commit 4: License..." -ForegroundColor Yellow
git add LICENSE .gitignore
git commit -m "legal: add MIT license and gitignore"

# Commit 5
Write-Host "Commit 5: GitHub templates..." -ForegroundColor Yellow
git add .github/
git commit -m "ci: add GitHub templates and workflows"

# Commit 6
Write-Host "Commit 6: Visual assets..." -ForegroundColor Yellow
git add hero-screenshot.* generate_hero_png.py view_dashboard.bat test_installation.py
git commit -m "assets: add visual assets and testing tools"

Write-Host ""
Write-Host "All commits done! Now syncing to GitHub..." -ForegroundColor Green
Write-Host ""

git log --oneline
