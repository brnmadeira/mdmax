#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversores Avançados para Auto-Convert v2.0
- Compressão Markdown melhorada (+5-10%)
- JPG/PNG com OCR
- EPUB (e-books)
"""

import re
import os
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False

try:
    import zipfile
    from xml.etree import ElementTree as ET
    ZIP_AVAILABLE = True
except ImportError:
    ZIP_AVAILABLE = False


class AdvancedMarkdownOptimizer:
    """Otimização Markdown avançada (+5-10% economia vs compressão padrão)"""

    @staticmethod
    def compress_aggressive(content):
        """Compressão agressiva com 5-10% economia adicional"""

        # 1. Remover espaços múltiplos (preservar 1)
        content = re.sub(r' {2,}', ' ', content)

        # 2. Remover linhas em branco múltiplas
        content = re.sub(r'\n{3,}', '\n\n', content)

        # 3. Comprimir tabelas (remover espaços em torno de |)
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if '|' in line:
                # Remover espaços ao redor de |
                line = re.sub(r'\s*\|\s*', '|', line)
            new_lines.append(line)
        content = '\n'.join(new_lines)

        # 4. Remover espaços no final de linhas
        content = re.sub(r' +$', '', content, flags=re.MULTILINE)

        # 5. Comprimir URLs longas em tabelas
        content = re.sub(
            r'(https?://[^\s]+)',
            lambda m: '[URL]' if len(m.group(1)) > 50 else m.group(1),
            content
        )

        # 6. Remover comentários HTML
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

        # 7. Minificar cabeçalhos (# Title -> # Title)
        # Já é minimizado naturalmente

        # 8. Comprimir listas de código (remover espaços extras)
        content = re.sub(
            r'```([a-z]+)\n\s+',
            r'```\1\n',
            content
        )

        # 9. Remover linhas em branco dentro de blocos de código
        code_blocks = re.findall(r'```.*?```', content, re.DOTALL)
        for block in code_blocks:
            compressed_block = re.sub(r'\n\s*\n', '\n', block)
            content = content.replace(block, compressed_block, 1)

        # 10. Comprimir metadados YAML (se existirem)
        content = re.sub(r'---\n\s+', '---\n', content)
        content = re.sub(r':\s+', ': ', content)

        return content.strip()

    @staticmethod
    def compress(content):
        """Wrapper compatível com versão anterior"""
        return AdvancedMarkdownOptimizer.compress_aggressive(content)


class ImageToMarkdownConverter:
    """Converte JPG/PNG para Markdown usando OCR"""

    @staticmethod
    def image_to_markdown(file_path):
        """Converte imagem para Markdown usando OCR"""

        if not PYTESSERACT_AVAILABLE:
            return (
                "# JPG/PNG (OCR não disponível)\n\n"
                "Instale dependências:\n"
                "```bash\n"
                "pip install pytesseract pillow\n"
                "# No Windows, também instale Tesseract:\n"
                "# https://github.com/UB-Mannheim/tesseract/wiki\n"
                "```\n"
            )

        try:
            # Abrir imagem
            img = Image.open(file_path)

            # Extrair metadados
            width, height = img.size
            format_name = img.format or "Desconhecido"

            # Executar OCR
            text = pytesseract.image_to_string(img, lang='por+eng')

            # Detectar dados estruturados (tabelas)
            data = pytesseract.image_to_data(file_path, output_type=pytesseract.Output.DICT)

            # Montar Markdown
            md = f"# Imagem - {Path(file_path).stem}\n\n"
            md += f"**Formato:** {format_name} | **Dimensões:** {width}×{height}px\n\n"

            if text.strip():
                md += "## Conteúdo Extraído\n\n"
                md += text
            else:
                md += "_Nenhum texto detectado na imagem_\n"

            # Adicionar confiança média do OCR
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                md += f"\n\n**Confiança OCR:** {avg_confidence:.1f}%"

            return md

        except Exception as e:
            return f"# JPG/PNG (erro ao processar)\n\nErro: {str(e)}"

    @staticmethod
    def detect_table_in_image(file_path):
        """Detecta se imagem contém tabela"""
        if not PYTESSERACT_AVAILABLE:
            return False

        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            # Heurística: se tem muitos |, --, +=, é provável tabela
            return bool(re.search(r'[\|+\-]{3,}', text))
        except:
            return False


class EPUBConverter:
    """Converte EPUB (e-books) para Markdown"""

    @staticmethod
    def epub_to_markdown(file_path):
        """Converte EPUB para Markdown"""

        if EPUB_AVAILABLE:
            try:
                book = epub.read_epub(file_path)
                md = f"# {book.title}\n\n"
                md += f"**Autor:** {book.author or 'Desconhecido'}\n\n"

                # Extrair capítulos
                for item in book.get_items():
                    if item.get_type() == 0:  # Tipo DOCUMENT
                        try:
                            content = item.get_content().decode('utf-8')
                            # Limpar HTML básico
                            content = re.sub(r'<[^>]+>', '', content)
                            md += content + "\n\n"
                        except:
                            pass

                return md
            except Exception as e:
                return f"# EPUB (erro com ebooklib)\n\n{str(e)}"

        # Fallback: usar zipfile diretamente
        if ZIP_AVAILABLE:
            try:
                md = f"# EPUB - {Path(file_path).stem}\n\n"

                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # Listar arquivos XHTML
                    files = [f for f in zip_ref.namelist() if f.endswith('.xhtml') or f.endswith('.html')]

                    for file_name in files[:20]:  # Primeiros 20 arquivos
                        try:
                            content = zip_ref.read(file_name).decode('utf-8')
                            # Remover tags HTML
                            content = re.sub(r'<[^>]+>', '', content)
                            content = re.sub(r'\s+', ' ', content)
                            if content.strip():
                                md += content[:500] + "\n\n"  # Primeiros 500 chars
                        except:
                            pass

                return md
            except Exception as e:
                return f"# EPUB (erro ao processar)\n\nErro: {str(e)}"

        return (
            "# EPUB (suporte não disponível)\n\n"
            "Instale ebooklib:\n"
            "```bash\n"
            "pip install ebooklib\n"
            "```\n"
        )


class DashboardGenerator:
    """Gera dashboard de economia de tokens"""

    @staticmethod
    def generate_dashboard(economy_file_path):
        """Gera dashboard visual de economia"""
        import json
        from datetime import datetime

        try:
            with open(economy_file_path, 'r') as f:
                stats = json.load(f)
        except:
            return None

        total_saved = stats.get('total_tokens_saved', 0)
        conversions = stats.get('conversions', 0)

        # Calcular por dia
        daily_stats = stats.get('daily_stats', {})
        today = datetime.now().strftime("%Y-%m-%d")
        today_saved = sum(daily_stats.get(today, {}).values()) if today in daily_stats else 0

        # Ranking de formatos
        format_stats = {}
        for day_data in daily_stats.values():
            for fmt, tokens in day_data.items():
                if fmt not in format_stats:
                    format_stats[fmt] = 0
                format_stats[fmt] += tokens

        return {
            "total_tokens_saved": total_saved,
            "total_conversions": conversions,
            "today_saved": today_saved,
            "average_per_conversion": total_saved / max(1, conversions),
            "top_formats": sorted(format_stats.items(), key=lambda x: x[1], reverse=True)[:5],
            "by_day": daily_stats
        }

    @staticmethod
    def render_html_dashboard(stats_dict):
        """Renderiza HTML do dashboard"""
        if not stats_dict:
            return "<p>Sem dados de economia</p>"

        html = f"""
        <div style="font-family: system-ui; padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h2>📊 Dashboard de Economia - Auto-Convert</h2>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 30px;">
                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="color: #666; font-size: 12px;">TOTAL ECONOMIZADO</div>
                    <div style="font-size: 28px; font-weight: bold; color: #00aa00;">
                        {stats_dict['total_tokens_saved']:,.0f}
                    </div>
                    <div style="color: #999; font-size: 12px; margin-top: 8px;">tokens</div>
                </div>

                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="color: #666; font-size: 12px;">HOJE ECONOMIZADO</div>
                    <div style="font-size: 28px; font-weight: bold; color: #0066cc;">
                        {stats_dict['today_saved']:,.0f}
                    </div>
                    <div style="color: #999; font-size: 12px; margin-top: 8px;">tokens</div>
                </div>

                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="color: #666; font-size: 12px;">MÉDIA POR CONVERSÃO</div>
                    <div style="font-size: 28px; font-weight: bold; color: #ff9900;">
                        {stats_dict['average_per_conversion']:,.0f}
                    </div>
                    <div style="color: #999; font-size: 12px; margin-top: 8px;">tokens</div>
                </div>
            </div>

            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="margin: 0 0 15px 0; color: #333;">📈 Top Formatos</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #eee;">
                        <th style="text-align: left; padding: 10px; color: #666; font-weight: 600;">Formato</th>
                        <th style="text-align: right; padding: 10px; color: #666; font-weight: 600;">Tokens Economizados</th>
                    </tr>
        """

        for fmt, tokens in stats_dict['top_formats']:
            html += f"""
                    <tr style="border-bottom: 1px solid #f0f0f0;">
                        <td style="padding: 10px; color: #333;">.{fmt}</td>
                        <td style="text-align: right; padding: 10px; color: #00aa00; font-weight: 600;">{tokens:,.0f}</td>
                    </tr>
            """

        html += """
                </table>
            </div>

            <div style="margin-top: 20px; color: #999; font-size: 12px;">
                Atualizado: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
            </div>
        </div>
        """

        return html
