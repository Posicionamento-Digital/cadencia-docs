# CONTEXT — Linguagem ubíqua do Cadência

> Termos do domínio com definição direta. Quando um agente diz "tenant", "editorial", "dossier" — significa exatamente o que está aqui. Ambiguidades flagadas como ⚠️.

## Entidades principais

**Tenant** — Cliente do SaaS Cadência. Cada tenant tem seu próprio `tenant_id`, `tenant_config`, créditos, posts, dossier, editoriais e CRM. Multi-tenancy via RLS Supabase (não DBs separados). Ver [ADR-0006](docs/adr/0006-multi-tenant-rls-supabase.md).

**Tenant config** — Linha em `tenant_config` por tenant com JSON `config` contendo branding, preferências de geração, email, canais e flags operacionais. Entidades do CRM vivem em tabelas próprias.

**Dossier** — Perfil de marca gerado pelo worker `dossier.py` na fase de onboarding. Guarda voz, valores, público, restrições. Insumo para todo conteúdo gerado depois. Tabela `tenant_dossier`.

**Editorial** — Cada tenant tem 3 editoriais (pilares de conteúdo). Gerados pelo worker `editorials.py` no onboarding. Tabela `editorials`. Toda `content_idea` pertence a 1 editorial (FK `editorial_id`).

**Content idea** — Ideia de post antes de virar conteúdo finalizado. Pode entrar pelo chat (`chat-ideias`) ou pelo gerador automático (`ideas-generator`). Tabela `content_ideas`. Status: `pending`, `approved`, `discarded`, `generated`.

**Published post** — Conteúdo finalizado (carrossel, blog, seinfeld, newsletter, linkedin, instagram). Tabela `published_posts`. Campos por canal: `seinfeld_subject`/`seinfeld_body`/`seinfeld_scheduled_at`/`seinfeld_sent`, `newsletter_included`, etc.

**Sub-preset (visual)** — Variação visual de identidade do tenant. 15 presets disponíveis no onboarding. Define paleta, tipografia, layout do carrossel.

## Identidade / Onboarding

**Onboarding** — Processo de 3 fases (fase 1 = signup + dados básicos, fase 2 = dossier + editoriais, fase 3 = visual + publish first post). Tabela `tenant_onboarding`. Tenant só recebe pipeline diário quando `onboarding_completed`.

**Identity Lock** — Mecanismo de geração de cover do carrossel via Gemini 2.5 Flash que mantém consistência visual (rosto/cores/composição) entre posts do mesmo tenant.

**Provisioning** — Criação do tenant, carteira inicial, pipelines/stages/tags/campos do CRM próprio, domínio Resend/DNS e artefatos de marca. Orquestrado pelo app e por `provision_tenant.py`.

## CRM Cadencia

**Contato** — Pessoa do CRM em `public.contacts`, sempre isolada por `tenant_id`.

**Empresa** — Organização relacionada a contatos em `public.companies`.

**Pipeline** — Funil comercial do tenant, identificado por slug estável e composto por stages ordenados.

**Stage** — Fase dentro de um pipeline do CRM Cadencia. Automações usam slugs, não IDs externos.

**Oportunidade** — Relação comercial entre contato, pipeline e stage, com valor, status e atividades.

## Geração de conteúdo

**Pipeline (interno Cadência)** — Sequência diária de geração por tenant, orquestrada por `growth_pipeline.py` (cron 11h BRT VPS). Ordem: `sync → blog → seinfeld --generate → seinfeld --dispatch → newsletter → linkedin → instagram`. Carrossel/reels NÃO entram no pipeline VPS — vão pelos workers no **Coolify VPS Master** (Railway DESLIGADO). Ver [ADR-0004](docs/adr/0004-carrossel-railway-resto-vps.md) e [ADR-0012](docs/adr/0012-workers-railway-para-coolify.md) (migração Railway→Coolify concluída).

**Trigger on-demand** — Geração disparada quando usuário aprova uma ideia. Endpoint `/api/app/trigger-generation` (Vercel) filtra canais: `carrossel`/`reels` → workers (Coolify, via `WORKERS_API_URL`); resto → `VPS:39090/trigger`. Newsletter é **silenciosamente ignorada** no trigger (G002).

**Generation queue** — Tabela `generation_queue` (planejada para refator PDL-171) para coordenar jobs entre workers e VPS. Hoje a coordenação é por mistura de `trigger_server.py` + cron + status em `published_posts`.

**Sync** — Step que carrega o estado do tenant e do CRM Cadencia antes de gerar. Sempre roda primeiro.

**Dispatch (Seinfeld)** — Envio real do email Seinfeld via Resend. Acontece no cron diário e retoma o item vencido mais antigo sem duplicar por contato/post.

## Growth (VPS)

**Growth pipeline** — Mesmo que pipeline interno acima. Rodado por `/cadencia/crons/growth_pipeline.py`.

**Seinfeld email** — Email diário no estilo "Jerry Seinfeld" (storytelling curto, sem CTA agressivo). Gerado a partir de `published_posts` que ainda não foram usados como Seinfeld (`seinfeld_sent=false AND seinfeld_scheduled_at IS NULL`).

**Newsletter** — Compilação semanal de artigos da semana. Dispara sexta 15h BRT. Não disponível no trigger on-demand.

**Scoring** — Lead scoring por eventos Resend/Svix na porta `8767`. Soma pontos em `contacts.score`, atualiza temperatura, atribui por `post_id` e aplica supressão em bounce/complaint. Score bands: Frio (<30), Aquecendo (≥30), Quente (≥60), Hot (≥80).

**Mission Control** — Dashboard HTML em VPS:8768 (`/cadencia/mission_control.py`) para Felipe ver estado dos tenants em tempo real.

## Workers (Coolify — VPS Master)

**Orchestrator** — Worker principal `pipeline-orchestrator` (7 steps) que coordena geração de carrossel/reels (workers no **Coolify VPS Master**; Railway DESLIGADO, ver [ADR-0012](docs/adr/0012-workers-railway-para-coolify.md)). Diferente do `growth_pipeline.py` (que roda VPS e cobre blog/seinfeld/linkedin/instagram).

**Theme engine** — Worker que escolhe tema visual para um post baseado no dossier + editorial + sub-preset.

**Chat agent** — Worker do "Tenho uma ideia" — conversa com usuário, captura ideia, devolve para `content_ideas`. Ver [ADR-0002](docs/adr/0002-chat-agent-design.md).

**RAG memory** — Memória de contexto do agente: histórico de posts do tenant, conversas chat, dossier. Usado para evitar repetição e manter coerência.

## Billing / Créditos (PDL-505, 11/06/2026 — sem planos)

> Cadência **não tem planos/assinatura** desde PDL-505. Termos `trial`/`essencial`/`starter`/`growth`/`growth_pro` são **legado** — não usar em código/copy novo. Fonte única do modelo: `times/produto/cadencia/MODELO-CREDITOS.md` (pd-framework).

**Carteira de créditos** — Tabela `tenant_plans` (nome legado) é a carteira de créditos do tenant, não um "plano". `plan_name` deve ser `creditos`. Tenant pode ter múltiplas linhas ativas (créditos somam). Todos os canais (blog/newsletter/Instagram/LinkedIn/etc) ficam liberados pra qualquer tenant — não há gating por tier.

**Crédito** — Unidade de geração. Cada post gerado consome créditos do tenant. Tenant com 0 créditos é skipado pelo pipeline (exceto sync + newsletter). Compra self-service: pacotes one-time (+10 R$49,90 · +30 R$129,90 · +60 R$219,90). Cliente gerido (white-glove): créditos injetados manualmente conforme venda comercial.

**Stripe** — Gateway de pagamento. Substituiu Asaas em 11/05/2026. Ver [ADR-0001](docs/adr/0001-stripe-em-vez-de-asaas.md).

## Tracking / Analytics

**CAPI** — Conversions API do Meta. Endpoint `/api/capi/*` envia eventos server-side para Meta Pixel (deduplicação client+server).

**Stevo** — Bot WhatsApp do Felipe (não brancado). Usado para notificações internas (deploy, incidentes, status semanal). Endpoint `/api/stevo/*`.

## Ambiguidades flagadas ⚠️

- ⚠️ **"Pipeline"** pode significar (a) pipeline interno de geração, (b) funil comercial do CRM. Sempre desambiguar pelo contexto.
- ⚠️ **"Token"** sem qualificador é ambíguo. Sempre dizer: `supabase_service_role`, `stripe_secret`, `resend_api_key` ou a credencial específica do canal.
- ⚠️ **"Worker"** pode ser (a) worker Coolify VPS Master (`cadencia-workers/`; Railway DESLIGADO), (b) script Python rodando na VPS growth (`/cadencia/`). VPS scripts são chamados de **growth scripts** quando o contexto exige desambiguação.
- ⚠️ **"Generation"** sem canal é ambíguo. Sempre dizer: geração de carrossel, blog, seinfeld, linkedin, instagram, reels, newsletter.

## Relacionamentos

```
Tenant ── tem ──► Tenant config ── configura ──► Canais e email
   │
   ├── tem ──► CRM Cadencia ──► contatos / empresas / oportunidades / cadências
   ├── tem ──► Dossier
   ├── tem ──► 3 Editoriais ──┐
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
