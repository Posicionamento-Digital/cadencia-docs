---
date: 2026-06-27
tags: [doc, projeto, cadencia-growth]
moc: "[[MOC-Projetos]]"
---

# cadencia-growth — Playbook

Pipeline de growth do Cadência (Python 3.12). Roda hoje em `/cadencia` na VPS Master, com plano de migração pro Coolify projeto Cadencia documentado.

## Identidade
- **Tipo:** backend / daemons / crons (multi-componente)
- **Stack:** Python 3.12 · openai · anthropic · supabase · resend · ghl
- **Repo:** [Posicionamento-Digital/cadencia-growth](https://github.com/Posicionamento-Digital/cadencia-growth)
- **Path VPS atual:** `/cadencia`
- **Status:** ativo (produção)

## O que é
Geração e dispatch de conteúdo multi-canal multi-tenant + scoring de leads + provisioning GHL. 5 componentes: pipeline, scoring, crons, scripts, mission_control.

## Componentes documentados
- [[Projetos/Cadencia-Growth/Docs/pipeline]] — geradores + provisioning + cadence_tick + trigger_server :39090
- [[Projetos/Cadencia-Growth/Docs/scoring]] — webhooks GHL :8766 + Resend :8767
- [[Projetos/Cadencia-Growth/Docs/crons]] — orquestrador + retry + cleanup
- [[Projetos/Cadencia-Growth/Docs/scripts]] — operacionais + drift_check
- [[Projetos/Cadencia-Growth/Docs/mission-control]] — dashboard infra :8768

## Migração planejada
Documento completo em [docs/migracao-coolify.md](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/migracao-coolify.md). 9 etapas, ordem obrigatória. Quando Felipe decidir executar.

## Links
- [Repo GitHub](https://github.com/Posicionamento-Digital/cadencia-growth)
- [CLAUDE.md](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/CLAUDE.md) — regras DURAS anti-drift
- [CONTEXT.md](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/CONTEXT.md) — vocabulário ubíquo
- [Architecture diagram](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/architecture.md)

## Notas Relacionadas
[[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Coolify]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Servicos]]