---
date: 2026-05-25
tags: [ia, framework, pd, time, marketing]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Time Marketing

> Documentação humana do bootstrap. Fonte canônica: `pd-framework/times/marketing/`
> Linear: PDL-253 (Done) · Sub-issue: PDL-254 (motor econômico — Backlog)
> Commits: f932e72 → c85a7a4 → b4cdaf7 → 8bb5aa1 → 251084f → 8353d0a → c07a6cf → b143057

## Função do Time

O Time Marketing gerencia **comunicação e geração/nutrição de leads** para todas as marcas da PD (PD Consultorias, PD Gestores de IA, Cadência SaaS). Não é uma área genérica — é um sistema de squads com personas, workers determinísticos e foundation docs que garantem consistência de marca sem depender de briefing a cada tarefa. Liderado por **Maria** (Head de Marketing, persona BMAD Mary).

---

## Estrutura

```
times/marketing/
├── CLAUDE.md                          (líder: Maria)
├── foundation/                        (10 docs constitutivos)
│   ├── README.md
│   ├── posicionamento.md              ⚠️ motor econômico EM REVISÃO (PDL-254)
│   ├── icp.md
│   ├── anti-icp.md
│   ├── narrativa.md
│   ├── metodo-historias.md
│   ├── tom-de-voz.md
│   ├── brand.md
│   ├── central-marca.md
│   ├── historia.md
│   └── decisions.md                   (decisões sobre os foundation docs)
├── skills/                            (2 skills atômicas)
│   ├── consultar-brand.md
│   └── marketing-debate.md            (roundtable party mode)
├── memory/
│   ├── STATE.md                       (L1/L2/L3 — agregado dos 4 squads)
│   └── decisions.md                   (D01-D09 + R01-R05)
├── marketing-produto/
├── intel-mercado/
├── nutricao/
└── comunicacao/                        (squad pai)
    ├── trafego/                        (persona: Pedro)
    ├── social-media/                   (persona: Rafael)
    └── assessoria-imprensa/
```

---

## Personas

| Persona | Squad | Inspiração | Voz |
|---|---|---|---|
| **Maria** | Time Marketing (líder) | BMAD Mary — discovery, posicionamento | Estratégica, integradora, faz perguntas que abrem |
| **Pedro** | Tráfego & Performance | Pedro Sobral — metodologia direta | "O criativo é a variável. A estratégia é a constante." |
| **Rafael** | Social Media | Rafael Kizo / mLabs — criativo, volume | "Gancho nos primeiros 3 segundos. Formato nativo." |
| Nutrição TBD | Nutrição | A definir | ❌ Sessão dedicada |
| Intel. Mercado TBD | Intel. de Mercado | A definir | ❌ Sessão dedicada |
| Mkto Produto TBD | Marketing de Produto | A definir | ❌ Sessão dedicada |
| AP TBD | Assessoria de Imprensa | A definir | ❌ Sessão dedicada |

---

## Foundation docs

| Doc | Status | Conteúdo principal |
|---|---|---|
| `posicionamento.md` | ⚠️ parcial | Framework Kotler + Al Ries + porco-espinho. Motor econômico EM REVISÃO — LHI desatualizado (pré-Cadência SaaS) |
| `icp.md` | ✅ populado | Big Five público PD, 3 trilhas, JTBD, anti-padrões por produto |
| `anti-icp.md` | ✅ populado | Desqualificadores por trilha, sinais gerais de não-fit |
| `narrativa.md` | ✅ populado | Técnica X/Y, 3 editorias, SOAP, Seinfeld, vídeo 60s, carrossel |
| `metodo-historias.md` | ✅ populado | PNM 8 passos, Brendan Kane, Jornada do Herói Vogler |
| `tom-de-voz.md` | ✅ populado | 4 atributos PD, tom Cadência (Maga+Sábia), 13 traduções IA→lead |
| `brand.md` | ✅ populado | Paleta PD (5 cores), EB Garamond + Inter, filete vertical #267788 |
| `central-marca.md` | ✅ populado | Arquétipos Sábio+Cuidador+Herói, origin story não-técnico, por que Cuidador é diferencial real |
| `historia.md` | ✅ rascunho | Arco X/Y: ESPM → Gastronomia → pivô IA → PD → Helena. Versões adaptadas a criar (SOAP, pitch, reels) |
| `decisions.md` | ✅ criado | Decisões sobre os próprios foundation docs (padrão novo — nível foundation/) |

---

## Decisões chave (top 5 do decisions.md)

- **2026-05-25 — R01** — Squad Branding dissolvido → skill `/consultar-brand` (sem workers, sem ritmo)
- **2026-05-25 — R02** — `crm/` renomeado → `nutricao/` com escopo explícito top-funnel pré-vendas (não CS, não Comercial)
- **2026-05-25 — R03** — `foundation/central-marca.md` criado com arquétipos reais (Sábio+Cuidador+Herói, origin story Felipe)
- **2026-05-25 — D09** — Felipe criará conta Cadência para perfil @felipeluissalgueiro (pendente criação)
- **2026-05-25 — foundation** — Motor econômico LHI marcado EM REVISÃO → PDL-254 criado

---

## Marcas gerenciadas

| Marca | Produto | Arquétipo | Rosto |
|---|---|---|---|
| **PD Consultorias** | Implementação IA em PMEs | Sábio + Cuidador + Herói | Felipe (porta-voz) |
| **PD Gestores de IA** | Franquia profissionais tech | Sábio + Herói | Felipe |
| **Cadência SaaS** | Plataforma conteúdo + CRM | Maga + Sábia | Avatar IA (Felipe em background) |

---

## Pessoas-chave

- **Felipe**: aprovador de conteúdo, fonte das pautas de AP, porta-voz das 3 marcas PD
- **Maria**: líder orquestradora (persona, não pessoa real)
- **Pedro**: tráfego pago, Meta Ads (persona)
- **Rafael**: social media orgânico (persona)

---

## Projetos Linear vinculados

- **PDL-253** — Bootstrap Time Marketing — ✅ Done
- **PDL-254** — Redefinir motor econômico porco-espinho (LHI) — Backlog, assignado Felipe
- **ff596e0e** — Pipeline Marketing PD (compartilhado: Tráfego + Social Media + Intel. Mercado — usar label `squad:<path>`)

---

## Bloqueios externos

- **AP Notion → Obsidian** — contexto operacional da Assessoria de Imprensa ainda no Notion (lista de veículos, templates, histórico). Sessão dedicada com Felipe necessária.
- **Motor econômico (PDL-254)** — porco-espinho incompleto até sessão Felipe + Maria.
- **Conta Cadência @felipeluissalgueiro (D09)** — aguarda Felipe criar a conta.

---

## Como usar

- **Abrir Time**: `times/marketing/` → Maria lidera
- **Abrir Squad específico**: `times/marketing/<squad>/`
- **Debate cross-canal**: `/marketing-debate` (Maria + Pedro + Rafael)
- **Consulta de marca**: `/consultar-brand`
- **Foundation**: sempre ler antes de criar asset (tabela no `CLAUDE.md`)

---

## Pendências para sessões futuras

- [ ] Criar 4 personas faltantes: Mkto Produto, Intel. Mercado, Nutrição, AP
- [ ] PDL-254: sessão Felipe + Maria para redefinir motor econômico
- [ ] Migração AP Notion → Obsidian (sessão dedicada)
- [ ] Versões adaptadas `historia.md`: SOAP email, pitch 3min, reels 60s (requer gravação com Felipe)
- [ ] `foundation/cadencia-contexto.md` — criar quando Mkto Produto abrir trabalho Cadência
- [ ] Grade semanal de conteúdo (Social Media — Rafael)
- [ ] Metas CPL/ROAS por produto (Tráfego — Pedro)
- [ ] Conta Cadência @felipeluissalgueiro (D09)

---

## Notas relacionadas

- [[IA-Tecnologia/2026-05-25 PD Framework — Hierarquia Time-Squad e memory híbrida]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Constituição dos Times]]
- [[IA-Tecnologia/2026-05-24 PD Framework — Mapa final e decisões consolidadas]]
