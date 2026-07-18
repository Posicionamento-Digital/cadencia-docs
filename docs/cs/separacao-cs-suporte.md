---
title: Separação CS vs Suporte Técnico
tags: [cs, canon]
---

# Separação CS vs Suporte Técnico — Regra absoluta

> Doc constitutivo. **PEDRA ANGULAR** do Time CS. Violar essa separação destrói agilidade e confunde o cliente.
> Fonte: Notion "Playbook - Acompanhamento e Sucesso do Cliente (CS)", seção 6 "Precauções e Alertas". Consolidado 2026-05-25.

---

## A regra

**NÃO MISTURAR canais de CS e Suporte.** São disciplinas distintas com responsabilidades distintas. Misturar = perda de agilidade + confusão de quem resolve o quê.

| CS (Sucesso) | Suporte (Técnico) |
|---|---|
| Resolve **insatisfação** | Resolve **bug técnico** |
| Cuida do **relacionamento** | Cuida da **ferramenta** |
| Métrica: NPS, Sentimento, Saúde Carteira | Métrica: tempo de resolução, recorrência |
| **Felipe** (CS Lead) | **dev externo** (Dev) |

---

## Por que importa

1. **Velocidade de resolução.** Quando CS tenta resolver bug, demora mais que Suporte resolver. Quando Suporte tenta acalmar cliente irritado sem entender o problema dele, vira ping-pong improdutivo.

2. **Métricas separadas.** KPIs de CS (Proatividade, Resposta, Adesão, Saúde, Resolução) não confundem com SLA técnico (tempo de fix, severidade, recorrência).

3. **Carreira do agente.** CS que vira "repassador de recados" perde valor (mesmo nome do KPI 5 — Eficiência de Resolução). Suporte que vira psicólogo perde tempo de produção.

---

## Como classificar uma demanda

Quando um cliente abre uma demanda, perguntar (no fluxograma da Rotina Diária):

```
Cliente relatou problema?
  ├─ SIM → É urgente?
  │         ├─ SIM → Escalar Gestão (Felipe)
  │         └─ NÃO → Suporte Técnico (dev externo)
  └─ NÃO → Registrar como ponto de contato positivo
```

Quando relatou problema, sub-classificação por **Tipo de Problema** (planilha CS):
- **Técnico (Bug)** → dev externo (Suporte)
- **IA (Alucinação)** → dev externo (Suporte) ou Felipe (Gestão), conforme severidade
- **Dúvida** → CS resolve (treinamento, materiais de adoção)
- **Processo** → CS resolve (orientação, ajuste de fluxo)

E **Ação Tomada** (planilha CS):
- **Resolvido na hora** → CS resolveu sozinho (ideal — KPI 5 > 60%)
- **Escalado Suporte** (dev externo) → bug técnico
- **Escalado Gestão** (Felipe) → problema crítico/comercial/estratégico

---

## Erros comuns a evitar

❌ **CS tentar debugar código.** Não é o papel. Coletar contexto e escalar pro dev externo.
❌ **Suporte tentar acalmar cliente irritado.** Não é o papel. Resolver o bug e devolver pro CS pra comunicação.
❌ **Mesma pessoa fazendo os dois.** Mesmo quando Felipe opera solo, MENTALMENTE separar os dois papéis. Hora "Felipe-CS" ≠ hora "Felipe-Suporte".
❌ **Cliente reclamando direto pro dev externo.** Redirecionar pro canal CS — dev externo não é canal de atendimento, é canal de fix.

---

## Onde isso aparece operacionalmente

- **Planilha CS** tem coluna "Ação Tomada" com as 3 opções (resolvido na hora / escalado Suporte / escalado Gestão)
- **KPI 5 Eficiência de Resolução** mede quanto CS resolve sozinho (sem escalar) — meta >60%
- **Hub/Esteira de Projetos** tem status visíveis (Pendente → Em Desenvolvimento → Concluído) — dev externo move o status técnico, CS comunica ao cliente
- **Bot Telegram Suporte** é caso especial: CS opera (configurações, FAQ, treinamento), Dev (dev externo) corrige bugs. Não inverter.

---

## Caso especial: Bot Telegram Suporte

Sub-squad aninhado em `times/cs/suporte/bot-telegram-suporte/`. Mesma regra aplicada:

| O que é do CS | O que é do Dev (dev externo) |
|---|---|
| Configurar bot pra novos clientes | Corrigir bugs de código |
| Atualizar FAQ/base de conhecimento | Refatorar arquitetura |
| Treinar cliente a usar bot | Deploy + infra |
| Triagem de mensagens não respondidas | Implementar features novas |

Quando CS detecta bug → abre chamado pro Dev (dev externo). Quando Dev corrige → comunica ao CS pra avisar cliente. Não pular etapas.

---

## Consequências de violar a regra

(Do playbook original — registrado no callout da Notion):

> ⚡ **NÃO misturar os canais — perda de agilidade**

Adicionar:
- Cliente fica confuso sobre quem chamar
- Métricas perdem significado (CS aparece resolvendo bug, Suporte aparece cuidando de NPS)
- Retrabalho: a pessoa errada começa a resolver e abandona quando percebe
- Carreira do agente estagna (não desenvolve nenhuma das duas disciplinas em profundidade)
