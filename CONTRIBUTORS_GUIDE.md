# 👥 Como Receber Contribuições no MdMax

Guia completo para aceitar contribuições da comunidade.

---

## 🎯 O Que É Contribuição?

**Contribuir significa:** Outras pessoas melhorarem seu projeto adicionando:

- ✅ **Bug fixes** (corrigir erros)
- ✅ **Features** (novas funcionalidades)
- ✅ **Documentation** (melhorar docs)
- ✅ **Tests** (testes automáticos)
- ✅ **Performance** (melhorar velocidade)
- ✅ **Translations** (traduzir para outros idiomas)

---

## 📋 Passo 1: Configurar Repositório para Contribuições

### 1.1 Habilitar Issues e Discussions

**GitHub → Settings:**

1. Desça até "Features"
2. ✅ Issues (deve estar ligado)
3. ✅ Discussions (habilitar)
4. ✅ Projects (opcional)
5. Save

### 1.2 Criar Seção "Contribute" no README

Adicione no README.md (perto do final):

```markdown
## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for:

- How to report bugs
- How to request features
- How to submit pull requests
- Coding guidelines

**Get started:**

1. Fork the repository
2. Create your branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test: `python test_installation.py`
5. Commit: `git commit -m "feat: your change"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed instructions.
```

---

## 📝 Passo 2: Você Já Tem Tudo Configurado!

Verificar `CONTRIBUTING_NOVO.md` (renomeado para `CONTRIBUTING.md`):

✅ **Bug report template** - Como reportar erros  
✅ **Feature request template** - Como sugerir features  
✅ **Pull request template** - Como fazer PR  
✅ **Development setup** - Como configurar ambiente  
✅ **Testing guidelines** - Como testar  

---

## 🔄 Passo 3: Receber Contribuições (Fluxo)

### 3.1 Alguém Abre uma Issue

**Exemplo:** "Feature: Support for ODT files"

**O que você faz:**
1. ✅ Ler a issue
2. ✅ Responder se é viável
3. ✅ Label: `bug`, `feature`, `help wanted`, etc
4. ✅ Assign (se necessário)

### 3.2 Alguém Faz um Fork

Eles clicam no botão "Fork" no seu repo

### 3.3 Eles Fazem Mudanças

No fork deles:
```bash
git checkout -b feature/odt-support
# ... fazem mudanças ...
git commit -m "feat: add ODT file support"
git push origin feature/odt-support
```

### 3.4 Eles Abrem um Pull Request

Clicam em "New Pull Request" no GitHub

### 3.5 Você Revisa

```
Pull Request: "Add ODT file support"

Your review:
1. Ler o código
2. Testar localmente
3. Comentar mudanças
4. Pedir ajustes se necessário
5. Aprovar
6. Merge
```

---

## 🏷️ Passo 4: Usar Labels (Tags)

No GitHub → Issues:

**Crie labels:**

- `bug` - É um erro
- `feature` - Nova funcionalidade
- `documentation` - Melhoria de docs
- `good first issue` - Fácil para iniciantes
- `help wanted` - Precisa de ajuda
- `enhancement` - Melhoria
- `question` - Dúvida/pergunta

**Como usar:**

```
Issue aberta: "PDF crashes with large files"
↓
Você clica: Label → `bug`
↓
Aparece para contribuidores
```

---

## 📌 Passo 5: Criar "Good First Issue"

Isso atrai contribuidores iniciantes:

**Exemplo de Good First Issue:**

```
Title: Add support for .odt files

Description:
MdMax should support OpenDocument Text files (.odt).

What to do:
1. Add .odt to SUPPORTED_FORMATS in config.json
2. Create converter in converters_advanced.py
3. Test with sample .odt file
4. Add tests in test_installation.py

Resources:
- https://python-odt.readthedocs.io/
- Refer to .docx implementation as example

This is a good first issue because:
- Clear scope
- Existing examples in codebase
- No breaking changes
- Good learning opportunity

Help wanted! 🙌
```

---

## 📊 Passo 6: Revisar Pull Requests

### Checklist para Revisar PR:

```
[ ] Code follows project style
[ ] Tests added/updated
[ ] Documentation updated
[ ] No breaking changes
[ ] Solves the issue/feature
[ ] Performance impact acceptable
[ ] All checks pass (CI/CD)
```

### Como Revisar no GitHub:

1. Vá ao PR
2. Clique em "Files changed"
3. Clique no `+` ao lado da linha para comentar
4. Click "Review changes"
5. Escolha:
   - ✅ Approve
   - 🔄 Request changes
   - 💬 Comment

---

## 🎁 Passo 7: Agradecer Contribuidores

**Importante:** Sempre agradeça!

```
Great contribution! Thanks for:
- Adding .odt support
- Writing comprehensive tests
- Updating docs

This really helps the project grow.
Merged! 🎉
```

---

## 📢 Passo 8: Promover Contribuições

### No README:

```markdown
## 🌟 Contributors

Thanks to everyone contributing to MdMax!

[Lista de contributors - GitHub gera automaticamente]
```

### Badges:

Adicione ao README:

```markdown
![Contributors](https://img.shields.io/github/contributors/username/mdmax)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
```

---

## 🤖 Passo 9: Automação (Opcional)

### Usar GitHub Actions para:

- ✅ Rodar testes automaticamente no PR
- ✅ Checker de linting
- ✅ Build automático
- ✅ Comentar com resultado

**Você já tem:** `.github/workflows/test.yml`

---

## 💬 Passo 10: Criar Discussions

Use **Discussions** para:

- 📝 Ideias grandes (antes de criar issue)
- 💡 Perguntas gerais
- 🎉 Anúncios
- 🗣️ Discussions comunitárias

---

## 📋 Fluxo Completo: Um Exemplo Real

```
1️⃣ CONTRIBUIDOR QUER AJUDAR
   ├─ Vê "Good First Issue: Add .odt support"
   └─ Clica em: "I want to help!"

2️⃣ VOCÊ RESPONDE
   └─ "Great! Follow the steps in the issue"

3️⃣ CONTRIBUIDOR FORKS
   └─ Clica: Fork button

4️⃣ CONTRIBUIDOR FAZ MUDANÇAS
   └─ Cria branch e commit

5️⃣ CONTRIBUIDOR ABRE PR
   └─ "Add .odt file support"

6️⃣ VOCÊ REVISA
   ├─ Lê o código
   ├─ Testa localmente
   ├─ Pede ajustes (se necessário)
   └─ Aprova ✅

7️⃣ VOCÊ MERGE
   └─ "Merged! Great work, thanks!"

8️⃣ VOCÊ AGRADECE
   └─ Menciona no README

9️⃣ CONTRIBUIDOR FICA FELIZ
   └─ Vê seu nome no projeto

🔟 PROJETO MELHORA
   └─ Comunidade cresce
```

---

## 🎯 Tipos de Contribuições Esperadas

### 🐛 Bug Reports

```
Title: "PDF conversion crashes with files > 100MB"
Body: 
- Steps to reproduce
- Expected vs actual
- Error message
- Environment (Python version, OS)
```

### ✨ Feature Requests

```
Title: "Add support for .odt files"
Body:
- Use case
- Why it's useful
- Suggested implementation
```

### 🔧 Pull Requests

```
Title: "feat: add ODT file support"
Body:
- What changed
- Why
- How to test
- Related issues
```

### 📚 Documentation

```
Typos, examples, better explanations
```

---

## 📊 Métricas de Sucesso

Você saberá que está recebendo contribuições quando:

- ✅ Issues criadas por outros
- ✅ Discussões com perguntas
- ✅ Pull requests recebidas
- ✅ Commits de outros
- ✅ Stars aumentando
- ✅ Forks crescendo

---

## ⚖️ Mantendo Qualidade

**Rejeitar PR se:**
- ❌ Não segue estilo do projeto
- ❌ Sem testes
- ❌ Sem documentação
- ❌ Breaking changes
- ❌ Falha em testes automáticos

**Sempre:**
- ✅ Seja respeitoso
- ✅ Explique claramente
- ✅ Ofereça ajuda
- ✅ Agradeça o esforço

---

## 🚀 Tornar Mais Fácil Contribuir

### Adicione ao README:

```markdown
## 🚀 Quick Contribute

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/mdmax.git
cd mdmax

# 2. Create branch
git checkout -b feature/your-feature

# 3. Install dev dependencies
pip install -e ".[dev]"

# 4. Make changes and test
python test_installation.py

# 5. Commit
git commit -m "feat: your change"

# 6. Push and open PR
git push origin feature/your-feature
```

**See [CONTRIBUTING.md](./CONTRIBUTING.md) for full guide.**
```

---

## 💡 Primeiras Contribuições Ideais

Comece com isso para atrair contribuidores:

1. **Documentation** (fácil, útil)
   - Melhorar README
   - Adicionar exemplos
   - Corrigir typos

2. **Tests** (importante)
   - Coverage testing
   - Edge cases

3. **Bugs simples** (labeled "good first issue")
   - Um arquivo afetado
   - Claro o que fazer

4. **Performance** (avançado)
   - Profile code
   - Otimizações

---

## ✅ Checklist: Pronto para Receber Contribuições?

- [ ] Issues habilitadas
- [ ] Discussions habilitadas
- [ ] CONTRIBUTING.md completo
- [ ] README tem seção "Contributing"
- [ ] Templates para PR/Issues
- [ ] GitHub Actions configurado
- [ ] Labels criadas
- [ ] Pelo menos 1 "Good First Issue" criada
- [ ] Você tem tempo para revisar PRs
- [ ] Comunidade sabe que você aceita contribuições

---

## 🎊 Resultado

Quando tudo estiver configurado:

```
GitHub repo mdmax/
├── 👥 Comunidade engajada
├── 🐛 Issues sendo reportadas
├── ✨ Features sugeridas
├── 🔄 PRs sendo recebidas
├── ✅ Código sendo melhorado
└── 🚀 Projeto crescendo
```

---

**Você está pronto para receber contribuições!** 🎉

Próximo passo: Criar seu primeiro "Good First Issue" para atrair contribuidores iniciantes.
