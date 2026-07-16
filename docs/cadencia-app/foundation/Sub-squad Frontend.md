# Sub-squad Frontend

Responsável pela experiência Next.js: app autenticado, admin, onboarding,
marketing e API routes.

## Superfícies

- conteúdo, calendário, histórico e performance;
- CRM nativo: contatos, empresas, oportunidades, pipelines e views;
- Lara: conversas, agente, conhecimento, tools e agenda;
- cadências: construtor, matrícula e acompanhamento;
- créditos, checkout e administração.

## Regras

- Resolver tenant server-side antes de acessar dados.
- Não expor `service_role` ou credenciais de provider.
- Componentes cliente chamam `/api/app/*`, nunca workers diretamente.
- Estados de loading/empty/error precisam ser reais e acessíveis.
- Mobile, safe area e PWA fazem parte do DoD.
