# Cadencia Docs

Documentação técnica central da Cadencia — produtos, infra, processo e framework.

**Site:** [posicionamento-digital.github.io/cadencia-docs](https://posicionamento-digital.github.io/cadencia-docs)

---

## Como navegar

Use a **barra lateral esquerda** para navegar entre seções. As abas no topo agrupam por área.

**Busca:** clique no ícone de lupa (ou pressione `/`) para buscar qualquer termo em todos os 339 documentos.

---

## O que tem aqui

### Produtos

| Seção | O que é |
|---|---|
| [Cadencia App](cadencia-app/README.md) | Arquitetura, workers, growth, motor gráfico, CLI/MCP, PRD, ADRs |
| [Cadencia App — Foundation](cadencia-app/foundation/README.md) | Product Vision, Tech Architecture, Multi-tenant Strategy, sub-squads |
| [Cadencia Growth](cadencia-growth/README.md) | Pipeline de growth, crons, mission control, scoring, scripts |
| [Cadencia App — Roadmap](cadencia-app/roadmap-features/Brief.md) | Features em planejamento (chat-ideia, tenant-agência, etc.) |
| [PD Portal](pd-portal/README.md) | Portal de clientes — overview, infra, skills |
| [Ecuro MCP](ecuro-mcp/README.md) | Ecuro — middleware MCP |
| [GCI-GO](gci-go/README.md) | Lara + confirmação de agenda |
| [Pipeline Conteúdo](pipeline-conteudo/README.md) | Pipeline de cortes e publicação |

### Sistemas internos

| Seção | O que é |
|---|---|
| [Central CS Onboarding](central-cs-onboarding/00-Visao-Geral.md) | Sistema autônomo de onboarding de clientes — receiver, consumer, workers |
| [Central de Observabilidade](central-observabilidade/README.md) | Audit cross-tenant, gate de triagem, deploy watcher, self-test |

### Infra

| Seção | O que é |
|---|---|
| [Infra — Visão Geral](_infra/README.md) | Topologia VPS, observabilidade, stack de monitoramento |
| [VPS Master](_infra/vps-master/VPS-Master-Arquitetura.md) | Arquitetura, serviços, Coolify, segurança, acesso |
| [VPS Dev](_infra/vps-dev/VPS-Dev-Documentacao-Tecnica.md) | Manual, POP de uso, playbook de provisionamento |
| [Recovery Hertzner](_infra/recovery-hertzner/00-indice.md) | Plano de disaster recovery — banco, código, N8N, infra |
| [Cloudflare](_infra/cloudflare/README.md) | DNS, proxy, configuração |

### PD Framework

| Seção | O que é |
|---|---|
| [Como Funciona](_pd-framework/PD%20Framework%20—%20Como%20funciona%20(consolidado%202026-05-25).md) | Visão consolidada do framework multi-agente |
| [Motor Autônomo 24/7](_pd-framework/motor-autonomo/motor-autonomo.md) | Loop, supervisor, auto-enqueue, outcomes |
| [Framework Interno](_pd-framework/framework-interno/README.md) | Knowledge graph, memory engine, session recorder, model map |
| [Squads](_pd-framework/squads/dev.md) | Perfis dos squads Dev / Infra / Produto |
| [Decisões](_pd-framework/decisoes/dev-memory.md) | Memória de decisões por squad e persona |
| [AI Founder Mode](_pd-framework/AI-Founder-Mode.md) | Framework de liderança na era da IA |

### Dev Process

| Seção | O que é |
|---|---|
| [Como Trabalhamos](_dev-process/Como-Trabalhamos.md) | Rituais, ferramentas, comunicação |
| [Processo de Desenvolvimento](_dev-process/Processo%20-%20Desenvolvimento%20(Time%20Dev).md) | Git flow, Linear, review, merge |
| [Incidentes](_dev-process/incidentes/) | 16 postmortems — bugs reais, root cause, fix |
| [Gotchas](_dev-process/gotchas/dev.md) | Pegadinhas conhecidas do stack |
| [Skills Dev](_dev-process/skills/Debug-Dev/Mp%20Diagnose.md) | Code review, debug, Matt Pocock, Spec-Kit, Linear |

### Onboarding & IA

| Seção | O que é |
|---|---|
| [Onboarding Dev](_onboarding/Onboarding-Dev.md) | Setup completo para novo dev |
| [Engenharia de Prompts](_onboarding/ia/Engenharia-de-Prompts-Manual-Completo.md) | Manual completo de prompts |
| [Harness IA](_onboarding/harness/Passo%20a%20Passo%20Montar%20Harness.md) | O que é um harness, como montar, por que é urgente |

---

## Como contribuir

Todo conteúdo fica em `docs/`. Edite direto na `main` ou via PR — o GitHub Actions rebuilda e publica automaticamente em ~40s.

```
docs/
  cadencia-app/        # App principal
  cadencia-growth/     # Pipeline de growth
  central-cs-onboarding/
  central-observabilidade/
  _infra/              # VPS, Cloudflare, N8N
  _pd-framework/       # Framework, Motor, Squads
  _dev-process/        # Processo, incidentes, skills
  _onboarding/         # IA, harness, setup
  pd-portal/
  ecuro-mcp/
  gci-go/
  pipeline-conteudo/
```

Fonte canônica das docs: **Obsidian vault Empresa** (`C:\Users\felip\Obsidian_Vaults_Empresa\`). Ao criar nova doc no Obsidian, copiar para o path correspondente aqui e commitar.
