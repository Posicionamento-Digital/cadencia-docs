---
date: 2026-07-04
tags: [doc, documentacao, projeto, observabilidade]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Central de Observabilidade]]"]
---
# self_test_suite — self-testing diário do framework (DEV-1159)

## TL;DR
Agregador determinístico que roda os `--self-test` de todos os motores do repo + `run_smoke` do adapter Codex, compara com baseline monotônica e responde "houve REGRESSÃO?". Roda como cron diário na Master; falha entra no loop de auto-correção da Central **sem código novo de Linear**.

## Identidade
- **Tipo:** motor `_core/` (Python stdlib) + cron Master
- **Path:** `_core/self_test_suite.py`
- **Cron:** `30 7 * * *` UTC em `/opt/pd-framework/`
- **Baseline:** `.pd/self-test-baseline.json` (padrão do `stop-skills-lint`)
- **Marcador:** `~/.self-test/last_ok.txt` — tocado **só em rodada sem regressão**
- **Vigiado por:** health check no MARCADOR (não no log)

## Registry (15 alvos)
13 motores `--self-test` (issue_flow, lint_skills, outcomes, model_map, memory_engine, session_recorder, linear_claims, cost_capture, new_skill, 3 guards PreToolUse, check_skills_junction[win]) + `adapters/codex/run_smoke.py` (determinístico — shims via subprocess) + pytest do cadencia-cli (win, skip-if-absent).

## Arquitetura de detecção (lição dos incidentes de 26-27/06)
**Mtime de log não é sinal de vida** — cron quebrado que grava erro no log mantém o mtime fresco e engana vigia. Por isso o health check vigia o **marcador de sucesso**: qualquer falha (do cron OU dos testes) envelhece o marcador → watchdog abre issue `own:agente` → autofix. Content-aware por construção.

## Baseline monotônica
- Falha **conhecida** (na baseline) não é regressão — rodada segue "limpa".
- Teste recuperado **sai** da baseline automaticamente (melhora trava).
- Falha **nova** = exit 2 + marcador não atualiza + delta no `#saude-sistemas`.
- `--accept-failures` adiciona falhas atuais à baseline — **só por ação humana**.

## Quickstart
```bash
python _core/self_test_suite.py              # painel humano
python _core/self_test_suite.py --json       # estruturado
python _core/self_test_suite.py --self-test  # dogfood da mecânica de baseline
```

## Quando NÃO confiar nela
Self-test in-process tem ponto cego de **integração real** (os 4 bugs da DEV-1155 passavam todos) — a camada 2 (e2e com CLI real de agente, fora da Master) é trabalho separado, não coberto por esta suíte.

## Histórico
- 2026-07-04 — criado (DEV-1159); 14/15 verdes na 1ª rodada real (1 skip esperado)


## Notas Relacionadas
[[deploy-log-e-deploy-watcher]]
