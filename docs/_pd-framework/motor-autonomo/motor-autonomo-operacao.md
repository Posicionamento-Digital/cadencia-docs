---
date: 2026-07-06
tags: [documentacao, projeto, feature]
moc: "[[MOC-Projetos]]"
squad: times/dev
type: source
entities: ["[[PD Framework]]"]
---
# Motor Autonomo 24/7 — Playbook

**Projeto:** PD Framework - Motor Autonomo 247
**Squad:** `times/dev`
**Repo:** `C:/dev/pd-framework`
**Branch merged:** melhorias parciais em `main` em 2026-07-06; auto-enqueue em PR 27 aguardando alçada
**Issues:** DEV-1132, DEV-1134, DEV-1135, DEV-1136, DEV-1137, DEV-1182, DEV-1191

## O que essa feature entrega

O Motor Autonomo pega issues `own:agente` no Linear, trabalha em ciclos serializados, abre PR ou libera a issue, e respeita a matriz de alçada. A operacao agora separa claramente kill switch e daemon local: `start` liga os dois; `on` so muda permissao. O loop tolera falhas transientes de Linear/Git e continua pegando proximas issues quando ha fila.

A melhoria DEV-1191 reduz o trabalho manual de etiquetar issue por issue. O auto-enqueue conservador lista candidatos seguros e aplica `own:agente` com comentario de auditoria. Como toca `_core/motor_select.py`, ainda aguarda aprovacao CTO no PR 27.

## Como usar

1. Ver fila atual: `python _core/motor_select.py queue`.
2. Ligar para trabalho continuo: `python _core/motor.py start --reason "<motivo>"`.
3. Acompanhar: `python _core/motor.py status --fresh` e `.pd/motor-loop.out.log`.
4. Se a fila ficar vazia, usar o auto-enqueue do PR 27 quando aprovado: `candidates --profile safe` e depois `enqueue --profile safe --limit N`.
5. PRs criticos ou de framework aguardam aprovacao humana; o motor segue para outra issue.
6. Para parar: `python _core/motor.py off --reason "<motivo>"`; para parar apenas o processo local: `python _core/motor.py stop-loop`.

## Como manter

- Ajustes de permissao/estado local ficam em `_core/motor.py`.
- Ajustes de ciclo, idle e robustez ficam em `_core/motor_loop.py`.
- Ajustes de fila, claim, modelo e auto-enqueue ficam em `_core/motor_select.py`.
- Mudancas em `_core`, hooks, guards ou adapters sao classe critica pela PR Escalation Matrix; abrir PR e aguardar CTO.
- Validar sempre com `python _core/motor.py --self-test`, `python _core/motor_loop.py --self-test` e, quando PR 27 estiver ativo, `python _core/motor_select.py --self-test`.

## Decisoes importantes

- Kill switch default OFF, git-versionado e auditavel.
- `start` e o comando operacional de ligar; `on` e toggle puro.
- Timeout de `git fetch origin motor-state` cai para cache local, nao derruba o daemon.
- O loop e serial no MVP e nao espera aprovacao de PR.
- Auto-enqueue e conservador: sem P1, sem assignee, sem labels de espera e com roteamento real.
- `repo:pendente` e `squad:pendente` nao contam como roteamento seguro.

## Refs tecnicas

- Docs repo: `C:/dev/pd-framework/_core/docs/motor-supervisor.md`
- Docs repo: `C:/dev/pd-framework/_core/docs/motor-loop.md`
- Docs repo: `C:/dev/pd-framework/_core/docs/motor-auto-enqueue.md`
- Overview: `C:/dev/pd-framework/_core/MOTOR-AUTONOMO.md`
- Matriz: `C:/dev/pd-framework/_core/PR-ESCALATION-MATRIX.md`
- Decisions Squad: `[[times/dev/decisions]]`
