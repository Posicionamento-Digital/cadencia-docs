> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`Posicionamento-Digital/cadencia-growth` / `main` / `docs/linkedin-generation.md`](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/linkedin-generation.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# linkedin-generation — post LinkedIn

## TL;DR

Gera e agenda post para LinkedIn do tenant. Roda no cron diário (11h BRT) e no trigger on-demand.

## Identidade

- **Tipo:** Python script
- **Path:** `/cadencia/pipeline/linkedin_generate.py` (VPS Master)
- **Status:** ativo
- **Deps:** `published_posts`, `tenant_config`, OpenAI (via OpenRouter)

## Como funciona

1. Busca ideias aprovadas sem post LinkedIn (`linkedin_published=false`)
2. Gera texto via LLM com voz da marca (dossier + editorial)
3. Salva em `published_posts.linkedin_content`
4. Publica via LinkedIn API (se `linkedin_access_token` configurado) ou salva como rascunho

## Frequência

- Planos `trial`/`essencial`/`starter`: só seg e qui (G006)
- Planos maiores: diário

## Don'ts

- `linkedin_access_token` expira — verificar antes de publicar

---

## Quando usar

- Cron diário 11h BRT via `growth_pipeline.py linkedin`.
- Trigger on-demand quando usuário aprova ideia (canal `linkedin`).

## Quando NÃO usar

- ❌ Para post visual (carrossel/reels) — vai para Instagram via Railway.
- ❌ Tenant `trial`/`essencial`/`starter` em dia que não seja segunda ou quinta (planos restritos a 2x/sem para LinkedIn).
- ❌ Sem `linkedin_url` configurada — não tem destino.

## Por que funciona assim

- Frequência variável por plano: `growth_pro` diário, `trial`/`essencial` só seg+qui.
- Geração baseada em blog (pega último blog do dia como insumo + adapta).

## 🚫 Don'ts

- **Não** disparar LinkedIn antes do blog do dia ter rodado — sem insumo.
- **Não** publicar sem CTA para o blog (link âncora).
- **Não** marcar `scheduled_at` antes do GHL confirmar a programação.

## 🪦 Já tentamos

- **2026-04-25 — LinkedIn CTA link blog ausente**: ver `2026-04-25_linkedin-cta-link-blog-ausente.md`.
- **2026-04-26 — LinkedIn research documents coluna errada**: ver `2026-04-26_linkedin-research-documents-coluna-errada.md`.
- **2026-04-26 — LinkedIn scheduled_at antes de GHL confirmar**: corrida com confirmação. Ver `2026-04-26_linkedin-scheduled-at-antes-ghl-confirmar.md`.
- **2026-04-26 — LinkedIn tab filtro sent ocultava posts gerados**: bug UI. Ver `2026-04-26_linkedin-tab-filtro-sent-ocultava-posts-gerados.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| LinkedIn não rodou seg/qui | Plano com weekday restrito; cron parou | Verificar `weekday()` filtro + crontab |
| Post sem CTA blog | Blog do dia falhou | Forçar regen blog antes |
| Posts não aparecem na aba | Filtro `sent` ocultando | Ver incident `linkedin-tab-filtro-sent` |

## 📚 Referências cruzadas

- [blog-instagram-gen](blog-instagram-gen.md) — Insumo
- [growth-pipeline-runner](growth-pipeline-runner.md)
