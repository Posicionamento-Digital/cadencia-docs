# Growth Pipeline VPS — Geração Multi-Canal

> **ARQUIVO HISTORICO / LEGADO.** Preservado como memoria tecnica; nao descreve o runtime atual e nao deve ser usado como runbook operacional.

**Tipo:** Backend Python (VPS Hostinger)
**Path na VPS:** `/cadencia/pipeline/`
**Path no repo:** repo canônico `Posicionamento-Digital/cadencia-growth`, dir `pipeline/`
**Status:** Ativo em produção
**Porta do trigger server:** `39090` (UFW aberta)
**Atualizado em:** 15/05/2026 (PDL-67/87/89/90/91)

---

## O que é

Pipeline de geração de conteúdo Growth que roda na VPS ao aprovar uma ideia no frontend. Responsável por gerar blog, email Seinfeld, LinkedIn e Instagram — tudo que não é carrossel (carrossel fica nos workers Coolify VPS Master; Railway DESLIGADO).

---

## Arquitetura

```
Frontend (Vercel)
  └── POST /api/app/trigger-generation  (Next.js route)
        └── POST http://72.60.4.71:39090/trigger  (trigger_server.py)
              ├── blog_generate.py      → Supabase published_posts + blog Vercel
              ├── seinfeld_generate.py  → email agendado via GHL
              ├── linkedin_generate.py  → post agendado no Social Planner GHL
              └── instagram_generate.py → legenda agendada no Social Planner GHL

GHL (eventos scoring)
  └── POST http://72.60.4.71:8766/webhook  (webhook_handler.py)

Crontab VPS (automático — sem trigger manual)
  ├── 0 14 * * *   growth_pipeline.py blog seinfeld   (11h BRT, todo dia)
  └── 0 18 * * 5   growth_pipeline.py newsletter      (15h BRT, toda sexta)
```

**Canal newsletter:** NÃO roda no trigger. O `blog_generate.py` cria o `published_post` com `newsletter_included=false`, e o cron de sexta compila e dispara via `newsletter_generate.py`.

---

## trigger_server.py

**Porta:** `39090` | **PID:** via `ps aux | grep trigger_server`
**Processo:** `nohup python3 /cadencia/pipeline/trigger_server.py >> /cadencia/logs/trigger_server.log 2>&1 &`

### Endpoints

| Endpoint | Método | Descrição |
|---|---|---|
| `/trigger` | POST | Dispara pipeline on-demand ao aprovar ideia |
| `/provision` | POST | Provisiona tenant Growth (GHL + blog + DNS) |
| `/newsletter` | POST | Força geração manual de newsletter |
| `/health` | GET | Health check — retorna `{"status":"ok","service":"trigger-server"}` |

### Payload `/trigger`

```json
{
  "tenant_id": "uuid",
  "channels": ["blog", "seinfeld", "linkedin", "newsletter", "instagram"],
  "secret": "<TRIGGER_SECRET>",
  "content_idea_id": "uuid (opcional — bypass da generation_queue)"
}
```

### Ordem de execução obrigatória

1. **sync** — sync de contas sociais do GHL (non-blocking)
2. **blog** — sempre primeiro; cria `published_post` que alimenta seinfeld e newsletter pool
3. **seinfeld** — só roda se blog OK (`exit=0`)
4. **linkedin** — só roda se blog OK
5. **instagram** — só roda se blog OK
6. **newsletter** — silenciosamente ignorado (canal acumula via cron de sexta)

**Se blog falhar → pipeline inteiro abortado.** Seinfeld/LinkedIn não rodam para não despachar conteúdo desconexo.

### Segurança

- `TRIGGER_SECRET` validado em cada request — server recusa iniciar se env var não estiver configurado
- 401 em mismatch de secret

### Env vars necessárias

```bash
# /cadencia/.env
TRIGGER_SECRET=<secret>          # mesmo valor que VPS_TRIGGER_SECRET no Vercel
OPENAI_API_KEY=sk-or-v1-...     # OpenRouter — usado por blog/seinfeld/linkedin/newsletter
OPENAI_IMAGES_KEY=sk-proj-...   # OpenAI direto — usado APENAS pelo DALL-E 3 no blog
OPENAI_BASE_URL=https://openrouter.ai/api/v1
SUPABASE_URL=https://elefbabxkaigusjiiflu.supabase.co
SUPABASE_SERVICE_KEY=...
```

---

## blog_generate.py

Gera artigo HTML a partir do Research Document da ideia aprovada, gera imagem featured com DALL-E 3, e publica no blog Vercel do tenant.

### Uso

```bash
python3 /cadencia/pipeline/blog_generate.py <tenant_id> [--dry-run] [--idea-id <uuid>]
```

### Dois clientes OpenAI (CRÍTICO)

```python
# Texto do artigo — via OpenRouter (gpt-5.4)
client_text = OpenAI(api_key=OPENAI_KEY, base_url=OPENAI_BASE_URL)

# Imagem featured — via OpenAI direto (DALL-E 3 não está no OpenRouter)
client_images = OpenAI(api_key=OPENAI_IMAGES_KEY, base_url="https://api.openai.com/v1")
```

**NUNCA** usar `OpenAI(api_key=OPENAI_IMAGES_KEY)` sem `base_url` — o SDK herda `OPENAI_BASE_URL` do ambiente (OpenRouter) e DALL-E 3 falha com 404 silencioso.

### Tabelas afetadas

- `published_posts` — cria com `newsletter_included=false`, `seinfeld_sent=false`
- `generation_queue` — marca `status=completed`

---

## newsletter_generate.py

Gera newsletter semanal compilando posts com `newsletter_included=false` e dispara via GHL.

### Uso

```bash
python3 /cadencia/pipeline/newsletter_generate.py <tenant_id> [--dry-run]
```

### Fluxo da função `run()`

```
1. Verificar GHL configurado (location_id presente)
2. Buscar posts pendentes (newsletter_included=false)
3. Se 0 posts → return (nada a enviar)
4. [PDL-90] Buscar contatos GHL ANTES de chamar LLM
5. Se 0 contatos → INFO log + return (sem custo de LLM)
6. Gerar HTML da newsletter via LLM (gpt-5.4)
7. Enviar para cada contato via GHL conversations/messages
8. Marcar posts como newsletter_included=true APENAS se ok > 0
```

### 🚫 Don'ts

- **NUNCA** usar `dispatched = ok > 0 or len(contacts) == 0` — marca posts sem enviar (bug PDL-87)
- **NUNCA** chamar LLM antes de verificar se há contatos no GHL (custo desnecessário — bug PDL-90)
- **NUNCA** marcar `newsletter_included=true` se 0 emails foram enviados com sucesso

---

## seinfeld_generate.py

Gera email narrativo estilo Seinfeld a partir do último blog post e agenda no banco para disparo via GHL.

### Uso

```bash
python3 /cadencia/pipeline/seinfeld_generate.py <tenant_id> --generate  # gera e agenda
python3 /cadencia/pipeline/seinfeld_generate.py <tenant_id> --dispatch   # dispara agendados
```

### Fluxo de `run_generate()`

```
1. Verificar GHL configurado
2. [PDL-91] Buscar contatos GHL ANTES de chamar LLM
3. Se 0 contatos → INFO log + return (sem custo de LLM)
4. Buscar published_post sem seinfeld agendado
5. Gerar email via LLM (gpt-5.4)
6. Calcular próximo slot livre (1 email/dia)
7. Salvar no banco com seinfeld_scheduled_at
```

### 🚫 Don'ts

- **NUNCA** gerar email sem verificar contatos GHL primeiro — custo sem utilidade (bug PDL-91)
- **NUNCA** chamar `--dispatch` sem `--generate` primeiro no on-demand (trigger usa só `--generate`)

---

## Monitoramento

```bash
# Status do trigger server
curl http://72.60.4.71:39090/health

# Logs em tempo real
ssh -i ~/.ssh/id_ed25519 root@72.60.4.71 "tail -f /cadencia/logs/trigger_server.log"

# Porta ativa
ssh -i ~/.ssh/id_ed25519 root@72.60.4.71 "ss -tlnp | grep 39090"

# Reiniciar após mudança de .env
ssh -i ~/.ssh/id_ed25519 root@72.60.4.71 "pkill -f trigger_server.py; sleep 1; nohup python3 /cadencia/pipeline/trigger_server.py >> /cadencia/logs/trigger_server.log 2>&1 &"
```

---

## 🔥 Troubleshooting

| Sintoma | Causa | Fix |
|---|---|---|
| Canais não gerados ao aprovar ideia | Vercel env `VPS_TRIGGER_URL` errado ou porta bloqueada no UFW | Verificar `/health`, checar `ufw status` |
| Blog publicado sem imagem | `OPENAI_IMAGES_KEY` não carregado OU `base_url` faltando no cliente de imagem | Ver `.env` da VPS + confirmar `base_url="https://api.openai.com/v1"` |
| Newsletter zera pool sem enviar | `dispatched = ok > 0 or len(contacts) == 0` (bug antigo) | Confirmar que código usa apenas `dispatched = ok > 0` |
| `POST / 404` no log do trigger | Vercel chamando URL sem path (env var é base URL, não full URL) | Confirmar que routes appenham `/trigger`, `/provision`, etc. |
| Trigger server não sobe | Porta em uso (`Address already in use`) | `pkill -f trigger_server.py` antes de subir |
| Key OpenAI rejeitada | Após trocar provider, variável de ambiente ainda em memória do processo antigo | Reiniciar trigger_server após mudar `.env` |

---

## 🪦 Já tentamos

- [2026-05-06 — trigger_server zerava pool da newsletter](../../../../Hub%20Projetos/Incidentes/2026-05-06_trigger-server-zerava-pool-newsletter.md)
- [2026-05-15 — regressão multi-canal porta VPS bloqueada](../../../../Hub%20Projetos/Incidentes/2026-05-15_regressao-multi-canal-porta-vps-bloqueada.md)
- [2026-04-26 — TRIGGER_SECRET mismatch após rotação](../../../../Hub%20Projetos/Incidentes/2026-04-26_trigger-secret-mismatch-pipeline-silenciosa.md)

---

## Decisões arquiteturais

- **Porta 39090** em vez de 8767 — UFW reconfigurando por segurança bloqueou 8767. 39090 já estava aberta. (PDL-67, 15/05/2026)
- **Newsletter fora do trigger** — newsletter é digest semanal, não on-demand. Acumula posts ao longo da semana e cron de sexta compila + dispara.
- **Blog primeiro, obrigatório** — seinfeld e linkedin dependem do `published_post` criado pelo blog. Se blog falhar, pipeline abortado para evitar emails sem conteúdo correspondente.
- **Dois clientes OpenAI** — DALL-E 3 não disponível no OpenRouter. Texto usa OpenRouter (custo menor, BYOK), imagens usam OpenAI direto.

---

*Documentado em 15/05/2026. Ver `docs/incidentes/` para histórico completo.*
