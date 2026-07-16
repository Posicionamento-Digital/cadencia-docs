# Feature: Growth Newsletter

> **ARQUIVO HISTORICO / LEGADO.** Preservado como memoria tecnica; nao descreve o runtime atual e nao deve ser usado como runbook operacional.

Newsletter semanal compilada por IA com os posts da semana, disparada via GHL.

**Status:** Produção — funcional
**Última atualização:** 2026-05-19
**Fonte:** `pipeline/newsletter_generate.py` (repo canônico `Posicionamento-Digital/cadencia-growth`)

---

## Fluxo completo

```
Sexta 15h BRT (18h UTC)
       │
       ▼
growth_pipeline.py newsletter
       │
       ▼
newsletter_generate.py <tenant_id>
       │
       ├── Valida GHL config (location_id + location_pit_token)
       ├── Busca contatos no GHL — aborta se 0 contatos (evita custo LLM)
       ├── Busca published_posts com newsletter_included=false
       ├── Gera newsletter via gpt-5.4 → JSON {subject, preheader, intro, posts[], closing}
       ├── Renderiza HTML via render_newsletter_html() com visual identity do tenant
       ├── Envia para todos os contatos via POST /conversations/messages
       └── Marca newsletter_included=true nos posts (só se enviou >= 1 contato)
```

---

## Query dos posts

```sql
SELECT * FROM published_posts
WHERE tenant_id = '<id>'
  AND newsletter_included = false
ORDER BY published_at ASC
```

**Sem filtro de data** — qualquer post com `newsletter_included=false` entra na próxima newsletter, independente de quando foi publicado. Se o cron falhar na sexta e rodar no sábado, os posts não se perdem.

---

## Geração do conteúdo (LLM)

**Modelo:** `gpt-5.4` | `max_completion_tokens: 2048`

**Input para o LLM:**
- Brand voice e ICP do `tenant_dossier`
- Dados dos posts: título, headline, corpo, URL

**Output esperado — JSON:**
```json
{
  "subject": "...",
  "preheader": "...",
  "intro": "...",
  "posts": [
    {"title": "...", "url": "...", "teaser": "..."}
  ],
  "closing": "..."
}
```

**Fallback:** se o LLM não retorna JSON válido, a função monta estrutura básica com título + link dos posts.

### Como cada post entra na newsletter

Não é título + link. Não é parágrafo recortado do artigo. O LLM gera bloco editorial original por post:

```
**[Headline]**
[Resumo com ângulo jornalístico — por que importa para o leitor]
[Dado ou insight-chave]
→ Leia o post completo: [link]
```

Ordem dos posts: por relevância editorial, não cronológica.

---

## Template HTML — `render_newsletter_html()`

```python
render_newsletter_html(
    subject, preheader, intro,
    posts,          # lista de {title, url, teaser}
    closing,
    brand_name,
    palette, fonts,
    edition_label,  # "Edição da semana — DD de mês de YYYY"
)
```

Regras de entregabilidade (anti-bounce):
- Mínimo 60% texto, 400+ chars de texto puro
- Máximo 2-3 imagens em toda a newsletter
- CTAs como texto HTML, nunca imagem
- Alt text obrigatório em imagens

---

## Envio via GHL

**Mesmo mecanismo do Seinfeld** — API direta de conversas, não workflow:

```python
for contact in contacts:
    conv_id = get_or_create_conversation(contact_id, location_id, api_key)
    POST /conversations/messages  {type: 'Email', html: newsletter_html, ...}
```

**Por que não workflow:** workflows GHL não aceitam HTML customizado no payload.

**Remetente:** `{brand_name} <noreply@mail.cadencia.app.br>`

**Guard de segurança:** marca `newsletter_included=true` nos posts **somente** se `ok > 0` (ao menos 1 envio bem-sucedido). Se todos os envios falharem, a newsletter rodará novamente no próximo cron sem duplicar.

---

## Credencial GHL

O script usa `ghl.location_pit_token`. Para tenants white-glove com `api_key`, gravar os dois campos:

```json
{
  "ghl": {
    "location_id": "...",
    "location_pit_token": "pit-..."
  }
}
```

---

## Banco de dados

| Coluna | Comportamento |
|---|---|
| `newsletter_included` | `false` = ainda não entrou em nenhuma newsletter. `true` = já foi incluído, nunca entra novamente. |

Não há tabela separada de histórico de newsletters — o controle é feito pelo flag no post.

---

## Frontend — NutricaoClient

**Aba Newsletter:**
- Barra de progresso: `newsletter_included=false` posts dos últimos 7 dias vs. 7 (meta semanal)
- Estado "em construção" se < 7 posts acumulados

---

## 🚫 Don'ts

- Nunca usar DELETE + POST para enrolar contato no GHL — DELETE não cancela emails enfileirados, POST recria duplicando o envio. Usar apenas POST (422 = idempotente, tratar como sucesso).
- Nunca marcar `newsletter_included=true` antes de confirmar envio (`ok > 0`).
- Nunca filtrar posts por data — posts antigos não incluídos devem entrar na próxima newsletter.
- Nunca chamar LLM sem verificar contatos GHL — desperdício de tokens se sub-conta vazia.

---

## Diferenças Cadencia vs PD Marketing

| Aspecto | PD Marketing | Cadencia |
|---|---|---|
| Fonte dos posts | Notion database | Supabase `published_posts` |
| Entrega | GHL workflow | `POST /conversations/messages` direto |
| Deduplicação | `last_newsletter_date` custom field no contato | `newsletter_included` flag no post |
| Filtro de posts | `published_at >= hoje - 7 dias` | Sem filtro — todos `newsletter_included=false` |
| HTML | Markdown → WordPress | HTML direto gerado pelo Cadencia |

---

## Pendências

- [ ] Paginação de contatos GHL (hoje limite de 100)
- [ ] Endpoint "Gerar agora" no Next.js (envio manual fora do cron de sexta)
- [ ] Campo `last_newsletter_date` no contato GHL para deduplicação por contato (vs. por post)
