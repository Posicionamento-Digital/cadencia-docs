---
date: 2026-07-08
tags: [ia, framework, agentes, arquitetura, pd, motor-autonomo, apresentacao]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework 2.0 — Apresentação

> Documento pra explicar o Framework 2.0 (Motor Autônomo 24/7) a alguém de fora do dia a dia técnico. Ver também o canvas visual: `[[2026-07-08 PD Framework 2.0 - Canvas Passo a Passo]]`

---

## 1. O que é o PD Framework

Não é um chatbot. É um **sistema operacional de agentes de IA** rodando dentro de uma empresa real (Cadencia) — vários "funcionários digitais" especializados, cada um dono de uma área (Comercial, CS, Dev, Marketing, Financeiro, Infra), que executam trabalho de verdade em sistemas reais (CRM, GitHub, WhatsApp, banco de dados).

**Realidade que motivou o framework:** empresa hoje = 1 pessoa executando tudo (Felipe) + 1 dev de escopo limitado (Luiz). Automação máxima não é otimização — é critério de sobrevivência operacional.

### Como é organizado
- **Squads por área** — cada um com persona própria, memória (`STATE.md`), regras (`CLAUDE.md`) e skills.
- **Stamper** — o orquestrador central, tipo Chief of Staff, que mantém contexto do dia a dia.
- **~150 skills** — comandos prontos pra tarefas recorrentes (fechar issue, provisionar cliente, revisar código, etc).
- **Memória estruturada** — nada se perde entre sessões: cada squad grava o que está em andamento, decisões tomadas e histórico de incidentes.

---

## 2. O que muda na versão 2.0 — Motor Autônomo 24/7

A v1 do framework precisa de alguém (Felipe) chamando o agente pra cada tarefa. A v2 introduz o **Motor Autônomo**: um sistema que **varre a fila de trabalho sozinho, escolhe o que fazer, executa, e só bate na porta humana quando precisa de aprovação pra algo arriscado.**

### Fluxo de 1 ciclo do motor

1. **Gate de segurança** — motor checa se está ligado (kill switch). Se desligado, não faz nada.
2. **Seleção** — pega a fila de issues marcadas "responsabilidade do agente" no Linear, ordenada por prioridade, pula quem já tem dono humano ativo, resolve qual squad é dono, e escolhe o modelo de IA certo pro tamanho da tarefa.
3. **Isolamento** — abre um ambiente de trabalho isolado (branch + worktree própria) pra não interferir em nada que esteja em andamento.
4. **Execução** — um agente de IA roda sozinho (headless, sem interface), só codifica e commita — com um conjunto de travas técnicas que bloqueiam ações proibidas.
5. **Entrega** — se produziu algo, abre um **Pull Request** (pedido de revisão), notifica, e registra o resultado. Se não conseguiu, libera a tarefa com o motivo.
6. **Continua** — o motor não espera aprovação. Vai pra próxima tarefa da fila. A aprovação humana acontece depois, de forma assíncrona.

---

## 3. Por que isso é eficiente

| Alavanca | Efeito |
|---|---|
| **Fila trabalha sozinha** | Tarefas represadas (que antes dependiam de alguém "ter tempo de chamar o agente") são processadas continuamente, 24/7. |
| **Paralelização de decisão** | Enquanto o motor trabalha em tarefas rotineiras, o humano foca só nas decisões que exigem julgamento (aprovar PR, resolver conflito de lógica). |
| **Modelo certo pro trabalho certo** | Seleciona automaticamente o "nível" de IA (mais barato/rápido vs. mais caro/potente) conforme a complexidade — não desperdiça custo em tarefa simples. |
| **Sem gargalo de etiquetagem manual** | A próxima etapa (auto-enqueue) deixa o próprio sistema identificar candidatas seguras no backlog, sem depender de alguém marcar manualmente. |
| **Zero retrabalho por erro repetido** | Toda decisão, correção e incidente vira memória persistente — o sistema nunca comete o mesmo erro duas vezes por falta de contexto. |

### As travas que tornam isso seguro (não é "IA descontrolada")

- **Fronteira de alçada:** o motor **nunca** faz merge em produção, nunca faz deploy, nunca força push, nunca fala direto com cliente. Só o humano aprova essas ações — existe uma matriz explícita de "quem aprova o quê".
- **Kill switch versionado:** dá pra desligar o motor inteiro com um commit — desligado por padrão até ser ativado.
- **Nunca roda em produção real:** o motor só roda em ambiente de desenvolvimento; produção só recebe scripts 100% determinísticos, sem IA tomando decisão ao vivo.
- **Teto de custo e esforço:** limites automáticos de gasto e de "quanto trabalho" o agente pode gastar numa tarefa.
- **Detecção de colisão:** se um humano já está mexendo numa tarefa, o motor pula pra outra — nunca briga por prioridade.
- **Piso de qualidade de modelo:** nenhuma tarefa de código roda no modelo mais barato/fraco — existe um piso mínimo de capacidade garantido.

---

## 4. Como isso pode mudar uma empresa

- **De "eu preciso fazer isso" para "isso está sendo feito"** — o trabalho operacional repetitivo (código, atendimento, follow-up, provisionamento) deixa de competir por atenção humana; roda em paralelo, o tempo todo.
- **Escala sem contratar** — uma empresa enxuta (1-2 pessoas) consegue operar com a cobertura de um time muito maior, porque o "time" de agentes nunca dorme, nunca esquece contexto, e processa fila continuamente.
- **Decisão humana concentrada no que importa** — como toda ação de risco exige aprovação explícita, a pessoa só gasta atenção em decisão de verdade — não em execução mecânica.
- **Conhecimento organizacional que não vaza quando alguém sai** — toda decisão, todo processo, todo erro vira memória estruturada e consultável — não fica só na cabeça de uma pessoa.
- **Modelo replicável por área** — a mesma arquitetura (squad + memória + skills + motor) se aplica a qualquer função da empresa: vendas, suporte, dev, financeiro, marketing.

---

## 5. Status real (transparência)

✅ **Funciona hoje:** caminho feliz validado ao vivo — o motor já pegou uma issue real, trabalhou sozinho e abriu um Pull Request de verdade.

⚠️ **Em construção:** escalonamento automático de incidente crítico via WhatsApp, deploy definitivo do motor como serviço contínuo, guarda de orçamento em código (hoje é regra documentada, não travada em código), execução em paralelo de várias tarefas ao mesmo tempo.

❌ **Ainda não ligado por padrão:** o motor fica desligado (kill switch OFF) até decisão explícita de ativação — não é "piloto automático" ligado sem supervisão.

---

## Referências técnicas (pra quem quiser aprofundar)

- `_core/MOTOR-AUTONOMO.md` — doc técnica completa do componente
- `_core/PR-ESCALATION-MATRIX.md` — matriz de quem aprova o quê
- `_core/BUDGET-GUARD.md` — travas de custo e esforço
- `CONTEXT.md` — arquitetura geral do framework
