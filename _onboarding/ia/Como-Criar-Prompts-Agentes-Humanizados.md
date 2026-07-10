---
date: 2026-05-14
tags: [processos, ia, prompts, agentes, humanizacao, framework, tecnologia, automacao]
moc: "[[MOC-Inbox]]"
---
# Como Criar Prompts de Agentes Humanizados

Guia para criar um prompt para um agente de IA que reflete traços humanos, tornando a interação mais natural e impactante. Dividido em 7 fases.

---

## Fase 1 — Criação da Profissão/Papel

**O que fazer:**
1. Definir o papel profissional ou técnico que o agente deve assumir
   - Exemplo: "Você é um estrategista digital especializado em automação para pequenas empresas, capaz de conectar ferramentas digitais aos objetivos dos negócios."
2. Fornecer o contexto operacional
   - Exemplo: "Seu objetivo é atender leads vindos de campanhas digitais e orientá-los sobre como soluções de automação podem melhorar sua eficiência."

---

## Fase 2 — Contextualização

1. **Cenário Operacional:** Onde o agente será usado
   - Exemplo: "Este agente será integrado ao WhatsApp para atender leads vindos de campanhas no Instagram."
2. **Adaptação ao Público-Alvo:** Perfil do público
   - Exemplo: "Empreendedores que buscam automatizar processos, mas têm conhecimento técnico limitado."

---

## Fase 3 — Definição do Objetivo

1. **Tarefa Primária:** Objetivo principal do agente
   - Exemplo: "Ajudar leads a entenderem como soluções de automação podem ser aplicadas ao seu contexto."
2. **Subtarefas Específicas:**
   - Identificar necessidades do cliente
   - Recomendar soluções práticas
   - Inspirar confiança e educar sobre automação
3. **Diretrizes para execução:** tom, abordagem, flexibilidade

---

## Fase 4 — Construção de Traços de Personalidade

1. **Traços Primários:** Empático, educador, inspirador, estratégico
2. **Tom Contextual:** Como esses traços se manifestam
   - "Seja caloroso e encorajador, mas mantenha a objetividade ao explicar soluções."
3. **Ajustes por Público:** Leads leigos vs. leads técnicos

---

## Fase 5 — Definição do Estilo de Comunicação

1. **Nível de Formalidade:** Semi-formal, acessível e direto
2. **Tonalidade Específica:** Adaptada ao público
3. **Linguagem Acessível:** Substituições de jargões
   - "Automação" → "Sistema que trabalha sozinho"
   - "Pipeline de vendas" → "Caminho organizado para fechar negócios"

---

## Fase 6 — Formato de Saída

1. **Estrutura Padrão:** Introdução → Diagnóstico/Detalhes → Próximos Passos
2. **Cadeia de Pensamento:** Explicar o raciocínio antes da solução
3. **Tags estruturantes:**
   ```
   <introdução>
   <detalhes>
   <solução>
   <próximos_passos>
   ```
4. **Limites:** Respostas breves (100-150 palavras) ou detalhadas (até 250)

---

## Fase 7 — Exemplos e Fechamento

1. **Exemplos de Respostas por cenário** — ilustrar comportamento em situações comuns
2. **Estratégia de Fechamento:**
   - Resumir o ponto principal discutido
   - Propor próximo passo claro
   - Tom positivo e aberto
3. **Restrições do Agente:**
   - Não fornecer informações sem consultar a base de conhecimento
   - Não responder fora do escopo comercial ou educativo
   - Nunca fazer promessas irreais
4. **Uso da Base de Conhecimento:**
   - Identificar o tipo de pergunta → consultar o documento relevante → formular resposta contextualizada

---

## Exemplo de Prompt Completo (Papel/Profissão)

> "Você é um agente inspirado no Felipe Salgueiro, estrategista visionário e parceiro estratégico. Seu objetivo é criar conexão humana, diagnosticar necessidades com empatia, educar com simplicidade e inspirar com possibilidades. Use uma linguagem prática, acolhedora e sem jargões técnicos. Sempre inicie com uma introdução calorosa, faça perguntas investigativas e finalize com um plano claro para dar continuidade."

---

## Simulação de Comportamento por Cenário

**Lead que chega pelo anúncio sem dizer nada:**
- Início: "Oi, tudo bem? Vi que você se interessou pelo nosso anúncio sobre [tema]. O que chamou sua atenção?"
- Exploração: "E como você organiza isso hoje? Já utiliza alguma solução ou faz manualmente?"
- Encerramento: "Vou montar um plano inicial e, se lembrar de algo mais, me avise."

---

## Notas Relacionadas

- [[Processos/Manuais/IA/Central-Aprendizado-IA]]
- [[Comercial/SDR-Prospeccao/Treinamento-IA-Aplicacoes-Venda]]
