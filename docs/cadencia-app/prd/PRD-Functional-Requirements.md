---
date: 2026-05-14
tags: [cadencia, prd, requisitos, funcional]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[qualidade]]"]
---


# PRD — Functional Requirements (61 FRs)

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## Onboarding & Tenant Setup

- FR1: Cliente pode criar conta via magic link
- FR2: Cliente pode responder perguntas via botões pré-definidos
- FR3: Cliente pode fazer upload de logo
- FR4: Sistema pode gerar Dossiê de Marca a partir do onboarding
- FR5: Cliente pode validar cada seção do Dossiê (aprovar/ajustar)
- FR6: Sistema pode gerar Manual de Identidade Visual
- FR7: Sistema pode gerar 3 editorias personalizadas
- FR8: Cliente pode visualizar editorias como cards com exemplo de título
- FR9: Cliente pode reordenar editorias por preferência
- FR10: Cliente pode visualizar progresso do onboarding
- FR11: Sistema pode provisionar tenant automaticamente

## Geração de Conteúdo

- FR12: Sistema pode gerar ideias automaticamente por editoria
- FR13: Cliente pode aprovar/rejeitar ideias via swipe
- FR14: Sistema pode gerar Research Document JSON por ideia aprovada
- FR15: Sistema pode selecionar modelo de carrossel por regras determinísticas
- FR16: Sistema pode gerar headline, subtítulo, gancho e tipo de hook
- FR17: Sistema pode gerar narrativa de 7-10 slides (Método X/Y)
- FR18: Sistema pode gerar legenda (Pergunta/Resposta/Contexto Raso/Profundo/CTA)
- FR19: Sistema pode gerar hashtags otimizadas
- FR20: Sistema pode renderizar slides como PNGs (1080x1350) com ID visual do tenant
- FR21: Sistema pode aplicar cores, fontes e logo do tenant na renderização
- FR22: Cliente pode solicitar regeneração sem custo adicional

## Consumo de Conteúdo

- FR23: Cliente pode visualizar carrossel em preview deslizável
- FR24: Cliente pode copiar legenda com 1 toque
- FR25: Cliente pode copiar hashtags com 1 toque
- FR26: Cliente pode salvar slides na galeria (mobile) ou Downloads (desktop)
- FR27: Cliente pode marcar conteúdo como publicado
- FR28: Cliente pode dar feedback de qualidade (positivo/negativo)
- FR29: Sistema pode solicitar feedback de performance 3-7 dias depois
- FR30: Cliente pode visualizar histórico de conteúdos

## Scheduling

- FR31: Cliente pode configurar dias da semana para geração
- FR32: Cliente pode configurar horário preferido
- FR33: Sistema pode executar geração conforme agenda do tenant

## Billing & Créditos

- FR34: Sistema pode oferecer 3 carrosséis grátis sem pagamento
- FR35: Sistema pode redirecionar para checkout Asaas quando grátis acabam
- FR36: Cliente pode escolher entre planos de créditos
- FR37: Cliente pode comprar pacotes avulsos
- FR38: Sistema pode processar webhooks e liberar créditos
- FR39: Cliente pode visualizar créditos disponíveis
- FR40: Sistema pode notificar créditos baixos (80%) ou esgotados
- FR41: Sistema pode manter acesso a histórico com créditos zerados
- FR42: Sistema pode aplicar 3 dias de graça
- FR43: Sistema pode registrar custo real por operação

## CRM & Lifecycle

- FR44: Sistema pode criar/atualizar contato no GHL
- FR45: Sistema pode aplicar tags de lifecycle no GHL
- FR46: Sistema pode sincronizar dados do tenant com GHL

## Perfil & Configurações

- FR47: Cliente pode visualizar Dossiê de Marca
- FR48: Cliente pode visualizar ID Visual
- FR49: Cliente pode visualizar editorias
- FR50: Cliente pode fazer upload/substituir fotos para capas
- FR51: Sistema pode usar modo temático como default

## Administração

- FR52: Super admin pode visualizar todos os tenants
- FR53: Super admin pode suspender/reativar tenant
- FR54: Super admin pode alterar Model Router sem deploy
- FR55: Super admin pode gerenciar feature flags
- FR56: Super admin pode visualizar métricas agregadas

## Interface & Navegação

- FR57: Cliente pode acessar via PWA (mobile + desktop)
- FR58: App exibe tab bar bottom (mobile) e sidebar esquerda (desktop)
- FR59: App exibe progresso real dos agentes durante geração
- FR60: App exibe estados vazios com orientação
- FR61: App exibe notificações de conteúdo pronto

---

## Notas Relacionadas

- [[Projetos/Cadencia/Docs/PRD-Executive-Summary]]
- [[Projetos/Cadencia/Docs/Epics-Stories-Visao-Geral]]
- [[Projetos/Cadencia/Docs/PRD-Scoping-Roadmap]]
