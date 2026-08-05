#!/usr/bin/env python3
"""
Auto-Convert to Markdown - OTIMIZADO
Implementa: Cache, Metadata Minimalista, Smart Truncation, Compressão, Processamento Paralelo
"""

import sys
import os
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Tuple
from queue import Queue
from threading import Thread
import time

try:
    import pdfplumber
    import pandas as pd
except ImportError:
    pdfplumber = None
    pd = None


class CacheManager:
    """Gerencia cache de conversões"""
    def __init__(self, cache_dir: Path):
        self.cache_file = cache_dir / "cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def get_file_hash(self, filepath: str) -> str:
        """Calcular MD5 do arquivo"""
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            md5.update(f.read())
        return md5.hexdigest()

    def is_cached(self, filepath: str) -> bool:
        """Verificar se arquivo já foi convertido"""
        file_hash = self.get_file_hash(filepath)
        filename = Path(filepath).stem

        if filename in self.cache:
            cached_hash = self.cache[filename].get('hash')
            return cached_hash == file_hash
        return False

    def get_cached_path(self, filepath: str) -> Optional[str]:
        """Retornar caminho do Markdown em cache"""
        filename = Path(filepath).stem
        if filename in self.cache:
            return self.cache[filename].get('markdown')
        return None

    def save_to_cache(self, filepath: str, md_path: str, tokens_saved: int):
        """Salvar info de conversão no cache"""
        file_hash = self.get_file_hash(filepath)
        filename = Path(filepath).stem

        self.cache[filename] = {
            'hash': file_hash,
            'markdown': str(md_path),
            'economia_tokens': tokens_saved,
            'data': datetime.now().isoformat()
        }

        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2)


class MarkdownOptimizer:
    """Otimiza Markdown gerado"""

    @staticmethod
    def compress(content: str) -> str:
        """Comprimir Markdown removendo espaços desnecessários"""
        # Remover múltiplas linhas vazias
        content = re.sub(r'\n\n\n+', '\n\n', content)

        # Remover espaços extras no fim das linhas
        lines = [line.rstrip() for line in content.split('\n')]
        content = '\n'.join(lines)

        # Remover espaços extras em tabelas
        content = re.sub(r'\|\s+', '| ', content)
        content = re.sub(r'\s+\|', ' |', content)

        return content.strip()

    @staticmethod
    def create_minimal_header(filename: str, rows: int, cols: int) -> str:
        """Header minimalista"""
        return f"# {filename} | {rows} linhas | {cols} colunas\n\n"


class SmartTruncator:
    """Detecta e trunca arquivos grandes"""

    @staticmethod
    def should_truncate(file_size_mb: float, file_type: str, row_count: int = None) -> Tuple[bool, str]:
        """Decidir se deve truncar"""
        if file_type == 'pdf' and file_size_mb > 5:
            return True, f"PDF grande ({file_size_mb:.1f}MB) - resumido"

        if file_type in ['xlsx', 'csv'] and row_count and row_count > 10000:
            return True, f"Tabela grande ({row_count} linhas) - amostra"

        if file_size_mb > 20:
            return True, f"Arquivo grande ({file_size_mb:.1f}MB) - comprimido"

        return False, ""

    @staticmethod
    def truncate_dataframe(df: pd.DataFrame, max_rows: int = 1000) -> Tuple[pd.DataFrame, str]:
        """Truncar dataframe grande"""
        if len(df) > max_rows:
            sample_df = df.sample(min(max_rows, len(df)))
            msg = f"⚠️ Amostra de {max_rows} de {len(df)} linhas\n\n"
            return sample_df, msg
        return df, ""

    @staticmethod
    def truncate_pdf_pages(content: str, max_pages: int = 20) -> Tuple[str, str]:
        """Extrair primeiras N páginas"""
        pages = content.split('## Page ')
        if len(pages) > max_pages:
            truncated = 'Content antes da última página'.join(pages[:max_pages+1])
            msg = f"⚠️ PDF resumido (primeiras {max_pages} de {len(pages)-1} páginas)\n\n"
            return truncated, msg
        return content, ""


class ConversionQueue:
    """Fila de processamento paralelo"""
    def __init__(self, num_workers: int = 3):
        self.queue = Queue()
        self.results = {}
        self.workers = []

        for i in range(num_workers):
            worker = Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)

    def _worker(self):
        """Worker thread para processar conversões"""
        while True:
            task = self.queue.get()
            if task is None:
                break

            filepath, output_dir = task
            try:
                result = MarkdownConverter(filepath, output_dir).convert()
                self.results[filepath] = result
            except Exception as e:
                self.results[filepath] = {'error': str(e)}

            self.queue.task_done()

    def add_task(self, filepath: str, output_dir: str):
        """Adicionar tarefa à fila"""
        self.queue.put((filepath, output_dir))

    def wait_all(self):
        """Aguardar todas as tarefas"""
        self.queue.join()


class MarkdownConverter:
    """Conversor principal com otimizações"""

    def __init__(self, input_file: str, output_dir: str = "markdown", debug: bool = False):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir = self.output_dir / ".metadata"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.cache = CacheManager(self.metadata_dir)
        self.debug = debug
        self.file_size = self.input_file.stat().st_size / 1_000_000  # MB
        self.file_type = self._detect_file_type()
        self.start_time = time.time()

    def _detect_file_type(self) -> str:
        ext = self.input_file.suffix.lower()
        if ext == ".pdf":
            return "pdf"
        elif ext in [".xlsx", ".xls"]:
            return "excel"
        elif ext == ".csv":
            return "csv"
        elif ext == ".ods":
            return "ods"
        else:
            raise ValueError(f"Formato não suportado: {ext}")

    def convert(self) -> Dict:
        """Converter arquivo com otimizações"""

        # 1. VERIFICAR CACHE
        if self.cache.is_cached(str(self.input_file)):
            cached_path = self.cache.get_cached_path(str(self.input_file))
            return {
                "markdown_file": cached_path,
                "success": True,
                "source": "cache",
                "economia_tokens": self.cache.cache[self.input_file.stem]['economia_tokens']
            }

        # 2. DETECTAR TRUNCAÇÃO
        should_truncate, truncate_msg = SmartTruncator.should_truncate(
            self.file_size, self.file_type
        )

        # 3. CONVERTER
        if self.file_type == "pdf":
            content, metadata, warning = self._convert_pdf(should_truncate)
        elif self.file_type == "excel":
            content, metadata, warning = self._convert_excel(should_truncate)
        elif self.file_type == "csv":
            content, metadata, warning = self._convert_csv(should_truncate)
        else:
            content, metadata, warning = self._convert_ods(should_truncate)

        # 4. OTIMIZAR MARKDOWN
        content = MarkdownOptimizer.compress(content)

        # 5. SALVAR COM METADATA MINIMALISTA
        resultado = self._save_optimized(content, metadata, warning)

        # 6. GUARDAR EM CACHE
        if resultado['success']:
            economia = self._estimate_tokens(content)
            self.cache.save_to_cache(str(self.input_file), resultado['markdown_file'], economia)
            resultado['economia_tokens'] = economia
            resultado['tempo_ms'] = int((time.time() - self.start_time) * 1000)

        return resultado

    def _convert_pdf(self, truncate: bool) -> Tuple[str, Dict, str]:
        """Converter PDF com smart truncation"""
        if pdfplumber is None:
            raise ImportError("pdfplumber não instalado")

        content = []
        warning = ""
        page_count = 0
        table_count = 0

        try:
            with pdfplumber.open(self.input_file) as pdf:
                page_count = len(pdf.pages)
                max_pages = 20 if truncate else page_count

                if truncate and page_count > max_pages:
                    warning = f"⚠️ PDF grande: primeiras {max_pages} de {page_count} páginas\n\n"

                for page_num, page in enumerate(pdf.pages[:max_pages], 1):
                    text = page.extract_text()
                    if text and text.strip():
                        content.append(f"## Página {page_num}\n\n{text}")

                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            content.append(self._table_to_markdown(table))
                            table_count += 1

        except Exception as e:
            raise RuntimeError(f"Erro PDF: {str(e)}")

        return "\n\n".join(content), {
            "pages": page_count,
            "tables": table_count,
            "format": "PDF",
            "truncated": truncate
        }, warning

    def _convert_excel(self, truncate: bool) -> Tuple[str, Dict, str]:
        """Converter Excel com smart truncation"""
        if pd is None:
            raise ImportError("pandas não instalado")

        content = []
        warning = ""
        sheet_count = 0
        total_rows = 0

        try:
            xls = pd.ExcelFile(self.input_file)
            sheet_count = len(xls.sheet_names)
            sheet_names = xls.sheet_names[:5] if truncate and sheet_count > 5 else xls.sheet_names

            if truncate and sheet_count > 5:
                warning = f"⚠️ {sheet_count} abas - mostrando primeiras 5\n\n"

            for sheet_name in sheet_names:
                df = pd.read_excel(self.input_file, sheet_name=sheet_name)

                if df.empty:
                    continue

                # Smart truncation de linhas
                if truncate and len(df) > 1000:
                    df, truncate_msg = SmartTruncator.truncate_dataframe(df, max_rows=1000)
                    warning += truncate_msg

                content.append(f"## {sheet_name}\n\n")
                content.append(f"*{len(df)} × {len(df.columns)}*\n\n")

                md_table = df.to_markdown(index=False)
                if md_table:
                    content.append(md_table)

                total_rows += len(df)

        except Exception as e:
            raise RuntimeError(f"Erro Excel: {str(e)}")

        return "\n\n".join(content), {
            "sheets": sheet_count,
            "rows": total_rows,
            "format": "Excel",
            "truncated": truncate
        }, warning

    def _convert_csv(self, truncate: bool) -> Tuple[str, Dict, str]:
        """Converter CSV com smart truncation"""
        if pd is None:
            raise ImportError("pandas não instalado")

        warning = ""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None

        for encoding in encodings:
            try:
                df = pd.read_csv(self.input_file, encoding=encoding)
                break
            except:
                continue

        if df is None:
            raise RuntimeError("Não conseguiu ler CSV")

        # Smart truncation
        if truncate and len(df) > 1000:
            df, truncate_msg = SmartTruncator.truncate_dataframe(df, max_rows=1000)
            warning = truncate_msg

        markdown_table = df.to_markdown(index=False)

        return markdown_table or "", {
            "rows": len(df),
            "columns": len(df.columns),
            "format": "CSV",
            "truncated": truncate
        }, warning

    def _convert_ods(self, truncate: bool) -> Tuple[str, Dict, str]:
        """Converter ODS (mesma lógica Excel)"""
        if pd is None:
            raise ImportError("pandas não instalado")

        content = []
        warning = ""
        sheet_count = 0
        total_rows = 0

        try:
            xls = pd.ExcelFile(self.input_file, engine="odf")
            sheet_count = len(xls.sheet_names)

            for sheet_name in xls.sheet_names[:100]:
                df = pd.read_excel(self.input_file, sheet_name=sheet_name, engine="odf")

                if df.empty:
                    continue

                if truncate and len(df) > 1000:
                    df, truncate_msg = SmartTruncator.truncate_dataframe(df)
                    warning += truncate_msg

                content.append(f"## {sheet_name}\n\n")
                markdown_table = df.to_markdown(index=False)
                if markdown_table:
                    content.append(markdown_table)

                total_rows += len(df)

        except Exception as e:
            raise RuntimeError(f"Erro ODS: {str(e)}")

        return "\n\n".join(content), {
            "sheets": sheet_count,
            "rows": total_rows,
            "format": "ODS",
            "truncated": truncate
        }, warning

    def _table_to_markdown(self, table):
        """Converter tabela para Markdown"""
        if not table:
            return ""

        cols = max(len(row) for row in table) if table else 0
        rows = []
        rows.append("| " + " | ".join(str(cell or "") for cell in table[0][:cols]) + " |")
        rows.append("|" + "|".join(["---"] * cols) + "|")

        for row in table[1:]:
            cells = [str(cell or "") for cell in row[:cols]]
            rows.append("| " + " | ".join(cells) + " |")

        return "\n".join(rows)

    def _save_optimized(self, content: str, metadata: Dict, warning: str) -> Dict:
        """Salvar com header minimalista"""
        # Header MINIMALISTA
        header = MarkdownOptimizer.create_minimal_header(
            self.input_file.name,
            metadata.get('rows', metadata.get('pages', 0)),
            metadata.get('columns', metadata.get('sheets', metadata.get('tables', 0)))
        )

        if warning:
            header += warning

        full_content = header + content

        # Salvar
        output_file = self.output_dir / f"{self.input_file.stem}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_content)

        # Metadata JSON minimalista
        metadata_file = self.metadata_dir / f"{self.input_file.stem}.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return {
            "markdown_file": str(output_file),
            "metadata_file": str(metadata_file),
            "success": True,
            "tamanho_original_mb": self.file_size,
            "tamanho_markdown_kb": len(full_content) / 1000,
            "warning": warning if warning else None
        }

    def _estimate_tokens(self, content: str) -> int:
        """Estimar tokens economizados"""
        return int(len(content.split()) * 1.3)  # Aproximado

    def _table_to_markdown(self, table):
        if not table:
            return ""
        cols = max((len(row) for row in table), default=0)
        if cols == 0:
            return ""

        rows = []
        rows.append("| " + " | ".join(str(cell or "") for cell in table[0][:cols]) + " |")
        rows.append("|" + "|".join(["---"] * cols) + "|")

        for row in table[1:]:
            cells = [str(cell or "") for cell in row[:cols]]
            rows.append("| " + " | ".join(cells) + " |")

        return "\n".join(rows)


def main():
    if len(sys.argv) < 2:
        print("Uso: python convert_optimized.py <arquivo> [output_dir] [--debug]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "markdown"
    debug = "--debug" in sys.argv

    try:
        converter = MarkdownConverter(input_file, output_dir, debug=debug)
        result = converter.convert()

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
