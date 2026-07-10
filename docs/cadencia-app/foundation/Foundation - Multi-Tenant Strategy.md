---
date: 2026-05-25
tags: [documentacao, cadencia, foundation, framework]
moc: "[[Cadencia-Framework/Docs/README]]"
projeto: Cadência
type: source
entities: ["[[Cadencia]]", "[[Karina Vieira]]", "[[marketing]]"]
---
> 📍 Origem: `times/produto/cadencia/foundation/multi-tenant-strategy.md` no `pd-framework`. Última sync: 2026-05-25.

# Multi-Tenant Strategy — Cadência

> Estratégia de isolation de dados, identidade e operação por tenant. Princípio absoluto: **multi-tenant nativo desde V1**. Não há "modo single-tenant" — todo tenant é isolado por design.

---

## Princípio

**Cada tenant é uma marca independente** com:
- Dados isolados (RLS Supabase + storage segregado)
- CRM próprio (subconta GHL brancada)
- Blog próprio (instância Vercel do template)
- Identidade visual própria (VI gerado por tenant)
- Dossiê de marca próprio (Big5 + DPR + Kane + Archetypes)
- Domínio próprio (add-on) ou subdomínio default

**Cadência opera N tenants simultaneamente sem vazamento entre eles.**

---

## Camadas de isolation

### 1. Banco de dados — Supabase RLS

**Toda tabela que armazena dado de tenant tem RLS habilitado.** Sem exceção.

Pattern típico:
```sql
CREATE POLICY "tenant_isolation" ON public.<tabela>
  USING (tenant_id = auth.jwt() ->> 'tenant_id');
```

**Otimização aplicada (PDL-163):** subselect `auth.jwt()` + index em `super_admin` evita re-execução por linha.

**Auditoria pendente (PDL-172):** schema drift entre `pg_dump` e migrations versionadas.

**Anti-padrão:**
- ❌ Nunca query com `service_role` no path do usuário final (bypassa RLS — só para admin/cron)
- ❌ Nunca filtro apenas no app — RLS é defesa em profundidade
- ❌ Nunca tenant_id implícito — sempre explícito na policy

### 2. Storage — Supabase Storage

- **Bucket `tenant-photos`** privado — fotos de referência (cover Identity Lock)
- **Bucket de slides** público mas com URL signed
- Path por tenant: `<tenant_id>/<asset_type>/<file>`
- Cleanup: cron retention (PDL-23 — a codar)
- Política retenção: PDL-22 (aguardando Felipe definir)

### 3. Auth — Supabase Auth

- Magic link + senha
- JWT com claim `tenant_id` populado no login
- Multi-conta agência (PDL-100 — Todo): um login → N tenants (futuro)
- Onboarding personalizado por Felipe pra clientes de agência (PDL-101 — Done)

### 4. CRM — GHL subconta brancada

- **Cada tenant tem subconta GHL própria** (criada no onboarding)
- Felipe/equipe não acessam diretamente a subconta — automação via API
- Email, WhatsApp, Social Planner isolados por subconta
- **Bug ativo PDL-202** (P1): subconta GHL não criada no onboarding tenant
- **Pendência PDL-25:** migração OAuth nova agência GHL

### 5. Blog — Vercel template multi-tenant

- Repo `cadencia-blog-template` é o template fonte
- Cada tenant: deploy automático no Vercel quando post aprovado
- Subdomínio `<slug-tenant>.cadencia-blog.app` ou domínio próprio (add-on)
- Conteúdo gerado pelo orchestrator → publicado via webhook → Vercel rebuild

### 6. Identidade visual (VI) por tenant

- `visual_identity.py` (workers) gera paleta + tipografia + regras a partir de:
  - Logo do tenant (upload onboarding)
  - Profiling Big5 + Archetypes
  - Editorias selecionadas (3 categorias post)
- Output: presets visuais armazenados em Supabase + aplicados em todos os assets gerados
- 11 presets visuais base + 29 modelos YAML + 7 famílias HTML

### 7. Identity Lock — Cover por tenant

- `cover_generation.py` (workers) usa **Gemini 2.5 Flash**
- Tenant upload 3+ fotos referência (frente + 3/4) → bucket `tenant-photos`
- Identity Lock + Camera Specs → 5/5 imagens consistentes com rosto do dono
- Alternativa por editoria:
  - `cover_style: "person"` → rosto (autoridade)
  - `cover_style: "thematic"` → sem rosto (impacto)

---

## Onboarding multi-tenant (3 caminhos)

### A) Onboarding default (Tour RPG 12 steps)

- Tenant self-service via `(onboarding)/` no frontend
- Magic link → preenchimento guiado → provisioning automático (subconta GHL + blog Vercel + identity visual + dossier)
- Usado por: clientes que entram via marketing direto

### B) White-glove agência (skill `/criar-tenant-agencia`)

- Felipe preenche TUDO manualmente via skill global
- Cobre: identidade, profiling Big5/DPR, visual 15 presets, fotos, logo, editorias, restrições, história
- Cria conta sem email confirmação, popula todas tabelas, chama workers pra dossier/VI/editorias
- Gera Soul.md por tenant
- Pode enviar credenciais via WhatsApp Stevo
- Usado por: agências (Karina, etc) trazendo clientes finais

### C) Briefing prévio via Tally (skill `/tally-form-cadencia`)

- 24 perguntas cobrindo identidade visual, perfil marca, público-alvo, rosto, prioridade conteúdo
- Útil pra clientes de agências antes da reunião de briefing
- Output alimenta o caminho A ou B

---

## Soul.md por tenant (PDL-93 Done, PDL-117/118 pendentes)

**Cada tenant tem seu próprio Soul.md** — distinto do SOUL.md do produto Cadência. Funciona como:
- Missão do negócio do tenant
- Voz/tom do tenant (não da Cadência)
- Valores e princípios do tenant
- Input pro chat "Tenho uma Ideia" (PDL-92 Done)
- Storage: `tenant_config.soul_md` no Supabase

**Pendências:**
- PDL-117: Soul.md para tenant `felipeluissalgueiro` (teste chat)
- PDL-118: Soul.md para tenants da Karina Vieira (antes briefing 19/05)
- PDL-119: Automatizar geração no onboarding (futuro — Done)

---

## Modelo de cobrança multi-tenant

- **Cliente direto:** Stripe por tenant (cada um paga seu plano)
- **Agência white-glove:** agência paga; tenants são "filhos" da agência
- Stripe webhooks → atualiza `tenant_config.plan` + créditos
- Trial: 3 posts grátis sem cartão (qualquer tenant novo)

---

## Cross-tenant features (poucas, controladas)

- **Lara (GCI-GO)** — agente atendimento IA é template reaproveitado, mas cada implantação é um component separado (vive em `times/produto/gci-go/`)
- **Cadência outbound 30d** (PDL-27) — scripts Supabase reaproveitáveis, mas cadência por tenant
- **Templates YAML/HTML** — compartilhados (29 modelos, 7 famílias) mas aplicados com VI do tenant
- **Prompts LLM** — compartilhados, mas contexto injetado é do tenant

---

## Performance e custo (otimizações aplicadas)

**Realizadas (Bugs project):**
- PDL-160 Done — drop publication `supabase_realtime` (pipeline_status)
- PDL-161 Done — polling on-demand em vez de Realtime
- PDL-163 Done — RLS subselect + index super_admin
- PDL-164 Done — investigação schema reloads PostgREST
- PDL-165 Done — drop indexes não usados
- PDL-166 Done — ajuste `idle_in_transaction_session_timeout`
- PDL-162 In Progress — validar economia CPU pós-deploy

**Custos operacionais (Visão Produto):**
- ~$10-25/tenant/mês infra (GHL incluído ~$97 plano agência, OpenAI $5-15, Gemini $2-5, Supabase $0-5, Vercel free)
- Custo por carrossel: $0.15-$0.25

---

## Anti-padrões — NÃO FAZER

1. **Tabela sem RLS** — bypassa isolation, vaza dados
2. **Service role no client-side** — bypassa RLS, qualquer usuário lê tudo
3. **Tenant_id implícito** — assumir contexto sem checar JWT
4. **Single-tenant feature flag** — não existe modo single, tudo é multi
5. **Hardcoded tenant** em código — sempre via JWT/session
6. **Cross-tenant query** sem `super_admin` claim — vaza dados entre tenants
7. **Storage path sem `tenant_id`** — assets podem ser acessados por outro tenant

---

## Refs

- `../SOUL.md` § Princípios técnicos (multi-tenant nativo)
- `tech-architecture.md` § Banco de dados — Supabase
- `tech-principles.md` § Multi-tenant first
- `docs/features/criar-tenant-agencia/` no repo `cadencia-app`
- Skills: `/criar-tenant-agencia` (global), `/tally-form-cadencia` (global), `/gerenciar-plano` (local)
- Incidents: 2026-05-19 (migration RLS rejeitada referência tabela inexistente `tenant_users`)
