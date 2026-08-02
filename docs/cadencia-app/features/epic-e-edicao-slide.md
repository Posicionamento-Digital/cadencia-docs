# Histórico — Epic E / DEV-1412: editor por overlay e rerender

> [!CAUTION]
> **ARQUITETURA REPROVADA E NÃO UTILIZÁVEL.** Esta página existe para preservar o histórico. Não reative `NEXT_PUBLIC_EPIC_E_ENABLED`, não continue a solução por overlay `<textarea>`/`layout_metadata` e não trate a ativação em produção como pendência válida. A direção atual está em [Editor visual — fundação Konva homologada](editor-visual-engine-spike.md).

## O que foi tentado

A Epic E posicionava campos React sobre o PNG canônico usando `layout_metadata.fields[]`. Ao salvar, persistia texto, enfileirava `rerender_slide`, aguardava worker Playwright, sobrescrevia o PNG no Storage e fazia polling até a conclusão.

Partes técnicas funcionaram: extração de bounding boxes, feature flag, backfill, job idempotente e polling. Isso não tornou a experiência adequada como editor visual.

## Por que não pode ser usado

- PNG não contém camadas editáveis; texto, imagens e formas já estão fundidos.
- `layout_metadata` cobre geometria de campos conhecidos, não o documento visual completo.
- A cobertura real ficou parcial entre famílias de template.
- Cada save dependia de API, fila, worker, Storage e polling.
- A interface bloqueava durante a operação e podia demorar dezenas de segundos.
- Continuar editando após fechar modal produziu estados de spinner e saída inaceitáveis nos testes humanos.

O requisito aprovado passou a ser resposta local em tempo real, feedback de save abaixo de 100 ms e teto absoluto de 3 s para a operação homologada. A arquitetura antiga não consegue atingir isso sem deixar de ser ela mesma.

## O que permanece válido

- O pipeline HTML→PNG dos workers continua funcional e não será reconstruído.
- Playwright continua sendo parte do renderer de geração inicial.
- O histórico, ADRs e incidentes da Epic E continuam úteis para evitar regressões e repetir erros.

## Substituição

A DEV-1669 testou Fabric e Konva no stack real. Konva foi homologado como engine da futura fundação: canvas local, estado estruturado próprio do Cadência, manipulação em tempo real e PNG derivado no navegador.

Isso ainda é um spike, não o editor completo. A próxima etapa define contratos definitivos na RFC e só então implementa persistência e UI de produto.

## Fontes históricas

- Repo: `cadencia-app/docs/epic-e/README.md`
- Incidente: `pd-framework/incidents/2026-07-21_epic-e-ui-quebrada-sem-manual-qa.md`
- Issue: [DEV-1412](https://linear.app/cadencia/issue/DEV-1412/featcadencia-epic-e-edicao-cosmetica-por-slide-pilar-4)
- Direção atual: [DEV-1669](https://linear.app/cadencia/issue/DEV-1669/spikeeditor-validar-fabricjs-vs-konva-no-next-15-e-react-19)
