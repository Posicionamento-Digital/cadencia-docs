---
date: 2026-06-21
tags: [projeto, documentacao, observabilidade, cadencia]
moc: "[[MOC-Projetos]]"
---

# Central de Observabilidade + Auto-correção com IA

Sistema que transforma erros e alertas das ferramentas (Sentry, Grafana, Supabase, Vercel) em **issues no Linear automaticamente**, tria, notifica o Felipe no WhatsApp e tenta **auto-corrigir** bugs via agente de IA. Projeto Linear `91d67a96`. Doc técnica fonte-de-verdade: `_repos/sentry-linear-bridge/docs/architecture.md`.

## Componentes (multi-repo)
- **bridge + gate + health-check + deploy-drift** — `sentry-linear-bridge` (Coolify VPS Master + cron Master 08h BRT)
- **dispatcher Grafana + advisors Supabase** — `grafana-webhook` (systemd `:9300` + cron Master 09h BRT)
- **agente autofix + handoff Luiz** — `cadencia-autofix` (cron VPS Dev `*/15min`)

## Duas portas de entrada
- **Sentry** (erro de código) → bridge → gate classifica → `own:agente` (agente corrige, abre PR) / `own:felipe` / ruído descartado
- **Grafana / Supabase / Vercel** (infra) → dispatcher/worker → `own:felipe` direto (pula o gate) + WhatsApp

## Ownership (lock no Linear)
`own:triagem` (inicial) → `own:agente` (IA corrigindo) / `own:felipe` (alçada Felipe / infra) / `own:review` (PR aberto) / `own:luiz` (escalado).

## Auto-monitoramento
Health-check diário (08h) verifica bridge, gate, issues travadas e **deploy drift** (push que não virou deploy). Falha → issue `own:felipe` + WhatsApp.

## Estado (2026-06-21)
Central **operando fim-a-fim nas 2 fontes**.
- **Done:** CAD-684, 686, 687, 688, 689, 690, 706, 707, 708, 713, 717, 719.
- **Planejadas:** CAD-716 (auto-remediation + explicação rica), CAD-709 (Hostinger).
- **Pendências Felipe:** CAD-718 (apagar repo vazio), CAD-721 (rotacionar VERCEL_TOKEN).
- **Baseline de segurança detectado (projeto maint):** CAD-722 (cadencia, 2 ERROR), CAD-723 (hub-pd), CAD-724 (blog, 15 ERROR).

## Crons de produção
| Cron | Host | Schedule |
|---|---|---|
| autofix loop | VPS Dev (felipe) | `*/15 * * * *` (flock) |
| pr-watcher | VPS Dev (luiz) | `*/10 * * * *` |
| health-check + deploy drift | VPS Master (root) | `0 11 * * *` UTC = 08h BRT |
| supabase advisors | VPS Master (root) | `0 12 * * *` UTC = 09h BRT (flock) |

## Notas Relacionadas
[[MOC-Projetos]]
