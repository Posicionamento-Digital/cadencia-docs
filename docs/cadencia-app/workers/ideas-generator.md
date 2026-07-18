> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `cadencia-workers/src/workers/ideas/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-workers/src/workers/ideas/CLAUDE.md)
> Sincronizar via `/documentar-software` ou `sync_to_framework.py`.

---

# ideas-generator — geração de ideias de conteúdo

## TL;DR

Gera ideias de conteúdo para o tenant baseado em editoriais, dossier e histórico de posts. Entry point: `POST /api/v1/ideas`.

## Identidade

- **Tipo:** Worker Python
- **Stack:** FastAPI + OpenAI
- **Path:** `cadencia-workers/src/workers/ideas.py`
- **Status:** ativo
- **Deps:** `content_ideas`, `editorials`, `tenant_dossier`, `published_posts` (histórico)

## Como funciona

1. Carrega editoriais do tenant (3 editoriais com pesos 0.40/0.35/0.25)
2. Carrega dossier para contexto de marca
3. Verifica histórico de posts recentes (evita repetição de temas)
4. Gera N ideias via LLM distribuídas pelos pesos dos editoriais
5. Salva em `content_ideas` com `status=pending`

## Trigger

- Onboarding (pós-editorials): gera 5 ideias iniciais automaticamente
- On-demand: frontend chama `POST /api/v1/ideas/generate`
- Admin: pode forçar regeneração por tenant

## Don'ts

- Nunca gerar ideias sem editoriais confirmados — resultado vira lixo sem contexto de marca

---

## Quando usar

- Geração automática de ideias para o tenant (fora do chat).
- Catch-up: tenant ficou sem ideias para aprovar e precisa de batch novo.
- Programado: cron interno gera N ideias por semana com base em editoriais.

## Quando NÃO usar

- ❌ Para entrada conversacional — usar `chat-ideias`.
- ❌ Para tenant sem dossier/editoriais — sem contexto, ideias genéricas.
- ❌ Para gerar conteúdo final — apenas ideias (insumo do pipeline).

## Por que funciona assim

- Separado do `chat-ideias`: chat é entrada UX-driven (usuário inicia); generator é cadência programada.
- Ideias respeitam pesos editoriais `[0.40, 0.35, 0.25]` — distribuição refletida no calendário do tenant.

## 🚫 Don'ts

- **Não** gerar ideia duplicada — verificar histórico `content_ideas` antes.
- **Não** ignorar `editorial_id` no insert — pipeline falha sem isso.
- **Não** rodar batch grande sem rate limit OpenAI.

## 🪦 Já tentamos

- Geração sem variação editorial → tenant via 80% das ideias do mesmo pilar. Fix: forçar distribuição pelos pesos.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Ideias muito similares | Histórico não consultado | Adicionar passagem de últimas N ideias no prompt |
| Distribuição editorial errada | Pesos ignorados | Validar lógica de sampling por peso |
| Ideia sem `editorial_id` | Bug no insert | Schema enforce + retry |

## 📚 Referências cruzadas

- [chat-ideias](../chat-ideias/CLAUDE.md) — Alternativa interativa
- [pipeline-orchestrator](../CLAUDE.md) — Consome a ideia aprovada
- [onboarding-workers](../onboarding/CLAUDE.md) — Define editoriais
