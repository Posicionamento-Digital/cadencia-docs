# Cadence Engine — runtime único de cadências

> Motor que matricula contatos por gatilho e faz a cadência avançar pelo canal correto. Substitui o runner experimental da Lara. Atualizado em 15/07/2026 (DEV-1329/1330).

## Identidade
- **Tipo:** scripts Python standalone (cron) — mesmo padrão do `growth_pipeline`
- **Stack:** Python 3.12 + `lib_api` (PostgREST via curl) + Resend + API da Lara
- **Paths:** `pipeline/cadence_tick.py`, `pipeline/cadence_templates.py`
- **Deploy:** VPS Master `/cadencia/` (git pull `main`) · cron root `10 14 * * *` (11:10 BRT)
- **Status:** motor único ativo; processa somente `driver='growth'`

## Componentes

| Arquivo | Função |
|---|---|
| `pipeline/cadence_tick.py` | Tick diário: varre `contact_cadences` running com `next_send_at <= now`, dispara o step devido, avança, loga |
| `pipeline/cadence_templates.py` | `render_template` (Mustache `{{var}}`) + `build_cadence_context` (vars tenant/lead/sistema) |

## Como funciona (cadence_tick)

1. **Cron 11h BRT** chama `cadence_tick.py [tenant_id]` (sem arg = todos os tenants).
2. Por tenant: checa toggle global `tenant_config.config.automacoes_ativas` — **default OFF** (opt-in). Off → pula.
3. `auto_enroll_sweep` matricula contatos elegíveis por `instant`, `stage` e `outbound_no_reply`. O inbound é matriculado pela RPC chamada pela Lara.
4. `get_due_cadences`: `contact_cadences?status=eq.running&driver=eq.growth&next_send_at=lte.{now}`.
5. Por cadência devida (`process_cadence`):
   - **reply gate:** resposta WhatsApp posterior a `started_at` pausa a inscrição;
   - resolve o step do `current_step` (próximo `step_order`);
   - **guard condição** (`trigger_condition` jsonb, incluindo `slot_available`) → se não satisfaz, espera;
   - **guard copy** `body_template == '[a definir]'` → check `skipped` (`copy_pendente`), não envia;
   - **roteia por canal:** `email` → Resend, `whatsapp` → adaptador Evolution da Lara, demais canais → check `pending` (tarefa humana);
   - **idempotência:** `record_check` insere em `cadence_step_checks` com UNIQUE `(contact_cadence_id, cadence_step_id, cadence_cycle)`. `sb_insert` retorna `[]` em 409 → já processado;
   - **avança** `current_step` + recalcula `next_send_at` (`offset_minutes` tem prioridade sobre `day_offset`); último step → `completed`.

## Decisões-chave

- **Por que cron script, não APScheduler:** o serviço já agenda por endpoint/cron (padrão `growth_pipeline`). APScheduler criaria 2 paradigmas + risco de lock multi-instância. Cron diário basta (cadência é por dia). Realinhado pro padrão do Luiz.
- **Idempotência no banco** (UNIQUE + 409), não em lógica frágil.
- **Recuperação em `dup`:** o UNIQUE prova que aquele step/ciclo já teve check gravado. Se `advance` falhou depois desse insert, o próximo tick recebe 409, não reenvia nem recria o log e executa somente o avanço idempotente. O `log_activity` ocorre apenas no caminho de insert novo e depois do avanço.
- **Erro técnico no insert** (`None`) → não avança, retoma no próximo tick.
- **Um scheduler:** estado/avanço ficam aqui; Lara fornece WhatsApp, disponibilidade e sinal inbound.
- **Só leads novos:** todo gatilho automático respeita `entry_trigger.since`.

## Gatilhos de matrícula

| Gatilho | Seleção |
|---|---|
| `manual` | nenhuma varredura; API de contato/oportunidade cria a inscrição |
| `instant` | contatos do `pipeline_id` após `since` |
| `stage` | oportunidades no `stage_id` após `since` |
| `outbound_no_reply` | `lara_conversations.last_manual_at` vencido sem inbound posterior |
| `inbound_whatsapp` | RPC `enroll_inbound_whatsapp` chamada pela Lara |

O sweep evita duplicar uma inscrição `running` ou `paused`. Novas linhas começam em `current_step=0`,
`status='running'` e `driver='growth'`.

## WhatsApp e agenda

`send_cadence_whatsapp` resolve o telefone, renderiza a copy e chama
`cadencia-lara /admin/cadence/send-whatsapp`. O tick continua responsável por check, idempotência e
avanço; a Lara não conhece `current_step`.

Condição `slot_available` chama `/admin/cadence/check-availability`, hoje implementado com o plugin
Easy!Appointments. Falha/indisponibilidade mantém o step esperando; não avança silenciosamente.

## send_cadence_email (CAD-578)

`send_cadence_email(tenant_id, cc, step, config)`:
1. busca contato (`contacts?id=...&select=email,first_name,unsubscribe_token,custom_fields,lead_source,status`);
2. guards: sem email / `status=unsubscribed`;
3. renderiza `subject_template`/`body_template` com `build_cadence_context` (escape HTML só no body);
4. `lib_api.resend_send(from, email, subject, html, tags={tenant_id,contact_id,cadence_step_id}, headers=List-Unsubscribe)` — **mesmo cliente do Seinfeld**;
5. `from` = `email_sender_address` do tenant (display name entre aspas, RFC 5322, CR/LF sanitizado);
6. retorno: `id`→(True,None); 4xx→(False,`resend_{st}`); transitório→(False,`resend_transient`).

As `tags` voltam no webhook Resend (`scoring/resend_webhook.py`) e permitem ao scoring resolver o contato.

## Templating (cadence_templates)

- `render_template(template, ctx, escape_html=False)` — `{{var}}`→valor; var ausente/vazia → mantém `{{var}}` cru + reporta em `missing`. `escape_html=True` (body do email) escapa **só os valores interpolados**, não a marcação.
- `build_cadence_context(config, contact, unsubscribe_link)` — mapeia `tenant_*` (config: nome_empresa, email_sender_name, angulo_unico, sobre, track_record), `lead_*` (contact: first_name, custom_fields.company, lead_source), `unsubscribe_link`.

## 🚫 Don'ts / gotchas
- `_iso` usa sufixo **`Z`**, não `+00:00` — `+` vira espaço na URL do PostgREST → 400 (achado qwen).
- `try/except` por cadência no `run_tick` — erro numa não aborta as demais (mas **não** silencia o avanço: ver recuperação em dup).
- O cron atual é `10 14 * * *` (diário). `offset_minutes` melhora o modelo, mas a precisão real continua limitada pela frequência do cron.
- `status` do runtime é `running`, não o comentário legado `active` da primeira migration.
- O endpoint da Lara deve estar saudável para WhatsApp e `slot_available`.
- A copy system foi preenchida em DEV-1330, mas é template genérico; clones podem e devem ser personalizados.

## Status real
- ✅ Email Resend, WhatsApp via Lara, idempotência, reply gate, gatilhos, offset em minutos e condições de agenda implementados.
- ⚠️ `automacoes_ativas` continua sendo o master switch por tenant.

## Refs
- Reviews §6: `docs/codex-reviews/codex-review-19-06-2026-cad577.md`, `...cad578.md`
- Planos: `pd-framework/times/produto/cadencia/context/plano-CAD-{577,578}.md`
- UI/schema: `cadencia-app/docs/features/cadencias-contatos.md`
- Adaptador: `cadencia-lara/docs/features/cadencias-adapter.md`

## Cobertura dos commits de expansão

`80dc7d7`, `87e8e81`, `ddfe418`, `d832dac`, `04f5892`, `efc2503`.
