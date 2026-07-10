> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/features/growth-social-planner/index.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/features/growth-social-planner/index.md)
> Sincronizado via `sync_cadencia_docs.py` em 2026-05-29 (PDL-342).

---

# Feature: Growth Social Planner (LinkedIn / Carrossel Instagram)

Agendamento de posts no GHL Social Planner via API.

**Referência:** PD Marketing `ghl-social-post.py`
**Cadencia:** `linkedin_generate.py` (VPS)
**Status Cadencia:** Gera conteúdo LinkedIn, dispatch GHL pendente. Carrossel → Social Planner não implementado.
**Última atualização:** 2026-04-25

> **Convenção:** ✅ = verificado no código | ⚠️ = inferência não verificada no código

---

## Upload de mídia (PNG → GHL Media Library)

### Endpoint
📄 Doc oficial + ✅ Código PD: `POST https://services.leadconnectorhq.com/medias/upload-file`

### Formato
📄 Doc oficial: `multipart/form-data`. Suporta dois modos:

| Campo | Tipo | Quando usar |
|---|---|---|
| `file` | binary | Upload direto (`hosted=false`) |
| `hosted` | boolean | `true` = URL remota, `false` = arquivo local |
| `fileUrl` | string | URL da mídia (quando `hosted=true`) |
| `name` | string | Nome do arquivo (opcional) |
| `parentId` | string | ID da pasta destino (opcional) |

📄 Limite de tamanho: **25 MB** para imagens, 500 MB para vídeo.

⚠️ **Divergência entre doc e código PD:** A doc oficial usa o campo `file`, o código PD usa `fileMedia`. Testar antes de implementar qual o GHL aceita.

```bash
# Versão doc oficial
curl -F "file=@slide_01.png" -F "hosted=false" ...

# Versão código PD (em produção)
curl -F "fileMedia=@slide_01.png" -F "name=slide_01.png" ...
```

✅ `Content-Type` **NÃO** é enviado manualmente — curl define `multipart/form-data` com `-F`.
✅ Timeout: **120s** (vs 30s nos outros endpoints — upload é lento).
✅ `User-Agent` de navegador real **obrigatório** — Cloudflare bloqueia curl padrão.
📄 Scope necessário: `medias.write`

### Resposta
📄 Doc oficial:
```json
{ "fileId": "...", "url": "https://storage.googleapis.com/..." }
```
✅ Código PD extrai `resp.get("url")`. Se `None`: loga erro mas não aborta o loop.

### Gotchas
✅ `time.sleep(0.3)` entre cada upload (rate limiting preventivo)
✅ Sem validação de tamanho antes do upload — erro só aparece no JSON de resposta

---

## Criação do post no Social Planner

### Endpoint
✅ `POST https://services.leadconnectorhq.com/social-media-posting/{locationId}/posts`

### Headers
```
Authorization: Bearer <api_key>
Version: 2021-07-28
Content-Type: application/json
User-Agent: Mozilla/5.0 ...   ← obrigatório (Cloudflare)
```

### Body
```json
{
  "accountIds": ["<account_id>"],
  "type": "post",
  "userId": "<ghl_user_id>",
  "summary": "<caption>",
  "media": [
    {"url": "<cdn_url>", "type": "image/png"}
  ],
  "status": "scheduled",
  "scheduleDate": "2026-04-28T13:00:00Z"
}
```

### Campos

| Campo | Doc oficial | Código PD | Detalhe |
|---|---|---|---|
| `accountIds` | ✅ obrigatório | ✅ obrigatório | Array com 1 ID da conta |
| `type` | ✅ obrigatório | ✅ obrigatório | `"post"`, `"story"` ou `"reel"` |
| `userId` | ✅ obrigatório | ✅ obrigatório | ID do usuário GHL |
| `summary` | 📄 opcional | ✅ obrigatório no uso | Caption/legenda |
| `media` | 📄 opcional | ✅ **sempre presente** | ⚠️ Divergência: doc diz opcional, código PD sempre inclui (mesmo `[]`). Incidente registrado: 422 se omitido. **Incluir sempre.** |
| `status` | 📄 opcional | ✅ usado | `"draft"`, `"scheduled"`, `"published"` etc. |
| `scheduleDate` | 📄 opcional | ✅ condicional | ISO 8601 UTC. Obrigatório na prática se `status = "scheduled"` |

📄 Status values documentados: `null`, `draft`, `scheduled`, `in_review`, `published`, `in_progress`, `deleted`
📄 Scope necessário: `socialplanner/post.write`
📄 Resposta 201: `{ "success": true, "statusCode": 201, "message": "Created Post" }`
⚠️ Twitter/X **depreciado em 04/12/2024** — não usar `accountIds` de Twitter.

---

## Ordenação dos slides no carrossel (crítico)

✅ Ordenação via `sorted(glob.glob(pattern))` — lexicográfico no path completo.

✅ Os slides devem ser nomeados com **zero-fill**:
```
slide_01_capa.png, slide_02_xxx.png, ..., slide_08_cta.png
```
Zero-fill garante que ordenação lexicográfica = ordenação numérica.
Sem zero-fill: `slide_10` viria antes de `slide_2`.

✅ O loop de upload preserva a ordem → lista de CDN URLs acumula na mesma ordem → `body["media"]` montado em ordem.

⚠️ **INFERÊNCIA NÃO VERIFICADA:** O código assume que o GHL Social Planner renderiza o carrossel na ordem do array `media[]`. Não há campo `position`, `index` ou `order` nos objetos do array. Não há documentação GHL no repositório confirmando esse comportamento.

---

## Account IDs (Cadencia — multi-tenant)

✅ No PD Marketing os IDs são hardcoded no script. Na Cadencia ficam no `tenant_config.config.ghl`:

```python
ghl_cfg = tenant_config.get('ghl', {})
linkedin_account_id  = ghl_cfg.get('linkedin_account_id')
instagram_account_id = ghl_cfg.get('instagram_account_id')
user_id              = ghl_cfg.get('user_id')
api_key              = ghl_cfg.get('api_key')
location_id          = ghl_cfg.get('location_id')
```

✅ Exemplos de IDs PD (formato observado no código):
```
linkedin:  6870069924dfd21a39d81410_4av6ZwswvBvuI8F13zbr_DKczzFxT9F_profile
instagram: 687005ab3303c454d9c18d9c_4av6ZwswvBvuI8F13zbr_17841400135990091
```

⚠️ **INFERÊNCIA:** O formato aparenta ser `{oauth_id}_{location_id}_{platform_id}` com sufixo `_profile` para LinkedIn. Não há documentação disso no repositório. O GHL infere a plataforma a partir do `account_id` — também inferência, não há código confirmando explicitamente.

✅ `GHL_USER_ID`: default hardcoded `"Gf4yO9n2XeVH3bjuz0EK"` no PD, sobrescrito por variável de ambiente.

---

## Cálculo de scheduled_date (melhoria Cadencia)

### Problema atual
✅ PD Marketing: `scheduled_date` passado manualmente pelo chamador (`Data da Postagem do Notion + T10:00:00Z`). Sem cálculo automático, sem consulta de conflitos.

### Implementação proposta Cadencia

```python
from datetime import datetime, timedelta, timezone

BRT = timezone(timedelta(hours=-3))
PUBLISH_HOUR_UTC = 13  # 10h BRT = 13h UTC

def find_available_slot(tenant_id, location_id, api_key):
    # Passo 1: âncora no banco
    rows = sb_get(f'published_posts?tenant_id=eq.{tenant_id}'
                  f'&linkedin_scheduled_at=not.is.null'
                  f'&order=linkedin_scheduled_at.desc&limit=1'
                  f'&select=linkedin_scheduled_at')
    last_slot = parse_datetime(rows[0]['linkedin_scheduled_at']) if rows else None
    candidate = next_publish_slot(last_slot)

    # Passo 2: confirmar com GHL via POST /posts/list (não é GET)
    # Endpoint oficial: POST /social-media-posting/{locationId}/posts/list
    # Body: { "skip": "0", "limit": "50", "fromDate": "...", "toDate": "...",
    #         "includeUsers": "true", "type": "scheduled" }
    for _ in range(7):
        occupied = get_ghl_scheduled_slots(location_id, api_key, candidate)
        if candidate not in occupied:
            return candidate
        candidate = next_weekday(candidate + timedelta(days=1))

    return candidate  # fallback


def next_publish_slot(last_scheduled_at=None):
    now = datetime.now(BRT)
    if last_scheduled_at:
        base = last_scheduled_at.date() + timedelta(days=1)
    else:
        base = now.date()
        if now.hour >= 10:  # já passou das 10h BRT
            base += timedelta(days=1)
    while base.weekday() >= 5:  # pula fim de semana
        base += timedelta(days=1)
    return datetime(base.year, base.month, base.day, PUBLISH_HOUR_UTC, 0, 0, tzinfo=timezone.utc)
```

| Situação | Resultado |
|---|---|
| Aprovação às 9h BRT | Agenda hoje 10h BRT |
| Aprovação às 11h BRT | Agenda amanhã 10h BRT |
| 3 aprovações mesmo dia | 3 dias úteis consecutivos |
| Cron falha sexta, roda segunda | Calcula a partir do último `linkedin_scheduled_at` |
| Slot GHL ocupado | Avança para próximo dia útil (máx 7 tentativas) |

---

## Migration necessária

```sql
ALTER TABLE published_posts
  ADD COLUMN IF NOT EXISTS linkedin_scheduled_at timestamptz;
```

---

## Carrossel → Social Planner (gap não implementado)

Ao gerar um carrossel, os PNGs estão em Supabase Storage. O fluxo de envio para o GHL Social Planner (para agendamento automático no Instagram):

```python
# 1. Para cada PNG em slides_content (em ordem do array):
#    - Nomear temporariamente: slide_{i:02d}.png (zero-fill)
#    - Download do Supabase (signed URL)
#    - Upload para GHL Media Library (multipart, timeout 120s)
#    - Coletar CDN URL

# 2. Criar post no Social Planner:
#    - accountIds: [instagram_account_id]
#    - media: CDN URLs em ordem
#    - scheduleDate: calculado via find_available_slot()
```

---

## Pendências Cadencia

- [ ] Verificar endpoints GHL na documentação oficial antes de implementar
- [ ] Migration: `linkedin_scheduled_at` em `published_posts`
- [ ] `linkedin_generate.py`: implementar `find_available_slot()` + `scheduleDate` no body GHL
- [ ] Implementar carrossel → GHL Social Planner (download Supabase → upload GHL → criar post)
- [ ] Validar comportamento do `media[]` na ordenação do carrossel (⚠️ inferência — testar antes de implementar em produção)
