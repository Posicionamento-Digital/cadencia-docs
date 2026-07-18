---
date: 2026-05-22
tags: [infra, vps, coolify, deploy, cicd]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]", "[[ecuro-mcp]]", "[[pd-portal]]"]
---
# VPS Master — Coolify (CI/CD)

---

## O que é o Coolify

Painel self-hosted de deploy automático (alternativa ao Vercel/Railway na própria VPS). Quando dev externo faz push para `main` em um repo GitHub, o Coolify detecta via webhook e faz o deploy automático.

**URL:** `https://coolify.cadencia.ia.br`

**Login:** Felipe sabe as credenciais.

**API token:** vault 1Password **Hosts** → item **Coolify - API - VPS Master**

---

## GitHub App

O Coolify usa um GitHub App instalado na org para clonar repos privados e receber webhooks.

| Campo | Valor |
|---|---|
| Nome | `coolify-vpsmaster` |
| Org | `Posicionamento-Digital` |
| App ID | 3817023 |
| Installation ID | 134754308 |

**Credenciais completas:** vault 1Password **Hosts** → **Coolify - GitHub App coolify-vpsmaster** e **Github - App Coolify - Private key**

> O GitHub App tem acesso à org `Posicionamento-Digital`. Para repos da conta pessoal `felipeluissalgueiro`, o app precisa ser instalado separadamente.

---

## Traefik

O Coolify gerencia o Traefik como reverse proxy:

- Container: `coolify-proxy`
- Versão: **traefik:v3.3.5** (fixada — não atualizar sem revisar changelog)
- Arquivo compose: `/data/coolify/proxy/docker-compose.yml`
- Auto-update: **desativado** (risco de memory leak — incidente Deyvin)

---

## Projeto no Coolify

**Destino padrão de TODO app PD novo (decisão Felipe 2026-06-27):** `Cadencia`
- **UUID:** `wbaqjeeyabmiy0gylk8ywutf`
- **Environment:** `production` (id 7, uuid `nxo9m0598haj9vwk7qj2s1w5`)

**Outros projetos (legados / clientes):**
- `Posicionamento Digital` (`fjd0bm5uozujjr5bhj5wjsrv`, env id 2) — **LEGADO** (era "VPS Master PD"). Apps já cadastrados ficam (cadencia-growth, lara-ai, insight-artificial, ecuro-mcp, gci-go-whatsapp, pd-portal), mas nada novo. Migrar pra Cadencia oportunamente.
- `Lara` (`i11f3knrmhqnb8iiqbfwqhjh`, env id 4) — apps da cliente Lara (Lara v2, confirmation-queue, ecuro-middleware)

**UUID do servidor:** `f47nciccwtfzez16d4hlulhy` (localhost — a própria VPS)

## Provisionamento automatizado (skill `/coolify-provisionar-app`, 2026-06-27)

Validado E2E 9/9 PASS. Skill com 4 modos:

| Modo | Quando usar |
|---|---|
| Padrão (sem flag) | Repo novo + app novo — cria repo na org PD via `gh repo create`, commita boilerplate opcional, cria app Coolify Path A (GitHub App), webhook auto, auto-deploy ON. ~5 segundos. |
| `--app-only existing_repo=<owner/repo>` | Repo já existe (não vou criar de novo), só cria app Coolify ligado a ele. Pre-check detecta duplicação. |
| `--migrate-existing existing_app_uuid=<x> existing_repo=<y>` | App já existe no Coolify mas falta auto-deploy on-commit. Faz PATCH `is_auto_deploy_enabled=true` + cadastra webhook GitHub se necessário (caso deploy-key). Validado com DEV-678 (cadencia-workers). |
| `--migrate-from-vps vps_path=<path> existing_repo=<owner/repo>` | **App rodando direto na VPS Master (cron + daemons no host), sem Dockerfile/compose no repo.** Trabalho complexo: requer Dockerfile + supervisord + cut-over 48h. Detalhes em `~/.claude/skills/coolify-provisionar-app/SKILL.md` seção "Modo Migração-VPS". |

Cascata: invocada automaticamente por `/linear-criar-projeto` (tipo interno) e `/linear-planejar-issue` (1ª issue técnica de projeto cliente). Modo `--migrate-from-vps` é sempre **manual** (Felipe roda quando decide migrar legado).

## Migração de apps existentes da VPS Master pro Coolify

Pra apps rodando hoje em `/cadencia`, `/opt/<projeto>`, `/root/<projeto>` direto na VPS Master (cron + daemons no host), seguir o checklist da skill `--migrate-from-vps`. Resumo das 9 etapas:

1. **Pre-flight read-only** (SSH master): git status, daemons (`ps aux`), portas (`ss -tlnp`), crons (`crontab -l`), env vars (só chaves, sem valores), volumes, consumidores externos das portas, stack/deps.
2. **Inferir `requirements.txt`** (ou equivalente) e commitar no repo `main`.
3. **Criar `Dockerfile` + `supervisord.conf` + `.dockerignore`** no repo (Opção C recomendada: 1 app + N Scheduled Tasks no Coolify).
4. **Apagar app Coolify órfão** se houver entrada legada que nunca subiu.
5. **Criar app novo** no projeto Cadencia via `/coolify-provisionar-app --app-only` (auto_deploy=false até cut-over).
6. **Copiar env vars** do `.env` da VPS via SSH → `POST /applications/{uuid}/envs/bulk`. Valores NUNCA em transcript.
7. **Criar Scheduled Tasks** no Coolify (1 por entrada do crontab original).
8. **1º deploy + validação** (portas respondem, 1ª Scheduled Task executa).
9. **Cut-over com janela de 48h** (comentar crons + parar daemons VPS, container Coolify assume, descomentar se quebrar). Após 48h estável, remover crons da VPS e atualizar regras do `CLAUDE.md` do repo migrado.

**Espelho dentro do repo migrado:** sempre criar `docs/migracao-coolify.md` no repo com o estado mapeado + plano específico daquele app, pra histórico canônico. Exemplo de referência: `docs/migracao-coolify.md` em `Posicionamento-Digital/cadencia-growth`.

**Limitação conhecida** (2026-06-27): deleção automática de repo na org PD ainda requer ajuste de PAT fine-grained (`Administration: write` no nível organization). Workaround: deletar repos órfãos pela UI GitHub.

### Aplicações configuradas

| Aplicação | Repo | UUID | Build | Env vars | Status |
|---|---|---|---|---|---|
| cadencia-growth | Posicionamento-Digital/cadencia-growth | j5xc8t3rcj37jtk2fonqhguh | docker-compose | ✅ 16 vars | Pronto para deploy |
| lara-ai | Posicionamento-Digital/lara-ai | iyqwooh6qlfyz2gyl4ajm6kp | docker-compose | ✅ 46 vars | Pronto para deploy |
| insight-artificial | Posicionamento-Digital/insight-artificial | lj10dgkkeo74rbxlcj3omwt0 | dockerfile | ✅ 6 vars | Pronto para deploy |
| gci-go-whatsapp | Posicionamento-Digital/gci-go-whatsapp | uzh34wi3iqsmhbpezihbbujp | docker-compose | ⚠️ pendente dev externo | Aguardando env vars |
| ecuro-mcp | Posicionamento-Digital/ecuro-mcp | al3me08q5svp9sqh5m91ik21 | docker-compose | ⚠️ pendente dev externo | Aguardando env vars |
| pd-portal | Posicionamento-Digital/pd-portal | c26ri7dkjtg9a11y376re4i0 | docker-compose | ⚠️ verificar repo | Aguardando env vars |

> ⚠️ **IMPORTANTE:** nenhuma aplicação foi deployada pelo Coolify ainda. Os containers que estão rodando foram iniciados manualmente. Antes do primeiro deploy pelo Coolify, verificar env vars e testar começando pelo **insight-artificial** (menor risco).
>
> **Para gci-go-whatsapp e ecuro-mcp:** pedir vars ao dev externo → configurar em `coolify.cadencia.ia.br` → VPS Master PD → app → Environment Variables.

---

## Como fazer o primeiro deploy pelo Coolify

Para cada aplicação que quiser migrar para o Coolify:

1. Acessar `https://coolify.cadencia.ia.br`
2. Projeto **VPS Master PD** → aplicação desejada
3. Aba **Environment Variables** → adicionar todas as vars necessárias
4. Aba **Configuration** → verificar porta, branch, Dockerfile path
5. Clicar **Deploy** → Coolify faz o build e sobe o container
6. Parar o container antigo (que foi iniciado manualmente)

### Fluxo automático após setup

```
dev externo faz commit + push para main
       ↓
GitHub dispara webhook para coolify.cadencia.ia.br
       ↓
Coolify detecta mudança no repo
       ↓
Build da imagem Docker
       ↓
Deploy do novo container
       ↓
Substitui o anterior sem downtime (rolling deploy)
```

---

## Repos GitHub configurados na org

| Repo | Descrição |
|---|---|
| Posicionamento-Digital/gci-go-whatsapp | Bots WhatsApp GCI GO |
| Posicionamento-Digital/cadencia-growth | Growth pipeline Cadência |
| Posicionamento-Digital/ecuro-mcp | MCP server ecuro |
| Posicionamento-Digital/pd-portal | Portal PD |
| Posicionamento-Digital/lara-ai | Lara AI (espelho openclaw-state) |
| Posicionamento-Digital/insight-artificial | Pipeline Insight Artificial |

---

## Branch protection

**Status atual:** não implementado (plano gratuito GitHub não suporta em repos privados).

**Processo acordado enquanto isso:**
1. dev externo cria uma branch para sua feature
2. Abre PR para `main`
3. Felipe revisa e aprova
4. Merge na `main` → Coolify deploya automaticamente

---

## Acessar o painel Coolify

```bash
# Abrir no browser diretamente
# URL: https://coolify.cadencia.ia.br

# Se precisar acessar via SSH tunnel (porta 8000 interna)
ssh -L 8000:localhost:8000 vps-master
# Abrir: http://localhost:8000
```

---

## Operações comuns via API

```bash
# Variável de ambiente
COOLIFY_TOKEN="<token do 1P>"
BASE="http://coolify.cadencia.ia.br"  # ou http://72.60.4.71:8000

# Verificar versão
curl -s "$BASE/api/v1/version" -H "Authorization: Bearer $COOLIFY_TOKEN"

# Listar servidores
curl -s "$BASE/api/v1/servers" -H "Authorization: Bearer $COOLIFY_TOKEN"

# Listar projetos
curl -s "$BASE/api/v1/projects" -H "Authorization: Bearer $COOLIFY_TOKEN"
```

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Arquitetura]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Projetos-opt]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Seguranca]]
