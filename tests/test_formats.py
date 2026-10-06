import json

import pytest

from fixtures import make_docx, make_epub, make_ods, make_odt, make_pdf, make_pptx, make_xlsx
from mdmax import NotConvertible, convert
from mdmax.tables import render_table, trim_table


# --------------------------------------------------------------------------- spreadsheets

def test_xlsx_keeps_zeros_dates_percent_and_cached_formula_values(tmp_path):
    rows = [
        ["produto", "qtd", "preco", "total", "data", "margem", "ativo"],
        ["Whey", 0, 99.9, ("f", "B2*C2", 0), ("date", 46296), ("pct", 0.125), True],
        ["Creatina", 3, 10, ("f", "B3*C3", 30), ("date", 46296.5), ("pct", 0.3), False],
    ]
    path = make_xlsx(tmp_path / "vendas.xlsx", [("Vendas", rows, False)])
    result = convert(path)
    lines = result.text.splitlines()
    assert "produto,qtd,preco,total,data,margem,ativo" in lines
    assert "Whey,0,99.9,0,2026-10-01,12.5%,TRUE" in lines
    assert "Creatina,3,10,30,2026-10-01 12:00,30%,FALSE" in lines
    assert result.baseline_kind == "markdown-table"
    assert result.saved > 0


def test_xlsx_formula_without_saved_value_is_shown_and_reported(tmp_path):
    path = make_xlsx(tmp_path / "f.xlsx", [("S", [["a", "b"], [2, ("f", "A2*2", None)]], False)])
    result = convert(path)
    assert "2,=A2*2" in result.text
    assert any("formula" in w for w in result.warnings)


def test_xlsx_skips_hidden_sheets_unless_asked(tmp_path):
    path = make_xlsx(tmp_path / "h.xlsx", [("Visible", [["x"], [1]], False), ("Secret", [["y"], [2]], True)])
    assert "Secret" not in convert(path).text
    assert any("hidden" in w for w in convert(path).warnings)
    assert "## Sheet: Secret" in convert(path, include_hidden=True).text


def test_xlsx_keeps_duplicate_rows(tmp_path):
    rows = [["id", "v"]] + [[1, "same"]] * 4
    path = make_xlsx(tmp_path / "d.xlsx", [("S", rows, False)])
    assert convert(path).text.count("1,same") == 4


def test_ods_ignores_repeated_empty_padding(tmp_path):
    path = make_ods(tmp_path / "p.ods", [("Plan1", [["nome", "valor"], ["A", 0], ["B", 2.5]])])
    result = convert(path)
    assert "nome,valor\nA,0\nB,2.5" in result.text
    assert len(result.text) < 200  # the 1,048,000 padded rows were not expanded


# --------------------------------------------------------------------------- documents

def test_docx_headings_lists_tables_links(tmp_path):
    path = make_docx(tmp_path / "r.docx", [
        ("h", 1, "Relatório Mensal"),
        ("p", "Vendas cresceram em outubro."),
        ("li", "Primeiro ponto"),
        ("li", "Segundo ponto"),
        ("table", [["Loja", "Total"], ["Centro", "1.200"], ["Barra", "980"]]),
        ("link", "site da Way", "https://example.com/way"),
    ])
    text = convert(path).text
    assert "# Relatório Mensal" in text  # localized style id, English style name
    assert "- Primeiro ponto\n- Segundo ponto" in text
    assert "Loja,Total" in text and "Centro,1.200" in text
    assert "[site da Way](https://example.com/way)" in text


def test_pptx_titles_tables_notes_without_footer_noise(tmp_path):
    path = make_pptx(tmp_path / "d.pptx", [
        {"title": "Resultados", "lines": ["Meta batida"], "notes": "Falar do Q4", "footer": "Confidencial"},
        {"title": "Lojas", "lines": [], "table": [["Loja", "Meta"], ["Centro", "100%"]], "footer": "Confidencial"},
    ])
    result = convert(path)
    assert "## Slide 1: Resultados\nMeta batida\nNotes: Falar do Q4" in result.text
    assert "Loja,Meta" in result.text
    assert "Confidencial" not in result.text
    assert result.pages == 2


def test_odt_and_epub(tmp_path):
    odt = make_odt(tmp_path / "t.odt", [("h", 2, "Seção"), ("p", "Texto"), ("li", "Item")])
    assert "## Seção\n\nTexto\n\n- Item" in convert(odt).text
    epub = make_epub(tmp_path / "b.epub", "Livro", [
        "<h1>Capítulo 1</h1><p>Era uma vez.</p><script>x()</script>",
        "<h1>Capítulo 2</h1><ul><li>um</li><li>dois</li></ul>",
    ])
    text = convert(epub).text
    assert "Title: Livro" in text
    assert text.index("Capítulo 1") < text.index("Capítulo 2")
    assert "- um\n\n- dois" in text or "- um\n- dois" in text
    assert "x()" not in text and "color" not in text


# --------------------------------------------------------------------------- PDF

def _report_pages(n):
    return [
        ["ACME Suplementos - Relatório interno", f"Seção {i}: vendas da semana {i}.",
         "Texto do corpo com informação única " + str(i) * 3, f"Página {i} de {n}"]
        for i in range(1, n + 1)
    ]


def test_pdf_removes_running_headers_and_page_numbers(tmp_path):
    path = make_pdf(tmp_path / "rel.pdf", _report_pages(5))
    result = convert(path)
    assert result.text.count("ACME Suplementos") == 0
    assert "Página 3 de 5" not in result.text
    assert "Seção 3: vendas da semana 3." in result.text
    assert result.pages == 5
    assert result.baseline_kind == "pdf-direct-estimate"
    assert result.saved_pct > 50  # page images dominate the cost of reading a PDF directly


def test_pdf_page_range_and_empty_page(tmp_path):
    pages = _report_pages(4)
    pages[1] = []
    path = make_pdf(tmp_path / "r.pdf", pages)
    result = convert(path, pages="2-3")
    assert result.pages == 2
    assert "no text on this page" in result.text
    assert "Seção 3" in result.text and "Seção 1" not in result.text


def test_scanned_pdf_is_not_converted(tmp_path):
    path = make_pdf(tmp_path / "scan.pdf", [[], [], []])
    with pytest.raises(NotConvertible):
        convert(path)


# --------------------------------------------------------------------------- text formats

def test_csv_with_semicolons_and_brazilian_decimals_round_trips(tmp_path):
    path = tmp_path / "v.csv"
    path.write_text("produto;preco;estoque\nWhey;99,90;0\nBarra;5,50;12\n;;\n", encoding="cp1252")
    text = convert(path).text
    assert "Whey;99,90;0" in text  # the delimiter that needs no quotes is kept
    assert ";;" not in text  # empty row dropped


def test_json_records_become_a_table_and_nested_json_is_compacted(tmp_path):
    records = tmp_path / "lojas.json"
    records.write_text(json.dumps([{"id": i, "nome": f"Loja {i}", "ativa": True} for i in range(20)], indent=2))
    result = convert(records)
    assert "id,nome,ativa" in result.text and "7,Loja 7,true" in result.text
    assert result.saved_pct > 40
    nested = tmp_path / "cfg.json"
    nested.write_text(json.dumps({"a": {"b": [1, 2, {"c": None}]}}, indent=4))
    assert '{"a":{"b":[1,2,{"c":null}]}}' in convert(nested).text


def test_html_drops_scripts_and_keeps_structure(tmp_path):
    path = tmp_path / "p.html"
    path.write_text(
        "<html><head><title>T</title><script>var x=1</script><style>a{}</style></head><body>"
        "<h2>Preços</h2><p>Texto <a href='https://ex.com/a'>link</a></p>"
        "<table><tr><th>a</th><th>b</th></tr><tr><td>1</td><td>2</td></tr></table></body></html>",
        encoding="utf-8",
    )
    text = convert(path).text
    assert "## Preços" in text and "[link](https://ex.com/a)" in text and "a,b\n1,2" in text
    assert "var x" not in text


def test_unsupported_and_missing_files(tmp_path):
    with pytest.raises(NotConvertible):
        convert(tmp_path / "x.bmp")
    with pytest.raises(FileNotFoundError):
        convert(tmp_path / "nope.pdf")


# --------------------------------------------------------------------------- tables

def test_auto_table_picks_the_shorter_rendering():
    rows = [["a", "b"], ["1", "2"]]
    assert render_table(rows).startswith("```csv")
    assert render_table(rows, "markdown").startswith("| a | b |")
    assert render_table([["x|y", "z"], ["1", "2"]], "markdown").startswith("| x\\|y |")


def test_trim_table_removes_empty_edges_but_not_inner_cells():
    assert trim_table([["a", "", "", ""], ["", "b", "", ""], ["", "", "", ""]]) == [["a", ""], ["", "b"]]
