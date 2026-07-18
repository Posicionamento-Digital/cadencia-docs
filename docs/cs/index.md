---
title: CS & Entrega
tags: [cs, canon]
---

# Time CS & Entrega — Cadencia

Manual operacional canônico do Time CS & Entrega. **Fonte de verdade** — o `pd-framework/times/cs/foundation/` é cópia derivada.

## Quem é

**Letícia** — CS Lead. Pragmática, orientada a resultado, defensora do cliente internamente. Garante que o que foi prometido no comercial seja entregue com qualidade e dentro do prazo. Gestiona a carteira ativa e coordena com Dev quando há gap técnico.

## Escopo

O Time CS & Entrega gerencia **tudo pós-fechamento de contrato**:

- **Implementações** — setup completo do Cadencia para clientes (tenant, agentes, integrações, CRM)
- **CS Recorrente** — acompanhamento mensal, renovações, NPS, expansão de escopo
- **Treinamentos** — Treinamento Claude Code 30d e variantes
- **Consultorias** — mentorias e projetos de IA sob medida

## Fronteiras

- **Comercial → CS:** quando o COM fecha negócio, faz handoff explícito via `/registrar-cliente`. A partir daí, CSE assume.
- **CS → Dev:** quando implementação exige código novo (worker, feature, bug), abrir issue no CAD. CSE gerencia o cliente, CAD gerencia o código.
- **CS → Jurídico:** contratos, notificações, aspectos legais → acionar `/elaborar-contrato`. CSE não elabora contratos — recebe assinado e executa.

## Sub-áreas

- **Onboarding** — implementação nova (fases 0-4.5 do playbook 11 fases)
- **Relacionamento** — CS recorrente (rotina diária/semanal/mensal + 5 KPIs)
- **Suporte** — SLA por severidade (P1-P4), separado do CS por princípio

## Referências principais

### Playbooks

- [Playbook Implementação 11 Fases](playbook-implementacao-11-fases.md) — do contrato à transição
- [Playbook Treinamento Claude Code 30d](playbook-treinamento-claude-code-30d.md) — do fechamento ao follow-up pós-treinamento
- [Playbook Retenção](playbook-retencao.md) — sinais de churn e ações preventivas
- [Rotina CS](rotina-cs.md) — diária, semanal, mensal + 5 KPIs

### Framework de decisão

- [Separação CS vs Suporte](separacao-cs-suporte.md) — pedra angular
- [SLA de Suporte](sla-suporte.md) — severidades P1-P4 + janela + escalation
- [Política de Expansão](politica-expansao.md) — upsell, cross-sell, indicação
- [Matriz de Responsabilidades](matriz-responsabilidades.md) — PD × Cliente × Gestor de tráfego por produto

### Processos

- [Sistema de Comunicação com Cliente](sistema-comunicacao-cliente.md) — e-mail + WhatsApp por etapa (gate obrigatório)
- [Protocolo de Aquecimento de Chip 14d](protocolo-aquecimento-chip-14d.md) — Fase 4.5, operação crítica
- [Padrão Pasta de Cliente](padrao-pasta-cliente.md) — estrutura `times/produto/consultorias/<slug>/`

### Templates

- [Checklist de Briefing (11 seções)](checklist-briefing.md) — para clientes de consultoria
- [Checklist de Briefing Treinamento Claude Code](checklist-briefing-treinamento-claude-code.md) — para alunos
- [Template Checklist Projeto Linear](template-checklist-projeto-linear.md) — adaptável por produto
- [Template Manual da Marca](template-manual-da-marca.md) — entregável padrão pós-briefing
