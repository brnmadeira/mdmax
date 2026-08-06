# 🤝 Contribuindo para MdMax

Obrigado por ter interesse em contribuir para o MdMax! Este documento descreve como você pode ajudar.

## 📋 Código de Conduta

- Seja respeitoso com outros contribuidores
- Forneça feedback construtivo
- Foque na discussão, não na pessoa
- Respeite as decisões de design

## 🐛 Relatando Bugs

Encontrou um bug? Ótimo! Aqui está como reportar:

1. **Verifique se já foi reportado** - Procure nas Issues existentes
2. **Descreva o problema** - Seja específico e detalhado
3. **Forneça exemplo** - Se possível, inclua arquivo que reproduz o bug
4. **Seu ambiente** - Python version, SO, arquivos envolvidos

**Exemplo de issue:**
```
Título: OCR falha com imagens PNG > 10MB

Descrição:
- Ao tentar converter PNG maior que 10MB, OCR trava
- Tesseract retorna erro de memória
- Reproduzível com: test_image_large.png (12MB)

Ambiente:
- Python 3.9
- Windows 11
- Tesseract 5.2.0
```

## ✨ Sugerindo Features

Tem uma ideia? Compartilhe!

1. **Use Discussions** - GitHub Discussions para ideias
2. **Descreva o caso de uso** - Por que essa feature é útil?
3. **Forneça exemplos** - Como seria usada?

**Exemplo:**
```
Título: Suporte para arquivos HTML

Descrição:
Seria útil converter HTML diretamente para Markdown.
Caso de uso: blogs, documentação web, etc.

Exemplo:
Entrada: artigo.html (200KB)
Saída: artigo.md (50KB comprimido)
Economia: ~75%
```

## 🔨 Desenvolvendo

### Setup Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/mdmax.git
cd mdmax

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale dependências de desenvolvimento
pip install pytesseract pillow ebooklib pytest

# Instale o projeto em modo edição
pip install -e .
```

### Estrutura do Projeto

```
mdmax/
├── scripts/
│   ├── convert_ultimate.py       # Conversor principal
│   ├── converters_advanced.py    # OCR + EPUB
│   ├── dashboard_advanced.py     # Dashboard com 5 features
│   ├── auto_convert_wrapper.py   # Integração
│   └── quick_test_features.py    # Testes
├── README.md                      # Este arquivo
├── MDMAX_FEATURES.md             # Guia de features
├── AUTHORS.md                     # Contribuidores
├── LICENSE                        # MIT License
└── CONTRIBUTING.md               # Este arquivo
```

### Padrões de Código

- **Python 3.8+** - Use type hints quando possível
- **Encoding UTF-8** - Sempre `# -*- coding: utf-8 -*-` no topo
- **Docstrings** - Descreva funções públicas
- **Comments** - Explique o "por quê", não o "o quê"

**Exemplo:**
```python
def convert_to_markdown(file_path: str) -> dict:
    """Converte arquivo para Markdown comprimido.
    
    Args:
        file_path: Caminho absoluto do arquivo
        
    Returns:
        dict com chaves: markdown, tokens_saved, quality_score
    """
    # Validar arquivo existe
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    # Detectar tipo automaticamente
    ext = Path(file_path).suffix.lower()
    
    # ... resto da implementação
```

### Testando

```bash
# Executar teste rápido das features
python scripts/quick_test_features.py

# Testar dashboard
python scripts/dashboard_advanced.py

# Testar com arquivo específico
python scripts/auto_convert_wrapper.py /caminho/arquivo.pdf
```

## 📝 Fazendo um Pull Request

1. **Crie uma branch** com nome descritivo:
   ```bash
   git checkout -b feature/suporte-html
   git checkout -b fix/ocr-memoria
   git checkout -b docs/tutorial-dashboard
   ```

2. **Commit com mensagens claras:**
   ```bash
   git commit -m "Add suporte para arquivos HTML"
   git commit -m "Fix OCR memory leak com imagens grandes"
   git commit -m "Update README com exemplos"
   ```

3. **Push para seu fork:**
   ```bash
   git push origin feature/suporte-html
   ```

4. **Abra um PR** com:
   - Título claro e descritivo
   - Descrição do que foi mudado
   - Por que essa mudança é necessária
   - Qualquer issue relacionada (#123)

**Template de PR:**
```markdown
## Descrição
O que essa PR faz?

## Tipo de Mudança
- [ ] Nova feature
- [ ] Bug fix
- [ ] Documentação
- [ ] Refatoração

## Testes
Como testar essas mudanças?

## Screenshots (se aplicável)
Adicione prints do antes/depois

## Checklist
- [ ] Código segue o style guide
- [ ] Documentação foi atualizada
- [ ] Testes passam localmente
- [ ] Não há conflitos com main
```

## 🎯 Prioridades de Desenvolvimento

### Alta Prioridade
- 🔴 Bugs críticos (crash, data loss)
- 🔴 Segurança
- 🔴 Performance (>10% melhoria)

### Média Prioridade
- 🟡 Novas features muito solicitadas
- 🟡 Melhorias de UX
- 🟡 Suporte para mais formatos

### Baixa Prioridade
- 🟢 Code cleanup
- 🟢 Documentação
- 🟢 Melhorias menores

## 📚 Documentação

Se você está melhorando documentação:

1. **Mantenha markdown limpo**
2. **Use exemplos reais**
3. **Atualize Table of Contents**
4. **Teste links**
5. **Revise para português claro**

## 🎉 Reconhecimento

Todos os contribuidores serão reconhecidos em:
- CHANGELOG
- GitHub contributors page
- AUTHORS.md

## ❓ Dúvidas?

- brn.madeira@gmail.com
- 💬 GitHub Issues: Para questões técnicas
- 📢 GitHub Discussions: Para conversas abertas

---

**Obrigado por contribuir para MdMax!** 🚀
