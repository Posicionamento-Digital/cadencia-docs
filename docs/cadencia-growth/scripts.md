# scripts/

Scripts operacionais — migrações pontuais, validação, recovery manual. Não rodam em cron (geralmente). Executar sob demanda quando precisar.

## Identidade

- **Tipo:** scripts operacionais (one-shot ou manuais)
- **Stack:** Python 3.12 + bash
- **Path no repo:** `scripts/`
- **Status:** ativo (uso operacional)

## Arquivos

| Arquivo | Tipo | Função |
|---|---|---|
| `drift_check.sh` | bash | Valida que `/cadencia` na VPS está sincronizado com `main` do repo. Falha se `git status` mostrar modificações locais não commitadas |
| `content_readiness.py` | python | Auditoria de tenants prontos para geração (brand voice, CRM, email e canais). |
| `email_resend_preflight.py` | python | Pre-check antes de mover tenant pro provider Resend (CAD-675) — valida DNS, subdomínio, Svix webhook |
| `recover_orphan_provisioning.py` | python | Recovery manual de tenant em estado orphan (alternativa a `crons/retry_provisioning.py` pra casos teimosos) |
| `test.sh` | bash | Wrapper que invoca pytest com flags corretas (`--ignore=tests/visual -q`) |

## Quickstart

```bash
# Validar drift (na VPS, executado pelo cron 12h também)
bash scripts/drift_check.sh
# Saída esperada: vazia (sem drift). Saída com linhas Modified/Untracked = ALERTA.

# Auditar prontidão de tenants
python3 scripts/content_readiness.py

# Pre-check cutover Resend
python3 scripts/email_resend_preflight.py --tenant-id <uuid>

# Recovery manual de orphan teimoso
python3 scripts/recover_orphan_provisioning.py --tenant-id <uuid> --force

# Testes
bash scripts/test.sh
```

## Don'ts

- ❌ **NÃO ignorar `drift_check.sh` em alerta** — significa que alguém editou `/cadencia` direto (viola regra dura nº 1 do CLAUDE.md). Capturar diff + versionar antes de qualquer `git pull`.
- ❌ **NÃO commitar `.env` mesmo backup** — `.gitignore` cobre `.env.bak*` desde DEV-835. Validar antes de push.

## Pós-migração Coolify

`drift_check.sh` fica **irrelevante** após migração — não há mais clone manual em `/cadencia`. Pode ser apagado OU repropósito (ex: validar que ninguém SSH-edita o container Coolify direto — improvável).

Scripts de recovery e auditoria continuam úteis como Scheduled Task ou one-shot via `coolify exec`.

## Troubleshooting

- **`drift_check.sh` retorna sempre Modified:** pode ser .git mode/ACL bagunçado por sudo vs não-sudo. Validar `sudo git -C /cadencia status` (com sudo).
- **`recover_orphan_provisioning.py --force` falha sem mensagem:** a flag pula validações. Se ainda assim falha, investigar Cloudflare, Resend, Supabase e logs em `/cadencia/logs/`.

## Histórico

- `migrate_ghl_contacts.py` e `migrate_ghl_opportunities.py` são artefatos da migração concluída. Preservar para auditoria; não executar novamente.
- 2026-06-27: README criado via `/documentar-software`
- 2026-06-17: scripts atualizados em batch (ver commits)
