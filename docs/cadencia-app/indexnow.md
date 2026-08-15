# IndexNow — notificação de URLs públicas

> Site institucional: [DEV-1774](https://linear.app/cadencia/issue/DEV-1774) (PR #331 `826eb65`, 2026-08-15).
> Blogs de tenant + provisionamento automático: [DEV-1775](https://linear.app/cadencia/issue/DEV-1775) (PR cadencia-app #333 + cadencia-growth #136).
> Público: quem precisa adicionar página SEO nova no `cadencia-app`, ou a skill `/cadencia-nova-pagina-seo` executando o fluxo, ou provisiona/administra tenant novo.

## O que é

**IndexNow** é o padrão HTTP aberto (adotado por **Bing, Yandex, Naver, DuckDuckGo, Seznam**) que permite avisar buscadores em segundos quando uma URL foi criada ou alterada. Substitui espera passiva de recrawl (dias/semanas) por notificação ativa em push.

**Motivo estratégico:** o ChatGPT usa Bing como fonte de busca em várias respostas. Aparecer no Bing rápido = aparecer no ChatGPT rápido — é o argumento da página [`/casos-de-uso/aparecer-no-chatgpt-e-no-google`](https://cadencia.app.br/casos-de-uso/aparecer-no-chatgpt-e-no-google) aplicado ao próprio site.

## Como funciona no cadencia-app

Fluxo em 3 partes:

1. **Chave pública** em `public/205cc7b8fb186b7909a4148c935785c9.txt` — validação de propriedade do domínio (o protocolo exige que a chave esteja acessível na URL declarada em `keyLocation`)
2. **Workflow GitHub Action** (`.github/workflows/indexnow.yml`) — dispara em push pra `master` (automático) ou `workflow_dispatch` manual
3. **Scripts Python** (`scripts/indexnow_urls.py` + `scripts/indexnow_payload.py`) — resolvem URLs alteradas a partir do checkout local e enviam POST único pra `https://api.indexnow.org/indexnow`

Resposta esperada: **HTTP 200 ou 202**. Validado em produção com POST real antes do merge inicial.

## Chave

- **Chave pública:** `205cc7b8fb186b7909a4148c935785c9`
- **Arquivo:** `public/205cc7b8fb186b7909a4148c935785c9.txt`
- **URL de validação:** `https://cadencia.app.br/205cc7b8fb186b7909a4148c935785c9.txt`

Chave **não é segredo operacional** — o protocolo IndexNow exige que ela seja pública no domínio (é como o buscador confirma que quem envia o ping é dono do site). Se rotacionar, trocar em 3 lugares no mesmo PR: (1) arquivo em `public/`, (2) `INDEXNOW_KEY` no workflow, (3) `INDEXNOW_KEY_LOCATION` no workflow.

Registrada também no **1Password** vault `Serviços & Tools` como item `IndexNow - cadencia.app.br` (só pra rastreabilidade operacional — pode ser lida direto do repo).

## Cobertura de URLs

O `scripts/indexnow_urls.py` mapeia caminhos alterados em URLs públicas usando duas estratégias.

### 1. Coleções automáticas (via `src/data/*.ts`)

Editar essas fontes = todas as URLs da coleção são notificadas:

| Arquivo alterado | URLs notificadas |
|---|---|
| `src/data/features.ts` | Todos os `/ferramentas/*` (15 URLs em 2026-08) |
| `src/data/cases.ts` | Todos os `/casos-de-uso/*` (20 URLs em 2026-08) |
| `src/data/lessons.ts` | Todos os `/desenvolvendo-com-ia/*` (3 URLs em 2026-08) |

Slug regex: `^\s*slug:\s*["'` + "`" + `]([^"'` + "`" + `]+)["'` + "`" + `]` — extraído por linha do TS.

### 2. Páginas estáticas declaradas

Dict `STATIC_PAGES` + `STATIC_PAGE_DIRS` no script:

| Path do arquivo | URL |
|---|---|
| `src/app/(marketing)/page.tsx` | `/` |
| `src/app/(marketing)/felipe-luis-salgueiro/**` | `/felipe-luis-salgueiro` |
| `src/app/(marketing)/en/felipe-luis-salgueiro/**` | `/en/felipe-luis-salgueiro` |
| `src/app/(marketing)/imprensa/**` | `/imprensa` |
| `src/app/(marketing)/treinamentos/**` | `/treinamentos` |

### 3. Wildcards globais

Alteração em `src/app/sitemap.ts`, `src/app/robots.ts`, `src/app/layout.tsx`, `next.config.ts`, ou componentes globais de marketing → **sitemap público inteiro é notificado**.

### 4. Rotas privadas — bloqueadas

`PRIVATE_PREFIXES` no script filtra: `/app`, `/admin`, `/api`, `/auth`, `/staff`, `/onboarding`, `/conectar-whatsapp`, `/_next`. Nunca são enviadas mesmo se alteradas.

### 5. Dispatch manual (`workflow_dispatch`)

Trigger manual no GitHub → Actions → IndexNow → Run workflow, input `urls` recebe URLs absolutas ou paths separados por vírgula/espaço. Vazio = sitemap inteiro.

## Integração com `/cadencia-nova-pagina-seo`

A skill do squad Cadencia `/cadencia-nova-pagina-seo` (em `times/produto/cadencia/skills/cadencia-nova-pagina-seo/`) respeita as regras acima:

| Tipo de página criada pela skill | Precisa tocar `indexnow_urls.py`? |
|---|---|
| **Ferramenta** (edita `src/data/features.ts`) | Não — cobertura automática |
| **Caso de uso** (edita `src/data/cases.ts`) | Não — cobertura automática |
| **Aula** (edita `src/data/lessons.ts`) | Não — cobertura automática |
| **Avulsa** (cria `src/app/(marketing)/[slug]/page.tsx` livre) | **Sim, obrigatório** — adicionar entrada em `STATIC_PAGES` no PR |

A regra está explicitada na skill (§Regras absolutas item 7) — sem essa entrada, o workflow não notifica IndexNow em push, e a página nova fica invisível pros crawlers de LLM até recrawl passivo.

## Decisão arquitetural — Python vs Node

O workflow usa Python (não Node) apesar de o cadencia-app ser majoritariamente TypeScript.

**Contexto:** PR #330 (versão descartada) usou Node ESM (`scripts/submit-indexnow.mjs`) mantendo consistência de stack. PR #331 (versão mergeada) usou Python 2 arquivos.

**Por quê Python foi escolhido:**
- **GitHub Actions runners Ubuntu** têm Python 3 pré-instalado, sem `npm ci`
- Elimina passo de instalação (`npm ci` no #330 levava ~30-40s; Python roda imediato)
- Scripts são standalone, sem dependência de `package.json` do cadencia-app
- Regex + JSON stdlib do Python bastam — não precisa nada de terceiros

**Trade-off:** introduz Python no repo. Aceitável pois:
- Contained em `scripts/indexnow_*.py` (2 arquivos, ~165 linhas totais)
- Não é importado por nenhum código do produto — apenas invocado por workflow
- Repo já tem `cadencia-workers/` (Python) — Python não é estranho ao stack

## Race condition evitada — sitemap vs deploy

Cadencia-app deploya no Vercel via push → build → CDN, com janela onde `https://cadencia.app.br/sitemap.xml` ainda serve versão **antiga** (build anterior) enquanto o workflow IndexNow já disparou.

O PR #330 puxava URLs do sitemap **de produção** — sujeito a race: se o push era o primeiro a criar uma URL nova, o sitemap de prod ainda não a tinha, e o IndexNow era notificado da lista **velha**, deixando a página nova órfã até o próximo push.

**Solução no #331:** `scripts/indexnow_urls.py` resolve URLs do **checkout local** (workflow rodou `actions/checkout@v4`, então tem a versão certa). Nenhuma leitura de sitemap remoto — a fonte de verdade é o TS versionado.

## Teste manual

Após deploy, validar chave acessível:

```bash
curl -sI https://cadencia.app.br/205cc7b8fb186b7909a4148c935785c9.txt | head -1
# Esperado: HTTP/2 200
```

POST manual pra 1 URL:

```bash
curl -i -H 'Content-Type: application/json' \
  -X POST 'https://api.indexnow.org/indexnow' \
  --data '{"host":"cadencia.app.br","key":"205cc7b8fb186b7909a4148c935785c9","keyLocation":"https://cadencia.app.br/205cc7b8fb186b7909a4148c935785c9.txt","urlList":["https://cadencia.app.br/casos-de-uso/aparecer-no-chatgpt-e-no-google"]}'
```

Aceite: **HTTP 200 ou 202**. Qualquer outro código → investigar.

Verificar indexação em Bing depois de ~24-48h:
```
site:cadencia.app.br/<url-testada>
```

## Gotchas conhecidos

- **HTTP 400 antes do deploy da chave.** Se rodar o teste com `keyLocation` apontando pra URL que ainda não existe em produção (deploy Vercel não terminou), IndexNow rejeita. Aguardar deploy antes de testar manualmente.
- **Google Search Console não usa IndexNow.** Cobre Bing + Yandex + DuckDuckGo + Naver + Seznam. Google continua indexando via sitemap tradicional + solicitação manual em Search Console.
- **Limite de 10.000 URLs/dia pelo Bing.** Muito acima do que Cadencia gera (37 URLs no total do site institucional). Sem risco de bater o cap.
- **Não confundir com Bing Webmaster Tools API.** IndexNow é padrão aberto multi-buscador; Bing Webmaster Tools tem API própria de submissão de URL. Complementares — a manual do Bing Webmaster Tools ainda é útil pra validação e monitoramento.
- **Ping ≠ garantia de rank.** IndexNow confirma recebimento (HTTP 200/202), não garante indexação rápida nem posicionamento. É condição necessária, não suficiente.

## Referências

- Padrão oficial: <https://www.indexnow.org/>
- Documentação Bing: <https://www.bing.com/indexnow>
- Documentação Yandex: <https://yandex.com/support/webmaster/indexnow/>
- Endpoint POST: `https://api.indexnow.org/indexnow` (JSON com `{host, key, keyLocation, urlList}`)
- Issue: [DEV-1774 no Linear](https://linear.app/cadencia/issue/DEV-1774)
- PRs: [#331 mergeado](https://github.com/felipeluissalgueiro/cadencia-app/pull/331) · [#330 descartado](https://github.com/felipeluissalgueiro/cadencia-app/pull/330)
- Related (produto): [`/casos-de-uso/aparecer-no-chatgpt-e-no-google`](https://cadencia.app.br/casos-de-uso/aparecer-no-chatgpt-e-no-google) — o argumento do próprio produto sobre por que aparecer no ChatGPT importa
- Related (feature): DEV-1771 hub SEO — IndexNow é o próximo passo lógico de distribuição

## IndexNow em blogs de tenant (DEV-1775)

Além do site institucional, **todo blog de tenant** notifica IndexNow no momento em que um post é publicado. Arquitetura análoga mas com **chave por tenant** (isolamento por design).

### Componentes

| Arquivo | Papel |
|---|---|
| `cadencia-blog/src/lib/indexnow.ts` | Helper `notifyIndexNow(urls[])` fail-safe (log-only, timeout 10s) |
| `cadencia-blog/src/middleware.ts` | Serve `/<INDEXNOW_KEY>.txt` com o valor da chave em texto plano — matcher restrito a `/:key.txt` |
| `cadencia-blog/src/app/api/publish/route.ts` | Chama `notifyIndexNow([postUrl])` após `sbUpsert` — não muda contrato do webhook |
| `cadencia-growth/pipeline/provision_tenant.py` | Gera chave hex 32 chars e injeta 2 env vars no Vercel do tenant (`INDEXNOW_KEY` + `INDEXNOW_KEY_LOCATION`) |

### Chave por tenant

Cada tenant recebe chave própria (`secrets.token_hex(16)`) gerada no provisionamento. Env vars injetadas via Vercel API v10 (`/projects/<id>/env`).

- **Tenant novo**: nasce com IndexNow ativo — chave hospedada via middleware em `https://<slug>.cadencia.app.br/<chave>.txt`
- **Tenant existente**: ganha IndexNow automático quando `provision_tenant.py` roda de novo (helper `_vercel_add_env_if_missing` é idempotente — só adiciona se ainda não existir). Cron diário de tenants pending já dispara isso.

### Fluxo de notificação

```
Growth pipeline VPS gera post → POST /api/publish (webhook)
  → sbUpsert em published_posts
  → Next.js revalidate (cache invalidation)
  → notifyIndexNow([postUrl])  ← NOVO
  → POST api.indexnow.org (JSON com host/key/keyLocation/urlList do tenant)
  → HTTP 200/202 = sucesso; qualquer outro = log warn, publicação segue
```

### Fail-safe (não bloqueia publicação)

- Sem `INDEXNOW_KEY` no env: `console.warn` + `return false`, publicação segue normal
- Erro HTTP no IndexNow: `console.error` com status + primeiros 200 chars do body, publicação segue
- Timeout de 10s: `AbortController` cancela, publicação segue
- **Publicação nunca é abortada por IndexNow** — regra dura, IndexNow é notificação, não caminho crítico

### Insight Artificial

Blog separado (`insightartificial.ia.br`) — repo do site em si não localizado nesta sessão. Requer investigação separada + PR próprio. Não incluído em DEV-1775 executada.

## Histórico

- **2026-08-15 (site institucional)** — Feature inicial via DEV-1774. Workflow GitHub Action + scripts Python + chave estática + doc básica (PR #331 merged `826eb65`). Doc expandida com integração `/cadencia-nova-pagina-seo`, ADR Python vs Node, cobertura por tipo e gotchas.
- **2026-08-15 (blogs de tenant)** — Expansão via DEV-1775 (parte 1+2 no cadencia-app PR #333, parte 3+4 no cadencia-growth PR #136). Helper + middleware + integração no webhook `/api/publish`; provisionamento gera chave por tenant + retrofit inline. Parte 5 (Insight Artificial) e testes de retrofit em tenants individuais pendentes.
