> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/adr/0004-carrossel-railway-resto-vps.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0004-carrossel-railway-resto-vps.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# ADR-0004 — Carrossel/reels Railway, blog/seinfeld/linkedin/instagram VPS

**Status:** aceito · **Data:** 2026-05-27 (decisão original ~10/2025)

## Contexto

Cadência gera 7 tipos de conteúdo: carrossel, reels, blog, seinfeld, linkedin, instagram (post simples), newsletter. Custo computacional e dependências variam drasticamente:

- **Carrossel:** Playwright + Chromium + identity lock (Gemini 2.5 Flash) + render HTML → PNG. Memória + tempo de render altos.
- **Reels:** ffmpeg + composição vídeo. Memória + CPU altíssimos.
- **Blog/seinfeld/linkedin/instagram/newsletter:** texto puro via OpenAI. Baixo custo.

## Decisão

Particionar por custo computacional:

- **Railway (workers Python FastAPI):** carrossel + reels. Memória reservada, Playwright/ffmpeg pré-instalados.
- **VPS Master (`/cadencia/`):** blog, seinfeld, linkedin, instagram, newsletter. Scripts Python simples + cron.

`api/app/trigger-generation/route.ts` decide o roteamento:

```typescript
if (channel === 'carrossel' || channel === 'reels') → Railway
else → VPS:39090/trigger
```

## Consequências

- ✅ Railway custo controlado (só workers que precisam).
- ✅ VPS custo zero adicional (já existia para outros usos).
- ✅ Independência: Railway down não para email; VPS down não para carrossel.
- ❌ Dois lugares para deploy — agente precisa lembrar onde mexer.
- ❌ Schema do Supabase é compartilhado — qualquer mudança afeta os dois.
- ⚠️ `growth_pipeline.py` (VPS) **não** processa carrossel/reels — confusão comum.
- ⚠️ Migração Railway → Coolify VPS em andamento (PDL-18 a 23) — vai unificar tudo na VPS Master.

## Não considerado

- Tudo Railway — custo escalaria com tenants.
- Tudo VPS — Playwright + ffmpeg na VPS Master comprometeria scripts críticos (mission control, scoring).
- Serverless (Vercel functions) — timeout de 10s/60s não comporta render de carrossel.
