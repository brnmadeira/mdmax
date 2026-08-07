---
name: enforcer
description: Valida transparência — detecta promessas vazias e força reconhecimento automático
---

# Enforcer: Transparência Total

**Status:** ✅ Auto-ativo via hook Stop

Detecta padrões proibidos e força você a reconhecer quando comete promessa vazia.

## Como Funciona

**Automático:**
- Hook Stop roda após cada resposta
- Script Python valida contra patterns
- Se encontra violação: systemMessage força reconhecimento
- Você reconhece e reexecuta AGORA

**Manual:**
- Execute `/enforcer` quando suspeitar
- Valida última resposta
- Lista exatamente o quê violou

## Padrões Bloqueados

```
❌ "deixa eu investigar/procurar" sem tool executada
❌ "vou investigar" sem resultado concreto
❌ "agent investigando em background" (promessa invisível)
❌ Anunciar ação (ler, buscar, checar) sem ferramenta disparada
```

## Padrões Obrigatórios

```
Vou fazer isso:
□ Read arquivo X
□ Grep padrão Y
□ Execute tool Z

▶️ Executando...
[resultado real]

✅ Encontrei X
```

## Arquivos

- **Hook config:** `.claude/settings.json` (Stop event)
- **Script:** `~/.claude/validate-response.py`
- **Regra:** `~/.claude/CLAUDE.md` (ENFORCER section)

---

**Zero promessas vazias. 100% automático.**
