---
tipo: processo-operacional
categoria: operacional
squad: operacional
versao: 1.0.0
managed_by: documentar-processos
atualizado_em: 2026-07-22
autor_decisao: Felipe Salgueiro
---

# Criar página ou site novo no ecossistema Cadencia

<!-- documentar-processos:managed START -->

## Trigger

Você precisa disparar este processo quando:

- Um **funcionário PD** precisa acessar um material que ainda não existe (ou está espalhado em Obsidian/Drive)
- Um **cliente** precisa ver algo dedicado a ele (guia de operação, playbook customizado, área white-label)
- Um **parceiro/revendedor** precisa acessar material de referência (ex.: Programa de Revenda pro Vayne)
- Um **aluno de treinamento** precisa de kit próprio
- Você percebeu que a mesma informação está sendo repetida em conversas — sinal de que virou candidato a doc

Se é **atualização** de página já existente, não use este processo — edite direto no repo do site (ver Refs).

## Steps

| # | Ação | Dono | Ferramenta | Tempo |
|---|---|---|---|---|
| 1 | **Definir o público-alvo.** Uma pessoa (Vayne), um grupo (staff PD), um cliente (OP Odontopenha), aluno? Anote nome + emails que vão acessar. | Felipe (ou quem pediu) | conversa | 2 min |
| 2 | **Decidir: página nova em site existente OU site novo?** Se já existe site que serve esse público (ex.: `cadencia-docs` pra staff, área de cliente existente etc.), é página nova. Se público novo/isolado, é site novo. | Felipe | tabela de decisão abaixo | 5 min |
| 3 | **Escolher estratégia de gate de acesso** (A / B / C — ver tabela abaixo). Padrão é A ou B; C só se A/B não servir. | Felipe | tabela de decisão abaixo | 5 min |
| 4a | **(Se página nova em site existente)** cd no repo, criar `.md` em `docs/<área>/`, adicionar entry em `nav:` do `mkdocs.yml`, commit e push em `main`. GitHub Actions builda `site/` sozinho e Vercel serve em ~2min. **Não commite `site/` local** — rebase conflict garantido. | agente IA (ou dev) | git + editor | 10 min |
| 4b | **(Se site novo)** rodar skill `/criar-site-protegido` do PD Framework — provisiona repo GitHub, Vercel, DNS Cloudflare, envs, e cria item no sidebar do Cadencia. Ela pergunta os 4 parâmetros (slug, domínio, roles, template) e faz o resto. | agente IA | `/criar-site-protegido` | 30-45 min |
| 5 | **(Se Estratégia B — allow-list)** adicionar emails no Vercel do `cadencia-app`, env var `DOCS_<AREA>_EMAILS` (CSV). Sempre `echo -n` pra evitar newline. Trigger redeploy. | agente IA | `vercel env add` | 3 min |
| 6 | **Validar acesso.** Se A: staff vê item no sidebar. Se B: user X (não staff) vê item. Se C: curl com sessão válida retorna 200; sem sessão retorna 302 pro login. | agente IA | `curl` + validação humana no browser | 5 min |
| 7 | **Comunicar quem tem acesso.** WhatsApp/email pro público-alvo dizendo "está pronto, acessa em <URL>". | Felipe (comercial se cliente/parceiro) | `/mandar-whatsapp` ou `/enviar-email` | 5 min |
| 8 | **Registrar no Linear** (se comercial/CS): touchpoint automático no CRM Cadencia + issue de acompanhamento se cliente. | agente IA | Linear MCP + `cadencia-cli` | 3 min |

### Tabela de decisão — Estratégia de gate

O `cadencia-docs` (site principal) usa este padrão desde 2026-07-22. Vale pra qualquer site novo também.

| Estratégia | Quem acessa | Como funciona | Quando usar |
|---|---|---|---|
| **A — Sidebar-only (super_admin)** | Só staff PD | Site é público em URL, mas item no sidebar do Cadencia só aparece pra `super_admin`. Quem não é staff nunca descobre a URL. | Docs internas, material técnico interno, roadmap. Ex.: `cadencia-docs` como um todo. |
| **B — Sidebar + allow-list de email** | Staff + grupo externo específico | Site continua público, item no sidebar aparece pra super_admin OU pra emails na env var `DOCS_<XXX>_EMAILS`. | Revendedor (Vayne), consultor parceiro, cliente-piloto. Padrão desde 22/07. |
| **C — Middleware Edge real** | Externo sem login Cadencia OU exige 403 real com URL vazada | Middleware valida JWT + role diretamente no site. Mais complexo, mais peças pra manter. | Portal com cliente final que loga direto no subdomínio, extranet auditada. Só se A/B não servir. |

**Regra dura:** se você não consegue explicar por que A ou B não serve, **use A ou B**. Middleware (C) trouxe 2h de downtime em 21/07 quando foi implementado sem necessidade. Detalhe em `pd-framework/stamper/skills/criar-site-protegido/SKILL.md § Passo 0`.

### Tabela de decisão — Página nova ou site novo?

| Situação | Rota |
|---|---|
| Público já tem acesso a algum site Cadencia (ex.: staff acessa `cadencia-docs`) | **Página nova nesse site** (Step 4a) |
| Público é novo e isolado (ex.: portal de agência parceira com branding próprio) | **Site novo** (Step 4b) |
| Cliente pediu área white-label com domínio próprio | **Site novo** (Step 4b) + domínio customizado |
| Página existe mas está desatualizada | **NÃO é este processo** — só edite direto e commite |

## Output

Ao final, você tem:

- URL viva servindo o conteúdo (`docs.cadencia.app.br/<área>/<slug>/` ou domínio próprio)
- Público-alvo notificado por WhatsApp/email
- Gate de acesso funcionando (validado no Step 6)
- Se B: env var `DOCS_<XXX>_EMAILS` populada no Vercel prod
- Se site novo: item no sidebar do Cadencia + registro Linear de rastreamento

## Failure modes

| Sintoma | Causa provável | Fix |
|---|---|---|
| User loga e não vê o item no sidebar | Cache do browser (hydration antiga) | Hard-refresh (Ctrl+Shift+R). Se persistir, checar email na allow-list (`vercel env pull`) |
| User vê item mas clique dá 404 | Página ainda não buildou (Actions em execução) | Aguardar ~2min. `vercel ls <project> --prod` mostra status |
| Deploy conflita rebase em N arquivos `site/*.html` | Alguém commitou `site/` local em paralelo ao Actions bot | Nunca commitar `site/` local. `git checkout -- site/` e recomeça |
| Env var com newline quebra o site | Uso de `echo` sem `-n` | `echo -n "valor" \| vercel env add ...` — sempre `-n` |
| Cookie de login em `cadencia.app.br` não é reconhecido em `<sub>.cadencia.app.br` | `NEXT_PUBLIC_COOKIE_DOMAIN` faltando no cadencia-app | Ver `criar-site-protegido/SKILL.md § Passo 9.4` |
| "Já criei middleware e agora loop de redirect" | Estratégia C escolhida sem necessidade | Reveja a tabela de estratégia. 90% dos casos = B, não C |

## SLA

- **Página nova em site existente:** publicada em até **1 hora** desde o pedido
- **Site novo com Estratégia A ou B:** publicado em até **1 dia útil** (provision + DNS propagation + comunicação)
- **Site novo com Estratégia C:** até **2 dias úteis** (adiciona ciclo de teste do middleware com sessão real)

## Refs cruzadas

- **Skill executável (agente IA):** `pd-framework/stamper/skills/criar-site-protegido/SKILL.md` — provisiona site novo end-to-end
- **Padrão de sidebar do Cadencia:** commits `6e05bc6` (item Programa de Revenda) e `b5a6859` (cookie cross-subdomain), ambos cadencia-app 22/07
- **Incidente que originou o padrão:** [Middleware cadencia-docs 21/07](../_dev-process/incidentes/2026-07-21_2026-07-21_cadencia-docs-middleware-auth-cross-domain.md) — 2h de downtime por middleware desnecessário
- **Onde adicionar novo revendedor:** env var `DOCS_RESELLER_EMAILS` no Vercel prod do `cadencia-app`
- **Onde adicionar novo funcionário PD:** basta ter role `super_admin` em `user_tenant_roles` no Supabase Cadencia — item admin_docs já aparece automaticamente

<!-- documentar-processos:managed END -->

## Notas manuais

_(Editar livremente abaixo — não gerenciado por skill.)_
