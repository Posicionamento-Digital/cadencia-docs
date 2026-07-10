---
date: 2026-05-14
tags: [skill, code, review, claude-code, opus, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Claude Review

Code review via Claude Code CLI (Opus 4.7) na branch atual. Classifica achados em P1/P2/P3 por categoria.

## Quando usar
"/claude-review", "roda claude review", "review com opus", "pede pro opus revisar", "claude review nos últimos commits".

---

## Conteúdo da Skill

```markdown
---
name: claude-review
description: >
  Roda code review via Claude Code CLI (Anthropic) com Opus 4.7 na branch atual, processa o output
  e classifica achados em P1/P2/P3 por categoria (lógica, sintaxe, estilo, segurança).
  Ativar quando Felipe disser "/claude-review", "roda claude review", "review com claude",
  "review com opus", "pede pro opus revisar", "claude review nos últimos commits".
---

# /claude-review — Code Review via Claude Code CLI (Opus 4.7) + Classificação Estruturada

Executa uma instância separada do Claude Code CLI com Opus 4.7 em modo headless (-p) para revisar os commits recentes da branch atual, depois processa e classifica o output em categorias e prioridades.

## Comandos

- `/claude-review` — revisa os últimos 3 commits da branch atual
- `/claude-review 5` — revisa os últimos N commits
- `/claude-review abc1234` — revisa um commit específico
- `/claude-review abc1234..def5678` — revisa range de commits

## Pré-requisitos

1. **Claude Code CLI instalado**: `npm install -g @anthropic-ai/claude-code`
2. **Autenticado**: login ativo no Claude Code
3. Estar dentro de um repositório git

## Fluxo

```
Felipe invoca /claude-review [args]
    |
    v
1. Verificar Claude Code CLI disponível
2. Coletar diff dos commits alvo
3. Montar prompt de review e enviar ao Claude Code CLI
   - Modo headless: claude -p "<prompt>" --model opus
   - Diff passado inline no prompt ou via pipe
    |
    v
4. Capturar output completo do Opus 4.7
    |
    v
5. Processar output (instância atual do Claude)
   - Parsear todos os achados
   - Classificar cada achado em:
     * Prioridade: P1 (crítico), P2 (importante), P3 (sugestão)
     * Categoria: LÓGICA | SINTAXE | ESTILO | SEGURANÇA | PERFORMANCE | DEAD_CODE
    |
    v
6. Gerar relatório estruturado
   - Salvar em: docs/claude-reviews/claude-review-DD-MM-YYYY.md
    |
    v
7. Perguntar se quer corrigir os P1s automaticamente
```

## Comando base

```bash
# Opção 1: Diff via pipe (preferida para diffs grandes)
git diff HEAD~3..HEAD | claude -p "$(cat <<'PROMPT'
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

NÃO use ferramentas, NÃO edite arquivos, NÃO rode comandos.
PROMPT
)" --model opus --max-turns 1
```

## Classificação de prioridade

### P1 — Crítico (corrigir ANTES de deploy)
- Bugs que quebram funcionalidade em produção
- Vulnerabilidades de segurança (auth bypass, injection, RLS)
- Race conditions que causam perda de dados
- Regressões que quebram fluxos existentes

### P2 — Importante (corrigir nesta sessão)
- Dead code que polui o codebase
- Error handling ausente em paths críticos
- Tipagem incorreta ou `any` em interfaces públicas

### P3 — Sugestão (backlog)
- Melhorias de estilo e legibilidade
- Refatorações opcionais
- Convenções de naming

## Formato do relatório

Salvar em `docs/claude-reviews/claude-review-DD-MM-YYYY.md`:

```markdown
# Claude Review — DD/MM/YYYY

## Resumo
- **Branch**: main
- **Commits revisados**: X (hash1..hashN)
- **Modelo**: claude-opus-4-7 (via Claude Code CLI)
- **Achados**: X P1 | Y P2 | Z P3

## P1 — Críticos
### [CATEGORIA] Título curto do achado
- **Arquivo**: path/to/file.ts:42
- **Problema**: descrição clara do bug/vulnerabilidade
- **Fix sugerido**: código ou instrução de correção

## P2 — Importantes
...

## P3 — Sugestões
...
```

## Comparação com as outras skills de review

| Aspecto | /codex-review | /gemini-review | /claude-review |
|---------|--------------|----------------|----------------|
| Modelo | GPT-5.4 (OpenAI) | Gemini 3.1 Pro (Google) | Opus 4.7 (Anthropic) |
| Auth | API key | OAuth pessoal | Claude Code login |
| Custo/review | ~$0.40 | $0 | $0 (assinatura) |
| SWE-bench Pro | 58.6% | #3 global | 64.3% (#1) |

## Pipeline de review triplo recomendado

Para review máximo de uma story/feature crítica:
1. `/gemini-review` — Gemini 3.1 Pro (Google) — $0
2. `/codex-review` — GPT-5.4 (OpenAI) — ~$0.40
3. `/claude-review` — Opus 4.7 (Anthropic) — ~$1.00

**Custo total do pipeline triplo: ~$1.40 por review.**
```

## Notas Relacionadas
[[Code-Review/Gemini Review]] · [[Code-Review/Codex Review]] · [[Stamper-Operacionais/Registrar Incidente]]
