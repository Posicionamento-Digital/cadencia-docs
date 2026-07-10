> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `cadencia-workers/src/workers/chat-ideias/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-workers/src/workers/chat-ideias/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# chat-ideias — "Tenho uma Ideia" chat agent

## TL;DR

Chat conversacional onde o tenant aprova/refina ideias de conteúdo via diálogo. Tem SOUL_TEMPLATE próprio por tenant (voz da marca). Entry point: `POST /api/v1/chat`.

## Identidade

- **Tipo:** Worker Python com memória de sessão
- **Stack:** FastAPI + OpenAI + Supabase
- **Path:** `cadencia-workers/src/workers/chat_agent/`
  - `__init__.py` — router + entry point
  - `memory.py` — memória persistente de conversa
  - `session.py` — gestão de sessão por tenant
  - `SOUL_TEMPLATE.md` — template base da persona
- **Status:** ativo (controlado por feature flag `flag_chat_ideas` em `tenant_config`)
- **Deps:** `content_ideas`, `tenant_config`, `tenant_dossier`, `editorials`

## Como funciona

1. Tenant abre chat no frontend (`/app/ideas`)
2. Worker carrega: SOUL_TEMPLATE do tenant (gerado no onboarding pelo dossier) + memória de sessão
3. LLM responde como a "versão IA da marca" do tenant
4. Ao confirmar ideia: `POST /api/app/ideas/from-chat` cria registro em `content_ideas`
5. Ideia aprovada dispara pipeline de geração

## provision_soul_md

Chamado automaticamente após o dossier de onboarding. Gera SOUL.md personalizado por tenant (salvo em `tenant_config.config.soul_md`) a partir do SOUL_TEMPLATE genérico + dados do dossier.

## Feature flag

`tenant_config.config.flag_chat_ideas = true/false` controla se o chat aparece para o tenant.
Admin toggle: `POST /api/app/toggle-config`.

## Don'ts

- Não editar SOUL_TEMPLATE.md sem testar impacto no tom dos tenants existentes
- Não desativar `flag_chat_ideas` globalmente — desativar por tenant individualmente

---

## Quando usar

- Tenant clica em "Tenho uma ideia" no `/app/ideas` (controlado por feature flag `flag_chat_ideas`).
- Aprovar ideia do chat: `POST /api/app/ideas/from-chat` → cria `content_ideas` → dispara pipeline.

## Quando NÃO usar

- ❌ Geração automática de ideias programada — usar `ideas-generator` (não-conversacional).
- ❌ Tenant em fase 1 sem dossier — SOUL.md não foi provisionado, chat genérico.
- ❌ Bypass de aprovação para criar `content_idea` diretamente — quebra fluxo.

## Por que funciona assim

- [ADR-0002](../../../../docs/adr/0002-chat-agent-design.md) — Design do chat agent.
- SOUL.md por tenant (não global) — voz precisa ser específica da marca; template genérico solta tom errado.
- Feature flag por tenant — controle de rollout, especialmente para clientes white-glove vs self-service.

## 🚫 Don'ts

- **Não** editar `SOUL_TEMPLATE.md` global sem testar regressão nos tenants existentes.
- **Não** desativar `flag_chat_ideas` globalmente — desativar por tenant.
- **Não** persistir memória de sessão sem expiração razoável — ruído acumula.
- **Não** criar `content_idea` sem `editorial_id` — pipeline falha em step research.

## 🪦 Já tentamos

- Chat sem SOUL.md → tom corporativo genérico, sem encaixe com a marca. Razão de ter `provision_soul_md` no onboarding.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Chat não aparece para o tenant | `flag_chat_ideas` false | Toggle via `POST /api/app/toggle-config` |
| Tom da resposta genérico | SOUL.md não provisionado ou genérico | Verificar `tenant_config.config.soul_md`; regenerar via onboarding |
| Aprovar ideia não dispara pipeline | `content_idea` criada sem `editorial_id` | Validar payload antes de insert |
| Memória da conversa zerada inesperadamente | `session.py` perdendo state | Verificar TTL da sessão + Supabase persistence |

## 📚 Referências cruzadas

- [onboarding-workers](../onboarding/CLAUDE.md) — Provisiona SOUL.md
- [ideas-generator](../ideas/CLAUDE.md) — Alternativa automática (não conversacional)
- [pipeline-orchestrator](../CLAUDE.md) — Consumidor da `content_idea` aprovada
- [ADR-0002](../../../../docs/adr/0002-chat-agent-design.md)
