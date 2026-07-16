# Foundation — estratégia multi-tenant

## Princípio

Uma aplicação e um projeto Supabase atendem todos os clientes. Isolamento é por
`tenant_id`, RLS e resolução server-side do tenant; não por bancos separados.

## Fronteiras

- `users` + `user_tenant_roles` definem acesso.
- Toda entidade de negócio pertence a um tenant.
- `service_role` exige filtro explícito; RLS é backstop.
- Domínios/blogs podem ser dedicados, mas apontam para o mesmo modelo lógico.
- WhatsApp usa uma instância Evolution por tenant.
- Email usa domínio/sender Resend por tenant.
- CRM, pipelines, contatos, oportunidades e cadências vivem no Supabase.

## Provisioning

Signup cria identidade, tenant, papel owner, onboarding e carteira inicial. O
provisionamento assíncrono semeia CRM, domínio Resend/DNS, blog e artefatos de
marca. Cada etapa é idempotente e registra estado parcial.

## Segurança

- Nunca aceitar `tenant_id` do body sem validar a sessão/chave.
- Não usar fallback global de tenant ou instância.
- Realtime, Storage e APIs precisam manter o mesmo escopo.
- Dados de um tenant nunca entram no prompt, log ou resposta de outro.
