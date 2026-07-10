---
date: 2026-07-06
tags: [produto, cadencia]
moc: "[[MOC-Projetos]]"
---
# Motor Supervisor

**Responsabilidade:** controlar o kill switch global do Motor Autonomo e o daemon local que consome a fila.
**Path:** `_core/motor.py`
**Issues:** DEV-1182, DEV-1191, ajustes operacionais 2026-07-06

## O que faz

`motor.py` separa duas coisas que parecem iguais na operacao diaria, mas nao sao: o **kill switch** git-versionado e o **loop local**. O kill switch vive na branch `motor-state` e responde se o motor tem permissao para trabalhar. O loop local e um processo `motor_loop.py run` que precisa estar ativo para consumir a fila.

O comando operacional correto para "deixar rodando" e `start`: ele sobe o loop local quando necessario e liga o kill switch com auditoria. `on` continua existindo, mas e apenas toggle do gate; se o loop estiver inativo, nada consome issues.

O status mostra os dois lados:

- `motor: LIGADO/DESLIGADO` vem da branch `motor-state` ou do cache local.
- `loop: ATIVO/INATIVO` vem do pidfile `.pd/motor-loop.pid` e do processo local.

## Como rodar localmente

```bash
python _core/motor.py status --fresh
python _core/motor.py start --reason "teste supervisionado"
python _core/motor.py start-loop
python _core/motor.py stop-loop
python _core/motor.py off --reason "pausa operacional"
python _core/motor.py --self-test
```

## Decisoes arquiteturais

- **Default OFF:** se a branch remota, o cache ou o JSON estiverem ausentes/invalidos, o motor nao trabalha.
- **Fetch remoto tolerante:** timeout de `git fetch origin motor-state` vira falha controlada e cai no cache local, em vez de derrubar o daemon.
- **Supervisor local separado do gate:** permite deixar o processo vivo em idle quando o motor esta OFF e retomar depois.
- **Pid check no Windows via `Get-Process`:** `tasklist` deu falso negativo/falso positivo em execucao real; `Get-Process -Id` virou a fonte local para status.

## Gotchas conhecidos

- `on` nao inicia daemon. Para teste noturno, use `start`.
- Se o status disser `fonte: cache-local`, o motor pode continuar nesta maquina, mas a leitura remota falhou naquele momento.
- O arquivo de log `.pd/motor-loop.err.log` acumula tracebacks antigos; valide o timestamp antes de concluir que o erro e atual.
- Em Windows, um PID antigo pode existir como processo Python sem estar consumindo fila; o status corrigido usa `Get-Process`, mas o sinal mais forte ainda e o log avancando ou a fila mudando.

## Refs

- Linear: DEV-1182, DEV-1191
- Docs: `_core/MOTOR-AUTONOMO.md`, `_core/PR-ESCALATION-MATRIX.md`
- Logs: `.pd/motor-loop.out.log`, `.pd/motor-loop.err.log`


---
Fonte repo: `C:/dev/pd-framework/_core/docs/motor-supervisor.md`

## Notas Relacionadas
[[Status]] - [[Motor-Autonomo]] - [[Motor-Loop]] - [[Motor-Supervisor]]
