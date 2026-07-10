---
date: 2026-07-04
tags: [doc, documentacao, projeto, observabilidade]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Central de Observabilidade]]"]
---

# hostinger_watcher — eventos do provedor viram alerta/issue (DEV-709)

## TL;DR
Cron diário na Master que consulta a hAPI (Hostinger) e alerta sobre o que o Grafana **não vê**: estado de VM mudado pelo provedor, assinatura suspensa e — o caso de maior valor — **auto-renew desligado com cobrança próxima** (preditivo, pega antes da suspensão).

## Identidade
- **Tipo:** worker/cron (Python stdlib)
- **Path:** `times/infra/workers/hostinger_watcher.py` · roda em `/opt/pd-framework/`
- **Cron:** `0 8 * * *` UTC (crontab do master)
- **Fonte:** hAPI `developers.hostinger.com` (`/vps/v1/virtual-machines` + `/billing/v1/subscriptions`)
- **Secret:** `HOSTINGER_API_TOKEN` (1P `Credencial API - Hostinger [ClaudeCode]`, vault Hosts) via `_shared/secrets`
- **Estado:** `~/.hostinger-watcher/state.json` — alerta **só na transição** (anti-spam)
- **Vigiado por:** health check (mtime de `~/logs/hostinger-watcher.log`)

## Roteamento
| Achado | Destino |
|---|---|
| VM ≠ `running` / `actions_lock` ≠ `unlocked` · assinatura ≠ `active` | Slack `#urgente` + issue Linear `tipo:infra` no projeto Central (dedup por título) |
| Auto-renew OFF com cobrança ≤7d | Slack `#saude-sistemas` |
| Normalização (ALTA → OK) | Slack `#saude-sistemas` |

## Limitações declaradas
- Roda na própria Master — se o provedor derrubar a Master, morre junto. O valor real é o preditivo (billing) e a VPS Dev.
- Manutenção programada / incidente de datacenter só chega por **email** do provedor — email-parser é v2 (na issue).

## Quickstart
```bash
python times/infra/workers/hostinger_watcher.py --dry-run
```

## Troubleshooting
- **401 na hAPI** → token expirado; regenerar no painel Hostinger e atualizar o item do 1P.
- **Issue não criada em achado ALTA** → precisa de `LINEAR_API_KEY` (env ou cascata do adapter); ver log.

## Histórico
- 2026-07-04 — criado (DEV-709); baseline real: 2 VMs + 3 assinaturas, tudo OK


## Notas Relacionadas
[[deploy-log-e-deploy-watcher]]
