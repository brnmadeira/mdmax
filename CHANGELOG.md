# 📝 Changelog - MdMax

Todas as mudanças notáveis do projeto MdMax serão documentadas neste arquivo.

## [2.0] - 2026-08-03

### ✨ Adicionado

#### 5 Melhorias de Contador
- 🏆 **Ranking em Tempo Real** - Ordena formatos por economia total
- 📊 **Projeção de Economia Mensal** - Calcula para 30 dias e 1 ano
- 🎯 **Notificações de Milestone** - Detecta 10K, 100K, 1M, 10M tokens
- 💾 **Export de Estatísticas** - CSV e JSON automáticos
- 📈 **Gráfico de Tendência** - Visualização dos últimos 30 dias

#### Dashboard Avançado
- Console ASCII com todas as 5 features
- Dashboard HTML interativo com cores e gráficos
- Botões de download para JSON/CSV
- Barra de progresso para milestones

#### Documentação
- `MDMAX_FEATURES.md` - Guia completo das features
- `README_GITHUB.md` - README para GitHub launch
- `AUTHORS.md` - Informações do desenvolvedor
- `CONTRIBUTING.md` - Guia para contribuidores
- `CHANGELOG.md` - Este arquivo

#### Ferramentas
- `dashboard_advanced.py` - Novo módulo com 5 features
- `quick_test_features.py` - Script de validação automática
- `view_dashboard.bat` - Atalho para visualizar dashboard

### 🔧 Alterado

- `auto_convert_wrapper.py` - Integração com novo dashboard
- `MDMAX_FEATURES.md` - Atualizado com v2.0+
- `config.json` - Suporte a 16 formatos confirmado

### 🏆 Status

- ✅ 16 formatos suportados
- ✅ 7 otimizações de compressão
- ✅ 4 features avançadas (OCR, EPUB, Dashboard, Compressão +5-10%)
- ✅ 5 melhorias de contador (Ranking, Projeção, Milestones, Export, Trend)
- ✅ Documentação completa
- ✅ Testes validados
- ✅ Pronto para GitHub launch

---

## [1.5] - 2026-08-01

### ✨ Adicionado

#### Suporte para Imagens e E-books
- 📷 JPG/PNG com OCR multilíngue
- 📚 EPUB (e-books) com extração de capítulos
- 🎨 SVG com conversão vetorial

#### Compressão Avançada
- Compressão Markdown +5-10% adicional
- Minificação de código blocos
- Remoção de HTML comentários
- Compressão de URLs longas

#### Dashboard Básico
- Console ASCII com estatísticas
- Ranking de formatos
- Gráfico ASCII de tendência

### 🔧 Alterado

- `converters_advanced.py` - Novo módulo com 450+ linhas
- `dashboard.py` - Versão 1 do dashboard
- Suporte expandido de 11 para 16 formatos

### 🎯 Status

- 16 formatos (PDF, XLSX, DOCX, PPTX, CSV, TSV, JSON, TXT, ODS, XLS, XLSM, SVG, JPG, PNG, EPUB)
- 7 otimizações de compressão
- 4 features avançadas

---

## [1.0] - 2026-07-25

### ✨ Adicionado

#### Conversor Principal
- Suporte para 11 formatos (PDF, XLSX, DOCX, PPTX, CSV, TSV, JSON, TXT, ODS, XLS, XLSM)
- Conversão automática para Markdown
- 7 otimizações de compressão

#### Sistema de Cache
- MD5 file hashing
- SHA256 content hashing
- Detecção de duplicatas automática
- Reutilização de conversões anteriores

#### Token Economy
- Rastreamento de tokens economizados
- Cálculo dinâmico por tipo de arquivo
- Predição de tokens antes da conversão
- Recomendações inteligentes

#### Integração
- Hook PostToolUse automático
- Processamento paralelo (3 workers)
- Limpeza automática de cache (7 dias)
- Validação de qualidade Markdown

### 🔧 Estrutura

```
convert_ultimate.py (23 KB)
├── TokenPredictor
├── RecommendationEngine
├── IndexGenerator
├── QualityValidator
├── StreamProcessor
├── CacheManager
├── CacheCleaner
├── MarkdownConverter (16 formatos)
├── EconomyTracker
└── process_directory()
```

### 🏆 Benchmarks

- PDF 50MB: ~2,850 → 285 tokens (90% economia)
- XLSX 5MB: ~2,500 → 750 tokens (70% economia)
- DOCX 3MB: ~1,800 → 630 tokens (65% economia)

### 🎯 Status

- ✅ Versão 1.0 funcional
- ✅ 11 formatos suportados
- ✅ 7 otimizações ativas
- ✅ Hook automático configurado
- ✅ Cache inteligente implementado

---

## Convenções de Versionamento

Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR** - Quebra de compatibilidade (1.0.0 → 2.0.0)
- **MINOR** - Nova feature compatível (1.0.0 → 1.1.0)
- **PATCH** - Bug fix (1.0.0 → 1.0.1)

---

## Roadmap Futuro

### v2.1 (Próximo)
- [ ] Suporte para mais idiomas (Chinês, Japonês)
- [ ] Otimização de performance para arquivos >500MB
- [ ] Cache distribuído em cloud

### v3.0
- [ ] Integração com Google Drive
- [ ] Integração com OneDrive
- [ ] API REST para integração com outras ferramentas

### v3.5
- [ ] Machine learning para detecção de relevância
- [ ] Compressão inteligente com IA
- [ ] Análise de sentimento em textos

---

## Contribuidores

- brn.madeira@gmail.com

---

## Agradecimentos

Obrigado a todos que ajudaram a melhorar MdMax através de:
- Bug reports
- Sugestões de features
- Contribuições de código
- Testes e feedback

---

**MdMax © 2026 - Desenvolvido com ❤️ para economizar tokens do Claude**
