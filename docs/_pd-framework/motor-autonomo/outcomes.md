---
date: 2026-07-03
tags: [docs, projeto, feature, documentacao]
moc: "[[MOC-Projetos]]"
squad: times/dev
type: source
entities: ["[[PD Framework - Motor Autonomo 247]]", "[[PD Framework]]"]
---
# Outcomes — Playbook

**Projeto:** PD Framework - Motor Autonomo 247
**Squad:** `times/dev`
**Repo:** `pd-framework`
**Branch merged:** pendente; story DEV-1103 em branch de sessao
**Issues:** DEV-1103

## O que essa feature entrega

Cria o primeiro contrato estruturado de outcome por tarefa do PD Framework v2.0. A partir dele, o framework passa a ter um formato unico para registrar resultado, executor, harness/modelo, custo quando conhecido, evidencias e intervencao humana.

Esse sinal e a base para as proximas stories: cost tracker, budget guard, report por issue/squad, model-map com aprendizado futuro e motor autonomo.

## Como usar

1. Rodar `python _core/outcomes.py --self-test` para validar o componente.
2. Registrar outcome simples com `python _core/outcomes.py append --issue DEV-1103 --squad times/dev --title "..." --status success --summary "..."`.
3. Conferir os ultimos eventos com `python _core/outcomes.py tail --limit 5`.
4. Usar `.pd/outcomes/outcomes.jsonl` como log local; nao commitar esse arquivo.

## Como manter

O contrato humano vive em `_core/OUTCOMES.md`. O helper fica em `_core/outcomes.py`. Alteracoes de compatibilidade precisam preservar `pd.outcome.v1` ou criar nova versao explicita.

DEV-1104 deve preencher o campo `cost`; DEV-1105 deve consumir esse sinal para budget guard.

## Decisoes importantes

- Evento append-only em JSONL local.
- Schema versionado `pd.outcome.v1`.
- `.pd/` ignorado no git.
- Sem dependencia externa de validacao.

## Refs tecnicas

- Docs componentes: `_core/docs/outcomes.md`
- cadencia-docs (fonte de verdade): `docs/_pd-framework/motor-autonomo/outcomes.md`
- Contrato: `_core/OUTCOMES.md`
- Runtime review: `times/dev/context/review-DEV-1103-runtime.md`
- Decisions Squad: `times/dev/memory/decisions.md`
