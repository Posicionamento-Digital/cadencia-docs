---
date: 2026-05-14
tags: [cadencia, motor, grafico, carrossel, tecnico, renderer, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]"]
---
# Motor Gráfico de Carrosséis — Documentação Técnica

Documento descreve absolutamente tudo que existe no motor. Cada componente com: o que é, para que serve, como funciona. Objetivo: qualquer pessoa consegue entender e recriar o sistema inteiro lendo este documento.

---

## Números do Motor

| Item | Quantidade |
|---|---|
| Etapas do pipeline | 7 |
| Agentes (módulos LLM) | 6 (research, classification, headline, carousel, caption, cover) |
| Modelos de carrossel (YAMLs) | 29 |
| Templates HTML (variantes A+B) | 58 |
| Flags de classificação | 12 booleanas + 1 content_type |
| Pares flag→modelo no scoring | ~40 |
| Campos configuráveis no total | ~2.000+ |

---

## Estrutura da Documentação

- **Parte 1:** Pipeline, agentes e prompts (como o conteúdo é gerado)
- **Parte 2:** Modelos, templates, configurações e banco de dados (como o visual é renderizado e tudo que pode ser editado)

Links Notion originais (partes detalhadas):
- Parte 1: https://www.notion.so/337a96f9516a818ca690eb265debce80
- Parte 2: https://www.notion.so/337a96f9516a81c29d15eddd23a941f8

---

## Pipeline de 7 Etapas

```
1. [Classificação] → flags booleanas + content_type por ideia aprovada
2. [Pesquisa] → Research Document JSON (dados relevantes para a ideia)
3. [Headline] → Headline + Subtítulo + Gancho + Tipo Hook
4. [Seleção de modelo] → scoring determinístico (flags → YAML de modelo)
5. [Carrossel] → 7-10 slides no formato Método X/Y
6. [Legenda] → Caption estruturado (P/R/Cr/Cp/CTA) + Hashtags
7. [Renderização] → generate_slides.py → PNGs via Playwright
```

---

## Agentes LLM

| Agente | Input | Output |
|---|---|---|
| research | ideia + dossiê de marca | Research Document JSON |
| classification | ideia | 12 flags booleanas + content_type |
| headline | research doc | headline, subtítulo, gancho, tipo de hook |
| carousel | research doc + headline | 7-10 slides (título + corpo + emoji) |
| caption | slides + research doc | legenda P/R/Cr/Cp/CTA + 15 hashtags |
| cover | headline + config visual | prompt para imagem de capa |

---

## Modelos de Carrossel (29 YAMLs)

Cada YAML define a sequência de componentes, regras de layout e campos configuráveis. Os 9 formatos principais:
1. Lista
2. Tutorial (passo a passo)
3. News Brief
4. Storytelling
5. Comparação
6. Expectativa vs Realidade
7. Antes/Depois
8. Recapitulação
9. Estudo de Caso

---

## Seleção Determinística de Modelo

Tabela de scoring no Supabase. Cada flag ativa ou penaliza modelos:
- `is_tutorial: true` → favorece modelos passo-a-passo
- `is_controversial: true` → favorece modelo expectativa vs realidade
- `content_type: "case"` → seleção direta de estudo de caso
- ~40 pares flag→modelo cobrem todos os casos do MVP

---

## Renderização

- Script: `generate_slides.py` (Python + Playwright)
- CSS Custom Properties injetadas via `tenant_config` → identidade visual por cliente
- 58 templates HTML (29 modelos × 2 variantes A/B)
- Output: PNGs em `1080×1080` (feed) e `1080×1920` (stories)
- Storage: Supabase Storage → CDN Cloudflare

---

## Campos Configuráveis (~2.000+)

Por tenant, configurável sem código:
- Tipografia (família, pesos, tamanhos por componente)
- Paleta de cores (primária, secundária, fundo, texto, acento)
- Logo (posição, tamanho, opacidade)
- Padding, border-radius, shadow de cada componente
- Tom de voz e persona dos agentes
- Editorias (3 por tenant, pesos de seleção)

---

## Notas Relacionadas

- [[Projetos/Cadencia/Docs/PRD-Arquitetura-Tecnica]]
- [[Projetos/Cadencia/Docs/PRD-Executive-Summary]]
- [[Projetos/Cadencia/Docs/Epics-Stories-Visao-Geral]]
