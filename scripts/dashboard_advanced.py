#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MdMax Dashboard Advanced - Contador com 5 Melhorias
- Ranking em tempo real
- Projeção de economia mensal
- Notificações de milestone
- Export de estatísticas
- Gráfico de tendência
"""

import json
import sys
import csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

ECONOMY_FILE = Path.home() / "markdown" / ".metadata" / "economy_stats.json"
EXPORT_DIR = Path.home() / "markdown" / "exports"

class MdMaxDashboard:
    """Dashboard avançado com 5 features de contador"""

    @staticmethod
    def load_stats():
        """Carrega estatísticas"""
        if not ECONOMY_FILE.exists():
            return None

        with open(ECONOMY_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def feature_1_ranking_realtime():
        """FEATURE 1: Ranking em tempo real (qual formato economiza mais)"""
        stats = MdMaxDashboard.load_stats()
        if not stats:
            return None

        # Agregar por formato
        format_stats = {}
        for day_data in stats.get('daily_stats', {}).values():
            for fmt, tokens in day_data.items():
                if fmt not in format_stats:
                    format_stats[fmt] = {'tokens': 0, 'count': 0}
                format_stats[fmt]['tokens'] += tokens
                format_stats[fmt]['count'] += 1

        # Ordenar por economia
        ranking = sorted(
            format_stats.items(),
            key=lambda x: x[1]['tokens'],
            reverse=True
        )

        return ranking

    @staticmethod
    def feature_2_monthly_projection():
        """FEATURE 2: Projeção de economia mensal"""
        stats = MdMaxDashboard.load_stats()
        if not stats:
            return None

        daily_stats = stats.get('daily_stats', {})
        today = datetime.now()

        # Pegar últimos 30 dias
        last_30_days = {}
        for i in range(30):
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if day in daily_stats:
                last_30_days[day] = sum(daily_stats[day].values())
            else:
                last_30_days[day] = 0

        # Calcular média diária
        total_30_days = sum(last_30_days.values())
        avg_per_day = total_30_days / 30 if total_30_days > 0 else 0

        # Projetar para 30 dias
        projected_monthly = avg_per_day * 30

        return {
            'last_30_days_actual': total_30_days,
            'average_per_day': avg_per_day,
            'projected_monthly': projected_monthly,
            'projected_yearly': projected_monthly * 12
        }

    @staticmethod
    def feature_3_milestones():
        """FEATURE 3: Notificações de milestone atingidos"""
        stats = MdMaxDashboard.load_stats()
        if not stats:
            return None

        total_saved = stats.get('total_tokens_saved', 0)

        milestones = [10000, 50000, 100000, 500000, 1000000, 5000000, 10000000]
        milestones_reached = [m for m in milestones if total_saved >= m]
        next_milestone = next((m for m in milestones if total_saved < m), None)

        return {
            'milestones_reached': milestones_reached,
            'next_milestone': next_milestone,
            'progress_to_next': (total_saved / next_milestone * 100) if next_milestone else 100
        }

    @staticmethod
    def feature_4_export_stats(format_type='json'):
        """FEATURE 4: Export de estatísticas (CSV, JSON)"""
        stats = MdMaxDashboard.load_stats()
        if not stats:
            return None

        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format_type == 'json':
            filename = EXPORT_DIR / f"mdmax_stats_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)

        elif format_type == 'csv':
            filename = EXPORT_DIR / f"mdmax_stats_{timestamp}.csv"

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Data', 'Formato', 'Tokens Economizados'])

                for date, formats in stats.get('daily_stats', {}).items():
                    for fmt, tokens in formats.items():
                        writer.writerow([date, fmt, tokens])

        return str(filename)

    @staticmethod
    def feature_5_trend_chart():
        """FEATURE 5: Gráfico de tendência de economia"""
        stats = MdMaxDashboard.load_stats()
        if not stats:
            return None

        daily_stats = stats.get('daily_stats', {})
        today = datetime.now()

        # Últimos 30 dias
        trend = {}
        for i in range(29, -1, -1):
            day = (today - timedelta(days=i)).strftime("%m-%d")
            full_day = (today - timedelta(days=i)).strftime("%Y-%m-%d")

            if full_day in daily_stats:
                trend[day] = sum(daily_stats[full_day].values())
            else:
                trend[day] = 0

        return trend

    @staticmethod
    def print_console_dashboard_advanced():
        """Imprime dashboard completo no console"""
        stats = MdMaxDashboard.load_stats()

        if not stats:
            print("❌ Nenhum arquivo de estatísticas encontrado")
            return

        print("\n" + "="*80)
        print("🎯 MDMAX DASHBOARD AVANÇADO - CONTADOR COMPLETO")
        print("="*80 + "\n")

        # Estatísticas principais
        total_saved = stats.get('total_tokens_saved', 0)
        conversions = stats.get('conversions', 0)

        print(f"💰 TOTAL ECONOMIZADO: {total_saved:,.0f} tokens")
        print(f"📁 CONVERSÕES: {conversions}")
        if conversions > 0:
            print(f"📈 MÉDIA: {total_saved/conversions:,.0f} tokens/conversão\n")

        # FEATURE 1: Ranking em tempo real
        print("🏆 FEATURE 1 - RANKING EM TEMPO REAL")
        print("-" * 80)
        ranking = MdMaxDashboard.feature_1_ranking_realtime()
        if ranking:
            for i, (fmt, data) in enumerate(ranking[:10], 1):
                pct = (data['tokens'] / total_saved * 100) if total_saved > 0 else 0
                bar = "█" * int(pct / 5)
                print(f"{i:2}. .{fmt:8} │ {data['tokens']:>12,.0f} tokens │ {bar:<20} {pct:>5.1f}%")
        print()

        # FEATURE 2: Projeção mensal
        print("📊 FEATURE 2 - PROJEÇÃO DE ECONOMIA MENSAL")
        print("-" * 80)
        projection = MdMaxDashboard.feature_2_monthly_projection()
        if projection:
            print(f"Últimos 30 dias:     {projection['last_30_days_actual']:>15,.0f} tokens")
            print(f"Média por dia:       {projection['average_per_day']:>15,.0f} tokens")
            print(f"Projeção (30 dias):  {projection['projected_monthly']:>15,.0f} tokens")
            print(f"Projeção (1 ano):    {projection['projected_yearly']:>15,.0f} tokens")
        print()

        # FEATURE 3: Milestones
        print("🎯 FEATURE 3 - MILESTONES ATINGIDOS")
        print("-" * 80)
        milestones = MdMaxDashboard.feature_3_milestones()
        if milestones:
            reached = milestones['milestones_reached']
            if reached:
                for m in reached:
                    print(f"✅ {m:>10,.0f} tokens")
            else:
                print("Próximo milestone a atingir...")

            next_m = milestones['next_milestone']
            progress = milestones['progress_to_next']
            if next_m:
                bar = "█" * int(progress / 5)
                print(f"\n🎯 Próximo: {next_m:,.0f} tokens")
                print(f"Progresso: {bar:<20} {progress:.1f}%")
        print()

        # FEATURE 4: Export
        print("💾 FEATURE 4 - EXPORT DE ESTATÍSTICAS")
        print("-" * 80)
        json_file = MdMaxDashboard.feature_4_export_stats('json')
        csv_file = MdMaxDashboard.feature_4_export_stats('csv')
        print(f"✅ JSON exportado: {json_file}")
        print(f"✅ CSV exportado:  {csv_file}")
        print()

        # FEATURE 5: Tendência
        print("📈 FEATURE 5 - GRÁFICO DE TENDÊNCIA (ÚLTIMOS 30 DIAS)")
        print("-" * 80)
        trend = MdMaxDashboard.feature_5_trend_chart()
        if trend:
            max_value = max(trend.values()) if trend.values() else 1

            # Mostrar 10 últimos dias
            recent = dict(list(trend.items())[-10:])
            for day, tokens in recent.items():
                if max_value > 0:
                    bar_width = int((tokens / max_value) * 40)
                    bar = "█" * bar_width
                else:
                    bar = ""
                print(f"{day} │ {bar:<40} {tokens:>10,.0f}")

        print("\n" + "="*80)
        print(f"Atualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")

    @staticmethod
    def generate_html_dashboard_advanced():
        """Gera HTML dashboard com todas as features"""
        stats = MdMaxDashboard.load_stats()
        if not stats:
            print("❌ Nenhum arquivo de estatísticas encontrado")
            return

        ranking = MdMaxDashboard.feature_1_ranking_realtime()
        projection = MdMaxDashboard.feature_2_monthly_projection()
        milestones = MdMaxDashboard.feature_3_milestones()
        trend = MdMaxDashboard.feature_5_trend_chart()

        total_saved = stats.get('total_tokens_saved', 0)
        conversions = stats.get('conversions', 0)

        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MdMax Dashboard - Contador Avançado</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: white; margin-bottom: 30px; text-align: center; font-size: 32px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .stat-box {{
            text-align: center;
            padding: 20px;
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .ranking-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .ranking-table th {{
            background: #f0f0f0;
            padding: 10px;
            text-align: left;
            font-weight: 600;
            color: #333;
        }}
        .ranking-table td {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        .ranking-table tr:hover {{
            background: #f9f9f9;
        }}
        .progress-bar {{
            height: 24px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}
        .milestone {{
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 8px 16px;
            border-radius: 20px;
            margin: 4px;
            font-weight: 600;
        }}
        .milestone.reached {{
            background: #e8f5e9;
            color: #388e3c;
        }}
        .trend-chart {{
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            height: 200px;
            gap: 4px;
            margin: 20px 0;
        }}
        .trend-bar {{
            flex: 1;
            background: linear-gradient(180deg, #667eea, #764ba2);
            border-radius: 4px 4px 0 0;
            min-height: 4px;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            color: white;
            font-size: 10px;
            padding-bottom: 4px;
        }}
        .export-link {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            margin: 5px;
            transition: background 0.3s;
        }}
        .export-link:hover {{
            background: #764ba2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 MdMax Dashboard Avançado</h1>

        <!-- Stats Principais -->
        <div class="grid">
            <div class="card stat-box">
                <div class="stat-label">TOTAL ECONOMIZADO</div>
                <div class="stat-number">{total_saved:,.0f}</div>
                <div class="stat-label">tokens</div>
            </div>
            <div class="card stat-box">
                <div class="stat-label">CONVERSÕES</div>
                <div class="stat-number">{conversions}</div>
                <div class="stat-label">arquivos</div>
            </div>
            <div class="card stat-box">
                <div class="stat-label">MÉDIA POR CONVERSÃO</div>
                <div class="stat-number">{total_saved/max(conversions,1):,.0f}</div>
                <div class="stat-label">tokens</div>
            </div>
        </div>

        <!-- FEATURE 1: Ranking -->
        <div class="card">
            <h2>🏆 Feature 1: Ranking em Tempo Real</h2>
            <p style="color: #666; margin-bottom: 15px;">Formatos ordenados por economia total</p>
            <table class="ranking-table">
                <thead><tr><th>#</th><th>Formato</th><th>Tokens</th><th>%</th></tr></thead>
                <tbody>
"""

        if ranking:
            for i, (fmt, data) in enumerate(ranking[:10], 1):
                pct = (data['tokens'] / total_saved * 100) if total_saved > 0 else 0
                html += f"""
                <tr>
                    <td>{i}</td>
                    <td>.{fmt}</td>
                    <td>{data['tokens']:,.0f}</td>
                    <td>{pct:.1f}%</td>
                </tr>
"""

        html += """
                </tbody>
            </table>
        </div>

        <!-- FEATURE 2: Projeção Mensal -->
        <div class="grid">
"""

        if projection:
            html += f"""
            <div class="card">
                <h3>📊 Feature 2: Projeção Mensal</h3>
                <p style="color: #666; margin: 10px 0; font-size: 14px;">Últimos 30 dias: <strong>{projection['last_30_days_actual']:,.0f}</strong> tokens</p>
                <p style="color: #666; margin: 10px 0; font-size: 14px;">Média/dia: <strong>{projection['average_per_day']:,.0f}</strong> tokens</p>
                <div style="background: #f9f9f9; padding: 10px; border-radius: 6px; margin-top: 10px;">
                    <p style="font-size: 12px; color: #999;">Projeção anual</p>
                    <p style="font-size: 20px; font-weight: bold; color: #667eea;">{projection['projected_yearly']:,.0f}</p>
                    <p style="font-size: 12px; color: #999;">tokens/ano</p>
                </div>
            </div>
"""

        # FEATURE 3: Milestones
        if milestones:
            html += f"""
            <div class="card">
                <h3>🎯 Feature 3: Milestones</h3>
                <div style="margin: 10px 0;">
                    {' '.join([f'<span class="milestone reached">{m:,}</span>' for m in milestones['milestones_reached']])}
                </div>
                <p style="color: #666; margin-top: 15px; font-size: 14px;">Próximo: <strong>{milestones['next_milestone']:,}</strong></p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {milestones['progress_to_next']:.0f}%">
                        {milestones['progress_to_next']:.0f}%
                    </div>
                </div>
            </div>
"""

        html += """
        </div>

        <!-- FEATURE 4: Export -->
        <div class="card">
            <h3>💾 Feature 4: Export de Estatísticas</h3>
            <p style="color: #666; margin-bottom: 15px;">Baixe seus dados em diferentes formatos</p>
            <div>
                <a href="#" class="export-link">📥 JSON</a>
                <a href="#" class="export-link">📊 CSV</a>
            </div>
        </div>

        <!-- FEATURE 5: Tendência -->
        <div class="card">
            <h3>📈 Feature 5: Gráfico de Tendência</h3>
            <p style="color: #666; margin-bottom: 15px;">Últimos 30 dias</p>
            <div class="trend-chart">
"""

        if trend:
            max_value = max(trend.values()) if trend.values() else 1
            recent = dict(list(trend.items())[-10:])
            for day, tokens in recent.items():
                if max_value > 0:
                    height_pct = (tokens / max_value) * 100
                else:
                    height_pct = 0
                html += f'<div class="trend-bar" style="height: {height_pct}%;"></div>\n'

        html += f"""
            </div>
        </div>

        <div style="text-align: center; color: white; margin-top: 30px; font-size: 12px;">
            Atualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""

        output_file = EXPORT_DIR / "mdmax_dashboard_advanced.html"
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Dashboard HTML gerado: {output_file}")
        return str(output_file)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "html":
            MdMaxDashboard.generate_html_dashboard_advanced()
        elif sys.argv[1] == "export":
            fmt = sys.argv[2] if len(sys.argv) > 2 else "json"
            file = MdMaxDashboard.feature_4_export_stats(fmt)
            print(f"✅ Exportado: {file}")
    else:
        MdMaxDashboard.print_console_dashboard_advanced()
