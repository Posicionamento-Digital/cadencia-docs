---
date: 2026-06-24
tags: [doc, componente, workers, cron, central-cs]
moc: "[[MOC-Projetos]]"
status: ativo
type: source
entities: ["[[comercial]]"]
---
# Workers de Acompanhamento (DEV-797)

5 workers determinísticos + 1 lib comum em `pd-framework/times/cs/workers/`. Cron diário na VPS Master, gate de cliente, idempotência via `state.json` por worker.

## Lib comum

`_onboarding_followup_lib/` — `business_days_between`, `now_brt`, `StateStore` (JSON atômico via `os.replace`), `WhatsAppSender` (Evo, dry_run, account pessoal/comercial), `with_auto_label`, `gate_cliente`.

## Workers

| Worker | Função | Cron sugerido |
|---|---|---|
| `aprovacao-tacita-debrief` | Aprova debrief após 3 dias úteis sem resposta | 12 UTC (09 BRT) |
| `chip-aquecimento-14d` | 14 mensagens diárias do guia de aquecimento (inicio = kickoff + 48h) | 12 UTC |
| `confirmacao-agenda` | Lembrete véspera + confirmação no dia ⚠️ fonte Cal.com stubada | 11 UTC |
| `conferencia-cobranca-pasta` | Diff pedido vs recebido + cobrança a cada 2 dias + escala após 3 | 13 UTC |
| `followup-generico` | Mensagem N dias (corridos ou úteis) após âncora | 12:30 UTC |

Cada worker tem `worker.py --once [--apply]` + `state.json` versionado (estado consolidado pelo líder).

## Don'ts

- Não rodar com `--apply` sem validar dry_run.
- Não criar cron real sem aprovação Felipe.
- Não acoplar fonte de agenda ao Cal.com sem credencial resolvida (`confirmacao-agenda.fetch_compromissos_calcom` está stub).

## Relacionadas

- [[07-Evo-Client]] · [[01-Infra-Deploy]]



---

## Atualização 2026-06-27 — Deploy DEV-897 P1-P4 (dry_run)

**4 workers ativos na VPS Master em dry_run** (sessão com Felipe ao vivo via SSH). Detalhes completos no repo: `pd-framework/times/cs/workers/README.md`.

| Worker | Schedule (BRT) | Issue | Flag APPLY |
|---|---|---|---|
| digest-diario | diário 18:00 | DEV-881 | DIGEST_APPLY=0 |
| milestones | diário 18:05 | DEV-875 | MILESTONES_APPLY=0 |
| checkin-3-3 | a cada ~3 dias 18:10 | DEV-878 | CHECKIN_APPLY=0 |
| conferencia-cobranca | cron diário 18:15 | DEV-797 | ONBOARDING_APPLY=0 |

### Padrão de deploy (gotcha registrado)

- 2 EnvironmentFile por service: `/etc/onboarding/op.env` (compartilhado) + `.env` por worker
- `OnCalendar` com `America/Sao_Paulo` explícito — sem isso systemd interpreta como UTC
- Horários escalonados 5 min

### P5 pendente

Smoke `--apply` piloto OP — efeito real cliente (email + WhatsApp), 1 worker/vez com confirmação textual Felipe.

### Operação amanhã

```bash
ssh -i ~/.ssh/hostinger_prod_master master@72.60.4.71
sudo journalctl -u digest-diario.service --since today
```

### Refs sessão

- Log: [[Sessoes/Logs/2026-06-27 dev-cs-dev-897-deploy-workers-master]]
- PR: pd-framework#6 (`fcdf89c`)
- TODO PR cleanup: refletir no repo edições in-place (.service EnvironmentFile + .timer timezone). [[DEPLOY-ONDAS-1-3]] desatualizado.
- Issue futura: [[DEV-906]] migração workers pra repo `cs-workers` + Coolify.
