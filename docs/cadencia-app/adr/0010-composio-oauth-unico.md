# ADR-0010 — Composio como provedor OAuth único

**Data:** 2026-06-16  
**Status:** aceito

## Contexto

Sem o GHL como motor de integrações, o Cadência precisava conectar múltiplas redes sociais sem manter uma implementação separada de autenticação, refresh e particularidades para cada provedor.

## Decisão

Usar o Composio como camada OAuth para as integrações sociais. A identidade externa é vinculada ao tenant, as conexões ficam registradas por usuário e canal e o backend comprova as capabilities antes de liberar publicação.

## Consequências

- Um fluxo comum para Instagram e LinkedIn.
- Menos código específico de autenticação por rede.
- Dependência operacional do Composio para conexão e transporte.
- Monitoramento e UX de reconexão continuam obrigatórios quando a credencial perde validade.

## Referência

- [Conexões e publicação social](../features/social-connections/index.md)
