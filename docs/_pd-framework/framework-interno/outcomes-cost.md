---
date: 2026-07-03
tags: [doc, componente, pd-framework, documentacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[PD Framework]]"]
---
# Outcomes & Cost Capture — sinal estruturado do Motor Autônomo

## Identidade
- **Tipo:** lib/CLI determinística (core do framework)
- **Stack:** Python 3.12, zero dependências externas
- **Path no repo:** `_core/outcomes.py` + `_core/cost_capture.py`
- **Issues:** DEV-1103 · DEV-1104 · DEV-1106 (projeto Motor Autônomo 24/7)
- **Status:** ativo

## O que é
A fundação de medição do PD Framework v2.0: cada tarefa relevante gera um **evento append-only** (`pd.outcome.v1`) em JSONL local (`.pd/outcomes/outcomes.jsonl`, fora do git) com tarefa, executor, harness/modelo, resultado, evidências e custo. É o "sinal de sucesso" que alimenta cost tracker, budget guard, MODEL-MAP e o futuro motor autônomo.

## Para que serve
- **Insight diretor do projeto:** aprendizado de agente é limitado pelo sinal de sucesso, não pelo mecanismo. Este componente É o sinal.
- Responder "quanto custou essa issue?" e "qual squad gasta mais?" com dados, não intuição.
- Base pro bandit de roteamento de modelos (D2) quando houver histórico.

## Como funciona
1. **Registro:** `append_outcome(...)` valida contra o contrato e appenda 1 linha JSON. Correção = evento novo (nunca reescreve).
2. **Captura de custo:** `cost_capture.py` lê passivamente o que cada harness já grava local — transcript JSONL do Claude Code, `token_count` do rollout do Codex, sqlite do OpenCode (único com custo real em USD; assinaturas ficam `amount: null`).
3. **Relatório:** `report` agrega por issue e squad — eventos, tokens, USD conhecido, intervenções humanas, status.

## Quickstart
```bash
python _core/outcomes.py --self-test
python _core/cost_capture.py probe --runtime claude-code
python _core/outcomes.py append --issue DEV-X --squad times/dev --title "..." --status success --summary "..." --auto-cost
python _core/outcomes.py report --squad times/dev --since 2026-07-01
```

## Decisões
- Schema versionado `pd.outcome.v1`; eventos fora do git (`.pd/` ignorado); contrato versionado em `_core/OUTCOMES.md`.
- **Pricing por modelo NÃO vive aqui** — `amount` só quando o runtime reporta; precificar assinatura é papel do MODEL-MAP (DEV-1113/1116).
- Leitura passiva dos artefatos do harness — sem hook novo, sem rede, tolerante (fonte ausente → `cost=null`, append nunca falha).

## Don'ts
- Nunca reescrever evento antigo (append-only).
- Nunca credencial/payload sensível/transcrição longa dentro do evento.
- `destructive_action=true` exige evidência de aprovação textual.

## Troubleshooting
- **`report` vazio** → eventos vivem em `.pd/outcomes/outcomes.jsonl` local por máquina; conferir `PD_OUTCOMES_LOG`.
- **opencode não captura** → directory no banco usa forward slashes (normalizado desde DEV-1104); sessões com 0 tokens são puladas.
- **probe claude-code pegou sessão errada** → pega o transcript mais recente do projeto; usar `--auto-cost-source <path>` quando precisão importa.

## Histórico
- 2026-07-03 — DEV-1103 schema+CLI (commit 48e4ced) · DEV-1104 cost capture 3 harnesses (8d753ba) · DEV-1106 report (26195da)

## Notas Relacionadas
[[adapter-codex]] · doc completa no repo: `_core/docs/outcomes.md` + `_core/docs/cost-capture.md` · contrato: `_core/OUTCOMES.md`
