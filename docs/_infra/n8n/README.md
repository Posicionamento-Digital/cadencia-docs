---
date: 2026-05-13
tags: [infra, n8n, automacao, workflows, integracao]
---

# Infra — N8N

Plataforma de automação low-code usada pela PD para orquestrar workflows de atendimento, SDR, confirmações, notificações e integrações entre sistemas.

## O que é o N8N da PD

Instância self-hosted do N8N onde rodam os workflows que conectam:
- Agentes de IA (Lara, SDR, confirmação) ↔ WhatsApp (via HUB|PD)
- CRM Cadencia ↔ sistemas dos clientes (Ecuro, planilhas, CRMs)
- Notificações internas da equipe
- Integrações com APIs externas (Apollo, Meta, etc.)

## O que fica aqui

- Documentação dos principais workflows e o que fazem
- Credenciais e configurações necessárias (referência ao .env)
- Como exportar, importar e fazer backup de workflows
- Como diagnosticar workflow que parou de rodar
- Como adicionar novo webhook ou trigger

## Workflows principais

| Workflow | Função |
|---|---|
| Atendimento GCI-GO | Roteamento de leads para Lara por unidade |
| Confirmação de Consultas | Disparo de confirmação 24h antes |
| SDR Prospecção | Cadência multicanal de leads frios |
| Notificações Time | Alertas de suporte, chamados, pendências |

## Notas Relacionadas

- [[Projetos/GCI-GO/Docs/README]]
- [[Infra/VPS-Hostinger/README]]
- [[Incidentes/Infra/README]]
