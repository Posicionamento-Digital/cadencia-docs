# Sub-squad Growth

Responsável pelo `cadencia-growth`: geração/dispatch de blog, email, newsletter,
LinkedIn e Instagram; scoring Resend/Svix; cadências e provisioning de email.

## Runtime

- trigger on-demand `:39090`;
- webhook Resend/Svix `:8767`;
- Mission Control `:8768`;
- crons de geração, retry, cleanup e cadence tick.

## Regras

- CRM Cadência/Supabase é a fonte de contatos e estado.
- Email usa Resend com domínio por tenant.
- Flags só mudam após confirmação do provider.
- Webhooks e dispatches são idempotentes.
- Um tenant/canal com falha não aborta os demais.
