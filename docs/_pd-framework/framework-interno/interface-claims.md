---
date: 2026-07-03
tags: [doc, componente, pd-framework, documentacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[PD Framework]]"]
---
# Interface & Claims — o contrato do estado compartilhado (D5)

## Identidade
- **Tipo:** contrato + lib/CLI + specs (core)
- **Path:** `_core/INTERFACE-CONTRACT.md` · `_core/linear_claims.py` · `_core/HANDOFF-FORMAT.md` · spec do reaper em `times/dev/context/`
- **Issues:** epic DEV-1127 (stories DEV-1128…1131)
- **Status:** ativo (reaper = spec gated)

## O que é
A D5 do estudo ruflo operacionalizada: **agente fala com estado compartilhado via CLI, nunca MCP como fundação**. O Linear é a fila e o sistema de claims (assignee+status); markdown+git é a memória curada; `.pd/` é derivado local; Cadencia é negócio via cadencia-cli.

## Como funciona
1. **Contrato:** 3 canais com custo (hook empurra grátis · CLI puxa grátis · MCP paga contexto por mensagem) + teste de decisão + gatilhos que reabririam camada de estado própria (→ Supabase).
2. **Claims:** `check` (claimable/mine/taken/finished) · `claim` (recusa dono ativo — sem steal silencioso; comenta auditoria) · `release` (devolve com motivo).
3. **Handoff:** bloco em comentário Linear — razão tipada, % honesto, becos sem saída obrigatórios, próxima ação concreta.
4. **Reaper:** spec do worker que devolve issue presa (2 estágios ping→release, dry-run, isenções) — só constrói com gatilho de evidência.

## Quickstart
```bash
python _core/linear_claims.py check DEV-XXXX
python _core/linear_claims.py claim DEV-XXXX --as worker-1
python _core/linear_claims.py release DEV-XXXX --reason "bloqueada: credencial"
```

## Don'ts
- Nunca criar MCP server pra estado que CLI resolve (o erro do ruflo).
- Nunca duplicar a fila do Linear em banco local (YAGNI).
- Nunca steal silencioso — dono ativo é respeitado.

## Histórico
- 2026-07-03 — epic completo: d39c3d4 (contrato) · 9635d85 (claims, validado read-only no Linear real) · df25592 (handoff) · 513ece9 (spec reaper) · 6f4f309 (docs)

## Notas Relacionadas
[[model-map]] · [[memory-engine]] · [[session-recorder]] · repo: `_core/docs/interface-claims.md` · manual §10.7
