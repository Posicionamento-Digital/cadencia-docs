---
date: 2026-05-13
tags: [processos, monitoramento, health, alertas, cron, uptime, clientes]
---

# Processos — Monitoramento

Como a equipe PD monitora a saúde dos sistemas, pipelines e clientes. O objetivo é detectar falhas **antes** que o cliente perceba.

## O que fica aqui

- Checklist de monitoramento diário (o que verificar toda manhã)
- Alertas configurados e onde chegam (WhatsApp, email, Slack)
- Como verificar saúde dos crons na VPS
- Como verificar instâncias WhatsApp conectadas no HUB|PD
- Como monitorar health de clientes no CRM Cadencia (score de engajamento)
- O que fazer quando um sistema cai fora do horário comercial

## O que monitoramos

| Sistema | Frequência | Como |
|---|---|---|
| Crons da VPS | Diário | `crontab -l` + logs |
| Instâncias WhatsApp | Diário | HUB\|PD painel |
| Agente Lara | Diário | Conversas e agenda no CRM Cadencia |
| Pipeline Cadência | Após cada geração | Log de output |
| N8N workflows | Semanal | Execuções com erro |

## Notas Relacionadas

- [[Infra/VPS-Hostinger/README]]
- [[Projetos/GCI-GO/Runbooks/README]]
- [[Incidentes/README]]
- [[Processos/Como-Trabalhamos/README]]
