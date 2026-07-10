---
date: 2026-07-06
tags: [produto, cadencia]
moc: "[[MOC-Projetos]]"
---
# Motor Auto-Enqueue

**Responsabilidade:** preparar fila `own:agente` a partir de candidatos seguros do Linear, sem Felipe precisar etiquetar issue por issue.
**Path:** `_core/motor_select.py`
**Issues:** DEV-1191

## Estado atual

O auto-enqueue foi implementado pelo Motor no PR 27 (`feat/dev-1191`) e validado em preview real contra o Linear, mas ainda toca `_core/motor_select.py`. Pela matriz de alcada, isso e **critico** e aguarda aprovacao CTO antes de virar comportamento definitivo em `main`.

Enquanto o PR nao entra em `main`, a documentacao abaixo descreve o contrato aprovado/validado do recurso e deve ser lida como "disponivel na branch do PR".

## O que faz

O recurso adiciona dois comandos:

- `candidates`: lista issues seguras para entrar na fila, sem efeito colateral.
- `enqueue`: aplica `own:agente` nos candidatos selecionados e registra comentario de auditoria no Linear.

O perfil inicial e conservador (`safe`). Ele inclui apenas issues em `Backlog`/`Todo`, sem assignee, sem labels de espera, sem `own:agente`, sem prioridade P1, e com roteamento explicito por `repo:*` ou `squad:*`.

O filtro tambem exclui roteamentos falsos como `repo:pendente` e `squad:pendente`; esse bug foi encontrado no preview real e corrigido antes da aprovacao.

## Como rodar localmente

```bash
# Na branch do PR 27 ate merge em main:
python _core/motor_select.py candidates --profile safe --limit 10
python _core/motor_select.py enqueue --profile safe --limit 5 --dry-run
python _core/motor_select.py enqueue --profile safe --limit 5
python _core/motor_select.py --self-test
```

## Decisoes arquiteturais

- **Preview antes de escrita:** `candidates` e `enqueue --dry-run` existem para inspecionar a fila antes de aplicar labels.
- **Perfil safe e limitado:** o comando nunca varre backlog inteiro sem limite; `--limit` e parte do contrato operacional.
- **Labels por nome, fallback por ID:** resolve `own:agente` no team do Linear e cai para o ID canonico se o label nao aparecer na query de team.
- **Sem gasto de modelo:** auto-enqueue so usa Linear GraphQL; nao aciona Claude, Codex, OpenCode nem OpenRouter.
- **Auditoria por comentario:** cada issue enfileirada recebe comentario indicando perfil e origem (`motor_select.py enqueue`, DEV-1191).

## Gotchas conhecidos

- `repo:pendente` nao e roteamento; tratar como ausencia de repo.
- P1 fica fora do auto-enqueue porque exige intervencao humana/CTO desde o inicio.
- Issue com assignee ativo fica fora mesmo se parecer simples; colisao humano/agente vence.
- A fila final ainda e `motor_select.py queue`: auto-enqueue so prepara labels, nao executa trabalho.

## Refs

- Linear: DEV-1191
- PR: GitHub PR 27 (`feat/dev-1191`)
- Docs: `_core/MOTOR-AUTONOMO.md`, `_core/PR-ESCALATION-MATRIX.md`


---
Fonte repo: `C:/dev/pd-framework/_core/docs/motor-auto-enqueue.md`

## Notas Relacionadas
[[Motor-Auto-Enqueue]] - [[Motor-Autonomo]]
