# Email cutover GHL→Resend + motor de warm-up (CAD-675)

> **Cutover concluído.** Todos os tenants e canais ativos operam sem GHL. As referências abaixo ao rollout gradual são históricas; a parte viva deste documento é o motor de warm-up Resend.

> Migra o envio de email (Seinfeld diário + newsletter semanal) do GHL para o Resend, por tenant, com ramp de aquecimento, priorização por engajamento e toggle por lead. Parte de "desligar o GHL".

## Identidade
- **Tipo:** lógica nos scripts de envio (cadencia-growth) + migração no schema (cadencia-app)
- **Paths:** `pipeline/email_warmup.py`, `pipeline/lib_api.py` (`get_subscribed_contacts`), `pipeline/seinfeld_generate.py`, `pipeline/newsletter_generate.py`
- **Schema:** `contacts.auto_email_enabled` (cadencia-app `supabase/migrations/20260620010000_*`)
- **Status:** **LIVE** — Resend ativo para todos os tenants; GHL desligado

## As 4 partes

### 1. Provedor per-tenant
`email_warmup.resolve_email_provider(config)` mantém compatibilidade com configurações antigas, mas o estado operacional válido é `resend`. Aplicado em `seinfeld_generate` e `newsletter_generate`; não usar o valor legado `ghl` como rollback.

### 2. Motor de warm-up
`email_warmup.warmup_daily_cap(config, today)` → cap de envios do dia.
- Lê `config.email_warmup.start_date` + `config.email_warmup.stages` (**editável via painel admin**).
- Sem `start_date` → `None` (sem cap, assume aquecido). Antes do start → `0` (não envia). Dentro de um estágio → o cap. Após o último → `None`.
- Default (`DEFAULT_WARMUP_STAGES`): dia 1-2=50, 3-4=100, 5-7=250, 8-10=500, 11-14=1000, 15+=ilimitado.
- Robustez: stages ordenados por `through_day` (admin pode salvar fora de ordem); `cap=max(0,int)` (cap negativo quebraria PostgREST); `except Exception` no sort (lista de não-dicts não derruba o cron — achado GLM 5.2).

### 3. Priorização por engajamento
`lib_api.get_subscribed_contacts(tenant_id, limit)` agora: `order=score.desc.nullslast` → dentro do cap, os leads com maior probabilidade de abrir recebem primeiro. Índice parcial `idx_contacts_dispatch_priority` suporta a ordenação.

### 4. Toggle por lead
`contacts.auto_email_enabled` (boolean NOT NULL default true). `get_subscribed_contacts` filtra `auto_email_enabled=eq.true`. UI do toggle = frontend (follow-on). Aplica a TODO tenant no caminho Resend.

## Aplicação no envio
- **Seinfeld** (`run_dispatch`): `provider = resolve_email_provider(config)`; se resend, `cap = warmup_daily_cap(config, hoje BRT)`; `cap==0`→skip; `get_subscribed_contacts(tenant_id, limit=cap)`.
- **Newsletter** (`run`): mesmo tratamento. `BRT = timezone(-3)` (faltava). From fixo `noreply@cadencia.app.br` (até CAD-676 dar domínio próprio).
- HTML por tenant em ambos: `get_visual_identity` → `render_email_html`/`render_newsletter_html` (palette/fonts/brand) → `resend_send(html=...)`.

## Go-live (estado)
- **Domínio Resend verificado:** `cadencia.app.br` (DKIM). `cadencia.ia.br` = Hostinger (caixa felipe@, serve de reply-to).
- **Flipados:** PD (`email_provider=resend`, `warmup.start_date=2026-06-19`, 4938 elegíveis, cap dia1=50) + Orsolon (36).
- **Test send** validado na inbox (autentica via DKIM).
- **`/api/unsubscribe`** live (307) · CNAME `redirect` de tracking existe.

## ⚠️ Rollout dos legados (pendente — fazer depois)
Risco histórico do cutover: tenants sem contatos migrados ficavam sem audiência. A migração foi concluída; hoje a fonte única é `public.contacts`. Monitorar audiência vazia diretamente no CRM Cadencia.

## Direção futura (CAD-676)
Domínio compartilhado `cadencia.app.br` é interim. Modelo final: **subdomínio Cadência auto-provisionado por tenant** (`<slug>.cadencia.app.br`, DNS via Cloudflare API + Resend Domains API, reputação isolada) + opção de domínio próprio. Resolve o risco de reputação compartilhada.

## 🚫 Don'ts / gotchas
- Não flipar tenant pra resend sem garantir contatos no CRM (regressão silenciosa).
- Cap é **per-tenant** mas a reputação do domínio compartilhado é **global** — flipar muitos de uma vez soma volume (mitigado pelo subdomínio por tenant, CAD-676).
- Warm-up `start_date` deve ser data **BRT**.
- **Rate limit do Resend (DEV-1041):** o dispatch envia com 10 workers concorrentes
  (`SEINFELD_DISPATCH_WORKERS`), dimensionado pro GHL. O Resend limita ~2 req/s →
  sem pacing dava **storm de 429**. `lib_api.resend_send` agora serializa por
  `RESEND_MAX_RPS` (env, default 2). Se o plano do Resend permitir mais, sobe a env;
  `0` desliga. Cap de warm-up limita volume/DIA; este limita req/SEGUNDO — são coisas
  diferentes. Throughput real acima do rate-limit = Resend **batch API** (follow-up).

## Refs
- Review §6: `docs/codex-reviews/codex-review-19-06-2026-cad675.md` (qwen + GLM 5.2)
- Runbook original: `docs/email-resend-migration.md`
- Convenção review (GLM 5.2 + qwen): memória `feedback-review-models`
