---
date: 2026-05-14
tags: [skill, code, review, codex, openai, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Codex Review

Code review via OpenAI Codex CLI na branch atual. Classifica achados em P1/P2/P3 por categoria.

## Quando usar
"/codex-review", "roda codex review", "review com codex", "pede pro codex revisar", "codex review nos ultimos commits".

---

## Conteúdo da Skill

```markdown
---
name: codex-review
description: >
  Roda code review via OpenAI Codex CLI na branch atual, processa o output e classifica
  achados em P1/P2/P3 por categoria (logica, sintaxe, estilo, seguranca).
  Ativar quando Felipe disser "/codex-review", "roda codex review", "review com codex",
  "pede pro codex revisar", "codex review nos ultimos commits".
---

# /codex-review — Code Review via OpenAI Codex + Classificacao Estruturada

Executa o Codex CLI da OpenAI para revisar os commits recentes da branch atual, depois processa e classifica o output em categorias e prioridades.

## Comandos

- `/codex-review` — revisa os ultimos 3 commits da branch atual
- `/codex-review 5` — revisa os ultimos N commits
- `/codex-review abc1234` — revisa um commit especifico
- `/codex-review abc1234..def5678` — revisa range de commits

## Pre-requisitos

1. **Codex CLI instalado**: `npm install -g @openai/codex` (ou `npx @openai/codex`)
2. **OPENAI_API_KEY** configurada como env var
3. Estar dentro de um repositorio git

## Passo 1 — Detectar API key

```bash
# Ordem de busca:
# 1. Variavel de ambiente OPENAI_API_KEY (ja exportada)
# 2. .env.local no projeto atual
# 3. .env no projeto atual

OPENAI_API_KEY=$(grep -m1 '^OPENAI_API_KEY=' .env.local 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
```

## Passo 2 — Executar Codex CLI

O Codex CLI tem o subcomando `codex review` com estas flags:

```
codex review [OPTIONS] [PROMPT]

Opcoes principais:
  --commit <SHA>       Revisar um commit especifico (UMA VEZ SO — nao repete a flag)
  --base <BRANCH>      Revisar diff entre base e HEAD (ex: HEAD~3, main, etc.)
  --model <MODEL>      Modelo a usar
  --max-tokens <N>     Limite de tokens

REGRAS DE USO:
  - --commit e --base sao MUTUAMENTE EXCLUSIVOS
  - --commit aceita UM UNICO SHA (nao aceita multiplos --commit)
  - --base NAO aceita [PROMPT] junto (sao mutuamente exclusivos)
  - Para revisar N commits: usar --base HEAD~N (sem prompt)
  - Para revisar 1 commit: usar --commit <SHA> (sem prompt)
```

### Mapeamento de argumentos do usuario → comando codex

| Argumento do usuario | Comando |
|---------------------|---------|
| `/codex-review` (sem args) | `codex review --base HEAD~3` |
| `/codex-review 5` | `codex review --base HEAD~5` |
| `/codex-review abc1234` | `codex review --commit abc1234` |
| `/codex-review abc1234..def5678` | `codex review --base abc1234` (HEAD implicito) |

### Exemplo real

```bash
# Ultimos 3 commits (default)
OPENAI_API_KEY="$KEY" codex review --base HEAD~3

# Commit especifico
OPENAI_API_KEY="$KEY" codex review --commit f2d3c16

# Ultimos 5 commits
OPENAI_API_KEY="$KEY" codex review --base HEAD~5
```

**IMPORTANTE**:
- NUNCA usar --quiet (nao existe)
- NUNCA usar --approval-mode (nao existe no subcomando review)
- NUNCA combinar --commit com --base
- NUNCA passar --commit mais de uma vez
- NUNCA passar prompt junto com --base
- Timeout: 5 minutos maximo

## Passo 3 — Classificacao de prioridade

### P1 — Critico (corrigir ANTES de deploy)
- Bugs que quebram funcionalidade em producao
- Vulnerabilidades de seguranca (auth bypass, injection, RLS)
- Race conditions que causam perda de dados
- Regressoes que quebram fluxos existentes

### P2 — Importante (corrigir nesta sessao)
- Dead code que polui o codebase
- Error handling ausente em paths criticos
- Tipagem incorreta ou `any` em interfaces publicas

### P3 — Sugestao (backlog)
- Melhorias de estilo e legibilidade
- Refatoracoes opcionais
- Convencoes de naming

**REGRA ABSOLUTA — ACENTUAÇÃO:**
Todo texto gerado DEVE usar acentuação correta do português brasileiro.

## Passo 4 — Formato do relatorio

Salvar em `docs/codex-reviews/codex-review-DD-MM-YYYY.md`:

```markdown
# Codex Review — DD/MM/YYYY

## Resumo
- **Branch**: main
- **Commits revisados**: X (hash1..hashN)
- **Achados**: X P1 | Y P2 | Z P3
- **Arquivos analisados**: N

## P1 — Criticos

### [CATEGORIA] Titulo curto do achado
- **Arquivo**: path/to/file.ts:42
- **Commit**: abc1234
- **Problema**: descricao clara do bug/vulnerabilidade
- **Impacto**: o que acontece se nao corrigir
- **Fix sugerido**: codigo ou instrucao de correcao

---

## P2 — Importantes
...

## P3 — Sugestoes
...

## Output bruto do Codex

<details>
<summary>Clique para expandir</summary>
[OUTPUT COMPLETO DO CODEX AQUI]
</details>
```

## Passo 5 — Acao pos-review

Depois de apresentar o resumo, perguntar:

> **P1s encontrados: N**
> Quer que eu corrija os P1s automaticamente? (sim/não/ver detalhes)

Se Felipe disser sim:
1. Corrigir cada P1 sequencialmente
2. Rodar `npm run build` apos cada correcao
3. Apresentar diff pro Felipe aprovar antes de commit

## Fallback — Se Codex nao estiver disponivel

1. Avisar: "Codex CLI nao encontrado. Posso instalar com `npm install -g @openai/codex` ou rodar o review manualmente."
2. Oferecer alternativa: fazer o review usando o proprio Claude (sem Codex), seguindo a mesma estrutura de classificacao P1/P2/P3.
```

## Notas Relacionadas
[[Code-Review/Claude Review]] · [[Code-Review/Gemini Review]]
