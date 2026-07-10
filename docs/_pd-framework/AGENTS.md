# AGENTS.md — Schema do Vault Empresa (LLM Wiki Pattern)

> Constituição da wiki operacional da Cadencia. Lido por **qualquer agente** (Claude, OpenCode, futuros) que escreva neste vault. Runtime-agnóstico por design — não carrega nome de fornecedor de modelo.
>
> Origem: DEV-955 / DEV-961 (2026-06-29). Inspirado no "LLM Wiki Pattern" de Karpathy. Decisão registrada em `times/dev/memory/decisions.md`.

---

## Princípio

Este vault é uma **wiki operacional** — a memória conectada da empresa. Não é arquivo morto nem dump de markdown. Cada nota se liga às outras por relações modeladas, formando um graph navegável onde clicar numa entidade (cliente, projeto) revela tudo ligado a ela.

A divisão de trabalho:
- **Humano** (Felipe) — fornece as fontes, faz as boas perguntas, navega o graph no Obsidian.
- **Agente** — faz o *bookkeeping*: cria notas no padrão, mantém os cross-references, liga source→entity, roda o lint. O trabalho tedioso que apodrece toda base de conhecimento humana.

Analogia operacional: **Obsidian é a IDE; o agente é o programador; esta wiki é o codebase.**

---

## As 3 camadas (mapeadas sobre a estrutura existente)

Não criamos estrutura nova nem mexemos na existente. Designamos papéis às pastas que já existem.

| Camada | Pastas do vault | Papel |
|---|---|---|
| **entities** (hubs) | `Clientes/`, `Projetos/`, `Time/` (pessoas), squads | Nós centrais do graph. Cada um é uma nota-hub durável |
| **sources** (eventos) | `Sessoes/`, `Incidentes/`, `Reuniões/`, `Comercial/Propostas/` | Coisas que aconteceram numa data. Apontam pras entities |
| **concepts** (atemporal) | `Conceitos/` (glossário), `Decisões/`, `Cultura/`, `Processos/` | Conhecimento que não é evento nem entidade |

**Raw layer (fora do vault):** o `pd-framework` (`sessions-log/`, `decisions.md`, incidentes brutos, glossário-fonte) é a camada imutável. O vault é a wiki que sintetiza e conecta — nunca o contrário. **Nenhum agente edita o pd-framework a partir do vault.**

---

## A regra que forma o graph

> **Toda nota-`source` declara, no frontmatter, as entities que menciona.**

```yaml
entities: ["[[Juliana Pereira]]", "[[Cadencia]]"]
```

Wikilink **por nome** (name-based), não por path — resiliente a mover a nota e mais limpo no graph. O backlink que isso gera na nota-hub **é** o graph. Substitui o wikilink-por-busca-de-string (frágil — depende do título aparecer literal no corpo) por **link modelado e explícito**.

Se a entity referenciada ainda não existe, o agente **cria a nota-hub stub** na hora (ver workflow ingest).

### Estrutura física da entity (DEV-963)

Cada entity é uma **pasta com a nota-hub dentro**, mesmo nome:

```
Clientes/
  Juliana Pereira/
    Juliana Pereira.md      ← hub (type: entity)
    Contrato.pdf            ← materiais do cliente moram aqui
    materiais/
```

O hub usa o nome real (não `README`) pro graph mostrar o nome certo e o wikilink ser `[[Juliana Pereira]]`. Materiais do cliente/projeto ficam na mesma pasta.

### Índice vivo (Dataview)

Cada hub carrega um bloco Dataview que lista sozinho as sources ligadas — nunca desatualiza:

````
```dataview
TABLE source_kind AS Tipo, date AS Data
FROM ""
WHERE contains(entities, this.file.link)
SORT date DESC
```
````

---

## Frontmatter canônico por tipo

O frontmatter atual do vault (`date`/`tags`/`moc`) é **preservado**. Adicionamos `type` e, em sources, `entities`.

### entity (nota-hub)
```yaml
---
type: entity
entity_kind: cliente | pessoa | projeto | squad
status: ativo | inativo
aliases: ["Juliana", "Juliana Pereira"]   # resolve variações de nome
tags: [...]
moc: "[[MOC-Clientes]]"
---
```

### source (evento)
```yaml
---
type: source
source_kind: sessao | incidente | reuniao | proposta
date: YYYY-MM-DD
entities: ["[[Clientes/Juliana]]"]        # ← a regra que forma o graph
tags: [...]
moc: "[[MOC-Sessoes]]"
---
```

### concept (atemporal)
```yaml
---
type: concept
tags: [...]
moc: "[[MOC-Conhecimento]]"
---
```

**Convenções herdadas (não mudam):** tags ASCII minúsculo sem acento (~5 máx), `moc` entre aspas com wikilink sem path, formas canônicas normalizadas pelo `vault-organizer.py`.

---

## Os 3 workflows

### 1. Ingest (fonte nova → wiki)
Quando uma skill/agente cria uma nota neste vault:
1. Escreve a nota no tipo certo (`source` na maioria dos casos) com frontmatter completo.
2. Preenche `entities:` com as entidades mencionadas (resolve por `aliases`).
3. Para cada entity que **não existe ainda**: cria a nota-hub stub (`type: entity`, status, aliases).
4. Não reescreve o histórico — sources são append-only.

### 2. Query (perguntar à wiki)
Buscar pela wiki sintetizada — `entities:`, backlinks, MOCs — **não** pelos arquivos brutos do pd-framework. A wiki já tem as conexões prontas; os brutos não.

### 3. Lint (manutenção determinística)
Roda no cron diário (junto do `vault-organizer.py`, 18h). Estende `vault-audit.py`. Reporta:
- entity sem nenhum source apontando (hub órfão)
- source sem `entities:` (folha solta)
- alias duplicado entre entities (colisão de identidade)
- wikilink quebrado (`[[...]]` que não resolve)

Lint é **grep/comm determinístico** — não depende de raciocínio de LLM pra checar consistência.

---

## De onde vêm as entities

| entity_kind | Fonte de verdade | Pasta |
|---|---|---|
| cliente | CRM Cadencia (cadencia-cli) + `_core/linear-squad-map.json` | `Clientes/` |
| pessoa | `_core/PEOPLE.md` | `Time/` |
| projeto | Linear (projetos) + `_core/REPO-MAP.md` | `Projetos/` |
| squad | `pd-framework/times/*` | (pasta a definir em F2) |

---

## Escopo — o que entra e o que NÃO entra

**Entra (vira wiki):** entities (cliente, pessoa, projeto, squad), sources (sessão, incidente, reunião, proposta), concepts (decisões, glossário, cultura, processos).

**NÃO entra:**
- `STATE.md` / `MEMORY.md` vivos — working memory de agente; snapshot velho + colisão de nomes
- código (`skills/`, `workers/`, `_shared/`, `CLAUDE.md` de squad)
- credenciais, `queue/`, logs de máquina

---

## Para o organizer e as skills

- `vault-organizer.py` continua rodando igual — só **soma** a leitura de `type`/`entities`, não substitui a classificação por pasta.
- Skills que escrevem no vault devem seguir este schema (ver auditoria em DEV-961). O alinhamento é feito em F4 (DEV-965).
- Este arquivo vive em `Setup/` porque o organizer **ignora** essa pasta (`IGNORE_DIRS`) — não vira nó no graph, não é classificado, mas é versionado e lido.
