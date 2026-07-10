---
type: source
source_kind: incidente
date: 2026-06-03
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-06-03_cadencia-cloudflare-proxied-bloqueia-ssl-vercel

# Incidente: DNS Cloudflare com proxied=True bloqueava Vercel emitir SSL → blogs HTTP 525 silenciosamente

**Data:** 03/06/2026
**Severidade:** Alta
**Projeto:** Cadência
**Duração do impacto:** ≥ 20h confirmado (Alejandro provisionado ~19h antes / Horus +Marinella mesmo dia). Possivelmente mais — desde a migração 1-blog=1-repo no PR `cadencia-growth#1` (02/06).
**Tags:** `#infra` `#vercel` `#cloudflare` `#ssl` `#dns` `#provisioning` `#silenciosa` `#regressao`

## O que aconteceu

Durante validação pós-onboarding de Marinella/Grupo WGL e Horus Marcas e Patentes em 03/06, descobri que os subdomínios provisionados retornavam **HTTP 525 (SSL handshake failed)** ao acessar os blogs:

- `https://grupo-wgl.cadencia.app.br` → HTTP 525
- `https://horus-marcas-e-patentes.cadencia.app.br` → HTTP 525
- `https://alejandro-pano.cadencia.app.br` → HTTP 525 (provisionado 20h antes — bug pré-existente)

Vercel project, deployments e domínio estavam todos OK: `vercel ls` mostrava "● Ready", domínio inspecionado retornava o projeto correto na seção `Projects`, e o subdomínio `.vercel.app` direto (`blog-grupo-wgl.vercel.app`) servia HTTP 200 normalmente.

A diferença com tenants que funcionavam: `felipe-salgueiro.cadencia.app.br` e `laboratorio-de-crescimento.cadencia.app.br` tinham CNAME idênticos (`cname.vercel-dns.com`) mas com **proxied=False** (DNS only). Os 3 quebrados tinham **proxied=True** (orange cloud).

## Causa raiz

`provision_tenant.py:404` na função `cf_dns_create_record()`:

```python
record = {
    'type': 'CNAME',
    'name': f'{subdomain}.cadencia.app.br',
    'content': target,
    'proxied': True,   # ← BUG
    'ttl': 1,
}
```

Cadeia técnica:

1. Vercel emite certificado SSL via **Let's Encrypt** (HTTP-01 ou DNS-01 challenge).
2. Quando o DNS está com `proxied=True` (orange cloud), o tráfego HTTP/HTTPS passa pelos servidores Cloudflare antes de chegar à Vercel. Os IPs visíveis públicamente são da Cloudflare, não da Vercel.
3. O challenge HTTP-01 do Let's Encrypt bate em `http://<dominio>/.well-known/acme-challenge/<token>` esperando que o servidor Vercel responda. Mas a request chega na Cloudflare que **não tem o token** (não foi configurada como reverse proxy do Vercel) → 404 ou redirect.
4. Let's Encrypt falha o challenge → certificado nunca é emitido.
5. Mesmo assim, Vercel marca `verified: true` (porque DNS aponta pra `cname.vercel-dns.com`), mas internamente o SSL provisioning fica em estado "pending" indefinidamente.
6. Cloudflare em modo SSL "Flexible" ou "Full" tenta handshake com origem (Vercel) que não tem cert válido → **HTTP 525 "SSL handshake failed"**.

## Por que não foi detectado

- **Provisionamento marca `provisioning_status=ready`** mesmo sem testar `HTTP 200` no domínio final. Bastava resolver DNS e criar projeto Vercel.
- **Nenhum smoke test pós-deploy**: o script não faz `curl https://<dominio>` ao final.
- **Sintoma só aparece quando alguém abre o blog**. Nem cron interno (que escreve via API) usa a URL pública.
- **`provisioning_errors=null`** — o status final era "OK" do ponto de vista do código.
- **Confusão diagnóstica**: erro 525 sugere problema com Vercel/Cloudflare SSL, não com configuração do registro DNS. Vercel `domains inspect` mostra "WARNING: not configured properly. Set A 76.76.21.21" o que aponta erradamente pra mudança de DNS quando na verdade basta desligar o proxy.

## Como foi corrigido

### 1. Fix de dados em produção (3 tenants afetados)

Via Cloudflare API, PATCH em cada record DNS:

```bash
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$CF_ZONE/dns_records/$REC_ID" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"proxied":false}'
```

Aplicado em:
- `grupo-wgl.cadencia.app.br` → HTTP 200 em ~60s
- `horus-marcas-e-patentes.cadencia.app.br` → SSL provisioning em curso
- `alejandro-pano.cadencia.app.br` → SSL provisioning em curso

### 2. Patch do código que cria DNS

`/cadencia/pipeline/provision_tenant.py` linha 404:

```python
# antes
'proxied': True,
# depois
'proxied': False,  # PDL-fix: Cloudflare proxy quebra emissão SSL Vercel (HTTP 525)
```

Backup `/cadencia/pipeline/provision_tenant.py.bak-proxied-20260603-2010`.

### 3. Force re-verify dos domínios via Vercel API

```bash
curl -X POST "https://api.vercel.com/v9/projects/<project>/domains/<domain>/verify" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

Retornou `verified: true` para todos — destrava Let's Encrypt cert issuance.

## Prevenção

### Checklist / regras pra evitar recorrência

- [ ] Em qualquer DNS record criado pra subdomínio Vercel: `proxied: False` (Cloudflare modo "DNS only"). Subdomínios já têm cert via Let's Encrypt automático do Vercel — proxy Cloudflare é redundante e quebra.
- [ ] Adicionar smoke test ao final do `provision_tenant.py`: `curl -s -o /dev/null -w "%{http_code}" https://<dominio>` esperando 200. Se falhar, marcar `provisioning_status=ssl_pending` (não `ready`).
- [ ] Dashboard "tenants com blog HTTP != 200" — rodar cron diário consultando blog_url e logando.
- [ ] Após criar/mudar DNS de subdomínio Vercel: aguardar 60-90s + testar acesso HTTP.
- [ ] Antes de assumir que cert SSL foi emitido: `vercel domains inspect <dominio>` — verificar ausência de WARNING + `Projects` populado.

### Pattern correto (Cloudflare DNS pra Vercel)

```python
# ❌ ERRADO — proxied bloqueia Let's Encrypt
record = {
    'type': 'CNAME',
    'name': f'{subdomain}.cadencia.app.br',
    'content': 'cname.vercel-dns.com',
    'proxied': True,
    'ttl': 1,
}

# ✅ CERTO — DNS only, Vercel gerencia SSL direto
record = {
    'type': 'CNAME',
    'name': f'{subdomain}.cadencia.app.br',
    'content': 'cname.vercel-dns.com',
    'proxied': False,
    'ttl': 1,
}
```

### Smoke test obrigatório pós-provisioning

```python
# Append ao final de provision()
import time, urllib.request
time.sleep(60)  # Aguardar DNS + Let's Encrypt
public_url = f'https://{tenant_slug}.cadencia.app.br'
try:
    req = urllib.request.Request(public_url, method='HEAD')
    code = urllib.request.urlopen(req, timeout=10).getcode()
    if code != 200:
        errors.append(f'Blog HTTP {code} pós-provision — investigar SSL')
except Exception as e:
    errors.append(f'Blog inacessível pós-provision: {e}')
```

### Gotcha novo (G020)

**Subdomínio Vercel + Cloudflare proxied=True = HTTP 525.** Let's Encrypt não consegue completar HTTP-01 challenge através do proxy Cloudflare. SSL nunca é emitido na origem Vercel. Cloudflare em "Full/Strict" SSL mode requer cert válido no origin → 525. Fix: `proxied=False` no record DNS Cloudflare.

### Regra atualizada em

- [x] `pd-framework/incidents/INDEX.md` (este incident)
- [ ] `pd-framework/times/produto/cadencia/EXPERTISE.md` — adicionar G020 (pendente)
- [ ] `cadencia-growth/provision_tenant.py` — sync com VPS Master + commit (pendente, branch `feat/pdl-fix-cloudflare-proxied`)

## Commits relacionados

- VPS `/cadencia/pipeline/provision_tenant.py` — patchado via `sed`, backup `.bak-proxied-20260603-2010` (não commitado — sync com `cadencia-growth` GitHub pendente)
- Cloudflare API — PATCH em 3 records DNS (não rastreável via git)

## Links relacionados

- Incidente pai (mesma sessão, causa-irmã da cascata): `2026-06-03_cadencia-trigger-server-env-stale-systemd.md`
- PR `cadencia-growth#1` (02/06) — introduziu o flow 1-blog=1-repo + DNS automation onde o bug nasceu
- Tenants afetados confirmados:
  - Marinella/Grupo WGL — `grupo-wgl.cadencia.app.br` (HTTP 200 após fix)
  - Mel Quevedo/Horus Marcas e Patentes — `horus-marcas-e-patentes.cadencia.app.br`
  - Alejandro Pano — `alejandro-pano.cadencia.app.br`

---
*Registrado via sistema de incidentes. Ver INDEX.md para histórico completo.*
