# RFC-003 — Integração social Composio

> **Status:** Rascunho
> **Data:** 2026-07-30
> **Autor:** Felipe (via /linear-rfc)
> **Projeto Linear:** https://linear.app/cadencia/project/feat-cadencia-integracao-social-composio-e4419afe2d97
> **PRD:** https://linear.app/cadencia/document/prd-cadencia-integracao-social-composio-53c8d4d63a86

## Contexto

O Cadência precisa transformar redes sociais em uma camada operacional nativa: conexão de contas, publicação de conteúdo, análise posterior e aprendizado para os workers. O PRD define o produto completo, mas a execução será incremental para reduzir risco: entregar uma parte, debugar, publicar, validar em uso real e só então avançar para a etapa seguinte.

Esta RFC cobre a arquitetura única do subsistema, mas separa explicitamente a execução em etapas. A primeira etapa é apenas conexão e publicação funcional via Composio, sem análise automática ainda. Análise, score, relatório semanal e ajuste automático dos workers ficam modelados aqui como contratos futuros para não criar dívida arquitetural, mas não entram no primeiro release implementável.

A integração deve respeitar o estado atual do Cadência: onboarding com passo `tipo`, Perfil com botões sociais legados não funcionais, carrosséis com botão atual “Já publiquei”, página/pill de LinkedIn e dashboard de performance já existente com base em email/blog.

## Estratégia de entrega

A RFC é única porque todos os blocos compartilham os mesmos contratos de identidade, canal, publicação, métricas e tenant. A implementação, porém, será fatiada em fases:

1. **Etapa 1 — Conexão + publicação**: OAuth/conexão, botões do Perfil funcionais, botão “Postar” nos conteúdos e publicação direta Instagram/LinkedIn.
2. **Etapa 2 — Análise + dados + score**: leitura de perfil/mídias/interações, persistência de métricas por canal e score geral explicável.
3. **Etapa 3 — Relatório semanal + feedback dos workers**: cron semanal, WhatsApp curto, email HTML completo, dashboard detalhado e aprendizado por canal alimentando novas gerações.

Cada etapa deve ser entregue, debugada, publicada e validada antes da próxima.

## Componentes

- **SocialConnectionGateway** — camada server-side para iniciar OAuth via Composio, receber callback e registrar estado de conexão por tenant/usuário/canal.
- **ConnectedAccountStore** — persistência local do vínculo entre tenant, usuário Cadência, canal e connected account Composio, sem armazenar token bruto no app.
- **PublishIntent UI** — alteração dos botões de conteúdo: “Já publiquei” vira “Postar”; abre seletor de canais disponíveis e confirma publicação.
- **ChannelPublisher** — serviço server-side que recebe intenção de publicação e executa ferramenta Composio apropriada por canal.
- **ContentPublicationStore** — fonte da verdade de publicação por conteúdo + canal, com status independente, external id/url, erro e timestamps.
- **SocialReadinessChecker** — valida conexão por leitura de perfil/permissões, sem post de teste.
- **SocialAnalysisPipeline** — etapa futura para leitura de perfil, posts e interações; grava análise inicial e semanal por rede.
- **PerformanceDashboardAdapter** — etapa futura para expor Email, Blog, Instagram, LinkedIn e TikTok na aba `/app/performance`.
- **WeeklyPerformanceReporter** — etapa futura para gerar relatório semanal determinístico e idempotente.
- **WorkerFeedbackContract** — etapa futura para entregar aprendizados por canal aos workers de conteúdo.

## Contratos entre componentes

### Conexão social

Entrada:

```ts
type SocialChannel = 'instagram' | 'linkedin' | 'tiktok'

type StartSocialConnectionInput = {
  tenantId: string
  userId: string
  channel: SocialChannel
  source: 'onboarding' | 'profile'
  returnTo: string
}
```

Saída esperada:

```ts
type SocialConnectionState = {
  tenantId: string
  userId: string
  channel: SocialChannel
  provider: 'composio'
  providerConnectedAccountId: string
  status: 'connected' | 'needs_reconnect' | 'failed'
  accountLabel?: string
  capabilities: {
    canReadProfile: boolean
    canReadPosts: boolean
    canPublish: boolean
    canReadInsights: boolean
  }
  connectedAt?: string
  lastValidatedAt?: string
  errorCode?: string
  errorMessage?: string
}
```

Regras:

- Conexão é sempre server-side.
- O Cadência guarda apenas ids, estado, capacidades e metadados não sensíveis.
- Token bruto fica sob responsabilidade do Composio/conta conectada.
- Ao conectar, a validação imediata é só leitura/permissão. Não publicar post de teste.
- Instagram exige conta Business/Creator para o escopo previsto; conta pessoal deve receber erro útil.
- TikTok não bloqueia a Etapa 1. Só entra em publicação após validação explícita de toolkit/auth/permissões.

### Publicação

Entrada:

```ts
type PublishContentInput = {
  tenantId: string
  userId: string
  contentId: string
  contentType: 'carousel' | 'linkedin_post' | 'blog' | 'email' | 'other'
  channels: Array<'instagram' | 'linkedin'>
  caption?: string
  mediaUrls?: string[]
  idempotencyKey: string
}
```

Persistência canônica:

```ts
type ContentPublication = {
  id: string
  tenantId: string
  contentId: string
  channel: 'instagram' | 'linkedin' | 'tiktok'
  provider: 'composio'
  providerConnectedAccountId: string
  status: 'draft' | 'publishing' | 'published' | 'failed'
  externalPostId?: string
  externalPostUrl?: string
  errorCode?: string
  errorMessage?: string
  requestedBy: string
  idempotencyKey: string
  publishedAt?: string
  createdAt: string
  updatedAt: string
}
```

Regras:

- A fonte da verdade é uma linha por `tenant_id + content_id + channel`.
- Publicação é independente por canal.
- Falha em um canal não desfaz publicação bem-sucedida em outro.
- Retry é por canal e não republica canais já publicados.
- Booleanos legados como `linkedin_sent=true` podem existir como compatibilidade, mas não são fonte primária.
- O botão em carrosséis/conteúdos deixa de ser “Já publiquei” e passa a ser “Postar”.
- “Postar” abre seletor de canais similar ao fluxo da página de ideias.
- Na pill de LinkedIn, por enquanto a publicação fica restrita ao LinkedIn.

### Análise e aprendizado por canal (etapa futura)

Persistência futura deve separar:

- análise inicial por rede;
- análise semanal por rede;
- métricas brutas normalizadas;
- insights gerados;
- mudanças de editoria/estratégia aplicadas;
- contrato consumível pelos workers.

O dossier original não deve ser sobrescrito de forma destrutiva. A camada correta é um histórico de aprendizados e ajustes versionados que respeitam o dossier como restrição superior.

## Decisões de domínio

- **RFC única, execução incremental** — a arquitetura fica em um documento para manter contratos coerentes; entrega é por etapas validadas em produção.
- **Etapa 1 é conexão + publicação, sem análise** — OAuth, callback, permissões, conta pessoal vs empresa e publicação já têm risco suficiente. Análise entra depois.
- **Publicação Etapa 1: Instagram + LinkedIn** — ambos têm documentação Composio com Managed App/OAuth. TikTok não bloqueia a primeira entrega.
- **Validação de conexão sem post de teste** — validar por leitura de perfil/permissões/capacidades. Publicar teste real em conta do cliente é risco operacional desnecessário.
- **Publicação por canal como fonte da verdade** — uma entidade por conteúdo + canal substitui booleanos soltos e suporta histórico, retry e publicação multicanal.
- **Falha/retry independente por canal** — sucesso parcial é preservado; retry só afeta canal com falha.
- **Perfil pessoal vs empresa vem antes da conexão no onboarding** — evita o usuário autorizar a conta errada antes de definir o contexto de uso.
- **Rafael é referência interna, não assinatura** — critérios de análise futura usam a régua da persona Rafael, mas a experiência externa é sempre Cadência.

## Edge cases sistêmicos

- **Conta Instagram pessoal** — conexão deve falhar com mensagem útil orientando Business/Creator; não mascarar como erro genérico.
- **Permissão insuficiente** — salvar conexão como `needs_reconnect` ou `failed` com capability faltante; UI deve orientar reconexão.
- **Token expirado/revogado** — publicação falha só naquele canal, registra erro e oferece reconectar/tentar novamente.
- **Callback OAuth duplicado** — operação idempotente por tenant/user/channel/provider account.
- **Duplo clique em “Postar”** — usar `idempotencyKey` para evitar post duplicado.
- **Publicação parcial** — se Instagram publica e LinkedIn falha, Instagram fica `published`; LinkedIn fica `failed` com retry.
- **Retry depois de sucesso parcial** — retry não republica canal já `published`.
- **Canal desconectado no seletor** — aparecer desabilitado ou com CTA de conectar, nunca enviar tentativa cega.
- **TikTok selecionado antes de suportado** — UI pode mostrar previsto/conectar se viável, mas publicação TikTok fica bloqueada até RFC/issue específica validar auth/permissões.
- **Service role/backend** — qualquer leitura/escrita precisa carregar `tenant_id` explicitamente; RLS/service role sem tenant é bug de segurança.

## Fora de escopo

- Análise automática no primeiro release.
- Score geral no primeiro release.
- Relatório semanal no primeiro release.
- Ajuste automático dos workers no primeiro release.
- Publicação TikTok na Etapa 1.
- Post de teste para validar conexão.
- Sistema de pontos/gamificação.
- Tarefas internas rastreáveis no produto.
- Landing pages como canal de desempenho.
- Reprocessar ou republicar conteúdo antigo automaticamente.

## Regras resolvidas no grill

- **[RFC única]** — uma RFC cobre o subsistema completo; a implementação será dividida em etapas executadas e validadas sequencialmente.
- **[Etapa 1]** — primeira entrega é conexão social + publicação funcional, sem análise inicial/automática.
- **[Publicação Etapa 1]** — publicação direta apenas para Instagram e LinkedIn. TikTok fica condicionado a validação posterior de auth/permissões.
- **[Source of truth]** — criar/usar registro por `tenant + conteúdo + canal` como fonte primária do status de publicação.
- **[Falhas]** — erro e retry são independentes por canal; publicação parcial válida é preservada.
- **[Teste de conexão]** — validação inicial é somente por leitura de perfil/permissões/capacidades; não publicar post de teste.

## Alternativas consideradas

- **Dividir em três RFCs** — rejeitado agora. A decomposição será feita nas etapas/issues, mantendo contratos em um único documento.
- **Incluir análise inicial na Etapa 1** — rejeitado para reduzir risco de debugging. Análise depende de métricas, schemas e modelo de dados ainda não fechados.
- **Incluir TikTok na publicação Etapa 1** — rejeitado por incerteza de auth/permissões e ausência de confirmação suficiente para bloquear o release inicial.
- **Usar campos booleanos no conteúdo** — rejeitado como fonte primária por não suportar multicanal, retry e histórico.
- **Publicação transacional multicanal** — rejeitada. Publicação por canal independente é mais robusta para redes externas.
- **Post de teste automático** — rejeitado por risco operacional na conta real do cliente.

## Refs

- Brief: `times/produto/cadencia/context/brief-feat-cadencia-integracao-social-composio.md`
- PRD: `times/produto/cadencia/context/prd-feat-cadencia-integracao-social-composio.md`
- Linear PRD: https://linear.app/cadencia/document/prd-cadencia-integracao-social-composio-53c8d4d63a86
- Composio Instagram toolkit: https://docs.composio.dev/toolkits/instagram
- Composio LinkedIn toolkit: https://docs.composio.dev/toolkits/linkedin
- Composio Tools API: https://docs.composio.dev/reference/api-reference/tools
- Composio Toolkits API: https://docs.composio.dev/reference/api-reference/toolkits
