# GHL API — Referência técnica verificada

> **ARQUIVO HISTORICO / LEGADO.** Preservado como memoria tecnica; nao descreve o runtime atual e nao deve ser usado como runbook operacional.

Base URL: `https://services.leadconnectorhq.com`
API Version header: `Version: 2021-07-28`

**Fontes:**
- 📄 = documentação oficial (github.com/GoHighLevel/highlevel-api-docs + marketplace.gohighlevel.com)
- ✅ = verificado em código de produção (PD Marketing ou Cadencia)
- ⚠️ = divergência ou inferência

> **Gotcha global:** `urllib`/`requests` Python são bloqueados pelo Cloudflare TLS fingerprint.
> Obrigatório usar `subprocess + curl` com `User-Agent` de navegador real.
> Ver: `C:\Users\felip\.claude\scripts\ghl_http.py`

---

## Headers obrigatórios em todos os requests

```
Authorization: Bearer {api_key}
Version: 2021-07-28
Content-Type: application/json      ← exceto upload de mídia (multipart)
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

---

## Contacts

### Listar contatos
```
GET /contacts/?locationId={id}&limit=100
```
✅ Paginação via `startAfter` (timestamp) + `startAfterId` (ID) do campo `meta` da resposta.
✅ **Retorna `customFields: []` vazio** — custom fields requerem GET individual.

### Buscar contato individual
```
GET /contacts/{contactId}
```
✅ Retorna `customFields` preenchidos.

### Criar contato
```
POST /contacts/
```
📄 Body obrigatório:
```json
{ "locationId": "...", "name": "...", "email": "..." }
```
📄 Resposta: `{ "contact": { "id": "..." } }`

### Atualizar contato / custom fields
```
PUT /contacts/{contactId}
```
```json
{
  "locationId": "...",
  "customFields": [
    { "id": "FIELD_ID", "value": "valor" }
  ]
}
```
⚠️ Alternativa também aceita (usada no código): `{ "key": "field_key", "field_value": "valor" }` — `field_value` deve ser string.

### Adicionar tags
```
POST /contacts/{contactId}/tags
```
```json
{ "tags": ["tag-1", "tag-2"] }
```

### Buscar por email (duplicidade)
```
GET /contacts/search/duplicate?locationId={id}&email={email}
```

### Listar custom fields do location
```
GET /locations/{locationId}/customFields
```
📄 Resposta: `{ "customFields": [{ "id", "name", "fieldKey" }] }`

---

## Workflows

### Enrolar contato em workflow
```
POST /contacts/{contactId}/workflow/{workflowId}
```
📄 Body: `{}` (todos os campos opcionais)
```json
{ "eventStartTime": "2026-04-28T10:00:00-03:00" }  // opcional
```
📄 Resposta sucesso:
```json
{ "succeded": true }
```
⚠️ Typo oficial no spec: `"succeded"` (um `e`), não `"succeeded"`.

📄 HTTP 422 = contato já está no workflow.
✅ **Tratar 422 como sucesso** (idempotente) — não é erro.

📄 Scope: `contacts.write`

### Listar workflows
```
GET /workflows/?locationId={id}
```

---

## Opportunities

### Buscar por contato
```
GET /opportunities/search?location_id={id}&pipeline_id={id}&contact_id={id}
```
✅ Usado para checar se oportunidade já existe antes de criar.

### Criar oportunidade
```
POST /opportunities/
```
📄 Body:
```json
{
  "locationId": "...",
  "pipelineId": "...",
  "pipelineStageId": "...",
  "contactId": "...",
  "name": "...",
  "status": "open"
}
```
📄 Resposta: `{ "opportunity": { "id": "..." } }`

### Mover stage
```
PUT /opportunities/{opportunityId}
```
```json
{ "pipelineStageId": "..." }
```

---

## Social Media Posting

### Upload de mídia
```
POST /medias/upload-file
```
📄 Formato: `multipart/form-data`
📄 Campos:
```
file=@{arquivo}     obrigatório se hosted=false
hosted=false        true = URL remota, false = arquivo local
fileUrl=...         obrigatório se hosted=true
name=...            opcional
```
⚠️ **Divergência:** Doc oficial usa `file`, código PD usa `fileMedia`. Testar antes de implementar.

📄 Limites: 25 MB imagens, 500 MB vídeo.
✅ Timeout recomendado: 120s (30s dá timeout).
✅ `Content-Type` NÃO enviado — curl define automaticamente com `-F`.
📄 Scope: `medias.write`

📄 Resposta:
```json
{ "fileId": "...", "url": "https://storage.googleapis.com/..." }
```

### Criar post
```
POST /social-media-posting/{locationId}/posts
```
📄 Body (`CreatePostDTO`):
```json
{
  "accountIds": ["<account_id>"],
  "type": "post",
  "userId": "...",
  "summary": "legenda do post",
  "media": [
    { "url": "https://...", "type": "image/png" }
  ],
  "status": "scheduled",
  "scheduleDate": "2026-04-28T13:00:00Z"
}
```

| Campo | Doc | Prática |
|---|---|---|
| `accountIds` | obrigatório | obrigatório |
| `type` | obrigatório | `"post"`, `"story"`, `"reel"` |
| `userId` | obrigatório | obrigatório |
| `summary` | opcional | usar sempre |
| `media` | opcional | **incluir sempre** — 422 se omitido (incidente registrado) |
| `status` | opcional | `"draft"` ou `"scheduled"` |
| `scheduleDate` | opcional | obrigatório se `status="scheduled"` |

📄 `scheduleDate`: ISO 8601 UTC (ex: `"2026-04-28T13:00:00Z"` para 10h BRT).
📄 Resposta 201: `{ "success": true, "statusCode": 201, "message": "Created Post" }`
📄 Scope: `socialplanner/post.write`
⚠️ Twitter/X **depreciado em 04/12/2024**.

### Listar posts agendados (para checar conflitos)
```
POST /social-media-posting/{locationId}/posts/list
```
⚠️ **Não é GET** — é POST com body JSON.

📄 Body (`SearchPostDTO`):
```json
{
  "skip": "0",
  "limit": "50",
  "fromDate": "2026-04-28T00:00:00Z",
  "toDate": "2026-04-28T23:59:59Z",
  "includeUsers": "true",
  "type": "scheduled"
}
```
📄 `skip`, `limit`, `fromDate`, `toDate`, `includeUsers` são obrigatórios.
📄 `type` options: `recent`, `all`, `scheduled`, `draft`, `failed`, `in_review`, `published`, `in_progress`, `deleted`.
📄 Scope: `socialplanner/post.readonly`

---

## Custom Values do Location

### Atualizar custom value
```
PUT /locations/{locationId}/customValues/{customValueId}
```
✅ Usado para injetar HTML da newsletter como custom value do GHL.
```json
{ "name": "nome_do_campo", "value": "conteúdo (pode ser HTML longo)" }
```

---

## Notas de implementação Cadencia

### Multi-tenant
Todos os IDs (location, pipeline, workflow, field, account) ficam em `tenant_config.config.ghl`:
```python
ghl = tenant_config.get('ghl', {})
api_key            = ghl['api_key']
location_id        = ghl['location_id']
user_id            = ghl.get('user_id')
linkedin_account_id = ghl.get('linkedin_account_id')
seinfeld_workflow_id = ghl.get('seinfeld_workflow_id')
newsletter_workflow_id = ghl.get('newsletter_workflow_id')
pipeline_id        = ghl.get('pipeline_id')
score_field_id     = ghl.get('score_field_id')
```

### Módulo utilitário
`C:\Users\felip\.claude\scripts\ghl_http.py` — wrapper curl com User-Agent correto.
