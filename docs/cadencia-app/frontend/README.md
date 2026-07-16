# Frontend e API

| Documento | Escopo |
|---|---|
| [frontend-app](frontend-app.md) | app autenticado, CRM, conteúdo e créditos |
| [frontend-marketing](frontend-marketing.md) | páginas públicas |
| [api-routes](api-routes.md) | mapa das API routes |
| [api-auth-provisioning](api-auth-provisioning.md) | signup e tenant provisioning |
| [api-integrations](api-integrations.md) | Stripe, CAPI e API interna |

## Regras

- Tenant resolvido server-side.
- Browser chama `/api/app/*`, não workers/VPS diretamente.
- Credenciais ficam server-side.
- CRM usa as tabelas nativas do Supabase.
- Estados mobile, acessibilidade, loading, empty e error fazem parte do DoD.
