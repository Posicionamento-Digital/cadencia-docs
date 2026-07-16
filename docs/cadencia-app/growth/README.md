# docs/ — cadencia-growth

7 docs de componente do pipeline VPS. Cada um documenta um script Python em `/cadencia/` na VPS Master.

> **Stack:** Python 3.12 + cron + systemd webhook. **Não confundir com os workers Coolify VPS Master** (carrossel/reels; Railway DESLIGADO) — esses vivem em `felipeluissalgueiro/cadencia-app/cadencia-workers/`. Ver [ADR-0004 no cadencia-app](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0004-carrossel-railway-resto-vps.md).

## Componentes

| Doc | Função em 1 linha | Quando roda |
|---|---|---|
| [growth-pipeline-runner.md](growth-pipeline-runner.md) | Orquestrador master — encadeia sync → blog → seinfeld → newsletter → linkedin → instagram | Cron 11h BRT diário + sex 15h BRT (newsletter) |
| [seinfeld-email.md](seinfeld-email.md) | Email diário estilo Jerry Seinfeld — dois modos `--generate` (agenda) + `--dispatch` (envia hoje) | Cron diário + on-demand `--generate` |
| [newsletter.md](newsletter.md) | Compilação semanal de artigos da semana | **Apenas** sex 15h BRT (pulada no trigger on-demand, com aviso claro no 202 — G002, DEV-496) |
| [cadence-engine.md](cadence-engine.md) | Motor único de cadências — matrícula por gatilho, email, WhatsApp via Lara, reply gate, agenda e idempotência | Cron 11h BRT (`cadence_tick.py`) |
| [email-warmup-cutover.md](email-warmup-cutover.md) | Histórico do cutover concluído + operação atual de warm-up, priorização e toggle por lead | Aplicado em seinfeld/newsletter dispatch |
| [email-domain-provisioning.md](email-domain-provisioning.md) | Auto-provisão de subdomínio de email por tenant no Resend + DNS Cloudflare | No provision de tenant novo |
| [email-resend-migration.md](email-resend-migration.md) | Runbook histórico da migração concluída; não executar como rollback | Arquivo histórico |
| [linkedin-generation.md](linkedin-generation.md) | Post LinkedIn diário derivado do blog do dia | Cron diário (planos restritos: só seg+qui) |
| [blog-instagram-gen.md](blog-instagram-gen.md) | Blog post + Instagram post simples (não carrossel) | Cron diário |
| [scoring-leads.md](scoring-leads.md) | Webhook Resend/Svix → score, temperatura, atribuição e supressão no CRM Cadência | Servidor HTTP `:8767`, event-driven |
| [email-scoring-hardening-2026-07.md](email-scoring-hardening-2026-07.md) | Invariantes recentes de email, Svix, scoring e compliance | Referência transversal |
| [luiz-features-coverage-2026-07.md](luiz-features-coverage-2026-07.md) | Cobertura commit a commit das entregas do Luiz | Auditoria documental |

## Mapa de portas e serviços na VPS

| Porta | Serviço | Origem |
|---|---|---|
| `:39090` | `trigger_server.py` — endpoint on-demand | growth-pipeline-runner |
| `:8767` | Webhook Resend/Svix | scoring-leads |
| `:8768` | Mission Control dashboard | `mission_control.py` |

## Cron diário (11h BRT)

```
growth_pipeline.py sync blog seinfeld linkedin instagram
  ├─ sync         (CRM Cadência/Supabase)
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
POST /api/app/trigger-generation (Vercel — cadencia-app)
  ├─ canal carrossel/reels → workers Coolify VPS Master (cadencia-app/cadencia-workers/)
  └─ outros canais        → POST 72.60.4.71:39090/trigger
      └─ trigger_server.py.run_pipeline():
          sync → blog → seinfeld --generate → linkedin → instagram
          (newsletter PULADA -- 202 devolve `warnings` avisando o motivo, DEV-496/G002)
```

## Cuidados transversais (Don'ts)

- **Seinfeld envia via Resend e scoring recebe via Svix.** Tags de tenant, contato e post fazem a atribuição.
- ~~Seinfeld com data passada fica preso (G001)~~ — corrigido em DEV-763: `--dispatch` busca `seinfeld_scheduled_at <= hoje` (não só hoje exato), 1 post/execução (guarda contra spam de backlog).
- **Newsletter NÃO roda no trigger on-demand** (G002) — mas agora o `POST /trigger` avisa no 202 (`warnings`) quando o canal é selecionado (DEV-496).
- **`growth_pipeline.py` processa TODOS tenants com config** (G005) — sem filtro `onboarding_completed`.
- A porta `8766` é histórica e não deve ser reativada. Provisionar tenants com `/cadencia-provisionar-tenant`.

## Acesso à VPS

```bash
ssh -i ~/.ssh/hostinger_prod_master master@72.60.4.71

cat /cadencia/pipeline/seinfeld_generate.py
crontab -l
tail -f /cadencia/logs/growth_pipeline.log
```

## Mirror no pd-framework

Cópia organizada por área lógica vive em:

```
pd-framework/times/produto/cadencia/docs/growth/
```

## Refs externas

- ADRs vivem em [`cadencia-app/docs/adr/`](https://github.com/felipeluissalgueiro/cadencia-app/tree/master/docs/adr) — não duplicadas aqui:
  - [0004 Railway/VPS](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0004-carrossel-railway-resto-vps.md)
  - [0005 PIT token](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0005-location-pit-token-por-tenant.md)
- Squad Cadência no pd-framework: `times/produto/cadencia/CLAUDE.md`
- VPS Access detalhado: `pd-framework/_core/VPS-ACCESS.md`
