> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `cadencia-workers/src/workers/rag-memory/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-workers/src/workers/rag-memory/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# rag-memory — RAG, memória de agente e refresh de tokens

## TL;DR

3 módulos de suporte ao pipeline de geração: RAG (contexto vetorial), memória persistente de agente e refresh de tokens OAuth.

## Identidade

- **Tipo:** Workers Python de suporte
- **Paths:**
  - `cadencia-workers/src/workers/rag.py` — retrieval augmented generation
  - `cadencia-workers/src/workers/agent_memory.py` — memória cross-session por agente
  - `cadencia-workers/src/workers/token_refresh.py` — refresh OAuth tokens
- **Status:** ativo
- **Deps:** Supabase (pgvector para embeddings), `tenant_config` (tokens)

## RAG (`rag.py`)

Fornece contexto de posts anteriores ao `research_agent` para evitar repetição e manter consistência de marca. Usa `pgvector` no Supabase para busca por similaridade semântica.

## Agent Memory (`agent_memory.py`)

Armazena padrões de geração bem-sucedidos por tenant. Usado pelo `headline_agent` e `carousel_agent` para aprender preferências ao longo do tempo.

## Token Refresh (`token_refresh.py`)

Renova `instagram_access_token` e outros tokens OAuth antes de expirar. Chamado proativamente pelo pipeline antes de publicar.

---

## Quando usar

- Worker que precisa de contexto histórico do tenant: últimos posts, conversas chat, dossier.
- Refresh de token periódico em integrações (`token_refresh.py`).

## Quando NÃO usar

- ❌ Como substituto do dossier — RAG complementa, não substitui.
- ❌ Para dados de outro tenant — RLS deve filtrar; service_role exige cuidado.
- ❌ Sem cache — chamadas repetidas degradam performance.

## Por que funciona assim

- Memória vetorial isolada por tenant — evita "cross-talk" entre marcas.
- `token_refresh.py` separado por integração — falha em uma não derruba o resto.

## 🚫 Don'ts

- **Não** indexar conteúdo de outro tenant no namespace errado.
- **Não** logar embeddings em texto claro — dados de marca confidenciais.
- **Não** ignorar TTL de refresh — tokens GHL expiram silenciosamente.

## 🪦 Já tentamos

- **2026-04-18 — Stevo API key expirou silenciosamente**: padrão de falha silenciosa em refresh. Ver `2026-04-18_stevo-api-key-expirou-silenciosamente.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Worker usando dados de outro tenant | Namespace errado no query | Auditar filtro `tenant_id` no RAG query |
| Refresh de token não roda | Cron parado | Verificar agendamento `token_refresh.py` |
| Resposta com contexto antigo | Cache não invalidou após novo post | Forçar reindex após publish |

## 📚 Referências cruzadas

- [chat-ideias](../chat-ideias/CLAUDE.md) — Consumidor de memória
- [onboarding-workers](../onboarding/CLAUDE.md) — Fonte de dossier
- [CONTEXT.md](../../../../CONTEXT.md) — RAG memory, Token PIT, Token agency OAuth
