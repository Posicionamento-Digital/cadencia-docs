---
date: 2026-05-25
tags: [documentacao, cadencia, foundation, framework]
moc: "[[Cadencia-Framework/Docs/README]]"
projeto: Cadência
type: source
entities: ["[[Cadencia]]", "[[marketing]]"]
---
> 📍 Origem: `times/produto/cadencia/foundation/tech-principles.md` no `pd-framework`. Última sync: 2026-05-25.

# Tech Principles — Cadência

> 8 princípios técnicos não-negociáveis. Trocar qualquer um exige **ADR formal** + decisão Felipe + entrada em `../memory/decisions.md`.
>
> Extraídos de: `SOUL.md` § Princípios técnicos + `CLAUDE.md` repo cadencia-app + decisões históricas.

---

## 1. Multi-tenant nativo desde V1

**Princípio:** RLS Supabase em todas as tabelas que armazenam dados de tenant. Sem exceção. Não existe "modo single-tenant" no produto.

**Por quê:** Cadência nasceu multi-tenant. Migração para multi-tenant em produto single-tenant é custo proibitivo. Construir multi-tenant first elimina classe inteira de bugs e vazamentos.

**Como aplicar:**
- Toda nova tabela = RLS + policy de isolation por `tenant_id`
- Toda query do cliente final = via JWT com `tenant_id` claim
- Service role só em scripts admin/cron, nunca path do usuário
- Storage paths sempre prefixados com `<tenant_id>/`

**Detalhes:** `multi-tenant-strategy.md`.

---

## 2. Supabase é source of truth

**Princípio:** PostgreSQL Supabase é fonte única de verdade. DB + Storage + Auth. Não duplicar estado em Redis, cache externo, ou outro DB.

**Por quê:** Multi-store gera sincronização eventual e bugs de consistência. PostgreSQL aguenta o volume Cadência. RLS resolve isolation. Storage Supabase é integrado.

**Como aplicar:**
- Sem Redis cache de leitura no path principal (usar Postgres + PostgREST)
- Sem DB secundário (MongoDB, Firestore, etc)
- Storage = Supabase Storage (não S3 separado)
- Auth = Supabase Auth (não Auth0/Cognito)

**Exceções permitidas:**
- Sentry (errors externos)
- Mixpanel/PostHog/GA4 (analytics — duplicação esperada)
- Stripe (transações com source of truth próprio)
- GHL (CRM brancado é externo por design)

---

## 3. Frontend Vercel `main`, Workers Railway `master` (migrando Coolify)

**Princípio:** dois pipelines de deploy, sincronizados por `git push origin main:master`.

**Por quê:** Frontend e workers têm ritmos de release diferentes. Frontend pode deployar 10x/dia, workers idealmente menos. Separação evita downtime de UI quando worker quebra.

**Como aplicar:**
- Push em `main` → Vercel deploy frontend automático
- Push em `master` (espelhamento de `main`) → Railway deploy workers
- Comando padrão pós-push: `git push origin main:master`
- Pós-push: validar `vercel ls | head -3` Ready e `railway logs` sem erro

**Migração ativa:** Railway → Coolify VPS Master (PDL-18 a 23 cadeia). Após migração, `master` push vai para Coolify.

---

## 4. GHL como CRM/email/WhatsApp/Social Planner brancado

**Princípio:** não construir CRM próprio. GHL é motor invisível embutido.

**Por quê:** GHL cobre CRM + email + WhatsApp + Social Planner + workflows num produto maduro. Construir do zero gastaria ano-equipe sem entregar mais valor. GHL plano agência permite N subcontas (~$97/mês incluso).

**Como aplicar:**
- CRM → GHL subconta por tenant
- Email transacional + marketing → GHL Workflows
- WhatsApp broadcast/atendimento → GHL
- Social Planner (Instagram pub) → GHL
- Tenant nunca sabe que existe GHL — UI Cadência abstrai 100%

**Anti-padrões:**
- ❌ Expor "GoHighLevel" na UI
- ❌ Tentar substituir GHL por código próprio sem ADR
- ❌ Sincronizar dados redundantemente entre Cadência e GHL — usar GHL como cache do que faz sentido

---

## 5. Renderer Playwright HTML→PNG

**Princípio:** carrosséis e covers são HTML renderizado para PNG via Playwright. 1080×1440. 7 famílias template. 11 presets visuais. 29 modelos YAML.

**Por quê:** HTML/CSS dá flexibilidade visual incomparável. Playwright headless garante consistência cross-browser. PNG é universal pra Instagram/LinkedIn/blog. SVG/Canvas/lib JS = limitação de tipografia e composição.

**Como aplicar:**
- Templates novos = HTML + CSS + variáveis injetáveis
- Cover Identity Lock = HTML + foto Gemini-generated + composição
- Tests visuais: `tests/visual/test_slide_contrast.py` (40/40 PASS antes de push)
- Output → Supabase Storage

**Não substituir** por:
- ❌ Canvas API JavaScript
- ❌ Libs tipo Sharp/Jimp pra composição
- ❌ Templates Figma exportados
- ❌ SVG renderizado pelo browser

---

## 6. LLM stack fixa (trocar exige ADR)

**Princípio:** OpenAI (texto via OpenRouter), Gemini 2.5 Flash (capas + Identity Lock), Apify (análise IG), Pexels (fallback stock). Trocar qualquer um = ADR formal.

**Por quê:** trocar LLM sem critério gera regressões caras (prompt engineering, validação de output, refatoração agents). Cada provider tem trade-off claro. OpenAI/OpenRouter já tem prompts otimizados; Gemini Identity Lock é único; Apify scrape IG estável; Pexels free tier suficiente.

**Como aplicar:**
- Mudança de modelo (gpt-5 → gpt-6) sem ADR — OK se mesmo provider
- Mudança de provider (OpenAI → Anthropic) — exige ADR
- Provider novo (ex: Vertex AI) — exige ADR + benchmark documentado

**PR ativo:** #2 — OpenRouter via `OPENAI_BASE_URL/OPENAI_MODEL` (ainda no domínio OpenAI compat, sem ADR).

---

## 7. Pipeline 7-step orchestrator é contrato

**Princípio:** Research → Model Selector → Headline → Carousel → Caption → Cover → Renderer é a **espinha dorsal**. Features novas se encaixam como steps adicionais — não substituem.

**Por quê:** orchestrator é estável, testado, validado em produção. Substituir = retrabalho monumental + risco de regressão. Adicionar step novo = baixo custo + composição limpa.

**Como aplicar:**
- Feature nova de geração = step novo (ex: video transcript step) ou pré/pós-processing
- Mudança no fluxo (ordem dos 7 steps) = ADR formal
- Steps podem ser opt-in por plano (Growth Pro tem step Remotion)

**Anti-padrões:**
- ❌ Pipeline paralelo separado (mantém o orchestrator único)
- ❌ Bypass do Model Selector (sempre passa pelos 12 flags)
- ❌ Renderer custom por feature (sempre Playwright HTML→PNG)

---

## 8. Validar antes de declarar pronto

**Princípio:** compilou ≠ testou. Build ≠ validação. Lint ≠ QA.

**Por quê:** histórico documentado de incidents (Vercel 6+7 deploys falhando silenciosos, P0 NameError, 38 bugs renderer, textos invisíveis recorrentes). Compilar é mínimo necessário — não suficiente.

**Como aplicar (checklist obrigatório):**

```
[ ] npm run build → ZERO erros (não-Sentry)
[ ] Se mexeu no renderer: python tests/visual/test_slide_contrast.py → 40/40 PASS
[ ] Rendi 1 post real local via Playwright OU declarei explicitamente que NÃO testei
[ ] Se NÃO consegui testar: avisei Felipe ANTES de pushar
```

**Pós-push:**
```
[ ] vercel ls | head -3 → Ready (não Error)
[ ] Se backend Python: git push origin main:master + railway logs
```

**Pós-deploy VPS (qualquer projeto):**
```
[ ] python3 -c 'compile(open("ARQUIVO").read(), "test", "exec")'
[ ] Dry-run com dados reais: importar funções, chamar queries, verificar output
[ ] Se cron: crontab -l confere o schedule
[ ] Se NÃO consegui dry-run: avisar Felipe
```

**Honestidade obrigatória:** se não testou, dizer "compilou mas NÃO testei". Sem desculpa. Skill `/validar-deploy-vps` automatiza checklist.

---

## Princípios meta (sobre os princípios)

### Como atualizar

1. Decisão Felipe explícita
2. ADR formal em `cadencia-app/docs/adr/NNNN-<descricao>.md`
3. Entrada em `../memory/decisions.md`
4. Atualização deste doc + git commit referenciando ADR

### Quando NÃO seguir

Princípio só é violável com:
- ADR documentando trade-off
- Aprovação Felipe explícita
- Plano de retorno ao princípio (se for exceção temporária)

Senão, princípio vence — sempre.

---

## Refs

- `../SOUL.md` § Princípios técnicos
- `multi-tenant-strategy.md` (princípio 1)
- `tech-architecture.md` (princípios 2, 3, 5, 6, 7)
- `cadencia-app/CLAUDE.md` (princípio 8 — checklist completo)
- `cadencia-app/docs/adr/0001-stripe-em-vez-de-asaas.md`
- `cadencia-app/docs/incidentes/` (histórico que origina princípio 8)
