---
title: Template — Checklist de Projeto no Linear
tags: [cs, canon]
---

# Template — Checklist de Projeto no Linear (adaptável por produto)

> Doc constitutivo. **Toda criação de projeto de cliente (`/linear-criar-projeto`) gera um Linear Document de checklist a partir deste template, adaptado ao produto contratado.**
> Fonte dos blocos: `checklist-briefing.md` (11 seções) + `playbook-implementacao-11-fases.md`.
> Criado 2026-06-17. Owner: Time CS (Letícia).

---

## Como a skill usa este template

1. Detecta o **produto contratado** (parâmetro da skill / tags do contato no CRM Cadencia / pergunta ao Felipe).
2. Monta o documento com os **blocos canônicos** abaixo.
3. Aplica a **Matriz de adaptação** — blocos marcados `N/A` pro produto entram na seção final "N/A neste produto" (riscados), não no corpo.
4. Personaliza placeholders (`{nome}`, `{empresa}`, `{tenant}`, `{deal}`, etc).
5. Cria via `save_document` no projeto Linear recém-criado, título `✅ Checklist Onboarding & Briefing — {nome} ({produto})`.

Princípio: **o checklist é sempre o mesmo na origem; o que muda é quais blocos aplicam.** Nunca inventar bloco fora desta lista — só ligar/desligar.

---

## Blocos canônicos (catálogo fechado)

| ID | Bloco | Origem |
|---|---|---|
| `B0` | Pré-reunião — preparação interna | checklist §pré |
| `B1` | Objetivos de Negócio | checklist §1 |
| `B2` | Processo Atual / Briefing do cliente | checklist §2 |
| `B3` | Ferramentas & Sistemas (CRM) | checklist §3 |
| `B4` | Produtos, Ofertas & Precificação | checklist §4 |
| `B5` | Requisitos da IA & Persona do Agente | checklist §5 |
| `B6` | Time Interno & Governança | checklist §6 |
| `B7` | Métricas de Sucesso | checklist §7 |
| `B8` | Riscos & Restrições | checklist §8 |
| `B9` | Go-Live & Cronograma | checklist §9 |
| `B10` | Suporte & Materiais Educativos | checklist §10 |
| `B11` | Oportunidades Futuras & Próximos Passos | checklist §11 |
| `F3` | Setup CRM e Pipelines | playbook Fase 3 |
| `F4` | Cadastro Asaas (cobrança recorrente cliente) | playbook Fase 4 |
| `F45` | Aquecimento de Chip WhatsApp 14d | playbook Fase 4.5 |
| `F5` | Integrações & IAs (canais, BM/Meta, tráfego) | playbook Fase 5 |
| `F7` | Treinamento e Adoção | playbook Fase 7 |
| `F8` | Acompanhamento de Implementação | playbook Fase 8 |

Conteúdo detalhado de cada bloco: copiar os itens `- [ ]` correspondentes de `checklist-briefing.md` / `playbook-implementacao-11-fases.md`. Adaptar o texto dos itens ao vocabulário do produto (ex: "leads" → "conteúdo" no Cadencia).

---

## Matriz de adaptação por produto

Legenda: ✅ aplica · ➖ aplica adaptado · ❌ N/A (vai pra seção riscada)

| Bloco | CRM-PD (completo) | IA Comercial / Agente WhatsApp | Cadência Bundle (conteúdo) | Tráfego / Meta Ads | Treinamento Claude Code 30d | Consultoria pontual |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| B0 Pré-reunião | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| B1 Objetivos | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| B2 Processo/Briefing | ✅ | ✅ | ➖ (briefing de conteúdo) | ➖ (funil/oferta) | ➖ (objetivo de capacitação) | ✅ |
| B3 Ferramentas/CRM | ✅ | ➖ | ❌ | ➖ | ❌ | ➖ |
| B4 Produtos/Ofertas | ✅ | ✅ | ✅ | ✅ | ➖ | ✅ |
| B5 Persona da IA | ✅ | ✅ | ➖ (persona da marca/dossier) | ❌ | ❌ | ❌ |
| B6 Time/Governança | ✅ | ✅ | ➖ | ✅ | ✅ | ✅ |
| B7 Métricas | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| B8 Riscos | ✅ | ✅ | ✅ | ✅ | ➖ | ✅ |
| B9 Go-Live/Cronograma | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| B10 Suporte/Materiais | ✅ | ✅ | ✅ | ➖ | ✅ | ➖ |
| B11 Próximos Passos | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| F3 Setup CRM | ✅ | ➖ | ❌ | ❌ | ❌ | ❌ |
| F4 Asaas recorrente | ✅ | ➖ | ❌ | ❌ | ❌ | ❌ |
| F45 Chip WhatsApp 14d | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| F5 Integrações/BM/Tráfego | ✅ | ➖ | ❌ | ✅ | ❌ | ❌ |
| F7 Treinamento/Adoção | ✅ | ✅ | ✅ | ➖ | ✅ | ➖ |
| F8 Acompanhamento | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Produto não listado:** usar a coluna mais próxima como base e perguntar ao Felipe quais dos blocos `❌` ele quer ligar. Nunca chutar — na dúvida, ✅ (incluir) e marcar `(confirmar)`.

---

## Estrutura final do documento gerado

```
✅ Checklist Onboarding & Briefing — {nome} ({produto})

> Adaptado ao produto {produto}. Base: checklist-briefing.md + playbook-implementacao-11-fases.md.
> Cliente: {nome} — {empresa}. {linha de contexto: tenant/deal/contato CRM Cadencia}.

## 0. Pré-reunião
## 1. Objetivos de Negócio
... (apenas blocos ✅/➖ do produto, na ordem do catálogo)

## N/A neste produto
- ~~{bloco desligado}~~ — {motivo curto}

---
Fonte do template: times/cs/foundation/template-checklist-projeto-linear.md
```

---

## Exemplo de referência (já gerado manualmente)

- **Mel Quevedo (Cadência Bundle):** Linear Document `9972f0fd00cb` no projeto `cs: Mel Quevedo — Cadência Bundle`. Mostra o padrão: blocos de conteúdo ativos + seção N/A com CRM/Asaas/chip/tráfego riscados.

---

## Refs

- `checklist-briefing.md` — 11 seções (itens detalhados de B0–B11)
- `playbook-implementacao-11-fases.md` — fases (itens detalhados de F3–F8)
- `times/juridico/foundation/map-contratos.md` — catálogo de produtos Cadencia (manter esta matriz alinhada quando produto novo surgir)
