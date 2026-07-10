---
date: 2026-07-04
tags: [produto, cadencia]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[PD Framework]]"]
---
# Astryx UI Standard — Sofia

## Status

- Dono: Time Dev / Sofia
- Escopo: novas UIs React/Next/Vite internas
- Fonte viva: `times/dev/sofia/context/astryx-ui-standard.md`
- Skills operacionais: `/astryx-planejar-ui` e `/astryx-storybook`

## Decisao

Sofia passa a usar Astryx como referencia padrao para planejar novas UIs internas, principalmente SaaS, dashboards, areas administrativas e ferramentas operacionais.

Isso nao e uma migracao automatica. Cadencia, PD Portal e qualquer produto com design system vivo continuam respeitando a identidade e os componentes existentes. Astryx entra como acelerador e biblioteca de referencia quando o produto precisa de uma UI nova ou de um padrao ainda nao coberto.

## Pergunta obrigatoria

Como Felipe nem sempre vai lembrar de pedir Astryx pelo nome, Sofia deve perguntar em todo planejamento de UI nova ou redesenho relevante:

```text
Para essa UI, voce quer seguir Astryx como base, avaliar outra biblioteca/design system, ou criar algo proprio?
```

Se Felipe nao escolher na hora, Sofia pode recomendar uma opcao, mas precisa deixar claro que Astryx e default sugerido para UI interna React/Next/Vite, nao imposicao.

## O que foi incorporado

- Fork GitHub: `felipeluissalgueiro/astryx`
- Clone local: `C:/dev/astryx`
- Clone VPS Dev: `/home/felipe/astryx`
- Storybook local validado: `http://localhost:6006/`
- Registro no Time Dev e na Sofia
- Skills criadas para abrir Storybook e planejar UI com Astryx

## Opiniao tecnica da Sofia

Astryx e um bom padrao de referencia para o Time Dev porque nao e apenas um kit visual. O repo combina componentes, tokens, temas, CLI, templates, docs densas para agentes, exemplos Next.js e Storybook.

O ponto forte para o PD Framework e a combinacao de componentes prontos para ferramentas internas: Table, PowerSearch, AppShell, SideNav, TopNav, Dialog, Toast, EmptyState, FormLayout e CommandPalette.

O risco principal e usar o visual base de forma literal. Sem tema Cadencia/PD e sem curadoria de fluxo, a UI pode ficar generica. Por isso Sofia deve adaptar Astryx a identidade do produto, nao copiar o look inteiro.

## Quando usar

Use Astryx como primeira referencia quando:

- A UI for nova.
- O repo alvo for React, Next ou Vite.
- A tela for interna, operacional, SaaS, dashboard ou admin.
- O design system atual nao cobrir bem o fluxo.
- Houver tempo para validar em browser desktop e mobile.

## Quando nao usar

Nao usar Astryx por default quando:

- A tarefa for bugfix visual pequeno.
- A tela existente ja tiver design system maduro.
- O produto tiver UI publica sensivel e Astryx ainda nao tiver tema proprio.
- A stack nao aceitar React/Next/Vite.
- A adocao aumentar complexidade sem ganho claro.

## Fluxo padrao

1. Ler a doc viva do produto e o design system existente.
2. Perguntar se a base sera Astryx, outra biblioteca/design system ou algo proprio.
3. Ativar `/astryx-planejar-ui`.
4. Rodar a CLI Astryx para buscar templates e componentes candidatos quando Astryx for a base ou candidato.
5. Se fizer sentido, ativar `/astryx-storybook` e abrir `http://localhost:6006/`.
6. Validar estados obrigatorios: loading, empty, error, success, disabled e mobile.
7. Definir se a decisao e usar Astryx, fazer spike ou rejeitar.
8. Encaminhar implementacao para o agente dev adequado.

## Gotchas ja validados

- `pnpm build` completo falhou no Windows porque `@astryxdesign/lab` usa `rm -rf`.
- `pnpm -F @astryxdesign/core build` passou.
- `pnpm storybook` funciona.
- `pnpm storybook -- --host ... --port ...` falhou porque o script ja fixa `-p 6006`.

## Definition of Done

- Sofia consultou Astryx antes de desenhar do zero.
- A proposta explica o que sera usado e o que sera rejeitado.
- A identidade Cadencia/PD foi considerada explicitamente.
- O Storybook foi aberto quando Felipe pediu validacao visual.
- A decisao foi registrada se criar precedente novo.

## Notas Relacionadas
[[Produto]] - [[Status]] - [[Skill]] - [[Cadencia]] - [[Pd Framework]]
