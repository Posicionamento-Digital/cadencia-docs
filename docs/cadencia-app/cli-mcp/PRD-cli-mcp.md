---
date: 2026-06-22
tags: [projeto, documentacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[comercial]]"]
---
# PRD — Cadencia: CLI/MCP de Controle

**Projeto Linear:** https://linear.app/cadencia/project/cadencia-climcp-de-controle-d9deefdea912 · **Autor:** Felipe · **Status:** Draft · **Data:** 2026-06-22

> Fonte da verdade = Linear Document. Esta é cópia de leitura. Gerado por Paloma (PO) via /linear-prd.

## Problema

Não existe forma limpa de operar o Cadencia por terminal/agente. Três superfícies fragmentadas: `/api/app` só aceita JWT de sessão (sem token de serviço); Supabase service_role bypassa RLS e pula a lógica de negócio; workers só por cron/SSH/HMAC disperso. Qualquer operação programática vira colcha de retalhos.

## Objetivo & métricas

Operar o Cadencia por terminal/agente via 3 camadas (lib Python → CLI → MCP futuro), módulos comercial + conteúdo, crescendo via registry/plugin sem duplicar lógica. **V1** = operar comercial + conteúdo fim-a-fim por CLI no tenant dogfooding PD (`6bb2c1ba`), validado E2E.

## Escopo (in)

Fundação arquitetural (lib registry/plugin + camada de acesso por comando + config de credenciais/worker) · Comercial — CRM (contacts/companies/opportunities/pipelines/tags/custom-fields/crm-views/enrichment) · Conteúdo (content/generation-queue/trigger-generation/newsletter) · CLI fina.

## Fora de escopo

MCP (camada 3, depois) · move-card HMAC (CAD-582) · cadências · email send · campanhas · multi-rede · agendador · backend inexistente · operar fora do tenant PD no V1.

## Requisitos não-funcionais (destaques)

service_role bypassa RLS (filtrar `tenant_id` sempre + queries parametrizadas) · credenciais via 1Password · UA server-like no Supabase · isolar instabilidade de schema `generation_queue` (PDL-171).

## Riscos & dependências

Decisão de repo (aberta — inclinação `cadencia-app`) · token de serviço inexistente (CAD-582 é o protótipo que destrava) · trigger on-demand limpo dos workers · migração Railway→Coolify (CAD-21, não hardcodar destino) · service_role bypassa RLS · schema `generation_queue` instável.

## Epics (V1)

- **Epic A** — Fundação arquitetural (lib + registry + acesso + config)
- **Epic B** — Módulo comercial (CRM)
- **Epic C** — Módulo conteúdo (geração)
- **Epic D** — Validação E2E no tenant PD

**Roadmap pós-V1:** CAD-582 (1º candidato), cadências, email send, campanhas, multi-rede, agendador.

## Marcos

Design+plano (decisão de repo + gate arquitetural + matriz de acesso) → Implementação (A → B+C) → Release (D — V1 validado no tenant PD).
