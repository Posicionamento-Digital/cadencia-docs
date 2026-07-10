# Arquitetura — Observabilidade + Notificação da PD

> Doc vivo. Blueprint de como a PD sabe que seus sistemas automatizados rodaram, quebraram ou ficaram em silêncio — e por onde os avisos chegam.
> Criado: 2026-06-23. Status: **desenho aprovado, implementação não iniciada.**

## Princípio diretor

- **Slack** = notificação assíncrona de máquina (rotina). Feed pesquisável dos sistemas.
- **WhatsApp/Stevo** = humano + urgente. Cliente nunca sai daqui.
- **Linear** = fonte de verdade do trabalho. Slack só reflete.
- **Obsidian** = conhecimento.
- Nada duplica comunicação que já funciona. Slack absorve o ruído de rotina que hoje polui o WhatsApp.

## As 4 dimensões de observabilidade

| Dimensão | Pergunta | Ferramenta | Status |
|---|---|---|---|
| Infra | "a máquina está viva/saudável?" | Grafana + `monitor-vps.sh` (Master, */5min) | ✅ existe |
| Aplicação | "o código quebrou em runtime?" | Sentry → bridge Linear | ✅ existe |
| Execução/liveness | "rodou OK / rodou com erro / NÃO rodou?" | heartbeat + cron-watchdog | ❌ a construir |
| **Negócio (clientes+projetos)** | "a operação está andando ou apodrecendo?" | business-watchdog (Linear + Cadencia CRM + Asaas) | ❌ a construir |

**Ponto cego comum às 2 camadas novas:** Sentry/Grafana (e o próprio negócio) são reativos a evento. Job que não dispara, cliente que para de engajar, issue que congela — nada "gera um erro"; apodrecem em silêncio. Os watchdogs invertem: assumem que algo *deveria* ter acontecido e alertam pela **ausência**. Único jeito de pegar morte silenciosa, técnica ou comercial.

### Dimensão Negócio — sinais

A lógica de leitura do Linear já existe na skill `/status` (pull manual). O business-watchdog a torna **proativa (push agendado)** e pluga no mesmo dispatcher.

| Sinal | Fonte (já existe) | Severidade |
|---|---|---|
| Pagamento atrasado | Asaas (`_shared/asaas_client`) | ALTA → WhatsApp |
| Cliente sem touchpoint há > N dias | Cadencia CRM timeline (cadencia-cli) | ROTINA (ALTA se tier alto) |
| Onboarding travado numa fase > prazo | Linear projeto impl + CS playbook 11 fases | ROTINA |
| Queda de engajamento no produto | Cadencia (posts não aprovados, sem login) | ROTINA |
| Contrato/renovação vencendo | Asaas + planilha contratos | ROTINA antecipada |
| Issue In Progress sem update há > N dias | Linear | ROTINA |
| Milestone/fase com prazo estourado | Linear | ALTA |
| Issue Urgent/P1 parada | Linear | ALTA |
| Projeto sem atividade há > N dias | Linear | ROTINA |

- **Registry de clientes** = Customers do Linear (já tem status/tier/needs). Não recriar.
- **Thresholds** começam grosseiros (7 dias sem touchpoint; fase > prazo do playbook) e calibram com uso. Definição dos números é do Felipe.
- Canais Slack novos: `#clientes`, `#projetos`.

## Fluxo

```
FONTES → DISPATCHER (:9300, já existe) → roteia por severidade → SLACK (rotina) | WhatsApp+Linear (alta)

INFRA: Grafana, monitor-vps.sh        ┐
APLICAÇÃO: Sentry                      ├─► grafana-webhook :9300 ─► severidade?
EXECUÇÃO: heartbeat() + watchdog (NOVO)┘                            ├ ALTA   → WhatsApp + Linear
                                                                    └ ROTINA → Slack
```

## Regra de roteamento por severidade

| Evento | Severidade | Destino |
|---|---|---|
| Prod caiu / cliente impactado / ação urgente | ALTA | WhatsApp + Linear |
| Job não rodou (watchdog) | ALTA | WhatsApp + Linear |
| Deploy READY / PR aberto / job rodou OK | ROTINA | Slack `#deploys` / `#heartbeat` |
| Alerta de infra recuperável | ROTINA | Slack `#alertas` |
| Plano do dia / log de sessão | INFO | Slack `#meu-dia` / `#log-sessoes` |

## Canais Slack (workspace cadencia-grupo.slack.com)

Começar magro: `#alertas` + `#deploys` + `#heartbeat`. Expandir só se provar valor.

| Canal | Conteúdo | Quem posta |
|---|---|---|
| `#alertas` | infra recuperável, fiscal, drift | workers via webhook |
| `#deploys` | PR/deploy status | pr-watcher, Vercel/Coolify |
| `#heartbeat` | "rodei OK" de todos os jobs (feed p/ watchdog auditar) | todos os jobs |
| `#incidentes` | Sentry + Grafana estruturados | bridges existentes |
| `#linear` | eventos de issue/PR | webhook nativo Linear↔Slack |
| `#meu-dia` | plano do dia, lembretes | /abrir-dia, /agenda |
| `#log-sessoes` | resumo /encerrar-sessao, handoff Luiz | skills de sessão |

## Registry de jobs (os 12 sob vigilância)

`_core/jobs-registry.yaml` — fonte de verdade do watchdog. Campos: nome · host · schedule · janela de tolerância · severidade-se-sumir.

| Job | Host | Schedule | Notificado hoje? |
|---|---|---|---|
| AlertasFiscais-PD | Windows | 09:00 diário | ❌ |
| VaultOrganizer-Daily | Windows | 18:00 diário | ❌ |
| Claude-LimparWorktrees | Windows | 18:05 diário | ❌ |
| SyncDevDocsVault | Windows | 23:30 | ❌ **FALHANDO (result 1)** |
| monitor-vps.sh | Master | */5min | parcial (é o monitor) |
| state-aggregator-cron.sh | Master | 06:00 | ❌ |
| cadencia-trigger.service | Master | long-running | systemd |
| cadencia-webhook.service | Master | long-running | systemd |
| grafana-webhook.service | Master | long-running | systemd (é o dispatcher) |
| sync-dev-docs.py | Dev | 23:00 | só log |
| cadencia-autofix (CAD-689) | Dev | */15min | só log |
| pr-watcher (Luiz) | Dev | */10min | log + WhatsApp |

> `analisar-post` (Windows) — **obsoleto, remover Task** (Felipe confirmou que não existe mais; acusa erro 0x8007010B à toa).

## Reaproveitado vs construído

| Já existe (não tocar) | Construir |
|---|---|
| Grafana + monitor-vps.sh | `_core/jobs-registry.yaml` |
| Sentry → Linear | `_shared/heartbeat.py` (1 linha por job) |
| Dispatcher :9300 (roteamento) | `cron-watchdog` (audita ausência, na Master) |
| Stevo/WhatsApp + Linear | `_shared/slack_notify.py` (Incoming Webhook por canal) |
| MCP Slack (skills interativas) | 5-7 canais Slack + 1 Slack App c/ webhooks (URLs no 1P) |

## Segurança

- VPS Master só roda scripts determinísticos (heartbeat/watchdog em Python puro, sem tool-use de agente) — respeita `_core/SECURITY.md`.
- Webhook URLs do Slack guardadas no 1Password, nunca commitadas.

## Pendências de implementação (ordem sugerida)

1. Remover Task `analisar-post` (Windows). [destrutivo — confirmar]
2. Investigar/consertar `SyncDevDocsVault` (Windows 23:30).
3. Criar `_core/jobs-registry.yaml` com os 12 jobs.
4. Criar Slack App + Incoming Webhooks → 1P. Criar canais.
5. `_shared/slack_notify.py` + `_shared/heartbeat.py`.
6. Instrumentar os 12 jobs com `heartbeat()`.
7. `cron-watchdog` na Master cruzando registry × heartbeats.
8. Webhook nativo Linear↔Slack.

## Risco real (não-técnico)

Slack só ajuda se o hábito migrar: parar de checar aviso no WhatsApp. Se virar "mais um lugar pra olhar", piora. Por isso começar magro e expandir sob evidência.
