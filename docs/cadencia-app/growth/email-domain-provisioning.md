# email-domain-provisioning — auto-provisão de subdomínio de email por tenant

## TL;DR

Todo tenant novo, ao ser provisionado (`provision_tenant.py`), ganha automaticamente um **subdomínio de email dedicado verificado no Resend** (`<empresa>.cadencia.app.br`), com os registros DNS criados no Cloudflare e `email_provider=resend` + sender gravados em `tenant_config`. Sem passo manual. (CAD-676 fase 1.)

## Identidade

- **Tipo:** Funções dentro de `pipeline/provision_tenant.py` (passo 4.6 da `provision()`)
- **Path (VPS):** `/cadencia/pipeline/provision_tenant.py`
- **Status:** ativo em produção (deploy 2026-06-20)
- **Deps:** Resend Domains API (`RESEND_API_KEY` — full-access, gerencia domínios), Cloudflare DNS API (`CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ZONE_ID`, zona `cadencia.app.br`)
- **Issues:** CAD-676 (fase 1, este doc) · CAD-681 (fase 2, UI self-service)

## Por que existe

Seinfeld e newsletter usam Resend com domínio **compartilhado** `cadencia.app.br`. Cada tenant recebe o **próprio subdomínio**, isolando reputação e warm-up. A fase 1 automatiza o subdomínio default; a fase 2 (CAD-681) será a UI para o cliente trazer domínio próprio.

## Como funciona (fluxo)

Dentro de `provision()`, passo **4.6** (após blog, antes do save), chama `provision_resend_email_domain(tenant_id, config)`:

1. **Deriva o label** do subdomínio via `_email_label(nome_empresa)`:
   - Slugifica (lowercase, sem acento, alfanumérico), dropa stopwords PT (`de/da/e/...`), pega as **2 primeiras palavras significativas**. Flat → `<label>.cadencia.app.br`.
   - Regra de naming (decisão Felipe): nome da empresa; se for nome de pessoa, as 2 primeiras palavras. Ex: `Grupo WGL`→`grupo-wgl`, `Horus Marcas e Patentes`→`horus-marcas`, `Gustavo Petinati Arquitetura`→`gustavo-petinati`.
   - Idempotência: reusa o label já gravado (lido via getter `email_sending_domain` — `config.email.sending_domain` objeto-first, flat `email_domain` como fallback) se existir.
2. **Resolve o domínio no Resend** (por `resend_domain_id` gravado > por nome via `GET /domains` > cria via `POST /domains`). Colisão de nome (empresa homônima) → sufixa `-<tid6>`.
3. **Cria os registros DNS no Cloudflare** (`create_cloudflare_dns`, upsert): DKIM TXT, SPF MX, SPF TXT. Idempotente (81057 = idêntico OK; 81058 = atualiza via PUT). `proxied=False`.
4. **Dispara verificação** (`POST /domains/{id}/verify`) **1×** e faz **poll** do status (8×10s ≈ 80s).
5. **Grava em `config.email` via merge ATÔMICO ANINHADO** — `merge_email_config(tenant_id, email_patch, flat_mirror)` (RPC `merge_tenant_config_email`, DEV-954 Fase 2). NÃO mais read-modify-write do `config` inteiro (fechava o risco R1 de clobber concorrente entre este writer e o `sending_domains.py`). O estado mora no objeto aninhado `config.email`:
   - `email_patch` (aninhado, casa ÚNICA) — sempre: `schema_version:2`, `sending_domain`, `resend_domain_id`, `verification_status`; só se `verified`: `provider:resend`, `sender_address` (`contato@<fqdn>`, lido via getter objeto-first → não clobbera custom), `sender_name`.
   - `flat_mirror` (nível-1 do config, ESPELHO de transição até a Fase 4) — `email_domain`, `resend_domain_id`, e (se verified) `email_provider`, `email_sender_address`/`name`. Idêntico ao aninhado; mantido só pros leitores legados durante a transição.
   - **Colisão `resend_domain_id` resolvida:** a casa ÚNICA é a aninhada (`config.email.resend_domain_id`); o root flat virou só espelho. O id é resolvido lendo o aninhado primeiro (getter), flat como fallback.

### Gate anti-silent-failure (importante)

`email_provider` **só** vira `resend` quando o domínio está `verified`. Se não verificar na janela de ~80s (DNS propagando), o provision finaliza `partial` e o `should_retry_provisioning` reavalia no próximo ciclo (self-healing) — **nunca** flipa pra um domínio pendente (que daria 403 no envio). Origem: o go-live manual do PD (2026-06-19) quebrou exatamente por enviar de subdomínio não verificado (403). Ver `email-warmup-cutover.md`.

## Host separado do blog (por que não usa o apex)

O blog ocupa `<slug>.cadencia.app.br` com **CNAME → Vercel**. O email **não pode** compartilhar esse apex: o CNAME captura as queries TXT/MX, quebrando SPF/DKIM/DMARC. Por isso o email usa um label próprio (`<empresa>.`), distinto do slug do blog.

## Funções (em `provision_tenant.py`)

| Função | Papel |
|---|---|
| `_email_label(company_name)` | Deriva o rótulo do subdomínio (regra de naming) |
| `resend_api(method, endpoint, data)` | Cliente Resend via curl + UA (Resend atrás de Cloudflare bloqueia urllib → 1010) |
| `_cf_curl(method, url, body)` / `create_cloudflare_dns(...)` | Upsert de registro DNS no Cloudflare |
| `provision_resend_email_domain(tenant_id, config)` | Orquestra tudo; grava `config.email` via `merge_email_config` (RPC atômica) e retorna `(email_patch, flat_mirror, errors)`, não levanta |
| `merge_email_config(tenant_id, email_patch, flat_mirror)` (em `lib_api.py`) | Merge atômico aninhado de `config.email` via RPC `merge_tenant_config_email`; retorna o config novo ou `None`+WARN. DDL `migrations/20260630_merge_tenant_config_email_rpc.sql`, aplicada em produção em 30/06/2026 |

## Quando usar / NÃO usar

- ✅ Automático em todo provision de tenant novo. Reusável manualmente importando `provision_resend_email_domain`.
- ❌ Não chamar pra trocar o domínio de um tenant que já tem sender customizado (a função não clobbera sender, mas pra trocar domínio é a fase 2/CAD-681).

## 🚫 Don'ts

- **Não** flipar `email_provider=resend` de um tenant manualmente sem domínio verificado **e sem contatos no CRM** (regressão silenciosa — envia de domínio quebrado / pra lista vazia).
- **Não** apontar o email pro apex `<slug>.cadencia.app.br` (CNAME do blog quebra SPF/DKIM).
- **Não** assumir que `RESEND_API_KEY` é só send-only — a key da VPS gerencia domínios (testado: `GET/POST /domains` 200).

## 🔥 Troubleshooting

| Sintoma | Causa | Fix |
|---|---|---|
| `403 ... domain is not verified` no envio | `email_sender_address` aponta pra subdomínio não verificado no Resend | Verificar domínio (`POST /domains/{id}/verify`) + conferir DNS no Cloudflare |
| Domínio fica `pending` após provision | DNS propagando > 80s | `should_retry_provisioning` reavalia; ou `POST /domains/{id}/verify` manual depois |
| `HTTP 1010` ao chamar Resend | urllib sem UA de browser | usar `resend_api` (curl + UA) — nunca urllib puro |
| `429` em burst de envio | rate-limit Resend | throttle no dispatch (ver `seinfeld-email.md`) |

## 📚 Referências cruzadas

- Skill `/cadencia-provisionar-tenant` no pd-framework — fluxo operacional atual
- [seinfeld-email](seinfeld-email.md) / [newsletter](newsletter.md) — consumidores do `email_sender_address`/`email_provider`
- [email-warmup-cutover](email-warmup-cutover.md) — histórico do cutover + operação de warm-up
- Resend Domains API: https://resend.com/docs/api-reference/domains
