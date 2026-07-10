---
date: 2026-06-03
tags: [ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
---
﻿---
date: 2026-06-03
tags: [ia, tecnologia, claude-code, harness, arquitetura]
moc: "[[Claude Code — Arquitetura das Camadas]]"
---

# O que é um harness

**Harness** é o conjunto de infraestrutura que envolve um modelo de IA para tornar seu comportamento previsível, contextualizado e repetível.

O modelo sozinho é **stateless** — cada prompt começa do zero, sem memória, sem identidade, sem regras. O harness resolve isso.

A equação mais simples do campo:

> **{Agente} = {Modelo} + {Harness}**

O modelo fornece raciocínio probabilístico bruto. O harness traduz isso em ação determinística e repetível.

---

## As 3 camadas

| Camada | Arquivo | Função |
|---|---|---|
| **Contexto** | `CLAUDE.md` | Quem é o agente, o que faz, o que não faz, regras |
| **Memória** | `STATE.md` | O que já aconteceu, o que está em andamento agora |
| **Execução** | Skills, Hooks, Workers | Comportamentos encapsulados e repetíveis |

---

## A analogia do computador (a mais precisa)

O artigo de referência do campo formula assim:

> *"The LLM is simply the CPU, the context window is the RAM, and the Agent Harness is the Operating System that manages I/O, memory, and scheduling."*
> — Adnan Masood, Agent Harness Engineering (2026)

| Computador | Harness de IA |
|---|---|
| **CPU** | LLM — executa raciocínio, mas é stateless |
| **RAM** | Janela de contexto — memória de trabalho da sessão |
| **Sistema Operacional** | Harness — gerencia I/O, memória, agendamento, segurança |
| **Programas** | Skills e Workers — tarefas encapsuladas que o SO executa |
| **Drivers / APIs** | MCP — protocolo que conecta o SO aos dispositivos externos |
| **Usuário** | Orquestrador — define o que o SO deve priorizar |

Antes do SO, programadores escreviam direto em código de máquina — trabalhoso, frágil, dependente de quem estava operando. Prompt engineering é exatamente isso: instrução direta ao modelo sem abstração.

O harness é o SO que abstrai essa complexidade e torna a operação previsível, segura e escalável para qualquer pessoa que entrar no sistema.

**O futuro:** o harness está evoluindo de exoesqueleto frágil para o **Sistema Nervoso Central da empresa automatizada** — um Enterprise AI Control Plane que combina CI/CD + Identity & Access Management + observabilidade, gerenciando uma força de trabalho digital autônoma.

---

## A analogia da cozinha (a mais intuitiva)

> **A cozinha é o harness. O chef é o modelo de IA.**

Um chef talentoso sem cozinha organizada improvisa, erra, repete trabalho. Um chef mediano numa cozinha bem montada entrega resultado consistente toda vez.

| Cozinha | Harness |
|---|---|
| Manual da cozinha | `CLAUDE.md` |
| Caderno de pedidos do dia | `STATE.md` |
| Receitas padrão da casa | Skills |
| Processos automáticos (fechar fogão, lavar louça) | Hooks |
| Estações especializadas (forno, grelha, confeitaria) | Squads |
| Sous-chef que coordena as estações | Orquestrador |
| Cozinheiros de cada estação | Workers |
| Fornecedores externos | MCP / APIs |

O CMV do restaurante é o custo de inferência da operação de IA. Quem controla o CMV com um harness bem montado reduz custo de token em até 10x sem trocar o modelo (KV-cache + semantic routing).

---

## Por que isso importa

- **88% dos projetos de IA empresarial não chegam em produção** — o gargalo não é o modelo, é o harness
- **65% das falhas** rastreiam para harness defects: Context Drift, Schema Misalignment, State Degradation
- Otimizar o modelo sem estabilizar o harness gera retornos decrescentes

Claude Code é a ferramenta que viabilizou o harness para não-devs. Não é um chat. Não é um plugin de IDE. É um agente de terminal que lê o projeto inteiro, executa tarefas encadeadas e respeita a estrutura montada ao redor dele.

Quem souber montar esse sistema opera com IA em outro nível. Quem não souber continua usando prompt solto.

---

## Notas relacionadas

[[Claude Code — Arquitetura das Camadas]] · [[Por que o harness é urgente — custos de inferência]] · [[NoCode Startup - Live-01- Harness-IA V2]]

## Notas Relacionadas
[[Skill]] - [[O Que É Um Harness]] - [[Skills]]
