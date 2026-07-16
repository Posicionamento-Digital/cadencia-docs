# cadencia-workers — guia para agentes

Python FastAPI backend. Gera carrossel, dossier, identidade visual, ideias de conteúdo.

## Deploy

- **Atual**: **Coolify** (VPS Master) — projeto `cadencia`, app `cadencia-workers` (id 10), branch `master`, build Dockerfile, domínio `workers.cadencia.ia.br`. Worker no ar e healthy.
- **Cutover concluído** (confirmação Felipe 2026-07-14): a Vercel (`WORKERS_API_URL`) aponta pro Coolify. **Railway está DESLIGADO — não existe serviço Cadencia rodando na Railway.** Menções a Railway em docs são histórico (ADR-0012).
- **Auto-deploy on-push está OFF** (deploy key sem webhook) → deploy manual via Coolify UI/API até CAD-678. Ver `docs/adr/0012-workers-railway-para-coolify.md` + `docs/infra-cli-access.md`.

## Estrutura

```
cadencia-workers/
  main.py                    # entrypoint FastAPI
  src/
    api/
      routes/
        chat.py              # /api/v1/chat — chat "Tenho uma Ideia"
        cron.py              # /api/v1/cron — triggers periódicos
        documents.py         # /api/v1/documents — geração documentos
        health.py            # /health
        ideas.py             # /api/v1/ideas — geração de ideias
        onboarding.py        # /api/v1/onboarding — dossier, identidade visual, editoriais
        pipeline.py          # /api/v1/pipeline — geração carrossel/reels
        theme.py             # /api/v1/theme — identidade visual
      middleware/
        auth.py              # JWT Supabase auth
        rate_limit.py
    integrations/
      pexels.py              # banco de fotos
      supabase.py
    models/
      *.yaml                 # 29 templates de formato (carrossel, lista, tutorial...)
```

## Orquestrador de onboarding (7 steps)

`/api/v1/onboarding/` executa em sequência:
1. Perfil (Big5 + DPR Signaling)
2. Dossier de marca
3. Identidade visual (sub-preset + Gemini cover)
4. Editoriais (3 por tenant)
5. Ideias iniciais (5 ideias)
6. Validação
7. Conclusão

## Como acessar o código

```bash
gh api "repos/felipeluissalgueiro/cadencia-app/contents/cadencia-workers/<path>?ref=master" \
  | python -c "import json,sys,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode())"
```

## Variáveis de ambiente críticas

Ver `cadencia-workers/.env.example`. Principais:
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- `OPENAI_API_KEY` (via OpenRouter)
