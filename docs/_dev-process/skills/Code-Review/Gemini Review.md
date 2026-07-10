---
date: 2026-05-14
tags: [skill, code, review, gemini, google, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Gemini Review

Code review via Gemini CLI (Google) na branch atual. Custo $0 via OAuth. Chunking obrigatório para diffs maiores que 30KB.

## Quando usar
"/gemini-review", "roda gemini review", "review com gemini", "pede pro gemini revisar", "gemini review nos últimos commits".

---

## Conteúdo da Skill

```markdown
---
name: gemini-review
description: >
  Roda code review via Gemini CLI (Google) na branch atual, processa o output e classifica
  achados em P1/P2/P3 por categoria (lógica, sintaxe, estilo, segurança).
  Ativar quando Felipe disser "/gemini-review", "roda gemini review", "review com gemini",
  "pede pro gemini revisar", "gemini review nos últimos commits".
---

# /gemini-review — Code Review via Gemini CLI + Classificação Estruturada

Executa o Gemini CLI do Google para revisar os commits recentes da branch atual, depois processa e classifica o output em categorias e prioridades.

## Comandos

- `/gemini-review` — revisa os últimos 3 commits da branch atual
- `/gemini-review 5` — revisa os últimos N commits
- `/gemini-review abc1234` — revisa um commit específico
- `/gemini-review abc1234..def5678` — revisa range de commits

## Pré-requisitos

1. **Gemini CLI instalado**: `npm install -g @google/gemini-cli`
2. **Autenticado via OAuth**: `gemini` (primeira execução autentica)
3. Estar dentro de um repositório git

## Comando base

```bash
# Opção 1: Diff via pipe (preferida para diffs grandes)
git diff HEAD~3..HEAD | gemini -m gemini-2.5-flash -p "$(cat <<'PROMPT'
Você é um code reviewer sênior especializado em [STACK_DETECTADA].

Revise o diff abaixo com foco em:
1. SEGURANÇA: auth bypass, injection, XSS, CSRF, RLS, exposure de dados
2. LÓGICA: fluxos quebrados, edge cases, null checks, race conditions
3. SINTAXE: erros de tipo, imports errados, tipagem incorreta
4. PERFORMANCE: queries N+1, renders desnecessários, bundles grandes
5. DEAD_CODE: imports, variáveis, funções não usadas
6. ESTILO: naming inconsistente, patterns quebrados

Para cada achado, responda EXATAMENTE neste formato:

**[CATEGORIA] Título curto**
- Arquivo: path/to/file:linha
- Severidade: P1 (crítico) | P2 (importante) | P3 (sugestão)
- Problema: descrição clara
- Fix sugerido: código ou instrução

Contexto dos commits: [COMMIT_LOG]

Diff para revisar:
PROMPT
)"

# Opção 2: Para diffs pequenos, inline no prompt
gemini -m gemini-2.5-flash -p "Revise este diff: $(git diff HEAD~3..HEAD)"
```

## Regras de execução

- **Modelo padrão: `gemini-2.5-flash`** — disponível no tier gratuito OAuth, 1M contexto
- **SEMPRE usar modo headless** (`-p` flag) — nunca modo interativo
- **Timeout**: 5 minutos máximo

## Limites do diff e chunking — OBRIGATÓRIO

O tier gratuito tem **250K tokens/minuto**. Um diff grande pode estourar isso.

**SEMPRE aplicar chunking:**

1. Verificar tamanho do diff: `git diff HEAD~N..HEAD | wc -c`
2. **Se < 30KB** (~10K tokens): enviar tudo em uma chamada
3. **Se 30KB-100KB**: dividir por arquivo, agrupar até ~30KB por chamada
4. **Se > 100KB**: dividir por arquivo individual, enviar um por vez com 5s de delay entre chamadas

```bash
# Passo 1: Listar arquivos modificados
git diff --name-only HEAD~N..HEAD

# Passo 2: Para cada grupo de arquivos (~30KB)
git diff HEAD~N..HEAD -- arquivo1.ts arquivo2.ts | gemini -m gemini-2.5-flash -p "<prompt>"
```

**Rate limit safety**: máximo 5 chamadas por minuto. Se tiver mais grupos, inserir `sleep 15` entre batches.

## Classificação de prioridade

### P1 — Crítico (corrigir ANTES de deploy)
- Bugs que quebram funcionalidade em produção
- Vulnerabilidades de segurança
- Race conditions que causam perda de dados
- Regressões que quebram fluxos existentes

### P2 — Importante (corrigir nesta sessão)
- Dead code que polui o codebase
- Error handling ausente em paths críticos
- Tipagem incorreta em interfaces públicas

### P3 — Sugestão (backlog)
- Melhorias de estilo e legibilidade
- Refatorações opcionais
- Convenções de naming

**REGRA ABSOLUTA — ACENTUAÇÃO:**
Todo texto gerado DEVE usar acentuação correta do português brasileiro.

## Comparação com as outras skills de review

| Aspecto | /codex-review | /gemini-review |
|---------|--------------|----------------|
| Modelo | GPT-5.4 (OpenAI) | Gemini 2.5 Flash (Google) |
| Auth | API key (OPENAI_API_KEY) | OAuth pessoal (Google) |
| Custo | ~$0.40/review | $0 (conta pessoal) |
| CLI | `codex review --base` | `gemini -m ... -p` |

## Uso combinado recomendado

Para review completo de uma story/feature:
1. `/codex-review` — primeira passada (OpenAI)
2. `/gemini-review` — segunda passada (Google)
3. Claude classifica e consolida achados de ambos
```

## Notas Relacionadas
[[Code-Review/Claude Review]] · [[Code-Review/Codex Review]]
