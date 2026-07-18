---
title: Checklist Briefing — Treinamento Claude Code 30d
tags: [cs, canon]
criado: 2026-06-12
origem: sessão Vayne Saccaro (primeiro aluno executado com esse padrão)
produto: Treinamento Prático Claude Code 30 dias
---

# Checklist de Briefing — Treinamento Claude Code 30d

> Doc constitutivo. Usado na Fase 3 do `playbook-treinamento-claude-code-30d.md` (call de briefing, sexta-feira D+5). Garante que Felipe entra na call com contexto pleno e sai com MVP definido, datas fechadas e aluno configurado.
>
> **Origem:** padrão extraído do briefing do Vayne Saccaro (12/06/2026) — primeiro aluno executado com esse roteiro completo.

---

## Pré-call (preparar antes de entrar)

- [ ] Ler respostas do Tally `KYGZDM` (form pré-briefing 7 seções)
- [ ] Pesquisa rápida sobre o cliente do aluno (site, redes, LinkedIn) — 15 min
- [ ] Criar issue PDL-XXX "Briefing — mapear contexto e definir MVP" com checklist no Linear
- [ ] Confirmar link da call no Calendar + enviado via WhatsApp
- [ ] Materiais S1 separados: template CLAUDE.md, exemplo PD Framework

---

## Contexto a extrair do Tally antes da call

Ao ler o form do aluno, mapear:

| Dimensão | O que extrair |
|---|---|
| **Perfil** | Consultor? Dev? Empreendedor? Transição? |
| **Faturamento IA atual** | Zero / até R$2k / R$2-5k / R$5-10k / +R$10k |
| **Clientes pagando** | Nenhum / 1-2 / 3-5 / +5 |
| **Stack** | Quais ferramentas usa + nível declarado |
| **Experiência com código** | Nunca / experimentou / tem fluência |
| **Caso-base** | Quem é o cliente, qual a dor principal |
| **Prazo** | Tem data? Urgência sem data? Só portfólio? |
| **Tentativas anteriores** | O que já tentou e não funcionou |
| **Objetivo final** | O que precisa ter acontecido pra "valer cada centavo" |
| **Maior receio** | Qual a objeção interna que pode travar o aprendizado |
| **Dedicação** | Horas/semana disponíveis fora das sessões ao vivo |

> ⚠️ Se o aluno não preencheu o Tally até 24h antes: cobrar via WhatsApp. Sem preenchimento até a manhã do briefing = avaliar remarcar (regra CS — adesão 100%).

---

## Estrutura da call (2h)

### Bloco 1 — Setup técnico (5min, antes de começar)

- [ ] Claude Pro contratado? (claude.ai — plano $20/mês)
- [ ] Claude Code instalado no terminal? (se não: instalar ao vivo — não bloqueia o briefing)
- [ ] Aluno tem autorização do cliente para usar dados da empresa no treinamento?

---

### Bloco 2 — Apresentação mútua (10min)

- [ ] Felipe se reapresenta como mentor (vai trabalhar junto, não é palestrante)
- [ ] Aluno conta trajetória em 2-3 min: de onde vem, o que fazia antes
- [ ] Validar perfil declarado no Tally
- [ ] Confirmar motivação real: "o que te levou a apostar nessa transição agora?"

---

### Bloco 3 — Mapeamento do caso real (40min)

**Objetivo: entender o contexto do cliente do aluno em profundidade.**

- [ ] Quem é o cliente (segmento, tamanho, localidade)
- [ ] Qual o problema principal (em palavras do próprio aluno)
- [ ] O cliente sabe que vai ser o case-piloto?
- [ ] Quais acessos o aluno tem hoje? (CRM, redes, base de dados, APIs)
- [ ] O que já existe de automação/sistema? (quem fez? funciona?)
- [ ] O que já foi tentado e não funcionou?

> **⚠️ Risco de escopo:** alunos geralmente chegam com múltiplas dores de um cliente. Fechar em 1 MVP aqui — não tentar resolver tudo em 30 dias.

**Ao final do bloco, Felipe escolhe com o aluno 1 MVP:**

| Critério do bom MVP |
|---|
| Resolve 1 dor real e urgente do cliente |
| Demonstrável ao cliente em 30 dias |
| Viável com stack do aluno + habilidades a desenvolver |
| Tem critério claro de "feito" (ex: "agente responde lead em <1min sem intervenção humana") |

---

### Bloco 4 — Definição do MVP (30min)

**Saída obrigatória deste bloco:**

- [ ] **Nome do sistema** (ex: "Agente de Atendimento Plug and Charge")
- [ ] **O que faz** (1 frase objetiva)
- [ ] **O que NÃO faz** (limites explícitos)
- [ ] **Critério de feito** em 30 dias (mensurável)
- [ ] **Onde vai rodar** (local / VPS / Vercel / n8n ainda?)

**Abordar receios técnicos comuns:**
- *"Não sei Python/Linux"* → O objetivo não é dominar a linguagem — é usar Claude Code pra fazer o código funcionar. Linux aparece só no deploy (S4), resolvemos juntos.
- *"Não sei se consigo em 1 mês"* → Vamos focar em 1 coisa só que funcione de verdade. 30 dias para 1 MVP real vale mais do que 30 dias tentando fazer tudo.

---

### Bloco 5 — Setup técnico ao vivo (30min)

- [ ] Instalar Claude Code (se ainda não instalado)
- [ ] Criar pasta de trabalho do treinamento
- [ ] Criar primeiro `CLAUDE.md` com contexto do caso real do aluno
- [ ] Mostrar diferença prática: "prompt no chat" vs "Claude Code com contexto persistente"
- [ ] Aluno sai com algo rodando — mínimo: CLAUDE.md lendo o contexto e gerando um resumo do caso

---

### Bloco 6 — Cronograma e expectativas (10min)

**Datas (confirmar com o aluno — ele é flexível ou tem restrições?):**

| Sessão | Semana | Foco |
|---|---|---|
| S1 | Semana 1 (D+7) | Setup, CLAUDE.md, fundamentos |
| S2 | Semana 2 (D+14) | PRD, núcleo da solução, primeira skill |
| S3 | Semana 3 (D+21) | MCPs, APIs, integrações |
| S4 | Semana 4 (D+28) | Deploy, documentação, pitch comercial |

- [ ] Confirmar dia e horário de cada sessão
- [ ] Criar 4 eventos no Google Calendar + enviar convite pro aluno
- [ ] Explicar regras do suporte WhatsApp:
  - Canal direto com Felipe, 30 dias a partir da S1
  - SLA 24h úteis (não é plantão)
  - O que mandar: dúvidas + screenshots + logs de erro
  - O que não mandar: voz / mensagens sem contexto
- [ ] Confirmar bônus do contrato (Cadência 30d + outro específico do deal)

---

## Saída obrigatória — conferir antes de encerrar a call

- [ ] Caso-base documentado no projeto Linear do aluno (nome sistema + o que faz + critério de feito)
- [ ] Datas S1-S4 criadas no Google Calendar
- [ ] Claude Code instalado (ou confirmado pra instalar antes da S1)
- [ ] Ata da call criada via `/ata-reuniao`
- [ ] Issue "Briefing" do projeto Linear → `Done`
- [ ] Issue S1 → `Todo` (próxima ação imediata do aluno)
- [ ] Acesso Cadência 30d liberado pro aluno (Felipe faz após a call)
- [ ] STATE CS atualizado com status do aluno

---

## Flags de risco comuns (checagem ao ler o Tally)

| Sinal no Tally | Risco | Como tratar |
|---|---|---|
| Aluno listou 3+ dores do cliente | Escopo aberto demais | Fechar 1 MVP no Bloco 3 — não tentar resolver tudo |
| Aluno "nunca escreveu código" | Pode subestimar a curva | Calibrar expectativa no Bloco 4 — Claude Code nivela isso |
| Aluno não tem cliente real | Motivação pode cair na S2-S3 | Identificar caso hipotético forte ou incentivar prospectar 1 cliente antes da S1 |
| "Menos de 2h/semana" de dedicação | Risco de não entregar o MVP | Ser direto: 2h/semana não fecha MVP em 30 dias — renegociar ou ajustar escopo |
| Prazo rígido do cliente | Pressão pode travar o aprendizado | Definir MVP realista considerando o prazo no Bloco 4 |
| Claude Pro não contratado | Bloqueia S1 | Cobrar via WhatsApp antes da call. Orientar instalação ao vivo se necessário |

---

## Como gerar checklist personalizado para cada aluno

Antes do briefing, criar arquivo em `times/cs/onboarding/context/<nome-aluno>-briefing-checklist.md` com:
1. Tabela de contexto preenchida com respostas do Tally
2. Radiografia técnica (stack + nível + experiência com código)
3. Caso-base detalhado (word-for-word do form)
4. Flags de risco identificados especificamente para aquele aluno
5. Seção de saída obrigatória

Atualizar a issue "Briefing" do projeto Linear do aluno com o checklist personalizado.

**Exemplo de execução:** `times/cs/onboarding/context/vayne-saccaro-briefing-checklist.md`

---

---

## Lições do primeiro encontro — Vayne Saccaro (12/06/2026)

> Primeira execução real deste playbook. 2h35min ao vivo. O que aprender para as próximas turmas.

### O que funcionou

**Demo do produto ao vivo (Cadência) no briefing é altamente eficaz.** Vayne visualizou valor imediatamente e surgiu oportunidade de parceria (white label para o cliente do aluno). Replicar com todo aluno que tem cliente-caso — abrir Cadência, buscar o CNPJ do cliente dele, mostrar enriquecimento de lead ao vivo.

**Extrair background antes de definir MVP.** Felipe perguntou "o que você fazia na consultoria que ninguém faz melhor do que você?" e descobriu 6 anos em vendas B2B industrial (GMB/Indisa). Isso abriu oportunidade de produto próprio que Vayne nem tinha mapeado. Fazer essa pergunta em todo briefing.

**Análogo concreto para cada conceito técnico.** Harness=rédea, N8N node=script Python, Redis=cache de videogame funcionaram. Vayne absorveu sem travar. Montar glossário de analogias para próximos alunos com background não-técnico.

**Dar tarefas de fim de semana concretas.** Vayne saiu com lista exata do que fazer antes da S1. Isso cria comprometimento imediato e reduz a chance de chegar na S1 sem progresso.

### O que não funcionou

**Briefing virou "aula 0" — 40min consumidos em setup técnico (PATH).** Acontece quando o aluno ainda não tem o ambiente configurado. Para próximas turmas: verificar via WhatsApp no dia anterior se Claude Code está funcionando no terminal. Se não estiver, resolver antes da call — não durante.

**MVP ficou aberto ao final.** Vayne saiu com 3 projetos simultâneos (semi-joias, SDR Plug and Charge, produto próprio). O Bloco 4 precisa de mais firmeza: Felipe fecha 1 MVP e nomeia os outros como "paralelos" — não são o projeto dos 30 dias.

**Datas S1-S4 não foram confirmadas durante a call.** Não deixar a call terminar sem datas no Calendar. Criar os 4 eventos ao vivo antes de encerrar.

**Kommo API ficou como tarefa aberta sem urgência explícita.** Vayne não sabe que a S3 trava sem o acesso. Na próxima turma com integração de CRM externo: deixar claro "sem isso a S3 não acontece — prazo para resolver: até segunda-feira da semana da S2."

### Adaptações para próximas turmas

| Aprendizado | Ação |
|---|---|
| Setup técnico pode consumir 40min | Checar via WhatsApp na véspera: `claude --version` no terminal. Se falhar: resolver antes da call |
| Briefing pode virar "aula 0" | Prever 30min de buffer. Se acontecer: documentar como aula 0 e ajustar datas (S1 uma semana depois) |
| Aluno lista múltiplas dores | Bloco 4 mais firme: fechar 1 MVP com nome + critério de feito antes de encerrar |
| Datas não confirmadas | Criar 4 eventos Calendar ao vivo antes de encerrar a call |
| Acessos críticos (APIs, CRMs) | Mapear no Bloco 3 quais acessos a S3 vai precisar + passar prazo explícito |
| Demo Cadência | Fazer em todo briefing com aluno que tem cliente-caso (5min, ao vivo, enriquecimento de lead do cliente) |

---

## Refs

- `playbook-treinamento-claude-code-30d.md` — Fase 3 (Briefing) é onde este doc é invocado
- `checklist-briefing.md` — checklist geral CS (para clientes de consultoria, não treinamento)
- Form Tally: `KYGZDM` (Briefing — Treinamento Prático Claude Code 30 dias)
- `times/produto/treinamentos/programar-com-ia/vayne-saccaro/sessoes/briefing.md` — ata completa da primeira execução
