---
name: canal-verde-research
description: >-
  Processo repetível para levantar lojas de canal verde (varejo de produtos
  naturais/suplementos/wellness) e empresas fabricantes de suplementos por
  estado brasileiro, e transformar isso em dados prontos para o mapa do app
  canal-verde-map. Use sempre que o usuário pedir para adicionar um novo
  estado ao mapa, atualizar dados de um estado já existente, ou perguntar
  como o levantamento de dados foi feito.
---

# Canal Verde Research

Processo usado para popular `canal-verde-map/src/data/<sigla>.json` a partir de
fontes oficiais + enriquecimento na web. Já rodado para RJ; repita para cada
novo estado.

## Por que esse processo (contexto importante)

- O servidor oficial da Receita Federal (`dadosabertos.rfb.gov.br`) não é
  acessível a partir do ambiente do Claude Code (timeout de conexão — provável
  bloqueio de IP de datacenter). Não tente baixar os arquivos brutos direto.
- O agregador "Casa dos Dados" bloqueia acesso automatizado com desafio
  anti-bot da Cloudflare. Não tente contornar isso.
- A fonte que funciona: **Base dos Dados** (basedosdados.org), que espelha a
  base completa de CNPJ da Receita Federal no Google BigQuery, com consulta
  gratuita (BigQuery Sandbox, sem cartão). Só que isso exige o usuário rodar a
  query com a própria conta Google — o agente não consegue autenticar nisso
  sozinho. **Sempre peça para o usuário rodar a query e exportar o CSV.**
- **cnpj.biz** — também bloqueado por desafio anti-bot da Cloudflare (403).
  Não tente.
- **listasdeempresa.com** — responde normalmente, mas é serviço pago (exporta
  lista só após pagamento via PagBank/boleto/Pix/cartão); não tem busca ou
  exportação gratuita. Não é utilizável sem custo.
- **Portais tipo `rj.gov.br/servico/emitir-comprovante-de-inscricao-e-situacao-cadastral...`**
  (JUCERJA/SEFAZ-RJ) — são consulta de **um CNPJ específico já conhecido**
  (emite certidão dele), não busca por segmento/cidade. Só serve pra conferir
  status de uma empresa que você já identificou por outra via, não pra
  descoberta de novas.

## Passo 1 — CNAEs relevantes (já verificados)

- `4729699` (4729-6/99) — Comércio varejista de produtos alimentícios em
  geral/especializado, inclui produtos naturais e dietéticos → **lojas de
  canal verde**
- `4637199` (4637-1/99) — Comércio atacadista de complementos e suplementos
  alimentícios → distribuidoras/atacado
- `1099607` (1099-6/07) — Fabricação de alimentos dietéticos e complementos
  alimentares → **empresas/fabricantes de suplementos**

## Passo 2 — Query SQL para o usuário rodar no BigQuery

Trocar `"RJ"` pela sigla do novo estado. Tabelas confirmadas via exemplo real:
`basedosdados.br_me_cnpj.estabelecimentos` (alias `est`, contém `cnpj_basico`,
`cnpj`, `sigla_uf`, `cnae_fiscal_principal`, `situacao_cadastral` — "2" =
ativa —, endereço, `nome_fantasia`) e `basedosdados.br_me_cnpj.empresas`
(alias `emp`, contém `cnpj_basico`, `razao_social`).

```sql
SELECT DISTINCT
  est.cnpj,
  emp.razao_social,
  est.nome_fantasia,
  est.cnae_fiscal_principal,
  est.logradouro,
  est.numero,
  est.complemento,
  est.bairro,
  est.cep,
  est.municipio,
  est.sigla_uf,
  est.ddd1,
  est.telefone1,
  est.email,
  est.situacao_cadastral
FROM `basedosdados.br_me_cnpj.estabelecimentos` AS est
JOIN `basedosdados.br_me_cnpj.empresas` AS emp
  ON est.cnpj_basico = emp.cnpj_basico
WHERE
  est.sigla_uf = "RJ"
  AND est.situacao_cadastral = "2"
  AND est.cnae_fiscal_principal IN ("4729699", "4637199", "1099607")
ORDER BY est.cnae_fiscal_principal, emp.razao_social
```

Instrua o usuário: console.cloud.google.com/bigquery (login Google, projeto
sandbox grátis), colar a query, rodar, "Save Results" → CSV, enviar o arquivo.

Se algum nome de coluna der erro (schema pode mudar), peça pro usuário rodar
`SELECT * FROM \`basedosdados.br_me_cnpj.estabelecimentos\` LIMIT 5` e ajuste
a query com os nomes reais antes de repetir.

## Passo 3 — Enriquecimento (site + Instagram)

Para o volume pequeno (~100 registros da busca por cidade), use o subagent
`canal-verde-enricher` (`.claude/agents/canal-verde-enricher.md`) passando a
lista de nome + endereço. Ele devolve site/instagram por empresa, ou `null`
quando não encontrar — nunca inventar dado.

**Não tente enriquecer (site/Instagram) o CSV inteiro do CNPJ aberto** — no RJ
isso já passou de 50 mil linhas; buscar site/instagram um por um não é viável
nessa escala. A camada de CNPJ aberto fica só com nome/endereço/telefone/email
(campos que já vêm no próprio CSV); site/instagram ficam `null` nela.

## Passo 4 — Geocodificação

O volume real do CNPJ aberto é grande (dezenas de milhares de linhas por
estado) — geocodificar endereço por endereço no Nominatim (1 req/s) é
inviável nessa escala (levaria horas). Em vez disso:

1. Extraia as cidades únicas do CSV (`municipio`).
2. Geocodifique só essas cidades (poucas dezenas por estado) via Nominatim —
   rápido, minutos.
3. Atribua a cada registro do CNPJ aberto o centro da sua cidade + um jitter
   aleatório pequeno (~400m) pra não empilhar tudo num único pixel.
4. Use `scripts/geocode-cidades.mjs` (cidades) e `scripts/geocode.mjs`
   (endereços completos, só pra volume pequeno tipo a camada de busca web).

Isso dá precisão de cidade, não de endereço exato — aceitável pro volume
grande; é a troca que viabiliza mostrar a cobertura oficial completa.

**Cuidado com duplicação no JOIN com `municipio`**: o LEFT JOIN por
`id_municipio_rf` pode multiplicar linhas (a tabela de diretórios não garante
`id_municipio_rf` único — no RJ isso quase dobrou o total: 53.633 → 29.617
depois de deduplicar por `cnpj`). Sempre deduplique por `cnpj` ao montar o
JSON final.

## Passo 5 — Montar o JSON final

Formato de `src/data/<sigla>.json` (schema usado pelo app, ver
`canal-verde-map/src/components/MapView.jsx`):

```json
{
  "id": "cnpj-ou-uuid",
  "nome": "...",
  "tipo": "loja" | "empresa",
  "endereco": "...",
  "lat": -22.9,
  "lng": -43.2,
  "site": "https://... | null",
  "instagram": "https://instagram.com/... | null",
  "telefone": "(21) 99999999 | null",
  "email": "... | null",
  "fonte": "cnpj-aberto | (omitido pros registros de busca web)"
}
```

`tipo` = `"loja"` para CNAE 4729699/4637199 (varejo/atacado), `"empresa"` para
CNAE 1099607 (fabricante). `id` da camada CNPJ = `rj-cnpj-<cnpj>` (ou
`<sigla>-cnpj-<cnpj>`); da camada de busca web = `rj-web-<slug-do-nome>` —
mantenha esse prefixo, o script de montagem usa ele pra saber o que já existe
e não duplicar ao reprocessar.

**Volume grande exige cluster no mapa**: com a camada de CNPJ aberto o total
passa facilmente de 20-50 mil pontos por estado. `MapView.jsx` já usa
`react-leaflet-cluster` (`MarkerClusterGroup`) — não plote os pontos direto
com `Marker` solto quando o volume for grande, senão o navegador trava.

## Passo 5.5 — Busca complementar por cidade (opcional, preenche lacunas)

O CNAE não pega tudo (empresa mal classificada ou informal escapa da query do
BigQuery). Depois de ter a lista via BigQuery, rode uma busca complementar no
Google por cidade: `loja suplementos <cidade> <UF>`, `produtos naturais
<cidade> <UF>`, etc. Por padrão, restrinja isso às ~15-20 cidades de maior
peso econômico/populacional do estado (não os ~90+ municípios inteiros —
custo alto, retorno marginal baixo nas cidades pequenas). Só faça a varredura
de todos os municípios se o usuário pedir explicitamente cobertura total.
Qualquer achado novo aqui entra no JSON com o mesmo schema, sem CNPJ
disponível (`id` pode ser um slug do nome).

## Passo 6 — Registrar o estado no app

Adicionar em `canal-verde-map/src/data/estados.js`: importar o novo JSON e
adicionar uma entrada `{ sigla, nome, center: [lat, lng], zoom, dados }` no
array `ESTADOS`. O app já suporta múltiplos estados sem mudança de código.
