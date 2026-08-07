# /mdmax - File Converter Skill

Use este comando para converter arquivos com MdMax:

```bash
mdmax convert document.pdf
mdmax convert spreadsheet.xlsx
mdmax stats
mdmax dashboard
mdmax config --show
```

## Como usar:

1. **Instale MdMax primeiro:**
   ```bash
   pip install mdmax
   ```

2. **Converta um arquivo:**
   ```bash
   mdmax convert ~/Downloads/document.pdf
   ```

3. **Veja estatísticas:**
   ```bash
   mdmax stats
   ```

4. **Mostre o dashboard:**
   ```bash
   mdmax dashboard
   ```

## Formatos suportados (16):

- **PDF, DOCX, PPTX** - Documentos
- **XLSX, XLS, XLSM, CSV, TSV, ODS** - Planilhas
- **JSON, TXT** - Dados
- **PNG, JPG, JPEG, SVG** - Imagens
- **EPUB** - E-books

## Economia típica:

- PDF (50MB) → 90% economia
- Excel → 70% economia
- Word → 75% economia
- Imagens → 70% economia

## Exemplos:

```bash
# Converter PDF
mdmax convert relatorio.pdf -o relatorio.md

# Converter tudo em uma pasta
mdmax convert *.xlsx

# Ver economia total
mdmax stats

# Exportar dados
mdmax stats --export json
```
