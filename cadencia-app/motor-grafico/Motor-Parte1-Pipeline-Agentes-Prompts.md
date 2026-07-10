---
date: 2026-05-14
tags: [cadencia, motor, grafico, pipeline, agentes, prompts, tecnico, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[marketing]]"]
---
# Motor Gráfico — Parte 1: Pipeline, Agentes e Prompts

Como o conteúdo é gerado, passo a passo, do momento em que o cliente aprova uma ideia até o carrossel ficar pronto.

---

## Visão Geral do Pipeline

O pipeline é a sequência de 7 etapas que transforma uma **ideia de post** em um **carrossel pronto** com imagens PNG, legenda e hashtags. Cada etapa é executada por um agente especializado — módulo Python que chama o LLM com um prompt específico.

**Tempo total médio:** 40-50 segundos.
**Arquivo principal:** `cadencia-workers/src/workers/orchestrator.py` (454 linhas)

### Fluxo de disparo
1. Cliente aprova uma ideia (swipe direito)
2. Frontend chama `POST /api/v1/pipeline/run` com `idea_id`
3. Backend cria registro em `generation_queue` com status `"pending"` e prioridade (1 pagos, 0 trial)
4. Pipeline inicia em thread separada — retorna `202 Accepted` imediatamente
5. Cada etapa atualiza progresso em `pipeline_status`
6. Frontend faz polling a cada 3s em `GET /api/v1/pipeline/status/{queue_id}`
7. Quando termina: documento fica `"ready"` e aparece na aba Posts

### As 7 etapas

| Etapa | Nome | O que faz | Agente | Tempo |
|---|---|---|---|---|
| 1 | Research | Pesquisa o tema, produz documento com fatos, dores, desejos e framework X/Y | `research_agent` | ~10s |
| 2 | Model Selection | Classifica ideia em 12 flags booleanas via LLM, pontua e escolhe o modelo | `model_selector` | ~2s |
| 3 | Headline | Gera título (máx. 8 palavras), subtítulo, tipo de gancho e palavra-chave | `headline_agent` | ~2s |
| 4 | Carousel | Gera texto de cada slide seguindo estrutura AIDA do modelo selecionado | `carousel_agent` | ~10s |
| 5 | Caption | Gera legenda (P/R/Cr/Cp/CTA) e 10-15 hashtags | `caption_agent` | ~6s |
| 6 | Cover Generation | Gera foto de capa via Gemini (com rosto, temática, ou pula) | `cover_generation` | ~3s |
| 7 | Rendering | Transforma slides em PNG 1080x1440 via Playwright e faz upload ao Supabase | `slide_renderer` | ~10s |

### Operações no banco durante o pipeline

| Momento | Tabela | Operação | Campos |
|---|---|---|---|
| Início | `generation_queue` | UPDATE | status → "processing", started_at |
| Início | `pipeline_status` | INSERT | tenant_id, generation_queue_id, current_step, progress |
| Início | `content_ideas`, `tenant_config`, `tenant_profile`, `tenant_dossier`, `tenant_editorials`, `tenant_visual_identity`, `profile_responses`, `social_connections` | SELECT | Carrega contexto completo |
| Início | `content_documents` | INSERT | Cria documento com status "generating" |
| Etapa 1 | `research_documents` | INSERT | Salva research document |
| Etapa 2 | `content_documents` | UPDATE | Salva `carousel_model` |
| Etapa 3 | `content_headlines` | INSERT | headline, subtitle, hook_type, focus_keyword |
| Etapa 4 | `content_documents` | UPDATE | Salva `slides_content` (sem URLs) |
| Etapa 5 | `content_documents` | UPDATE | Salva caption e hashtags |
| Etapa 6 | `tenant_config` | UPDATE | Salva physical_description (se auto-gerada) |
| Etapa 7 | `content_documents` | UPDATE | slides_content COM URLs + status → "ready" |
| Final | `generation_queue` | UPDATE | status → "completed" ou "failed", completed_at |
| Final | `content_ideas` | UPDATE | status → "used" (só se sucesso) |

---

## Etapa 1 — Research Agent

**Arquivo:** `cadencia-workers/src/workers/research_agent/__init__.py` (117 linhas)

**Propósito:** Todos os outros agentes dependem deste documento. Sem ele, geram conteúdo genérico.

**Fluxo:**
1. Recebe: `idea`, `editorial`, `dossier`, `config`
2. Monta prompt com `_build_prompt()`
3. Envia ao LLM (`max_tokens=1500`)
4. Remove code fences, faz `json.loads()`
5. Valida via Pydantic (`ResearchDocument`)
6. Salva em `research_documents`

### Prompt completo do Research Agent

```
Você é um pesquisador de conteúdo para Instagram.
Produza um Research Document completo para esta ideia de carrossel.

REGRAS:
- Tudo em pt-BR.
- Dados REAIS e verificáveis quando possível.
- Use o Método X/Y: X = problema superficial, Y = transformação real.
- O documento serve como base para um carrossel educativo/inspiracional.
- Seja específico ao nicho do profissional.

IDEIA:
- Título: {idea.title}
- Descrição: {idea.description}

EDITORIAL:
- Nome: {editorial.name}
- Função: {editorial.editorial_function}
- Tom: {editorial.tone}

CONTEXTO:
- Nicho: {config.nicho}
- Posicionamento: {dossier.posicionamento (truncado em 300 chars)}
- Público-alvo: {dossier.publico_alvo (truncado em 300 chars)}

Responda EXATAMENTE no formato JSON (sem markdown, sem code fences):
{
  "topic": "Tópico principal",
  "key_facts": ["Fato 1", "Fato 2", "Fato 3"],
  "audience_pain": "Dor principal que o conteúdo resolve",
  "audience_desire": "O que o público quer alcançar",
  "x_problem": "Problema superficial (X)",
  "y_meaning": "Transformação real (Y)",
  "hook_angle": "Ângulo do gancho emocional",
  "data_points": ["Dado 1", "Dado 2"]
}
```

### Campos do output

| Campo | Para que serve | Onde é usado |
|---|---|---|
| `topic` | Tema central em uma frase | Caption agent |
| `key_facts` | 3-5 fatos verificáveis | Carousel agent (slides de corpo) |
| `audience_pain` | Âncora emocional de todo o carrossel | Hook, slides, legenda |
| `audience_desire` | Destino da jornada narrativa | Climax, CTA |
| `x_problem` | Problema de superfície (identificação imediata) | Hook |
| `y_meaning` | Transformação real ("aha moment") | Slide de climax |
| `hook_angle` | Ângulo emocional/curiosidade | Headline agent |
| `data_points` | Dados de suporte, hero numbers | Slides |

### Configurações editáveis

| Config | Valor atual | Impacto se mudar |
|---|---|---|
| System prompt | "Você é um pesquisador de conteúdo para Instagram." | Tom e papel |
| Método X/Y | Instrução no prompt | Trocar por PAS mudaria a estrutura |
| max_tokens | 1500 | Mais tokens = respostas mais detalhadas |
| Truncamento posicionamento | 300 chars | Mais = mais contexto, mais custo |
| Modelo LLM | GPT-5.4 | Modelos mais baratos = mais rápido, menos preciso |

---

## Etapa 2 — Model Selection

**Arquivo:** `cadencia-workers/src/shared/model_config.py`, linhas 126-158 e 253-294

### Fase 1 — Classificação via LLM

Chama `classify_idea()` com `max_tokens=400`. Retorna JSON com 12 flags booleanas + `content_type`.

**Fallback:** se o LLM falhar, todas as flags assumem `false` e content_type assume `"general"`. Pipeline não para.

### As 12 flags de classificação

| Flag | Quando é True | Exemplo |
|---|---|---|
| `is_news` | Post ligado a algo recente | "Nova lei trabalhista muda regras para CLT." |
| `has_story` | Narrativa com personagem, conflito e resolução | "Como a Maria triplicou o faturamento." |
| `is_tutorial` | Ensina de forma sequencial ou listada | "5 passos para montar uma proposta." |
| `is_comparison` | Compara duas coisas | "Marketing digital vs. tradicional." |
| `has_data` | Números/estatísticas são centrais | "73% dos brasileiros preferem comprar online." |
| `has_transformation` | Antes e depois com resultado tangível | "De 3 horas a 40 minutos com IA." |
| `is_opinion` | Posicionamento, crítica, react | "Por que discordo da produtividade tóxica." |
| `is_humor` | Meme, piada, situação engraçada | "Quando o cliente pede 'só uma alteraçãozinha'." |
| `has_testimonial` | Depoimento ou prova social | "O que meus clientes dizem." |
| `is_interactive` | Pede participação ativa | "Teste: qual é seu estilo de liderança?" |
| `is_promotional` | Objetivo direto de venda | "50% de desconto só até sexta." |
| `is_review` | Avaliação crítica de produto/ferramenta | "3 ferramentas de IA que testei." |

### Fase 2 — Filtragem de modelos compatíveis

3 filtros em sequência:
1. `compatible_nichos` do modelo inclui o nicho do tenant (ou `"all"`)
2. `compatible_editorials` inclui a função editorial do post (ou está vazia)
3. Modelo NÃO é um dos 3 últimos usados pelo tenant (anti-repetição)

### Fase 3 — Scoring Engine

Para cada modelo que passou nos filtros:
- Consulta `FLAG_MODEL_AFFINITY` para cada flag True → soma pontos
- Consulta `CONTENT_TYPE_AFFINITY` para o `content_type` → soma pontos extras
- Ordena por score decrescente
- Version 0 → maior score; Version 1 → 2º; Version 2 → 3º

### Tabela de afinidade Flag → Modelo → Pontos

| Flag | Modelos → Pontos |
|---|---|
| `is_news` | noticias(100), trend(80), react_opinion(60) |
| `has_story` | storytelling(100), transformacao(80), bastidores(70), estudo_caso(60), entrevista(50) |
| `is_tutorial` | tutorial(100), dicas_rapidas(80), animacao_processo(60), lista(50) |
| `is_comparison` | comparacao(100), expectativa_realidade(80), antes_depois(60) |
| `has_data` | infografico(100), analise_profunda(90), estudo_caso(80), recapitulacao(50) |
| `has_transformation` | antes_depois(100), transformacao(90), storytelling(60), depoimento(50) |
| `is_opinion` | react_opinion(100), citacao(80), motivacional(70) |
| `is_humor` | meme_humor(100) |
| `has_testimonial` | depoimento(100), feedback_respostas(70), estudo_caso(50) |
| `is_interactive` | desafio(100), enquete_qa(90), teste_quiz(80) |
| `is_promotional` | flash_sale(100), unboxing(80) |
| `is_review` | resenha(100), analise_profunda(60) |

### Tabela de afinidade por Content Type (boost menor)

| Content Type | Modelos → Pontos |
|---|---|
| `tutorial` | tutorial(40), dicas_rapidas(30), lista(20) |
| `story` | storytelling(40), bastidores(30), transformacao(20) |
| `news` | noticias(40), trend(30) |
| `opinion` | react_opinion(40), citacao(30), motivacional(20) |
| `humor` | meme_humor(40) |
| `general` | lista(20), dicas_rapidas(15), recapitulacao(10) |

---

## Etapa 3 — Headline Agent

**Arquivo:** `cadencia-workers/src/workers/headline_agent/__init__.py` (139 linhas)

**Fluxo:** Recebe ideia, research, editoria, config, version_index → monta prompt → LLM (`max_tokens=500`) → valida via Pydantic → salva em `content_headlines`

### Prompt completo

```
Você é um copywriter especialista em Instagram.
Gere uma headline IMPACTANTE para este carrossel.

REGRAS:
- Headline: MÁXIMO 8 palavras. Curta, direta, impossível de ignorar.
- Subtitle: 1 frase complementar que expanda a headline.
- Hook type: escolha entre autoridade, curiosidade, dados, provocação,
  prova_social, medo, aspiração.
- Focus keyword: 1 palavra-chave principal.
- Highlighted words: 2-3 palavras do headline para destacar visualmente.
- Tudo em pt-BR.
- Siga a regra de headline da editoria.

{instrução especial de versão, se version_index > 0}

IDEIA: {idea.title} / {idea.description}
PESQUISA: dor={research.audience_pain}, gancho={research.hook_angle}, X={research.x_problem}
EDITORIAL: regra={editorial.headline_rule}, tom={editorial.tone}
NICHO: {nicho}
```

### Os 7 tipos de gancho (hook_type)

| Tipo | Quando usar | Exemplo |
|---|---|---|
| `autoridade` | Profissional quer se posicionar como referência | "O que 10 anos de consultoria me ensinaram." |
| `curiosidade` | Cria lacuna de informação | "O erro que 90% dos empreendedores cometem." |
| `dados` | Há um dado forte no research | "73% dos brasileiros não sabem isso." |
| `provocação` | Vai contra o senso comum | "Trabalhar mais não te faz mais produtivo." |
| `prova_social` | Há um case ou testemunho forte | "Como a Maria dobrou o faturamento." |
| `medo` | Público precisa agir para evitar algo | "Sua proposta pode estar afastando clientes." |
| `aspiração` | Mostra transformação positiva | "De confusa a vendável com consultoria." |

### Versões alternativas

| version_index | Instrução adicionada | Resultado |
|---|---|---|
| 0 | Nenhuma | Melhor headline possível |
| 1 | "ÂNGULO EMOCIONAL. Foque na TRANSFORMAÇÃO, não no problema." | Versão emocional |
| 2 | "PROVOCATIVA baseada em DADOS ou PROVA SOCIAL. Use números." | Versão com dados |

---

## Etapa 4 — Carousel Agent

**Arquivo:** `cadencia-workers/src/workers/carousel_agent/__init__.py` (151 linhas)

**Fluxo:**
1. Recebe 12 parâmetros: idea, research, headline, editorial, model, config, dossier, content_restrictions, profile_insights, cta_mode, cta_keyword
2. Carrega YAML do modelo via `load_model(slug)` (cacheado em memória)
3. Fallback para `"lista"` se modelo não encontrado
4. `build_carousel_prompt()` monta o prompt mais longo do sistema
5. LLM com `max_tokens=3000`
6. Parse JSON (aceita `{"slides": [...]}` ou bare `[...]`)
7. Valida: mínimo 3 slides, máximo 12
8. Salva em `content_documents.slides_content`

### O framework AIDA

| Posição | Nome | O que o slide faz |
|---|---|---|
| 1 | **Hook** (Atenção) | Título impactante + frase que gera curiosidade ou identificação |
| 2 | **Transition** (Ponte) — opcional | Descreve a situação problemática do público |
| 3-N | **Tease** (Interesse) | Fatos, passos, argumentos, exemplos, ações concretas |
| N-1 | **Climax** (Desejo) | O "aha moment" — insight principal que muda a perspectiva |
| N | **Action** (Ação) | CTA claro: salvar, compartilhar, comentar |

### Níveis de personalização

| Nível | O que é injetado | Modelos que usam |
|---|---|---|
| **high** | Nome da marca, nicho, tom de voz, dor do público, transformação Y | storytelling, transformacao, antes_depois, estudo_caso, depoimento, bastidores, flash_sale |
| **medium** | Nicho, tom de voz, referência à dor | lista, tutorial, comparação, desafio, enquete, infográfico |
| **low** | Apenas tom de voz e nicho geral | citacao, motivacional, meme |

### As 7 regras globais de geração

| # | Regra | Por que |
|---|---|---|
| 1 | Máximo 2-3 frases curtas por slide | Slides com muito texto não funcionam no Instagram |
| 2 | 2-4 palavras por slide como highlighted | Highlights guiam o olho do leitor |
| 3 | Termine cada slide com micro-hook para swipe | Sem isso a pessoa para no slide 3 |
| 4 | Headline do slide 1: máximo 6 palavras | A capa precisa ser lida em 1 segundo |
| 5 | CTA claro e óbvio | CTA ambíguo = ninguém age |
| 6 | Português do Brasil, sem emojis | O Cadencia usa ícones Lucide, não emojis |
| 7 | Nunca use jargão técnico | Público-alvo inclui leigos em tecnologia |

### CTA dinâmico

| Situação | CTA gerado |
|---|---|
| Sem Instagram conectado | "Salve esse post para consultar depois." |
| Com Instagram conectado | "Comente {KEYWORD} para receber mais." (keyword do nicho em uppercase, máx. 12 chars) |

---

## Etapa 5 — Caption Agent

**Arquivo:** `cadencia-workers/src/workers/caption_agent/__init__.py` (116 linhas)
**max_tokens:** 1000

### Estrutura P/R/Cr/Cp/CTA

| Parte | Nome | O que é | Para que serve |
|---|---|---|---|
| P | **Pergunta** | Pergunta que as pessoas digitariam no Google | SEO |
| R | **Resposta** | Resposta direta em 1-2 frases | Satisfação imediata |
| Cr | **Contexto Raso** | Insight acessível que expande a resposta | Aprofunda sem complicar |
| Cp | **Contexto Profundo** | Conexão emocional com a dor ou desejo | Cria identificação e urgência |
| CTA | **Chamada para Ação** | Pede ação clara: salvar, compartilhar, comentar | Converte atenção em engajamento |

**Configurações:** máximo 300 palavras, 2-3 emojis, parágrafos de 2-3 linhas, 10-15 hashtags.

---

## Etapa 6 — Cover Generation

**Arquivo:** `cadencia-workers/src/workers/cover_generation.py` (431 linhas)

**Geração de capa é não-fatal.** Se falhar, pipeline continua com capa tipográfica.

### Árvore de decisão

1. Categoria do modelo é `"social"` (meme, citação, motivacional)? → **Pula a capa**
2. `cover_style == "person"` E tenant tem ≥1 foto? → **Modo Person** (foto com rosto real)
3. `cover_style == "thematic"` OU sem fotos? → **Modo Thematic** (cena sem rosto)

### Modo Person

1. Verifica se tenant tem `physical_description` salva
2. Se não: envia 1 foto ao Gemini 2.5 Flash e gera descrição física em 2-3 frases (custo único)
3. Seleciona cena aleatória das templates da editoria (3-4 opções)
4. Monta prompt com: **Identity Lock** + **Camera Specs** + **Scene**
5. Envia ao Gemini `gemini-3.1-flash-image-preview` com até 6 fotos de referência
6. Upload para `content/{tenant_id}/{doc_id}/cover.png` no Supabase Storage

**Identity Lock prompt:**
```
SUBJECT IDENTITY (must match ALL reference images exactly):
{physical_description}

CRITICAL FACE RULES:
- LEAN face with angular jawline — NOT round, NOT chubby.
- Do NOT make face rounder/fuller than references.
- Match EXACT facial proportions shown in references.
- Same eye shape, nose bridge contour, jawline angle, lip proportions.
- Same beard pattern, hair style, skin texture.
```

### Camera Specs por editoria

| Editoria | Câmera | Iluminação | Ângulo | Mood | WB | Saturação |
|---|---|---|---|---|---|---|
| **demonstrativa** | Canon EOS R5, 85mm f/1.4 | Warm studio, golden hour | Eye level, rule of thirds | Confiante, profissional | 5500K warm | Rich, boosted |
| **educativa** | Sony A7IV, 35mm f/1.8 | Soft natural window light | Levemente acima dos olhos | Acessível, calmo | 5200K neutral | Natural, clean |
| **confrontadora** | Canon EOS R5, 50mm f/1.2 | Dramatic side light | Abaixo dos olhos, dutch angle | Bold, intenso | 4800K cool | Dessaturado, moody |

**Regras comuns:** profundidade rasa, bokeh natural, leve grão, sem pele plástica. Formato 4:5 (1080x1350px). SEM texto, watermarks ou logos.

### Modo Thematic

Prompt simplificado com camera specs + cena + regra "sem pessoas". Geração via Gemini, sem Identity Lock.

---

## Notas Relacionadas

- [[Projetos/Cadencia/Docs/Motor-Grafico-Carrosseis-Doc-Tecnica]]
- [[Projetos/Cadencia/Docs/Motor-Parte2-Modelos-Templates-BD]]
- [[Projetos/Cadencia/Docs/PRD-Arquitetura-Tecnica]]
