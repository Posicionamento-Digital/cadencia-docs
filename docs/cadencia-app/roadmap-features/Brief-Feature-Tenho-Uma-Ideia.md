---
date: 2026-05-16
tags: [ia, tecnologia, automacao, briefing]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Karina Vieira]]", "[[financeiro]]", "[[marketing]]", "[[qualidade]]"]
---
# Brief — Feature: "Tenho uma Ideia"
## Entrada de conteúdo pelo cliente (chat, áudio, link)

**Projeto Linear:** https://linear.app/posicionamento-digital/project/prod-cadencia-roadmap-6475d91c6139
**Atualizado em:** 2026-05-16
**Preenchido por:** Felipe

---

## O que é e por que existe

Nova seção dentro de `/app/ideas` onde o cliente expressa suas ideias de 3 formas:

1. **Chat com LLM especializado** (texto) — PRIORIDADE, cliente já aguardando
2. **Envio de áudio** — transcreve e processa
3. **Envio de link** — artigo, vídeo YouTube, post de redes sociais

O agente ajuda a desenvolver o conteúdo via conversa. Ao finalizar, aparece um botão **"Gerar posts"** — o usuário escolhe os canais e os posts saem prontos, sem etapa de aprovação de ideia separada.

**Origem da demanda:**
- **Karina Vieira** (agência de marketing): gerencia 8+ clientes, usa ChatGPT com prompts específicos por cliente hoje. Quer digitar livremente como faz no ChatGPT, sem botões ou formulários guiados. Está comprando 3 contas Cadencia para substituir copywriters e social media. Clientes dela: enfermeira, cantinho de alfabetização, BPO financeiro, terapeuta transpessoal, psicanalista, espaço terapêutico, farmácia veterinária, psicóloga, medicina chinesa.
- **Dra. Nathalia Galardo** (dermatologista): demanda pelo link/áudio — quer transformar artigos científicos e referências externas em posts.
- Múltiplos outros clientes validaram a demanda independentemente.

**Por que chat e não formulário:** usuários se frustram com IA porque não sabem criar contexto suficientemente bom. O chat guia a extração do contexto correto através da conversa, gerando outputs melhores com menos esforço cognitivo.

---

## Fluxo do usuário

```
1. Usuário abre aba "Tenho uma Ideia"
2. Escolhe o modo: chat / áudio / link
3. [Chat] Conversa com o agente para desenvolver e refinar o conteúdo
4. Agente ajuda a estruturar: tema, ângulo, público, objetivo
5. Botão "Gerar posts" aparece quando conteúdo está desenvolvido
6. Usuário seleciona os canais desejados
7. Posts gerados pelo motor Cadencia (9 modelos, dossiê, ID visual)
8. Posts entram no fluxo normal — prontos, sem aprovação de ideia separada
```

---

## Stakeholders

- **Felipe** — decisão e configuração dos tenants da Karina (onboarding manual)
- **Karina Vieira** — usuária principal do chat, valida a feature
- **Dra. Nathalia Galardo** — usuária principal do link/áudio

---

## Estrutura de issues

Issue pai com 3 sub-issues independentes:

| Sub-issue | Escopo | Prioridade |
|---|---|---|
| Chat com LLM especializado | Texto livre via conversa → posts | URGENTE |
| Envio de áudio | Transcrição + processamento | Alta |
| Envio de link | Artigo, YouTube, redes sociais | Alta (discovery já existe) |

---

## Estado atual

- Discovery completo para "link" em `_bmad-output/feature-ideias-de-conteudo-externo/` (arquitetura Winston, análise Mary, decisões pendentes)
- Chat e áudio: briefing feito agora, arquitetura a definir no planejamento das issues
- Nenhuma linha de código escrita ainda

---

## Decisões arquiteturais tomadas (alto nível)

Arquitetura inspirada no Hermes Agent (NousResearch) — não reinventamos o que já foi resolvido.

**Referências Hermes consultadas:**
- Soul.md: https://hermes-agent.nousresearch.com/docs/guides/use-soul-with-hermes
- Context Files: https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files
- Memory Providers: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers

**Decisões tomadas:**

| Decisão | Escolha | Motivo |
|---|---|---|
| Memória de sessão | Supabase `chat_sessions` | Sem Redis — overkill para este caso de uso |
| Memória longa | Supabase pgvector (`tenant_memories`) | Infra já existente, busca semântica |
| Soul.md | Por tenant, em `tenant_config` | Gerado no onboarding, identidade do agente especializado |
| Embed de sessão | Destilação → embed → pgvector | Mem0 pattern: destila 3-5 fatos estruturados, não embeda bruto |
| System prompt | Imutável mid-session (frozen snapshot) | Prefix cache Anthropic — reduz custo |
| Recuperação de contexto | Tool calls on-demand | LLM busca o que precisa, não injeta tudo |
| Canal | Web-only agora | Outros canais = issue separada futura |
| Memória entre sessões | pgvector sem memory.md | Multi-tenant: arquivo por tenant não escala |

**Montagem do system prompt (ordem Hermes):**

```
#1  Soul.md do tenant       (~300-500 tokens, sempre injetado)
#2  Tool guidance            (schemas das tools disponíveis)
#3  Frozen memory snapshot   (top N memórias relevantes do pgvector)
#4  Retrieval on-demand      (dossiê, editorias, posts — só quando LLM pedir via tool call)
```

---

## Estratégia de rollout

**Não será liberada para todos os usuários imediatamente.**

Cadencia já tem sistema de feature flags (`/app/admin/flags`). Rollout em 3 fases:

1. **Fase 1 — Validação:** flag `feature_chat_ideas` ativa apenas nos tenants da Karina
2. **Fase 2 — Early access:** abrir para lista de usuários selecionados via admin
3. **Fase 3 — GA:** liberar para todos após validação completa

Nenhum ambiente preview separado necessário — feature flag por tenant resolve com menos complexidade.

---

## O que NÃO fazer

- **Não usar Redis** — overkill para sessão de chat criativo de baixo volume
- **Não usar memory.md por tenant** — cresce sem controle, não escala multi-tenant
- **Não injetar o dossiê inteiro no system prompt** — usar tool call on-demand
- **Não embedar a conversa bruta** — destila em fatos estruturados primeiro (3-5 por sessão)
- **Não construir outros canais agora** — WhatsApp etc. é issue separada
- **Não fazer onboarding self-service para clientes da Karina** — Felipe configura manualmente
- **Não misturar com fluxo de aprovação de ideia existente** — chat vai direto para geração de posts

---

## Issues adjacentes identificadas (não fazem parte desta feature)

1. **Login multi-conta para agências** — Karina faz login uma vez, alterna entre tenants
2. **Onboarding personalizado por Felipe** — configurar tenants manualmente para clientes de agências em vez do self-service
3. **Chat em outros canais** — WhatsApp, Telegram, etc.

---

## Dependências críticas

- Discovery "link/YouTube" existente deve ser consolidado na sub-issue 3
- Soul.md gerado no onboarding é pré-requisito para qualidade do chat
- Feature flags existentes no admin devem suportar ativação por tenant individual

---

## Critério de conclusão — Fase 1

- Karina abre o chat, conversa com o agente sobre a ideia de um cliente
- Agente refina o conteúdo via conversa e apresenta botão "Gerar posts"
- Karina escolhe os canais e recebe posts prontos pelo motor Cadencia
- O agente usa contexto do tenant (nicho, tom, marca) sem Karina precisar explicar
- Feature visível apenas para tenants com flag ativa

## Notas Relacionadas
[[Brief]] - [[Editorias]]
