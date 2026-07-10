---
type: source
source_kind: incidente
date: 2026-06-02
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-06-02_cadencia-aprovou-e-nao-gerou-4-causas-raiz-convergentes

# 2026-06-02 — Cadência: "aprovou ideia e não gerou" — 4 causas raiz independentes convergindo no mesmo sintoma

**Projeto:** Cadência (full stack: cadencia-app + cadencia-growth + Supabase + Vercel + GHL)
**Severidade:** Alta
**Tags:** `#backend` `#frontend` `#api` `#ghl` `#supabase` `#vercel` `#schema-drift` `#silenciosa` `#regressao` `#modelo-negocio` `#falha-detectada`

---

## Resumo executivo

Felipe relatou: "dezenas de vezes corrigi a mesma coisa de emails que não são gerados, linkedin e blog que também não são gerados". A investigação cross-temporal cross-canal expôs que **4 bugs raiz independentes convergem no mesmo sintoma percebido** ("aprovou ideia, esperou, nada apareceu"). Cada fix anterior tratava 1 dos 4, então o sintoma sempre voltava por outro caminho.

Achados da sessão: 22 tenants ativos, **só 7 publicaram nos últimos 30 dias**; 6 contas pagantes com plano ativo e **zero posts em 30d**; e quem publicava, frequentemente só blog (sem linkedin/seinfeld/instagram).

## As 4 causas raiz

### Causa 1 — `VPS_TRIGGER_URL` no Vercel com `\n` literal no final

`env pull` revelou: `len=25 last3=[48, 92, 110]` — ASCII para `0`, `\`, `n`. O valor tinha **dois caracteres literais `\` + `n`** no final, fruto de um `echo "..." | vercel env add` antigo. Resultado: `http://72.60.4.71:39090\n/trigger` é URL inválida; `fetch()` falhava em todas as aprovações depois de algum momento entre maio e junho. O `trigger-generation/route.ts` retornava 200 ao frontend (porque a chamada era fire-and-forget) e o cron de 14h era a única fonte de geração — quem aprovasse depois esperava 24h.

**Fix:** `vercel env rm VPS_TRIGGER_URL production --yes && printf 'http://72.60.4.71:39090' | vercel env add VPS_TRIGGER_URL production`. Verificado por `env pull` novo: `len=23` (sem o `\n`).

**Eco do README:** o arquivo `src/app/api/app/trigger-generation/README.md` documenta exatamente o mesmo bug, mas para o SECRET. O URL foi setado depois e caiu no mesmo padrão.

### Causa 2 — Coluna `channels` (plural) não existia na tabela `generation_queue`

Schema real (via Management API): `channel text DEFAULT 'blog'` (singular). Migration original `20260425000000_generation_queue.sql` criou só essa coluna. Mas o frontend (`POST /api/app/generation-queue/route.ts` linha 47) sempre fez:

```ts
.insert({ tenant_id, content_idea_id, channels, priority: 1, status: "pending" })
```

Supabase silenciosamente descartava a coluna inexistente, o INSERT subia com `channel='blog'` por default. Toda informação multi-canal era perdida. PDL-171 estava aberto descrevendo o sintoma mas nunca foi corrigido.

**Fix:**
```sql
ALTER TABLE generation_queue ADD COLUMN IF NOT EXISTS channels text[] NOT NULL DEFAULT '{}';
UPDATE generation_queue SET channels = ARRAY[channel] WHERE channels = '{}' AND channel IS NOT NULL;
NOTIFY pgrst, 'reload schema';
```

269 rows backfillados. Migration commitada em `supabase/migrations/20260602230000_generation_queue_channels_array.sql` (PR cadencia-app#7).

### Causa 3 — `GHL_COMPANY_ID` errado no `/cadencia/.env`

`provision_tenant.py:create_ghl_location()` monta `body = {'name', 'email', 'companyId': os.environ.get('GHL_COMPANY_ID', '')}`. O valor em `.env` era `yXnyB5pagLHLdjEvGpYe` — empresa diferente da que o `GHL_AGENCY_TOKEN` (`pit-02f184...`) tem permissão. GHL respondia 403 "Forbidden resource". Provisioning ficava em `partial` para sempre.

Confirmação: rodei `curl POST /locations/` com mesmo token + `companyId=rIrmvD1WcDqVNAyDRnf8` (extraído de location existente) → 201 Created. Com `companyId=yXnyB5...` → 403.

**Fix:** `sudo sed -i 's|^GHL_COMPANY_ID=.*|GHL_COMPANY_ID=rIrmvD1WcDqVNAyDRnf8|' /cadencia/.env`. Backup salvo em `/cadencia/.env.bak-pdl364-20260602-2340`.

Reprovisioning manual passou em 4 tenants: Lab. Crescimento (Alexandre Manhães), Diego do Bitcoin, Jhonatan, Petrafix Engenharia, Alejandro Pano. Todos `provisioning_status=ready` com `location_id` real.

### Causa 4 — Modelo de cobrança migrou pra crédito-only, mas código ainda tem lógica de plano/tier

Felipe explicou na sessão: Cadência é vendida por **créditos**; "planos" (trial/essencial/starter/growth) são apenas convenções comerciais (lotes com desconto). Todo cliente deve ter todos os canais habilitados. Pago = créditos > 0.

Mas o `growth_pipeline.py` mantinha:
- `if plan_name in ('trial', 'essencial', 'starter'): steps_to_run = [s for s in steps_to_run if s != 'seinfeld']` — pulava email
- `weekday not in (0, 3)` → pulava blog/linkedin/instagram em terça/quarta/sexta/fim de semana

E o `provision-tenant/route.ts` só criava `tenant_config` se houvesse `attribution`. Resultado: 20/22 tenants em prod com `growth_channels=NULL`, pipeline filtrava silenciosamente.

**Fix:**
- Remoção do bloco `if plan_name in ('trial', 'essencial', 'starter')` em `growth_pipeline.py` (deploy direto na VPS Master, backup `bak-creditos-2015`).
- Backfill: `UPDATE tenant_config SET config = jsonb_set(config, '{growth_channels}', '["blog","seinfeld","linkedin","instagram"]')` aplicado em 20 tenants.
- PR cadencia-app#7: `provision-tenant/route.ts` agora cria `tenant_config` sempre com `growth_channels` default + attribution se houver.
- PR cadencia-app#7: `trigger-generation/route.ts` retorna 400 estruturado (`TENANT_NOT_CONFIGURED` / `GHL_NOT_READY`) em vez de fail silencioso; `ideas/page.tsx` mostra a mensagem.

## Por que isso convive há tanto tempo sem ser descoberto

Cada bug por si só é parcialmente compensado pelos outros:
- Cliente aprova → Causa 1 mata a chamada imediata, mas o cron de 14h vai eventualmente rodar
- Cron de 14h corre e pega a queue → Causa 2 perde a info multi-canal, mas `blog_generate.py` lê "qualquer pending sem filtro" e gera blog mesmo assim
- Cliente entusiasmado vê o blog publicado → assume que está funcionando
- Mas linkedin/instagram/seinfeld dependem de `published_posts` + `location_id` GHL → Causa 3 + Causa 4 matam silenciosamente
- Cliente nota "blog vem, redes não" → reclama → fix pontual em algum canal → volta sintoma por outro canal
- Felipe corrige "dezenas de vezes a mesma coisa" — sempre era OUTRA das 4 causas

## Sinal-chave que destravou o diagnóstico

Quando Felipe disse "hoje um user novo aprovou e não gerou, e eu mesmo uso diariamente", a hipótese inicial ("cliente abandona") caiu. Investigação concreta de **DOIS casos específicos** (Alejandro Pano que aprovou hoje 14:58, Lab. Crescimento que provisionou hoje 13:55) expôs assinaturas diferentes que apontaram pra causas distintas:

- Alejandro: `growth_channels=NULL` + `ghl.location_id=None` + cron já tinha passado → causas 1+3+4
- Lab. Crescimento: 16 ideias `pending` `updated_at == created_at` (nunca tocadas) + `provisioning_status=partial` GHL 403 → causa 3 isolada, mais Felipe ainda não tinha entrado no app

## Prevenção

1. **Schema drift entre frontend e banco:** o INSERT do `generation-queue/route.ts` deveria ter falhado quando incluísse `channels`. Supabase aceitar e descartar é faca de dois gumes — pra dev rápido ajuda, em prod silencia bugs. Considerar gerar TypeScript types do schema (`supabase gen types`) e usar tipagem estrita nos inserts.

2. **Newline em valores de env:** rodar `node -e "console.log(JSON.stringify(process.env.X))"` ou similar como smoke test pós-deploy. Documentar `printf` (não `echo`) já está no README pro SECRET — adicionar também para URLs.

3. **Modelo de negócio em código:** quando o produto muda (plano → crédito), grep `plan_tier|plan_name|trial|essencial|starter` em todo o repo antes de assumir migração completa. Lógicas de filtro escondem em geradores secundários.

4. **Provisioning como gate, não só log:** o frontend hoje deixa o usuário aprovar ideia mesmo com `provisioning_status=partial`. Fix do PR#7 transforma isso em erro estruturado, mas a defesa ideal é a UI mostrar "Setup pendente" antes de habilitar o swipe de aprovar.

5. **Métricas de "tenant ativo sem entregar":** hoje não há dashboard que mostre "X dias sem post publicado por tenant pagante". Sintoma só aparecia quando o cliente reclamava. Próximo: cron diário que alerta CS via WhatsApp se algum tenant com `tenant_plans.status=active credits>0` tem `MAX(published_at) < hoje - 3d`.

## Pendências (não resolvidas neste incidente)

- **Vercel "10 projects per Git Repo"**: Alejandro caiu nesse erro uma vez no provisioning; ao reprovisionar, "Blog already provisioned — skip". Continuará bloqueando provisioning de novos tenants quando o repo `cadencia-blog-template` chegar no limite. Soluções: template por shard de N tenants, projetos sem Git deploy, ou plano Vercel maior.
- **OAuth GHL nunca rola**: script sempre cai em "Using static GHL_AGENCY_TOKEN (fallback)". Não impede operação após Causa 3 corrigida, mas é dívida — token estático não renova.
- **Bug B "double gate"**: hoje o `generation-queue/route.ts` insere row pending mas não dispara trigger; o `ideas/page.tsx` chama `trigger-generation` separado. Se algum dos dois falhar isoladamente, o outro não cobre. Considerar centralizar a chamada do trigger dentro de `generation-queue/route.ts`.

## Recuperação operacional executada

- Re-dispatched email do dia 02/06 para tenant Felipe em background (`nohup seinfeld_generate.py 6bb2c1ba --dispatch`) — perdido por timeout do cron 14h.
- Reprovisionados 5 tenants com `provisioning_status=partial` → todos `ready`.
- Backfill 20/22 `tenant_config.growth_channels` → 22/22 com 4 canais.
- 269/269 rows `generation_queue.channels` populadas via `ARRAY[channel]`.

## Cross-link

- Incidente complementar (mesma sessão): [2026-06-02 dual-write log false cron sombra timeout dispatch](2026-06-02_cadencia-dual-write-log-falso-cron-sombra-timeout-dispatch.md) — bugs cosméticos + timeout que confundiram diagnóstico inicial.
- PR aberto: `felipeluissalgueiro/cadencia-app#7` — provisioning default + validação pre-conditions + migration channels[].
