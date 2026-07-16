# cadencia-growth

Pipeline de growth do Cadência na VPS Master (`/cadencia`): geração e dispatch
de blog, email Seinfeld, LinkedIn, Instagram e newsletter; scoring de leads;
cadências de contatos; e provisionamento de domínio de email.

## O que faz

1. carrega tenants e estado do CRM Cadência;
2. gera e publica conteúdo pelos providers de cada canal;
3. envia Seinfeld/newsletter via Resend;
4. recebe eventos Resend/Svix e atualiza score, temperatura e supressão;
5. executa o motor de cadências e integra WhatsApp/agenda pela Lara;
6. provisiona subdomínio Resend e DNS para tenants novos.

## Stack

| Camada | Tecnologia |
|---|---|
| Runtime | Python 3.12, cron e daemons HTTP |
| Dados/CRM | Supabase PostgreSQL |
| Email/scoring | Resend + Svix |
| WhatsApp/agenda | cadencia-lara |
| DNS | Cloudflare |
| Conteúdo | OpenAI/OpenRouter + providers dos canais |

## Estrutura

| Pasta | Responsabilidade |
|---|---|
| `crons/` | orquestração diária, retry e manutenção |
| `pipeline/` | geração, dispatch, cadências e provisioning |
| `scoring/` | webhook Resend/Svix |
| `scripts/` | auditoria, recovery e migrações one-shot históricas |
| `docs/` | arquitetura, componentes e runbooks |
| `tests/` | suíte automatizada |

## Serviços

| Porta | Serviço |
|---|---|
| `39090` | trigger on-demand |
| `8767` | webhook Resend/Svix |
| `8768` | Mission Control |

## Setup local

Use `.env.example` como mapa e resolva credenciais pelo 1Password. Nunca grave
tokens em documentação ou commits.

```bash
python -m compileall -q -x 'prompts_before\.py' pipeline scoring scripts
python3 -m pytest tests/ --ignore=tests/visual -q
```

`pipeline/prompts_before.py` é snapshot histórico congelado e fica fora do
compile gate.

## Documentação

- [docs/README.md](docs/README.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/growth-pipeline-runner.md](docs/growth-pipeline-runner.md)
- [docs/scoring-leads.md](docs/scoring-leads.md)
- [docs/cadence-engine.md](docs/cadence-engine.md)
