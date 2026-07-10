> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/features/growth-email-dispatch/index.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/features/growth-email-dispatch/index.md)
> Sincronizado via `sync_cadencia_docs.py` em 2026-05-29 (PDL-342).

---

# Feature: Growth — Email Dispatch (Seinfeld + Newsletter)

Pipeline completo de geração e envio de emails para tenants Growth via GHL.

**Status:** Produção — Seinfeld e Newsletter funcionais
**Última atualização:** 2026-05-19
**Fontes:** `cadencia-growth/pipeline/seinfeld_generate.py`, `newsletter_generate.py`

---

## Visão geral

```
Aprovação de ideia (frontend)
        │
        ▼
POST /api/app/trigger-generation (Next.js)
        │
        ▼
trigger_server.py (VPS :8767)
        │
        ├── blog_generate.py        → published_post no Supabase
        ├── seinfeld_generate.py    → gera email Seinfeld, agenda (não dispara)
        └── linkedin_generate.py   → agenda no Social Planner GHL

Crons VPS:
  11h BRT (14h UTC) diário  → seinfeld_generate.py --dispatch
  15h BRT (18h UTC) sexta   → newsletter_generate.py
  11h30 BRT (14h30 UTC) seg-sex → linkedin_generate.py
```

---

## Scripts e responsabilidades

| Script | Modo | Gatilho |
|---|---|---|
| `trigger_server.py` (porta 8767) | Servidor HTTP permanente | POST /trigger da API Next.js |
| `blog_generate.py` | On-demand | Aprovação de ideia |
| `seinfeld_generate.py --generate` | On-demand | Aprovação de ideia |
| `seinfeld_generate.py --dispatch` | Cron 11h BRT | Diário |
| `newsletter_generate.py` | Cron 15h BRT sexta | Semanal |
| `linkedin_generate.py` | Cron 11h30 BRT seg-sex | Dias úteis |
| `growth_pipeline.py` | Orchestrator multi-tenant | Chamado pelos crons |

---

## Credencial GHL — campo crítico

Ambos os scripts buscam `ghl.location_pit_token` no `tenant_config`. **Não `api_key`.**

Para tenants white-glove que usam `api_key`, gravar também `location_pit_token`:

```json
{
  "ghl": {
    "location_id": "...",
    "api_key": "pit-...",
    "location_pit_token": "pit-..."
  },
  "nome_empresa": "Nome da Marca"
}
```

Sem `location_pit_token`, todas as chamadas GHL retornam HTTP 401 silenciosamente.

---

## Fluxo Seinfeld (diário)

**Fase 1 — Geração (on-demand):**
1. Valida `location_id` no config
2. Verifica contatos no GHL antes do LLM (evita custo se sub-conta vazia)
3. Busca próximo `published_post` sem Seinfeld agendado (FIFO por `published_at`)
4. Gera `{subject, preheader, body}` via `gpt-5.4`
5. Calcula próximo slot livre (1 email/dia, sem colisão)
6. Salva no banco — **não dispara**

**Fase 2 — Dispatch (cron 11h BRT):**
1. Busca posts com `seinfeld_scheduled_at = hoje` e `seinfeld_sent=false`
2. Renderiza HTML com visual identity do tenant
3. Busca contatos GHL (`GET /contacts/?locationId=...&limit=100`)
4. Por contato: `get_or_create_conversation()` → `POST /conversations/messages`
5. Marca `seinfeld_sent=true`

**Por que não GHL workflow:** workflows não aceitam HTML customizado — executam apenas templates internos do GHL.

---

## Fluxo Newsletter (sexta 15h BRT)

1. Busca **todos** `published_posts` com `newsletter_included=false` (sem filtro de data)
2. Verifica contatos no GHL antes do LLM
3. Gera newsletter via `gpt-5.4` → JSON `{subject, preheader, intro, posts[], closing}`
4. Renderiza HTML via `render_newsletter_html()` com visual identity
5. Envia para todos os contatos via `POST /conversations/messages`
6. Marca `newsletter_included=true` nos posts **somente se enviou para ao menos 1 contato**

**Sem filtro de data intencional:** se o cron falhar e rodar no sábado, posts antigos ainda entram. `newsletter_included=true` é o único controle de deduplicação.

---

## Banco de dados

### `published_posts` — campos de dispatch

| Coluna | Tipo | Controlado por |
|---|---|---|
| `seinfeld_sent` | boolean DEFAULT false | seinfeld_generate.py |
| `seinfeld_subject` | text | seinfeld_generate.py |
| `seinfeld_body` | text | seinfeld_generate.py |
| `seinfeld_scheduled_at` | timestamptz | seinfeld_generate.py |
| `newsletter_included` | boolean DEFAULT false | newsletter_generate.py |

### `generation_queue` — canais disponíveis

```sql
channels text[]  -- ['blog', 'seinfeld', 'newsletter', 'linkedin', 'instagram']
```

---

## Infraestrutura VPS

| Porta | Script | Processo |
|---|---|---|
| 8766 | `scoring/webhook_handler.py` | systemd `cadencia-webhook.service` |
| 8767 | `pipeline/trigger_server.py` | `@reboot` no crontab |

### Crontab

```cron
# Seinfeld + Blog — 11h BRT (14h UTC), diário
0 14 * * * /usr/bin/python3 /cadencia/crons/growth_pipeline.py blog seinfeld

# Newsletter — 15h BRT (18h UTC), sexta
0 18 * * 5 /usr/bin/python3 /cadencia/crons/growth_pipeline.py newsletter

# LinkedIn — 11h30 BRT (14h30 UTC), dias úteis
30 14 * * 1-5 /usr/bin/python3 /cadencia/crons/growth_pipeline.py linkedin

# Trigger server — sobe no reboot
@reboot nohup python3 /cadencia/pipeline/trigger_server.py >> /cadencia/logs/trigger.log 2>&1 &
```

---

## API Next.js

### `POST /api/app/trigger-generation`
Autentica → `tenant_id` → filtra canais (exclui `carrossel`, `reels`) → chama VPS :8767

### `POST /api/app/generation-queue`
Insere `generation_queue` com canais selecionados para a ideia aprovada

---

## 🚫 Don'ts

- Nunca usar `api_key` no config sem também gravar `location_pit_token`
- Nunca usar GHL workflows para envio de email — não passam HTML
- Nunca marcar `newsletter_included=true` antes de confirmar envio bem-sucedido
- Nunca chamar LLM sem verificar contatos GHL primeiro

---

## Limitações conhecidas

| Limitação | Impacto |
|---|---|
| `limit=100` sem paginação | Tenants com >100 contatos recebem email parcial |
| Sem rastreamento de abertura | Score de lead não atualiza automaticamente |
| 1 email/dia por tenant (Seinfeld) | Todos contatos recebem no mesmo dia, não por segmento |
| `firstName` depende de dados no GHL | Contatos sem nome recebem saudação genérica |
