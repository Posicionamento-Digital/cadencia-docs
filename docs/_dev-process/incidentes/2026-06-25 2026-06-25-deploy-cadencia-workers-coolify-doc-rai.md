---
type: source
source_kind: incidente
date: 2026-06-25
entities: ["[[Cadencia]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-06-25_deploy-cadencia-workers-coolify-doc-railway-vps-saturada

# Deploy cadencia-workers: doc apontando Railway descontinuado + build travado por VPS saturada

**Data:** 2026-06-25
**Severidade:** Média
**Projeto:** Cadência (cadencia-workers)
**Duração:** ~1h40 (build ~1h + 1 deploy não-promovido + redeploy)
**Tags:** #deploy #infra #coolify #railway #vps #silenciosa

## O que aconteceu

Durante o deploy do fix DEV-859 (slide CTA vazio) no `cadencia-workers`, dois problemas encadeados:

1. **Quase-deploy no lugar errado.** A cópia local da doc `times/produto/cadencia/docs/infra-cli-access.md` (sync de 29/05) ainda descrevia o deploy dos workers via **Railway** + `railway.toml` no repo. O agente seguiu essa pista e ia disparar deploy no Railway — **descontinuado**. O Felipe interrompeu ("não usamos mais Railway"). A fonte de verdade correta é o **ADR-0012** (workers migraram pro Coolify VPS Master em 20/06).

2. **Build estourou ~1h e o 1º Redeploy não promoveu o container.** O Redeploy no Coolify buildou a imagem (`1906f18`) mas levou ~1h só no `pip install` por **saturação da VPS Master** (steal ~38% pelo hypervisor Hostinger, load 5.5 em box de 2 vCPU, ~290 MB RAM livre). O deployment do Coolify aparentemente bateu timeout: a imagem ficou pronta mas o **container nunca foi promovido** (continuou rodando a imagem antiga de 19/06; helper de build ficou órfão "Up 9h"). Pelo painel "parecia ok", mas o fix **não estava no ar**.

## Causa raiz

1. **Drift de documentação:** `docs/infra-cli-access.md` (cópia no framework) desatualizada vs ADR-0012. O bloco Railway não foi removido/marcado como legado na cópia local — só no master do repo.
2. **Capacidade da VPS Master:** box de 2 vCPU compartilhado (lara, ecuro, temporal, evolution, postgres, mission_control, vários uvicorns) + build do Chromium/Playwright por cima → contention extrema. O `start_period`/timeout do orquestrador Coolify não tolera build de ~1h, deixando deployment em estado inconsistente (imagem buildada, container não trocado, helper órfão).

## Por que não foi detectado

- O painel do Coolify mostrava o deployment como aparentemente concluído, mas a verificação real (imagem em uso pelo container via `docker inspect`) provou que o swap não ocorreu.
- Sem validação pós-deploy do **conteúdo do container** (não só health 200), o "deploy ok" era falso — o health 200 vinha do container **antigo**.

## Como foi corrigido

- **Doc errada:** consultada a fonte de verdade (ADR-0012 + `infra-cli-access.md` do master no GitHub) → deploy é via API Coolify (`POST /api/v1/deploy?uuid=x10s2h2186f7n81496rn6puh`), auto-deploy OFF por design (CAD-678).
- **Deploy travado:** 2º Redeploy (manual, painel) — imagem já cacheada → build em ~3min, **rolling update completou healthy às 15:02** (commit `43bf092`). Container antigo removido.
- **Validação definitiva:** `docker exec <container> grep` no `_TYPE_MAP` em prod confirmou `"ação"/"acao"/"action": "cta"` rodando. Health 200.
- **Mapa 1P atualizado:** item `Coolify - API - VPS Master` (vault Hosts, campo `password`) adicionado ao `Credenciais/mapa-1password.md` com o comando de deploy.

## Prevenção

- [ ] **Sincronizar `docs/infra-cli-access.md` no framework** (rodar `/documentar` ou `sync_cadencia_docs.py`) — a cópia local está em drift desde 29/05. Marcar bloco Railway como LEGADO igual ao master.
- [ ] **Validar deploy pelo conteúdo do container, não só health:** `docker inspect <cid> --format '{{.Image}}'` deve bater com a imagem do commit deployado; ou `docker exec` num marcador do código. Health 200 sozinho pode ser o container antigo.
- [ ] **Aliviar a VPS Master antes de builds pesados** (ou subir o cap/box): build do Chromium em 2 vCPU com steal ~38% leva ~1h e arrisca timeout do Coolify. Considerar build com mais recursos ou registry pré-buildado.
- [ ] **Após Redeploy do Coolify, confirmar promoção:** checar que não sobrou helper órfão (`docker ps | grep <helper-hash>`) e que o container tem `RunningFor` recente.
- [ ] **Token Coolify no 1P:** usar `op item get "Coolify - API - VPS Master" --vault Hosts --fields password` (evita rate-limit por busca às cegas no SA).

### Pattern correto (deploy worker Coolify)
```bash
TOKEN=$(op item get "Coolify - API - VPS Master" --vault Hosts --fields password --reveal)
curl -s -X POST "https://coolify.cadencia.ia.br/api/v1/deploy?uuid=x10s2h2186f7n81496rn6puh" -H "Authorization: Bearer $TOKEN"
# validar: docker inspect do container = imagem do commit, e docker exec grep do código
```

## Commits relacionados

- `e15e040`, `ff28524` — fix DEV-859 (slide_renderer `_TYPE_MAP`).
- `1906f18` — merge PR #72 no master.
- `43bf092` — commit efetivamente deployado (rolling update 15:02).

## Links relacionados

- Issue: DEV-859 (maint: Cadência — Bugs e suporte)
- ADR-0012 — Workers Railway → Coolify (fonte de verdade)
- `times/produto/cadencia/context/runtime-fix-review-DEV-859.md`
