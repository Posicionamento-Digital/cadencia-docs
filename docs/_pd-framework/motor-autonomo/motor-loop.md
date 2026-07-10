---
date: 2026-07-06
tags: [produto, cadencia]
moc: "[[MOC-Projetos]]"
---
# Motor Loop

**Responsabilidade:** executar ciclos autonomos em serie enquanto o kill switch estiver ligado.
**Path:** `_core/motor_loop.py`
**Issues:** DEV-1132, DEV-1134, DEV-1135, DEV-1136, DEV-1137

## O que faz

`motor_loop.py` e o daemon 24/7 do Motor Autonomo. A cada iteracao ele consulta `motor.is_enabled(fresh=True)`. Se o motor estiver OFF, fica em idle. Se estiver ON, chama `motor_run.run_cycle()` para fazer uma unidade completa de trabalho: selecionar issue, claimar, abrir worktree, rodar harness, classificar mudanca, abrir PR ou liberar a issue.

O loop e serial por design. Ele nao tenta paralelizar issues; quando um ciclo termina em PR aguardando alcada, o loop nao espera aprovacao, volta para a fila e pega a proxima issue elegivel.

Falhas de ciclo nao encerram o daemon. Excecoes em `run_cycle()` sao registradas no stdout e o loop continua. O caso corrigido em 2026-07-06 foi anterior ao `run_cycle`: timeout no fetch do kill switch escapava de `motor.is_enabled()`; agora `motor.py` transforma isso em fallback de cache.

## Como rodar localmente

```bash
python _core/motor_loop.py run --once
python _core/motor_loop.py run --max-cycles 3
python _core/motor_loop.py run --idle-sleep 300 --work-sleep 15
python _core/motor_loop.py --self-test
```

## Decisoes arquiteturais

- **Um ciclo por vez:** reduz colisao de worktree, claim e budget enquanto a confianca do motor amadurece.
- **Idle separado de erro:** fila vazia e motor OFF contam como idle; erro real incrementa `errors` mas nao mata o loop.
- **Aprovacao assincrona:** PR em review nao bloqueia a proxima issue.
- **Sem deploy/merge em main:** o loop entrega PR ou branch de integracao conforme matriz de alcada; producao segue humana.

## Gotchas conhecidos

- `run --once` pode demorar varios minutos se o harness realmente estiver trabalhando; timeout de shell nao significa necessariamente falha.
- O loop loga no final do ciclo. Durante trabalho longo, a evidencia viva pode estar no Linear: issue em `In Progress`, comentario de claim, worktree/branch criada.
- Se nao houver issue `own:agente` elegivel, o loop fica ocioso mesmo com motor ligado.

## Refs

- Linear: epic DEV-1132, stories DEV-1134/1135/1136/1137
- Docs: `_core/MOTOR-AUTONOMO.md`, `_core/PR-ESCALATION-MATRIX.md`, `_core/BUDGET-GUARD.md`
- Consumidores: `_core/motor.py`, `_core/motor_run.py`, `_core/motor_select.py`


---
Fonte repo: `C:/dev/pd-framework/_core/docs/motor-loop.md`

## Notas Relacionadas
[[Motor-Autonomo]] - [[Motor-Loop]]
