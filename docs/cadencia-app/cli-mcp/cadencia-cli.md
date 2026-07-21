---
date: 2026-06-22
tags: [documentacao, projeto]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[comercial]]", "[[marketing]]"]
---
# cadencia-cli — documentação técnica

CLI/lib Python para operar o **Cadencia** por terminal/agente. Repo `Posicionamento-Digital/cadencia-cli` (clone `Hub Projetos/_repos/cadencia-cli`). Projeto Linear: Cadencia — CLI/MCP de Controle (`7648831d`).

## Identidade
- **Tipo:** lib + CLI (backend, operador)
- **Stack:** Python 3.12, typer (CLI), httpx (HTTP), pytest. 1Password (credenciais), SSH (disparo worker).
- **Path:** `_repos/cadencia-cli` · **Status:** ativo, em produção (**105 comandos · 265 testes**)

## Arquitetura (3 camadas)
lib (`src/cadencia_cli/`) → CLI fina (`cli.py`) → MCP futuro. Registry/plugin auto-registrável (`@action`). Camada de acesso por comando: READ (Supabase blindado) / WRITE (CRUD blindado) / MUTATION (regra de negócio — **futura RPC Postgres**; DEV-582 cancelada) / DISPATCH (SSH na VPS Master).

## Comandos
- **contacts** — list/get/search/create/update + **cpf/registro_profissional/endereço** + note/notes + activity/activities + tag + link-company + **add/list/remove email|phone** (multi-contato) + **find** (resolve por nome/email/tel) + enrich (até RPC)
- **companies** — list/get/search/create/update (+ **site/endereço estruturado**) + link-contact/contacts
- **opportunities** — list/get/create/update/close/move
- **cadences** — list/create/add-step/steps + **status** `<contact_id>` (inscrições do contato com posição atual) + **atrasados** `[--cadence X] [--limit N]` (contatos com toque vencido — `next_send_at < now()`)
- **tasks** — create/list/get/**hoje**/complete/delete (follow-ups, soft-delete)
- **products** — list/get/create/update + link-contact/unlink/contacts/of-contact
- **pipeline** — summary/forecast (contagem+valor por stage)
- **leads** — **search/import/enrich-company** por CNPJ (CNPJ.ws gratuito)
- **loss-reasons** list · **credits** balance/history
- **pipelines / pipeline-stages / tags / custom-fields / crm-views** — list (metadados)
- **tenants** — provision/set-config/set-dossier/set-editorials/set-visual/upload-asset/verify (dispatch pendente)
- **content** — ideas/documents/queue/published, growth-dispatch, newsletter-dispatch, carousel-dispatch (bloqueado), **publish**

## Como funciona
Casca typer monta comandos do registry → ação resolve a camada de acesso → Supabase (read/write blindado por tenant_id) ou SSH (disparo do worker `<canal>_generate.py` na VPS Master). Tenant default PD; override por `CADENCIA_TENANT_ID`.

## Quickstart
```bash
cd _repos/cadencia-cli && pip install -e .
export SUPABASE_ACCESS_TOKEN=$(op item get "Supabase - ClaudeCode - CLI" --vault databases --fields credencial --reveal)
cadencia-cli contacts list --limit 10
cadencia-cli content publish --title "Post sobre X" --channel blog --send
```

## Decisões (ADRs)
Repo dedicado (não dentro de cadencia-app); disparo via SSH (dispensa TRIGGER_SECRET); status sempre `dispatched`. **DEV-582 cancelada (2026-06-24):** HMAC/token de serviço é redundante no uso interno (segurança vem do controle de acesso ao ambiente); a regra de negócio do `enrich` (crédito + API paga) será uma **RPC Postgres**, não endpoint HMAC. Detalhe em `docs/decisions.md` do repo + nota [[Autenticacao de API - Bearer vs HMAC]].

## Don'ts
- Não hardcodar destino de worker (config/env).
- Não gravar mutação com lógica de negócio (crédito) direto no Supabase — vai contornar débito/idempotência. Caminho futuro = RPC Postgres.
- service_role bypassa RLS — sempre filtrar tenant_id.

## Gaps de produto (fora da CLI)
SOAP + cadências 10D (DEV-779/784, dependem do engine CAD-579/580/581 inexistente); carrossel self-service (DEV-773); canais Threads/TikTok/YouTube (DEV-771, APIs externas); enrich PF (DEV-782, via RPC futura); leads por setor (DEV-783 follow-up, DataStone pago).

## Histórico
- **2026-07-18** — DEV-784: **cadences — 2 comandos READ de runtime** (`status <contact_id>` + `atrasados`). 16 testes novos (e2e offline via CliRunner). CLI: 103→105 comandos, 249→265 testes. PR #35 mergeado. Nota: `status='running'` (não `'active'`) é o que a engine grava — filtrar errado devolve vazio em silêncio.
- **2026-06-24** — Sessão MODO B: **11 issues, CLI 67→103 comandos, 249 testes**. contacts (cpf/endereço + multi-email/phone atômico + find), companies (site/endereço), enums lifecycle PT, módulos novos tasks/products/pipeline/sales_utils/leads. 4 módulos comerciais em paralelo (subagentes). **DEV-582 cancelada.** Trabalho migrou pra clone fora do OneDrive (revertia arquivos).
- 2026-06-22 — V1 (4 Epics/15 stories) + disparo SSH (DEV-747) + comercial avançado (E1) + content publish (F1). Bug do worker `titulo` corrigido (DEV-748).

## Cascateamento (skills)
As skills atômicas `cadencia-<area>-<comando>` (22 comercial + 12 conteúdo, nos squads) são as peças. Skills existentes que as cascateiam: comercial (`/registrar`, `/proposta`, `/agenda`, `/eduardo-preparar-call`), marketing (`/rafael-blog-cadencia`, `/nutricao-seinfeld`, `/nutricao-newsletter`), Linear (`/linear-criar-projeto`, `/criar-reuniao`). Mapa visual: [[Cadencia-CLI-Cascatas]] (canvas).

## Notas relacionadas
[[Projetos/Cadencia-CLI-MCP/Brief]] · [[Projetos/Cadencia-CLI-MCP/PRD]] · [[Cadencia-CLI-Cascatas]]
