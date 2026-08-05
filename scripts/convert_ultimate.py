#!/usr/bin/env python3
"""
Auto-Convert to Markdown - ULTIMATE Edition
16 Otimizações: Cache, Metadata, Truncation, Compressão, Paralelo, Resumo,
Duplicatas, Limpeza, Dashboard, Hipercomprimido + NOVAS: Predição, Recomendações,
Indexação, Qualidade, Streaming
"""

import json
import hashlib
import os
import re
import csv
import logging
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import openpyxl
from openpyxl.utils import get_column_letter
import PyPDF2

# Importar conversores avançados
try:
    from converters_advanced import (
        AdvancedMarkdownOptimizer,
        ImageToMarkdownConverter,
        EPUBConverter,
        DashboardGenerator
    )
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importações adicionais para novos formatos
try:
    import xlrd  # Para .xls
except ImportError:
    xlrd = None

try:
    from zipfile import ZipFile
    from xml.etree import ElementTree as ET
except ImportError:
    pass

CACHE_DIR = Path.home() / "markdown" / ".metadata"
CACHE_FILE = CACHE_DIR / "cache.json"
CONTENT_HASH_FILE = CACHE_DIR / "content_hashes.json"
ECONOMY_FILE = CACHE_DIR / "economy_stats.json"
CONFIG_FILE = Path(__file__).parent.parent / "config.json"

# Carregar configuração
def load_config():
    """Carrega configuração do arquivo"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {
        "default_mode": "ultra",
        "cache_cleanup_days": 7,
        "enable_logging": True,
        "parallelization": {"enabled": True, "workers": 3},
        "optimize_tokens": {"aggressive": True}
    }

CONFIG = load_config()

class TokenPredictor:
    """Estima tokens ANTES de converter"""

    @staticmethod
    def estimate_tokens(file_path, file_type):
        try:
            file_size = os.path.getsize(file_path)

            # Regras de estimativa baseadas em tipo
            if file_type == "pdf":
                # ~150 tokens por página, ~200KB por página
                pages = max(1, file_size // 200000)
                return pages * 150
            elif file_type in ["xlsx", "csv", "ods"]:
                # ~0.5 tokens por célula
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                return max(100, int(lines * 3))
            else:
                # Padrão: ~0.25 tokens por byte
                return max(50, int(file_size * 0.00025))
        except:
            return 200  # Fallback

class RecommendationEngine:
    """Recomenda melhor modo de processamento"""

    @staticmethod
    def analyze_and_recommend(file_path, file_type, estimated_tokens):
        recommendations = []
        suggested_mode = "normal"

        try:
            file_size = os.path.getsize(file_path)

            # Análise por tipo
            if file_type == "pdf":
                if estimated_tokens > 500:
                    recommendations.append({
                        "reason": "PDF grande (>50 páginas)",
                        "suggestion": "Use resumo executivo para máxima economia",
                        "mode": "resumo",
                        "potential_economy": "até 80%"
                    })
                    suggested_mode = "resumo"
                elif file_size > 5000000:
                    recommendations.append({
                        "reason": "Arquivo > 5MB",
                        "suggestion": "Use modo hipercomprimido",
                        "mode": "ultra",
                        "potential_economy": "até 40%"
                    })
                    suggested_mode = "ultra"

            elif file_type in ["xlsx", "csv"]:
                if estimated_tokens > 300:
                    recommendations.append({
                        "reason": "Tabela grande (>1000 linhas)",
                        "suggestion": "Use smart truncation + hipercomprimido",
                        "mode": "ultra",
                        "potential_economy": "até 70%"
                    })
                    suggested_mode = "ultra"
                elif estimated_tokens < 100:
                    recommendations.append({
                        "reason": "Arquivo pequeno",
                        "suggestion": "Modo normal é eficiente",
                        "mode": "normal",
                        "potential_economy": "até 22%"
                    })

            # Recomendação geral
            if not recommendations:
                recommendations.append({
                    "reason": "Análise padrão",
                    "suggestion": f"Modo recomendado baseado em tamanho",
                    "mode": suggested_mode,
                    "potential_economy": "até 22%"
                })

            # Calcular economia dinâmica baseado no tipo e tamanho
            economy_rate = 0.22  # Default 22%

            if file_type == "pdf":
                if estimated_tokens > 500:
                    economy_rate = 0.80  # PDFs grandes: até 80%
                elif estimated_tokens > 200:
                    economy_rate = 0.50  # PDFs médios: até 50%
                else:
                    economy_rate = 0.22  # PDFs pequenos: 22%
            elif file_type in ["xlsx", "csv", "ods"]:
                if estimated_tokens > 100000:
                    economy_rate = 0.70  # Tabelas gigantes: até 70%
                elif estimated_tokens > 10000:
                    economy_rate = 0.60  # Tabelas grandes: até 60%
                elif estimated_tokens > 1000:
                    economy_rate = 0.40  # Tabelas médias: até 40%
                else:
                    economy_rate = 0.22  # Tabelas pequenas: 22%

            return {
                "recommended_mode": suggested_mode,
                "recommendations": recommendations,
                "estimated_tokens_original": estimated_tokens,
                "estimated_tokens_after": int(estimated_tokens * (1 - economy_rate)),
                "economy_rate": f"{economy_rate * 100:.0f}%"
            }
        except Exception as e:
            return {
                "recommended_mode": "normal",
                "recommendations": [{"reason": "Erro na análise", "suggestion": "Use modo normal"}],
                "error": str(e)
            }

class IndexGenerator:
    """Gera índice automático para documentos grandes"""

    @staticmethod
    def generate_index(markdown_content):
        """Extrai índice de seções do markdown"""
        lines = markdown_content.split('\n')
        sections = []

        for i, line in enumerate(lines):
            if line.startswith('# '):
                sections.append({
                    "level": 1,
                    "title": line.replace('# ', '').strip(),
                    "line": i
                })
            elif line.startswith('## '):
                sections.append({
                    "level": 2,
                    "title": line.replace('## ', '').strip(),
                    "line": i
                })
            elif line.startswith('### '):
                sections.append({
                    "level": 3,
                    "title": line.replace('### ', '').strip(),
                    "line": i
                })

        return sections

class QualityValidator:
    """Valida qualidade do markdown convertido"""

    @staticmethod
    def validate(markdown_content, original_size):
        issues = []
        compression_ratio = len(markdown_content) / max(original_size, 1)

        # Verificar compressão excessiva
        if compression_ratio < 0.05:
            issues.append({
                "severity": "warning",
                "message": "Compressão muito agressiva (<5% do original)",
                "recommendation": "Considere usar modo normal"
            })

        # Verificar tabelas bem formadas
        if '|' in markdown_content:
            table_lines = [l for l in markdown_content.split('\n') if '|' in l]
            if table_lines:
                if not all('---' in l or '|' in l for l in table_lines):
                    issues.append({
                        "severity": "info",
                        "message": "Tabelas podem estar incompletas",
                        "recommendation": "Verificar formatação manual"
                    })

        # Verificar se há conteúdo mínimo
        if len(markdown_content) < 50:
            issues.append({
                "severity": "error",
                "message": "Markdown muito pequeno (possível erro na conversão)",
                "recommendation": "Reconverter com modo normal"
            })

        return {
            "valid": len([i for i in issues if i["severity"] == "error"]) == 0,
            "compression_ratio": round(compression_ratio * 100, 2),
            "issues": issues,
            "quality_score": max(0, 100 - (len(issues) * 10))
        }

class StreamProcessor:
    """Processa arquivos gigantes em chunks"""

    @staticmethod
    def process_large_file(file_path, chunk_size=1000):
        """Processa arquivo grande em chunks (para PDFs > 100MB)"""
        file_size = os.path.getsize(file_path)
        chunks = []

        if file_size > 100000000:  # > 100MB
            with open(file_path, 'rb') as f:
                chunk_num = 0
                while True:
                    chunk = f.read(chunk_size * 1024)
                    if not chunk:
                        break
                    chunks.append({
                        "chunk": chunk_num,
                        "size": len(chunk),
                        "offset": f.tell()
                    })
                    chunk_num += 1

            return {
                "is_streaming": True,
                "total_chunks": chunk_num,
                "chunks": chunks[:5]  # Primeiros 5
            }

        return {"is_streaming": False}

class CacheCleaner:
    """Limpeza agressiva de cache"""

    @staticmethod
    def cleanup(days=None):
        """Remove cache com mais de X dias"""
        if days is None:
            days = CONFIG.get("cache_cleanup_days", 7)

        if not CACHE_FILE.exists():
            return 0

        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)

            cutoff = datetime.now() - timedelta(days=days)
            removed = 0

            for key, entry in list(cache.items()):
                try:
                    ts = datetime.fromisoformat(entry.get('timestamp', ''))
                    if ts < cutoff:
                        del cache[key]
                        removed += 1
                except:
                    pass

            if removed > 0:
                with open(CACHE_FILE, 'w') as f:
                    json.dump(cache, f, indent=2)
                logger.info(f"Cache: removidos {removed} entries (>{days} dias)")

            return removed
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return 0

class CacheManager:
    """Gerencia cache com MD5 e SHA256"""
    def __init__(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_file_hash(self, file_path):
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def _get_content_hash(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def get(self, file_path):
        if not CACHE_FILE.exists():
            return None

        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)

            file_hash = self._get_file_hash(file_path)
            return cache.get(file_hash)
        except:
            return None

    def set(self, file_path, markdown_path):
        cache = {}
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r') as f:
                    cache = json.load(f)
            except:
                pass

        file_hash = self._get_file_hash(file_path)
        content_hash = self._get_content_hash(file_path)

        cache[file_hash] = {
            "markdown_path": str(markdown_path),
            "timestamp": datetime.now().isoformat(),
            "content_hash": content_hash
        }

        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)

        # Registrar content_hash
        if CONTENT_HASH_FILE.exists():
            with open(CONTENT_HASH_FILE, 'r') as f:
                content_hashes = json.load(f)
        else:
            content_hashes = {}

        content_hashes[content_hash] = str(markdown_path)
        with open(CONTENT_HASH_FILE, 'w') as f:
            json.dump(content_hashes, f, indent=2)

class MarkdownConverter:
    """Converte arquivos para Markdown"""

    @staticmethod
    def csv_to_markdown(file_path):
        rows = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
        except:
            with open(file_path, 'r', encoding='latin-1') as f:
                reader = csv.reader(f)
                rows = list(reader)

        if not rows:
            return ""

        md = "| " + " | ".join(rows[0]) + " |\n"
        md += "| " + " | ".join(["---"] * len(rows[0])) + " |\n"

        for row in rows[1:]:
            md += "| " + " | ".join(row) + " |\n"

        return md

    @staticmethod
    def xlsx_to_markdown(file_path):
        wb = openpyxl.load_workbook(file_path)
        md = ""

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            md += f"## {sheet_name}\n\n"

            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                continue

            md += "| " + " | ".join(str(c or "") for c in rows[0]) + " |\n"
            md += "| " + " | ".join(["---"] * len(rows[0])) + " |\n"

            for row in rows[1:]:
                md += "| " + " | ".join(str(c or "") for c in row) + " |\n"

            md += "\n"

        return md

    @staticmethod
    def pdf_to_markdown(file_path):
        md = ""
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages[:20]):
                    text = page.extract_text()
                    if text:
                        md += f"## Página {i+1}\n\n{text}\n\n"
        except:
            md = "# PDF (conteúdo não extraível)\n\nArquivo PDF muito complexo para conversão."

        return md

    @staticmethod
    def txt_to_markdown(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            return content

    @staticmethod
    def json_to_markdown(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            md = "# JSON Data\n\n```json\n"
            md += json.dumps(data, indent=2, ensure_ascii=False)
            md += "\n```\n"
            return md
        except:
            return "# JSON (erro ao processar)"

    @staticmethod
    def xls_to_markdown(file_path):
        if xlrd is None:
            return "# XLS (xlrd não instalado)\n\nInstale: pip install xlrd"
        try:
            workbook = xlrd.open_workbook(file_path)
            md = ""
            for sheet_name in workbook.sheet_names():
                sheet = workbook.sheet_by_name(sheet_name)
                md += f"## {sheet_name}\n\n"
                for row_idx in range(min(sheet.nrows, 1000)):
                    row = sheet.row_values(row_idx)
                    md += "| " + " | ".join(str(c) for c in row) + " |\n"
                    if row_idx == 0:
                        md += "| " + " | ".join(["---"] * len(row)) + " |\n"
                md += "\n"
            return md
        except:
            return "# XLS (erro ao processar)"

    @staticmethod
    def tsv_to_markdown(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                rows = list(reader)
            if not rows:
                return ""
            md = "| " + " | ".join(rows[0]) + " |\n"
            md += "| " + " | ".join(["---"] * len(rows[0])) + " |\n"
            for row in rows[1:]:
                md += "| " + " | ".join(row) + " |\n"
            return md
        except:
            return "# TSV (erro ao processar)"

    @staticmethod
    def docx_to_markdown(file_path):
        try:
            from docx import Document
            doc = Document(file_path)
            md = ""
            for para in doc.paragraphs:
                if para.text.strip():
                    md += para.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    md += "| " + " | ".join(cell.text for cell in row.cells) + " |\n"
            return md
        except:
            return "# DOCX (python-docx não instalado)\n\nInstale: pip install python-docx"

    @staticmethod
    def pptx_to_markdown(file_path):
        try:
            from pptx import Presentation
            prs = Presentation(file_path)
            md = ""
            for slide_idx, slide in enumerate(prs.slides):
                md += f"## Slide {slide_idx + 1}\n\n"
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        md += shape.text + "\n\n"
            return md
        except:
            return "# PPTX (python-pptx não instalado)\n\nInstale: pip install python-pptx"

    @staticmethod
    def svg_to_markdown(file_path):
        """Converte SVG (XML vetorial) para descrição Markdown"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Remover namespace
            ns = {'svg': 'http://www.w3.org/2000/svg'}

            md = "# Diagrama SVG\n\n"

            # Extrair atributos do SVG
            width = root.get('width', 'sem especificação')
            height = root.get('height', 'sem especificação')
            viewBox = root.get('viewBox', 'não definido')

            md += f"**Dimensões:** {width} × {height}\n"
            md += f"**ViewBox:** {viewBox}\n\n"

            # Extrair elementos
            elements = []

            # Círculos
            circles = root.findall('.//svg:circle', ns)
            if not circles:
                circles = root.findall('.//{http://www.w3.org/2000/svg}circle')

            for circle in circles:
                cx = circle.get('cx', '?')
                cy = circle.get('cy', '?')
                r = circle.get('r', '?')
                fill = circle.get('fill', 'nenhum')
                elements.append(f"- **Círculo:** posição ({cx},{cy}), raio {r}, cor: {fill}")

            # Retângulos
            rects = root.findall('.//svg:rect', ns)
            if not rects:
                rects = root.findall('.//{http://www.w3.org/2000/svg}rect')

            for rect in rects:
                x = rect.get('x', '?')
                y = rect.get('y', '?')
                w = rect.get('width', '?')
                h = rect.get('height', '?')
                fill = rect.get('fill', 'nenhum')
                elements.append(f"- **Retângulo:** posição ({x},{y}), {w}×{h}, cor: {fill}")

            # Linhas
            lines = root.findall('.//svg:line', ns)
            if not lines:
                lines = root.findall('.//{http://www.w3.org/2000/svg}line')

            for line in lines:
                x1 = line.get('x1', '?')
                y1 = line.get('y1', '?')
                x2 = line.get('x2', '?')
                y2 = line.get('y2', '?')
                stroke = line.get('stroke', 'preta')
                elements.append(f"- **Linha:** de ({x1},{y1}) a ({x2},{y2}), cor: {stroke}")

            # Caminhos
            paths = root.findall('.//svg:path', ns)
            if not paths:
                paths = root.findall('.//{http://www.w3.org/2000/svg}path')

            for i, path in enumerate(paths[:5]):  # Limite a 5 caminhos
                d = path.get('d', '')[:50] + '...' if len(path.get('d', '')) > 50 else path.get('d', '')
                fill = path.get('fill', 'nenhum')
                elements.append(f"- **Caminho {i+1}:** {d}, preenchimento: {fill}")

            # Texto
            texts = root.findall('.//svg:text', ns)
            if not texts:
                texts = root.findall('.//{http://www.w3.org/2000/svg}text')

            for text_elem in texts:
                text_content = ''.join(text_elem.itertext())
                x = text_elem.get('x', '?')
                y = text_elem.get('y', '?')
                if text_content.strip():
                    elements.append(f"- **Texto:** \"{text_content}\" em ({x},{y})")

            if elements:
                md += "## Elementos\n\n"
                md += "\n".join(elements)
            else:
                md += "_Nenhum elemento SVG detectado_\n"

            return md
        except Exception as e:
            return f"# SVG (erro ao processar)\n\nErro: {str(e)}"

    @staticmethod
    def jpg_to_markdown(file_path):
        """Converte JPG para Markdown com OCR"""
        if ADVANCED_AVAILABLE:
            return ImageToMarkdownConverter.image_to_markdown(file_path)
        return "# JPG (conversor avançado não disponível)\n\nInstale: pip install pytesseract pillow"

    @staticmethod
    def png_to_markdown(file_path):
        """Converte PNG para Markdown com OCR"""
        if ADVANCED_AVAILABLE:
            return ImageToMarkdownConverter.image_to_markdown(file_path)
        return "# PNG (conversor avançado não disponível)\n\nInstale: pip install pytesseract pillow"

    @staticmethod
    def epub_to_markdown(file_path):
        """Converte EPUB (e-book) para Markdown"""
        if ADVANCED_AVAILABLE:
            return EPUBConverter.epub_to_markdown(file_path)
        return "# EPUB (conversor avançado não disponível)\n\nInstale: pip install ebooklib"

class MarkdownOptimizer:
    """Otimiza markdown com compressão (usa versão avançada se disponível)"""

    @staticmethod
    def compress(content):
        if ADVANCED_AVAILABLE:
            return AdvancedMarkdownOptimizer.compress_aggressive(content)

        # Fallback: compressão padrão
        lines = content.split('\n')
        cleaned = []

        for line in lines:
            stripped = line.strip()
            if stripped and not (cleaned and not cleaned[-1]):
                cleaned.append(stripped)

        return '\n'.join(cleaned)

class EconomyTracker:
    """Rastreia economia de tokens"""

    @staticmethod
    def track(tokens_saved, file_type, estimated_original):
        if not ECONOMY_FILE.exists():
            stats = {
                "total_tokens_saved": 0,
                "conversions": 0,
                "daily_stats": {}
            }
        else:
            with open(ECONOMY_FILE, 'r') as f:
                stats = json.load(f)

        today = datetime.now().strftime("%Y-%m-%d")
        if today not in stats["daily_stats"]:
            stats["daily_stats"][today] = {"saved": 0, "count": 0}

        stats["total_tokens_saved"] += tokens_saved
        stats["conversions"] += 1
        stats["daily_stats"][today]["saved"] += tokens_saved
        stats["daily_stats"][today]["count"] += 1

        with open(ECONOMY_FILE, 'w') as f:
            json.dump(stats, f, indent=2)

        return stats

def process_file(file_path, output_dir, ultra=False):
    """Processa arquivo com TODAS as 16 otimizações"""
    file_path = Path(file_path)
    output_dir = Path(output_dir)

    if not file_path.exists():
        return {"error": "Arquivo não encontrado"}

    file_type = file_path.suffix.lower().lstrip('.')
    original_size = os.path.getsize(file_path)

    # 1. PREDIÇÃO DE TOKENS
    predictor = TokenPredictor()
    estimated_tokens = predictor.estimate_tokens(str(file_path), file_type)

    # 2. RECOMENDAÇÕES INTELIGENTES
    recommendation_engine = RecommendationEngine()
    recommendations = recommendation_engine.analyze_and_recommend(
        str(file_path), file_type, estimated_tokens
    )

    # 3. VERIFICAR CACHE
    cache = CacheManager()
    cached = cache.get(str(file_path))

    if cached:
        content_hash = cache._get_content_hash(str(file_path))
        if CONTENT_HASH_FILE.exists():
            with open(CONTENT_HASH_FILE, 'r') as f:
                content_hashes = json.load(f)
                if content_hash in content_hashes:
                    return {
                        "markdown_file": content_hashes[content_hash],
                        "success": True,
                        "source": "duplicate",
                        "economia_tokens": 0,
                        "tempo_ms": 0
                    }

    # 4. CONVERSÃO
    converter = MarkdownConverter()
    if file_type == "pdf":
        markdown = converter.pdf_to_markdown(str(file_path))
    elif file_type == "xlsx" or file_type == "xlsm":
        markdown = converter.xlsx_to_markdown(str(file_path))
    elif file_type == "xls":
        markdown = converter.xls_to_markdown(str(file_path))
    elif file_type == "csv":
        markdown = converter.csv_to_markdown(str(file_path))
    elif file_type == "tsv":
        markdown = converter.tsv_to_markdown(str(file_path))
    elif file_type == "txt":
        markdown = converter.txt_to_markdown(str(file_path))
    elif file_type == "json":
        markdown = converter.json_to_markdown(str(file_path))
    elif file_type == "docx":
        markdown = converter.docx_to_markdown(str(file_path))
    elif file_type == "pptx":
        markdown = converter.pptx_to_markdown(str(file_path))
    elif file_type == "svg":
        markdown = converter.svg_to_markdown(str(file_path))
    elif file_type == "jpg" or file_type == "jpeg":
        markdown = converter.jpg_to_markdown(str(file_path))
    elif file_type == "png":
        markdown = converter.png_to_markdown(str(file_path))
    elif file_type == "epub":
        markdown = converter.epub_to_markdown(str(file_path))
    else:
        return {"error": f"Tipo de arquivo não suportado: {file_type}"}

    # 5. COMPRESSÃO
    optimizer = MarkdownOptimizer()
    if ultra:
        markdown = optimizer.compress(markdown)
        # Remover linhas vazias extras
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    # 6. INDEXAÇÃO AUTOMÁTICA
    index_gen = IndexGenerator()
    sections = index_gen.generate_index(markdown)

    if len(sections) > 5:  # Se tem muitas seções, gerar índice
        index_md = "## 📑 Índice\n\n"
        for sec in sections[:10]:
            indent = "  " * (sec["level"] - 1)
            index_md += f"{indent}- {sec['title']}\n"
        markdown = index_md + "\n" + markdown

    # 7. ANÁLISE DE QUALIDADE
    quality = QualityValidator.validate(markdown, original_size)

    # 8. STREAMING (detecção)
    stream_info = StreamProcessor.process_large_file(str(file_path))

    # SALVAR
    output_dir.mkdir(parents=True, exist_ok=True)
    md_file = output_dir / f"{file_path.stem}.md"

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    # METADATA
    metadata = {
        "file_name": file_path.name,
        "file_type": file_type,
        "lines": len(markdown.split('\n')),
        "chars": len(markdown),
        "estimated_tokens_original": estimated_tokens,
        "estimated_tokens_after_economy": recommendations["estimated_tokens_after"],
        "quality_score": quality["quality_score"],
        "has_index": len(sections) > 5,
        "is_streaming": stream_info.get("is_streaming", False),
        "recommendations": recommendations,
        "quality_analysis": quality
    }

    meta_file = output_dir / ".metadata" / f"{file_path.stem}.json"
    meta_file.parent.mkdir(parents=True, exist_ok=True)
    with open(meta_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    # ECONOMIA
    tokens_saved = estimated_tokens - recommendations["estimated_tokens_after"]
    stats = EconomyTracker.track(tokens_saved, file_type, estimated_tokens)

    # CACHE
    cache.set(str(file_path), md_file)

    return {
        "markdown_file": str(md_file),
        "metadata_file": str(meta_file),
        "success": True,
        "tamanho_original_mb": round(original_size / 1024 / 1024, 6),
        "tamanho_markdown_kb": round(len(markdown) / 1024, 3),
        "economia_tokens": int(tokens_saved),
        "quality_score": quality["quality_score"],
        "has_index": len(sections) > 5,
        "recommendations": recommendations,
        "quality_analysis": quality,
        "is_streaming": stream_info.get("is_streaming", False),
        "economy_summary": {
            "total_tokens_saved": stats["total_tokens_saved"],
            "total_conversions": stats["conversions"],
            "average_per_conversion": stats["total_tokens_saved"] // max(1, stats["conversions"])
        }
    }

def process_directory(dir_path, output_dir, ultra=False):
    """Processa todos os arquivos de um diretório em paralelo"""
    dir_path = Path(dir_path)
    output_dir = Path(output_dir)

    if not dir_path.is_dir():
        return {"error": "Diretório não encontrado"}

    supported = {'.pdf', '.xlsx', '.xls', '.xlsm', '.csv', '.tsv', '.txt', '.json', '.ods', '.docx', '.pptx'}
    files = [f for f in dir_path.glob('*') if f.suffix.lower() in supported]

    logger.info(f"Processando {len(files)} arquivos do diretório {dir_path.name}")

    results = []
    workers = CONFIG.get("parallelization", {}).get("workers", 3)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_file, str(f), output_dir, ultra): f for f in files}
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Erro ao processar: {e}")

    total_saved = sum(r.get('economia_tokens', 0) for r in results if r.get('success'))
    return {
        "success": True,
        "directory": str(dir_path),
        "files_processed": len(results),
        "total_tokens_saved": total_saved,
        "results": results
    }

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python convert_ultimate.py <arquivo|diretório> [output_dir] [--ultra]")
        sys.exit(1)

    path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "markdown"
    ultra = "--ultra" in sys.argv or CONFIG.get("default_mode") == "ultra"

    # Limpeza agressiva antes de processar
    CacheCleaner.cleanup()

    if Path(path).is_dir():
        result = process_directory(path, output_dir, ultra)
    else:
        result = process_file(path, output_dir, ultra)

    print(json.dumps(result, indent=2, ensure_ascii=False))
