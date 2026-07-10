> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `CONTEXT.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/CONTEXT.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# CONTEXT — Linguagem ubíqua do Cadência

> Termos do domínio com definição direta. Quando um agente diz "tenant", "editorial", "dossier" — significa exatamente o que está aqui. Ambiguidades flagadas como ⚠️.

## Entidades principais

**Tenant** — Cliente do SaaS Cadência. Cada tenant tem seu próprio `tenant_id`, `tenant_config`, créditos, planos, posts, dossier, editoriais e subconta GHL. Multi-tenancy via RLS Supabase (não DBs separados). Ver [ADR-0006](docs/adr/0006-multi-tenant-rls-supabase.md).

**Tenant config** — Linha em `tenant_config` por tenant com JSON `config` contendo: `ghl.location_id`, `ghl.location_pit_token`, `ghl.white_label_url`, `ghl.pipeline_id`, `ghl.pipeline_stages`, `ghl.score_ia_field_key`, branding, preferências de geração.

**Dossier** — Perfil de marca gerado pelo worker `dossier.py` na fase de onboarding. Guarda voz, valores, público, restrições. Insumo para todo conteúdo gerado depois. Tabela `tenant_dossier`.

**Editorial** — Cada tenant tem 3 editoriais (pilares de conteúdo). Gerados pelo worker `editorials.py` no onboarding. Tabela `editorials`. Toda `content_idea` pertence a 1 editorial (FK `editorial_id`).

**Content idea** — Ideia de post antes de virar conteúdo finalizado. Pode entrar pelo chat (`chat-ideias`) ou pelo gerador automático (`ideas-generator`). Tabela `content_ideas`. Status: `pending`, `approved`, `discarded`, `generated`.

**Published post** — Conteúdo finalizado (carrossel, blog, seinfeld, newsletter, linkedin, instagram). Tabela `published_posts`. Campos por canal: `seinfeld_subject`/`seinfeld_body`/`seinfeld_scheduled_at`/`seinfeld_sent`, `newsletter_included`, etc.

**Sub-preset (visual)** — Variação visual de identidade do tenant. 15 presets disponíveis no onboarding. Define paleta, tipografia, layout do carrossel.

## Identidade / Onboarding

**Onboarding** — Processo de 3 fases (fase 1 = signup + dados básicos, fase 2 = dossier + editoriais, fase 3 = visual + publish first post). Tabela `tenant_onboarding`. Tenant só recebe pipeline diário quando `onboarding_completed`.

**Identity Lock** — Mecanismo de geração de cover do carrossel via Gemini 2.5 Flash que mantém consistência visual (rosto/cores/composição) entre posts do mesmo tenant.

**Provisioning** — Criação automática de subconta GHL para um tenant novo, via `provision_tenant.py` (VPS). Bloqueado atualmente por PDL-25 (OAuth agency vazio).

## GHL (motor invisível)

**Location** — Subconta GHL de um tenant. Identificada por `location_id`. Cada tenant tem a sua. Cadência também tem uma **location central** (`PrAh9rKjmpUkElCu5KBI`) usada apenas pelos workers do `cadencia-app` para tracking lifecycle (signup, trial, churn).

**Location PIT token** — Private Integration Token da location do tenant. Permite chamar API GHL no contexto daquela subconta. **NÃO confundir com `api_key`** — são tokens distintos. Seinfeld e scoring exigem `location_pit_token`. Ver [ADR-0005](docs/adr/0005-location-pit-token-por-tenant.md).

**Agency OAuth** — Token OAuth no nível de Company (agência) que gera location tokens via `POST /oauth/locationToken`. Guardado em `ghl_agency_oauth`. Hoje vazio → bloqueio PDL-25.

**White-label URL** — Domínio brancado do GHL daquele tenant. Usado para abrir CRM/contatos direto pelo frontend (`tenant_config.config.ghl.white_label_url`).

**Pipeline (GHL)** — Funil comercial dentro do GHL. Cada tenant tem o seu (`config.ghl.pipeline_id`). Cadência tem o "Cadencia App [Clientes]" (`dJ9sF3kuYcVtWvN9QJJQ`) para tracking dos próprios clientes.

**Stage** — Fase dentro de um pipeline GHL. Stages padrão da Cadência: `trial`, `nao_avancou`, `cliente_ativo`, `churn`. Stages do tenant variam (configurados no onboarding).

## Geração de conteúdo

**Pipeline (interno Cadência)** — Sequência diária de geração por tenant, orquestrada por `growth_pipeline.py` (cron 11h BRT VPS). Ordem: `sync → blog → seinfeld --generate → seinfeld --dispatch → newsletter → linkedin → instagram`. Carrossel/reels NÃO entram no pipeline VPS — vão por Railway. Ver [ADR-0004](docs/adr/0004-carrossel-railway-resto-vps.md).

**Trigger on-demand** — Geração disparada quando usuário aprova uma ideia. Endpoint `/api/app/trigger-generation` (Vercel) filtra canais: `carrossel`/`reels` → Railway workers; resto → `VPS:39090/trigger`. Newsletter é **silenciosamente ignorada** no trigger (G002).

**Generation queue** — Tabela `generation_queue` (planejada para refator PDL-171) para coordenar jobs entre workers e VPS. Hoje a coordenação é por mistura de `trigger_server.py` + cron + status em `published_posts`.

**Sync** — Step do pipeline que sincroniza estado do tenant com GHL antes de gerar (contatos, opportunities). Sempre roda primeiro.

**Dispatch (Seinfeld)** — Envio real do email Seinfeld via `POST /conversations/messages` GHL. Acontece em cron 11h BRT diário. Pega só posts agendados para `hoje` exato — posts com `seinfeld_scheduled_at` no passado ficam presos (G001).

## Growth (VPS)

**Growth pipeline** — Mesmo que pipeline interno acima. Rodado por `/cadencia/crons/growth_pipeline.py`.

**Seinfeld email** — Email diário no estilo "Jerry Seinfeld" (storytelling curto, sem CTA agressivo). Gerado a partir de `published_posts` que ainda não foram usados como Seinfeld (`seinfeld_sent=false AND seinfeld_scheduled_at IS NULL`).

**Newsletter** — Compilação semanal de artigos da semana. Dispara sexta 15h BRT. Não disponível no trigger on-demand.

**Scoring** — Lead scoring por evento GHL. Webhook handler em VPS:8766 recebe eventos `email_opened`/`link_clicked`. Soma pontos em `contact.score_ia` (custom field GHL). Score bands: Frio (<30), Aquecendo (≥30), Quente (≥60), Hot (≥80). Ver [ADR-0005](docs/adr/0005-location-pit-token-por-tenant.md).

**Mission Control** — Dashboard HTML em VPS:8768 (`/cadencia/mission_control.py`) para Felipe ver estado dos tenants em tempo real.

## Workers (Railway)

**Orchestrator** — Worker principal `pipeline-orchestrator` (7 steps) que coordena geração de carrossel/reels via Railway. Diferente do `growth_pipeline.py` (que roda VPS e cobre blog/seinfeld/linkedin/instagram).

**Theme engine** — Worker que escolhe tema visual para um post baseado no dossier + editorial + sub-preset.

**Chat agent** — Worker do "Tenho uma ideia" — conversa com usuário, captura ideia, devolve para `content_ideas`. Ver [ADR-0002](docs/adr/0002-chat-agent-design.md).

**RAG memory** — Memória de contexto do agente: histórico de posts do tenant, conversas chat, dossier. Usado para evitar repetição e manter coerência.

## Billing / Planos

**Plan** — Plano comercial. Hoje: `trial`, `essencial`, `starter`, `growth`, `growth_pro`. Cada um define cota de créditos e quais canais geram diariamente. Tabela `tenant_plans` — tenant pode ter múltiplos planos ativos (créditos somam).

**Crédito** — Unidade de geração. Cada post gerado consome créditos do tenant. Tenant com 0 créditos é skipado pelo pipeline (exceto sync + newsletter).

**Stripe** — Gateway de pagamento. Substituiu Asaas em 11/05/2026. Ver [ADR-0001](docs/adr/0001-stripe-em-vez-de-asaas.md).

## Tracking / Analytics

**CAPI** — Conversions API do Meta. Endpoint `/api/capi/*` envia eventos server-side para Meta Pixel (deduplicação client+server).

**Stevo** — Bot WhatsApp do Felipe (não brancado). Usado para notificações internas (deploy, incidentes, status semanal). Endpoint `/api/stevo/*`.

## Ambiguidades flagadas ⚠️

- ⚠️ **"Pipeline"** pode significar (a) pipeline interno Cadência de geração, (b) pipeline GHL (funil comercial). Sempre desambiguar pelo contexto.
- ⚠️ **"Token"** sem qualificador é ambíguo. Sempre dizer: `api_key`, `location_pit_token`, `agency_oauth_token`, `supabase_service_role`, `stripe_secret`.
- ⚠️ **"GHL"** pode ser (a) a location central da Cadência, (b) a location do tenant. Sempre dizer "GHL central" vs "GHL do tenant".
- ⚠️ **"Worker"** pode ser (a) worker Railway (`cadencia-workers/`), (b) script Python rodando na VPS (`/cadencia/`). VPS scripts são chamados de **growth scripts** quando o contexto exige desambiguação.
- ⚠️ **"Generation"** sem canal é ambíguo. Sempre dizer: geração de carrossel, blog, seinfeld, linkedin, instagram, reels, newsletter.

## Relacionamentos

```
Tenant ── tem ──► Tenant config ── tem ──► GHL location (PIT token)
   │                                            │
   ├── tem ──► Dossier                          ├── recebe ──► Seinfeld dispatch
   ├── tem ──► 3 Editoriais ──┐                 ├── publica ──► Workflows scoring
   │                          │                 └── armazena ──► Contatos
   ├── gera ──► Content ideas◄┘
   │            │
   │            ▼
   ├── gera ──► Published posts ──► (carrossel/blog/seinfeld/linkedin/instagram/newsletter)
   │
   ├── compra ──► Tenant plans ──► Créditos
   └── progride ──► Tenant onboarding (3 fases)
```

## Referências

- [docs/architecture.md](docs/architecture.md) — Diagrama C4 dos containers e fluxos
- [CLAUDE.md](CLAUDE.md) — Manual operacional do repo
- [docs/adr/](docs/adr/) — Decisões arquiteturais
