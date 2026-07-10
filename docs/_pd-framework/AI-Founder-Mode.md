---
tipo: conceito
tags: [conceito, lideranca, gestao, ia, empreendedorismo, founder-mode, cultura-pd]
date: 2026-05-28
moc: "[[MOC-Operacional]]"
---

# AI Founder Mode (AFM)

> Forma de operar a PD na era da IA: estar nos detalhes via instrumentação assíncrona, com organograma achatado, sem managers puros — refundando estrutura em vez de otimizá-la. Princípio diretor de toda decisão organizacional.

## O que é

AFM = Founder Mode × instrumentação IA. Brian Chesky cunhou em entrevista ao *Invest Like The Best* (mai/2026) ainda em formulação — ele se descreve "no meio de tentar pensar como redesenhar a empresa".

A diferença em relação ao **Founder Mode original** (Paul Graham, pós-pandemia de Chesky na Airbnb): o Founder Mode legado funcionava em 35h semanais de reunião porque reunião era o único canal de informação. AFM substitui reunião por instrumentação — dashboards, agentes, documentos vivos — e por isso consegue ir ainda mais fundo no detalhe sem virar gargalo.

### Três axiomas (não negociáveis)

| # | Axioma | Citação |
|---|---|---|
| AX1 | **Detalhe sob demanda** — líder mergulha em qualquer camada sem virar gargalo | *"você tem quase tudo em demanda"* |
| AX2 | **Gerencia-se o trabalho, não as pessoas** | *"Você não gerencia as pessoas, você gerencia o trabalho"* |
| AX3 | **Refundar > otimizar** — IA exige redesenho fundamental | *"temos que redesenhar nossa empresa inteira de novo"* |

### Cinco pilares operacionais

1. **Org chart achatado** — teto 4 camadas (Igreja Católica = 4 em 2 mil anos)
2. **Async como canal default** — reunião é exceção
3. **Todo manager é IC híbrido** — engenheiro-gerente codifica, designer-gerente desenha
4. **Detalhamento via instrumentação** — dashboards, agentes, docs vivos
5. **Decisão centralizada com cadeia transparente** — visível em documento, não em sala

### Quem não sobrevive ao AFM

- **People manager puro** (cargo cuja função é só gerir gente)
- **Gente rígida** sem mentalidade de crescimento
- **CEO profissional avesso a risco** (não tem músculo de refundação)

## Por que importa para a PD

A arquitetura da PD já é **AFM-nativa por design**:

| Pilar AFM | Como aparece na PD |
|---|---|
| AX1 + P4 (detalhe sob demanda via instrumentação) | Stamper + Squads + STATE.md + workers VPS + Linear + Obsidian |
| P2 (async default) | Decisões em Linear, log de sessões, STATE.md, workers determinísticos |
| P3 (manager híbrido) | Personas são todas IC com ofício técnico: Catarina/Cadência, Vitor/Tech Lead, Diego/DevOps, Letícia/CS, Bárbara/CFO, Eduardo/Comercial, Maria/Marketing |
| P1 (4 camadas) | Felipe → Stamper → Squad → Worker |
| P5 (decisão centralizada async) | Felipe decide; cadeia visível em STATE + decisions.md de cada Squad |

Felipe intuiu essa estrutura há meses. AFM só deu nome ao princípio e formalizou o critério de auditoria.

### Guard-rails ativos na PD

1. **Contratação humana** — só IC ou IC-híbrido. "Gerente de gente" puro = veto. (Ver [[RH/AFM-Decisao-Contratacao]])
2. **Design de Squad novo** — persona líder precisa ter ofício técnico declarado, não só skill de orquestração.
3. **Refundação contínua** — quando observação revela trabalho mudado, refunda. Não otimiza.
4. **Mentor externo recomendando estrutura tradicional** — Felipe traduz pra AFM antes de aceitar.

## Risco principal a evitar

Cair em **"otimização" disfarçada de transformação**. Usar IA pra fazer o mesmo 20% mais rápido não é AFM — é Founder Mode com esteróide. AFM exige refundação fundamental.

A cada 90 dias, pergunta-auditoria: *"algum trabalho mudou de forma material por causa da IA?"* Se sim, refunda (deleta Squad, cria persona nova, reescreve skill, descontinua worker). Se não, segue.

## Conexões

- [[RH/AFM-Decisao-Contratacao]] — playbook prático de contratação aplicando AFM
- [[Cultura/Principios-Fundamentais]] — cultura PD em que AFM se ancora
- [[Cultura/Manifesto-PD]]
- [[MOC-Operacional]]
- [[MOC-Time]]

## Fontes

- **Brian Chesky** em *Invest Like The Best* (Patrick O'Shaughnessy) — 2026-05 — [vídeo](https://www.youtube.com/watch?v=eURcW5_uS60)
- Princípio diretor formal: `pd-framework/_core/AFM.md`
- Conceito Zettelkasten pessoal: vault Pessoal → `Conceitos/AI Founder Mode`
- Artigo público derivado: https://insightartificial.ia.br/founder-mode-era-ia-chesky
