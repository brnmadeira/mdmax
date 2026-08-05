#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Convert Wrapper - Dispara automaticamente ao ler arquivos
Integrado com hooks do Claude Code
"""

import sys
import os
import json
from pathlib import Path
import subprocess

# Fix encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SUPPORTED_EXTENSIONS = ['.pdf', '.xlsx', '.xls', '.xlsm', '.csv', '.tsv', '.txt', '.json', '.ods', '.docx', '.pptx', '.svg', '.jpg', '.jpeg', '.png', '.epub']
SCRIPT_DIR = Path(__file__).parent
CONVERT_SCRIPT = SCRIPT_DIR / "convert_ultimate.py"

def should_auto_convert(file_path):
    """Verifica se arquivo deve ser convertido"""
    try:
        path = Path(file_path)
        return path.suffix.lower() in SUPPORTED_EXTENSIONS
    except:
        return False

def run_convert(file_path):
    """Executa conversão e retorna resultado"""
    try:
        result = subprocess.run(
            [sys.executable, str(CONVERT_SCRIPT), file_path, "markdown"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr, "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}

def get_counter_bar(tokens_saved):
    """Cria barra visual de tokens economizados"""
    total_per_bar = 10000  # 10K tokens = 1 bloco
    blocks = int(tokens_saved / total_per_bar)
    remainder = (tokens_saved % total_per_bar) / total_per_bar

    bar = "[" + "█" * blocks
    if remainder > 0 and blocks < 10:
        bar += "▓" if remainder > 0.5 else "░"
    bar += " " * (10 - blocks - 1) + "]"
    return bar

def display_result(result):
    """Exibe resultado de forma bonita"""
    if not result.get("success", True):
        print(f"Erro: {result.get('error', 'Desconhecido')}")
        return

    print("\n" + "="*70)
    print("AUTO-CONVERT TO MARKDOWN (ULTIMATE)")
    print("="*70)

    # Contador de economia
    if "economy_summary" in result:
        econ = result["economy_summary"]
        total_saved = econ.get('total_tokens_saved', 0)
        bar = get_counter_bar(total_saved)
        print(f"\nCONTADOR DE TOKENS ECONOMIZADOS:")
        print(f"   {bar} {total_saved:,} tokens")
        print(f"   Conversoes: {econ.get('total_conversions', '?')}")
        print(f"   Media: {econ.get('average_per_conversion', '?'):,} tokens/conversao")

    # Duplicata
    if result.get("source") == "duplicate":
        print(f"\n[DUPLICATA DETECTADA]")
        print(f"   Arquivo ja foi convertido anteriormente")
        print(f"   Reutilizando conversao anterior (100% economia)")
        print(f"   Markdown: {result.get('markdown_file', '')}")
        print("\n" + "="*70 + "\n")
        return

    # Predição
    if "recommendations" in result:
        recs = result["recommendations"]
        print(f"\nPREDICAO DE TOKENS:")
        print(f"   Original: {recs.get('estimated_tokens_original', '?')} tokens")
        print(f"   Com economia: {recs.get('estimated_tokens_after', '?')} tokens")
        print(f"   Economia: {result.get('economia_tokens', '?')} tokens")

    # Recomendações
    if "recommendations" in result:
        recs = result["recommendations"]
        print(f"\nRECOMENDACOES INTELIGENTES:")
        print(f"   Modo: {recs.get('recommended_mode', '?').upper()}")
        if recs.get('recommendations'):
            for rec in recs['recommendations']:
                print(f"   - {rec.get('reason', '')}")
                print(f"     -> {rec.get('suggestion', '')}")

    # Qualidade
    if "quality_analysis" in result:
        qa = result["quality_analysis"]
        print(f"\nANALISE DE QUALIDADE:")
        print(f"   Score: {qa.get('quality_score', '?')}/100")
        print(f"   Compressao: {qa.get('compression_ratio', '?')}%")
        if not qa.get('issues'):
            print(f"   Issues: NENHUM")
        else:
            for issue in qa['issues']:
                print(f"   - {issue.get('message', '')}")

    # Arquivo
    if "markdown_file" in result:
        print(f"\nARQUIVO GERADO:")
        print(f"   {result.get('markdown_file', '')}")

    print("\n" + "="*70 + "\n")

def show_dashboard(format_type='console'):
    """Mostra dashboard avançado"""
    try:
        dashboard_script = SCRIPT_DIR / "dashboard_advanced.py"
        if not dashboard_script.exists():
            return

        cmd = [sys.executable, str(dashboard_script)]
        if format_type == 'html':
            cmd.append('html')

        subprocess.run(cmd, capture_output=False)
    except Exception as e:
        pass  # Dashboard é opcional

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python auto_convert_wrapper.py <arquivo>")
        print("     python auto_convert_wrapper.py dashboard [html]")
        sys.exit(1)

    if sys.argv[1].lower() == "dashboard":
        fmt = sys.argv[2] if len(sys.argv) > 2 else 'console'
        show_dashboard(fmt)
        sys.exit(0)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        sys.exit(1)

    if not should_auto_convert(file_path):
        print(f"⏭️  Arquivo não suportado: {file_path}")
        print(f"   Formatos suportados: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(0)

    print(f"🔄 Processando: {Path(file_path).name}")
    result = run_convert(file_path)
    display_result(result)
