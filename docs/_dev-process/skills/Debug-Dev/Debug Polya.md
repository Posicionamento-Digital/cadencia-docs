---
date: 2026-05-14
tags: [skill, debug, polya, metodologia, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Debug Polya

Framework estruturado de debugging baseado nos 4 pilares de Pólya (How to Solve It): Compreensão → Plano → Execução → Retrospecto. Força raciocínio metodológico antes de mexer em código.

## Quando usar
"/debug-polya", "debugar isso", "por que tá quebrando", "investiga esse bug", "o que tá causando isso", "não tá funcionando", "analisa esse erro".

---

## Conteúdo da Skill

```markdown
---
name: debug-polya
description: Framework estruturado de debugging baseado nos 4 pilares de Pólya (How to Solve It). Ativar quando Felipe disser "/debug-polya", "debugar isso", "por que tá quebrando", "investiga esse bug", "o que tá causando isso", "não tá funcionando", "analisa esse erro". Força o agente a pensar metodicamente antes de sair mexendo em código.
---

# Debug Pólya — Resolução Estruturada de Bugs

Framework de debugging em 4 fases obrigatórias. Baseado em "How to Solve It" (George Pólya), adaptado para debugging de software.

**REGRA ABSOLUTA:** Nunca pular direto pra "tentar corrigir". O agente DEVE completar a compreensão antes de agir.

---

## Fluxo Principal

### Passo 0 — TRIAGEM AUTOMÁTICA

Ao receber o relato do problema, o agente DEVE:

1. Executar a Fase 1 (Compreensão) internamente
2. Com base na compreensão, **recomendar a severidade** ao Felipe:

```
🎯 TRIAGEM

[Resumo do problema em 1-2 linhas]

Severidade recomendada: [TRIVIAL / MÉDIO / CRÍTICO]
Justificativa: [por que essa classificação]

→ TRIVIAL: rodo as 4 fases em bloco único, resolvo direto
→ MÉDIO: mostro compreensão + hipóteses, você valida, depois resolvo
→ CRÍTICO: paro em cada fase pra você validar antes de eu avançar

Quer seguir com [recomendação] ou prefere outro modo?
```

3. **Aguardar confirmação do Felipe** antes de prosseguir

### Critérios de classificação

| Severidade | Quando | Exemplos |
|---|---|---|
| TRIVIAL | Causa provável é óbvia, impacto baixo, reversível | typo, import errado, variável undefined, config faltando |
| MÉDIO | Múltiplas causas possíveis, ou impacto moderado | bug de lógica, integração quebrando, comportamento inesperado |
| CRÍTICO | Prod afetada, dados em risco, receita impactada, ou causa desconhecida | prod down, dados corrompidos, cron silenciosamente quebrado, regressão pós-deploy |

---

## Fase 1 — COMPREENSÃO DO PROBLEMA

```
🔍 FASE 1 — COMPREENSÃO
Esperado: [X]
Observado: [Y]
Erro: [mensagem exata]
Ambiente: [onde]
Desde: [quando / desconhecido]
Reproduz: [sempre / intermitente / condição]
Sistemas envolvidos: [lista]
Dados faltando: [o que preciso perguntar ao Felipe, se algo]
```

---

## Fase 2 — PLANO DE INVESTIGAÇÃO

**Consulta obrigatória a incidentes:** Antes de montar hipóteses, verificar `Hub Projetos/Incidentes/INDEX.md`.

```
🗺️ FASE 2 — PLANO DE INVESTIGAÇÃO

Incidentes relacionados: [nenhum / link pro incidente]

Hipóteses (ordem de probabilidade):
H1: [descrição] → Teste: [o que vou verificar]
H2: [descrição] → Teste: [o que vou verificar]
H3: [descrição] → Teste: [o que vou verificar]

Ordem de execução: H1 → H2 → H3
Restrição: não alterar código até confirmar causa raiz
```

---

## Fase 3 — EXECUÇÃO DO DIAGNÓSTICO

### Regras de execução
- **Um teste por vez.** Não rodar 5 coisas ao mesmo tempo.
- **Verificar cada passo.** "O resultado confirma ou descarta a hipótese?"
- **Registrar evidência.** Cada teste produz um resultado concreto.
- **Não corrigir durante diagnóstico.** Primeiro entender, depois corrigir.

### Anti-patterns proibidos
- ❌ Mudar código "pra ver se resolve" sem entender a causa
- ❌ Aplicar fix de Stack Overflow sem validar que o contexto é o mesmo
- ❌ Alterar múltiplas coisas ao mesmo tempo
- ❌ Ignorar a mensagem de erro e ir direto pro código
- ❌ Assumir que "deve ser X" sem evidência
- ❌ Teorizar sem ler logs primeiro

```
🔬 FASE 3 — DIAGNÓSTICO

Teste H1: [o que fiz] → Resultado: [confirmado/descartado]
  Evidência: [output/log/valor concreto]

Teste H2: [o que fiz] → Resultado: [confirmado/descartado]
  Evidência: [output/log/valor concreto]

✅ CAUSA RAIZ IDENTIFICADA:
[descrição precisa — arquivo:linha, fluxo, por que quebra]

Cadeia causal: [A] → [B] → [C] → [erro observado]
```

---

## Fase 4 — CORREÇÃO + RETROSPECTO

```
🔧 FASE 4 — CORREÇÃO + RETROSPECTO

Correção aplicada:
  Arquivo: [path:linha]
  Mudança: [descrição concisa]

Verificação:
  [ ] Comportamento esperado restaurado
  [ ] Sem regressão identificada
  [ ] Testado em [ambiente]

Retrospecto:
  Tempo gasto: [estimativa]
  Poderia ter sido mais rápido se: [insight]
  Reutilizável em: [outro lugar / não aplicável]
  Prevenção: [o que fazer pra não repetir]
  Registrar incidente: [sim/não — justificativa]
```

---

## Comportamento por modo

### TRIVIAL
- Fases 1→2→3→4 em bloco único, output condensado

### MÉDIO
- Fase 1 + Fase 2 → **PARA** → Felipe valida hipóteses
- Fase 3 + Fase 4 → apresenta resultado

### CRÍTICO
- Cada fase → **PARA** → Felipe valida antes de avançar
- `/registrar-incidente` obrigatório ao final

---

## Integração com outras skills

- Consultar incidentes: `Hub Projetos/Incidentes/INDEX.md` (obrigatório na Fase 2)
- Registrar incidente: `/registrar-incidente` (quando aplicável na Fase 4)
- Log da sessão: `/log-sessao` (se o debug foi significativo)
```

## Notas Relacionadas
[[Debug-Dev/Mp Diagnose]] · [[Stamper-Operacionais/Registrar Incidente]] · [[Code-Review/Claude Review]]
