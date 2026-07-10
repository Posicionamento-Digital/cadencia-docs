---
date: 2026-07-02
tags: [dev, llm, infra, referencia]
moc: "[[MOC-IA-Tecnologia]]"
type: source
entities: []
---

# LLM Cost Tracking — Repos Avaliados

Pesquisa pra sistema de metrificação de uso de tokens/custo LLM por cliente/projeto — relevante pro contexto Cadencia multi-tenant (saber quanto cada cliente está gastando, gasto por projeto, budget/limite por chave).

| Repo | Estrelas | O que faz |
|---|---|---|
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | 52k | Proxy/gateway unificado 100+ LLM APIs, cost tracking nativo por API key/team/tag — virtual key por cliente/projeto com budget/limite. **Recomendação principal.** |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | 30k | Observabilidade LLM (YC W23) — traces, custo por trace/sessão/usuário, dashboards. Mais debug/eval que billing. |
| [Portkey-AI/gateway](https://github.com/Portkey-AI/gateway) | 12k | Gateway rápido, guardrails, roteamento 1600+ modelos, budget alerts. |
| [traceloop/openllmetry](https://github.com/traceloop/openllmetry) | 7k | Observabilidade via OpenTelemetry — encaixa se já tem stack OTel. |
| [Helicone/helicone](https://github.com/Helicone/helicone) | 6k | Proxy de observabilidade, 1 linha de código, custo por usuário/rota. |
| [openmeterio/openmeter](https://github.com/openmeterio/openmeter) | 2k | Não é LLM-específico — metering + usage-based billing genérico (ingere eventos, agrega, fatura). Combina com LiteLLM: LiteLLM mede, OpenMeter fatura. |

## Recomendação

LiteLLM como proxy/medidor por cliente; se precisar faturar automaticamente por uso, complementar com OpenMeter.

## Contexto

Pesquisa disparada numa conversa com o aluno Vayne Saccaro (treinamento Claude Code) sobre como estruturar cobrança/monitoramento de custo de IA por cliente. Lista enviada a ele via WhatsApp comercial em 2026-07-02. Todos os 6 repos favoritados (starred) no GitHub do Felipe, organizados na lista "Self-hosted / Infra" (github.com/stars).

## Notas Relacionadas

Nenhuma nota existente sobre billing/metering de LLM no vault até o momento — esta é a primeira referência do tema.
