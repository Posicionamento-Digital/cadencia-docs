---
date: 2026-06-22
tags: [brief, projeto, documentacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[comercial]]", "[[marketing]]", "[[pd-portal]]"]
---
# Brief — Cadencia — CLI/MCP de Controle

**Projeto Linear:** https://linear.app/cadencia/project/cadencia-climcp-de-controle-d9deefdea912
**Atualizado em:** 2026-06-22
**Preenchido por:** Felipe (via levantamento Vitor/Time Dev)

---

## O que é e por que existe

Sistema para operar o Cadencia inteiro por terminal/agente (lib + CLI + MCP futuro), começando pela operação comercial e criação de conteúdo de marketing, crescendo incrementalmente via registry/plugin.

Hoje o Cadencia só é operável pela UI (JWT de sessão) ou por acesso bruto (Supabase service_role / SSH), que **pula a lógica de negócio** (débito de crédito, idempotência, validações). Não há superfície limpa pra operar por terminal, agente ou cron. Usuários: Felipe (operador), agentes Claude Code (via shell), futuramente cron e multi-cliente.

---

## Stakeholders

- **Felipe** — owner / operador / decisões de produto e arquitetura
- **Luiz Sidião** — dev (escopo `cadencia-app` + `pd-portal`)
- **Time Dev** — Vitor (arquitetura), Amélia (execução), Camila (QA), Paula (docs)

---

## Estado atual

**Existe e maduro (`/api/app`, JWT sessão):** CRM completo — contacts (CRUD + search + import + sub-recursos), companies, opportunities, pipelines/stages, tags, custom-fields, crm-views, daily-goals, enrichment.

**Existe parcial (conteúdo):** content, generation-queue, trigger-generation, newsletter/generate.

**Workers:** growth já na VPS Master `/cadencia/` (`:39090/trigger`, HMAC). Carrossel/reels no Coolify VPS Master (migração concluída — DEV-638; Railway DESLIGADO).

**NÃO existe:** token de serviço · endpoint HMAC `/api/v1/automations/move-card` (CAD-582) · cadências (CAD-579/580/581) · email send (CAD-617) · campanhas (CAD-619) · multi-rede (CAD-624) · agendador (CAD-631).

---

## Arquitetura e stack

**3 camadas, sem duplicar lógica:** lib Python → CLI fina → MCP fino (depois). Design registry/plugin: cada ação é módulo auto-registrável.

**Acessos:** Supabase (`elefbabxkaigusjiiflu`, prod=`master`), `/api/app` (Vercel), workers (SSH + HTTP HMAC `:39090`). Tenant dogfooding PD `6bb2c1ba-7fb3-416a-b523-7c9561ea8db3`.

**Repo:** decisão **aberta pro PRD**. Inclinação: dentro de `cadencia-app` (feature do produto). Alternativas: `cadencia-cli` dedicado ou `pd-framework/_shared`.

---

## Decisões técnicas tomadas

1. CLI/lib antes de MCP (Claude Code já usa shell).
2. 3 camadas sem duplicar lógica.
3. Registry/plugin para crescimento barato.
4. Convenção de exposição = padrão CAD-582 (HMAC + idempotency + rate-limit + `tenant_api_keys`).
5. Camada de acesso decidida por comando (leitura→Supabase; mutação com lógica→`/api/app`; disparo→HTTP HMAC).

---

## O que NÃO fazer

- Não hardcodar destino de worker (migração Railway→Coolify VPS Master concluída — DEV-638).
- Supabase service_role bypassa RLS → risco; preferir `/api/app` quando houver token; parameterized queries.
- UA browser → 401 na service key (usar UA server-like).
- `generation_queue` schema instável (PDL-171) — verificar antes de escrever.

---

## Dependências críticas pendentes

- **Token de serviço** pras rotas `/api/app` — não existe. CAD-582 destrava. Gap de arquitetura #1.
- **Migração de workers** (CAD-21) — estabiliza destino de disparo.

---

## Critério de conclusão (V1)

**V1 = operar comercial + conteúdo fim-a-fim por linha de comando, no tenant PD (dogfooding):** CRUD + busca de contatos/empresas/oportunidades, mover pipeline, enfileirar/disparar geração de conteúdo. Tudo validado E2E no tenant PD.

**Fora do V1:** move-card HMAC (CAD-582, 1º pós-V1), cadências, email send, campanhas, multi-rede, agendador.
