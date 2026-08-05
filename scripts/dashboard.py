#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard de Economia - Auto-Convert
Visualizar estatísticas de economia de tokens em tempo real
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from converters_advanced import DashboardGenerator

ECONOMY_FILE = Path.home() / "markdown" / ".metadata" / "economy_stats.json"

def print_console_dashboard():
    """Imprime dashboard no console (ASCII art)"""

    if not ECONOMY_FILE.exists():
        print("❌ Nenhum arquivo de estatísticas encontrado")
        print("Execute a skill primeiro para gerar dados")
        return

    try:
        with open(ECONOMY_FILE, 'r') as f:
            stats = json.load(f)
    except:
        print("❌ Erro ao ler arquivo de estatísticas")
        return

    total_saved = stats.get('total_tokens_saved', 0)
    conversions = stats.get('conversions', 0)
    daily_stats = stats.get('daily_stats', {})

    # Cabeçalho
    print("\n" + "="*70)
    print("📊 AUTO-CONVERT - DASHBOARD DE ECONOMIA")
    print("="*70 + "\n")

    # Estatísticas principais
    print(f"💰 TOTAL ECONOMIZADO: {total_saved:,.0f} tokens")
    print(f"📁 CONVERSÕES: {conversions}")
    if conversions > 0:
        print(f"📈 MÉDIA: {total_saved/conversions:,.0f} tokens/conversão")

    # Hoje
    today = datetime.now().strftime("%Y-%m-%d")
    today_data = daily_stats.get(today, {})
    today_saved = sum(today_data.values()) if today_data else 0
    today_count = len(today_data)

    print(f"\n🌅 HOJE ({today}):")
    print(f"   💾 Economizado: {today_saved:,.0f} tokens")
    print(f"   📂 Conversões: {today_count}")

    # Últimos 7 dias
    print(f"\n📅 ÚLTIMOS 7 DIAS:")
    weekly_total = 0
    for i in range(7):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        day_data = daily_stats.get(day, {})
        day_saved = sum(day_data.values()) if day_data else 0
        weekly_total += day_saved
        print(f"   {day}: {day_saved:>10,.0f} tokens")

    print(f"   {'─'*35}")
    print(f"   TOTAL: {weekly_total:>20,.0f} tokens")

    # Formatos mais usados
    format_stats = {}
    for day_data in daily_stats.values():
        for fmt, tokens in day_data.items():
            if fmt not in format_stats:
                format_stats[fmt] = {'tokens': 0, 'count': 0}
            format_stats[fmt]['tokens'] += tokens
            format_stats[fmt]['count'] += 1

    if format_stats:
        print(f"\n🏆 FORMATOS TOP:")
        sorted_formats = sorted(format_stats.items(), key=lambda x: x[1]['tokens'], reverse=True)
        for i, (fmt, data) in enumerate(sorted_formats[:5], 1):
            print(f"   {i}. .{fmt:8} → {data['tokens']:>12,.0f} tokens ({data['count']} conversões)")

    # Economia monetária (para referência)
    cost_per_1k_tokens = 0.003  # Preço Claude
    cost_saved = (total_saved / 1000) * cost_per_1k_tokens

    print(f"\n💵 ECONOMIA MONETÁRIA (referência):")
    print(f"   Custo evitado: ${cost_saved:.2f} em tokens")

    # Próximas milestones
    milestones = [10000, 100000, 1000000, 10000000]
    for milestone in milestones:
        if total_saved < milestone:
            remaining = milestone - total_saved
            print(f"   🎯 Próximo: {milestone:,} tokens (faltam {remaining:,})")
            break

    print("\n" + "="*70 + "\n")

def generate_html_dashboard():
    """Gera arquivo HTML do dashboard"""

    if not ECONOMY_FILE.exists():
        print("❌ Nenhum arquivo de estatísticas encontrado")
        return

    stats_dict = DashboardGenerator.generate_dashboard(str(ECONOMY_FILE))
    html = DashboardGenerator.render_html_dashboard(stats_dict)

    output_file = Path.home() / "markdown" / "dashboard.html"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto-Convert Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: white; margin-bottom: 30px; text-align: center; font-size: 32px; }}
        {html}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Auto-Convert - Dashboard de Economia</h1>
        {html}
    </div>
</body>
</html>
        """)

    print(f"✅ Dashboard gerado: {output_file}")
    print(f"   Abra no navegador para visualizar")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "html":
        generate_html_dashboard()
    else:
        print_console_dashboard()
