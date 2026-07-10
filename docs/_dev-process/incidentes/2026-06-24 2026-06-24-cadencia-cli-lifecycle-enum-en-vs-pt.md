---
type: source
source_kind: incidente
date: 2026-06-24
entities: ["[[Cadencia]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-06-24_cadencia-cli-lifecycle-enum-en-vs-pt

# Incidente: cadencia-cli — `--lifecycle` aceita enum em inglês mas o CRM usa português (UPDATE falha com 400 silencioso)

**Data:** 24/06/2026
**Severidade:** Média
**Projeto:** cadencia-cli
**Duração do impacto:** não afetou produção do produto; bloqueou um update de contato (contornado)
**Tags:** #backend #api #supabase #cli #silenciosa #falha-detectada

## O que aconteceu

Ao corrigir o lifecycle da cliente Nathalia Galardo (contato `6ab4f719`, `lead` → cliente) durante o setup da sincronização Cal.com→CRM, rodei:

```
cadencia-cli contacts update 6ab4f719... --lifecycle customer
```

O comando retornou apenas `Erro: Client error '400 Bad Request' for url '.../database/query'` — sem dizer o motivo. O `--first-name`/`--last-name` no mesmo contato funcionaram; só o `--lifecycle` falhava.

Workaround usado: `UPDATE contacts SET lifecycle='cliente'` direto via Supabase Management API. **Isso está fora do caminho oficial** (a regra é operar via CLI/API do produto, não SQL direto no Supabase) — usado só como contorno pontual, autorizado pelo Felipe na hora.

## Causa raiz

1. `src/cadencia_cli/actions/contacts.py` (update/create) repassa o valor de `--lifecycle` **cru** ao banco, sem validar nem traduzir.
2. O help e `docs/COMMANDS.md` documentam `lifecycle (lead/mql/sql/customer/churned)` — **valores em inglês**. O enum real da coluna `contacts.lifecycle` usa **português**: `lead`, `cliente`. `customer` não existe → constraint rejeita → HTTP 400.
3. O CLI **engole o corpo do erro** do Supabase/PostgREST e mostra só `400 Bad Request` genérico, escondendo a causa real.

## Por que não foi detectado

- Sem teste de `update` com valor de `lifecycle` real (válido e inválido).
- Help/docs do CLI nunca foram conferidos contra o enum real do schema.
- Erros do backend não são propagados — a mensagem genérica impede diagnóstico rápido.

## Como foi corrigido

Parcial. O dado da Nathalia foi corrigido (`lifecycle='cliente'`, `temperatura='quente'`, nome) via Supabase Management API — contorno pontual. **O bug do CLI permanece** — issue de correção aberta (ver Links).

## Prevenção

### Checklist / regras pra evitar recorrência

- [ ] CLI valida `--lifecycle` (e checar `--status`, `--lead-source`, `--temperatura`) contra os enums reais do schema antes de enviar; rejeita com mensagem clara listando os valores válidos.
- [ ] CLI propaga o corpo do erro do Supabase/PostgREST em vez de `400 Bad Request` genérico.
- [ ] Atualizar `docs/COMMANDS.md` + help com os valores reais (`lifecycle: lead/cliente`; confirmar os demais campos enum no schema).
- [ ] Teste cobrindo `contacts update` com lifecycle válido e inválido.
- [ ] Não usar Supabase Management API direto como caminho operacional — só workaround pontual e registrado.

### Pattern correto

```python
LIFECYCLE_VALIDOS = {"lead", "cliente"}  # enum real do schema (confirmar no DB)
if lifecycle is not None and lifecycle not in LIFECYCLE_VALIDOS:
    raise typer.BadParameter(f"lifecycle inválido. Válidos: {sorted(LIFECYCLE_VALIDOS)}")
```

### Regra atualizada em

- [ ] `docs/COMMANDS.md` do cadencia-cli (valores enum reais)
- [ ] Help dos comandos `contacts create/update/list`

## Commits relacionados

- (pendente — correção na issue vinculada)

## Links relacionados

- Issue de correção: [DEV-833](https://linear.app/cadencia/issue/DEV-833)
- Contexto: setup sincronização Cal.com→CRM · mapa `stamper/context/mapa-cal-com.md`

---
*Registrado via sistema de incidentes. Ver INDEX.md para histórico completo.*
