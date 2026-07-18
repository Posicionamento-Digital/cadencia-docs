# Migração de email GHL → Resend — runbook de go-live

> **ARQUIVO HISTÓRICO — migração concluída.** GHL está desligado em todos os tenants e canais. Não executar os passos de rollout ou rollback deste documento; a operação atual é Resend + CRM Cadencia.

Tira o **envio de email** e o **scoring** do GHL e coloca no **Resend + Supabase**.
Contatos passaram a viver no Supabase e o provider ativo é Resend. As flags e
comandos abaixo registram o cutover, não o estado operacional atual.

> Escopo: **só email** (Seinfeld + newsletter + scoring + transacional). CRM,
> LinkedIn/Instagram e a UI também não dependem mais de GHL.

## Estado em 2026-06-17 — o que já está pronto e o que falta

**Pronto e validado:**
- ✅ Código mergeado e na VPS (`/cadencia` = origin/main `cf2fc57`, drift limpo, 101 testes verdes).
- ✅ Daemon de scoring `resend_webhook.py` **live** (`:8767`), `@reboot` no crontab do root.
  Exposto por HTTPS em `https://webhooks.cadencia.ia.br` (GET 200, POST sem assinatura 401).
- ✅ `RESEND_API_KEY` **full-access** válida; `RESEND_WEBHOOK_SECRET` setado.
- ✅ Webhook no Resend: endpoint `https://webhooks.cadencia.ia.br`, **enabled**, com
  `email.opened/clicked/bounced/complained` (entre outros).
- ✅ `contacts` no Supabase: ~7685 (migrados via RPC `import_ghl_contacts_batch` do CRM próprio).
- ✅ DKIM (`resend._domainkey`), SPF (`send` TXT) e MX (`send`) **verified** → **envio funciona/autentica**.

**Falta pro go-live (ações fora do meu alcance):**
1. 🔴 **DNS — registro de tracking** (domínio está `partially_failed` só por causa disto):
   adicionar na zona `cadencia.app.br` o **CNAME** `redirect` → `links1.resend-dns.com`,
   **DNS only (nuvem cinza, NÃO proxied)** — proxiar quebra a verificação do Resend.
   Sem ele, o **rastreio de clique** (`email.clicked`, +5 no score) não funciona; aberturas
   (`email.opened`) podem funcionar pela pixel, mas o domínio só vira `verified` com este CNAME.
   Depois: `POST https://api.resend.com/domains/442ed3c4-2021-487d-9bc9-2044b68ec363/verify`.
2. 🔴 **Vercel (app)** — os deploys de produção do `master` ficam **BLOCKED** quando o
   merge-commit é de autoria `luizsidiao` (não autorizada no projeto). Destravar: **Redeploy**
   pelo painel do deploy mais recente do master, **ou** adicionar `luizsidiao` como membro do
   projeto Vercel com permissão de deploy (fix permanente). Publica `/api/unsubscribe`,
   blog-desacoplado e provision-trigger.
3. 🟡 **Cutover** `EMAIL_PROVIDER=resend` — só DEPOIS de (1), e com **warm-up** (domínio é
   "frio": começar por 1 tenant-piloto, subir volume gradual). Hoje está `ghl` (produção intacta).

## PRs (mergear nesta ordem)

| # | Repo / PR | O que entrega |
|---|---|---|
| 1 | app `feat/contacts-table` | tabela `contacts` (Supabase) |
| 1 | growth `feat/email-resend-foundation` | `resend_send` + `migrate_ghl_contacts.py` |
| 2 | growth `feat/email-resend-senders` | Seinfeld/Newsletter via Resend (flag) |
| 3 | growth `feat/email-resend-scoring` | webhook de scoring do Resend |
| 4 | growth `feat/email-resend-compliance` | unsubscribe + List-Unsubscribe |
| 4 | app `feat/email-unsubscribe` | rota `/api/unsubscribe` |

## Pré-requisitos (ação humana — não dá pra automatizar daqui)

1. ✅ **Domínio `cadencia.app.br` VERIFICADO no Resend** (feito 2026-06-16, região
   `sa-east-1`). Registros publicados na zona Cloudflare: `resend._domainkey` (DKIM),
   `send` (SPF `v=spf1 include:amazonses.com ~all` + MX `feedback-smtp.sa-east-1.amazonses.com`).
   From dos envios: `noreply@cadencia.app.br` (override por tenant via `email_sender_address`).
   Envio de teste confirmado (`POST /emails` → HTTP 200 + id). O apex tem `SPF -all` +
   `DMARC p=reject`, mas **passa via DKIM alinhado** (`d=cadencia.app.br`) — validado no teste.
   O link de unsubscribe usa a mesma base (`APP_BASE_URL=https://cadencia.app.br`).
2. **Gerar** `RESEND_API_KEY` e o **signing secret** do webhook (`whsec_...`).
3. **Webhook no Resend** apontando para o endpoint HTTPS do scoring (ver Daemon),
   marcando os eventos: `email.opened`, `email.clicked`, `email.bounced`,
   `email.complained`.

## Env (VPS `/cadencia/.env`)

```
EMAIL_PROVIDER=ghl                # vira 'resend' por tenant no cutover
RESEND_API_KEY=re_...
RESEND_WEBHOOK_SECRET=whsec_...
RESEND_WEBHOOK_PORT=8767
APP_BASE_URL=https://cadencia.app.br
```

## Deploy

1. Mergear os PRs (ordem acima). App = Vercel (push `master`, Felipe); growth =
   `ssh master@72.60.4.71 'sudo git -C /cadencia pull origin main'` + `drift_check.sh`.
2. Aplicar a migration `contacts` no Supabase (vem do PR app).
3. Subir o **daemon de scoring** (sobrevive a reboot):
   ```
   # crontab -e (root) na VPS — mesmo padrão dos outros daemons (@reboot)
   @reboot /usr/bin/python3 /cadencia/scoring/resend_webhook.py >> /cadencia/logs/scoring_resend.log 2>&1 &
   ```
   ⚠️ Resend exige **HTTPS** — expor a porta 8767 via reverse proxy (TLS) e usar
   essa URL no webhook do Resend.
4. **Transacional** (paralelo, sem código): no painel do Supabase Auth, configurar
   Custom SMTP apontando pro `smtp.resend.com` → reset de senha sai pelo Resend.

## Cutover (tenant-piloto)

```bash
# 0. contacts JÁ migrados (~7685) via RPC import_ghl_contacts_batch — re-rodar é idempotente:
#    python3 scripts/migrate_ghl_contacts.py --tenant <TID>           # dry-run
#    python3 scripts/migrate_ghl_contacts.py --tenant <TID> --apply   # via RPC batch (CAD-566)
# 1. PRÉ-REQ: CNAME redirect verificado no Resend (senão clique não rastreia) — ver topo.
# 2. ligar o Resend (global por env; valide com 1 tenant antes de migrar a base):
#    setar EMAIL_PROVIDER=resend no .env  +  warm-up (subir volume gradual no domínio frio)
# 3. disparar e validar (envio chega no inbox + email.opened/clicked sobem o score)
```

## Validação (ciclo completo)

- [ ] **Pré-flight:** `python3 scripts/email_resend_preflight.py` → tudo `OK`/`READY`
      (checa EMAIL_PROVIDER, RESEND_API_KEY, domínio verificado, webhook secret,
      tabela `contacts` populada). É o gate automático dos pré-reqs.
- [ ] Envio: Seinfeld/newsletter chegam (inbox, não spam) — checar SPF/DKIM/DMARC `pass` no header.
- [ ] Scoring: abrir/clicar → `contacts.score`/`temperatura` sobem + row em `scoring_events`.
- [ ] Suppression: bounce/complaint → `contacts.status` muda; contato sai dos envios.
- [ ] Unsubscribe: link do rodapé + one-click do Gmail → `status=unsubscribed`.
- [ ] `content_readiness.py` / queries no Supabase batem com o esperado.

## Continuidade do score (importante)

A migração cria os contatos com `score=0` — **não** importa o `contact.score_ia`
acumulado do GHL (o list endpoint do GHL não traz custom fields de forma confiável;
backfill exigiria 1 GET por contato). Impacto real é baixo (o score hoje é pouco
consumido a jusante e **re-acumula** por abertura/clique após o cutover). Se a
continuidade for crítica para algum tenant, rodar um backfill pontual
(`GET /contacts/{id}` → `score_ia` → `contacts.score`) **antes** de ligar o Resend.

## Rollback

O rollback para GHL foi aposentado e não deve ser usado. Em incidente, pausar o
envio Resend e corrigir o CRM Cadencia preservando dedup e flags.

## Rollout

Validado o piloto, ligar `EMAIL_PROVIDER=resend` para todos + rodar
`migrate_ghl_contacts.py --all --apply`. Manter o **warm-up** de volume do domínio.

## Depois (fora deste runbook)

`ghl_contact_id` em `contacts` é a ponte de transição. Quando CRM/social saírem do
GHL, descartar a coluna e desligar o `webhook_handler.py` (GHL) e os tokens de location.
