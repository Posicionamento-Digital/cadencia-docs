---
date: 2026-05-14
tags: [cadencia, motor, grafico, modelos, templates, banco, dados, tecnico, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]"]
---
# Motor Gráfico — Parte 2: Modelos, Templates, Configurações e Banco de Dados

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.



Como o visual é renderizado, os 29 modelos de carrossel, os templates HTML/CSS, as configurações do tenant e o schema do banco de dados.

---

## Etapa 7 — Rendering (Motor de Renderização)

**Arquivo:** `cadencia-workers/src/workers/slide_renderer/__init__.py` (401 linhas)

Transforma slides (texto + variáveis visuais) em **imagens PNG de 1080x1440 pixels** via Playwright (Chromium headless).

### Fluxo

1. Recebe: tenant_id, document_id, slides, visual_identity, carousel_model, brand_handle, cover_image_path
2. Carrega template HTML do modelo (`{slug}.html`). Fallback para `storytelling.html` se não encontrar
3. Se há cover image: download da URL Supabase Storage → converte para base64 data URI
4. Para **cada slide**:
   - Monta variáveis: cores, fontes, texto, subtexto, tipo, número, highlights
   - Slide tipo `"cover"` com foto → HTML standalone com foto full-bleed + gradient overlay
   - Outros → substitui variáveis `{{var}}` no template HTML
   - Aplica highlights: envolve palavras em `<span>` com fundo accent
   - Injeta CSS de safe zones e tipografia mínima
   - Playwright carrega HTML no viewport 1080x1440 → screenshot PNG
   - Upload para Supabase Storage com 3 retries
   - Se upload falha após 3 tentativas → HEAD request para verificar se arquivo existe
5. Retorna lista de URLs
6. Orchestrator faz merge: adiciona `"url"` a cada slide → grava com status `"ready"`

### Dimensões e Safe Zones

| Parâmetro | Valor | Por que |
|---|---|---|
| Largura | 1080px | Padrão Instagram carrosséis |
| Altura | 1440px | Formato 3:4 — maior ocupação de tela no feed |
| Safe zone topo | 180px | Header do Instagram (nome + botões) cobre essa área |
| Safe zone base | 180px | Rodapé do Instagram (likes, comentários) |
| Safe zone esquerda | 50px | Respiro visual |
| Safe zone direita | 120px | Seta de "próximo slide" |

**Tipografia mínima:** headlines 50px, body text 14px.

### Mecanismo de Highlights

Para cada palavra em `highlighted_words`:
1. Busca case-insensitive no texto
2. Substitui primeira ocorrência por: `<span style="background-color: {accent_color}; padding: 2px 8px; border-radius: 4px; color: #FFFFFF;">{palavra}</span>`

### Upload para Supabase Storage

| Parâmetro | Valor |
|---|---|
| Bucket | `content` |
| Path | `{tenant_id}/{document_id}/slide_{NN}.png` |
| Método | httpx POST com `x-upsert: true` |
| Retries | 3 tentativas com 1s entre cada |
| Timeout | 30s por upload |
| URL pública | `{SUPABASE_URL}/storage/v1/object/public/content/{path}` |

---

## Os 29 Modelos de Carrossel

Definidos em arquivos YAML em `cadencia-workers/src/models/`.

| # | Slug | Nome | Categoria | Slides | Pers. | Editoriais |
|---|---|---|---|---|---|---|
| 1 | `lista` | Lista / Checklist | educacional | 7 | medium | educativa, demonstrativa |
| 2 | `tutorial` | Tutorial / Passo a passo | educacional | 8 | medium | educativa, demonstrativa |
| 3 | `dicas_rapidas` | Dicas Rápidas | educacional | 5 | medium | educativa, demonstrativa |
| 4 | `comparacao` | Comparação | educacional | 7 | medium | educativa, demonstrativa |
| 5 | `infografico` | Infográfico | educacional | 6 | medium | educativa, demonstrativa |
| 6 | `recapitulacao` | Recapitulação / Resumo | educacional | 7 | medium | educativa, demonstrativa |
| 7 | `analise_profunda` | Análise Profunda | educacional | 9 | medium | educativa, demonstrativa |
| 8 | `resenha` | Resenha / Review | educacional | 7 | medium | educativa, demonstrativa |
| 9 | `entrevista` | Entrevista | educacional | 7 | medium | educativa, demonstrativa |
| 10 | `storytelling` | Storytelling / Narrativa | narrativo | 8 | high | demonstrativa, confrontadora |
| 11 | `transformacao` | Transformação / Jornada | narrativo | 8 | high | demonstrativa, confrontadora |
| 12 | `antes_depois` | Antes e Depois | narrativo | 6 | high | demonstrativa, confrontadora |
| 13 | `expectativa_realidade` | Expectativa vs Realidade | narrativo | 7 | medium | confrontadora, educativa |
| 14 | `bastidores` | Bastidores | narrativo | 7 | high | social, demonstrativa |
| 15 | `estudo_caso` | Estudo de Caso | prova | 8 | high | demonstrativa, educativa |
| 16 | `depoimento` | Depoimento / Testemunho | prova | 5 | high | demonstrativa, social |
| 17 | `unboxing` | Unboxing / Revelação | prova | 6 | medium | demonstrativa, educativa |
| 18 | `citacao` | Citação Inspiradora | social | 3 | low | social, engajamento |
| 19 | `motivacional` | Mensagem Motivacional | social | 4 | low | social, engajamento |
| 20 | `meme_humor` | Meme / Humor | social | 3 | low | social, engajamento |
| 21 | `noticias` | Notícias / Boletim | social | 6 | low | educativa, confrontadora |
| 22 | `react_opinion` | React / Comentário | social | 5 | medium | educativa, social |
| 23 | `trend` | Trend | social | 5 | low | educativa, demonstrativa |
| 24 | `desafio` | Desafio | interativo | 7 | medium | educativa, demonstrativa |
| 25 | `enquete_qa` | Enquete / Q&A | interativo | 6 | medium | educativa, demonstrativa |
| 26 | `teste_quiz` | Teste / Avaliação | interativo | 6 | medium | educativa, demonstrativa |
| 27 | `feedback_respostas` | Feedback / Respostas | interativo | 6 | medium | educativa, demonstrativa |
| 28 | `flash_sale` | Flash Sale / Oferta | conversão | 4 | high | demonstrativa |
| 29 | `animacao_processo` | Animação / Processo Visual | visual | 5 | medium | educativa, demonstrativa |

### Categorias

| Categoria | Qtd | Comportamento especial |
|---|---|---|
| educacional | 9 | Nenhum |
| narrativo | 5 | Personalização high na maioria |
| social | 6 | meme, citação, motivacional **pulam geração de cover** |
| prova | 3 | Personalização high |
| interativo | 4 | Nenhum |
| conversão | 1 | Personalização high, poucos slides (4) |
| visual | 1 | Nenhum |

---

## Templates HTML/CSS

58 arquivos HTML (29 modelos × 2 variantes A/B) + 1 CSS base compartilhado.

**Fluxo:**
1. Renderer carrega `{slug}_a.html` ou `{slug}_b.html`
2. Substitui variáveis `{{var}}` pelos valores reais
3. Injeta CSS de safe zones e tipografia mínima
4. Playwright renderiza → screenshot 1080×1440 PNG

### CSS Base — Classes disponíveis

| Classe | O que é | Valores atuais |
|---|---|---|
| `.slide` | Container principal | 1080×1440px, overflow hidden |
| `.slide-content` | Área de conteúdo | Padding: 180px topo, 120px direita, 180px base, 50px esquerda |
| `.headline` | Título principal | 55px, weight 800, letter-spacing -0.02em |
| `.subtitle` | Subtítulo | 24px, weight 400, line-height 1.4 |
| `.body-text` | Texto de corpo | 22px, weight 400, line-height 1.5 |
| `.body-text-large` | Texto maior | 28px, weight 600, line-height 1.3 |
| `.label` | Label pequeno | 14px, uppercase, letter-spacing 0.15em |
| `.highlight` | Destaque fundo colorido | Fundo accent, padding 4×12px, radius 6px, texto branco |
| `.highlight-underline` | Destaque sublinhado | Border-bottom 4px accent |
| `.big-number` | Número decorativo fundo | 180px, weight 900, opacity 0.15, absolute |
| `.step-number` | Número de passo | 72px, weight 800, cor accent |
| `.hero-number` | Número central destaque | 180px, weight 900, cor primary, text-shadow |
| `.quote-mark` | Aspas decorativas | 240px Georgia, opacity 0.3, absolute |
| `.quote-text` | Texto de citação | 36px, italic, weight 700 |
| `.bg-dark` | Fundo escuro | Background: color_primary, texto branco |
| `.bg-light` | Fundo claro | Background: color_bg, texto color_text |
| `.bg-accent` | Fundo accent | Background: color_accent, texto branco |
| `.photo-bg` | Foto de fundo | Background-size: cover, center |
| `.photo-gradient-bottom` | Gradiente inferior | 60% da altura, preto 0.85→transparente |
| `.photo-gradient-full` | Gradiente completo | 135deg, preto 0.7→0.3 |
| `.cta-button` | Botão visual de CTA | Padding 20×48px, radius 16px, fundo accent, texto branco |
| `.cta-keyword` | Keyword grande | 48px, weight 900, cor accent |
| `.brand-handle` | Watermark @handle | 16px, weight 500, opacity 0.7 |
| `.slide-counter` | Contador "3/8" | 14px, opacity 0.5, canto superior direito |
| `.progress-bar` | Barra de progresso | 4px de altura, fill com cor accent |
| `.checklist-item` | Item de checklist | Flex, gap 16px |
| `.check-icon` | Ícone de check | 28px, fundo accent, SVG branco |
| `.cards-container` | Container de cards | Flex, gap 24px |
| `.card` | Card individual | Padding 32px, radius 16px |
| `.accent-line` | Linha vertical | 4px largura, height 100%, left absolute |
| `.divider` | Divisor horizontal | 60×4px, cor accent, radius 2px |

### Variáveis disponíveis nos templates

| Variável | De onde vem | Exemplo |
|---|---|---|
| `{{color_primary}}` | Visual identity | `#4F46E5` |
| `{{color_secondary}}` | Visual identity | `#7C3AED` |
| `{{color_accent}}` | Visual identity | `#F59E0B` |
| `{{color_bg}}` | Visual identity | `#FFFFFF` |
| `{{color_text}}` | Visual identity | `#111827` |
| `{{font_heading}}` | Visual identity | `Inter` |
| `{{font_body}}` | Visual identity | `Inter` |
| `{{text}}` | Texto principal (com highlights HTML) | "De confusa a vendável." |
| `{{subtext}}` | Texto de suporte | "Veja essa virada." |
| `{{slide_type}}` | Tipo do slide (YAML) | `capa`, `corpo`, `cta` |
| `{{slide_number}}` | Número sequencial | `1`, `2`, `3` |
| `{{headline}}` | Título (só na capa) | "De confusa a vendável." |
| `{{brand_handle}}` | @handle do profissional | `@felipeconsultoria` |
| `{{cta_label}}` | Texto do botão CTA | "Salvar este post" |
| `{{icon}}` | Emoji/ícone | "💡" |

---

## Editorias (por tenant)

Armazenadas em `tenant_editorials`. Cada ideia pertence a uma editoria. Cada tenant tem tipicamente 3.

### Campos de cada editoria

| Campo | Para que serve | Onde é usado |
|---|---|---|
| `name` | Identificação visual | Prompts de research, carousel, caption |
| `objective` | O que o tipo de post busca alcançar | Contexto para geração de ideias |
| `tone` | Como o texto deve "soar" | Headline, carousel, caption agents |
| `topics` | Temas sugeridos | Ideas agent |
| `audience_pains` | Dores do público que a editoria resolve | Ideas agent, prompts |
| `headline_rule` | Regra específica para headlines | Headline agent |
| `calendar_weight` | Peso no calendário (0.0 a 1.0) | Distribuição de ideias no cron |
| `editorial_function` | Função editorial | Model selection, cover generation |
| `cover_style` | "person" ou "thematic" | Cover generation |

### Funções editoriais disponíveis

| Função | Camera specs | Modelos compatíveis |
|---|---|---|
| `demonstrativa` | Warm studio, confiante | storytelling, transformacao, estudo_caso, lista |
| `confrontadora` | Dramatic, moody | storytelling, expectativa_realidade, antes_depois |
| `educativa` | Soft, natural | lista, tutorial, dicas, comparacao, infografico |
| `social` | N/A (sem cover) | citacao, motivacional, bastidores |
| `engajamento` | N/A (sem cover) | citacao, motivacional, meme |

---

## Visual Identity (por tenant)

Gerada automaticamente a partir do logo no onboarding. Armazenada em `tenant_visual_identity`.

| Campo | Onde é usado | Exemplo |
|---|---|---|
| `palette.primary` | Fundo dark, headlines, elementos principais | `#4F46E5` (indigo) |
| `palette.secondary` | Gradientes, detalhes secundários | `#7C3AED` (roxo) |
| `palette.accent` | Botões CTA, highlights, dividers, check icons | `#F59E0B` (amarelo) |
| `palette.background` | Fundo de slides claros | `#FFFFFF` |
| `palette.text` | Texto de corpo em slides claros | `#111827` |
| `fonts.heading` | Headlines, labels, botões | `Inter` |
| `fonts.body` | Texto de corpo, subtextos, handle | `Inter` |

---

## Config do Tenant (`tenant_config`)

| Campo | Para que serve | Onde é usado |
|---|---|---|
| `nicho` | Filtra modelos, personaliza prompts | Model selection, todos os prompts |
| `nome_empresa` | Nome da marca | Carousel agent (level high) |
| `fotos_rosto_urls` | Fotos de referência | Cover generation (Modo Person) |
| `physical_description` | Descrição física (auto-gerada) | Cover generation |
| `content_restrictions` | Guardrail absoluto ("nunca falar de X") | Carousel agent |
| `multi_version_enabled` | Gera 3 versões por ideia | Pipeline, Ideas |
| `schedule.active` | Habilita cron diário | Cron |
| `schedule.days` | Dias da semana para gerar | Cron |
| `auto_approve_ideas` | Pula o swipe e gera direto | Ideas |

---

## Pipeline Global e Cron

### Pipeline Settings

| Config | Valor atual |
|---|---|
| Modelo LLM | GPT-5.4 (via OpenAI API) |
| Max retries LLM | 3 tentativas, backoff exponencial (2s, 4s, 8s) |
| Timeout LLM | 120s |
| Anti-repetição | Últimos 3 modelos excluídos |
| Min slides | 3 (validação Pydantic) |
| Max slides | 12 (validação Pydantic) |
| Regenerações máximas | 3 por documento |
| Prioridade pagos | 1 (jobs de pagos rodam primeiro) |
| Prioridade trial | 0 |

### Cron Diário

**Endpoint:** `POST /api/v1/cron/daily` com header `x-cron-secret` (chamado pelo cron-job.org às 8h BRT)

**Fluxo:**
1. Verifica secret
2. Busca tenants com `schedule.active = true` e dia atual em `schedule.days`
3. Para cada tenant: verifica idempotência → gera 5-10 ideias distribuídas entre as 3 editorias → insere como `"approved"` → cria jobs no pipeline

---

## Geração de Ideias

**Arquivo:** `cadencia-workers/src/workers/ideas.py`

**Prompt:**
```
Você é um estrategista de conteúdo para Instagram.
Gere entre 5 e 10 ideias de carrosséis para este profissional,
distribuídas entre as 3 editorias abaixo.

REGRAS:
- Distribua: ~40% editorial 0, ~35% editorial 1, ~25% editorial 2.
- Títulos: máximo 12 palavras.
- Score: 0.0 a 1.0 indicando relevância/potencial.
- Keywords: 3-5 palavras-chave.
- Tudo em pt-BR. NÃO repita temas.

EDITORIAS: [bloco com as 3 editorias do tenant]
CONTEXTO: nicho, posicionamento (300 chars), público (300 chars), tom (200 chars)
```

---

## Publicação no Instagram

**Arquivo:** `cadencia-workers/src/workers/instagram_publisher.py` (208 linhas)

**Fluxo:**
1. Busca `social_connections` → descriptografa `access_token` (XOR com `TOKEN_ENCRYPTION_KEY`)
2. Cria containers filhos: POST para cada slide PNG com `is_carousel_item=true`
3. Cria container do carrossel: POST com `media_type=CAROUSEL` + todos os IDs + caption
4. Publica: POST em `media_publish`
5. Busca permalink: GET no media publicado
6. Atualiza banco: `publish_status="published"`, `instagram_media_id`, `instagram_permalink`

**Config:** Graph API `v21.0`, mínimo 2 slides (exigência do Instagram)

---

## Token Refresh

**Arquivo:** `cadencia-workers/src/workers/token_refresh.py` (106 linhas)

- Roda diariamente via cron
- Busca conexões com `token_expires_at < agora + 10 dias`
- Chama `GET refresh_access_token` na Graph API
- Sucesso: atualiza token criptografado + `token_expires_at` + `last_refresh_at`
- Falha: marca como `"expired"` e loga

---

## Schema do Banco de Dados

| Tabela | Campos principais | Propósito |
|---|---|---|
| `content_documents` | id, tenant_id, idea_id, status, carousel_model, headline_id, slides_content, caption, hashtags, publish_status, instagram_media_id, regeneration_count | Documento principal do carrossel |
| `content_ideas` | id, tenant_id, editorial_id, title, description, score, keywords, status, source | Ideias de posts |
| `content_headlines` | id, tenant_id, content_document_id, headline, subtitle, hook_type, focus_keyword | Headlines geradas |
| `research_documents` | id, tenant_id, idea_id, data, nicho, editorial_function, topic_cluster, keywords | Documentos de pesquisa |
| `generation_queue` | id, tenant_id, content_idea_id, status, priority, started_at, completed_at, version_index | Fila de geração |
| `pipeline_status` | id, tenant_id, generation_queue_id, current_step, progress, error | Progresso em tempo real |
| `tenant_config` | tenant_id, config (JSON) | Configurações gerais |
| `tenant_dossier` | tenant_id, data (JSON) | Dossiê da marca |
| `tenant_editorials` | id, tenant_id, name, objective, tone, editorial_function, headline_rule, topics, audience_pains, cover_style, calendar_weight | Editorias |
| `tenant_visual_identity` | tenant_id, data (JSON) | Paleta e fontes |
| `tenant_profile` | tenant_id, data | Perfil do onboarding |
| `tenant_plans` | tenant_id, plan_name, status | Plano ativo |
| `profile_responses` | tenant_id, question_key, trait, score | Profiling comportamental |
| `social_connections` | id, tenant_id, provider, username, access_token_encrypted, token_expires_at, connection_status | Conexões OAuth |
| `publish_jobs` | id, tenant_id, content_document_id, social_connection_id, status, instagram_media_id | Jobs de publicação |
| `api_call_logs` | tenant_id, task_type, provider, model, input_tokens, output_tokens, cost_usd, latency_ms | Log de custos |
| `credit_transactions` | tenant_id, operation_type, credits_consumed, cost_breakdown | Controle de créditos |

---

## Variáveis de Ambiente

| Variável | Usada por | Propósito |
|---|---|---|
| `OPENAI_API_KEY` | llm.py | Autenticação OpenAI |
| `GEMINI_API_KEY` | cover_generation.py | Autenticação Google Gemini |
| `SUPABASE_URL` | config.py | Endpoint do banco |
| `SUPABASE_SERVICE_ROLE_KEY` | config.py | Chave de serviço (bypassa RLS) |
| `SUPABASE_JWT_SECRET` | config.py | Secret para JWTs |
| `TOKEN_ENCRYPTION_KEY` | instagram_publisher.py, token_refresh.py | Criptografia XOR para tokens OAuth |
| `META_APP_SECRET` | fallback | Secret do app Meta |
| `CRON_SECRET` | cron.py | Autenticação do cron |
| `GHL_API_KEY` | config.py | API GoHighLevel |
| `ASAAS_API_KEY` | config.py | API Asaas (pagamentos) |
| `SENTRY_DSN` | config.py | Error tracking |

---

## Custos por modelo LLM (estimativa, USD/token)

| Modelo | Input | Output |
|---|---|---|
| gpt-5.4 | $0.000003 | $0.000015 |
| gpt-4.1 | $0.000002 | $0.000008 |
| gpt-4.1-mini | $0.0000004 | $0.0000016 |

---

## Notas Relacionadas

- [[Projetos/Cadencia/Docs/Motor-Grafico-Carrosseis-Doc-Tecnica]]
- [[Projetos/Cadencia/Docs/Motor-Parte1-Pipeline-Agentes-Prompts]]
- [[Projetos/Cadencia/Docs/PRD-Arquitetura-Tecnica]]
