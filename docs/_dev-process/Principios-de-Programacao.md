---
date: 2026-07-17
tags: [dev, principios, qualidade, dry, etc, ortogonalidade]
---

# Princípios de Programação

> Como escrevemos código na Cadencia — **não é preferência de estilo, é redução de risco real.**

Fonte única dos princípios que valem pra **qualquer código** da empresa (pd-framework, Cadencia,
projetos de cliente). Inspirado no **Programador Pragmático** (Hunt & Thomas) — Felipe lendo o
livro e aplicando o que aprende aqui, um princípio por vez. Cada princípio ganha sua seção nesta
página, não um arquivo por princípio (motivo: princípios são a mesma categoria de conhecimento;
espalhar em N arquivos recria o problema que o princípio §1 abaixo existe pra evitar).

**Status (decisão Felipe 2026-07-17):** DRY, ETC e Ortogonalidade são **princípios invioláveis**
do framework. Qualquer decisão de design/código/doc que os viole exige **justificativa explícita
registrada como ADR ou nota de decisão**; sem justificativa, é **bug de arquitetura** e deve ser
revertido. Reversibilidade e tracer bullets seguem como próximos candidatos, ainda não elevados a
inviolável.

**Complementa (não substitui) o dev workflow:** as regras operacionais completas de como
planejamos, codamos, revisamos e mergeamos vivem em [Processo de Desenvolvimento](Processo - Desenvolvimento (Time Dev).md),
[Como Trabalhamos](Como-Trabalhamos.md) e [Gestão de Projetos](Gestao-Projetos-Dev.md).
Esta página é a régua de **qualidade** que atravessa todas essas etapas: cada gate do workflow
(planejamento, review, close) checa se o código respeita os 3 princípios abaixo.

---

## 1. DRY — Don't Repeat Yourself

**Definição real (não é sobre código copy-paste):** todo conhecimento — uma regra de negócio, uma
decisão, uma estrutura, um mapeamento — deve ter **uma representação única, autoritativa e
inequívoca** no sistema. Duas cópias do mesmo conhecimento **vão divergir**; é questão de quando,
não de se.

Isso vale igual para:

- **Lógica/config** — a mesma regra escrita em 2 funções, 2 scripts, 2 mapeamentos
- **Documentação** — a mesma estrutura/decisão redigitada em 2+ arquivos `.md`
- **Templates/rubrics** — o mesmo critério (ex: severidade de review) copy-pasted entre skills

### Quando é violação

| Sinal | Exemplo real já corrigido/encontrado no framework |
|---|---|
| Mesma estrutura documentada em N arquivos sem geração | Árvore Time→Squad redigitada em `CONTEXT.md` + `_core/HIERARCHY.md` + `manual/` |
| Mesmo texto/narrativa mantido à mão em 2 formatos | Playbook Obsidian escrito "igual ao cadencia-docs" antes do fix — ver `_core/lib/cadencia_docs_to_playbook.py` (OPS-24) |
| Mesmo rubric/critério copy-pasted entre skills irmãs | P1/P2/P3 de severidade repetido em `claude-review`, `codex-review`, `gemini-review` |
| Import via manipulação de path em vez de módulo compartilhado | acopla lógica ao layout de pastas, não ao contrato da função |

### Como resolver (regra prática)

1. **Identifique a fonte única** — geralmente o dado/decisão mais "upstream" (o Canvas antes do
   Mermaid; o cadencia-docs antes do Playbook; `decisions.md` do Squad antes de qualquer doc que
   cite a decisão).
2. **Tudo o mais é derivado** — gerado por script, linkado, ou lido em runtime. Nunca copiado à
   mão.
3. **Se não dá pra gerar automaticamente ainda**, pelo menos linka pra fonte (`Ver X`) em vez de
   reescrever o conteúdo.
4. **Multiplicação × 2 é o limite de tolerância informal** — a mesma frase de regra de negócio
   aparecendo pela 2ª vez em prosa solta (não código) já é sinal de criar a fonte única antes da
   3ª.

### Exceções legítimas (não é DRY se...)

- **Camadas com audiência/altitude diferentes** — MD de componente (dev no repo) vs página
  cadencia-docs (qualquer um na empresa) cobrem o mesmo sistema em zoom diferente; isso é ok, não
  é duplicação de conhecimento, é **tradução de audiência**. A regra é: **o fato em si** (uma
  decisão, um número, um critério) não pode ter 2 fontes — a apresentação pode variar.
- **Aliases retrocompat finos** — `incidents-lookup.py`/`sessions-lookup.py`/`memory-lookup.py` só
  injetam um parâmetro e delegam pra `lookup.py`. Isso é o padrão certo (uma implementação, N
  pontos de entrada), não uma violação.

### Enforcement

- **Vitor (code review — `/claude-review`, `/codex-review`, `/gemini-review`, `/dual-review`):**
  ao revisar, checar se a lógica/config/doc nova reaproveita uma fonte existente ou cria uma 2ª
  cópia. **P2** se a duplicação é de lógica/config; **P3** se é só doc/prosa (a menos que já tenha
  causado bug real — aí sobe pra P1/P2).
- **`/documentar-software` (Paula) e `/documentar-processos`:** Passo 1 já manda checar
  `decisions.md` do Squad "para não duplicar" — mesma régua vale para as 4 camadas entre si (não
  reescrever o mesmo texto em MD de componente + cadencia-docs + Playbook + Obsidian; gerar ou
  linkar).
- **Antes de criar arquivo/script novo:** `grep`/`lookup.py` pela lógica que você está prestes a
  escrever — se já existe versão parecida em outro squad/script, reusar ou extrair, não recriar.

---

## 2. ETC — Easier To Change

**Definição:** o **meta-princípio** que está atrás de DRY, ortogonalidade e reversibilidade. Toda
decisão de design se julga pela mesma pergunta: **isso torna o sistema mais fácil ou mais difícil
de mudar depois?** Acoplamento apertado, configuração cravada no código, decisão que "vazou" pra
muitos lugares — tudo isso é ETC violado, mesmo sem duplicação de conhecimento (isso seria DRY).

### Quando é violação

| Sinal | Exemplo real já encontrado no framework (OPS-28) |
|---|---|
| Path/config de máquina cravado no código-fonte | Paths `C:\Users\felip\...` hardcoded em 17+ arquivos (`_shared/obsidian_client.py` e outros) — trocar de máquina ou adicionar 2º operador quebra silenciosamente. Corrigido em OPS-29 via `_core/_pd_paths.py` (env override → fallback). |
| IDs/config de serviço externo cravados como constante | `TEAM_CAD_ID`/`FELIPE_ID` hardcoded em `_shared/linear_client.py`, duplicado em 2 arquivos-fonte — trocar de workspace Linear exige caçar e editar manualmente. |
| Decisão arquitetural sem camada de reversão | Migração GHL→CRM Cadencia sem feature-flag viva (rollback cancelado, CAD-588) — troca de provedor virou reescrita direta em vez de swap atrás de interface. |
| Acoplamento temporal implícito | Merge automático do hook `Stop` depende de instrução em prosa ("nunca rode X manualmente"), não de trava verificável em código. |

### Como resolver

1. Toda decisão que amarra o sistema a **uma máquina, um workspace externo, um provedor
   específico** deve passar por uma camada (env var, config, interface) entre a decisão e quem a
   usa — nunca a decisão espalhada em N arquivos como constante.
2. **Interface estável, implementação variável:** um módulo expõe contrato (função/CLI/schema) que
   esconde o "como" — trocar a implementação não deveria quebrar quem consome.
3. **Decisão reversível > decisão definitiva**, quando o custo de manter a reversão é baixo
   (feature flag, camada de abstração fina). Se a reversão for cancelada conscientemente,
   documentar o porquê (não deixar como dado morto sem explicação).

### Exemplos já corretos no framework (usar como referência)

- `_core/lib/squad_resolver.py` — estrutura de squad = editar 1 JSON, não código
- `_core/state-aggregator.py` — detecta Squad por presença de `CLAUDE.md`, não lista hardcoded
- `_core/_pd_paths.py` — resolve raiz do repo por env → filesystem → git, funciona em qualquer
  máquina

### Enforcement

- Mesmo ponto do DRY: Vitor no code review, cascata Linear (`/linear-planejar-issue`,
  `/linear-close-issue`) — ao planejar/fechar, perguntar **"essa decisão amarra o sistema a algo
  externo específico? existe camada entre ela e quem consome?"**.
- Auditoria completa (achados + issues de correção): OPS-28 (veredito), OPS-29/30/31/32 (sub-issues).

---

## 3. Ortogonalidade

**Definição:** dois componentes são ortogonais quando mudar um **não afeta** o outro. O sistema
inteiro é ortogonal quando você consegue mudar qualquer peça sem cascatear reescrita em outras
peças sem relação óbvia. É a propriedade que faz o sistema **absorver mudança sem se despedaçar**
— e é uma das três razões pelas quais ETC funciona (junto com DRY e reversibilidade).

**Não confundir com modularidade.** Módulo separado pode continuar acoplado (mudar A obriga a
mexer em B mesmo eles estando em arquivos/pastas diferentes). Ortogonalidade é a **ausência de
acoplamento cruzado**, não a presença de fronteira física.

### Quando é violação

| Sinal | Exemplo real já encontrado no framework |
|---|---|
| Mudança em um lugar cascateia em N sem relação óbvia | Adicionar Squad novo obrigava editar 3+ arquivos hardcoded antes de `_core/lib/squad_resolver.py` centralizar (OPS-28 §resolver) |
| Função/módulo faz mais de uma coisa não-relacionada | Skill que mistura "coletar input" + "chamar API externa" + "gerar doc" — mudar o formato do doc quebra a chamada da API |
| Duas features compartilham estado mutável escondido (variável global, arquivo, env var não-declarada) | Env var `SUPABASE_ACCESS_TOKEN` stale sombreando o mapa 1P (DEV-1164) — mudar setup do corpus quebrou skills de Cadencia sem sinal de causa |
| Mistura de camadas — apresentação puxando lógica de negócio direto do banco, ou lógica de negócio conhecendo formato de UI/saída | Skill que gera markdown com regra de negócio embutida (mudar layout do markdown vira debate sobre a regra) |
| "Ah, mas se eu mexer aqui, tenho que ir lá também" — dito em voz alta durante refactor | **Sinal humano canônico** de acoplamento. Não é sobre paranoia; é sinal a registrar |

### Como resolver

1. **Uma responsabilidade por componente.** Se você precisa de duas frases pra descrever o que uma
   função/módulo/skill faz e uma delas usa "e", provavelmente é duas coisas — separe.
2. **Estado explícito, não escondido.** Parâmetros e retornos > variáveis globais, arquivos
   partilhados, env vars não-declaradas. Se dois componentes precisam trocar dado, o contrato deve
   ser visível na assinatura.
3. **Camadas com direção clara.** Lógica de negócio não conhece formato de saída; saída não
   conhece lógica de negócio. Testes ficam triviais quando as camadas são ortogonais.
4. **Teste de estresse mental: "e se eu trocar X?"** — se a resposta é "quebra Y e Z sem relação
   óbvia", ortogonalidade violada. Se é "só quem consome X precisa se adaptar via contrato", ok.

### Exemplos já corretos no framework (usar como referência)

- `_core/lib/squad_resolver.py` — adicionar Squad = editar 1 JSON, zero código
- `_core/state-aggregator.py` — detecta Squad por presença de `CLAUDE.md`, não lista hardcoded
- `_shared/*_client.py` (`evo_client`, `calcom_client` etc.) — cada cliente conhece só sua API;
  skills consomem via contrato, não sabem o transporte
- Hooks `PreToolUse`/`Stop` — cada hook faz uma coisa; ativar/desativar hook X não afeta hook Y

### Enforcement

- **Vitor (code review):** ao revisar, aplicar o teste **"e se eu trocar X?"** — se a mudança
  proposta amarra dois componentes que hoje são independentes, exigir justificativa ou refactor.
  **P2** se cria acoplamento novo entre módulos que deveriam ser independentes; **P1** se
  reintroduz acoplamento que já foi corrigido antes (regressão de decisão).
- **`/linear-planejar-issue`:** no gate Vitor (análise profunda), incluir *"essa feature acopla
  componentes hoje independentes? se sim, por quê e qual a alternativa?"*.
- **Refactor drift:** frase *"se eu mexer aqui, tenho que ir lá também"* dita durante trabalho é
  gatilho pra registrar débito ortogonal — vira issue de refactor, não é ignorado.

---

## Como se encaixa no dev workflow

Os 3 princípios são **checkpoints obrigatórios** em cada etapa do fluxo dev:

| Etapa do workflow | Checkpoint dos princípios |
|---|---|
| **Planejamento** (`/linear-planejar-issue`, gate Vitor) | "Essa feature: (a) reaproveita fonte existente ou cria cópia? (b) amarra o sistema a algo externo específico? (c) acopla componentes hoje independentes?" |
| **Codar** (Amélia babysitting, Modo A/B) | Antes de criar arquivo/script novo, `grep`/`lookup.py` pela lógica. Interface antes de implementação. Uma responsabilidade por componente. |
| **Review** (`/claude-review`, `/codex-review`, `/gemini-review`, `/dual-review`) | Rubric P1/P2/P3 aplicado aos 3 princípios (ver Enforcement de cada seção acima) |
| **Close** (`/linear-close-issue`, gate Amélia) | Se algum princípio violado sem justificativa registrada, close é bloqueado |
| **Doc** (`/documentar-software`, `/documentar-processos`) | DRY§1 explícito: gerar ou linkar, nunca reescrever à mão |

Regras operacionais completas: [Processo de Desenvolvimento](Processo - Desenvolvimento (Time Dev).md),
[Gestão de Projetos](Gestao-Projetos-Dev.md), [PR & Deploy Vercel](Processo - PR e Deploy na Vercel.md).

## Refs técnicas

- **Fonte de código operacional (agentes/devs no pd-framework):** `_core/CODING-PRINCIPLES.md`
- **Enforcement:** gate de code review (`_core/DEV-WORKFLOW.md` §15) + cascata Linear
  (`/linear-planejar-issue`, `/linear-close-issue`)
- **Princípio irmão:** `_core/CODE-COMMENTS.md` (comentários = porquê; DRY = uma fonte de
  verdade)
- **Resumo tático do Time Dev (Clean Code, Martin — KISS/YAGNI/naming/segurança):**
  `times/dev/foundation/code-principles.md` §2 (linka pra cá em vez de duplicar tratamento
  completo — é o próprio §1 aplicado)
- **Exemplo aplicado:** geração automática do Playbook Obsidian a partir desta mesma fonte
  (`_core/lib/cadencia_docs_to_playbook.py`)
- **Livro:** *O Programador Pragmático*, Hunt & Thomas
  - cap. "The Evils of Duplication" (DRY)
  - cap. "The Essence of Good Design" (ETC)
  - cap. "Orthogonality" (Ortogonalidade)

## Histórico

- **2026-07-11** — versão inicial, seção §1 (DRY). Origem: OPS-24 (fix Playbook/cadencia-docs) +
  OPS-25 (codificação do princípio). Projeto Linear: `ops: Programador Pragmático — aplicação na
  empresa`.
- **2026-07-11** — seção §2 (ETC). Origem: OPS-28 (auditoria) + correções em OPS-29 (paths
  hardcoded). Achada e corrigida sobreposição não-intencional com
  `times/dev/foundation/code-principles.md` §2 (mesma duplicação que o princípio §1 pune —
  cross-referenciado em vez de reescrito).
- **2026-07-17** — seção §3 (Ortogonalidade) + elevação dos 3 (DRY, ETC, Ortogonalidade) a
  **princípios invioláveis** do framework. Origem: decisão Felipe na sessão de design do identity
  layer multi-tenant (repo próprio pro Renan) — a escolha entre "1 repo compartilhado com
  sparse-checkout" e "N repos por tenant" foi decidida por ortogonalidade + DRY, o que gerou a
  necessidade de registrar os princípios como regra dura antes de codar.
- **2026-07-17** — sincronização completa deste doc com `_core/CODING-PRINCIPLES.md` do framework
  (fonte de verdade unificada). Removida versão parcial anterior que só cobria DRY.
