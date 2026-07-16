# Foundation — princípios técnicos

1. **CRM Cadência é a fonte de verdade.** Contatos, empresas, oportunidades,
   pipelines, tags, scoring e cadências vivem no Supabase.
2. **Tenant scope é obrigatório.** `service_role` nunca substitui filtro de
   `tenant_id`.
3. **Provider por canal.** Email usa Resend; WhatsApp usa Lara/Evolution; canais
   sociais usam integrações próprias.
4. **Idempotência no banco.** Webhooks, dispatches, provisioning e cadências têm
   chaves/constraints explícitas.
5. **Estado só após confirmação.** Flags `sent`, `scheduled` e `done` não mudam
   antes do provider ou writer confirmar.
6. **Configuração com merge atômico.** Nunca sobrescrever JSON compartilhado por
   read-modify-write concorrente.
7. **Operação observável.** Erros, retries e estados parciais precisam aparecer
   em logs/health checks.
8. **Credenciais no 1Password.** Nenhum segredo em docs, exemplos ou commits.
