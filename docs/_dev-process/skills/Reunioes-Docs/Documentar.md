---
date: 2026-05-14
tags: [skill, documentacao, obsidian, wiki, repo, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Documentar

Gera ou atualiza documentação completa de projeto no cadencia-docs (fonte de verdade cross-time, MkDocs Material) + espelho para os agentes no repo do projeto.

## Quando usar
"/documentar-software", "documenta o projeto", "gera doc", "playbook do projeto", "atualiza a documentação", "documenta o que fiz nessa sessão", "documenta o cadencia".

---

## Conteúdo da Skill

```markdown
---
name: documentar
description: >
  Gera ou atualiza documentação completa de um projeto no cadencia-docs
  (fonte de verdade cross-time, MkDocs Material publicado em docs.cadencia.ia.br)
  + espelho para os agentes no repo do projeto (CLAUDE.md + docs/).
---

# /documentar-software — Documentação Completa de Projeto/Feature/Componente

Gera ou atualiza documentação técnica de software em **3 destinos sincronizados** a partir da mesma fonte de verdade (código + interação com Felipe):

| Destino | Pra quem | Formato |
|---|---|---|
| cadencia-docs (fonte de verdade cross-time, MkDocs Material) | Felipe + time + agentes navegando doc | Markdown com navegação, busca, dark mode |
| MDs no repo (`src/<componente>/README.md`, `CONTEXT.md`, `docs/adr/`) | Agentes IA + dev navegando código | Markdown denso, paths absolutos |

**Princípios não-negociáveis:**

1. **Aderente ao padrão do Felipe** — preserva formato `context-*.md` do `_bmad-output/`, respeita hub `Hub Projetos/Incidentes/`.
2. **Defensiva** — confirma antes de qualquer ação destrutiva. Preserva trabalho manual em seções editadas à mão.
3. **Idempotente** — rodar 2x não duplica nada. Detecta estado anterior via `docs/.documentar-meta.json`.
4. **Honesta** — quando faltar info pra preencher seção, pergunta. Não inventa decisões arquiteturais.
5. **Não invoca outras skills automaticamente** — `/log-sessao`, `/registrar-incidente`, `/handoff-sessao` só são SUGERIDAS no fim, nunca chamadas sem autorização.

---

## Fluxo principal — 10 fases

### Fase 1 · Descoberta inicial

Ler em paralelo:
1. **Estrutura do projeto** — `Get-ChildItem` no cwd, identificar tipo: Monorepo, Frontend, Backend, etc.
2. **Doc existente** — verificar se `docs/.documentar-meta.json` existe.
3. **BMAD presente?** — checar `_bmad/`, `_bmad-output/`, `.bmad-core/`.
4. **Padrões existentes** — ler `README.md`, `CLAUDE.md`, `CONTEXT.md`, `docs/`.
5. **Hub de Incidentes** — verificar `C:\Users\felip\OneDrive\Documentos\ClaudeCode\Hub Projetos\Incidentes\INDEX.md`.

### Fase 2 · Decisão de escopo (interativa)

Apresentar ao Felipe 3 modos:

```
[1] 🌍 Projeto inteiro — Documenta TODOS os componentes.
[2] 🎯 Sessão vigente — Só o que foi mexido nesta conversa / git status / últimos commits.
[3] 🔬 Feature ou componente isolado — Você especifica o escopo (path ou nome).

Modo dry-run? [s/N]
  Se SIM: gera tudo em C:\tmp\documentar-<projeto>-<ts>\ pra revisar antes de aplicar.
```

### Fase 3 · Decisão sobre doc existente (se aplicável)

Se `docs/.documentar-meta.json` existe:

```
[1] 🔄 Atualizar (recomendado)
[2] ➕ Adicionar componentes novos
[3] 🆕 Regenerar do zero
[4] 🔍 Auditar (dry-run)
```

### Fase 4 · Detecção de BMAD (sub-fluxo opcional)

Se `_bmad/` existir: perguntar se quer rodar `bmad-document-project` primeiro ou usar formato Felipe direto.

### Fase 5 · Detecção de componentes

Heurísticas em ordem de prioridade:
1. Monorepo declarado → cada subpasta de `apps/`, `services/`, `packages/` é componente
2. Sub-projetos físicos → subpastas com `package.json`/`pyproject.toml` próprio na raiz
3. Estrutura `src/` → subdiretórios top-level de `src/` viram componentes

Filtros automáticos (NUNCA viram componente): `node_modules/`, `.next/`, `dist/`, `build/`, `.git/`, `__pycache__/`.

### Fase 6 · Geração MD por componente

Pra cada componente: ler código, aplicar template COMPONENTE.md, preencher seções obrigatórias (TL;DR, Identidade, O que é, Pra que serve, Como funciona, Quickstart).

### Fase 7 · Geração de docs globais

Arquivos da raiz do repo:
1. **`README.md`** — Pitch em 30s + Stack + Estrutura + Status + Conceitos-Chave
2. **`CONTEXT.md`** — Termos do domínio com definição tight
3. **`docs/architecture.md`** — Diagrama C4 (Context + Container) em mermaid
4. **`docs/adr/NNNN-*.md`** — Formato MP minimalista (1-3 frases)
5. **`CHANGELOG.md`** — Append (não sobrescreve)

### Fase 8 · Geração HTML wiki

Em `docs/wiki/`: `index.html`, `<componente>.html`, `architecture.html`, `style.css`, `script.js` (busca client-side).

**Assets obrigatórios** (sem isso os HTMLs quebram):
```powershell
$wikiSrc = "C:\Users\felip\.claude\skills\documentar\wiki-template"
$wikiDest = "docs/wiki"
Copy-Item "$wikiSrc\style.css" "$wikiDest\style.css" -Force
Copy-Item "$wikiSrc\script.js" "$wikiDest\script.js" -Force
```

**Conversão MD → HTML:** usar Python com a lib `markdown` (`pip install markdown`).

### Fase 9 · Obsidian — Vault Time PD (`Projetos/[nome]/Docs/`)

Pra cada componente documentado, criar/atualizar nota com frontmatter + wikilinks:

```markdown
---
date: YYYY-MM-DD
tags: [doc, componente, nome-projeto]
---

## Identidade
- **Tipo:** [frontend / backend / worker / lib / infra]
- **Stack:** [Next.js / FastAPI / Python / etc]
- **Path no repo:** `src/[componente]/`

## O que é
...

## Para que serve
...

## Como funciona
...

## Quickstart
```bash
[comandos mínimos pra rodar/testar]
```

## Decisões (ADRs)
- [[docs/adr/NNNN-decisao]] — resumo em 1 linha

## Don'ts
- [Nunca fazer X porque Y]

## Histórico
- YYYY-MM-DD — [o que mudou] (commit hash)

## Notas Relacionadas
[[Projetos/[Projeto]/Docs/outro-componente]]
```

### Fase 10 · Validação + Finalização

**REGRA ABSOLUTA: nunca declarar "concluído" sem ter testado.** Reportar status real:

```
📚 Documentação — Relatório de execução

✅ Feito e validado:
  - [N] MDs por componente gerados
  - docs/wiki/index.html + N páginas HTML
  - N páginas Obsidian validadas via CLI

⚠️ Feito mas com avisos:
  - [warning 1]

❌ Falhou ou não foi possível:
  - [falha 1]

📋 Próximas ações pra você:
  - [ ] Revisar commit antes de push
  - [ ] Validar visualmente: abrir docs/wiki/index.html no browser
```

---

## Pegadinhas Windows

- **Encoding UTF-8 SEM BOM obrigatório** em todos os Write.
- **PowerShell** vs **Bash**: usar PowerShell pra git/file ops, Bash pra heredocs e curl
- **Notion API + Python urllib** — usar `subprocess` + `curl` com User-Agent de browser real (Cloudflare bloqueia urllib default)

## Quando NÃO usar essa skill

- Fix pontual sem mudança arquitetural — overkill.
- Documentação de processo (não-técnica) — usar `/ata-reuniao`, etc.
- Geração de ADR isolada — escrever direto em `docs/adr/NNNN-*.md`.
```

## Notas Relacionadas
[[Reunioes-Docs/Ata Reuniao]] · [[Stamper-Operacionais/Registrar Notas]] · [[Stamper-Operacionais/Registrar Incidente]]
