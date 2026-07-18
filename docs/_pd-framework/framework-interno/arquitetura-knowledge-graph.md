---
date: 2026-07-04
tags: [doc, documentacao, projeto, framework, arquitetura]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Central de Observabilidade]]", "[[PD Framework]]", "[[comercial]]", "[[marketing]]", "[[pd-portal]]"]
---
# Arquitetura — PD Framework

> Gerado por `/documentar-software` alimentado pelo knowledge graph (`.understand-anything/knowledge-graph.json`, 04/07/2026 — 415 arquivos, 1.309 nós, 1.671 arestas, 8 camadas). Doc canônica de decisões: `CONTEXT.md` (raiz) + `_core/RUNTIME-CONTRACT.md`. Este arquivo é a visão C4 derivada do código real.

## Nível 1 — Contexto

```mermaid
graph TB
    Felipe[Felipe<br/>decisor + executor]
    dev externo[dev externo<br/>dev cadencia-app/pd-portal]
    Linear[(Linear<br/>fonte de verdade do trabalho)]
    OneP[(1Password<br/>fonte única de secrets)]
    Slack[(Slack<br/>notificação de máquina)]
    WhatsApp[(WhatsApp EVO/Stevo<br/>humano + urgente)]
    Supabase[(Supabase<br/>Hub PD + Cadencia)]
    VPSs[(VPS Master/Dev + Coolify + Vercel)]
    Obsidian[(Obsidian<br/>conhecimento)]

    subgraph PD [PD Framework]
        FW[Monorepo multi-agente<br/>kernel + squads + workers + adapters]
    end

    Felipe -->|abre squads, roda skills| FW
    FW -->|issues, claims, docs| Linear
    FW -->|secrets via SA headless| OneP
    FW -->|digest, deploys, alertas| Slack
    FW -->|urgências, handoffs| WhatsApp
    FW -->|sinks: deploys, audit, corpus| Supabase
    FW -->|workers cron/systemd, deploy| VPSs
    FW -->|notas, wiki| Obsidian
    dev externo -->|framework próprio, espelhado via luiz_state| FW
```

## Nível 2 — Containers (as 8 camadas do grafo)

```mermaid
graph TB
    subgraph Kernel ["_core — Núcleo (134 nós-arquivo)"]
        Motores[Motores determinísticos<br/>issue_flow · lint_skills · outcomes<br/>memory_engine · lookup · self_test_suite · motor]
        Hooks[_core/hooks — adapter Claude Code<br/>PreToolUse guards · Stop merge · UserPrompt routing]
        Specs[Specs canônicas .md<br/>CONTEXT · RUNTIME-CONTRACT · DEV-WORKFLOW · SECURITY]
    end
    subgraph Shared ["_shared — Bibliotecas (86)"]
        Clients[Clients de API<br/>linear · llm · stripe · evo · supabase · deploy_log]
        Secrets[secrets.py — adapter 1P<br/>env → op.env → op CLI]
        Tests[tests/ — 19 tested_by edges]
    end
    subgraph Adapters ["adapters/ (16)"]
        Codex[codex + opencode<br/>mesmo Runtime Contract, shims por harness]
    end
    subgraph Squads ["times/ — Squads"]
        Manuais[Manuais CLAUDE.md (53)<br/>personas + regras por área]
        Workers[Workers (40)<br/>observabilidade · CS · comercial · fiscal<br/>cron/systemd nas VPS]
    end
    subgraph Empacote ["cs-workers-boilerplate (25)"]
        Boiler[Docker + supercronic<br/>espelho de _shared pra Coolify]
    end
    subgraph Apps ["Apps isoladas"]
        Remotion[remotion-editor (56)<br/>React/Remotion → MP4]
    end

    Hooks -->|implementam C1-C8 de| Specs
    Codex -->|porta o mesmo contrato de| Specs
    Motores -->|consomem| Clients
    Workers -->|importam| Clients
    Workers -->|secrets sempre via| Secrets
    Manuais -->|documentam/configuram| Workers
    Boiler -->|sync-from-pd-framework.sh copia| Shared
    Hooks -->|roteiam sessão pra| Manuais
```

## Como as camadas se integram (achado do grafo)

O acoplamento entre camadas é **fraco de propósito**: só 5 arestas de import cruzam camadas — a integração real acontece por **subprocess/CLI/filesystem** (op CLI, cadencia-cli, git, curl), não por import Python. Isso é o que permite o mesmo código rodar em Windows, VPS Master (só determinístico — `SECURITY.md §1`) e containers Coolify. Consequência prática: quebras de integração não aparecem em teste de import — por isso existem o health check content-aware e a `self_test_suite` (DEV-832/1159).

## Fluxos-chave (espinha do tour do grafo, 13 passos)

1. **Sessão**: `CLAUDE.md` raiz roteia → hook UserPrompt abre squad → PreToolUse cria `session/YYYY-MM-DD-HHMM` na 1ª escrita → Stop mergeia na main (C3-C6 do Runtime Contract).
2. **Issue**: `issue_flow.py start/step/close` com gates (review §6, e2e, git) → Linear é espelho, nunca `save_issue` direto pra Done.
3. **Observabilidade**: falha → watchdog/health check → issue `own:agente` → autofix worker (Dev) → PR → humano mergeia. Validado e2e em 04/07 (DEV-1174).
4. **Secrets**: qualquer worker → `_shared/secrets.get()` → env → `op.env` → op CLI (SA 1Password). Nunca token em arquivo commitado.

## Onde mexer pra cada coisa

| Quero... | Camada / path |
|---|---|
| Novo guard de runtime | `_core/hooks/pretooluse-*.py` (+ espelho em `adapters/*/`) |
| Novo motor de fluxo | `_core/*.py` com `--self-test` (entra automático na `self_test_suite`) |
| Novo client de API | `_shared/<serviço>_client.py` + entrada no `SECRETS-1P-MAP.json` |
| Novo worker de squad | `times/<squad>/workers/` + cron guardado + registrar no `jobs.json` do health check |
| Worker containerizado CS | `cs-workers-boilerplate/` (sync copia `_shared`) |
| Composição de vídeo | `times/marketing/remotion-editor/src/compositions/` |

## Explorar interativamente

`/understand-dashboard` abre o grafo navegável; `/understand-chat "<pergunta>"` responde sobre dependências/gotchas; `/understand-diff HEAD~N..HEAD` mostra impacto de mudanças nas camadas.


## Componentes documentados (04/07 — grafo)
- [[_core]] → `_core/README.md` (kernel: motores + hooks + specs)
- [[_shared]] → `_shared/README.md` (clients de API + secrets)
- adapters → `adapters/README.md` (Runtime Contract em Codex/OpenCode)
- remotion-editor → `times/marketing/remotion-editor/README.md`

## Notas Relacionadas
[[Projetos/Central de Observabilidade/Docs/self-test-suite]] · [[Projetos/Central de Observabilidade/Docs/deploy-log-e-deploy-watcher]]
