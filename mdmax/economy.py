"""
Token Economy Tracking for MDMAX
Measures compression and cost savings
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class TokenEconomy:
    """Track token usage and savings across conversions"""

    # Approximate tokens per byte (based on typical document encoding)
    TOKENS_PER_BYTE = {
        "pdf": 0.057,      # 22-80% savings (use 57 tokens/1000 bytes)
        "docx": 0.12,      # 50-70% savings
        "pptx": 0.115,     # 40-75% savings
        "xlsx": 0.15,      # 40-70% savings
        "xls": 0.15,
        "xlsm": 0.15,
        "csv": 0.20,       # 50-60% savings
        "tsv": 0.20,
        "json": 0.25,      # 30-50% savings
        "txt": 0.33,       # 20-30% savings
        "png": 0.19,       # 70% savings (OCR)
        "jpg": 0.19,
        "jpeg": 0.19,
        "svg": 0.25,       # 70-80% savings
        "epub": 0.18,      # 75-85% savings
        "ods": 0.15,
        "rtf": 0.18,
        "md": 0.33,        # Already markdown
    }

    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or Path.home() / ".mdmax" / "economy.jsonl"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.sessions: List[Dict] = []

    def track(
        self,
        filename: str,
        input_bytes: int,
        output_bytes: int,
        format: str,
    ):
        """Record a conversion"""
        format_clean = format.lstrip(".").lower()

        # Estimate tokens
        input_tokens = self._estimate_tokens(input_bytes, format_clean)
        output_tokens = len(self._estimate_markdown_tokens(output_bytes))

        # Calculate savings
        savings_bytes = input_bytes - output_bytes
        savings_tokens = input_tokens - output_tokens
        savings_pct = (savings_bytes / input_bytes * 100) if input_bytes > 0 else 0

        record = {
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "format": format_clean,
            "input_bytes": input_bytes,
            "output_bytes": output_bytes,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "savings_bytes": savings_bytes,
            "savings_tokens": savings_tokens,
            "savings_pct": round(savings_pct, 1),
        }

        self.sessions.append(record)
        self._write_log(record)

    def get_stats(self) -> Dict:
        """Get aggregate statistics"""
        if not self.sessions:
            return {
                "total_conversions": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_savings_tokens": 0,
                "overall_savings_pct": 0,
                "by_format": {}
            }

        total_input = sum(s["input_tokens"] for s in self.sessions)
        total_output = sum(s["output_tokens"] for s in self.sessions)
        total_savings = total_input - total_output

        by_format = defaultdict(lambda: {
            "count": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "savings_tokens": 0,
            "avg_savings_pct": 0,
        })

        for session in self.sessions:
            fmt = session["format"]
            by_format[fmt]["count"] += 1
            by_format[fmt]["input_tokens"] += session["input_tokens"]
            by_format[fmt]["output_tokens"] += session["output_tokens"]
            by_format[fmt]["savings_tokens"] += session["savings_tokens"]

        # Calculate average savings % per format
        for fmt in by_format:
            if by_format[fmt]["input_tokens"] > 0:
                by_format[fmt]["avg_savings_pct"] = round(
                    (by_format[fmt]["savings_tokens"] / by_format[fmt]["input_tokens"] * 100), 1
                )

        return {
            "total_conversions": len(self.sessions),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_savings_tokens": total_savings,
            "overall_savings_pct": round(total_savings / total_input * 100, 1) if total_input > 0 else 0,
            "by_format": dict(by_format),
        }

    def get_dashboard(self) -> str:
        """Format statistics as readable dashboard"""
        import sys
        stats = self.get_stats()

        # Use ASCII art on Windows
        is_windows = sys.platform == "win32"

        lines = [
            "=" * 60,
            "MDMAX - Token Economy Dashboard",
            "=" * 60,
            "",
            f"Total Conversions: {stats['total_conversions']}",
            f"Input Tokens:      {stats['total_input_tokens']:,}",
            f"Output Tokens:     {stats['total_output_tokens']:,}",
            f"Tokens Saved:      {stats['total_savings_tokens']:,} ({stats['overall_savings_pct']:.1f}%)",
            "",
            "By Format:",
            "-" * 60,
        ]

        # Format table
        for fmt, data in sorted(stats["by_format"].items(), key=lambda x: x[1]["savings_tokens"], reverse=True):
            line = f"  {fmt.upper():8} | {data['count']:3} files | {data['savings_tokens']:8,} tokens saved ({data['avg_savings_pct']:5.1f}%)"
            lines.append(line)

        lines.extend([
            "",
            "Savings breakdown:",
            f"  Monthly projection (1M input): {stats['overall_savings_pct']*10_000:,.0f} tokens saved",
            f"  Annual cost reduction: ${stats['total_savings_tokens']*0.00015:.2f} (at Claude API rates)",
        ])

        return "\n".join(lines)

    @staticmethod
    def _estimate_tokens(input_bytes: int, format: str) -> int:
        """Estimate tokens in original document"""
        factor = TokenEconomy.TOKENS_PER_BYTE.get(format, 0.33)
        return int(input_bytes * factor)

    @staticmethod
    def _estimate_markdown_tokens(output_bytes: int) -> str:
        """Estimate tokens in output markdown"""
        # Markdown is roughly 0.33 tokens per byte
        return "x" * int(output_bytes * 0.33)

    def _write_log(self, record: Dict):
        """Append record to JSONL log"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def export(self, format: str = "json", output_path: Optional[Path] = None) -> str:
        """Export stats as JSON or CSV"""
        stats = self.get_stats()

        if format == "json":
            result = json.dumps(stats, indent=2)
        elif format == "csv":
            # Simple CSV export
            lines = ["format,count,input_tokens,output_tokens,savings_tokens,avg_savings_pct"]
            for fmt, data in stats["by_format"].items():
                lines.append(
                    f"{fmt},{data['count']},{data['input_tokens']},"
                    f"{data['output_tokens']},{data['savings_tokens']},{data['avg_savings_pct']}"
                )
            result = "\n".join(lines)
        else:
            raise ValueError(f"Unknown format: {format}")

        if output_path:
            Path(output_path).write_text(result)

        return result


def estimate_tokens(file_path: str, format: Optional[str] = None) -> int:
    """Quick estimate of tokens in a file"""
    path = Path(file_path)
    if not format:
        format = path.suffix.lstrip(".").lower()

    bytes_size = path.stat().st_size
    return TokenEconomy._estimate_tokens(bytes_size, format)
