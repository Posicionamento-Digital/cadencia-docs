# RFC-004 — Editor visual de slides

> **Status:** Rascunho — motor de canvas pendente do spike
> **Data:** 2026-07-31
> **Autor:** Felipe (via /linear-rfc)
> **Projeto Linear:** https://linear.app/cadencia/project/sys-refundacao-da-geracao-de-conteudo-d8a2d7c8edb9
> **PRD:** https://linear.app/cadencia/document/prd-cadencia-editor-visual-de-slides-e-biblioteca-de-midia-1dc851d791fd

## Contexto

A DEV-1412 provou que o Cadência consegue alterar um slide e renderizá-lo novamente, mas colocou API, fila, worker, Chromium, Storage e polling no caminho crítico da edição. Esse fluxo permanece adequado para criação/finalização, mas é incompatível com interação visual imediata.

Esta RFC substitui somente a arquitetura de edição do Pilar 4 antigo. O pipeline, as responsabilidades, o runtime e a saída PNG atuais dos workers são preservados. Para slides novos, a geração passa a emitir também um documento visual estruturado; o editor manipula esse documento no navegador e exporta o PNG sem chamar worker ou Chromium no save.

A biblioteca de mídia é domínio separado, definido na RFC-005. O editor conhece imagens apenas por `media_asset_id`.

## Componentes

- **SlideDesignProducer** — extensão aditiva do renderer atual; produz o manifest editável junto do PNG durante a geração de slides novos.
- **SlideDesignSchema** — envelope canônico e versionado `cadencia.slide-design/v1`, independente do motor de canvas.
- **CanvasEngineAdapter** — traduz o schema Cadência para o motor escolhido e retorna mutações/exportações sem vazar JSON privado da biblioteca.
- **EditorShell** — rota React em tela cheia, toolbar, painel de camadas/propriedades, miniaturas e guard de viewport.
- **EditorSessionStore** — cache local por slide, dirty state e histórico de undo/redo; mantém apenas um canvas instanciado.
- **BrowserSlideExporter** — exporta PNG 1080 × 1440 após fontes/assets estarem carregados e seguros para CORS.
- **SlideBatchSaveAPI** — valida e confirma vários slides, com idempotência, atomicidade e resultado por item.
- **SlideVersionStore** — revisões monotônicas, versões imutáveis, retenção e restauração.
- **SlideDesignFeatureGate** — feature flag, autorização e guard de largura mínima; flag/viewport nunca substituem segurança server-side.

## Contratos entre componentes

### Documento visual canônico

```ts
type SlideDesignV1 = {
  schema: 'cadencia.slide-design/v1'
  canvas: { width: 1080; height: 1440; backgroundElementId: string }
  elements: SlideElement[]
  mediaAssetIds: string[]
  generatedFrom: {
    templateFamily: string
    templateVersion: string
    sourceSlidesContentRevision: string
  }
}

type SlideElement =
  | TextElement
  | ImageElement       // referencia mediaAssetId; nunca URL persistida
  | ShapeElement       // rect | ellipse | line | arrow
  | BackgroundElement  // solid | gradient | image
```

Regras:

- `designState` nasce durante a geração do slide novo e é a fonte visual canônica desde a criação.
- `slides_content` preserva conteúdo semântico/proveniência; não há sincronização bidirecional implícita.
- PNG, miniatura e índice textual são derivados.
- URLs assinadas, objetos Canvas, handlers e estado interno do motor nunca são persistidos.
- Toda evolução incompatível cria migrador explícito de schema.

### Produção do manifest no worker

O renderer continua produzindo o PNG atual. Antes do screenshot, templates ativos passam a declarar elementos editáveis por ids estáveis e tipos suportados. O `SlideDesignProducer` extrai geometria, computed styles, conteúdo, z-order, recortes e referências de mídia e valida o resultado contra `SlideDesignSchema`.

Não é permitido reconstruir camadas a partir do screenshot nem tratar o `layout_metadata` parcial como documento editável. Cada família de template ativa precisa de contract test provando que todo elemento visível relevante possui representação no manifest. Template incompatível não pode ser anunciado como editável.

### Sessão e lazy load

- A abertura recebe a lista de slides e URLs das miniaturas, carregando somente o design do slide inicial.
- Clique em miniatura busca o design sob demanda e o mantém em cache local limitado.
- Um único canvas permanece montado; trocar slide desmonta listeners/assets do anterior.
- Cada slide mantém dirty state e undo/redo próprios.
- Fechar com mudanças abre confirmação; “Continuar editando” apenas fecha o diálogo.

### Save em lote

```ts
type SaveSlideItem = {
  operationId: string
  slideId: string
  baseRevision: number
  design: SlideDesignV1
  exportedPngUploadId: string
}

type SaveSlideResult =
  | { slideId: string; status: 'saved'; revision: number; versionId: string; pngUrl: string }
  | { slideId: string; status: 'conflict'; currentRevision: number }
  | { slideId: string; status: 'failed'; code: string; retryable: boolean }
```

Fluxo por slide:

1. navegador exporta PNG e faz upload assinado temporário;
2. API valida autenticação, tenant, schema, dimensões, revisão e cada `media_asset_id`;
3. transação cria versão imutável, atualiza revisão/artefato ativo e grava referências de mídia;
4. retry com o mesmo `operationId` devolve o resultado anterior;
5. falha/conflito mantém o slide dirty localmente; sucessos do mesmo lote são preservados.

`baseRevision` desatualizada retorna conflito próprio. “Salvar como cópia” cria novo slide/id e nunca contorna a revisão do original.

### Versionamento

- Undo/redo é histórico de sessão e não toca banco.
- Cada save confirmado cria versão imutável.
- Retenção: versão original + versão ativa + 20 versões recentes.
- Restaurar cria nova versão baseada na escolhida.
- Limpeza nunca remove original ou ativa.

## Decisões de domínio

- **D1 — Design canônico desde a geração** — o slide novo já nasce editável; não há conversão posterior do PNG.
- **D2 — Schema do Cadência, motor substituível** — dados persistidos não dependem do JSON experimental de fornecedor.
- **D3 — Extensão aditiva do renderer** — preservar workers significa manter pipeline/runtime/PNG, adicionando o manifest estruturado necessário.
- **D4 — Interação totalmente local** — nenhum gesto, undo/redo ou preview chama API, worker ou Chromium.
- **D5 — Save explícito e em lote** — botão existente salva somente slides modificados; atomicidade é por slide.
- **D6 — PNG exportado no browser** — worker não participa do save; servidor valida antes do commit.
- **D7 — Desktop primeiro** — editor oculto abaixo de 1024 px; deep link recebe aviso.
- **D8 — Motor decidido após spike** — Fabric e Konva permanecem candidatos. Filerobot só pode avançar se provar React 19 e estado estável.

## Edge cases sistêmicos

- **Asset cross-tenant** — qualquer `media_asset_id` alheio invalida somente aquele item do lote e gera evento de segurança.
- **Canvas contaminado por CORS** — export não inicia enquanto ativos não vierem de URL assinada compatível ou proxy autorizado.
- **Fonte ainda carregando** — exporter aguarda `document.fonts.ready`; timeout mantém dirty state.
- **Retry após resposta perdida** — `operationId` impede versão duplicada.
- **Duas sessões** — segunda revisão recebe conflito, sem sobrescrita.
- **Falha parcial** — slides confirmados deixam de ser dirty; apenas falhas/conflitos permanecem.
- **Template incompatível** — slide é gerado normalmente, mas não recebe capability editável; telemetria bloqueia rollout amplo até cobertura dos templates ativos.
- **Schema antigo** — migrador roda antes de montar o canvas; falha não corrompe estado persistido.
- **Navegação por 20 slides** — cache tem limite/LRU e libera recursos; nunca mantém 20 canvases.
- **Saída acidental** — reload/rota/fechar usa dirty guard sem disparar save automático.

## Gate do spike do motor de canvas

O spike roda no Next.js 15 + React 19 real, em branch/preview isolada, e precisa provar:

1. build e TypeScript strict sem `--legacy-peer-deps`, fork, patch local ou hydration warning;
2. round-trip do schema Cadência com texto/fonte, crop de imagem, quatro formas, fundo sólido/imagem/gradiente, camadas e undo/redo;
3. PNG determinístico 1080 × 1440 após reload, fontes carregadas e assets CORS-safe;
4. interação local a 60 FPS no notebook homologado;
5. save individual p95 ≤ 1 s e lote representativo de até 10 slides ≤ 3 s;
6. qualquer execução > 3 s no cenário homologado reprova;
7. somente um canvas vivo e ausência de crescimento contínuo ao navegar por 20 slides;
8. sanitização de JSON/SVG, rejeição cross-tenant e reprodução de conflito em duas sessões;
9. acessibilidade de foco, teclado, dialogs e toolbar.

**Recomendação inicial:** Fabric.js é o primeiro candidato pelo modelo de objetos e serialização maduros. Konva é o segundo, usando estado de domínio próprio. O spike, e não esta preferência, decide o adapter inicial.

## Fora de escopo

- Slides históricos ou migração de PNG para camadas.
- Mobile/tablet abaixo de 1024 px.
- Autosave e colaboração em tempo real.
- Filtros fotográficos, desenho livre e fontes personalizadas.
- Templates reutilizáveis e formatos diferentes de 1080 × 1440.
- Alteração em massa entre slides.
- Substituição do pipeline de workers.
- Persistir JSON interno do motor como fonte canônica.
- Ativar flag, mergear ou publicar em produção como parte do spike/RFC.

## Regras resolvidas no grill

- **Duas RFCs** — editor e biblioteca têm responsabilidades e contratos distintos.
- **Fonte de verdade** — `designState` é canônico para o visual; `slides_content` é proveniência.
- **Contrato de mídia** — editor conhece apenas `media_asset_id`.
- **Atomicidade** — save em lote preserva sucesso parcial, com transação por slide.
- **Concorrência** — revisão monotônica impede sobrescrita silenciosa.
- **Recorte** — somente slides novos 1080 × 1440, desktop e sem autosave.

## Alternativas consideradas

- **Filerobot como documento canônico** — rejeitado: `designState` é experimental e a documentação de compatibilidade React não cobre React 19.
- **JSON Fabric/Konva persistido diretamente** — rejeitado por lock-in e dificuldade de migração.
- **Reconstruir camadas do PNG/layout_metadata** — rejeitado por perda de informação e baixa fidelidade.
- **Worker rerender no save** — rejeitado por repetir a latência da DEV-1412.
- **Transação única para o lote** — rejeitada porque uma falha descartaria sucessos válidos.

## Refs

- Análise pré-RFC: `cadencia-app/docs/image-platform-pre-rfc-analysis.md`
- DEV-1412: https://linear.app/cadencia/issue/DEV-1412/featcadencia-epic-e-edicao-cosmetica-por-slide-pilar-4
- PRD: https://linear.app/cadencia/document/prd-cadencia-editor-visual-de-slides-e-biblioteca-de-midia-1dc851d791fd
- Fabric.js core/serialização: https://fabricjs.com/docs/core-concepts/
- Konva save/load em React: https://konvajs.org/docs/data_and_serialization/Best_Practices.html
- Filerobot Image Editor: https://github.com/scaleflex/filerobot-image-editor
