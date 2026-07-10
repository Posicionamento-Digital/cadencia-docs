> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `src/app/(onboarding)/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/src/app/(onboarding)/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# frontend-onboarding — fluxo de onboarding

## TL;DR

Fluxo linear multi-fase que coleta perfil do tenant e dispara geração de dossier/identidade/editoriais. 3 fases principais com 7 sub-passos.

## Identidade

- **Tipo:** Next.js 15 App Router
- **Path:** `src/app/(onboarding)/`
- **Status:** ativo
- **Deps:** Workers Railway (onboarding endpoints), Supabase (`tenant_onboarding`)

## Estrutura de fases

| Fase | API | O que coleta |
|---|---|---|
| Fase 1 | `POST /api/onboarding/phase1` | Dados básicos: nome, nicho, profissão, sobre |
| Fase 1.5 | `POST /api/onboarding/phase1p5` | Big5 (personalidade) + DPR signaling |
| Fase 2 | `POST /api/onboarding/phase2` | Dispara dossier + identidade visual (workers) |
| Fase 3 | `POST /api/onboarding/phase3` | Confirma editoriais, finaliza onboarding |
| Progressive | `POST /api/onboarding/progressive` | Coleta incremental sem bloquear acesso ao app |
| Adjust | `POST /api/onboarding/adjust-feedback` | Feedback do usuário sobre dossier gerado |
| Instagram | `POST /api/onboarding/instagram-analysis` | Análise do perfil Instagram via Apify |

## Após completar

- `tenant_onboarding.current_phase = 3`
- Redireciona para `/app/preparing` (polling até 5 ideias prontas)
- Workers geram: dossier → visual-identity → editorials → ideas (5 iniciais)

## Don'ts

- Não bloquear acesso ao app se fase 3 incompleta — `progressive` permite coleta incremental
- `instagram-analysis` via Apify tem custo — não disparar mais de 1x por tenant sem necessidade

---

## Quando usar

- Signup novo tenant → fluxo onboarding (fases 1, 1.5, 2, 3).
- Coleta progressive incremental — completa perfil sem bloquear app.
- Análise Instagram via Apify durante fase 1.5/2.

## Quando NÃO usar

- ❌ Após fase 3 completa — refletir mudanças via `/app/profile`, não onboarding.
- ❌ Para re-rodar análise Instagram sem necessidade — Apify tem custo.
- ❌ Bypass de fases — pipeline diário espera `onboarding_completed=true` (mas G005 ignora — gera mesmo assim).

## Por que funciona assim

- Fases lineares (não wizard reversível) — força decisão antes de avançar; permite resumir progresso.
- Progressive coleta — não bloqueia uso do app antes de completar 100%.
- Workers desacoplados (dossier, visual_identity, editorials) — falha em um não derruba o resto.

## 🚫 Don'ts

- **Não** disparar `instagram-analysis` em loop — custo Apify acumula.
- **Não** atualizar `current_phase` pulando — mantém consistência com workers que rodam após.
- **Não** confiar em `tenant_dossier` sem ter passado por `dossier.py` — pode estar vazio.

## 🪦 Já tentamos

- **2026-04-23 — Stale closure dossier confirm/approve**: ver incident.
- **2026-04-23 — Stale ref onboarding answers snapshot**: ver incident.
- **2026-04-23 — Visual identity prompt sem acentos**: ver incident.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Stuck em fase 2 sem dossier | Worker falhou silencioso | Logar resposta + retry endpoint |
| Apify retorna conta privada | Esperado — tratar com fallback genérico | UI mostra mensagem clara |
| Editoriais vazios após fase 3 | `editorials.py` falhou | Retry `POST /api/v1/onboarding/editorials` |
| Fase progressive não persiste | Conflito com fase principal | Reconciliar `current_phase` |

## 📚 Referências cruzadas

- [onboarding-workers](../../../cadencia-workers/src/workers/onboarding/CLAUDE.md)
- [api-routes](../../../api/CLAUDE.md) — Endpoints `/api/onboarding/*`
- [CONTEXT.md](../../../../CONTEXT.md) — Onboarding, Dossier, Editorial
