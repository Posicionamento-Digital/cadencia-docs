---
date: 2026-05-16
tags: [ia, tecnologia, automacao, briefing]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]"]
---
# Brief — prod: Cadencia — Roadmap

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.




**Projeto Linear:** https://linear.app/posicionamento-digital/project/prod-cadencia-roadmap-6475d91c6139
**Atualizado em:** 2026-05-16
**Preenchido por:** Felipe

---

## O que é e por que existe

Esteira contínua de evolução do produto Cadencia — concentra issues de ajustes, inovações e features baseadas em feedbacks de clientes, novas ideias e estruturas já mapeadas. Inspirado em empresas como GHL e Tally, que expõem seu roadmap publicamente para os clientes saberem o que está sendo desenvolvido.

---

## Stakeholders

- **Felipe** — decisão final sobre o que entra e prioridade
- **Clientes** — fonte de feedback e validação de demanda
- **dev externo** — execução técnica e sugestões de arquitetura

---

## Estado atual

19 issues criadas, todas em **Todo**. Nenhuma em andamento oficialmente. Escopo cobre: infra (migração Railway → VPS), integrações (WhatsApp, cold email, DataStone, Vapi, HeyGen, GHL OAuth), produto (Remotion Reels, landing pages, analytics por tenant, enriquecimento por foto).

Visibilidade: interna por ora. Futuro: página pública para clientes acompanharem o roadmap em tempo real.

---

## Arquitetura e stack

Ver CLAUDE.md do projeto Cadencia — contexto completo disponível.

---

## Decisões técnicas tomadas

_Não preenchido._

---

## O que NÃO fazer

- **Não fragmentar o repo** sem estratégia definida: dev externo sugeriu repos independentes por feature ou categoria, mas a decisão ainda está em aberto. Nenhuma mudança estrutural de repo enquanto não houver um plano claro que não quebre o que está funcional.
- **Sempre consultar** `Hub Projetos/Incidentes/` antes de qualquer mudança — há bugs e problemas já documentados que não devem ser repetidos no Cadencia.

---

## Dependências críticas pendentes

Nenhuma.

---

## Critério de conclusão

Projeto contínuo por natureza — é uma esteira de melhoria, correção e aprimoramento constante do produto. Não tem fim definido.

---

## Processo de execução

Antes de iniciar qualquer issue:
1. **Consultar `Hub Projetos/Incidentes/`** — verificar se há incidente relacionado
2. **Consultar `Cadencia/Logs_execução/`** — identificar onde a issue parou na última sessão e qual o estado atual do trabalho
3. Só então partir para o código

## Notas Relacionadas
[[Brief]]
