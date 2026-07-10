---
date: 2026-06-03
tags: [ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[NoCode-Startup]]", "[[PD Framework]]", "[[comercial]]"]
---
﻿---
title: "Live 01 V2 — Como Montar seu Próprio Harness de IA com Claude Code"
tags: [nocode-startup, claude-code, live, harness, produto]
date: 2026-06-03
projeto: NoCode Startup
status: rascunho-v2
versao: v2
referencia: "[[NoCode Startup - Live-01- Harness-IA]]"
---

# Live 01 V2 — Como Montar seu Próprio Harness de IA com Claude Code

**Duração:** 2 horas | **Formato:** Gancho → Demo → Quebra-cabeça ao vivo | **Data:** 04/06/2026

> Referência V1:[[NoCode Startup - Live-01- Harness-IA (legacy)]]]
> Canvas: [[Claude Code — Arquitetura das Camadas.canvas]]
> Conceito base: [[O que é um harness]]
> Por que agora: [[Por que o harness é urgente — custos de inferência]]

---

## A equação

> **{Agente} = {Modelo} + {Harness}**

O modelo é a commodity. O harness é a vantagem competitiva.

---

## Sequência de Canvas — o que abrir e quando

| # | Momento | Canvas | Ação |
|---|---|---|---|
| 1 | **Setup** — antes de apresentar qualquer coisa | [[Quebra-cabeça — 9 Peças do Harness.canvas]] | Mostrar o destino: "é isso que vamos montar" |
| 2 | **Bloco 1 → 1.5** — após o gancho CMV | [[Claude Code — Arquitetura das Camadas.canvas]] | Ancora a analogia do computador + 5 layers |
| 3 | **Bloco 1.5 → Bloco 2** — transição para o demo | [[3 Defects do Harness.canvas]] | Visualiza os 65% de falha antes de mostrar o PD Framework |
| 4 | **Bloco 3** — construção peça a peça | [[Quebra-cabeça — 9 Peças do Harness.canvas]] | Abrir e manter visível: cada peça construída = uma célula "acesa" |
| 5 | **Bloco 4** — apresentação do HIVE | [[Evolução do Harness — 4 Estágios.canvas]] | Mostra onde o aluno chegou (Estágio 2) e onde fica o PD Framework (Estágio 3) |
| 6 | **Q&A** | [[Glossário Harness de IA.canvas]] | Referência de termos durante perguntas |

> **Todos os canvas da live:**
> - [[Claude Code — Arquitetura das Camadas.canvas]] — arquitetura completa do harness
> - [[Glossário Harness de IA.canvas]] — termos do artigo traduzidos
> - [[Quebra-cabeça — 9 Peças do Harness.canvas]] *(novo)* — progressão visual das peças
> - [[3 Defects do Harness.canvas]] *(novo)* — Context Drift / Schema Misalignment / State Degradation
> - [[Evolução do Harness — 4 Estágios.canvas]] *(novo)* — de Prompt Engineering até PD Framework

---
## Estrutura da Live (2h)

### Bloco 1 — Gancho CMV (5 min)

> 📌 **Canvas aberto no setup:** [[Quebra-cabeça — 9 Peças do Harness.canvas]] — mostrar antes de falar, não fechar durante a live

**O que acontece:** Felipe abre com o problema econômico antes de mostrar qualquer ferramenta.

**Por que esse bloco:** sem ancoragem no problema, a solução parece técnica demais. 
Com o CMV, qualquer pessoa de negócio entende instintivamente por que harness importa — antes de ver uma linha de código.

**Script sugerido:**

> "Quem aqui já ouviu falar de CMV? Custo de Mercadoria Vendida. Todo restaurante que sobrevive controla o CMV na régua — é a diferença entre margem e falência. Ingrediente caro, processo ruim, produto indo pro lixo: CMV estoura e o restaurante fecha.
>
> IA tem o mesmo problema. O preço por token caiu 280 vezes em dois anos. E mesmo assim as empresas estão gastando 320% a mais com IA. Por quê? Porque workflows agênticos disparam 10 a 20 chamadas de LLM por tarefa. RAG infla contexto. Modelos mais sofisticados consomem mais tokens por operação.
>
> 88% dos projetos de IA empresarial não chegam em produção. E quando chegam, 65% das falhas não são problema do modelo — são problema do que está em volta dele.
>
> Esse 'em volta' tem um nome: harness. E o harness é o CMV control da sua operação de IA.
>
> Hoje vocês vão entender o que é — e vão construir o próprio."

**Dados de apoio:**
- Preço por token: queda de 280x em 2 anos (Gartner 2026)
- Gasto total com IA: +320% no mesmo período
- 88% dos projetos de IA não chegam em produção
- 65% das falhas = harness defects (Context Drift, Schema Misalignment, State Degradation)
- Harness com KV-cache reduz custo de $3,00/MTok para $0,30/MTok sem trocar o modelo — 10x de margem

---

### Bloco 1.5 — A Equação e o Mental Model (3 min)

**O que acontece:** Felipe ancora o mental model com duas imagens antes de mostrar qualquer ferramenta. Essas imagens vão servir de referência ao longo de toda a live.

> 📌 **Abrir agora:** [[Claude Code — Arquitetura das Camadas.canvas]]

**Imagem 1 — A equação:**

> *"{Agente} = {Modelo} + {Harness}"*

"O modelo é a commodity. Todos usam o mesmo GPT, o mesmo Claude, o mesmo Gemini. A vantagem competitiva está no harness — no que você construiu em volta."

**Imagem 2 — O computador:**

> *"O LLM é o CPU. A janela de contexto é a RAM. O harness é o Sistema Operacional."*

| Computador | Harness de IA |
|---|---|
| CPU | LLM — executa raciocínio, stateless |
| RAM | Janela de contexto — memória da sessão |
| BIOS / Firmware | `_core/` — Layer 0: regras globais, schemas, segurança, hierarquia |
| Sistema Operacional | Harness — gerencia I/O, memória, identidade dos agentes |
| Programas | Skills — comportamentos encapsulados |
| Drivers | MCP — conecta ao mundo externo |
| Processos batch/cron | Workers (VPS) — rodam **fora** do SO, paralelos, sem Claude |

"Antes do SO, programadores escreviam direto em código de máquina. Trabalhoso, frágil, dependente de quem estava operando. Prompt engineering é exatamente isso — instrução direta ao modelo sem abstração. O harness é o SO que abstrai essa complexidade."

**O futuro** (1 frase): "Daqui pra frente, o harness vai se tornar o sistema nervoso central da empresa automatizada — um Control Plane que combina CI/CD + gestão de identidade + observabilidade para uma força de trabalho digital. Quem não construir isso vai ficar preso no prompt engineering para sempre."

---

### Bloco 1.5b — 3 Defects (transição para o demo)

> 📌 **Trocar canvas:** [[3 Defects do Harness.canvas]]

*Mostrar antes do demo. Leva 1 min — ancora por que 65% falham antes de mostrar o que funciona.*

---

### Bloco 2 — O Destino (8 min)

> 📌 **Canvas:** [[Claude Code — Arquitetura das Camadas.canvas]] — voltar pra este durante o demo
> 💻 **Abrir IDE:** Claude Code em pd-framework/stamper/ — mostrar o sistema real rodando

**O que acontece:** agora sim o demo. O aluno já sabe o que está olhando — a equação na mente, o modelo mental do SO.

**Script de transição:**

> "Então como é esse SO de IA rodando em produção? Vou mostrar. Isso aqui é o PD Framework — o sistema que opera a empresa onde trabalho. 11 squads, memória viva, automações, agentes especializados por área. Cada peça tem nome. Vocês vão reconhecer tudo ao final dessa live."

**O que mostrar na demo:**
1. Stamper (orquestrador) recebendo uma solicitação
2. STATE.md de um squad sendo lido — o agente sabe onde parou
3. Skill disparando com `/nome`
4. Hook rodando automaticamente em background
5. "Isso foi construído com Claude Code. Não é mágica — são peças. Vou desmontar cada uma agora, e vocês vão montar juntos comigo."

---

### Bloco 3 — Montando o Quebra-cabeça (55 min)

> 📌 **Trocar canvas:** [[Quebra-cabeça — 9 Peças do Harness.canvas]] — manter aberto até o fim do bloco

**O que acontece:** Felipe e aluno constroem juntos. Cada peça é introduzida como solução de um problema, mostrada no PD Framework real, e construída ao vivo. O quebra-cabeça cresce na tela.

> 💻 **Trocar diretório no IDE:** criar pasta nova (ex: meu-harness/) e abrir Claude Code nela — a partir daqui o aluno acompanha ao vivo

**Dinâmica de cada peça:**
1. **Problema** — "sem essa peça, o que acontece?" (30s)
2. **Conceito** — nome + função em uma frase (30s)
3. **No PD Framework** — mostrar a peça real (1 min)
4. **Construir** — aluno acompanha e replica (3-5 min)
5. **"Peça encaixada."** — visual do quebra-cabeça crescendo

---

#### Peca 1 — CLAUDE.md (8 min)

**Problema:** "Abro o Claude Code agora. Ele não sabe quem é, o que faz, o que não pode tocar. Cada sessão começa do zero. Minha empresa tem jeito de trabalhar — ele não sabe nenhum desses jeitos."

**Conceito:** CLAUDE.md = manual operacional do agente. Carregado automaticamente em toda sessão. É o contrato de trabalho: quem é, o que faz, o que não faz.

**Cascata de carregamento:**
- `~/.claude/CLAUDE.md` → global, sempre
- `projeto/CLAUDE.md` → quando cwd é o projeto
- `squad/CLAUDE.md` → quando cwd é o squad

**Analogia:** manual da cozinha. Todo chef que entrar nessa cozinha vai operar da mesma forma.

**Construir ao vivo:**
```
meu-harness/
  CLAUDE.md   <- criar agora
```
Conteúdo mínimo: nome do agente, tom, 3 regras do projeto, o que não faz.

**Testar:** abrir Claude Code no diretório — ver o agente responder com a persona definida.

---

#### Peca 2 — STATE.md (6 min)

**Problema:** "Fechei o Claude Code ontem no meio de um trabalho. Hoje abri de novo. Ele não sabe nada do que estava em andamento. Tenho que recontar tudo."

**Conceito:** STATE.md = memória viva. O CLAUDE.md define quem é o agente (imutável). O STATE.md registra o que está acontecendo agora (atualizado a cada sessão).

```
SOUL.md    → constituição da empresa (não muda)
CLAUDE.md  → contrato de trabalho do agente (muda raramente)
STATE.md   → quadro do standup de hoje (muda todo dia)
```

**Estrutura L1/L2/L3:**
- **L1** — Status atual: o que está em andamento hoje (máx 3 linhas)
- **L2** — Em progresso: tarefas com contexto e próximos passos
- **L3** — Backlog: próximas issues priorizadas

**Os 3 arquivos de memória do squad:**
| Arquivo | O que registra | Frequência |
|---|---|---|
| `STATE.md` | O que está acontecendo agora | Toda sessão |
| `decisions.md` | O que foi decidido e por quê | Por decisão não-trivial |
| `gotchas.md` | Armadilhas técnicas: sintoma / causa / solução | Por falha recorrente |

**Construir ao vivo:**
```
meu-harness/
  CLAUDE.md
  memory/
    STATE.md      <- criar agora
    decisions.md  <- append-only (vazio até primeira decisão)
    gotchas.md    <- catálogo de armadilhas (vazio até primeira falha)
```

---

#### Peca 3 — Squad (5 min)

**Problema:** "Tenho um agente com identidade e memória. Mas preciso de agentes diferentes para áreas diferentes — comercial, produto, dev. Um generalista que faz tudo não escala."

**Conceito:** squad = agente especializado com CLAUDE.md próprio (persona + escopo), STATE.md próprio (memória do domínio) e skills próprias.

**Analogia:** estação especializada da cozinha. O churrasqueiro não faz confeitaria. Cada um domina seu domínio.

**Construir ao vivo:**
```
meu-harness/
  CLAUDE.md           <- orquestrador global
  squads/
    meu-squad/
      CLAUDE.md       <- persona do squad
      memory/
        STATE.md      <- memória do squad
```

**Testar:** abrir cwd em `squads/meu-squad/` — persona diferente do orquestrador global.

---

#### Peca 4 — Skill /status (8 min)

**Problema:** "Tenho STATE.md. Mas toda vez que quero um resumo do que está em andamento, formulo o pedido do zero. Como encapsulo esse comportamento para invocar sempre igual?"

**Conceito:** skill = comportamento encapsulado e reutilizável, invocável com `/nome`. Arquivo Markdown com instruções estruturadas.

**Estrutura:**
```
skills/
  status/
    SKILL.md   <- objetivo + passos + inputs + outputs
```

**Construir ao vivo:**
Criar skill `/status` que:
1. Lê `memory/STATE.md` do squad atual
2. Reporta: o que está em andamento, o que está bloqueado, qual o próximo passo
3. Formato fixo — output previsível toda vez

**Invocar:** `/status` — ver o agente ler o STATE e reportar o panorama.

---

#### Peca 5 — Hook (8 min)

**Problema:** "Toda vez que começo a trabalhar, preciso criar uma branch. Toda vez que termino, preciso fazer commit e merge. São sempre as mesmas ações — e esqueço metade das vezes."

**Conceito:** hook = script que dispara automaticamente em eventos do agente. Roda sem pedir.

**Tipos:**
- `PreToolUse` — antes de executar uma ferramenta
- `PostToolUse` — depois de executar
- `Stop` — quando o agente encerra a sessão
- `UserPromptSubmit` — quando o usuário envia mensagem

**Analogia:** processos automáticos da cozinha. Fogão desliga sozinho ao fechar. Louça vai pra máquina. O sistema roda — o chef não precisa lembrar.

**Construir ao vivo:**
```
.claude/
  settings.json   <- configurar hook simples
```
Hook `Stop` que escreve timestamp de encerramento no STATE.md.

**Mostrar no PD Framework:** hook cria session branch ao primeiro Edit, hook faz merge+commit ao Stop.

---

#### Peca 6 — MCP (+ nota sobre Workers) (conceitual + demo, 10 min)

**Problema:** "Preciso que meu agente acesse o Linear, atualize o CRM, leia o Supabase. Mas não quero escrever código de integração toda vez."

**Conceito 1 — MCP:** protocolo que conecta o agente diretamente ao serviço em tempo real, dentro da sessão. O "USB-C" da IA — padrão universal.

**Conceito 2 — Workers:** scripts Python que rodam na VPS de forma autônoma, 24/7, **sem Claude**. Para tarefas determinísticas — só execução.

> ⚠️ **Workers não são uma layer do harness.** Rodam em paralelo ao Claude Code, fora do harness, acionados por cron ou fila. O harness e os workers se comunicam via STATE.md ou banco — mas são sistemas separados. Confundir os dois é o erro mais comum ao escalar.

| Modo | Analogia | Quando usar |
|---|---|---|
| **MCP** | Chef com câmera direto no fornecedor | Sessão interativa |
| **CLI** | Painel de controle dos equipamentos | Ação rápida no terminal |
| **API** | Fornecedor que entrega quando você liga | Worker autônomo na VPS |

**Demo no PD Framework:** Linear MCP criando issue em tempo real, worker processando leads no CRM sem supervisão.

*(Não construir ao vivo — conceitual. Implementação é conteúdo de live futura.)*

---

#### Peca 7 — Permissões e settings.json (5 min)

**Problema:** "Meu agente está operando bem. Mas e se ele deletar um arquivo que não devia? Ou fizer um deploy que não estava pronto?"

**Conceito:** settings.json controla o que o agente executa automaticamente vs. o que pede confirmação explícita.

**Operações que exigem confirmação:**
- Deletar arquivos / registros
- `git reset --hard`, `git push --force`
- DROP table em banco
- Deploy em produção

**Analogia:** o que precisa de assinatura do chef antes de sair da cozinha.

**Mostrar:** configuração de permissions no settings.json. Diferença entre `allow`, `ask` e `deny`.

---

### Bloco 4 — Quebra-cabeça Montado + HIVE (12 min)

> 📌 **Trocar canvas:** [[Evolução do Harness — 4 Estágios.canvas]]

**Script de fechamento:**

> "Vocês acabaram de montar o esqueleto. CLAUDE.md, STATE.md, squad, skill, hook. Cada peça resolve um problema específico. Juntas, elas formam um sistema que trabalha — não só responde perguntas.
>
> Esse é exatamente o padrão que está por baixo do PD Framework. A diferença entre o que vocês montaram hoje e o que eu mostrei lá no início é só uma coisa: tempo e contexto.
>
> E por falar nisso — vocês não precisam começar do zero."

**Apresentação do HIVE:**
- O que é: versão pública e genérica do PD Framework, open source
- O que tem: 11 squads, memória estruturada, 9 hooks, skill `/hive-setup` de onboarding
- Repo: https://github.com/felipeluissalgueiro/hive
- Landing: https://hive.cadencia.ia.br
- Como usar: `git clone` + `/hive-setup` — personalizado em menos de 10 minutos

> "Vocês construíram o esqueleto. O HIVE é o edifício inteiro — 11 squads, memória, hooks, workers — pronto pra personalizar pra sua empresa. É o mesmo framework que a PD usa. E agora vocês entendem cada peça."

---

### Bloco 5 — Q&A (20 min)

> 📌 **Canvas de referência:** [[Glossário Harness de IA.canvas]] — abrir quando surgir dúvida de terminologia

- Perguntas abertas sobre o que foi construído
- "Onde encaixo isso no meu projeto atual?" — Felipe responde casos reais
- Prévia das próximas lives: construção de produto real usando o harness como base
- Como continuar: HIVE + comunidade

---

## Resultado esperado ao final da live

1. **Mental model** — entende a equação {Agente} = {Modelo} + {Harness} e por que o harness é o CMV da operação de IA
2. **Vocabulário** — sabe nomear cada peça de qualquer harness que encontrar (Cursor, Windsurf, frameworks customizados)
3. **Esqueleto funcional** — CLAUDE.md + squad + STATE.md + skill + hook rodando na própria máquina
4. **HIVE** — harness completo para clonar e expandir imediatamente
5. **Direção** — sabe o próximo passo: usar o HIVE como base e construir produto nas próximas lives

---

## Materiais de referência

- [[Claude Code — Arquitetura das Camadas.canvas]] — canvas com todas as peças do harness
- [[O que é um harness]] — definição técnica + analogia da cozinha completa
- [[Por que o harness é urgente — custos de inferência]] — dados que sustentam o gancho CMV

## Notas Relacionadas
[[Status]] - [[Skill]] - [[Skills]]
