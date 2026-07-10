> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/infra-cli-access.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/infra-cli-access.md)
> Sincronizado via `sync_cadencia_docs.py` em 2026-05-29 (PDL-342).

---

# Acesso à Infraestrutura via CLI — Cadencia

## Vercel (Frontend Next.js)

### Como linkar ao projeto
```bash
vercel link --yes --project cadencia-app
```
O projeto é `felipeluissalgueiros-projects/cadencia-app`.

### Comandos disponíveis
```bash
vercel env ls                          # Listar env vars
vercel env add VAR_NAME production     # Adicionar (valor via stdin)
vercel env rm VAR_NAME production --yes # Remover
vercel env pull                        # Baixar .env.local
vercel logs                            # Ver logs
vercel --prod                          # Deploy manual produção
vercel project ls                      # Listar projetos
```

### Domínios configurados
- **Produção:** `cadencia.app.br` (domínio principal)
- **Alias:** `cadencia.ia.br` (também funciona)
- **Vercel:** `cadencia-app.vercel.app`

### Env vars importantes
- `NEXT_PUBLIC_APP_URL` = `https://cadencia.app.br`
- `NEXT_PUBLIC_SUPABASE_URL` = URL do Supabase
- `SUPABASE_SERVICE_ROLE_KEY` = service role (acesso admin ao banco)
- `WORKERS_API_URL` = URL do Railway backend

---

## Railway (Backend Python)

### Comandos disponíveis
```bash
railway status                         # Ver serviço atual
railway logs                           # Ver logs
railway variables                      # Listar env vars
railway variables set KEY=VALUE        # Setar variável
railway up                             # Deploy manual
```

### Deploy automático
- Railway deploya do branch `master`
- Após push no main: `git push origin main:master`

### Env vars importantes (via `railway variables`)
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` — acesso ao banco
- `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` — LLMs
- `PEXELS_API_KEY` — fotos stock
- `CRON_SECRET` — segredo do cron job

---

## Supabase (Banco de Dados)

### Acesso via REST API (service role key)
```bash
# Ler dados
curl -s "https://elefbabxkaigusjiiflu.supabase.co/rest/v1/TABLE?select=COLS&limit=N" \
  -H "apikey: SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer SERVICE_ROLE_KEY"

# Inserir/atualizar
curl -s -X POST "https://elefbabxkaigusjiiflu.supabase.co/rest/v1/TABLE" \
  -H "apikey: SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=minimal" \
  -d '{"col": "val"}'

# Rodar SQL direto (via rpc)
curl -s -X POST "https://elefbabxkaigusjiiflu.supabase.co/rest/v1/rpc/FUNCTION_NAME" \
  -H "apikey: SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Credenciais
- **Project ref:** `elefbabxkaigusjiiflu`
- **URL:** `https://elefbabxkaigusjiiflu.supabase.co`
- **Service Role Key:** disponível via `railway variables` (campo `SUPABASE_SERVICE_ROLE_KEY`)
- **JWT Secret:** disponível via `railway variables` (campo `SUPABASE_JWT_SECRET`)

### Supabase Management API (configurar auth, templates, etc.)
- **Endpoint:** `https://api.supabase.com/v1/projects/elefbabxkaigusjiiflu/config/auth`
- **Token:** salvo em `Hub Projetos/Credenciais/supabase-access-token.txt`
- **Header:** `Authorization: Bearer <token>`
- **Usado para:** Site URL, Redirect URLs, Email Templates, Auth providers

```bash
# Ler config de auth
TOKEN=$(cat "C:/Users/felip/OneDrive/Documentos/ClaudeCode/Hub Projetos/Credenciais/supabase-access-token.txt" | tr -d '\n')
curl -s "https://api.supabase.com/v1/projects/elefbabxkaigusjiiflu/config/auth" \
  -H "Authorization: Bearer $TOKEN"

# Atualizar config de auth
curl -s -X PATCH "https://api.supabase.com/v1/projects/elefbabxkaigusjiiflu/config/auth" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"site_url": "https://cadencia.app.br"}'
```

### O que a service role key NÃO faz
- Não altera configurações de auth (Site URL, Redirect URLs, Email Templates)
- Para isso usar a Management API com o Personal Access Token acima

---

## Git (Deploy)

```bash
git push origin main              # Vercel deploya automaticamente
git push origin main:master       # Railway deploya automaticamente
```

Sempre pushar para AMBOS após mudanças no backend Python.

---

## CORS — Origens permitidas

Backend Python (`cadencia-workers/src/shared/config.py`):
- `https://cadencia.app.br`
- `https://cadencia.ia.br`
- `https://cadencia.posicionamentodigital.com` (legacy)
- `https://cadencia-app.vercel.app`
