---
date: 2026-05-13
tags: [gci-go, documentacao, tecnico, lara, agendamento, ecuro]
---

# Docs — GCI-GO

> **ARQUIVO HISTÓRICO.** Registro do projeto encerrado; não representa a stack operacional atual da Cadencia.

Documentação técnica da implementação de IA para o **Grupo GCI — clínicas odontológicas em Goiás**.

## O que fica aqui

- Arquitetura do sistema de atendimento (agente Lara via WhatsApp)
- Integração com Ecuro (sistema de agendamento odontológico)
- Configuração do GHL: pipelines, workflows, automações por unidade
- Fluxos de atendimento, agendamento e confirmação de consultas
- Mapeamento de instâncias WhatsApp por unidade clínica
- Decisões técnicas e limitações conhecidas

## Stack técnica

| Camada | Ferramenta |
|---|---|
| Atendimento WhatsApp | Agente Lara via HUB\|PD |
| Agendamento | Ecuro MCP |
| CRM e pipeline de leads | GHL (por unidade) |
| Automações | N8N |

## Como funciona o atendimento

1. Lead chega via Meta Ads → WhatsApp da clínica
2. Lara atende, qualifica, agenda no Ecuro
3. Agente de confirmação confirma a consulta 24h antes
4. CRC monitora exceções e faz follow-up manual quando necessário

## Notas Relacionadas

- [[Projetos/GCI-GO/Runbooks/README]]
- [[Clientes/GCI/Manual-Utilizacao-Lara]]
- [[Clientes/GCI/Manual-CRM-PD]]
- [[Projetos/ecuro-mcp/Docs/README]]
- [[Incidentes/GCI-GO/README]]
