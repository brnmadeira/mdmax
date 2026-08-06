#!/usr/bin/env python3
"""
MdMax Budget Planner - Token budget forecasting and planning
Feature [5] of v2.2: Plan token budgets and forecast savings
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import statistics


class BudgetPlanner:
    """Plan and forecast token budgets"""

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / '.mdmax'
        self.stats_file = self.config_dir / 'token_stats.json'
        self.budget_file = self.config_dir / 'budget.json'
        self._ensure_files()

    def _ensure_files(self):
        """Ensure config files exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.stats_file.exists():
            self.stats_file.write_text(json.dumps([], indent=2))

        if not self.budget_file.exists():
            self.budget_file.write_text(json.dumps({
                'monthly_budget': None,
                'alerts_enabled': True,
                'alert_threshold': 80,
            }, indent=2))

    def record_conversion(self, tokens_saved: int, file_size_mb: float, file_format: str):
        """Record a conversion for statistics"""
        stats = json.loads(self.stats_file.read_text())

        stats.append({
            'timestamp': datetime.now().isoformat(),
            'tokens_saved': tokens_saved,
            'file_size_mb': file_size_mb,
            'file_format': file_format,
        })

        self.stats_file.write_text(json.dumps(stats, indent=2))

    def set_monthly_budget(self, tokens: int):
        """Set monthly token budget"""
        budget = json.loads(self.budget_file.read_text())
        budget['monthly_budget'] = tokens
        self.budget_file.write_text(json.dumps(budget, indent=2))

    def get_monthly_budget(self) -> Optional[int]:
        """Get current monthly budget"""
        budget = json.loads(self.budget_file.read_text())
        return budget.get('monthly_budget')

    def forecast_monthly_savings(self) -> Dict:
        """Forecast monthly savings based on historical data"""
        stats = json.loads(self.stats_file.read_text())

        if not stats:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough conversion history to forecast',
            }

        # Get stats from last 30 days
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)

        recent_stats = [
            s for s in stats
            if datetime.fromisoformat(s['timestamp']) > thirty_days_ago
        ]

        if not recent_stats:
            return {
                'status': 'insufficient_data',
                'message': 'No conversions in last 30 days',
            }

        # Calculate statistics
        total_conversions = len(recent_stats)
        total_tokens_saved = sum(s['tokens_saved'] for s in recent_stats)
        avg_tokens_per_file = total_tokens_saved / total_conversions
        avg_file_size = statistics.mean(s['file_size_mb'] for s in recent_stats)

        # Forecast for full month
        conversions_per_day = total_conversions / 30
        forecasted_monthly = int(avg_tokens_per_file * conversions_per_day * 30)

        # Cost calculation (Claude API pricing)
        cost_per_token = 0.00027  # $0.27 per 1M tokens (approximate)
        monthly_savings_usd = (forecasted_monthly * cost_per_token) / 1000000

        return {
            'status': 'success',
            'recent_conversions': total_conversions,
            'recent_days': 30,
            'total_tokens_saved': total_tokens_saved,
            'avg_tokens_per_file': avg_tokens_per_file,
            'avg_file_size_mb': avg_file_size,
            'conversions_per_day': conversions_per_day,
            'forecasted_monthly_tokens': forecasted_monthly,
            'forecasted_monthly_savings_usd': monthly_savings_usd,
        }

    def plan_with_budget(self, monthly_token_budget: int) -> Dict:
        """Plan file conversions with a monthly budget"""
        forecast = self.forecast_monthly_savings()

        if forecast['status'] != 'success':
            return {
                'status': 'error',
                'message': forecast['message'],
            }

        avg_tokens_per_file = forecast['avg_tokens_per_file']
        files_that_fit = int(monthly_token_budget / avg_tokens_per_file)
        avg_file_size = forecast['avg_file_size_mb']
        total_data_size = files_that_fit * avg_file_size

        # Cost savings
        cost_per_token = 0.00027
        actual_savings = (monthly_token_budget * cost_per_token) / 1000000

        # If forecast exceeds budget
        budget_utilization = (forecast['forecasted_monthly_tokens'] / monthly_token_budget * 100) if monthly_token_budget else 0

        return {
            'status': 'success',
            'monthly_budget_tokens': monthly_token_budget,
            'avg_tokens_per_file': avg_tokens_per_file,
            'files_can_process': files_that_fit,
            'estimated_data_size_gb': total_data_size / 1024,
            'monthly_savings_usd': actual_savings,
            'budget_utilization_percent': budget_utilization,
            'alert_level': self._get_alert_level(budget_utilization),
            'recommendation': self._get_recommendation(budget_utilization, files_that_fit),
        }

    def _get_alert_level(self, utilization: float) -> str:
        """Get alert level based on budget utilization"""
        if utilization < 50:
            return 'low'
        elif utilization < 80:
            return 'medium'
        elif utilization < 100:
            return 'high'
        else:
            return 'critical'

    def _get_recommendation(self, utilization: float, files_count: int) -> str:
        """Get recommendation based on budget analysis"""
        if utilization < 50:
            return f'Budget is under-utilized. You can process {files_count} files safely this month.'
        elif utilization < 80:
            return f'Good budget usage. Processing {files_count} files will use 80% of budget.'
        elif utilization < 100:
            return f'High budget usage. Only {files_count} files can be processed before exceeding budget.'
        else:
            return f'Budget exceeded! Reduce processing or increase monthly budget to process {files_count} files.'

    def generate_report(self, monthly_budget: Optional[int] = None) -> str:
        """Generate a comprehensive budget report"""
        if monthly_budget is None:
            monthly_budget = self.get_monthly_budget()

        report = "╔════════════════════════════════════════════════════════════╗\n"
        report += "║           MdMax Token Budget Planner Report                 ║\n"
        report += "╚════════════════════════════════════════════════════════════╝\n\n"

        # Forecast
        forecast = self.forecast_monthly_savings()

        if forecast['status'] == 'success':
            report += "📊 MONTHLY FORECAST (based on last 30 days)\n"
            report += f"  Total conversions: {forecast['recent_conversions']}\n"
            report += f"  Total tokens saved: {forecast['total_tokens_saved']:,}\n"
            report += f"  Avg per file: {forecast['avg_tokens_per_file']:.0f} tokens\n"
            report += f"  Avg file size: {forecast['avg_file_size_mb']:.1f} MB\n"
            report += f"  Daily rate: {forecast['conversions_per_day']:.1f} files/day\n\n"

            report += "💰 PROJECTED MONTHLY SAVINGS\n"
            report += f"  Tokens (forecasted): {forecast['forecasted_monthly_tokens']:,}\n"
            report += f"  USD savings: ${forecast['forecasted_monthly_savings_usd']:.2f}\n\n"

            if monthly_budget:
                plan = self.plan_with_budget(monthly_budget)

                report += "🎯 BUDGET PLAN\n"
                report += f"  Monthly budget: {monthly_budget:,} tokens\n"
                report += f"  Files to process: {plan['files_can_process']}\n"
                report += f"  Data size (est): {plan['estimated_data_size_gb']:.1f} GB\n"
                report += f"  Budget usage: {plan['budget_utilization_percent']:.1f}%\n"
                report += f"  Alert level: {plan['alert_level'].upper()}\n\n"

                report += "💡 RECOMMENDATION\n"
                report += f"  {plan['recommendation']}\n\n"

        else:
            report += "⚠️ NOT ENOUGH DATA\n"
            report += f"  {forecast['message']}\n"
            report += "  Process some files first to get forecasts.\n\n"

        report += "════════════════════════════════════════════════════════════\n"

        return report


def print_report(monthly_budget: Optional[int] = None):
    """Print budget report to console"""
    planner = BudgetPlanner()
    print(planner.generate_report(monthly_budget))


def set_budget_cli(tokens: int):
    """CLI: Set monthly budget"""
    planner = BudgetPlanner()
    planner.set_monthly_budget(tokens)
    print(f"✅ Monthly budget set to {tokens:,} tokens")
    print_report(tokens)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--set':
        if len(sys.argv) > 2:
            try:
                tokens = int(sys.argv[2])
                set_budget_cli(tokens)
            except ValueError:
                print(f"Error: {sys.argv[2]} is not a valid number")
                sys.exit(1)
        else:
            print("Usage: budget_planner.py --set <tokens>")
            sys.exit(1)
    else:
        print_report()
