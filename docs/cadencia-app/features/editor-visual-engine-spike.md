# Editor visual de slides — arquitetura atual

> **Estado atual:** o editor visual baseado em Konva e `cadencia.slide-design/v1` está disponível em produção para gerações novas. O salvamento atual persiste texto; as demais manipulações visuais ainda são locais da sessão.

## Não confundir com a Epic E

A arquitetura vigente usa canvas Konva, estado estruturado em `design_manifest` e a rota full-screen `/app/editor/[documentId]?slide=<index>`.

A [Epic E / DEV-1412](epic-e-edicao-slide.md) é histórico arquivado. Seus overlays `<textarea>`, `layout_metadata.fields[]`, URL `?edit=` e backfill não devem ser reativados nem usados como base para novas funcionalidades.

## Componentes atuais

- **Contrato:** `cadencia.slide-design/v1`, armazenado em `slides_content[i].design_manifest`.
- **Engine:** Konva atrás de adapter próprio do Cadência.
- **UI:** editor full-screen desktop, um canvas vivo e miniaturas lazy-loaded.
- **Sessão:** cache LRU de até 10 slides, baseline e dirty state por slide.
- **Fallback:** gerações históricas sem manifesto continuam exibindo o PNG.
- **PNG final:** o pipeline HTML + Playwright dos workers continua sendo a fonte da imagem publicada.

## O que o usuário consegue fazer

| Ação | Na sessão | Depois de salvar e reabrir |
|---|---:|---:|
| Editar texto | Sim | **Sim** |
| Inserir quebra de linha com `Shift + Enter` | Sim | **Sim** |
| Desfazer/refazer | Sim | Não se aplica antes do save |
| Mover, duplicar, excluir ou reordenar | Sim | Não |
| Criar formas | Não | Não |
| Trocar fundo ou imagem | Não | Não |

Na edição inline, `Enter` conclui, `Shift + Enter` cria uma nova linha e `Esc` cancela. O botão **Salvar** aceita somente alterações textuais. Se também houver transformação, mudança de camada ou CRUD local, o editor pede que essas alterações sejam desfeitas antes de salvar o texto.

## Como o salvamento funciona

Cada campo textual alterado é enviado para o endpoint de edição com uma chave de idempotência. O servidor atualiza o campo do slide e o `design_manifest`, preserva o espelhamento `headline` ↔ `text` das capas e enfileira o rerender do PNG. O cliente espera cada job terminar antes de enviar o campo seguinte, recarrega o manifesto e só então limpa o dirty state.

O endpoint e o polling foram reaproveitados da infraestrutura anterior, mas isso não reativa a Epic E: somente o contrato de persistência/fila é compartilhado.

## Evolução segura

- Evoluir `cadencia.slide-design/v1`, o adapter Konva e os componentes `SlideDesignEditor`.
- Não inferir camadas de PNGs históricos nem executar o backfill de `layout_metadata` para o editor novo.
- Persistência de transformações, formas, propriedades e background exige stories e contrato próprios.
- Toda mudança passa pelo gate visual e pelo E2E de save em Vercel Preview; os runners recusam produção.

## Referências

- Fonte técnica canônica: `cadencia-app/docs/editor/slide-design-v1.md`
- ADR vigente: `cadencia-app/docs/adr/0019-editor-visual-konva-slide-design-v1.md`
- QA: `cadencia-app/tests/qa/README.md`
- Engine: [DEV-1669](https://linear.app/cadencia/issue/DEV-1669/spikeeditor-validar-fabricjs-vs-konva-no-next-15-e-react-19)
- Contrato: [DEV-1670](https://linear.app/cadencia/issue/DEV-1670/feateditor-gerar-e-abrir-slide-novo-no-contrato-cadenciaslide-designv1)
- Shell e save: [DEV-1671](https://linear.app/cadencia/issue/DEV-1671/feateditor-abrir-editor-full-screen-com-miniaturas-lazy-loaded)
