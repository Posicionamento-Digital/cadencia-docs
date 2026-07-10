> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `cadencia-workers/src/workers/onboarding/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-workers/src/workers/onboarding/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# onboarding-workers — dossier, identidade visual, editoriais

## TL;DR

3 workers independentes executados em sequência pelo fluxo de onboarding (fases 2-3). Cada um tem endpoint próprio em `/api/v1/onboarding/`.

## Identidade

- **Tipo:** Workers Python
- **Stack:** FastAPI + OpenAI (via OpenRouter)
- **Paths:**
  - `cadencia-workers/src/workers/dossier.py` → `POST /api/v1/onboarding/dossier`
  - `cadencia-workers/src/workers/visual_identity.py` → `POST /api/v1/onboarding/visual-identity`
  - `cadencia-workers/src/workers/editorials.py` → `POST /api/v1/onboarding/editorials`
- **Status:** ativo
- **Deps:** `tenant_config`, `tenant_dossier`, `editorials`, `tenant_themes`, `profile_responses`

## Dossier (`dossier.py`)

- Gera brand dossier completo via LLM baseado no perfil do tenant (Big5, signaling, nicho, profissão)
- Salva em tabela `tenant_dossier`
- Após gerar: chama `chat_agent.provision_soul_md` para criar SOUL_TEMPLATE do tenant
- Endpoint regenera seção específica: `POST /dossier/section` com feedback do usuário

## Identidade visual (`visual_identity.py`)

- Consulta `style_configs` cruzando Big5 + DPR signaling do tenant
- Retorna 3 opções de sub-preset para o usuário escolher
- Endpoint choice: `POST /sub-preset-choice` — salva `preferred_sub_preset` em `tenant_config`
- Gera capa de cover com identidade visual usando Gemini 2.5 Flash (Identity Lock)

## Editoriais (`editorials.py`)

- Gera 3 editoriais complementares com pesos no calendário: `[0.40, 0.35, 0.25]`
- Cada editorial tem `editorial_type`, `function`, `brand_voice`, `content_pillars`
- Endpoint regenera editorial individual: `POST /editorial` com feedback

## Fluxo de onboarding completo

```
Fase 1 (frontend) → perfil básico (Big5 + signaling)
  ↓
Fase 2: dossier → visual-identity → sub-preset-choice → editorials
  ↓
Fase 3: validação → conclusão → redirect /app/preparing (polling 5 ideias)
```

## Don'ts

- Pesos de editorial são fixos — não alterar sem decisão de produto
- `provision_soul_md` é chamado automaticamente pelo dossier — não chamar separado

---

## Quando usar

- Fase 2-3 do onboarding novo tenant. Dispara automaticamente após fase 1 concluída.
- Regerar seção do dossier com feedback: `POST /dossier/section`.
- Regerar editorial individual: `POST /editorial`.
- Trocar sub-preset durante onboarding (antes da fase 3 concluir): `POST /sub-preset-choice`.

## Quando NÃO usar

- ❌ Tenant já onboardado — não chamar `dossier.py` para sobrescrever. Editar campos manualmente no `tenant_dossier` se precisar.
- ❌ Pular `dossier.py` antes de `editorials.py` — editoriais dependem do dossier.
- ❌ Para tenant em fase 1 — perfil básico ainda vazio (`profile_responses` incompleto).

## Por que funciona assim

- 3 workers separados (não 1 monolito) — cada um pode ser regerado isoladamente sem refazer todo o onboarding.
- Pesos editoriais fixos `[0.40, 0.35, 0.25]` — decisão de produto baseada em equilíbrio "core / suporte / surpresa". Mudança exige decisão Catarina (PM).
- `provision_soul_md` chamado automaticamente dentro do dossier — SOUL.md é derivado do dossier, não input independente.

## 🚫 Don'ts

- **Não** alterar pesos editoriais sem decisão de produto.
- **Não** chamar `provision_soul_md` separado do `dossier.py` — sempre encadeado.
- **Não** gerar identidade visual antes do dossier — sub-preset depende do perfil completo.
- **Não** usar Gemini Identity Lock para cover sem foto rosto válida — falha silenciosa.

## 🪦 Já tentamos

- **2026-04-23 — Stale closure no dossier confirm/approve**: state do frontend não atualizava ao aprovar seção. Ver `2026-04-23_stale-closure-dossier-confirm-approve.md`.
- **2026-04-23 — Stale ref answers snapshot**: respostas do onboarding antigas vazavam para nova geração. Ver `2026-04-23_stale-ref-onboarding-answers-snapshot.md`.
- **2026-04-23 — Visual identity prompt sem acentos**: ver incident.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Dossier gerado vazio/genérico | `profile_responses` da fase 1 incompletas | Validar fase 1 antes de chamar `/dossier` |
| 3 editoriais retornam similares | Dossier muito genérico | Regenerar dossier com mais contexto, depois editoriais |
| Sub-preset não aplica | `preferred_sub_preset` não salvou em `tenant_config` | Verificar resposta de `/sub-preset-choice` — se 200 mas tenant_config não atualizou, problema de RLS |
| Cover Identity Lock falha | Foto rosto inválida/ausente | Aceitar capa temática como fallback |
| `provision_soul_md` não cria SOUL | Erro silencioso na chamada interna | Logar resposta + reexecutar via `POST /dossier` regen |

## 📚 Referências cruzadas

- [chat-ideias](../chat-ideias/CLAUDE.md) — Consome `SOUL.md` gerado por `provision_soul_md`
- [pipeline-orchestrator](../CLAUDE.md) — Depende de dossier + editoriais
- [theme-engine](../theme-engine/CLAUDE.md) — Aplica sub-preset escolhido
- [CONTEXT.md](../../../../CONTEXT.md) — Dossier, Editorial, Onboarding, Sub-preset
