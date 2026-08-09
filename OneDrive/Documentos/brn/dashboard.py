#!/usr/bin/env python3
"""
MdMax Dashboard - Token Economy Visualization
"""

import json
from pathlib import Path
from datetime import datetime

ECONOMY_FILE = Path.home() / ".mdmax" / "economy_stats.json"

class DashboardGenerator:
    """Simple dashboard generator"""
    
    def __init__(self):
        self.stats = self.load_stats()
    
    def load_stats(self):
        """Load economy statistics"""
        if ECONOMY_FILE.exists():
            try:
                with open(ECONOMY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[WARNING] Failed to load stats: {e}")
                return self.default_stats()
        return self.default_stats()
    
    def default_stats(self):
        """Default empty stats"""
        return {
            "total_tokens_saved": 0,
            "conversions": 0,
            "by_format": {},
            "daily_stats": {}
        }
    
    def print_console_dashboard(self):
        """Print ASCII dashboard"""
        print("\n" + "="*60)
        print("[DASHBOARD] MdMax - Token Economy Dashboard")
        print("="*60)

        total = self.stats.get("total_tokens_saved", 0)
        conversions = self.stats.get("conversions", 0)
        by_format = self.stats.get("by_format", {})

        print(f"\n[TOKENS] Total Tokens Saved: {total:,}")
        print(f"[FILES] Conversions: {conversions}")

        if conversions > 0:
            print(f"[AVERAGE] Average: {total/conversions:,.0f} tokens/file")

        if by_format:
            print("\n[FORMAT STATS] By Format:")
            for fmt, count in sorted(by_format.items(), key=lambda x: x[1], reverse=True):
                print(f"  * {fmt.upper()}: {count} files")

        print("\n" + "="*60 + "\n")
    
    def generate_html_dashboard(self):
        """Generate HTML dashboard"""
        total = self.stats.get("total_tokens_saved", 0)
        conversions = self.stats.get("conversions", 0)
        avg_saving = f"{total/conversions:,.0f}" if conversions > 0 else "N/A"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MdMax Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        .stat {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #007bff; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>MdMax Dashboard</h1>
        <div class="stat">
            <div class="stat-label">Total Tokens Saved</div>
            <div class="stat-value">{total:,}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Files Converted</div>
            <div class="stat-value">{conversions}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Average Saving</div>
            <div class="stat-value">{avg_saving} tokens/file</div>
        </div>
    </div>
</body>
</html>
"""

        with open("dashboard.html", "w", encoding='utf-8') as f:
            f.write(html)
