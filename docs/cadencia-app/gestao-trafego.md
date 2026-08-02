# Gestão de Tráfego (Meta Ads) — feature por tenant

> DEV-1474 · em produção desde 2026-08-02 (commit merge `228053b`).
> Repositórios: `cadencia-app` (front + API routes) · Meta Graph API v21.

## O que é

Aba dentro do app (`/app/growth/trafego`) que lê campanhas Meta Ads do tenant, exibe insights de 7 dias com árvore de decisão (Pedro) e permite ações reais na conta (pausar, escalar, ampliar segmentação, criar campanha em rascunho). Feature isolada por tenant via feature flag — quem não tem a flag ligada não vê o menu, a página responde 404 e as APIs respondem 403.

## Pra que serve

Consolida a operação de tráfego pago de cada cliente dentro do próprio Cadencia, sem depender do Meta Ads Manager pra tarefas recorrentes: decidir o que pausar, o que escalar, o que ajustar de segmentação. Pedro (persona de tráfego, ver `times/marketing/comunicacao/trafego/`) faz o diagnóstico e propõe a ação; o cliente aprova; a mudança vai direto pra Meta Graph API.

## Como funciona

**Gate em 3 camadas (defesa em profundidade):**

1. `Sidebar` esconde o item de menu se `flag_trafego_enabled` estiver off no tenant
2. `/app/growth/trafego/page.tsx` responde 404 se off
3. Cada rota em `/api/app/trafego/*` valida `isTrafegoEnabled(admin, role)` e responde 403 se off

Super_admin sempre vê (pra suporte), independente da flag.

**Config Meta por tenant:** tabela `tenant_trafego_meta` guarda `ad_account_id` (obrigatório) + `page_id` (opcional, necessária pra adset de LEADS) + `access_token` (opcional, override do default). O token default vem da env server-side `META_SYSTEM_USER_TOKEN` (system user "Claude Code", app `846142204524437`, never-expire) que enxerga todas as contas atribuídas via BM partner flow.

**Fluxo de leitura (`GET /api/app/trafego/insights`):**

1. Middleware autentica user (`getUser`)
2. `resolveTenant()` retorna tenant efetivo (respeita cookie de impersonation pra super_admin)
3. `isTrafegoEnabled()` valida flag
4. `getTrafegoMetaConfig()` lê `tenant_trafego_meta` do tenant
5. `fetchAccountName()` + `fetchCampaignSnapshots()` chamam Meta Graph em paralelo
6. `decide()` aplica a árvore da decisão em cada snapshot (motor.ts)
7. Response: `{ items, accountName, collectedAt }` — UI ordena por `STATUS_ORDER` e renderiza tabela

**Fluxo de escrita (`POST /api/app/trafego/apply`):** três ações — `pausar`, `reativar`, `escalar` (dailyBudgetBRL). Cada uma faz um único PATCH na Graph API na entidade correta (campanha ou adset). `POST /api/app/trafego/create-campaign` cria rascunho `PAUSED` (nunca ativa sozinho — Felipe aprova depois no BM).

**Chat do Pedro (`POST /api/app/trafego/chat`):** proxy autenticado pro OpenRouter (modelo `anthropic/claude-sonnet-5`) com system prompt de Pedro focado em tráfego. Env `OPENROUTER_API_KEY` obrigatória.

**Sugestão de campanha (`POST /api/app/trafego/create-proposal`):** dois modos — `briefing` (usuário descreve o que quer) ou `sugerir` (Pedro propõe baseado nas campanhas existentes). Retorna JSON estruturado `{propostas: [...]}` pra UI mostrar antes de criar.

## Componentes internos

| Arquivo | Papel |
|---|---|
| `src/lib/trafego/gate.ts` | `isTrafegoEnabled(admin, role)` — flag por tenant + super_admin bypass |
| `src/lib/trafego/meta.ts` | Cliente Graph API: `getTrafegoMetaConfig`, `fetchAccountName`, `fetchCampaignSnapshots`, `applyPausar`, `applyEscalar`, `applySegmentacaoAmpliarLocalizacao`, `createCampaignDraft` |
| `src/lib/trafego/motor.ts` | Árvore de decisão pura: recebe `CampaignSnapshot`, devolve `Decision` (status + veredicto + ação sugerida) |
| `src/lib/trafego/fixtures.ts` | 5 campanhas mock (usadas só quando `TRAFEGO_DEMO_FIXTURES=1` — hoje desligado em prod e preview) |
| `src/app/api/app/trafego/insights/route.ts` | GET — lê campanhas + aplica motor |
| `src/app/api/app/trafego/apply/route.ts` | POST — executa ação real na Meta |
| `src/app/api/app/trafego/create-campaign/route.ts` | POST — cria rascunho PAUSED |
| `src/app/api/app/trafego/create-proposal/route.ts` | POST — LLM propõe estrutura de campanha |
| `src/app/api/app/trafego/chat/route.ts` | POST — chat livre com Pedro dentro de uma campanha |
| `src/app/(app)/app/growth/trafego/page.tsx` | Server component com gate de 404 |
| `src/app/(app)/app/growth/trafego/TrafegoView.tsx` | Client component: tabela, filtros, drawer de detalhe, chat |
| `src/app/(app)/app/growth/trafego/CreateCampaignDrawer.tsx` | UI de criação (proposta + confirmação) |
| `src/app/(app)/app/admin/flags/page.tsx` | Toggle da flag por tenant (seletor + switches, mecanismo DEV-829) |
| `supabase/migrations/20260801220000_tenant_trafego_meta_dev1474.sql` | Cria tabela + RLS deny-all + trigger updated_at |

## Envs necessárias

| Env | Escopo | Origem |
|---|---|---|
| `META_SYSTEM_USER_TOKEN` | production + preview | System user Meta "Claude Code". 1P `Credenciais de API - Meta API token` (Posicionamento Digital) — item precisa update manual (SA sem write no vault) |
| `OPENROUTER_API_KEY` | production + preview | 1P `OpenRouter - API - Cadencia app` (Providers IA) |

**Legado removido em 01/08:** `META_DEMO_ACCESS_TOKEN`, `META_DEMO_AD_ACCOUNT_ID`, `TRAFEGO_DEMO_TENANT_ID`, `TRAFEGO_DEMO_FIXTURES` — substituídos por `META_SYSTEM_USER_TOKEN` + `tenant_trafego_meta` + `flag_trafego_enabled`.

## Como habilitar pra um tenant novo

1. Descobrir `ad_account_id` real (formato `act_XXXX`) e opcionalmente `page_id`
2. INSERT em `tenant_trafego_meta`:
   ```sql
   INSERT INTO public.tenant_trafego_meta (tenant_id, ad_account_id, page_id)
   VALUES ('<uuid>', 'act_XXXX', '<page-id ou NULL>');
   ```
3. Ligar flag: `/app/admin/flags` → selecionar tenant → toggle "Gestão de Tráfego" ON. (Ou via SQL: `UPDATE tenant_config SET config = config || '{"flag_trafego_enabled": true}'::jsonb WHERE tenant_id = '<uuid>'`)
4. System user Meta precisa ter a conta atribuída no BM da agência (partner flow) — senão o token não enxerga

## Tenants habilitados em 2026-08-02

| Tenant | Slug | ad_account_id | Page |
|---|---|---|---|
| Felipe/PD | `felipe-salgueiro` (`6bb2c1ba`) | `act_351565742250610` (Felipe Luis Martins) | `1109163152278055` (Cadencia) |
| Iasmin Lopes Pinto | `iasmin-lopes-pinto-5e748c` (`5b777771`) | `act_980990662449502` (CA - Ageu Ribeiro) | (NULL) |

## Quando NÃO usar

- Tenant sem BM configurado ou sem conta atribuída ao system user → deixe a flag off (o gate mostra empty state, mas nada roda)
- Cliente que só quer ver relatórios estáticos — a feature é operacional, escreve real na Meta
- Cadência tem tenants demo/POC → não ligar; a feature acessa a conta real

## 🚫 Don'ts

- **Nunca importar `src/lib/trafego/meta.ts` em client component.** Server-only — se importar, `META_SYSTEM_USER_TOKEN` vaza pro bundle.
- **Nunca commitar valor de `META_SYSTEM_USER_TOKEN` ou `access_token` de tenant no repo.** Sempre via env server ou 1P.
- **Não confiar em `access_token` do tenant sem RLS** — a tabela é deny-all pra `anon`/`authenticated`; só service_role lê. Se algum dia precisar expor, criptografar com pgcrypto antes.
- **Nunca ligar `TRAFEGO_DEMO_FIXTURES=1` em production.** Mock aparece pro cliente como se fosse real.
- **Nunca alterar `PUBLIC_ROUTES` em `src/lib/supabase/proxy.ts` sem cascata `/aprovar-pr` completa.** O gate de auth roda `getClaims()` antes da allowlist; mexer sem testar cookie envenenado dispara o loop do incidente 01/08.

## 🪦 Já tentamos (histórico)

- **Env por tenant (`TRAFEGO_DEMO_TENANT_ID`) — descartado 01/08:** funcionava pra 1 tenant só (Iasmin em preview). Não escala. Substituído por flag em `tenant_config`.
- **Config Meta via envs (`META_DEMO_*`) — descartado 01/08:** exigia redeploy pra cada tenant novo. Substituído por `tenant_trafego_meta` + service_role.
- **Filtro implícito "só ACTIVE || spend > 0" — abandonado 02/08:** rodava dentro do `if (TRAFEGO_DEMO_FIXTURES === "1")`. Removi o filtro junto com a env. Cliente agora vê todas as campanhas (inclusive PAUSED). Se aparecer "dashboard poluído", opção documentada é reintroduzir o filtro com toggle "Mostrar pausadas".
- **Header "Conta: Ageu Ribeiro" hardcoded — corrigido 02/08:** sobra do protótipo Iasmin. Agora vem dinâmico via `fetchAccountName(cfg)` → `/act_X?fields=name`.

## 🔥 Troubleshooting

| Erro | Causa provável | Fix |
|---|---|---|
| `503 NOT_CONFIGURED` no `/insights` | Tenant tem flag on mas sem row em `tenant_trafego_meta` | INSERT config Meta do tenant (ver "Como habilitar") |
| `502 LLM_ERROR` no `/chat` ou `/create-proposal` | `OPENROUTER_API_KEY` desatualizada em Vercel | Upsert env com valor do 1P + commit vazio pra forçar rebuild (Vercel cacheia env em serverless) |
| `502 META_UNAVAILABLE` no `/insights` | Token Meta inválido / expirado / conta sem permissão | Validar token com `curl /me?access_token=X`. Se conta faltando, checar partner flow no BM |
| Campanhas aparecem zeradas | Conta 100% pausada ou sem gasto em 7d — comportamento correto | Nenhum fix — realidade da conta |
| Menu não aparece pra tenant com flag on | Cookie de impersonation stale (super_admin vendo outro tenant) | Clear site data ou POST `/api/app/admin/impersonate` com body vazio pra sair |
| `subcode 4834011` ao criar campanha via API direta | Meta exige `is_adset_budget_sharing_enabled` | Passar `false` (o `createCampaignDraft` já cobre — só afeta quem chama Graph API direto) |

## 📚 Referências

- Issue: [DEV-1474](https://linear.app/cadencia/issue/DEV-1474)
- PR: [#198](https://github.com/felipeluissalgueiro/cadencia-app/pull/198) merge commit `228053b`
- Persona Pedro: `times/marketing/comunicacao/trafego/CLAUDE.md` (pd-framework)
- Cliente Iasmin: `times/produto/consultorias/iasmim-lopes/CLAUDE.md`
- Incidente relacionado: PR #271 quebrou auth por adicionar rota pública sem cascata — fix PR #274 `bypassSupabaseAuth`
- Mecanismo da flag: DEV-829 (`/app/admin/flags` + `POST /api/app/toggle-config`)

## Histórico

- **2026-08-02** — Merge em prod (commit `228053b` cadencia-app). Fix header dinâmico + rebase + migration aplicada.
- **2026-07-31→08-02** — Retomada da execução (parada 12d). Migration + seed + env Vercel + rebase + 2 fixes (P2 review + header hardcoded).
- **2026-07-21** — Plano técnico aprovado (Vitor/Time Dev). Branch criada.
- **07-2026** — Protótipo demo Iasmin ativo em preview via envs `META_DEMO_*` + `TRAFEGO_DEMO_TENANT_ID`.
