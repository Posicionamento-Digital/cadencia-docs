# Paths e storage — VPS Dev

> `ls -la` + `du -sh` + `docker volume ls` reais coletados em 2026-07-31.

## `/home/felipe/` — home do Felipe (35 dirs)

```
Rotina/                        # clone repo rotina (não confirmado)
cadencia-autofix/              # worker autofix (cron 15min) — CAD-689
health-dev/                    # dev_selfreport (cron 10min)
pos-briefing-trigger.sh        # cron script CSE-97 (path referencia pd-framework-main)
transcricoes-inbox/            # inbox pra pos-briefing
pd-framework/                  # clone canônico do framework
pd-framework-main/             # ⚠️ possível clone antigo? referenciado por pos-briefing
.hermes/                       # Hermes Agent (data + repo clonado) — third-party
.motor/                        # {claude,codex} bind mount pro pd-motor container
.self-test/                    # (não investigado)
.health-dev/                   # (mesma coisa que health-dev/? investigar)
.pd-hooks/                     # hooks do framework
.multi_mcp/                    # multi_mcp config (não confirmado uso)
.sentry/ + .sentryclirc        # Sentry CLI config
.claude/ + .claude.json (52KB) # Claude Code sessions persistidas
.codex/                        # Codex CLI sessions
.config/                       # inclui op/service-account-token
.local/, .npm/, .nvm/          # padrão node/python
.bashrc, .profile              # dotfiles
.gitconfig
```

**Ownership:** tudo `felipe:felipe` (uid 1000). Exceção: `..` é `root:root` (dir /home).

## `/home/luiz/` — inerte pós-desligamento

```
drwxr-xr-x  8 luiz luiz     # recriado nos 18min entre kill e reboot (30/07 18:04 UTC)
.bash_history (61 bytes)     # ls + claude + tmux — atividade mínima
.bashrc, .bash_logout         # dotfiles default
.cache/                      # cache do Claude Code
.claude/ + .claude.json       # sessions do último Claude aberto
.npm/                         # cache node
.ssh/authorized_keys          # ESVAZIADO 30/07 (chave revogada)
```

Home **preservado** por escolha explícita ("só corte o acesso"). User existe mas sem grupos privilegiados, sem senha, sem chave. Inerte. Se decidir deletar depois: `sudo userdel -r luiz` (safe — 0 processos rodam como uid 1001 hoje).

## `/home/renan/` — NÃO EXISTE

Deletado via `userdel -r renan` em 30/07 ~14h BRT. Backup em `/root/renan-preserve/`.

## `/opt/` — scripts de sistema

```
drwx--x--x  4 root   root    containerd/                     # docker containerd runtime
drwxr-xr-x  2 root   root    daily-brief/                    # brief.py + queue.py (cron 11h/21h30)
drwxrwxrwx  2 felipe felipe  dev-docs/                       # docs sincronizados (cron 23h)
drwxr-xr-x  2 luiz   luiz    luiz-state/                     # ⚠️ ÓRFÃO — luiz_state.py + luiz_state_cron.sh
drwxr-xr-x  3 root   root    pd-framework/                   # só tem _shared/ (subset do framework)
-rwxr-xr-x  1 root   root    sync-dev-docs.py                # script cron 23h
```

## `/root/luiz-preserve/` — backup pré-desligamento Luiz

```
drwxr-xr-x  3 root root      304K total
-rw-r--r--  PROCESSO-PR-DEPLOY-VERCEL.md    # doc que Vitor escreveu, cópia local do Luiz
-rw-------  authorized_keys.bak.2026-07-30  # 3 chaves SSH revogadas (backup fingerprint)
-rw-------  bash_history (20KB)             # histórico shell dele
-rw-------  claude.json (76KB)              # último state Claude Code
drwx------  config-backup/                  # ~/.config completo (gh, op, opencode, zed)
-rw-r--r--  dev-1465-qr-prep.patch (3.4KB)  # stash preservado durante Fase A
-rw-r--r--  dev-1614-snapshot-completo.patch (64KB) # PR pendente DEV-1614
-rw-r--r--  gitconfig                       # user.email/name dele
drwxr-xr-x  pos-invasao-18min/              # backup dos 18min de recuperação de acesso
  ├── bash_history                          # atividade nesses 18min (só claude+tmux)
  ├── claude.json                           # state Claude da sessão
  └── authorized_keys_nova.bak              # chave nova (lucns@Predator) revogada
```

## `/root/renan-preserve/` — backup pré-deleção Renan

```
104K total
- PROCESSO-PR-DEPLOY-VERCEL.md?  (verificar — pode não estar aqui, era só do Luiz)
- authorized_keys.bak.2026-07-30
- bash_history
- claude.json
- config-backup/                  # ~/.config
- cadencia-docs-cli.patch         # único trabalho não commitado com valor (cadencia-cli.md)
- gitconfig
```

## Docker storage — `/var/lib/docker/`

```
/var/lib/docker/volumes    2.5G      # 18 volumes locais
/var/lib/docker/containers 65M       # 16 containers (7 up + 9 exited)
/var/lib/docker/image      128K      # metadata images
/var/lib/docker/overlay2   (não medido — mas provável 3-5GB)
```

**Volumes nomeados (persistentes):**
```
cadencia-agenda-mysql-data       # MySQL do Easy!Appointments (~poucos MB, banco vazio)
lara-postgres-data               # Postgres da Lara GCI-GO (3 tenants ~mês de dados)
lara-redis-data                  # AOF Redis da Lara
```

**Volumes anônimos (14 restantes)** — hashes uuid. Provavelmente dos 9 containers Attemys exited + alguns descartáveis. Vale rodar `sudo docker volume prune -f` DEPOIS de deletar os Attemys, pra limpar sem risco.

## Storage disponível

```
df -h  # (não coletei — TODO próxima passada)
```

## Backups fora da VPS

**Não há backup automático da VPS Dev.** Snapshot Hostinger é a única rede de segurança (fora do nosso controle direto). Se um volume corromper (`lara-postgres-data`), dados vão a menos que snapshot recente cubra.

**Para backups pontuais críticos:**
```bash
# Postgres Lara
sudo docker exec lara-postgres pg_dump -U lara lara | gzip > /root/backup-lara-$(date -u +%Y%m%dT%H%M).sql.gz

# Home Felipe
sudo tar czf /root/backup-felipe-home-$(date -u +%Y%m%d).tar.gz /home/felipe/

# Copiar pra Master (que tem mais espaço + fica em outra máquina)
scp /root/backup-*.sql.gz master@72.60.4.71:/backups/vps-dev/
```

## Refs

- Snapshot antigo (desatualizado, mas útil pra comparar): `docs/snapshots/vps-dev-2026-05-25.md`
- Backup preservado do Luiz: `/root/luiz-preserve/`
- Backup preservado do Renan: `/root/renan-preserve/`
