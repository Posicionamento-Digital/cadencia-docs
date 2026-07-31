# RFC-005 — Biblioteca de mídia e geração de imagens

> **Status:** Rascunho
> **Data:** 2026-07-31
> **Autor:** Felipe (via /linear-rfc)
> **Projeto Linear:** https://linear.app/cadencia/project/sys-refundacao-da-geracao-de-conteudo-d8a2d7c8edb9
> **PRD:** https://linear.app/cadencia/document/prd-cadencia-editor-visual-de-slides-e-biblioteca-de-midia-1dc851d791fd

## Contexto

O Cadência já possui upload assinado por slide, crop no navegador, bucket privado e geração de imagem por IA. Porém, o contrato atual está ligado ao slide, rate limits vivem em memória de instância e imagens geradas não formam um catálogo permanente e reutilizável.

Esta RFC cria um domínio de mídia por tenant. Imagens enviadas ou geradas tornam-se ativos independentes, acessíveis em uma página própria e em seletores consumidores. O editor da RFC-004 referencia somente `media_asset_id`; não conhece provedor, crédito, bucket, prompt ou garbage collection.

## Componentes

- **MediaAssetStore** — fonte canônica de metadata, origem, autoria, estado e paths privados.
- **MediaAssetReferenceStore** — relação consultável entre asset e consumidores/versões, usada por integridade e GC.
- **MediaStorageGateway** — upload assinado, validação de arquivo, originais e derivados no Supabase Storage.
- **MediaLibraryAPI** — listagem, busca, filtros, paginação, lixeira, restauração e autorização por tenant.
- **MediaLibraryUI** — página própria da biblioteca.
- **MediaPicker** — seletor embutido no editor, integrado somente por `media_asset_id`.
- **AIImageGenerationService** — prompt, idempotência, worker existente, persistência e prévia.
- **CreditChargeGateway** — custo server-side, débito/estorno idempotente e ledger.
- **MediaLifecycleWorker** — limpeza de uploads abandonados, retenção da lixeira e GC referencial.
- **DistributedRateLimiter** — limites por tenant/usuário em ambiente serverless.

## Contratos entre componentes

### Ativo canônico

```ts
type MediaAsset = {
  id: string
  tenantId: string
  createdBy: string
  origin: 'upload' | 'ai_generation'
  status: 'processing' | 'active' | 'trashed' | 'failed'
  mimeType: 'image/png' | 'image/jpeg' | 'image/webp'
  width: number
  height: number
  byteSize: number
  originalStoragePath: string
  previewStoragePath?: string
  prompt?: string
  provider?: string
  model?: string
  generationOperationId?: string
  creditCost?: number
  createdAt: string
  trashedAt?: string
}
```

Paths físicos e URLs assinadas são implementação do `MediaStorageGateway`; consumidores persistem apenas o id. Metadata de prompt/provedor não dá ao editor permissão para acionar nova cobrança.

### Referências

```ts
type MediaAssetReference = {
  tenantId: string
  mediaAssetId: string
  consumerType: 'slide_design_version'
  consumerId: string
  createdAt: string
}
```

- Referências são atualizadas na mesma transação que confirma uma versão de slide.
- Exclusão/GC consulta esta relação; é proibido varrer `designState` em tempo real para inferir uso.
- Asset em lixeira continua servindo consumidores existentes.

### Upload

1. `upload-init` autentica tenant/usuário, aplica rate limit e retorna path/token assinado temporário;
2. navegador envia direto ao Storage;
3. `upload-commit` valida path, tenant, MIME, magic bytes, dimensões e tamanho;
4. commit idempotente cria `media_asset` ativo;
5. upload iniciado e não confirmado é elegível para limpeza após 24 horas.

A tabela `slide_image_uploads` e o bucket atual são fontes de migração/compatibilidade, não um segundo catálogo canônico. Confirmados são migrados ou associados a `media_assets`; contratos antigos permanecem apenas durante rollout.

### Geração por IA e créditos

```ts
type GenerateMediaInput = {
  operationId: string
  prompt: string
  intendedUse: 'slide'
}
```

Fluxo:

1. UI busca custo server-side e mostra `Gerar imagem — 1 crédito`;
2. confirmação chama serviço com `operationId`;
3. servidor reserva/debita exatamente 1 crédito no ledger;
4. serviço existente gera imagem e persiste original/preview;
5. somente após o asset ficar `active`, a UI recebe a prévia;
6. falha técnica antes da entrega estorna de forma idempotente;
7. `Aplicar` retorna `media_asset_id`; `Descartar` não remove o ativo nem estorna crédito;
8. retry com mesmo `operationId` não cobra nem gera novamente.

O custo atual de 5 créditos deve ser migrado para configuração server-side de 1 crédito antes do rollout. UI nunca é fonte do preço.

### Biblioteca e permissões

- Todos os usuários autenticados e autorizados do tenant podem listar e reutilizar ativos ativos.
- Upload e geração exigem permissão de criação de conteúdo.
- Lixeira/restauração exigem criador do asset ou papel administrativo do tenant; até existir matriz de papéis completa, restringir ao papel administrativo atual.
- Busca/filtros: texto/prompt, origem, recentes, não utilizados e lixeira.
- Consultas sempre paginadas; thumbnails/previews usam URLs temporárias.

### Lixeira e GC

- `Excluir` faz soft delete e remove o asset da listagem principal.
- Asset referenciado nunca é removido fisicamente.
- Asset não referenciado permanece restaurável na lixeira por 30 dias.
- Após 30 dias, worker revalida ausência de referência, remove derivados/original e então metadata.
- Original de imagem gerada paga é preservado enquanto ativo ou referenciado.
- Falha parcial de remoção é retryable/idempotente e não apaga metadata antes do Storage.

## Decisões de domínio

- **D1 — Biblioteca única por tenant** — uploads e gerações compartilham catálogo, com filtro de origem.
- **D2 — Ativo existe fora do slide** — aplicar/descartar não controla sua existência.
- **D3 — Imagem paga é persistida antes da prévia** — o usuário mantém acesso ao que consumiu crédito.
- **D4 — Contrato por id** — editor e futuros consumidores não conhecem Storage, IA ou cobrança.
- **D5 — Referência explícita** — integridade/GC dependem de tabela relacional, não de varredura de JSON.
- **D6 — Exclusão lógica** — lixeira nunca quebra slides existentes.
- **D7 — Cobrança server-side e idempotente** — 1 crédito visível antes do clique; falha técnica estorna.
- **D8 — Rate limit distribuído** — Maps em memória não são aceitáveis no Vercel multi-instância.

## Edge cases sistêmicos

- **Duplo clique/retry de IA** — mesmo `operationId` retorna operação/asset existente e cobra uma vez.
- **Débito feito, geração falha** — estorno idempotente e asset `failed`; UI informa sem perder prompt.
- **Geração conclui, resposta se perde** — retry consulta operação e devolve asset ativo.
- **Descartar prévia** — asset continua na biblioteca.
- **Asset na lixeira usado por slide** — continua disponível ao renderer/editor; não aparece em novos pickers.
- **Asset restaurado** — volta a `active` sem mudar id ou referências.
- **Tentativa cross-tenant** — retorna autorização negada e registra evento; URL assinada nunca é emitida.
- **Arquivo forjado** — commit valida magic bytes, MIME, dimensões, limite e decode real.
- **GC concorrente com novo uso** — referência e estado são rechecados/lockados antes da remoção.
- **Storage removido, DB falha** — worker registra incidente e mantém tombstone retryable.
- **Prompt impróprio/provedor rejeita** — não expor payload sensível; aplicar política do provedor e estornar quando não houver entrega.

## Fora de escopo

- Vídeo, áudio, PDF e outros tipos de mídia.
- Biblioteca pública entre tenants.
- Marketplace ou compra de stock images.
- Edição fotográfica/filtros dentro da biblioteca.
- Upload de fontes e documentos de marca.
- Compartilhamento externo por link público.
- Conhecer schema de canvas/slide dentro da biblioteca.
- Cobrar por upload, manipulação ou reutilização de asset existente.
- Apagar imediatamente uma imagem paga, ativa ou referenciada.
- Reutilizar tabelas/buckets da Lara.
- Alterar produção ou migrar destrutivamente durante a RFC.

## Regras resolvidas no grill

- **RFC separada** — mídia/IA é domínio próprio, integrado ao editor por id.
- **Biblioteca compartilhada** — ativos pertencem ao tenant e registram `created_by`.
- **Origem unificada** — uploads e IA vivem no mesmo catálogo com filtros.
- **Crédito explícito** — geração custa 1 crédito informado antes do clique.
- **Persistência paga** — descartar não remove a imagem gerada.
- **Integridade** — lixeira e GC preservam qualquer asset referenciado.

## Alternativas consideradas

- **Manter upload preso ao slide** — rejeitado: impede reuso e não representa imagem gerada que ainda não foi aplicada.
- **Varrer JSON de designs para GC** — rejeitado por custo, acoplamento e risco de perder referência.
- **Hardcode de 1 crédito no frontend** — rejeitado: preço e débito precisam ser validados no servidor.
- **Rate limit em memória** — rejeitado em runtime serverless distribuído.
- **Apagar ao descartar a prévia** — rejeitado porque o usuário já pagou pela geração.
- **Tabela/bucket da Lara** — rejeitado por segregação de domínio e risco de vazamento cross-função.

## Refs

- Análise pré-RFC: `cadencia-app/docs/image-platform-pre-rfc-analysis.md`
- PRD: https://linear.app/cadencia/document/prd-cadencia-editor-visual-de-slides-e-biblioteca-de-midia-1dc851d791fd
- DEV-1439: upload de imagem por slide
- DEV-1443: garbage collection de uploads
- DEV-1450: rate limit distribuído
- DEV-1452: geração de imagem por IA
