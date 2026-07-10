---
date: 2026-06-27
tags: [doc, componente, cadencia-growth]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
---
# cadencia-growth → pipeline/

Núcleo do sistema — geradores por canal + provisioning + cadence_tick + trigger_server.

## Identidade
- **Tipo:** módulo de aplicação
- **Stack:** Python 3.12 · openai · anthropic · supabase-py
- **Path:** `pipeline/`
- **Daemon:** trigger_server.py na porta `:39090`
- **Status:** ativo

## Arquivos chave
- `blog_generate.py` / `seinfeld_generate.py` / `linkedin_generate.py` / `instagram_generate.py` / `newsletter_generate.py` — geradores por canal
- `provision_tenant.py` — cria subconta GHL + subdomínio Resend
- `cadence_tick.py` — motor de cadências (CAD-577/578)
- `trigger_server.py` — daemon HTTP on-demand
- `email_warmup.py` — cutover GHL→Resend per-tenant
- `brand_template.py` / `prompts.py` / `lib_api.py` — utils compartilhados

## Como funciona
1. Cron 14h BRT chama `growth_pipeline.py sync blog linkedin instagram`
2. `sync_accounts` refresh tokens GHL
3. Por tenant + por canal: gera prompt → LLM → salva em Supabase → dispatch (se aplicável)

## Don'ts
- Não usar `urllib` pra GHL (Cloudflare bloqueia)
- Não inline `sb_*` / `ghl_request` — usar `lib_api`
- Não editar daemon `trigger_server.py` sem restart (`systemctl restart cadencia-trigger`)

## Notas Relacionadas
[[Projetos/Cadencia-Growth/Docs/README]] · [[Projetos/Cadencia-Growth/Docs/scoring]] · [[Projetos/Cadencia-Growth/Docs/crons]]