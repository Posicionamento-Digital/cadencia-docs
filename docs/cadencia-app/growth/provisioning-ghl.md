> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`Posicionamento-Digital/cadencia-growth` / `main` / `docs/provisioning-ghl.md`](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/provisioning-ghl.md)
> Sincronizar via `/documentar-software` ou `sync_to_framework.py`.

---

# provisioning-ghl — provisionamento de tenant GHL

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória e auditoria. Não executar este runbook nem usar seu conteúdo como arquitetura atual.

## TL;DR

Cria subconta GHL para novo tenant, configura campos customizados, pipeline de oportunidades e salva tokens em `tenant_config`. É o script mais crítico do onboarding.

## Identidade

- **Tipo:** Python script (2 cópias: canonical em `/cadencia/provision_tenant.py`, chamada em `/cadencia/pipeline/provision_tenant.py`)
- **Paths (VPS):** `/cadencia/provision_tenant.py` (canonical) — idêntico a `pipeline/provision_tenant.py`
- **Status:** ativo — com bloqueio PDL-25 (ghl_agency_oauth vazia)
- **Deps:** GHL Agency PIT, `ghl_agency_oauth` table, `tenant_config`

## Fluxo completo

1. Signup usuário → `POST /api/auth/provision-tenant` (Vercel)
   → cria `tenants` + `users` + `user_tenant_roles` + `tenant_onboarding` + `tenant_plans`
2. Fire-and-forget: `POST /api/v1/ghl/signup` (workers Coolify VPS Master)
   → cria contato GHL na location central + oportunidade em trial
3. `provision_tenant.py` na VPS (chamado por trigger `/provision`):
   - `_get_oauth_agency_token()` — lê de `ghl_agency_oauth` (PDL-25: tabela vazia = bloqueado)
   - Fallback: `GHL_API_KEY` estático se OAuth falhar
   - `create_ghl_subconta()` — cria location via agency PIT + snapshot
   - `_find_custom_field()` + `_find_pipeline()` — auto-descoberta via snapshot
   - `create_ghl_user()` — cria usuário na subconta
   - `seed_example_scoring()` — cria contato exemplo para testar scoring
   - Salva `config.ghl.location_id` e `config.ghl.location_pit_token` em `tenant_config`

## Bloqueio ativo (PDL-25)

`ghl_agency_oauth` está vazia — `location_pit_token` não é salvo automaticamente. Subconta é criada mas sem token por tenant. Contorno: injetar `location_pit_token` manualmente em `tenant_config` para cada tenant.

## Don'ts

- `pipeline/provision_tenant.py` deve ser idêntico ao root canonical — nunca divergir
- Não alterar `GHL_PIPELINE_ID` (location central) — é fixo
- OAuth agency: só há 1 registro válido em `ghl_agency_oauth` — não criar duplicata

---

## Quando usar

- **Provisioning automático** disparado ao tenant completar fase 1 do onboarding.
- **Retry** via `retry_provisioning.py` (cron 10h55 BRT) para tenants com `provisioning_status='failed'` e `attempts<3`.

## Quando NÃO usar

- ❌ Sem `ghl_agency_oauth` válido — bloqueio PDL-25. Hoje vazio.
- ❌ Para tenant já provisionado (`config.ghl.location_id` já preenchido).
- ❌ Manualmente sem coordenar com onboarding-workers (que dependem de location_pit_token salvo).

## Por que funciona assim

- [ADR-0005](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0005-location-pit-token-por-tenant.md) — `location_pit_token` por tenant.
- Cria subconta via agency PIT + snapshot pré-configurado (workflows, pipelines, custom fields).
- `POST /oauth/locationToken` gera token específico da location → salva em `tenant_config.config.ghl.location_pit_token`.

## 🚫 Don'ts

- **Não** rodar sem agency OAuth completo (PDL-25 bloqueia).
- **Não** sobrescrever `location_pit_token` existente sem revogar o anterior.
- **Não** criar subconta sem snapshot — workflows/scoring não funcionam.

## 🪦 Já tentamos

- PDL-25 bloqueia provisioning desde início — `ghl_agency_oauth` vazio. Workaround: provisioning manual via `/cadencia-provisionar-tenant` skill.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| `POST /oauth/locationToken` 401 | `ghl_agency_oauth` vazio (PDL-25) | Completar OAuth Marketplace |
| Subconta criada sem workflows | Snapshot errado | Verificar snapshot_id na chamada |
| `location_pit_token` não salvou | Erro silencioso em `tenant_config` update | Logar resposta + retry via `retry_provisioning.py` |
| Provisioning loop | `attempts>=3` ainda tentando | Auditar `attempts` field + reset manual se justificado |

## 📚 Referências cruzadas

- [scoring-leads](scoring-leads.md) — Configura `score_ia_field_key` e `pipeline_stages`
- [seinfeld-email](seinfeld-email.md) — Requer `location_pit_token` salvo aqui
- Skill `/cadencia-provisionar-tenant` — Workaround manual
