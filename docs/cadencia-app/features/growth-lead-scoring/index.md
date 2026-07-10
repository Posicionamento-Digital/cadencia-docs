> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/features/growth-lead-scoring/index.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/features/growth-lead-scoring/index.md)
> Sincronizado via `sync_cadencia_docs.py` em 2026-05-29 (PDL-342).

---

# Feature: Growth Lead Scoring

Pontuação de comportamento de leads via webhook HTTP. Atualiza campo `score_ia` no contato GHL em tempo real.

**Status:** Produção — webhook rodando na VPS, eventos email_opened/link_clicked ativos
**Última atualização:** 2026-05-19
**Fonte:** `cadencia-growth/scoring/webhook_handler.py`

---

## Arquitetura

```
Fonte externa (pixel de rastreamento, automação GHL, etc.)
    │
    ▼
POST http://72.60.4.71:8766  (webhook_handler.py — VPS)
    │
    ├── Extrai locationId + contactId + type do payload
    ├── Busca tenant_config pelo location_id (multi-tenant)
    ├── Calcula delta via SCORE_MAP
    ├── GET /contacts/{id} → score atual
    ├── PUT /contacts/{id} → score + delta
    └── Retorna {ok, old_score, new_score}
```

**O scoring é inteiramente calculado pelo Cadencia.** O GHL é apenas o storage do campo numérico `score_ia`.

---

## Tabela de pontos (SCORE_MAP)

Definido no código — fonte de verdade:

| Evento (`type` no payload) | Delta |
|---|---|
| `email_opened` / `email_open` | +2 |
| `link_clicked` / `email_clicked` / `link_click` | +5 |

Score nunca fica negativo: `new_score = max(0, current + delta)`

---

## Payload esperado

```json
{
  "locationId": "<GHL location ID>",
  "contactId": "<GHL contact ID>",
  "type": "email_opened"
}
```

Aceita também `location_id` e `contact_id` (com underscore) como aliases.

**Respostas:**
```json
{"ok": true, "old_score": 10, "new_score": 12, "updated": true}
{"ok": true, "skip": "unknown event: <tipo>"}
{"ok": true, "skip": "tenant not found"}
{"ok": true, "skip": "no api_key"}
```

O handler sempre retorna HTTP 200 — erros são logados, nunca re-tentados.

---

## Multi-tenant: como o tenant é identificado

```python
def get_tenant_by_location(location_id):
    # Varre todos os tenant_config em busca do que tem ghl.location_id == location_id
    rows = sb_get('tenant_config?select=tenant_id,config')
    for row in rows:
        if row['config']['ghl']['location_id'] == location_id:
            return row['tenant_id'], row['config']
```

O campo `ghl.location_id` no `tenant_config` é a chave de roteamento. Cada sub-conta GHL mapeia para exatamente um tenant Cadencia.

---

## Armazenamento no GHL

Campo customizado numérico no contato:
- **Key:** `contact.score_ia` (padrão — configurável em `ghl.score_ia_field_key`)
- **Tipo no GHL:** `NUMERICAL`
- **Leitura:** `GET /contacts/{id}` → `customFields[]` onde `key == field_key`
- **Escrita:** `PUT /contacts/{id}` com `customFields: [{key, field_value: str(score)}]`

> Importante: `GET /contacts/?locationId=...` (listagem) retorna `customFields: []` vazio. O score real só está disponível no GET individual por contato.

---

## Configuração por tenant (`tenant_config.ghl`)

Campos necessários para o scoring funcionar:

```json
{
  "ghl": {
    "location_id": "...",
    "location_pit_token": "pit-...",
    "score_ia_field_key": "contact.score_ia",
    "score_field_id": "<ID do campo no GHL>",
    "pipeline_id": "...",
    "stage_frio_id": "...",
    "stage_aquecendo_id": "...",
    "stage_quente_id": "...",
    "stage_hot_id": "..."
  }
}
```

> O `score_field_id` e o pipeline/stages não são usados pelo `webhook_handler.py` atual — são referência para futuras implementações de pipeline movement.

---

## Servidor

```python
HTTPServer(('0.0.0.0', PORT), WebhookHandler)
# PORT = WEBHOOK_PORT env var, default 8766
```

**Processo:** `systemd` via `cadencia-webhook.service`
**Logs:** stdout redirecionado para `/cadencia/logs/scoring.log`

Verificar se está rodando:
```bash
curl http://72.60.4.71:8766
# {"status": "ok", "port": 8766}
```

---

## 🚫 Don'ts

- Nunca usar `api_key` no config sem `location_pit_token` — o script lê `location_pit_token`
- Nunca assumir que o score vai ser atualizado se o campo `score_ia` não existir na sub-conta GHL — criar o campo antes de ativar o webhook
- Nunca expor a porta 8766 sem verificar autenticação — atualmente sem auth, qualquer IP pode enviar score

---

## Pendências

- [ ] Autenticação no webhook (token compartilhado no header)
- [ ] Pipeline movement: mover contato entre stages (Frio → Aquecendo → Quente → Hot) quando score cruzar thresholds
- [ ] Paginação no `get_tenant_by_location` — hoje varre todos os tenants a cada request
- [ ] Endpoints para eventos newsletter (`newsletter_aberta`, `newsletter_clicada`)
- [ ] `inatividade_job.py` adaptado para multi-tenant (decay de -10 após 30 dias sem atividade)
- [ ] Tabela `scoring_events` no Supabase para auditoria
- [ ] Auto-provisioning do campo `score_ia` ao ativar Growth para novo tenant

---

## Comparativo Cadencia vs PD Marketing

| Aspecto | PD Marketing | Cadencia atual |
|---|---|---|
| Roteamento de eventos | Por path da URL (`/email-aberto`, `/link-clicado`) | Por campo `type` no payload JSON |
| Eventos suportados | 8+ (email, newsletter, WhatsApp, SOAP) | 2 (email_opened, link_clicked) |
| Pipeline movement | Automático ao cruzar threshold | Não implementado ainda |
| `scoring_events` auditoria | Tabela Supabase preenchida | Não implementado ainda |
| Inatividade (decay) | `inatividade_job.py` diário | Não portado ainda |
| Identificação de tenant | IDs fixos no .env | `location_id` no `tenant_config` (multi-tenant) |
