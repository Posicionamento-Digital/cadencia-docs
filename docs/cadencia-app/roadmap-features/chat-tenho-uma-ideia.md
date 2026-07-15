---
date: 2026-05-16
tags: [cadencia, feature, chat, agent, pdl, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Karina Vieira]]"]
---
# Chat — "Tenho uma Ideia"

> Documentação técnica completa: `Cadencia/docs/features/chat-tenho-uma-ideia/README.md`
> Wiki HTML: `Cadencia/docs/wiki/chat-tenho-uma-ideia.html`
> ADR: [[ADR-0002 Chat Agent Design]]

## O que é

Agente de chat especializado por tenant que permite ao cliente digitar livremente suas ideias de conteúdo. O agente conhece o nicho, tom de voz e arquétipo do tenant (via Soul.md + dossier) e extrai tema, ângulo e objetivo através da conversa. Quando tem contexto suficiente, sinaliza com `[READY]` — botão "Gerar posts" aparece.

Ao clicar, cria uma `content_idea` real no banco e dispara o motor de geração normal do Cadencia.

## Por que foi feito

[[Brief-Feature-Tenho-Uma-Ideia]] — Karina Vieira (agência, 8+ clientes) usa ChatGPT com prompts por cliente. Quer digitar livremente sem formulários. Comprou 3 contas Cadencia para substituir copywriters.

## Decisões-chave

| Decisão | Escolha |
|---|---|
| Soul.md | **Automático** via `provision_soul_md()` no onboarding (PDL-119). White-glove: endpoint `POST /api/v1/chat/regenerate-soul` |
| Sessão | Supabase JSONB (sem Redis) |
| Segurança RPC | `SECURITY INVOKER` (mudado de DEFINER — evita bypass de RLS multi-tenant) |
| Imports | Lazy imports para isolar `ModuleNotFoundError` |
| Feature flag | `flag_chat_ideas` em `tenant_config.config` — verificado em backend + frontend |
| Prompt | Processo obrigatório 5 passos (não instrução declarativa) — impede `[READY]` prematuro |
| max_tokens | 2000 (aumentado de 500 que causava truncamento) |

## Fluxo resumido

```
ChatIdeaSection.tsx
  → POST /api/v1/chat/session (workers Coolify VPS Master)
    → load_session_context() = Soul.md + dossier + editorias
    → INSERT chat_sessions → session_id + welcome
  → POST /api/v1/chat/message (SSE)
    → build_system_prompt() → LLM via OpenRouter
    → stream delta → [READY] quando tem contexto
  → POST /api/app/ideas/from-chat (Vercel)
    → INSERT content_ideas (pending, score=0.8)
    → drawer de geração normal
```

## Rollout

- Fase 1 (atual): flag `flag_chat_ideas` ativa por tenant (tenants da Karina)
- Fase 2: early access via admin para lista selecionada
- Fase 3: GA para todos após validação

## Limitações MVP

- Soul.md gerado automaticamente mas pode ser superficial se dossier incompleto — revisar (PDL-116)
- Memória inter-sessão não implementada — `get_relevant_memories()` retorna `[]` (PDL-111)
- Ideia cancelada antes de "Gerar posts" não vai ao swipe deck (sem reload)
- Prompt do chat em ajuste com base em uso real — PDL-116 aberta

## Issues abertas

- [[PDL-116]] — Revisão do prompt com conversas reais da Karina
- [[PDL-117]] — Soul.md do tenant felipeluissalgueiro
- [[PDL-118]] — Soul.md tenants da Karina (briefing 19/05)
- [[PDL-111]] — Memória semântica v2

## Arquivos principais

- `cadencia-workers/src/workers/chat_agent/session.py`
- `cadencia-workers/src/workers/chat_agent/memory.py`
- `cadencia-workers/src/api/routes/chat.py`
- `src/components/chat/ChatIdeaSection.tsx`
- `src/app/api/app/ideas/from-chat/route.ts`
- `src/hooks/useChatFeatureFlag.ts`
- `supabase/migrations/20260516000001_chat_agent_tables.sql`

## Notas Relacionadas
[[Readme]] - [[Brief]] - [[Chat-Tenho-Uma-Ideia]] - [[Editorias]]
