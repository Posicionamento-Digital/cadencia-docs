> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`Posicionamento-Digital/cadencia-growth` / `main` / `docs/scoring-leads.md`](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/scoring-leads.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# scoring-leads — scoring de leads via webhooks GHL

## TL;DR

Servidor HTTP (porta 8766, systemd) que recebe webhooks de email aberto/clicado do GHL e atualiza score do contato.

## Identidade

- **Tipo:** Python servidor HTTP (systemd)
- **Path:** `/cadencia/scoring/webhook_handler.py` (VPS Master)
- **Status:** ativo — requer GHL Workflows publicados
- **Deps:** GHL `location_pit_token` por tenant, Supabase `scoring_events`, `tenant_config`

## Como funciona

1. Recebe `POST /` com payload GHL (evento `email_opened` ou `link_clicked`)
2. Resolve tenant por `location_id`: varre `tenant_config` buscando `config.ghl.location_id == location_id`
3. Aplica SCORE_MAP: `email_opened/email_open` = +2 pts; `link_clicked/email_clicked/link_click` = +5 pts
4. Atualiza `contact.score_ia` (custom field GHL) + `contact.temperatura` via `PUT /contacts/{id}`
5. Score bands: Frio (<30), Aquecendo (≥30), Quente (≥60), Hot (≥80)
6. Gerencia tags: `score:aquecendo`, `score:quente`, `score:hot`
7. Move/cria oportunidade no pipeline do tenant (`config.ghl.pipeline_id` + `config.ghl.pipeline_stages`)
8. Persiste em `scoring_events` (fire-and-forget, thread separada)

## Pré-requisito crítico

**GHL Workflows publicados** que enviam eventos para `http://72.60.4.71:8766`. Sem os workflows publicados, nenhum evento chega ao scoring.

## mission_control.py

Dashboard HTTP porta 8768 — visão geral de tenants, status dos serviços, logs recentes. Roda via @reboot.

## Gotchas

- G007: usa `location_pit_token`, não `api_key`
- G008: tabela de contatos não existe no Supabase — GHL é fonte da verdade
- Score acumula — não tem reset automático

## Don'ts

- Não alterar SCORE_MAP sem decisão de produto (afeta todos os tenants)
- Nunca usar `api_key` global aqui — requer token por tenant

---

## Quando usar

- **GHL workflows publicados** chamam `POST http://72.60.4.71:8766` para cada evento `email_opened`/`link_clicked`.
- Atualiza `contact.score_ia` + `temperatura` + tags no GHL via `PUT /contacts/{id}`.

## Quando NÃO usar

- ❌ Sem GHL Workflows publicados — sem isso, nenhum evento chega.
- ❌ Para scoring manual — esse worker é só event-driven.
- ❌ Para tenant sem `score_ia_field_key` configurado em `tenant_config`.

## Por que funciona assim

- [ADR-0005](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0005-location-pit-token-por-tenant.md) — `location_pit_token` por tenant.
- Score bands: Frio (<30), Aquecendo (≥30), Quente (≥60), Hot (≥80).
- SCORE_MAP fixo: open=+2, click=+5.
- Fire-and-forget para `scoring_events` (thread separada) — não atrasa resposta ao GHL.
- Move opportunity no pipeline do tenant automaticamente conforme banda muda.

## 🚫 Don'ts

- **Não** usar `api_key` global — autenticação falha (G007).
- **Não** rodar webhook handler sem porta aberta no firewall VPS (8766).
- **Não** confiar em ordem de eventos — GHL pode entregar fora de ordem; sempre re-aplicar SCORE_MAP cumulativo.
- **Não** assumir que evento sem `path` é válido — alguns webhooks GHL chegam sem path.

## 🪦 Já tentamos

- **2026-04-22 — Scoring webhook sem path evento ignorado**: ver `2026-04-22_scoring-webhook-sem-path-evento-ignorado.md`.
- **2026-04-23 — GHL webhook customdata categoria vazio**: ver `2026-04-23_ghl-webhook-customdata-categoria-vazio.md`.
- **2026-05-15 — Regressão multi-canal porta VPS bloqueada**: porta 8766 bloqueada pelo firewall após update. Ver `2026-05-15_regressao-multi-canal-porta-vps-bloqueada.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Eventos não chegam | Workflow GHL não publicado ou URL errada | `https://72.60.4.71:8766` (não https) |
| 401 ao atualizar contato | `location_pit_token` errado | Mesmo fluxo Seinfeld |
| Score não atualiza | `score_ia_field_key` ausente em `tenant_config` | Adicionar custom field GHL + key no config |
| Opportunity não muda de stage | `pipeline_stages` ausente em `tenant_config` | Configurar mapping bandas → stage IDs |
| Porta 8766 unreachable | Firewall VPS após update | Reabrir porta (ver incident `regressao-multi-canal`) |

## 📚 Referências cruzadas

- [provisioning-ghl](provisioning-ghl.md) — Configura `score_ia_field_key`
- [seinfeld-email](seinfeld-email.md) — Origem dos eventos
- [newsletter](newsletter.md) — Origem dos eventos
- ADR: [0005 location_pit_token](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0005-location-pit-token-por-tenant.md)
