---
date: 2026-05-18
tags: [documentacao, infra, portal-pd, supabase]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[pd-portal]]"]
---
# Infra — Portal PD

## Supabase
- **Project ref:** elefbabxkaigusjiiflu (mesmo do Cadencia)
- **Tabela:** client_portal_access(user_id, tenant_slug, tenant_name) + RLS
- **Bucket:** client-portal (privado, RLS por tenant_slug)
- **Credentials:** vault databases -> Supabase - ClaudeCode - CLI -> credencial

## Vercel
- **Project:** pd-portal (team felipeluissalgueiros-projects)
- **Deploy:** manual - vercel --prod --yes
- **Alias:** vercel alias set pd-portal-kappa.vercel.app portal.cadencia.ia.br

## DNS (Cloudflare)
- **Zona:** cadencia.ia.br
- **Record:** CNAME portal -> cname.vercel-dns.com (proxied: false)
- **Credentials:** vault Hosts -> Cloudflare - API Token + Zones -> api_token

## Notas de migracao
- sb_secret key nao funciona na Storage API REST -> buscar JWT legacy via GET /v1/projects/{ref}/api-keys?reveal=true
- NOTIFY pgrst, 'reload schema' necessario apos CREATE TABLE
- uri_allow_list do Supabase Auth deve incluir portal.cadencia.ia.br

## Historico
- 2026-05-18 - Setup inicial: tabela, bucket, RLS, CNAME

## Notas Relacionadas
[[portal-pd-overview]]
