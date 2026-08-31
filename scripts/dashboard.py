#!/usr/bin/env python3
"""
MdMax Dashboard - Token Economy Visualization
"""

import json
from pathlib import Path
from datetime import datetime

ECONOMY_LOG = Path.home() / ".mdmax" / "economy.jsonl"

class DashboardGenerator:
    """Simple dashboard generator"""

    def __init__(self):
        self.stats = self.load_stats()

    def load_stats(self):
        """Aggregate economy statistics from the conversion log"""
        if not ECONOMY_LOG.exists():
            return self.default_stats()

        total_tokens_saved = 0
        conversions = 0
        by_format = {}
        daily_stats = {}

        try:
            with open(ECONOMY_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    conversions += 1
                    total_tokens_saved += record.get('savings_tokens', 0)

                    fmt = record.get('format', 'unknown')
                    by_format[fmt] = by_format.get(fmt, 0) + 1

                    day = record.get('timestamp', '')[:10]
                    if day:
                        daily_stats[day] = daily_stats.get(day, 0) + record.get('savings_tokens', 0)
        except OSError:
            return self.default_stats()

        return {
            "total_tokens_saved": total_tokens_saved,
            "conversions": conversions,
            "by_format": by_format,
            "daily_stats": daily_stats,
        }
    
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
        print("📊 MdMax - Token Economy Dashboard")
        print("="*60)
        
        total = self.stats.get("total_tokens_saved", 0)
        conversions = self.stats.get("conversions", 0)
        by_format = self.stats.get("by_format", {})
        
        print(f"\n💰 Total Tokens Saved: {total:,}")
        print(f"📁 Conversions: {conversions}")
        
        if conversions > 0:
            print(f"📈 Average: {total/conversions:,.0f} tokens/file")
        
        if by_format:
            print("\n📊 By Format:")
            for fmt, count in sorted(by_format.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {fmt.upper()}: {count} files")
        
        print("\n" + "="*60 + "\n")
    
    def generate_html_dashboard(self):
        """Generate HTML dashboard"""
        total = self.stats.get("total_tokens_saved", 0)
        conversions = self.stats.get("conversions", 0)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
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
        <h1>📊 MdMax Dashboard</h1>
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
            <div class="stat-value">{total/conversions:,.0f} tokens/file</div>
        </div>
    </div>
</body>
</html>
"""
        
        with open("dashboard.html", "w") as f:
            f.write(html)
