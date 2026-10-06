# mdmax

**Documentos em texto compacto para o Claude: menos tokens, nada descartado.**

[English](README.md) · [Benchmark](BENCHMARK.md) · [Mudanças](CHANGELOG.md)

O mdmax converte PDF, Word, Excel, PowerPoint, OpenDocument, EPUB, JSON, HTML e CSV em
Markdown/CSV compacto antes de o Claude ler, e mostra quantos tokens isso economizou.
Funciona no Claude Code, no Claude Desktop, no claude.ai e no terminal, sem configurar nada.

| Documento ([benchmark](BENCHMARK.md)) | Sem o mdmax | Com o mdmax | Economia |
|---|---:|---:|---:|
| Relatório em PDF, 12 páginas | ~28.557 | ~9.481 | 67% |
| JSON exportado de API, 300 registros | ~23.214 | ~6.743 | 71% |
| Página da web | ~4.725 | ~1.979 | 58% |
| Planilha, 500 linhas (contra tabela Markdown) | ~17.778 | ~13.669 | 23% |
| CSV exportado, 1.000 linhas | ~17.107 | ~14.844 | 13% |

De onde vem a economia, sem resumir nada:

- **PDF**: quando o Claude lê um PDF, recebe o texto *e uma imagem de cada página*. Num documento
  de texto a imagem é a maior parte do custo; o mdmax manda só o texto e tira cabeçalhos, rodapés
  e números de página repetidos. PDF escaneado ou visual (cartaz, folheto) não é convertido, porque
  nele a imagem é o conteúdo.
- **Planilhas** (xlsx, xlsm, xls, ods): um bloco CSV por aba, com os valores calculados (não as
  fórmulas), zeros mantidos, datas como `2026-10-01`, porcentagens como `12.5%` e abas ocultas
  de fora (a não ser que você peça).
- **Word, PowerPoint, OpenDocument, EPUB**: Markdown com títulos, listas, tabelas, links, título
  de cada slide e anotações do apresentador; sem formatação, número de slide ou rodapé.
- **JSON**: lista de registros vira tabela (os nomes dos campos aparecem uma vez só); o resto é compactado.
- **HTML**: texto, títulos, links e tabelas; scripts, estilos e menus saem.
- **CSV**: regravado com o separador que precisa de menos aspas, sem linhas e colunas vazias.

Toda tabela é montada em CSV e em Markdown, e fica a menor.

## Instalar

| Onde | Como |
|---|---|
| **Claude Code** | `/plugin marketplace add brnmadeira/mdmax` e depois `/plugin install mdmax@mdmax` |
| **Claude Desktop** | baixe o `mdmax.mcpb` em [Releases](https://github.com/brnmadeira/mdmax/releases) e abra |
| **claude.ai** | baixe o `mdmax-skill.zip` em [Releases](https://github.com/brnmadeira/mdmax/releases) e envie em Configurações > Recursos > Skills |
| **Terminal** | `uvx --from git+https://github.com/brnmadeira/mdmax mdmax relatorio.pdf` ou `pip install git+https://github.com/brnmadeira/mdmax` |
| **Outro cliente MCP** | comando `uvx`, argumentos `--from git+https://github.com/brnmadeira/mdmax mdmax-mcp` |

Precisa de Python 3.9 ou mais novo. O núcleo usa só a biblioteca padrão; `pypdf` (PDF) e `xlrd`
(.xls antigo) são pacotes pequenos em Python puro. O Claude Desktop instala tudo sozinho.

### Claude Code

O plugin traz três coisas:

1. **Conversão automática.** Quando o Claude usa o Read num PDF, Office, OpenDocument ou EPUB,
   o mdmax converte e o Read devolve o texto compacto, com um aviso para o Claude. Ler o mesmo
   arquivo de novo na sessão devolve o original, para quando ele precisar ver um gráfico. Arquivos
   de texto (CSV, JSON, Markdown...) nunca são trocados, para o Claude conseguir editá-los.
   As regras `deny` e `ask` das suas permissões são respeitadas: se alguma pode valer para o arquivo,
   o mdmax não mexe.
2. **A skill `mdmax`**, para CSV/JSON/HTML, para salvar um arquivo convertido e para o relatório de economia.
3. **Um servidor MCP** com `convert_document` e `token_savings` (precisa do [uv](https://docs.astral.sh/uv/)).

Na primeira sessão o plugin instala `pypdf` e `xlrd` na pasta de dados dele
(`~/.claude/plugins/data/...`), nada no sistema; `MDMAX_NO_AUTO_INSTALL=1` pula essa etapa.
Para desligar a conversão automática: `MDMAX_HOOK=off`. No Windows ela roda no Git Bash.

## No terminal

```bash
mdmax relatorio.pdf                   # grava relatorio.md e mostra a economia
mdmax convert *.xlsx -o convertidos/  # vários arquivos
mdmax convert manual.pdf --pages 1-20 --stdout
mdmax stats                           # tokens economizados até agora, por formato
mdmax doctor                          # o que está instalado
```

## Como os tokens são contados

- **Por padrão, estimados**, sem internet, em 2,2 caracteres por token. A conta foi calibrada em
  outubro de 2026 com contagens reais do tokenizador do Claude Opus 4.7 em diante (erro médio de
  cerca de 8%). Modelos mais antigos usam menos tokens; para eles o número sai um pouco alto.
  A porcentagem compara dois textos medidos do mesmo jeito e é mais confiável que o número
  absoluto. Estimativas aparecem com `~`.
- **Exatos**, pela contagem oficial da Anthropic ([`count_tokens`](https://platform.claude.com/docs/en/build-with-claude/token-counting),
  gratuita): `pip install "mdmax[exact]"`, a variável `ANTHROPIC_API_KEY` e `--exact` (ou
  `MDMAX_EXACT_TOKENS=1`). Em PDF conta o que o próprio PDF custa, imagens incluídas.
  `MDMAX_MODEL` escolhe o modelo (padrão `claude-opus-5-5`).
- O tokenizador da OpenAI (`tiktoken`) não é usado: ele conta tokens do Claude a menos.

O registro de economia (`~/.mdmax/savings.jsonl`, ou `MDMAX_HOME`) guarda só nomes de arquivo e
números, nunca o conteúdo. Tudo roda no seu computador; só o `--exact` manda texto para a API da Anthropic.

## O que o mdmax não faz

- **Imagens e páginas escaneadas**: o Claude lê imagens direto, melhor do que um OCR leria.
- **Resumos**: nada é cortado ou reescrito. Toda célula, parágrafo e slide fica.
- Gráficos dentro dos documentos não são descritos; quando importam, leia a página original.

## Desenvolvimento

```bash
pip install -e ".[test]"
pytest                               # sem arquivos de teste: tests/fixtures.py gera os documentos
python tools/benchmark.py --write    # atualiza o BENCHMARK.md
python tools/build_skill_zip.py      # dist/mdmax-skill.zip (claude.ai)
python tools/build_mcpb.py           # dist/mdmax.mcpb (Claude Desktop)
claude plugin validate .             # confere o marketplace e o plugin do Claude Code
```

Uma tag `v*` enviada ao GitHub roda os testes e anexa os dois arquivos a uma release.

## Licença

MIT, Bruno Madeira.
