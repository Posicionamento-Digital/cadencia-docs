---
date: 2026-05-19
tags: [documentacao, cadencia, growth, newsletter, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
---
## Identidade
- **Tipo:** feature Growth — email semanal
- **Stack:** Python 3.12, OpenAI gpt-5.4, GHL API
- **Path no repo:** `cadencia-growth/pipeline/newsletter_generate.py`
- **Status:** Produção — funcional

## O que é
Newsletter semanal compilada por IA com os posts publicados desde a última edição, disparada toda sexta às 15h BRT.

## Como funciona
Cron sexta 15h BRT → busca todos `published_posts` com `newsletter_included=false` (sem filtro de data) → LLM gera JSON com subject, intro, cards por post, closing → renderiza HTML → envia via POST /conversations/messages → marca newsletter_included=true.

## Quirk importante
Sem filtro de data — posts não incluídos acumulam para a próxima edição. Isso é intencional: protege contra falha do cron na sexta.

## Pendências
- Paginação de contatos GHL (hoje limit=100)
- Endpoint "Gerar agora" no Next.js

## Notas Relacionadas
[[growth-email-dispatch]] · [[growth-lead-scoring]]
