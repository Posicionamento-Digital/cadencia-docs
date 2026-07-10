# seinfeld-email — email Seinfeld diário

> ⚠️ **Provedor de envio migrou GHL → Resend (CAD-675/676).** O envio agora é
> **per-tenant** via `email_warmup.resolve_email_provider(config)`: se
> `config.email.provider == 'resend'` (padrão dos tenants novos), envia pelo
> **Resend** com contatos do CRM próprio (Supabase) e domínio próprio do tenant
> (`<sub>.cadencia.app.br`) — **sem depender do GHL**. O caminho GHL abaixo
> (`location_pit_token`, `/conversations/messages`) é **legado**, mantido só para
> tenants antigos ainda não flipados. **Fonte da verdade do estado atual:**
> [`email-warmup-cutover.md`](email-warmup-cutover.md) + [`email-domain-provisioning.md`](email-domain-provisioning.md).

## TL;DR

Envia 1 email por dia para cada contato do tenant, pelo **provedor resolvido por tenant**
(Resend ativo; GHL legado). Dois modos independentes: `--generate` (cria rascunho ao
aprovar ideia) e `--dispatch` (dispara no horário agendado, respeitando o cap de warm-up).

## Identidade

- **Tipo:** Python script
- **Path:** `/cadencia/pipeline/seinfeld_generate.py` (VPS Master)
- **Status:** ativo
- **Deps:** `email_warmup.resolve_email_provider` (provedor per-tenant) · **Resend** (`resend_send`, contatos via `get_subscribed_contacts` do CRM) · Supabase `published_posts` · GHL `location_pit_token` **(legado, só tenants antigos)**

## Modo --generate (on-demand, ao aprovar ideia)

> No caminho **Resend** (ativo), a geração é igual (gera subject+body e agenda o slot);
> o que muda é o **dispatch** (envio via Resend + contatos do CRM + cap de warm-up).
> O passo 1 abaixo (`config.ghl.*`) só se aplica ao **GHL legado**.

1. Busca `config.ghl.location_id` e `config.ghl.location_pit_token` do tenant
2. Chama `GET /contacts/` — se 0 contatos: aborta sem erro
3. Busca `published_posts` com `seinfeld_scheduled_at IS NULL AND seinfeld_sent=false` (FIFO)
4. Gera subject + body via LLM
5. Calcula próximo slot livre (1 email/dia, sem colisão com outros agendados)
6. Salva `seinfeld_subject`, `seinfeld_body`, `seinfeld_scheduled_at`
7. **NÃO dispara. NÃO marca `seinfeld_sent=true`.**

## Modo --dispatch (cron 11h BRT diário)

`provider = resolve_email_provider(config)` decide o caminho:

**Resend (ativo):** aplica `warmup_daily_cap(config, hoje BRT)` (cap 0 = pula); busca
`get_subscribed_contacts(tenant_id, limit=cap)` (contatos do CRM, ordenados por score,
filtrando `auto_email_enabled`); envia via `send_email_resend` do subdomínio próprio
do tenant. Detalhe: [`email-warmup-cutover.md`](email-warmup-cutover.md).

**GHL (legado):** o fluxo abaixo.
1. Busca posts com `seinfeld_scheduled_at` ENTRE `hoje 00:00 BRT` e `hoje 23:59 BRT` e `seinfeld_sent=false`
2. **Posts com data passada ficam presos para sempre** — dispatch só pega hoje exato (G001)
3. Para cada contato: `get_or_create_conversation()` → `POST /conversations/messages` (type=Email)
4. `emailFrom`: `{brand_name} <noreply@mail.cadencia.app.br>`
5. Marca `seinfeld_sent=true`

## Gotchas críticos

- **G001:** data passada = post preso. Fix: `UPDATE published_posts SET seinfeld_scheduled_at = NULL` para reagendar
- **G007:** usa `location_pit_token`, NÃO `api_key` — são tokens diferentes
- Não usa GHL Workflows — chama API GHL diretamente
- Dados ficam em `published_posts`, não em tabela separada

## Don'ts

- Nunca usar `api_key` global — seinfeld requer `location_pit_token` por tenant
- Não alterar a query de dispatch sem considerar o range BRT exato

---

## Quando usar

- **`--generate`**: chamada em sequência pelo `growth_pipeline.py` (cron 11h BRT) ou pelo `trigger_server.py` quando usuário aprova ideia. Agenda próximo Seinfeld no slot livre.
- **`--dispatch`**: chamada em sequência pelo cron 11h BRT depois do `--generate`. Pega só posts agendados para `hoje` exato.

## Quando NÃO usar

- ❌ Para enviar email transacional — usar GHL workflow direto.
- ❌ Para tenant sem `location_pit_token` em `config.ghl` (G007).
- ❌ Para tenant sem contatos GHL — `--generate` aborta silenciosamente.
- ❌ Sem GHL Workflows publicados — sem isso, scoring não rastreia abertura/clique.

## Por que funciona assim

- [ADR-0005](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0005-location-pit-token-por-tenant.md) — `location_pit_token` por tenant.
- `--generate` e `--dispatch` separados — permite agendar agora e enviar depois (1 email/dia BRT).
- Slot livre: varre `published_posts.seinfeld_scheduled_at` IS NOT NULL para evitar 2 emails no mesmo dia.

## 🚫 Don'ts

- **Não** usar `api_key` no lugar de `location_pit_token` — autenticação falha (G007).
- **Não** marcar `seinfeld_sent=true` no `--generate` — só no dispatch após `POST /conversations/messages` OK.
- **Não** alterar range do dispatch para "menor ou igual a hoje" — quebra lógica do slot livre (posts antigos brigam por slot atual).
- **Não** deixar `seinfeld_scheduled_at` no passado sem `seinfeld_sent=true` — post fica preso (G001). Fix: `UPDATE published_posts SET seinfeld_scheduled_at=NULL WHERE seinfeld_scheduled_at < CURRENT_DATE AND seinfeld_sent=false`.

## 🪦 Já tentamos

- **2026-04-19 — Seinfeld não disparado, lock stale + claude-cli vazio**: lock de cron antigo bloqueava + falha LLM. Ver `2026-04-19_seinfeld-nao-disparado-lock-stale-claude-cli-vazio.md`.
- **2026-04-25 — Seinfeld merge tag firstname não preenchia**: GHL workflow esperava `{{firstName}}` mas Cadência mandava texto cru. Ver `2026-04-25_seinfeld-merge-tag-firstname-nao-preenchia.md`.
- **2026-04-26 — GHL workflow não passa HTML em emails**: workflow downstream do envio strippava HTML. Ver `2026-04-26_ghl-workflow-nao-passa-html-emails.md`.
- **2026-04-26 — Render email HTML NameError**: vars não definidas no template Jinja. Ver `2026-04-26_render-email-html-nameerror-vars-nao-definidas.md`.
- **2026-04-26 — Calendário badges lógica dispatch ≠ geração**: UI mostrava badge errado porque confundia data de geração com data de dispatch. Ver incident.
- **2026-05-04 — Corpo claro texto invisível**: bug visual recorrente. Ver `2026-05-04_corpo-claro-texto-invisivel-nuclear-omissao-recorrente.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Post nunca foi enviado | Data agendada no passado (G001) | `UPDATE published_posts SET seinfeld_scheduled_at=NULL WHERE id=X AND seinfeld_sent=false` |
| 401/403 no GHL | `location_pit_token` ausente ou expirado | Regerar via `provision_tenant.py` ou completar OAuth (PDL-25) |
| `--generate` aborta em silêncio | 0 contatos GHL | Verificar `get_all_contacts()` no log |
| Email enviado mas firstname vazio | Merge tag GHL não bate | Validar `{{firstName}}` no template do workflow GHL |
| 2 emails mesmo dia | Slot livre lógica errada | Auditar query de `seinfeld_scheduled_at` |
| HTML strippado no email | GHL workflow downstream strippa | Ver incident 04-26 |

## 📚 Referências cruzadas

- [newsletter](newsletter.md)
- [scoring-leads](scoring-leads.md) — Recebe webhooks após envio
- [growth-pipeline-runner](growth-pipeline-runner.md)
- ADRs: [0005 location_pit_token](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0005-location-pit-token-por-tenant.md)
