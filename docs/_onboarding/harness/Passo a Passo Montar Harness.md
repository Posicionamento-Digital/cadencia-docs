---
date: 2026-06-03
tags: [nocode-startup, claude-code, harness, skill, roteiro]
moc: "[[NoCode Startup - Live-01- Harness-IA V2]]"
type: source
entities: ["[[Cadencia]]", "[[comercial]]", "[[financeiro]]", "[[marketing]]"]
---
# Passo a Passo — Montando um Harness 

> Roteiro interativo que o Stamper segue ao vivo durante a live.
> Cada peça: **explica o problema → dá opções → cria o arquivo → mostra o resultado.**
> Base para a skill `/montar-harness`.

---

```
╔══════════════════════════════════════════════════════════════╗
║           MONTANDO UM HARNESS — PASSO A PASSO               ║
║                    (roteiro do Stamper)                      ║
╚══════════════════════════════════════════════════════════════╝

PEÇA 1 — A PASTA RAIZ
─────────────────────
Criar: meu-harness/
Stamper explica: "Aqui mora tudo. O cwd é o que define qual
agente está ativo. Mude a pasta, muda o agente."
Pergunta: "Como você quer chamar seu harness?"
→ Cria a pasta com o nome escolhido.

          │
          ▼

PEÇA 2 — CLAUDE.md (identidade)
────────────────────────────────
Criar: meu-harness/CLAUDE.md
Stamper explica: "Esse arquivo é o contrato de trabalho do
agente. Ele lê isso em toda sessão. Sem isso, ele não sabe
quem é."
Perguntas:
  → "Qual o nome dessa IA? Como ela se apresenta?"
  → "O que ela faz? Descreva em 1 frase."
  → "O que ela NUNCA faz? (exemplos: deletar sem confirmar,
     inventar dados, responder fora do escopo)"
  → "Tem regras de tom? (formal, direto, técnico, amigável)"
Opções de estrutura:
  A) Mínimo (persona + 3 regras) — para começar rápido
  B) Completo (persona + escopo + stack + regras + refs) — produção
→ Cria o CLAUDE.md com o que foi respondido.


          │
          ▼

PEÇA 1.5 — SOUL.md (alma do agente — opcional)
────────────────────────────────────────────────
Stamper pergunta: "Esse agente tem identidade forte — nome
próprio, voz de marca, referência cultural? Stamper é o Doug
Stamper de House of Cards. Cadência tem missão e valores.
Se o seu agente é só operacional, pulamos. Se tem
personalidade própria — criamos o SOUL.md."

  A) Tem identidade forte → criar SOUL.md
  B) É operacional → pular para STATE.md

Se A — Stamper explica: "O CLAUDE.md é o contrato de
trabalho. O SOUL.md é a constituição: missão, valores, voz.
Muda só se o propósito do agente mudar — o que é raro."

Perguntas:
  → "Qual a missão em uma frase? (o porquê de existir)"
  → "Quais os 3 valores que definem como ele age?"
  → "Tem referência cultural que captura a personalidade?"
  → "Como ele se apresenta — qual a primeira impressão?"

→ Cria SOUL.md com missão + valores + referência + voz.
          │
          ▼

PEÇA 3 — memory/STATE.md (memória viva)
────────────────────────────────────────
Criar: meu-harness/memory/STATE.md
Stamper explica: "O CLAUDE.md define quem o agente é.
O STATE.md define o que está acontecendo agora. Sem isso,
cada sessão começa do zero."
Pergunta sobre COMO armazenar a memória:
  → "Que tipo de projeto é esse?"
     A) Projeto de produto (SaaS, app) — foco em issues abertas,
        bugs, decisões técnicas recentes
     B) Operação de empresa (comercial, CS, marketing) — foco em
        leads, clientes, tarefas do dia
     C) Pesquisa/estudo — foco em descobertas, hipóteses, fontes
     D) Uso pessoal — foco em metas, hábitos, pendências
Pergunta sobre COMO consumir a memória:
  → "Quem vai ler esse STATE.md?"
     A) Só o agente (automaticamente no início de cada sessão)
     B) O agente + eu (quero ver o STATE formatado quando abro)
     C) Vários agentes (squads diferentes precisam ver o estado)
Stamper cria o STATE.md com estrutura L1/L2/L3 adaptada
à escolha:
  [L1] Status atual — máx 3 linhas, o que está rolando hoje
  [L2] Em progresso — tarefas abertas com contexto
  [L3] Backlog — próximos passos priorizados

          │
          ▼

PEÇA 4 — settings.json (permissões e comportamento)
─────────────────────────────────────────────────────
Criar: .claude/settings.json
Stamper explica: "Esse arquivo define o que o agente executa
sozinho vs. o que ele para e pergunta antes. É o freio do
sistema."
Pergunta:
  → "Você quer que o agente execute comandos de terminal
     automaticamente?"
     A) Sim, confio — Bash: allow
     B) Depende — Bash: ask (pergunta antes de cada comando)
     C) Nunca — Bash: deny
  → "E para editar arquivos?"
     A) Pode editar livre — Edit: allow
     B) Sempre pede confirmação — Edit: ask
  → "Quer algum aviso antes de deletar?"
     → Delete: always ask (recomendado — Stamper já configura)
→ Cria settings.json com as escolhas.

          │
          ▼

PEÇA 5 — squads/ (especialização)
───────────────────────────────────
Criar: meu-harness/squads/nome-do-squad/
Stamper explica: "Um agente generalista não escala. Squads
são agentes especializados — cada um sabe só do seu domínio.
O orquestrador (esse CLAUDE.md raiz) delega pra eles."
Pergunta:
  → "Qual área você quer especializar primeiro?"
     Exemplos: comercial, produto, financeiro, conteúdo, dev
  → "Qual o nome da persona? (ex: Eduardo — Executivo Comercial)"
  → "O que esse squad faz que o orquestrador não faz?"
→ Cria a pasta do squad.
→ Cria o CLAUDE.md do squad com persona + escopo + o que NÃO faz.
→ Cria memory/STATE.md do squad (mesmo fluxo da Peça 3,
   mas scoped para o domínio).


          │
          ▼

PEÇA 5.5 — context/ e foundation/ (referência e processos)
────────────────────────────────────────────────────────────
Stamper explica: "O CLAUDE.md diz quem o agente é. O STATE.md
diz o que está acontecendo. Mas tem mais uma camada: o que
ele sabe consultar. Credenciais ficam onde? Quem são as
personas? Como é o processo de vendas? Sem isso, inventa.
Com isso, consulta."

  context/    → base de conhecimento
               (mapa de credenciais, perfil do usuário,
                personas, lista de clientes, briefings)
  foundation/ → playbooks e processos operacionais
               (como qualificar lead, como escrever
                relatório, checklist de entrega)

Perguntas:
  → "Tem referências que esse squad precisa consultar?"
  → "Tem processos ou playbooks que ele deve seguir?"
  → "Quer um mapa de credenciais? (onde buscar — nunca
     os valores em texto claro)"

→ Cria os arquivos com o conteúdo fornecido.
          │
          ▼

PEÇA 6 — skills/ (comportamentos encapsulados)
────────────────────────────────────────────────
Criar: meu-harness/squads/nome-do-squad/skills/status/SKILL.md
Stamper explica: "Skills são receitas. Você define uma vez,
invoca sempre igual com /nome. O agente executa os mesmos
passos toda vez — sem precisar repetir a instrução."
Pergunta:
  → "Qual comportamento você repete mais nesse squad?"
     Exemplos: resumo do que está em andamento, criar relatório,
     gerar rascunho de mensagem, atualizar status no CRM
  → "Como você quer invocar? (/status, /resumo, /relatorio...)"
  → "O que entra? O que sai?" (inputs e outputs)
→ Cria a skill com objetivo + passos + formato de saída.
→ Testa ao vivo: invoca /status → agente lê STATE.md e reporta.

          │
          ▼

PEÇA 7 — hooks (automação silenciosa)
───────────────────────────────────────
Criar: entrada em .claude/settings.json → hooks: {}
Stamper explica: "Hooks são o que roda sem você pedir. O
fogão que desliga sozinho. O commit que acontece ao fechar.
Você define uma vez — o sistema cuida para sempre."
Pergunta:
  → "O que você sempre esquece de fazer ao abrir uma sessão?"
     Exemplos: criar branch, verificar pendências, ler o STATE
  → "O que você sempre esquece ao fechar?"
     Exemplos: commitar, atualizar STATE.md, enviar resumo
  → "Tem algo que você quer que aconteça ANTES de qualquer
     ação do agente?"
     Exemplos: confirmar operações destrutivas, lookup de
     incidentes passados
Stamper sugere 3 hooks básicos para começar:
  A) Stop → atualiza timestamp no STATE.md ao encerrar
  B) PreToolUse → avisa antes de deletar qualquer arquivo
  C) UserPromptSubmit → relembra as regras do CLAUDE.md
→ Configura os hooks escolhidos no settings.json.

          │
          ▼

╔════════════════════════════════════════════════╗
║           HARNESS MÍNIMO FUNCIONAL             ║
║                                                ║
║  meu-harness/                                  ║
║    CLAUDE.md          ← identidade             ║
║    SOUL.md            ← alma (se aplicável)    ║
║    memory/STATE.md    ← memória viva           ║
║    .claude/           ← configuração           ║
║      settings.json    ← permissões + hooks     ║
║    squads/            ← especialização         ║
║      nome-squad/                               ║
║        CLAUDE.md      ← persona do squad       ║
║        memory/STATE.md                         ║
║        context/       ← base de conhecimento   ║
║        foundation/    ← playbooks e processos  ║
║        skills/status/ ← primeiro skill         ║
╚════════════════════════════════════════════════╝

          │
          ▼  (próximas lives)

EXPANSÃO
─────────
→ MCP: conectar Linear, Supabase, GitHub
→ Workers: scripts Python na VPS para tarefas autônomas
→ Squads adicionais por área
→ HIVE: clonar o framework completo como base
```

---

## Notas relacionadas

[[NoCode Startup - Live-01- Harness-IA V2]] · [[Claude Code — Arquitetura das Camadas]] · [[O que é um harness]]