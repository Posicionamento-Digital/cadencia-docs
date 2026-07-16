# Contratos de Estado — Cadência

> **REGRA (obrigatória):** criar, alterar ou re-significar QUALQUER status/flag de
> tabela compartilhada ⇒ (1) atualizar este documento; (2) `grep` de TODOS os
> consumidores nos 3 repos (`cadencia-growth`, `cadencia-app/src`,
> `cadencia-app/cadencia-workers/src`). O bug cleanup×`dispatched` (jun/2026)
> nasceu de um status novo (PDL-171) que um consumidor de 1 dia antes (PDL-167)
> não conhecia. Este doc existe pra essa classe de bug nunca voltar.

As 4 superfícies de deploy (Vercel, VPS growth, Coolify VPS Master, Supabase) se comunicam por
estas flags — elas são a API interna do sistema. Última revisão: 2026-06-11
(auditoria técnica).

---

## published_posts (1 row = 1 ideia publicada; blog cria, canais marcam flags)

### `status`
- **Valores:** `published` (na prática, 100% das rows).
- **Escritor:** `blog_generate.py` no INSERT.
- **Leitores:** dashboard "no ar" (`cadencia-app/src/app/(app)/app/page.tsx`),
  geradores de canal (filtram `status=eq.published`).

### `seinfeld_sent` / `seinfeld_subject` / `seinfeld_body` / `seinfeld_scheduled_at`
- **Significado de `sent=true`:** dispatch do email COBRIU todos os contatos
  elegíveis do dia (zero falhas transitórias; falhas PERMANENTES — DND/4xx —
  não seguram o flag).
- **Escritores:** `seinfeld_generate.py --generate` (subject/body/scheduled_at);
  `--dispatch` (sent, só com `transient_fail == 0`).
- **Leitores:** `--generate` (próximo post: `scheduled_at IS NULL`), `--dispatch`
  (janela `hoje-3d..hoje`, `sent=false`), `email-stats` (frontend),
  `newsletter_generate` indireto.
- **Idempotência do dispatch:** `seinfeld_daily_sent` (abaixo).

### `linkedin_sent` / `linkedin_text` / `linkedin_scheduled_at`
- **Significado de `sent=true` (desde Fase 2 da auditoria):**
  - com conta conectada: publicação/agendamento CONFIRMADO pelo provider ativo (2xx) — `scheduled_at` preenchido;
  - sem conta conectada: "processado" — texto gerado e disponível no dashboard
    pra uso manual; a fila progride. (`sent=true` + `scheduled_at=null` + conta
    configurada = órfão legado pré-Fase-2.)
- **Escritor:** `linkedin_generate.py` (texto salvo separado; sent só no sucesso
  do agendamento OU no caminho sem-conta).
- **Leitores:** o próprio gerador (próximo post `sent=false`; âncora de slot por
  `scheduled_at`); aba LinkedIn do dashboard lê `linkedin_text` (NÃO a flag).
- **Retry:** falha do provider ⇒ `sent=false`; próximo ciclo REUTILIZA `linkedin_text`
  (sem custo LLM).
- **DEV-476 (reconciliação com `channels_published`):** `'linkedin'` só entra em
  `channels_published` no MESMO momento em que `linkedin_sent` vira `true` pelo
  agendamento confirmado no provider (2xx) — nunca no caminho sem-conta (aí só o texto
  fica disponível pra uso manual, sem publicação real). Antes disto, `linkedin_generate.py`
  nunca escrevia `channels_published` (só `instagram_generate.py`, desde PDL-470,
  fazia essa reconciliação) — todo tenant com LinkedIn confirmado acumulava
  `linkedin_sent=true` com `channels_published=['blog']` (bookkeeping mentiroso).

### `instagram_sent` / `instagram_text` / `instagram_scheduled_at`
- Igual ao LinkedIn (mesma semântica Fase 2). ⚠️ Coluna `instagram_sent` existe
  em prod mas NÃO nas migrations (drift — PDL-172).

### `channels_published` (text[])
- **Significado:** canais com publicação REAL confirmada. `['blog']` no INSERT;
  `'instagram'` = carrossel agendado; `'instagram_image_fallback'` = só imagem
  (carrossel pendente — PDL-470); `'linkedin'` = post agendado no provider social
  confirmado (2xx) (DEV-476). Desde a Fase 2, tags de IG/LinkedIn só
  entram com o agendamento confirmado — NUNCA no caminho sem-conta (aí `*_sent`
  vira `true` mas não há publicação real, só texto disponível pra uso manual).

### `newsletter_included`
- `true` = post já saiu numa newsletter (marca só com ≥1 envio OK — PDL-87).
- Escritor/leitor: `newsletter_generate.py` (pool = `false`, sem filtro de data).

## content_ideas

### `status`: `pending → approved → used` (e `processing`, workers Coolify VPS Master)
- `pending→approved`: frontend (aprovação).
- `approved→used`: `blog_generate.py` ao publicar (PDL-468) e orchestrator
  workers Coolify VPS Master ao completar carrossel.
- `approved` sem job >10min: `cleanup_orphan_ideas.py` cura → `used` (se tem
  published_post) ou `pending` (órfã — re-aprovar). Job ativo = generation_queue
  em `pending/processing/completed/dispatched`.
- ⚠️ Não existe transição para `rejected`; `processing` preso é resetado pelo
  cleanup-stuck dos workers Coolify VPS Master (quando rodar) ou fica até intervenção.

## generation_queue

### `status`
- `pending`: aguardando consumo — workers Coolify VPS Master (carrossel) ou modo fila do
  `blog_generate` (APENAS rows com `channels` contendo `blog`).
- `processing/completed/failed`: ciclo do orchestrator (workers Coolify VPS Master).
- `dispatched`: **registro de aprovação multi-canal** (frontend) — NÃO é fila;
  nenhum worker consome; `blog_generate` fecha como `completed` ao publicar
  (direct mode). Consumidores que checam "job ativo" DEVEM incluir `dispatched`.
  Desde DEV-1082, o `trigger_server` fecha como `failed` (+`error_message`)
  quando o blog falha num run idea-specific — a row não fica mais `dispatched`
  pra sempre e o cleanup de órfãs pode reciclar a ideia se nenhum job restar ativo.
- `in_progress`: usado pelo modo fila do blog na VPS.

### `channels` (text[]) vs `channel` (text, legado)
- Canônico: `channels` (array). `channel` singular existe em prod por drift
  (versionado em 20260610210000); nenhum código lê.
- Filtro de canal usa `channels=cs.{blog}` URL-encoded (`%7B%7D` — curl globba `{}`).

## content_documents (carrosséis, workers Coolify VPS Master)

### `status`: `generating → ready | render_failed`
- ⚠️ `_fail_job` do orchestrator NÃO marca o doc em falhas fora do render ⇒ docs
  zumbis em `generating` (PDL-473).
- Dashboard conta "prontos" = `ready` + `published_at IS NULL`, deduplicado por
  `idea_id` (multi-version: N docs por ideia = 1 card).

### `publish_status`: `draft → ...` (publicação manual via frontend)
- ⚠️ Frontend hoje só olha `status='ready'`; `publish_status` é subutilizado.

## seinfeld_daily_sent (dedup por contato/dia)
- UNIQUE (tenant, contact, sent_date). INSERT antes do envio (409 = já recebeu
  hoje ⇒ pular); DELETE em falha de envio (permite retry same-day).
- `sb_insert` contrato: `list` = ok | `[]` = 409 (dedup) | `None` = erro real.

## tenant_config.config (JSON)
- `growth_channels[]`: gate de GERAÇÃO por canal (vazio/ausente = todos).
- `email`: configuração canônica de envio, domínio, tracking e warm-up.
- `cadence`: configuração do motor de cadências; estado de execução vive nas tabelas próprias.
- Credenciais de providers externos ficam server-side e nunca são enviadas ao frontend.

**Regra de escrita (nível-1):** quem mexe em chaves de nível-1 do `config` (ex.: o
`provision_tenant.provision()` grava `blog`/`plan_tier` no save final) deve usar
`lib_api.merge_tenant_config(tenant_id, patch)` (RPC `merge_tenant_config`, DEV-975) —
merge RASO atômico sob row lock, com o `patch` contendo SÓ as chaves alteradas. NUNCA
read-modify-write do `config` inteiro via `sb_patch` montado de um snapshot antigo: a
janela do provision é de minutos (blog smoke ~52s + email verify ~80s) e qualquer
escrita concorrente de OUTRO fluxo (CRM/admin/onboarding) nas chaves-irmãs seria
clobberada (risco R1/P3-A). `email` NÃO entra nesse patch — tem casa própria via
`merge_email_config` (merge ANINHADO; ver abaixo). ⚠️ `merge_tenant_config` é raso: pra
mexer SÓ num campo dentro de um sub-objeto (ex.: `config.email`) sem clobberar os irmãos
dele, use a RPC aninhada dedicada, não esta. DDL da RPC base:
cadencia-app `supabase/migrations/20260630000000_merge_tenant_config_rpc.sql` (DEV-975) —
**APLICADA em prod 30/06**.

## tenant_config.config.email (objeto unificado — DEV-954)
Objeto que consolida os campos de email do tenant, historicamente espalhados em
campos **flat** (`email_sender_address`, `email_sender_name`, `email_domain`,
`email_provider`, `email_sending_enabled`, `email_warmup`). Estado da transição:
- **Fase 0** (getters): leitura **objeto-primeiro / flat-fallback** (behavior-neutral).
- **Fase 1** (backfill): `config.email` já é OBJETO `schema_version:2` em prod; as
  flat keys ficam como ESPELHO.
- **Fase 2** (writers atômicos): toda escrita de `config.email` passa pela RPC
  `merge_tenant_config_email` (helper `lib_api.merge_email_config`) — merge ANINHADO
  e ATÔMICO, sem read-modify-write do config inteiro (fecha o risco R1 de clobber
  concorrente). A casa ÚNICA do estado é o objeto aninhado; o root flat é só espelho
  de transição (gravado idêntico via `p_flat_mirror`), removido na Fase 4.

Campos:
- `schema_version` (int): `2` para o schema-objeto.
- `contact_address` (str): endereço de contato/reply do tenant. (Legado: quando
  `config.email` veio como **string** crua, ela é lida como `contact_address`.)
- `sender_address` (str): From do envelope (fallback flat `email_sender_address`).
- `sender_name` (str): display name do From (fallback flat `email_sender_name`).
- `sending_domain` (str): domínio de envio dedicado (fallback flat `email_domain`).
  **Namespace de email (FIX 1, 30/06):** tenant NOVO é provisionado em
  `<slug>.mail.cadencia.app.br` (subdomínio normal sob `mail.cadencia.app.br`), NÃO em
  `<slug>.cadencia.app.br` — este é o CNAME do BLOG (Vercel). Pra nomes de 1-2 palavras
  o slug de email == slug do blog, então o domínio de envio caía SOBRE o CNAME do blog e
  o guard de tracking ("pai é CNAME") pulava o tracking. O segmento `mail` vive na
  constante `MAIL_DOMAIN` (`sending_domains.py`; decisão de produto, trocável). Tenants
  ANTIGOS (verified em `<nome>.cadencia.app.br`) são reusados AS-IS — não migram.
- `resend_domain_id` (str): id do domínio no Resend (provisioning per-tenant). Casa
  ÚNICA = aqui (aninhado); o root flat `resend_domain_id` é só espelho de transição.
- `provider` (`resend` | null): `resend` é o único valor operacional; null resolve para Resend.
- `verification_status` (str): status de verificação DNS do domínio no Resend.
- `tracking_enabled` (bool): open/click tracking de fato ATIVO — flags ligados no Resend
  **+ CNAME `redirect.<sub>` publicado no Cloudflare E o domínio `verified`**. Ligado
  AUTOMÁTICO no provisioning (DEV-954) pelos DOIS caminhos (`provision_tracking` em
  `sending_domains.py`) — sem isto o tenant envia mas não pontua engajamento. **FIX 3
  (30/06):** reflete a REALIDADE — só é `true` quando `tracking_status=='verified'`; em
  `pending` (DNS propagando, tracking ainda não no ar), `failed` ou `skipped` fica
  `false` (o `tracking_status` preserva o porquê e um provision futuro re-verifica). NÃO
  é gate de envio (campo só de estado/telemetria). Guard: se o `<fqdn>` já é CNAME
  (cliente com site no Vercel), o tracking é PULADO (`false` + `tracking_note`).
- `tracking_status` (str): status do domínio no momento de ligar o tracking
  (`pending|verified|...`) ou `skipped`/`failed` no edge-case/erro.
- `tracking_note` (str, opcional): motivo de `tracking_enabled:false` (ex. `pai é CNAME
  (site) — tracking incompatível`).
- `provisioned_at` (timestamp): quando o domínio foi provisionado.
- `sending_enabled` (bool): master liga/desliga de envio (fallback flat
  `email_sending_enabled`; parse defensivo de `'false'/'0'/'no'/'off'`).
- `warmup` (obj): `{start_date, stages[]}` do ramp (fallback flat `email_warmup`).
- `cta_label` / `cta_label_seinfeld` / `cta_label_newsletter` (str, **DEV-357**): texto do
  botão/CTA do email, personalizável por tenant E canal. Precedência (getter
  `email_cta_label`): `cta_label_<canal>` → `cta_label` (genérico) → default do canal
  (`Ler artigo completo` no Seinfeld, `Ler artigo` na newsletter).
- `preheader` / `preheader_seinfeld` / `preheader_newsletter` (str, **DEV-357**):
  preview-text do inbox (o texto após o subject). Presença = override "manual";
  ausência = "auto" — o getter `email_preheader` deriva da 1ª frase do corpo (~100
  chars). Ordem: `preheader_<canal>` → `preheader` → fallback (preheader do LLM, na
  newsletter) → auto-derivado do corpo. Garante NÃO-VAZIO sempre que houver corpo
  (preheader vazio custava 20-30% de open rate; o Seinfeld ia com `''` antes do DEV-357).
- `from_name` / `from_email` (str, **DEV-357**): APELIDOS de `sender_name`/`sender_address`
  (nomes do schema exposto na UI). Os getters `email_sender_name`/`email_sender_address`
  aceitam ambos; o canônico (`sender_*`, gravado pelo provisioning) vence o apelido.
  `from_email` custom = domínio próprio do cliente (Fase 4, adiado p/ OPS-9); hoje o
  isolamento de reputação já vem do subdomínio dedicado por tenant (`sending_domain`).

**Regra de acesso:** acessar SEMPRE via os getters de `pipeline/email_warmup.py`
(`email_sender_address`, `email_sender_name`, `email_sending_domain`,
`email_contact_address`, `email_cta_label`, `email_preheader`, `resolve_email_provider`,
`email_sending_enabled`, `warmup_daily_cap`, e `email_cfg`) — objeto-primeiro com
fallback flat durante a transição; nunca ler `config['email_*']` direto. Valor vazio
(`''`) no objeto conta como ausente e cai no flat. Os getters nunca levantam.

**Regra de escrita:** gravar SEMPRE via `lib_api.merge_email_config(tenant_id,
email_patch, flat_mirror)` (RPC `merge_tenant_config_email`) — manda SÓ os campos que
mudaram (`email_patch`, merge aninhado preserva o resto) + o espelho flat de transição
(`flat_mirror`). NUNCA fazer read-modify-write do `config` inteiro via `sb_patch` pra
mexer em email (abre o clobber concorrente R1). Writers: `sending_domains.py`
(`provision_sending_domain`) e `provision_tenant.py` (`provision_resend_email_domain`).
A RPC é DDL (`migrations/20260630_merge_tenant_config_email_rpc.sql`) — **APLICADA em prod
30/06** (junto com a `merge_tenant_config` base, DEV-975). Dois detalhes do .sql vivo:
(a) **guard `jsonb_typeof`** — o merge só roda quando `config.email` já é um OBJETO; se
fosse a STRING legada, `'"str"'::jsonb || '{...}'::jsonb` faria concat de ARRAY e
corromperia o config (vira `["str", {...}]`); (b) **`revoke execute ... from anon,
authenticated`** além do `revoke from public` — o Supabase concede EXECUTE default a esses
roles, que `from public` não cobre.

## tenant_plans
- `status`: `active | grace | refunded | ...`. **Crédito válido = active+grace**
  (GET e débito — a RPC `debit_credits` em prod ainda só olha `active`; fallback
  CAS na route cobre `grace` até a RPC ser corrigida — PDL-169/bundle Felipe).

## contacts (fonte de contatos no Supabase)
- UNIQUE (tenant_id, email) — email SEMPRE lowercased na escrita (upsert idempotente
  via `on_conflict=tenant_id,email`). Telefone não participa da UNIQUE.
- `status`: `subscribed | unsubscribed | bounced | complained` — **suppression embutida**;
  o envio (`get_subscribed_contacts`) filtra `status=subscribed`.
- `score` (int) / `temperatura`: acumulador de scoring.
  Atualizado pelo webhook do Resend (PR-3) via tag `contact_id`.

## EMAIL_PROVIDER (Resend)
- `seinfeld_generate.py` e `newsletter_generate.py` usam contatos do Supabase e
  `lib_api.resend_send`, com tags `{tenant_id, contact_id}` para scoring.
- Dedup (`seinfeld_daily_sent`) e flags (`seinfeld_sent`/`newsletter_included`)
  permanecem independentes do transporte.
