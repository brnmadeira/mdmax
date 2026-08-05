#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate hero screenshot PNG from HTML
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Create image
WIDTH = 1200
HEIGHT = 800
BG_COLOR = (102, 126, 234)  # Purple gradient start
IMG = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(IMG)

# Gradient effect (simple horizontal)
for x in range(WIDTH):
    ratio = x / WIDTH
    r = int(102 + (118 - 102) * ratio)
    g = int(126 + (75 - 126) * ratio)
    b = int(234 + (162 - 234) * ratio)
    draw.rectangle([(x, 0), (x, HEIGHT)], fill=(r, g, b))

# White box for content
BOX_MARGIN = 40
BOX_Y = 120
BOX_HEIGHT = 600
draw.rectangle(
    [(BOX_MARGIN, BOX_Y), (WIDTH - BOX_MARGIN, BOX_Y + BOX_HEIGHT)],
    fill=(255, 255, 255),
    outline=(200, 200, 200),
    width=2
)

# Title
title_y = 50
draw.text((WIDTH//2, title_y), "🚀 MdMax in Action",
         fill=(255, 255, 255), anchor="mm",
         font=None)  # Uses default font

# Subtitle
subtitle_y = 90
draw.text((WIDTH//2, subtitle_y),
         "Transform files into compressed Markdown while tracking token economy",
         fill=(255, 255, 255), anchor="mm",
         font=None)

# Left side (Before)
LEFT_X = BOX_MARGIN + 60
RIGHT_X = WIDTH - BOX_MARGIN - 60
CONTENT_Y = BOX_Y + 40

# Before section
draw.text((LEFT_X, CONTENT_Y), "❌ WITHOUT MdMax", fill=(0, 0, 0), font=None)
before_y = CONTENT_Y + 40
metrics_before = [
    ("File: report.pdf", "Size: 50 MB"),
    ("Claude reads: Binary", "Tokens: 2,850"),
    ("Processing: 10 min", "Cost: $0.86"),
    ("Insights: ❌ None", ""),
]
for line1, line2 in metrics_before:
    draw.text((LEFT_X, before_y), line1, fill=(100, 100, 100), font=None)
    before_y += 25
    if line2:
        draw.text((LEFT_X, before_y), line2, fill=(100, 100, 100), font=None)
        before_y += 25

# Arrow in middle
arrow_x = WIDTH // 2
arrow_y = BOX_Y + BOX_HEIGHT // 2
draw.text((arrow_x, arrow_y), "→", fill=(102, 126, 234), anchor="mm", font=None)

# After section
draw.text((RIGHT_X - 200, CONTENT_Y), "✅ WITH MdMax", fill=(0, 0, 0), font=None)
after_y = CONTENT_Y + 40
metrics_after = [
    ("File: report.md", "Size: 5 MB"),
    ("Claude reads: Markdown", "Tokens: 285"),
    ("Processing: 1 min", "Cost: $0.09"),
    ("Insights: ✅ 5 metrics", ""),
]
for line1, line2 in metrics_after:
    draw.text((RIGHT_X - 200, after_y), line1, fill=(46, 125, 50), font=None)
    after_y += 25
    if line2:
        draw.text((RIGHT_X - 200, after_y), line2, fill=(46, 125, 50), font=None)
        after_y += 25

# Savings badge at bottom
badge_y = BOX_Y + BOX_HEIGHT - 50
draw.rectangle(
    [(BOX_MARGIN + 50, badge_y - 20), (WIDTH - BOX_MARGIN - 50, badge_y + 20)],
    fill=(232, 245, 233),
    outline=(46, 125, 50),
    width=2
)
draw.text((WIDTH//2, badge_y), "💰 Save $0.77 per file • 90% Token Reduction",
         fill=(46, 125, 50), anchor="mm", font=None)

# Save image
output_path = Path(__file__).parent / "hero-screenshot.png"
IMG.save(output_path, "PNG", quality=95)

print(f"✅ Hero screenshot generated: {output_path}")
print(f"📊 Size: {WIDTH}x{HEIGHT}px")
print(f"💾 File size: {output_path.stat().st_size / 1024:.1f}KB")
