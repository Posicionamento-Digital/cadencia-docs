# RFC-001 — Espelho de eventos de email do Resend

**Status:** Proposto

**Issue:** DEV-1444

**Responsáveis:** Cadência App + Cadência Growth

## Problema

O dashboard de performance infere envios por `published_posts.published_at` e
usa `scoring_events` apenas para aberturas e cliques. Publicar conteúdo não é
enviar email; também faltam entregas, falhas, rejeições e um denominador real
por campanha. O resultado pode mostrar zero ou números desalinhados com o
Resend, mesmo quando o tenant enviou emails.

## Decisão

Persistir um espelho multi-tenant e append-only dos envios e webhooks do
Resend. O tenant continua sendo resolvido server-side pela sessão; nenhum
usuário ou tenant será fixado no código.

### Modelo

`resend_email_sends` representa uma mensagem aceita pelo provider:

- `email_id` (PK, ID do Resend), `tenant_id`, `channel`;
- `campaign_id` estável, `post_id` opcional e `contact_id`;
- `subject`, `sent_at` e `created_at`.

`resend_email_events` representa cada evento recebido:

- `svix_id` (PK/idempotência), `email_id`, `event_type`;
- `occurred_at`, `created_at` e metadados não sensíveis necessários à UI. URLs
  clicadas não são copiadas, pois podem conter identificadores ou tokens.

As tabelas não armazenam corpo do email. Email do destinatário não é
necessário para analytics e não será copiado. Acesso de `anon` e
`authenticated` é revogado; somente backend com service role escreve/lê.

### Identidade de campanha

- Seinfeld: `campaign_id = post_id`.
- Newsletter: chave determinística derivada do post âncora da edição e
  reutilizada entre retries; a edição pode conter vários posts.
- Tags enviadas ao Resend incluem `tenant_id`, `contact_id`, `channel`,
  `campaign_id` e, quando existir, `post_id`.

### Ingestão

1. Depois de `POST /emails` retornar sucesso, o worker grava o `email_id` e o
   contexto do envio em `resend_email_sends`.
2. O webhook valida a assinatura e tenta persistir o evento antes de responder
   `2xx`.
3. Conflito de `svix_id` é duplicata e retorna sucesso sem reprocessar.
4. Falha técnica de persistência retorna `5xx`, permitindo retry do Resend.
5. Scoring e supressão continuam assíncronos após a captura durável.

Assim, `webhook_dedup` deixa de ser a fonte de idempotência para eventos de
email; a chave única do espelho cumpre esse contrato.

### Leitura

Uma função SQL `resend_email_analytics(tenant_id, since)` agrega no banco:

- resumo: campanhas, mensagens enviadas, entregues, falhas, aberturas e
  cliques;
- série diária: enviados, entregues, abertos e clicados;
- por campanha: assunto, canal, data, destinatários, entregas, pessoas que
  abriram/clicaram e respectivas taxas.

A rota `/api/app/email-stats` resolve o tenant da sessão e chama a função com
esse UUID. Taxas usam contatos únicos como numerador e mensagens enviadas como
denominador. A UI chama abertura de métrica aproximada, por limitações dos
clientes de email.

## Backfill

Um comando idempotente lista emails do Resend dentro da retenção disponível,
recupera detalhes/tags e grava os envios. Tags legadas sem `channel` e
`campaign_id` são resolvidas pelo post/assunto canônico, sem fallback em erro
técnico. `last_event` não é transformado em evento porque a listagem não fornece
seu timestamp; usar o horário do envio falsearia o gráfico. Aberturas e cliques
históricos anteriores ao cutoff explícito de go-live podem ser reconciliados de
`scoring_events`. A atribuição só ocorre quando há exatamente um `email_id`
candidato para tenant/post/contato; casos ambíguos são contabilizados e pulados.
O dashboard identifica essa cobertura histórica como parcial. Replays do
webhook continuam aceitos e idempotentes.

Durante a transição, a API pode usar o ledger `seinfeld_daily_sent` apenas para
explicar lacunas de envios antigos, com marcador de fonte. Ele não substitui o
espelho para eventos futuros.

## Falhas e observabilidade

- envio aceito pelo Resend mas insert local falha: log estruturado com
  `email_id`, tenant e campanha, além de comando de reconciliação;
- webhook sem envio conhecido: evento é preservado e reconciliado depois;
- evento duplicado ou fora de ordem: agregação usa existência e timestamp, não
  ordem de chegada;
- tags ausentes: recuperar `/emails/{id}` fora do caminho crítico, sem atribuir
  evento a outro tenant.

## Fora de escopo

- substituir o Resend;
- armazenar HTML/texto dos emails;
- afirmar que abertura representa leitura humana;
- alterar regras de scoring, warm-up ou supressão.

## Rollout e rollback

1. migration aditiva;
2. writers nos dois pipelines;
3. captura durável no webhook;
4. backfill/reconciliação;
5. endpoint e UI leem o espelho quando houver cobertura.

Rollback da leitura volta a API antiga sem apagar as tabelas. Writers e
webhook podem permanecer ativos, pois são aditivos.

## Validação

- isolamento entre tenants e ausência de UUID/email hardcoded;
- replay do mesmo `svix_id` não duplica nem pontua duas vezes;
- falha de banco no webhook responde `5xx`;
- totais da API batem com fixture do espelho por período;
- gráfico e lista cobrem enviados, entregues, abertos e clicados;
- build/testes do app, pytest do growth e `mkdocs build` verdes.
