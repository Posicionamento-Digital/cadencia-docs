---
date: 2026-05-14
tags: [processos, ia, prompts, engenharia, manual, llm, tecnicas, tecnologia, automacao]
moc: "[[MOC-Inbox]]"
---
# Engenharia de Prompts — Manual Completo

**O que é:** Engenharia de prompt é a arte e ciência de construir instruções que facilitem a compreensão de IAs para obter melhores respostas.

---

## Arquitetura de um Prompt Profissional

A estrutura hierárquica **identidade → objetivo → execução → formato → limitações** segue o princípio de "priming" — a definição inicial da identidade molda todo o comportamento subsequente.

### 1. Profissão/Papel (Identidade)

Define quem o agente é, função, especialização e traços de personalidade.

**Por que vem primeiro:** Cria forte efeito de "priming". Impacta como o modelo interpreta todas as instruções subsequentes.

**Componentes essenciais:** Função profissional clara, traços de personalidade que humanizam, relação com o público-alvo.

```
Você é um especialista em marketing digital e psicologia humana,
com experiência em criar estratégias de conversão para e-commerce.
```

### 2. Objetivo Central (Propósito)

Define a razão de existência do agente e métricas de sucesso.

**Componentes essenciais:** Objetivo principal articulado, métricas de sucesso, foco estratégico.

### 3. Processo Estruturado (Execução)

Detalha o passo-a-passo em subtarefas com instruções condicionais.

**Componentes essenciais:** Decomposição em subtarefas, instruções condicionais, exemplos contrastivos (bons vs ruins), tags delimitadoras.

### 4. Formato de Saída (Apresentação)

Define como as respostas devem ser formatadas.

**Componentes essenciais:** Estrutura clara de resposta, exemplos modelo, contraexemplos do que evitar.

### 5. Uso de Ferramentas (Recursos)

Detalha ferramentas disponíveis e como utilizá-las.

### 6. Regras e Restrições (Limitações)

Estabelece limites de comportamento do agente. Mais efetivos após estabelecimento completo do papel.

---

## Princípios Científicos Aplicados

| Princípio | O que é |
|---|---|
| **Contextual Scaffolding** | Construção progressiva do contexto em camadas |
| **Role-Based Conditioning** | Definição clara do papel ativa redes neurais específicas |
| **Chain of Thought** | Estruturação explícita do raciocínio em etapas melhora precisão |
| **Few-Shot Learning** | Exemplos permitem aprendizado por demonstração, não apenas instrução |
| **Constraint Propagation** | Restrições explícitas são mais eficazes após o modelo compreender seu papel |

---

## Otimizações Técnicas

### Tags Delimitadoras
```xml
<processo-estruturado-vendas>
  <exemplos-saudação>
    ...
  </exemplos-saudação>
</processo-estruturado-vendas>
```
Servem como marcadores que facilitam navegação contextual.

### Exemplificação Contrastiva
Apresentar exemplos positivos E negativos cria limites claros.

✅ **Bom:** `"Olá! Que bom falar com você. Como posso ajudar hoje?"`
❌ **Mau:** `"Oi. O que vc quer?"`

### Instruções Metacognitivas
Instruções sobre como o modelo deve pensar sobre suas próprias respostas:
```
NUNCA mencione, cite ou referencie diretamente as ferramentas
internas que você usa para obter informações.
```

### Hierarquia Aninhada
Estrutura aninhada permite representação mental hierárquica dos procedimentos.

---

## Diretrizes para Estruturar Prompts

### 1. Seja Claro e Direto
❌ "Me ajude com uma apresentação."
✅ "Preciso de ajuda para criar apresentação de 10 slides para reunião trimestral de vendas. Deve cobrir desempenho Q2, produtos mais vendidos e metas Q3. Forneça esboço com pontos principais para cada slide."

### 2. Use Exemplos
❌ "Escreva um email profissional."
✅ "Preciso escrever email profissional sobre atraso no projeto. Aqui está exemplo similar: [exemplo]. Ajude-me a redigir novo email seguindo tom e estrutura similares."

### 3. Incentive o Pensamento
❌ "Como posso melhorar produtividade da equipe?"
✅ "Estou procurando melhorar produtividade da equipe. Pense passo a passo, considerando: 1) Bloqueadores atuais, 2) Soluções potenciais, 3) Desafios de implementação, 4) Métodos de medição. Para cada etapa, explique seu raciocínio."

### 4. Refinamento Iterativo
❌ "Torne isso melhor."
✅ "Esse é bom começo, mas refine: 1) Torne tom mais casual, 2) Adicione exemplo específico de cliente, 3) Encurte segundo parágrafo focando em benefícios."

### 5. Use Interpretação de Papéis
✅ "Você é fornecedor de tecidos. Estou me preparando para negociar redução de 10% nos preços. Como fornecedor, forneça: 1) Três objeções potenciais, 2) Contra-argumentos da minha perspectiva, 3) Propostas alternativas."

---

## Técnicas Avançadas

### Zero-Shot
Sem exemplos, apenas instrução direta. **Quando usar:** Tarefas simples onde o modelo já tem conhecimento.

### Few-Shot
Dá alguns exemplos para ensinar o padrão. **Quando usar:** Formato específico ou raciocínio que precisa ser aprendido.
```
Escreva sinônimo para cada palavra:
Palavra: Feliz → Sinônimo: Contente
Palavra: Triste → Sinônimo: Abatido
Palavra: Inteligente → Sinônimo:
```

### Chain of Thought (CoT)
Força o modelo a pensar passo a passo. **Quando usar:** Problemas complexos que requerem lógica e raciocínio.
```
Resolva explicando seu raciocínio passo a passo:
João tem 5 maçãs. Ganha mais 3. Quantas tem no total?
```

### Prompt Chaining
Divide tarefa em múltiplos prompts sequenciais. **Quando usar:** Tarefas longas ou multi-etapas.
```
Prompt 1: Quais são os passos para criar plano de negócios?
Prompt 2: Descreva o primeiro passo em detalhes.
Prompt 3: Agora descreva o segundo passo.
```

---

## Markdowns Essenciais

| Sintaxe | Uso |
|---|---|
| `[ ]` | Placeholders e marcadores |
| `< >` | Estruturação hierárquica (XML) |
| `{ }` | Conjuntos de valores ou código |
| `( )` | Informações contextuais |
| `#` `##` `###` | Hierarquia de títulos |
| Tabelas | Estruturação de dados |

---

## Evitando Alucinações

1. **Instruções Claras:** "Responda apenas com base em informações que você conhece. Se não souber, diga claramente."
2. **Restrinja o Escopo:** Limitar o domínio de resposta reduz invenção
3. **Admitir Falta de Conhecimento:** "Se não tiver certeza, responda 'Não sei'."
4. **Baseie em Fontes:** "Baseie sua resposta em informações verificáveis."
5. **Formatos Estruturados:** Separar fatos conhecidos de incertezas

---

## Checklist para Prompts de Qualidade

- [ ] **Clareza:** A instrução é direta e objetiva?
- [ ] **Contexto:** O modelo tem todas as informações necessárias?
- [ ] **Exemplos:** Incluí exemplos para facilitar compreensão?
- [ ] **Formato:** Especifiquei como quero a resposta?
- [ ] **Detalhamento:** Deixei claro o nível de detalhe esperado?
- [ ] **Persona:** Pedi para assumir um papel, se necessário?
- [ ] **Lógica:** Usei cadeias de pensamento para raciocínios complexos?
- [ ] **Restrições:** Defini limites e comportamentos proibidos?

---

## Notas Relacionadas

- [[Processos/Manuais/IA/Central-Aprendizado-IA]]
- [[Processos/Manuais/IA/Como-Criar-Prompts-Agentes-Humanizados]]
- [[Processos/Manuais/IA/Prompts-Audio-TTS]]
