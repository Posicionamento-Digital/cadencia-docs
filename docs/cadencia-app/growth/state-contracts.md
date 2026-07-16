# Contratos de estado — cadencia-growth

## Princípios

- Supabase é a fonte de verdade.
- Toda operação multi-tenant filtra `tenant_id`.
- Flags de entrega só mudam após confirmação do provider.
- Erro técnico é diferente de conflito idempotente.
- Writers de configuração usam RPC/merge, nunca read-modify-write do JSON inteiro.

## `published_posts`

- `seinfeld_body`/`subject`: conteúdo existe, não significa envio.
- `seinfeld_scheduled_at`: slot planejado.
- `seinfeld_sent`: dispatch concluído segundo o contrato do job.
- `newsletter_included`: post já consumido por uma newsletter concluída.
- `linkedin_text`/`instagram_caption`: conteúdo gerado.
- Flags `*_sent`/`scheduled_at` exigem confirmação do provider correspondente.

Retries reutilizam conteúdo já gerado. Não chamar LLM novamente quando apenas a
entrega falhou.

## Dedup de email

`seinfeld_daily_sent` reserva contato/post antes do envio:

- lista com row: reserva criada;
- `[]`: conflito legítimo, já reservado/enviado;
- `None`: erro técnico, não enviar.

O dispatch cross-day usa o mesmo contrato para impedir duplicação ao retomar
backlog.

## `tenant_config`

`merge_tenant_config` aplica patch no PostgreSQL sob lock. Writers não podem
sobrescrever o objeto inteiro.

### `config.email`

Casa canônica:

- `provider: resend`;
- `sending_domain` e `resend_domain_id`;
- `verification_status`;
- `sender_address`, `sender_name`, CTA e preheader;
- flags/caps de warm-up.

Campos flat existem apenas como espelho temporário para leitores antigos. A RPC
`merge_tenant_config_email` faz merge aninhado e preserva writers concorrentes.

## `contacts`

Fonte única de destinatários e scoring:

- `tenant_id` + email/telefone identificam o contato no escopo correto;
- `status=subscribed` entra em dispatch;
- `bounced`/`complained` ficam suprimidos;
- `score` e `temperatura` acumulam eventos;
- tags/custom fields vivem no CRM Cadência.

## `scoring_events`

- `svix_id`/event ID fornece idempotência;
- `post_id` atribui o evento ao conteúdo;
- `contact_id` e `tenant_id` são obrigatórios após resolução;
- patches de score/supressão precisam ser condicionais para tolerar concorrência.

## Cadências

### `cadences` / `cadence_steps`

Definição da sequência, gatilho, canal, copy, offset e condição.

### `contact_cadences`

Runtime por contato: `status`, `current_step`, `next_send_at`, ciclo e timestamps
de resposta.

### `cadence_step_checks`

UNIQUE por `(contact_cadence_id, cadence_step_id, cadence_cycle)`:

- insert novo: executar avanço e, quando aplicável, log;
- conflito: não reenviar; recuperar somente o avanço idempotente;
- erro técnico: não avançar.

## Provisioning

`provisioning_log` diferencia `pending`, `partial`, `ready` e falha permanente.
Retry só executa etapas faltantes e nunca apaga estado concluído. CRM, domínio
Resend, DNS e blog possuem checks idempotentes próprios.

## Generation queue

- `pending`: aguardando claim;
- `processing`: worker assumiu;
- `done`: saída persistida;
- `failed`: erro final observável.

Claim precisa ser atômico. Jobs presos exigem timeout/cleanup explícito, não
alteração manual silenciosa.

## Gates de validação

```bash
pytest -q tests
```

Cobrir concorrência, dedup, retry, isolamento tenant, bounce/complaint e avanço
de cadência após conflito idempotente.
