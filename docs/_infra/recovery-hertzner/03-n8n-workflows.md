---
date: 2026-05-19
tags: [documentacao, recovery, hetzner, n8n, workflows, automacao, ia, tecnologia]
moc: "[[MOC-Projetos]]"
---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

# 03 — N8N Workflows

## O que é
Backup completo das automações n8n capturadas em 09/05/2026. 188 workflows + 92 credenciais, prontos para importar.

## Conteúdo
- `workflows/` — 188 JSONs renomeados com o nome real de cada workflow
- `credentials/` — 92 JSONs de credenciais (WhatsApp, Ecuro, GHL, Airtable, Pipedrive)

## Como importar
1. n8n → Workflows → Import from file → selecionar JSONs
2. Importar primeiro os 41 workflows **ativos**
3. Settings → Credentials → Import → JSONs de `credentials/`
4. Atualizar secrets após importar (podem ter expirado)

## 41 workflows ativos (prioridade)
Agendamento: `[AGENDAMENTO] [CABO FRIO]`, `[AGENDAMENTO] [MACAÉ]`, `[AGENDAMENTO] [RIO DAS OSTRAS]`, `[AGENDAMENTO] [SAO PEDRO]`, `[AGENDAMENTO] [VILA ISABEL]`, `AGENDAMENTO`, `Verificar e Realizar Agendamento`

Fluxos: `[SORRIA-RIO] [CABO FRIO]`, `[SORRIA-RIO] [MACAÉ]`, `[SORRIA-RIO] [RIO DAS OSTRAS]`, `[VAMOS-SORRIR] [VILA ISABEL]`, `[FLUXO PRINCIPAL] [CASA-DIGITAL]`, `Central [GOIAS]`, `Teresopolis Fluxo Principal`

Confirmações: `Confirmação Cabo Frio`, `Confirmação Macaé`, `Confirmação Meier`, `Confirmação Teresopolis`, `Confirmação [CAMPO GRENDE]`, `CONFIRMAÇÃO [BANGU]`, `CONFIRMAÇÃO [MADUREIRA]`, `Fluxo confirmação`

Infra: `WEBHOOK-GERAL`, `Backup-credenciais`, `Backup-workflows`, `QR-CODE`, `QRCode`

## Arquivos `_dup`
Duplicados: verificar qual versão manter. `QR-Code_1_dup.json` estava ativo.

## Notas Relacionadas
[[00-indice]] · [[04-banco-dados]] · [[05-infraestrutura]]
