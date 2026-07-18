---
title: RH — Decisão de Contratação (AFM)
tags: [operacional, canon, rh, afm]
---

# RH — Decisão de Contratação (AFM)

> Fundamento operacional do Time Operacional para qualquer decisão de contratação humana na Cadencia.
> Princípio diretor: `_core/AFM.md`. Conceito cristalizado: Obsidian `Conceitos/AFM — Decisão de Contratação`.
>
> **Aplicação:** toda vez que surgir impulso "precisamos contratar alguém pra X", ler este doc antes de abrir qualquer conversa ou processo seletivo.

---

## Por que este documento existe

A PD opera em AI Founder Mode (AFM). Isso significa que contratação humana **não é o default** quando surge demanda — é o último recurso, após esgotar skill, worker, persona e refundação de processo.

Sem esse filtro, o crescimento natural da empresa replicaria o erro que Chesky descreve: empresas com 7-9 camadas de gestão, managers puros sem ofício técnico, e cultura de reunião como canal default. O AFM existe pra impedir esse drift. Este documento aplica AFM ao plano operacional de RH.

---

## Regra-mãe — sequência obrigatória

```
1. Posso resolver com skill/worker?          → Sim: cria skill, fim.
2. Posso resolver com agente/persona?        → Sim: cria persona no Squad, fim.
3. Posso resolver refundando processo?       → Sim: refunda, fim.
4. Só agora: humano vira opção real.
```

Ordem é inegociável. Pular etapa = contratação prematura.

---

## 5 sinais que pedem humano (não agente)

Apenas essas cinco classes de demanda justificam contratação humana:

| Sinal | Por que não-IA | Exemplo PD |
|---|---|---|
| **Relacionamento físico recorrente** | Cliente quer olho no olho, jantar, presença física | Reuniões WGL-tier, eventos, mentorias presenciais |
| **Decisão com risco legal/financeiro pessoal** | Não pode ser delegada a agente determinístico | Assinar contrato, lidar com BACEN, defender posição na Receita |
| **Execução física no mundo** | Mão na coisa, deslocamento | Operação de evento, entrega física, vistoria local |
| **Julgamento ético em zona cinzenta** | Não delega a worker | Demitir, recusar cliente tóxico, posicionamento público sensível |
| **Geração de relacionamento com volume que passa do single point** | Volume excede capacidade de Felipe + personas | Cadência com 30+ clientes ativos pedindo CS humano simultâneo |

**Outras dores não pedem humano:**
- Organizar informação → skill
- Gerar artefato (doc, relatório, post) → skill
- Lembrar / agendar / monitorar → worker
- Executar processo repetível → worker
- Triagem volume baixo / resposta padronizada → agente + worker

Se a dor proposta não cabe em uma das 5 classes acima, **não é contratação**. É skill, worker ou persona.

---

## Árvore de decisão

```
Que função vai fazer?
│
├─ Coordenar/gerenciar/acompanhar gente
│  └─ ❌ VETO ABSOLUTO (Pilar 3 AFM — manager puro morre)
│
├─ Documentar/organizar/estruturar processo
│  └─ ❌ Cria skill. Não contrata.
│
├─ Atender/responder/triagem volume baixo
│  └─ ❌ Worker + agente. Não contrata.
│
├─ Executar tarefa repetível
│  └─ ❌ Worker. Não contrata.
│
├─ X técnico não-automatizável hoje
│  ├─ Volume justifica ≥ 20h/sem de pessoa só nisso?
│  │  ├─ Não → ❌ freelancer/contractor pontual
│  │  └─ Sim → ✅ candidato real → aplica filtro AFM
│  │
│
└─ Cara no mundo físico (eventos, vendas presenciais, ops)
   └─ ✅ candidato real → aplica filtro AFM
```

---

## Filtro AFM — 5 checks antes de abrir vaga

Toda contratação candidata precisa passar nos 5 checks. Reprovou 1 = não contrata, refunda a função.

- [ ] **É IC ou IC-híbrido** (vai ter ofício técnico próprio, não só gestão)?
- [ ] **A função NÃO é > 70% gerir outras pessoas** (sem manager puro)?
- [ ] **Não cria 5ª camada hierárquica** (teto AFM = 4 camadas)?
- [ ] **Sobrevive ao redesenho de 12 meses** (não é tapa-buraco temporário)?
- [ ] **Tem trabalho async claro** (não depende de "estar lá" presencialmente)?

---

## Gatilho universal — quando começar a discutir contratação

> **A mesma demanda voltou 3× seguidas, em janelas próximas, e nem worker nem agente nem refundação de processo resolveu de forma sustentável.**

Antes desse gatilho: refunda. Depois desse gatilho: abre o filtro AFM.

Demanda única ou pontual NUNCA justifica contratação. Mesmo que urgente. Resolve pontualmente com freelancer ou consultoria.

---

## Pergunta-chave antes de qualquer vaga

> *"Se eu não contratar essa pessoa e em vez disso passar 4 horas redesenhando o processo + criando uma skill nova + ajustando um Squad — eu resolvo isso?"*

- Resposta = **"sim, mas seria trabalhoso"** → não contrata, refunda.
- Resposta = **"não, é fundamentalmente humano"** → começa pipeline.

Essa pergunta deve ser feita por Felipe antes de qualquer abertura de vaga. Não pode ser pulada.

---

## Método de execução (modo Chesky) quando passou no filtro

Quando a vaga é legítima e o filtro passou, executar contratação assim:

1. **Pipeline contínuo, sem search firm.** Não abre vaga; chama alguém que já foi mapeado em conversas anteriores. Se não tem ninguém mapeado, **não está pronto pra contratar**.

2. **Começa pelos resultados, não pelo currículo.**
   - Viu um pitch comercial impecável de outra empresa? Descobre quem fez.
   - Viu um onboarding de cliente bem desenhado? Procura quem é o autor.
   - Anúncio que para o feed? Designer/copy responsável.

3. **Toda conversa de negócio termina com mapeamento.** Pergunta padrão: *"Quem são as duas ou três melhores pessoas que você conhece em [área]?"*. Anota em rolodex permanente.

4. **Felipe é o hiring manager.** Não delega a Stamper, não delega a futuro líder do Squad. Entrevista pessoal nas primeiras conversas. Critério Chesky: "primeiras 200 pessoas o CEO contrata diretamente".

5. **Mafias de talento.** Pesca em redes onde mora qualidade: ex-V4, ex-G4 Educação, ex-Stone, ex-tech consagrada. Não em job board.

---

## Estado atual da Cadencia (referência)

### Onde NÃO contrata (próximos 6-12 meses)

| Área | Por quê não |
|---|---|
| **CS Cadência** | Escala Letícia (persona) + workers + dossier automation até ~30 clientes ativos pedindo intervenção simultânea |
| **Marketing** | Maria (persona) + Felipe como rosto. Sem cargo de "social media" |
| **Financeiro** | Bárbara (CFO virtual). NF manual sob demanda. Contador externo cobre folha |
| **Operacional/RH** | Sem cargo. Este doc é o playbook quando virar |
| **Qualidade/Inteligência** | Workers + personas |

### Próximas contratações reais (quando o gatilho disparar)

| Cargo candidato | Sinal de gatilho | Tipo |
|---|---|---|
| **Closer comercial** (ticket médio, NÃO SDR — SDR é agente) | Perder 3 deals seguidos por "Felipe não teve agenda" | IC comercial |
| **Outro dev IC** (NUNCA tech lead, NUNCA CTO) | Luiz + agentes saturados em Cadência + projetos cliente (Lara, NSkin, GCI-GO) simultaneamente por 60+ dias | IC técnico |
| **Par operacional executivo** (estilo Hiroki Asai — executa o que Felipe desenha, não "assistente") | Felipe passando de ~40h/sem em tarefa não-criativa de forma sustentada | IC operacional sênior |

Nenhum desses cargos tem subordinado. Todos são IC. Todos passam no filtro AFM.

---

## Anti-patterns explícitos — vetos absolutos

Estes pedidos serão **automaticamente vetados** quando aparecerem:

- ❌ "Gerente de operações" / "head of operations" sem ofício técnico
- ❌ "Diretor comercial" / "head of sales" gerindo SDRs ou closers
- ❌ "Tech lead" / "CTO" / "engineering manager" antes de >5 IC dev humanos
- ❌ "Chief of staff" como cargo (Stamper já é isso, virtualmente)
- ❌ "Coordenador" de qualquer coisa
- ❌ "Social media manager" (Maria + Felipe rosto resolve)
- ❌ "Assistente" administrativo (worker resolve agenda; par executivo é IC sênior, não assistente)

Cada um desses é Founder Mode legado disfarçado ou estrutura de empresa tradicional sendo importada sem análise. Veto.

---

## Processo de contratação quando aprovada

1. **Documentação prévia** (Felipe):
   - Justificativa do gatilho (qual demanda voltou 3×?)
   - Confirmação dos 5 checks AFM
   - Descrição da função em termos de **ofício técnico**, não de gestão
   - Faixa salarial alinhada à `times/financeiro/foundation/precificacao-margens.md`

2. **Pipeline** (Felipe + rolodex):
   - Lista de pessoas já mapeadas que cabem na função
   - Se vazia: **adia contratação até mapeamento existir**

3. **Entrevistas** (Felipe direto):
   - Conversa de fit técnico (do ofício, não comportamental)
   - Conversa sobre resultados anteriores (concretos, verificáveis)
   - Apresentação aos Squads / personas com quem a pessoa vai interagir

4. **Contratação** (Felipe + Time Financeiro):
   - Contrato PJ (modelo: `times/financeiro/foundation/contratos-modelo.md`)
   - Setup de credenciais via 1Password
   - Onboarding ao framework: leitura obrigatória de CLAUDE.md raiz + `_core/AFM.md` + foundation do Squad onde vai operar

5. **Documentação pós** (Felipe):
   - Atualizar `times/operacional/data/pessoas.md` (criar se não existir)
   - Atualizar `_core/PEOPLE.md` se aplica
   - Registrar no STATE.md do Squad relevante

---

## Forms Tally reutilizáveis (qualquer contratação)

Criados 2026-07-12 no onboarding do Renan, já genéricos (sem nome de pessoa) — reaproveitar em qualquer contratação nova, não recriar do zero:

| Form | Link | Uso |
|---|---|---|
| Onboarding técnico — Autoavaliação e perfil de trabalho | `https://tally.so/r/9qyDdp` | Nível técnico (dev/infra/Git/IA/harness) + perfil cognitivo/estilo de trabalho — mandar antes da 1ª reunião |
| Dados para contrato de trabalho | `https://tally.so/r/aQgYxq` | Nome completo, CPF, endereço/CEP, status MEI + dados bancários se MEI ativa |

Gerenciados via `_shared/tally_builder.py` (workspace `mRYoEv`). Pra editar sem recriar: `patch_form(form_id, blocks=..., name=...)`.

---

## Refs

- `_core/AFM.md` — princípio diretor (seção H: Decisão de contratação)
- `_core/PEOPLE.md` — pessoas operacionais da Cadencia
- `_core/HIERARCHY.md` — codificação do P1 (4 camadas)
- `_core/PERSONAS.md` — codificação do P3 (IC híbrido)
- `times/financeiro/foundation/contratos-modelo.md` — modelo PJ
- Obsidian: `Conceitos/AFM — Decisão de Contratação`
- Obsidian: `Conceitos/AI Founder Mode`
- Fonte original: entrevista Brian Chesky no Invest Like The Best (2026-05)
