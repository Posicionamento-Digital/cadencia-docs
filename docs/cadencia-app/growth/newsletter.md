> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`Posicionamento-Digital/cadencia-growth` / `main` / `docs/newsletter.md`](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/newsletter.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# newsletter — newsletter semanal

## TL;DR

Compila posts da semana do tenant e dispara newsletter via GHL toda sexta às 15h BRT.

## Identidade

- **Tipo:** Python script
- **Path:** `/cadencia/pipeline/newsletter_generate.py` (VPS Master)
- **Status:** ativo
- **Deps:** `published_posts`, GHL `location_pit_token` por tenant

## Como funciona

- `growth_pipeline.py newsletter` → chama este script (schedule: `0 18 * * 5` sexta 15h BRT)
- Busca `published_posts` com `newsletter_included=false` do tenant
- Compila artigos da semana em uma newsletter formatada
- Dispara via `POST /conversations/messages` (mesmo padrão do Seinfeld — GHL direto)
- Marca `newsletter_included=true` após envio

## Gotcha crítico

**NÃO entra no trigger on-demand** (`trigger_server.py`). Se o tenant aprovar uma ideia e escolher "newsletter", esse canal é silenciosamente ignorado (G002). Newsletter só roda pelo cron sexta.

## Don'ts

- Não tentar disparar newsletter via trigger on-demand — não vai funcionar
- Canal "newsletter" no frontend é visual only — backend ignora no trigger

---

## Quando usar

- **Apenas** cron sexta 15h BRT via `growth_pipeline.py newsletter`.

## Quando NÃO usar

- ❌ Trigger on-demand — é **silenciosamente ignorada** pelo `trigger_server.py` (G002). Canal `newsletter` selecionado no frontend não dispara nada.
- ❌ Para tenant sem `location_pit_token`.
- ❌ Para semana sem artigos publicados (`newsletter_included=false` zerado).

## Por que funciona assim

- Cadência semanal fixa (não diária) — newsletter é compilado, exige acúmulo.
- Sexta 15h BRT: melhor janela de abertura observada empiricamente.
- Mesma autenticação do Seinfeld (`location_pit_token` + `POST /conversations/messages`).

## 🚫 Don'ts

- **Não** disparar newsletter on-demand — quebra cadência percebida pelo usuário.
- **Não** reenviar — não há flag de "retry" hoje.
- **Não** ignorar `newsletter_included` no select — gera duplicação.

## 🪦 Já tentamos

- **2026-05-01 — Newsletter bloqueada regra confirmação CLAUDE.md**: regra de confirmação destrutiva interpretou geração como destrutiva. Ver `2026-05-01_newsletter-bloqueada-regra-confirmacao-claude-md.md`.
- **2026-05-06 — Trigger server zerava pool newsletter**: bug que zerava `newsletter_included` ao reiniciar. Ver `2026-05-06_trigger-server-zerava-pool-newsletter.md`.
- **2026-04-17 — Crons newsletter+seinfeld não dispararam**: timezone. Ver incident.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Newsletter não enviou sexta | Cron parou; tz errado; sem artigos | `crontab -l`; verificar `published_posts WHERE newsletter_included=false` |
| Duplicação de artigos | `newsletter_included` zerou | Auditar `trigger_server.py` para ver se zera ao restart |
| Tenant não recebeu | Sem `location_pit_token` | Mesmo fluxo Seinfeld |

## 📚 Referências cruzadas

- [seinfeld-email](seinfeld-email.md) — Mesma stack de envio
- [growth-pipeline-runner](growth-pipeline-runner.md)
