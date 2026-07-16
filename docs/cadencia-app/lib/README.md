# Lib e infraestrutura

| Documento | Escopo |
|---|---|
| [lib-integrations](lib-integrations.md) | wrappers externos server-side |
| [supabase-schema](supabase-schema.md) | tabelas e contratos principais |
| [payment-billing](payment-billing.md) | Stripe e carteira de créditos |
| [tracking-analytics](tracking-analytics.md) | Mixpanel, PostHog, GA4, Meta e CAPI |

## Regras

- Tokens nunca entram no bundle cliente.
- `tenant_id` é obrigatório com `service_role`.
- Um wrapper por serviço, com timeout/retry observável.
- Billing e auth usam banco/Stripe como fonte de verdade, não feature flags.
