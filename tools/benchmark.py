"""Measures mdmax on a reproducible set of documents and writes BENCHMARK.md.

    python tools/benchmark.py            # built-in corpus, prints the table
    python tools/benchmark.py --write    # ... and updates BENCHMARK.md
    python tools/benchmark.py a.pdf b.xlsx   # your own files (nothing is written)
    add --exact to count with the Anthropic API (needs mdmax[exact] and an API key)

The corpus is generated (see tests/fixtures.py), so anyone gets the same numbers.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from fixtures import make_docx, make_epub, make_pdf, make_pptx, make_xlsx  # noqa: E402
from mdmax import __version__, convert  # noqa: E402
from mdmax.convert import BASELINE_LABELS  # noqa: E402
from mdmax.tokens import CHARS_PER_TOKEN, PDF_IMAGE_TOKENS_PER_PAGE  # noqa: E402

WORDS = (
    "a rede de lojas registrou crescimento nas vendas de suplementos proteicos durante o trimestre "
    "com destaque para whey creatina e vitaminas enquanto o estoque das filiais foi ajustado para "
    "atender a demanda dos clientes que buscam produtos naturais e preços competitivos no varejo "
    "regional sendo necessário revisar metas prazos fornecedores e campanhas de marketing digital"
).split()


def prose(rng: random.Random, sentences: int) -> str:
    out = []
    for _ in range(sentences):
        words = [rng.choice(WORDS) for _ in range(rng.randint(12, 24))]
        out.append(" ".join(words).capitalize() + ".")
    return " ".join(out)


def wrap(text: str, width: int = 95):
    line, lines = "", []
    for word in text.split():
        if len(line) + len(word) + 1 > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + ([line] if line else [])


def build_corpus(folder: Path):
    rng = random.Random(42)
    files = []
    pages = []
    for n in range(1, 13):
        lines = ["Way Suplementos - Relatório trimestral 3T26", ""]
        lines += wrap(prose(rng, 14))
        lines += ["", f"Página {n} de 12"]
        pages.append(lines)
    files.append(("Report, 12 text pages", make_pdf(folder / "relatorio.pdf", pages)))

    header = ["data", "filial", "produto", "categoria", "quantidade", "preco", "desconto", "total"]
    rows = [header]
    for i in range(500):
        qty = rng.randint(0, 40)
        price = round(rng.uniform(19, 249), 2)
        rows.append([("date", 46204 + i % 90), f"Loja {rng.randint(1, 21):02d}", f"Produto {rng.randint(1, 120)}",
                     rng.choice(["proteína", "vitaminas", "naturais", "acessórios"]), qty, price,
                     ("pct", rng.choice([0, 0.05, 0.1])), round(qty * price, 2)])
    files.append(("Spreadsheet, 500 rows x 8 columns", make_xlsx(folder / "vendas.xlsx", [("Vendas", rows, False)])))

    blocks = [("h", 1, "Proposta comercial 2027")]
    for s in range(6):
        blocks.append(("h", 2, f"Seção {s + 1}"))
        blocks.append(("p", prose(rng, 6)))
        blocks.append(("li", prose(rng, 1)))
        blocks.append(("li", prose(rng, 1)))
    blocks.append(("table", [["Produto", "Preço", "Prazo"]] + [[f"Produto {i}", f"{rng.uniform(20, 200):.2f}", f"{rng.choice([30, 60, 90])} dias"] for i in range(40)]))
    files.append(("Word document with a 40-row table", make_docx(folder / "proposta.docx", blocks)))

    slides = [{"title": f"Tema {i}", "lines": wrap(prose(rng, 2), 60), "notes": prose(rng, 2),
               "footer": "Confidencial - Way Suplementos"} for i in range(1, 16)]
    slides[7]["table"] = [["Loja", "Meta", "Real"]] + [[f"Loja {i}", "100%", f"{rng.randint(80, 120)}%"] for i in range(10)]
    files.append(("Slide deck, 15 slides with notes", make_pptx(folder / "apresentacao.pptx", slides)))

    products = [{"id": i, "sku": f"WAY-{1000 + i}", "nome": f"Produto {i}", "categoria": rng.choice(["proteína", "vitaminas"]),
                 "preco": round(rng.uniform(10, 300), 2), "estoque": rng.randint(0, 500), "ativo": rng.random() > 0.1}
                for i in range(300)]
    path = folder / "produtos.json"
    path.write_text(json.dumps(products, indent=2, ensure_ascii=False), encoding="utf-8")
    files.append(("JSON API export, 300 records (indented)", path))

    article = "".join(f"<h2>Parte {i}</h2><p>{prose(rng, 5)}</p>" for i in range(1, 7))
    table = "<table><tr><th>Item</th><th>Valor</th></tr>" + "".join(
        f"<tr><td>Item {i}</td><td>{rng.randint(1, 999)}</td></tr>" for i in range(30)) + "</table>"
    html = (
        "<!doctype html><html><head><title>Blog</title><style>" + "body{margin:0;padding:0;font:16px sans-serif}" * 40
        + "</style><script>" + "window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}" * 30
        + "</script></head><body><nav><ul>" + "".join(f'<li><a href="/c/{i}" class="nav-link">Menu {i}</a></li>' for i in range(20))
        + f'</ul></nav><main><article class="post">{article}{table}</article></main>'
        + '<footer><div class="f">© Way</div></footer></body></html>'
    )
    path = folder / "pagina.html"
    path.write_text(html, encoding="utf-8")
    files.append(("Web page with scripts and styles", path))

    csv_rows = ["codigo;cliente;cidade;valor;;;;"] + [
        f"{i};Cliente {i};{rng.choice(['Rio de Janeiro', 'Niterói', 'Maricá'])};{rng.uniform(10, 900):.2f}".replace(".", ",") + ";;;;"
        for i in range(1000)]
    path = folder / "clientes.csv"
    path.write_text("\n".join(csv_rows) + "\n", encoding="utf-8")
    files.append(("CSV export, 1,000 rows (empty trailing columns)", path))

    chapters = [f"<h1>Capítulo {i}</h1>" + "".join(f"<p>{prose(rng, 4)}</p>" for _ in range(8)) for i in range(1, 6)]
    files.append(("E-book, 5 chapters", make_epub(folder / "livro.epub", "Guia de suplementação", chapters)))
    return files


def measure(files, exact: bool):
    rows = []
    for label, path in files:
        start = time.perf_counter()
        result = convert(path, exact=exact)
        rows.append({
            "label": label, "file": Path(path).name, "tokens": result.tokens, "baseline": result.baseline_tokens,
            "kind": result.baseline_kind, "pct": result.saved_pct, "method": result.method,
            "ms": (time.perf_counter() - start) * 1000,
        })
    return rows


def table(rows) -> str:
    out = ["| Document | Without mdmax | With mdmax | Saved | Compared with |", "|---|---:|---:|---:|---|"]
    for r in rows:
        approx = "~" if r["method"] == "estimated" else ""
        base = f"{approx}{r['baseline']:,}" if r["baseline"] is not None else "-"
        pct = f"{r['pct']:.0f}%" if r["pct"] is not None else "-"
        out.append(f"| {r['label']} (`{r['file']}`) | {base} | {approx}{r['tokens']:,} | {pct} | {BASELINE_LABELS.get(r['kind'], r['kind'])} |")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--exact", action="store_true")
    args = parser.parse_args()
    if args.files:
        rows = measure([(Path(f).name, Path(f)) for f in args.files], args.exact)
        print(table(rows))
        return
    with tempfile.TemporaryDirectory() as tmp:
        rows = measure(build_corpus(Path(tmp)), args.exact)
    text = table(rows)
    print(text)
    if args.write:
        method = "counted with the Anthropic `count_tokens` API" if args.exact else (
            f"estimated at {CHARS_PER_TOKEN} characters per token (calibrated on the tokenizer of Claude Opus 4.7 and later, "
            "mean error about 8%; older models produce fewer tokens)")
        doc = f"""# Benchmark

mdmax {__version__}, generated by `python tools/benchmark.py --write` on {time.strftime('%Y-%m-%d')}.
The documents are synthetic and reproducible (built by `tests/fixtures.py`), in Portuguese,
like the documents mdmax was made for. Run the script on your own files to see your numbers:
`python tools/benchmark.py file1.pdf file2.xlsx`.

{text}

## How to read it

- **Tokens** are {method}. The percentage compares two texts measured the same way, so it is
  more reliable than the absolute numbers.
- **PDF** is compared with what Claude spends when it reads the PDF itself: the text plus one image
  of every page, estimated at {PDF_IMAGE_TOKENS_PER_PAGE:,} tokens per page (the cap of the standard
  image tier; models from Claude 4.7 on can use up to 4,784). Most of the saving is that image.
  mdmax does not convert scanned or mostly visual PDFs, where the image *is* the content.
- **Spreadsheets** are compared with a plain Markdown table, which is what most converters produce.
  Claude cannot read .xlsx directly.
- **Word, PowerPoint and e-books** have no comparison point: Claude cannot read them directly,
  so only the size of the result is shown in the log.
- **CSV, JSON, HTML** are compared with the original file, which Claude can read as is.
- Nothing is summarized or dropped: every cell, paragraph and slide is kept. What goes is
  formatting, repeated headers and footers, JSON indentation and repeated keys, markup,
  scripts and styles, and empty rows and columns.
"""
        (ROOT / "BENCHMARK.md").write_text(doc, encoding="utf-8")
        print("\nBENCHMARK.md written")


if __name__ == "__main__":
    main()
