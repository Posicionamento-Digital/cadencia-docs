# growth/ — Pipeline VPS Master (`/cadencia/`)

7 scripts Python que rodam na **VPS Master `72.60.4.71` em `/cadencia/`**. Geram blog, email Seinfeld, LinkedIn, newsletter, post simples Instagram + scoring de leads.

> **⚠️ NÃO confundir com workers Coolify VPS Master** ([`../workers/`](../workers/)). Esses scripts são para conteúdo de texto/email e scoring. Carrossel e reels NÃO rodam aqui. Ver [ADR-0004](../adr/0004-carrossel-railway-resto-vps.md).
>
> **Migração em andamento:** `/cadencia/` → `/opt/cadencia-growth/` (PDL-213).

## Componentes

| Script | Doc | Função em 1 linha | Quando roda |
|---|---|---|---|
| **Growth Pipeline Runner** | [growth-pipeline-runner.md](growth-pipeline-runner.md) | Orquestrador master — encadeia sync → blog → seinfeld → newsletter → linkedin → instagram | Cron 11h BRT diário + sex 15h BRT (newsletter) |
| **Seinfeld Email** | [seinfeld-email.md](seinfeld-email.md) | Email diário estilo Jerry Seinfeld (storytelling curto) — dois modos `--generate` + `--dispatch` | Cron diário + on-demand `--generate` |
| **Newsletter** | [newsletter.md](newsletter.md) | Compilação semanal de artigos da semana | **Apenas** sex 15h BRT (silenciosamente pulada no trigger on-demand — G002) |
| **LinkedIn Generation** | [linkedin-generation.md](linkedin-generation.md) | Post LinkedIn diário derivado do blog do dia | Cron diário (planos restritos: só seg+qui) |
| **Blog + Instagram Gen** | [blog-instagram-gen.md](blog-instagram-gen.md) | Blog post + Instagram post simples (não carrossel) | Cron diário |
| **Scoring Leads** | [scoring-leads.md](scoring-leads.md) | Webhook handler que recebe eventos GHL (open/click) → score_ia + temperatura + tags | Servidor HTTP `:8766`, event-driven |
| **Provisioning GHL** | [provisioning-ghl.md](provisioning-ghl.md) | Cria subconta GHL para tenant novo via OAuth agência | Após signup + retry 10h55 BRT |

## Mapa de portas e serviços na VPS

| Porta | Serviço | Origem |
|---|---|---|
| `:39090` | `trigger_server.py` — endpoint on-demand | `growth-pipeline-runner` |
| `:8766` | Scoring webhook | `scoring-leads` |
| `:8768` | Mission Control dashboard | `mission_control.py` |

## Cron diário (11h BRT)

```
growth_pipeline.py sync blog seinfeld linkedin instagram
  ├─ sync         (contatos GHL)
  ├─ blog         (texto + HTML → cadencia-blog white-label)
  ├─ seinfeld --generate    (agenda próximo email)
  ├─ seinfeld --dispatch    (envia email do dia se houver agendado)
  ├─ linkedin     (deriva do blog)
  └─ instagram    (post simples, não carrossel)

# sex 15h BRT — adicional:
growth_pipeline.py newsletter
```

## Trigger on-demand (usuário aprovou ideia no frontend)

```
POST /api/app/trigger-generation (Vercel)
  ├─ canal carrossel/reels → workers Coolify VPS Master
  └─ outros canais       → POST 72.60.4.71:39090/trigger
      └─ trigger_server.py.run_pipeline():
          sync → blog → seinfeld --generate → linkedin → instagram
          (newsletter PULADA — G002)
```

## Cuidados transversais (Don'ts)

- **Seinfeld + scoring usam `location_pit_token` do tenant** (G007), não `api_key` global. Tokens completamente diferentes.
- **Seinfeld com data passada fica preso** (G001) — `--dispatch` só pega hoje exato BRT.
- **Newsletter NÃO roda no trigger on-demand** (G002) — silenciosamente ignorada.
- **`growth_pipeline.py` processa TODOS tenants com config** (G005) — sem filtro `onboarding_completed`. Só verifica créditos.
- **Provisioning bloqueado** (PDL-25) — `ghl_agency_oauth` vazio. Workaround: skill `/cadencia-provisionar-tenant`.

## Acesso à VPS

```bash
ssh -i ~/.ssh/hostinger_prod_master master@72.60.4.71

# Ler arquivo
cat /cadencia/pipeline/seinfeld_generate.py

# Ver crontab
crontab -l

# Logs
tail -f /cadencia/logs/growth_pipeline.log
```

## Refs

- Voltar: [`../README.md`](../README.md)
- ADRs: [`../adr/0004-*`](../adr/0004-carrossel-railway-resto-vps.md) (workers Coolify vs VPS growth), [`../adr/0005-*`](../adr/0005-location-pit-token-por-tenant.md) (PIT token)
- Outro pólo (carrossel/reels): [`../workers/`](../workers/)
- Fluxo end-to-end: [`../architecture/architecture.md`](../architecture/architecture.md)
- VPS Access: `pd-framework/_core/VPS-ACCESS.md`
