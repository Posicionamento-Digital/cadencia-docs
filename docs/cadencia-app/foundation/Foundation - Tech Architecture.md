# Foundation — arquitetura técnica

```mermaid
graph TB
    User[Usuário] --> App[Next.js / Vercel]
    App --> DB[(Supabase CRM + Auth + Storage)]
    App --> Workers[Workers Coolify]
    App --> Growth[cadencia-growth VPS]
    App --> Lara[cadencia-lara]
    Workers --> DB
    Growth --> DB
    Growth --> Resend[Resend/Svix]
    Growth --> Social[Providers sociais]
    Growth --> Lara
    Lara --> Evolution[Evolution GO]
    Lara --> DB
```

## Camadas

- **Frontend/API:** Next.js 15 na Vercel.
- **Dados:** Supabase PostgreSQL, Auth, Storage e Realtime.
- **Workers:** geração pesada no Coolify VPS Master.
- **Growth:** cron, dispatch, scoring e cadências na VPS Master.
- **Lara:** WhatsApp, agente, KB, tools e agenda multi-provider.
- **Email:** Resend com domínio por tenant e webhook Svix.

## Contratos

- `tenant_id` atravessa todas as fronteiras.
- Chamadas internas usam segredo/HMAC e idempotency key.
- Eventos externos validam assinatura.
- Jobs longos ficam fora do timeout da Vercel.
- Estado compartilhado vive no banco, não na memória do processo.
