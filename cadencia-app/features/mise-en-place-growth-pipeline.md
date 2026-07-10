> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/features/mise-en-place-growth-pipeline.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/features/mise-en-place-growth-pipeline.md)
> Sincronizado via `sync_cadencia_docs.py` em 2026-05-29 (PDL-342).

---

# Mise en place — Growth Pipeline completo (CertaDoc demo 28/04)

**Data:** 2026-04-25
**Demo:** 2026-04-28 (Fabiano / CertaDoc)
**tenant_id CertaDoc:** `3cbbe352-8b4e-4195-ab61-10640f6a19b6`

---

## Estado atual do tenant_config (CertaDoc)

| Campo | Estado |
|---|---|
| `location_id` | `Ov0Pu1lmMAajPgBS2uei` ✅ |
| `blog.vercel_url` | `https://cadencia-blog-certadoc.vercel.app` ✅ |
| `seinfeld_workflow_id` | criado no GHL mas ID não salvo ❌ |
| `newsletter_workflow_id` | criado no GHL mas ID não salvo ❌ |
| `api_key` | ausente ❌ |
| `user_id` | ausente ❌ |
| `linkedin_account_id` | ausente ❌ |
| `pipeline_id` | não criado ❌ |
| `score_field_id` | ausente ❌ |

---

## PRÉ-VÔOO — Felipe faz antes de começar (manual no GHL)

Tudo que requer acesso ao painel GHL da sub-conta CertaDoc:

### PV-1 — Buscar API key da sub-conta CertaDoc
No GHL Agency > Settings > Locations > CertaDoc > API Key (ou Private Integrations).
Copiar a API key da **sub-conta** (location token, não o agency token).

### PV-2 — Buscar user_id do usuário da sub-conta
No GHL: Settings > My Staff > CertaDoc user > copiar o ID da URL ou via API:
`GET /users/search?locationId=Ov0Pu1lmMAajPgBS2uei`

### PV-3 — Pegar os IDs dos workflows criados
No GHL: Automation > Workflows > Seinfeld Daily + Newsletter Weekly.
Abrir cada um e copiar o ID da URL (formato: `workflow/{ID}`).

### PV-4 — Buscar linkedin_account_id
No GHL: Marketing > Social Planner > Accounts > LinkedIn conectado.
O `accountId` aparece na URL ou via:
`GET /social-media-posting/accounts?locationId=Ov0Pu1lmMAajPgBS2uei` (se existir)

### PV-5 — Criar pipeline de oportunidades no GHL
No GHL: CRM > Pipelines > Create Pipeline.
Nome: "Nutrição CertaDoc"
Stages: "Aquecendo" | "Quente" | "Hot DFY"
Salvar e copiar o pipeline_id da URL.

### PV-6 — Verificar/criar custom field score_ia no GHL
No GHL: Settings > Custom Fields > "score_ia" (tipo: Number).
Se não existir, criar. Copiar o field_id.

---

## BATCHES DE IMPLEMENTAÇÃO

### BATCH 0 — Salvar credenciais GHL no tenant_config (5 min)
**Depende de:** PV-1 a PV-6 concluídos
**Executor:** Claude (código)

Atualizar `tenant_config.config.ghl` no Supabase via REST API com todos os IDs coletados no pré-vôo.

```python
# Script a executar após Felipe fornecer os IDs
config_patch = {
    "ghl": {
        "api_key": "<PV-1>",
        "location_id": "Ov0Pu1lmMAajPgBS2uei",
        "user_id": "<PV-2>",
        "seinfeld_workflow_id": "<PV-3a>",
        "newsletter_workflow_id": "<PV-3b>",
        "linkedin_account_id": "<PV-4>",
        "pipeline_id": "<PV-5>",
        "score_field_id": "<PV-6>"
    }
}
```

**Verificação:** Re-ler o `tenant_config` e confirmar todos os campos preenchidos.

---

### BATCH 1 — Correções no pipeline VPS (30 min)
**Depende de:** BATCH 0
**Executor:** Claude (VPS via SSH)

**1.1 — `seinfeld_generate.py`: tratar HTTP 422 como sucesso**
```python
# Anti-duplicata: se contato já está no workflow → não é erro
if resp_code == 422:
    print(f"  INFO: contact {cid} already in workflow (422) — treating as success")
    ok += 1
    continue
```

**1.2 — `newsletter_generate.py`: anti-duplicata com last_newsletter_date**
```python
# Antes de enrolar: checar last_newsletter_date no contato
# Após enrolar com sucesso: gravar today no campo
# 422 → tratar como sucesso
```

**1.3 — Corrigir crontab newsletter: 15 UTC → 18 UTC (15h BRT)**
```bash
# Errado (atual):  0 15 * * 5
# Correto:         0 18 * * 5
```

**Verificação:** Rodar `seinfeld_generate.py <tenant_id> --dry-run` e confirmar que não quebra.

---

### BATCH 2 — Migration linkedin_scheduled_at (10 min)
**Depende de:** independente
**Executor:** Claude (Supabase Management API)

```sql
ALTER TABLE published_posts
  ADD COLUMN IF NOT EXISTS linkedin_scheduled_at timestamptz;
```

**Verificação:** Confirmar coluna no schema via REST API.

---

### BATCH 3 — linkedin_generate.py: agendamento automático (45 min)
**Depende de:** BATCH 0, BATCH 2
**Executor:** Claude (VPS via SSH)

Implementar `find_available_slot()`:
1. Âncora no banco (`linkedin_scheduled_at` mais recente do tenant)
2. Confirmar com GHL via `POST /social-media-posting/{locationId}/posts/list`
3. Avançar dia útil se slot ocupado (máx 7 tentativas)
4. Salvar `linkedin_scheduled_at` no banco junto com `linkedin_sent=true`
5. Passar `scheduleDate` no body GHL (status `"scheduled"`)

**Verificação:** Rodar `linkedin_generate.py <tenant_id> --dry-run` e confirmar `scheduleDate` calculada corretamente.

---

### BATCH 4 — Teste E2E (30 min)
**Depende de:** BATCH 0, 1, 2, 3
**Executor:** Felipe (manual) + Claude (monitoramento logs)

1. Login CertaDoc → `/app/ideas`
2. Aprovar ideia com todos os canais
3. Acompanhar logs VPS: trigger_server + blog_generate
4. Verificar `/app` → carrossel gerado ✅
5. Verificar `/app/growth/nutricao` → email pendente aparece (seinfeld_sent=false → conteúdo gerado)
6. Verificar `/app/growth/calendario` → linkedin agendado aparece
7. Aguardar próximo cron (11h BRT) ou rodar manualmente:
   `ssh root@72.60.4.71 "python3 /cadencia/pipeline/seinfeld_generate.py 3cbbe352-8b4e-4195-ab61-10640f6a19b6"`
8. Confirmar email enviado no GHL

---

### BATCH 5 — Carrossel → GHL Social Planner (60-90 min)
**Depende de:** BATCH 0
**Executor:** Claude (VPS + Railway)
**Prioridade:** pós-demo se apertar o tempo

Ao gerar carrossel, enviar PNGs automaticamente para o Social Planner do Instagram:

1. No orchestrator (Railway): após render, chamar `/api/v1/carrossel/schedule-social` passando `doc_id` + `tenant_id`
2. No endpoint: download PNGs do Supabase → upload para GHL Media Library (zero-fill nos nomes) → criar post com `accountIds=[instagram_account_id]`
3. `scheduleDate` via `find_available_slot()` reutilizando mesma lógica do LinkedIn

⚠️ Atenção: Railway (`cadencia-workers/src/`) é gerenciado por outro agente. Verificar antes de modificar.

---

### BATCH 6 — Lead scoring completo (pós-demo)
**Depende de:** BATCH 0
**Executor:** Claude

- Migration `scoring_events` no Supabase
- `webhook_handler.py`: adicionar endpoints `newsletter-aberta` e `newsletter-clicada`
- `webhook_handler.py`: `mover_pipeline` multi-tenant (buscar `pipeline_id` do `tenant_config`)
- `inatividade_job.py`: adaptar para multi-tenant

---

## ORDEM DE EXECUÇÃO RECOMENDADA

```
Felipe faz PV-1 a PV-6 (manual)
         │
         ▼
BATCH 0 — salvar credenciais (Claude, 5 min)
         │
    ┌────┴────┐
    ▼         ▼
BATCH 1    BATCH 2
(VPS fix)  (migration)
    │         │
    └────┬────┘
         ▼
      BATCH 3
  (linkedin agenda)
         │
         ▼
      BATCH 4
      (E2E test)
         │
         ▼
      BATCH 5 (se sobrar tempo antes da demo)
      BATCH 6 (pós-demo)
```

---

## CHECKLIST PRÉ-DEMO (28/04)

- [ ] PV-1 a PV-6 concluídos (Felipe)
- [ ] BATCH 0: tenant_config com todos os IDs GHL
- [ ] BATCH 1: 422 tratado, newsletter anti-duplicata, crontab 18h UTC
- [ ] BATCH 2: coluna `linkedin_scheduled_at` criada
- [ ] BATCH 3: `linkedin_generate.py` com agendamento automático
- [ ] BATCH 4: E2E testado — carrossel ✅, email gerado ✅, LinkedIn agendado ✅
- [ ] `growth_onboarding_shown` resetado para false (para demo mostrar o modal)
