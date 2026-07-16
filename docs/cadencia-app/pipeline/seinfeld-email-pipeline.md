# Pipeline de Email Seinfeld — Documentação Técnica

> **ARQUIVO HISTORICO / LEGADO.** Preservado como memoria tecnica; nao descreve o runtime atual e nao deve ser usado como runbook operacional.

**Última atualização:** 2026-05-19
**Fonte:** `pipeline/seinfeld_generate.py` (repo canônico `Posicionamento-Digital/cadencia-growth`)

---

## O que é

Email diário de nutrição de leads gerado por IA. Técnica Seinfeld: história cotidiana concreta → virada de significado → conexão com o problema do ICP. Sem pitch, sem vender. Disparado para todos os contatos GHL da sub-conta do tenant via API direta de conversas.

---

## Arquitetura

```
Aprovação de ideia (frontend)
    │
    ▼
POST /api/app/trigger-generation (Next.js)
    │
    ▼
POST http://72.60.4.71:8767/trigger (trigger_server.py)
    │
    ├── blog_generate.py      → cria published_post no Supabase
    │
    └── seinfeld_generate.py --generate
          → busca próximo published_post sem seinfeld agendado
          → LLM gera subject + preheader + body (gpt-5.4)
          → calcula próximo slot livre (1 email/dia, FIFO)
          → salva: seinfeld_subject, seinfeld_body, seinfeld_scheduled_at
          → NÃO dispara ainda

Cron 11h BRT (14h UTC) — diário:
    │
    ▼
growth_pipeline.py seinfeld → loop por todos os tenants Growth
    │
    ▼
seinfeld_generate.py --dispatch
    ├── busca published_posts com seinfeld_scheduled_at = hoje + seinfeld_sent=false
    ├── renderiza HTML via render_email_html() com visual identity do tenant
    ├── busca todos os contatos GHL da sub-conta (GET /contacts/?locationId=...)
    ├── para cada contato com email:
    │       → get_or_create_conversation() via GHL
    │       → POST /conversations/messages com HTML completo
    └── marca seinfeld_sent=true no banco
```

---

## Dois modos de operação

### `--generate` (on-demand ao aprovar ideia)

1. Verifica `config.ghl.location_id` — aborta se ausente
2. Verifica contatos no GHL **antes** de chamar LLM (evita custo se sub-conta vazia)
3. Busca próximo `published_post` com `seinfeld_sent=false` e `seinfeld_scheduled_at IS NULL`, ordem `published_at ASC` (FIFO)
4. Carrega `tenant_dossier` (brand_name, brand_voice, ICP)
5. Chama `gpt-5.4` com `build_seinfeld_prompt()` → JSON `{subject, preheader, body}`
6. Calcula próximo slot livre: varre `seinfeld_scheduled_at` dos posts existentes, encontra primeiro dia sem colisão
7. Salva no banco: `seinfeld_subject`, `seinfeld_body`, `seinfeld_scheduled_at`
8. **NÃO** marca `seinfeld_sent=true` — apenas agenda

### `--dispatch` (cron 11h BRT)

1. Busca posts com `seinfeld_scheduled_at::date = hoje` e `seinfeld_sent=false`
2. Para cada post:
   - Carrega `tenant_visual_identity` (palette + fonts)
   - `brand_name` → prioridade: `config.nome_empresa` > `dossier.brand_name` > `"Cadencia"`
   - Busca todos os contatos GHL: `GET /contacts/?locationId=...&limit=100`
   - Para cada contato com email: renderiza HTML personalizado + envia via conversas GHL
   - Marca `seinfeld_sent=true`

---

## Envio via GHL — API direta de conversas

**Por que não workflow GHL:** workflows não aceitam HTML customizado no payload. O GHL executa o template interno — sem acesso ao HTML gerado pelo Cadencia.

```python
# Fluxo por contato:
conv_id = get_or_create_conversation(contact_id, location_id, api_key)
payload = {
    'type': 'Email',
    'contactId': contact_id,
    'conversationId': conv_id,
    'subject': subject,
    'html': html_body,
    'emailTo': email,
    'emailFrom': f'{brand_name} <noreply@mail.cadencia.app.br>',
}
POST /conversations/messages
```

**Remetente:** `{nome_empresa} <noreply@mail.cadencia.app.br>`
**Personalização:** `greeting = "Bom dia, {firstName},"` — fallback `"Bom dia,"` se sem nome

---

## Credencial GHL — campo obrigatório

Os scripts buscam `ghl.location_pit_token` no `tenant_config`. **Não `api_key`.**

```python
api_key = ghl_cfg.get('location_pit_token', '')
```

Para tenants provisionados via white-glove (que usam `api_key`), é obrigatório gravar também `location_pit_token` com o mesmo valor. Caso contrário, as chamadas GHL falham silenciosamente (string vazia como bearer token).

**Config mínima obrigatória:**
```json
{
  "ghl": {
    "location_id": "...",
    "location_pit_token": "pit-..."
  },
  "nome_empresa": "Nome da Marca"
}
```

---

## Slot de agendamento

Regra: **máximo 1 email por dia por tenant.**

```python
def next_available_slot(tenant_id):
    # Lê todos os seinfeld_scheduled_at do tenant
    # Encontra primeiro dia a partir de hoje sem colisão
    # Retorna datetime UTC equivalente a 11h BRT desse dia
```

Se todos os próximos 60 dias estiverem ocupados: usa o dia 61 (fallback extremo).

---

## Template de email

```python
render_email_html(
    subject, preheader, body_text,
    brand_name, palette, fonts,
    blog_url='', greeting='',
    cta_label='Ler artigo completo',
)
```

Estrutura HTML gerada:
```
[Header: fundo palette.primary, brand_name em branco]
[Greeting personalizado em negrito]
[Parágrafos do seinfeld_body]
[Botão CTA: palette.accent, linka blog_url]
[Divider]
[Footer: brand_name · Cancelar inscrição]
```

Todos os campos texto passam por `html.escape()` antes de interpolação.

---

## Prompt Seinfeld

**Estrutura obrigatória — 4 parágrafos:**
1. História cotidiana — específica, crua, concreta. "Aconteceu ontem."
2. A virada — detalhe que muda o significado da história
3. Conexão com o problema do ICP — sem explicar demais
4. Encerramento com impacto ou pergunta reflexiva — sem links nem CTAs

**Regras anti-guru:**
- Sem linguagem de coach, "transformação", "jornada", "mindset"
- Sem exclamação
- Sem metáforas clichê
- Método, não ferramenta

**Regras de subject (anti-spam):**
- Sem emojis, CAPS, exclamação
- Sem: "grátis", "exclusivo", "urgente", "clique"
- Curiosity gap — sugere sem entregar
- Máximo 50 chars

---

## Banco de dados — `published_posts`

| Coluna | Tipo | Descrição |
|---|---|---|
| `seinfeld_subject` | text | Assunto gerado pelo LLM |
| `seinfeld_body` | text | Corpo em texto puro (parágrafos `\n\n`) |
| `seinfeld_scheduled_at` | timestamptz | Quando será/foi disparado (UTC) |
| `seinfeld_sent` | boolean | true após dispatch bem-sucedido |

---

## Variáveis de ambiente (VPS `/cadencia/.env`)

| Variável | Descrição |
|---|---|
| `SUPABASE_URL` | URL do projeto Supabase |
| `SUPABASE_SERVICE_KEY` | Service role key |
| `OPENAI_API_KEY` | Chave OpenAI (gpt-5.4) |

---

## Comandos operacionais

```bash
# Gerar email para tenant (on-demand, não dispara)
python3 /cadencia/pipeline/seinfeld_generate.py <tenant_id> --generate

# Gerar em modo dry-run (não salva no banco)
python3 /cadencia/pipeline/seinfeld_generate.py <tenant_id> --generate --dry-run

# Disparar emails agendados para hoje
python3 /cadencia/pipeline/seinfeld_generate.py <tenant_id> --dispatch

# Dry-run do dispatch
python3 /cadencia/pipeline/seinfeld_generate.py <tenant_id> --dispatch --dry-run

# Forçar re-dispatch (resetar campos via Supabase REST)
curl -X PATCH "$SUPABASE_URL/rest/v1/published_posts?id=eq.<post_id>" \
  -H "apikey: $SVC_KEY" -H "Content-Type: application/json" \
  -d '{"seinfeld_sent": false, "seinfeld_scheduled_at": null}'

# Ver logs
tail -f /cadencia/logs/trigger.log
```

---

## Crontab (VPS)

```cron
# Seinfeld — 11h BRT (14h UTC), diário
0 14 * * * /usr/bin/python3 /cadencia/crons/growth_pipeline.py seinfeld
```

---

## 🚫 Don'ts

- Nunca usar `api_key` diretamente — o script lê `location_pit_token`. Gravar os dois campos.
- Nunca usar GHL workflows para envio — não aceitam HTML customizado.
- Nunca enviar sem verificar contatos — chamada LLM é cara; verificar contatos primeiro.
- Nunca commitar `/cadencia/.env` — credenciais em arquivo local na VPS.

---

## Limitações conhecidas

| Limitação | Impacto | Caminho |
|---|---|---|
| `GET /contacts/?locationId=...&limit=100` | Só pega os primeiros 100 contatos | Implementar paginação com cursor |
| Domínio de envio fixo (`mail.cadencia.app.br`) | Domínio da agência, não do tenant | Tenant configura domínio próprio no GHL location |
| Sem tracking nativo de abertura | Score de lead não atualiza por abertura | Pixel futuro via webhook_handler.py |
| `firstName` depende do GHL | Contatos sem nome recebem "Bom dia," | Garantir `firstName` nos CSVs importados |
