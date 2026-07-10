---
date: 2026-06-03
tags: [ia, tecnologia, harness, custos, inferencia, mercado]
moc: "[[O que é um harness]]"
type: source
entities: ["[[qualidade]]"]
---
# Por que o harness é urgente — custos de inferência

> Argumento central: o custo de usar IA está subindo na prática, mesmo com preço por token caindo. A resposta não é pagar mais — é otimizar o que se tem. E otimizar significa construir harness.

---

## O paradoxo dos custos de IA em 2026

O preço por token caiu **280x em dois anos**. E mesmo assim o gasto total das empresas com IA **subiu 320% no mesmo período**.

Por quê? Porque workflows agênticos disparam **10 a 20 chamadas de LLM por tarefa do usuário** em vez de uma. RAG infla janelas de contexto. Sistemas mais sofisticados = mais tokens por operação.

O custo unitário caiu. O consumo explodiu. A conta aumentou.

> *"By 2030, inference on a 1 trillion parameter model will cost 90% less than in 2025 — yet overall inference costs are expected to increase, because token demand will grow faster than token prices fall."*
> — [Gartner, março 2026](https://www.gartner.com/en/newsroom/press-releases/2026-03-25-gartner-predicts-that-by-2030-performing-inference-on-an-llm-with-1-trillion-parameters-will-cost-genai-providers-over-90-percent-less-than-in-2025)

---

## A crise econômica da inferência

OpenAI gerou ~$3,7 bilhões em receita em 2025. E perdeu $5 bilhões. **Gasta $1,35 para cada $1 que recebe.**

Um pesquisador do Google Turing Award publicou em 2026 um paper identificando os custos de inferência como o principal gargalo econômico impedindo empresas de IA de atingir lucratividade.

Isso não é problema só das big techs. É a realidade de qualquer empresa que usa IA em produção sem otimização.

> Fonte: [AI Inference Cost Crisis 2026 — Oplexa](https://oplexa.com/ai-inference-cost-crisis-2026/)

---

## Scaling laws chegando no limite

Durante anos, a resposta para "como melhorar IA" era simples: mais parâmetros, mais dados, mais compute.

Esse modelo está esgotando. Sara Hooker documentou em 2026 no ensaio *"On the Slow Death of Scaling"*:

- Modelos menores estão fechando o gap com modelos maiores através de técnicas de treinamento melhores
- Exemplo: Falcon 180B foi superado pelo Llama 3 8B **um ano depois** do lançamento
- Retornos de RL scaling mostram saturação latente — modelos maiores ganham eficiência, mas com retornos decrescentes
- Datasets muito grandes geram redundância e diminuição de performance abaixo do previsto pelas leis de escala

A conclusão prática: **mais parâmetros não será a resposta**. A vantagem vai para quem souber fazer mais com o que tem.

> Fonte: [LLM Scaling Laws Explained — BuildFastWithAI](https://www.buildfastwithai.com/blogs/llm-scaling-laws-explained)

---

## A evolução dos paradigmas: prompt → contexto → harness

A forma como a indústria interage com IA evoluiu em 3 fases:

| Fase | Período | Foco |
|---|---|---|
| **Prompt Engineering** | 2022–2024 | Como formular bem a pergunta |
| **Context Engineering** | 2025 | Como construir o contexto ao redor da pergunta |
| **Harness Engineering** | 2026 | Como arquitetar o sistema inteiro que opera o agente |

**Andrej Karpathy** foi quem cunhou o termo "context engineering" em 2025, argumentando que engenharia de contexto importa mais do que engenharia de prompts — não basta frasear bem; é preciso **projetar em nível de sistema** o que está disponível para o modelo no momento do raciocínio.

Harness Engineering (2026) é o estágio atual: subsume os dois anteriores e opera num nível mais alto — define o workflow do agente, suas restrições, loops de feedback, toolchain e ciclo de vida.

> Fontes:
> - [The Third Evolution: Why Harness Engineering Replaced Prompting in 2026 — Epsilla](https://www.epsilla.com/blogs/harness-engineering-evolution-prompt-context-autonomous-agents)
> - [Agent Harness Engineering — The Rise of the AI Control Plane — Adnan Masood, Medium](https://medium.com/@adnanmasood/agent-harness-engineering-the-rise-of-the-ai-control-plane-938ead884b1d)

---

## O que quebra sem harness — dados de 2026

**65% das falhas de IA em empresas rastreiam para Harness Defects**, especificamente:

- **Context Drift** — o contexto muda entre sessões e o agente perde coerência
- **Schema Misalignment** — o agente não sabe o que pode e não pode fazer
- **State Degradation** — memória inconsistente entre execuções

Otimizar o modelo sem estabilizar o harness gera retornos decrescentes.

> A métrica central de 2026 não é mais qualidade do prompt — **é KV-cache hit rate e complexidade do harness**.

> Fonte: [Beyond Prompts and Context: Harness Engineering for AI Agents — MadPlay](https://madplay.github.io/en/post/harness-engineering)

---

## A conclusão para a live

O harness não é uma sofisticação opcional. É a resposta econômica e técnica ao momento atual:

1. **Custos sobem na prática** — mais chamadas por tarefa, contextos maiores, workflows agênticos
2. **Scaling tem retorno decrescente** — modelos maiores não são a saída
3. **65% das falhas** são de harness, não de modelo
4. **A indústria inteira migrou** de prompt → contexto → harness nos últimos 2 anos

Quem souber construir harness vai fazer mais com menos. Quem não souber vai pagar cada vez mais por resultados cada vez menos previsíveis.

---

## Notas relacionadas

[[O que é um harness]] · [[Claude Code — Arquitetura das Camadas]] · [[NoCode Startup - Live-01- Harness-IA (legacy)]]
