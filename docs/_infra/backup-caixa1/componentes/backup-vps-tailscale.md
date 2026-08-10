# Backup VPSs → CAIXA1 via Tailscale (F7 + F8)

> Sistema produtivo desde 2026-08-09. Substitui o design original (tar-over-SSH pra CAIXA1, que travava com buffer PowerShell 4GB em `/home/felipe`). VPSs Dev + Master hoje pushando delta encriptado direto pro rest-server rodando na CAIXA1, atravessando NAT via Tailscale (não CF Tunnel).

## Por que existe

O 1º design (F6) fazia `ssh vps 'tar -cf - /home' | restic backup --stdin` do CAIXA1. Falhava com 4 problemas simultâneos: sem checkpoint (stream = 1 arquivo), RAM PowerShell descontrolada (4 GB WS medidos), rede single-connection lenta, Celeron 2 cores da CAIXA1 CPU-bound em dedup+AES256. O tar de `/home/felipe` (18 GB) travou 40 min sem output.

Solução: **inverter o fluxo**. Restic client roda LOCAL na VPS (CPU melhor que Celeron), dedup+encrypt acontece antes de sair da VPS, só chunks encriptados atravessam a rede. Retomada e retry vêm nativos do restic. Rest-server na CAIXA1 é HTTP simples com basic auth.

## Por que Tailscale (não CF Tunnel)

F7 tentou primeiro **rest-server + CF Tunnel público** (`restic.cadencia.app.br`). O tunnel subiu, auth funcionou (curl com header `Mozilla/…` retornava 200). Mas `restic init` sempre recebia HTTP 403. Debug isolou a causa: **Cloudflare Bot Fight Mode** identifica o User-Agent `restic/0.16.4` como bot e devolve HTML "Enable JavaScript". Restic não executa JS → loop de challenge → 403.

Alternativas consideradas:
- **A** Skip WAF via API — bloqueado (tokens 1P sem permissão Zone WAF)
- **B** Novo token CF com WAF Edit — rejeitado (mais um segredo pra rotacionar)
- **C** Tailscale — escolhida. Ganho colateral: VPSs no tailnet abre observabilidade nativa (SSH TS, magic DNS, health-check via IP tailnet) sem depender de CF/Traefik.

CF Tunnel `restic.cadencia.app.br` continua no ar sem tráfego — deprecação pendente (issue F8).

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│  vps-dev (Hostinger)         vps-master (Hostinger)                 │
│  ├─ tailscale ip: 100.81.223.73  ├─ tailscale ip: 100.118.181.81    │
│  ├─ cron root 03:00 UTC          ├─ cron root 02:55 UTC (dumps)     │
│  │  └─ pd-restic-backup.sh       │  └─ pd-restic-dumps.sh           │
│  │     • lê /etc/pd-restic/paths.env   │                            │
│  │     • restic backup local           ├─ cron root 03:00 UTC       │
│  │                                     │  └─ pd-restic-backup.sh    │
│  └─ TCP 8000 outbound via TS          │     --dump-first            │
│                                       │                             │
└────────────────┬────────────────────────────┬───────────────────────┘
                 │                            │
                 │       (chunks CDC + AES256)│
                 ▼                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CAIXA1 (Windows 10, tailnet ip: 100.107.73.81)                     │
│  ├─ rest-server (nssm service ResticRestServer)                     │
│  │  • listen 0.0.0.0:8000  (era 127.0.0.1 antes do rebind)          │
│  │  • --path F:\restic-repos-remote                                 │
│  │  • --htpasswd-file (bcrypt: restic-client, vps-dev, vps-master)  │
│  │  • --private-repos  ← client acessa só /<username>/              │
│  │                                                                  │
│  ├─ Firewall Windows: TCP 8000 IN allow RemoteAddress=100.64/10     │
│  │                    (range CGNAT Tailscale, bloqueia internet)    │
│  │                                                                  │
│  └─ Repos separados por VPS (não deduplica entre eles, mas dentro): │
│     F:\restic-repos-remote\vps-dev\     ← 8.3 GiB → 3.3 GiB stored  │
│     F:\restic-repos-remote\vps-master\  ← 5.1 GiB → 269 MiB stored  │
└─────────────────────────────────────────────────────────────────────┘
```

## Scripts (versionados em `_shared/backup-caixa1/vps/`)

| Arquivo | Papel |
|---|---|
| `pd-restic-backup.sh` | Wrapper diário. Source-a creds + paths.env, roda `restic backup` com tag `cron-daily`, escreve stats em `/var/log/pd-restic/last-stats.json` (health-check consome via mtime). Exit codes: 0=ok, 1=parcial, 2=fatal |
| `pd-restic-forget.sh` | Retention semanal (domingo 04:00 UTC). Policy: `--keep-daily 30 --keep-weekly 12 --keep-monthly 12 --keep-tag never-delete` + `--prune` |
| `pd-restic-dumps.sh` | Só vps-master. `docker exec pg_dumpall` por container Postgres. **User real vem de `docker inspect POSTGRES_USER`**, não hard-coded como `postgres` (Coolify usa `coolify`, Lara/Evo usa `evogo`) |
| `paths.env.vps-dev` / `paths.env.vps-master` | Define `CLIENT`, `BACKUP_PATHS` (array de paths), `EXCLUDES` (array). CLIENT é explícito porque `hostname` retorna `dev`/`master`, não `vps-dev`/`vps-master` |
| `install-on-vps.sh` | Roda LOCAL na VPS como sudo. Copia creds do primeiro `/home/*/.config/restic/creds.env` pra root, instala wrapper/paths.env/log-dir, cria `/etc/cron.d/pd-restic`. Idempotente |

Scripts que ativaram F7 (rebind + install rest-server no CAIXA1):

| Arquivo | Papel |
|---|---|
| `install-restic-rest-server.ps1` | Instala rest-server v0.13.0 como serviço Windows via nssm |
| `add-restic-users.ps1` | Adiciona 3 users no htpasswd (senha bcrypt via Python — `Set-Content -NoNewline` collapsa LF, precisa Python direto) |
| `rebind-rest-server-ts.ps1` | Reconfigura AppParameters do serviço pra `--listen 0.0.0.0:8000`, abre firewall pra 100.64/10, restart. **Não usar `nssm get AppParameters` como base do replace** — retorna UTF-16 e polui o `-replace`, use string literal completa |
| `vps-restic-switch-to-ts.sh` | Roda na VPS. Faz `sed` no `creds.env` trocando URL CF Tunnel pela URL Tailscale HTTP |
| `install-cloudflared-tunnel-restic.ps1` | **DEPRECATED** — F8 vai remover o tunnel e o DNS |
| `cf-waf-skip-restic.ps1` | **DEPRECATED** — tentativa abortada (sem permissão WAF no token) |

## Cron nas VPSs

```cron
# /etc/cron.d/pd-restic — instalado pelo install-on-vps.sh

# vps-master:
55 2 * * * root /usr/local/bin/pd-restic-backup.sh --dump-first
0  4 * * 0 root /usr/local/bin/pd-restic-forget.sh

# vps-dev:
0  3 * * * root /usr/local/bin/pd-restic-backup.sh
0  4 * * 0 root /usr/local/bin/pd-restic-forget.sh
```

Cron **root** (não user felipe/master) porque wrapper escreve em `/var/log/pd-restic/`, `/var/backups/pg/`, e precisa `docker exec` sem passar por group `docker`.

## Paths backupados

**vps-dev:** `/home/felipe`, `/home/luiz`, `/etc`, `/opt/pd-framework`, `/opt/dev-docs`, `/opt/daily-brief`, `/opt/sync-dev-docs.py`
**Excludes:** `.venv`, `venv`, `node_modules`, `__pycache__`, `.next`, `dist`, `build`, `.cache`, `*.pyc`, `*.log`, `.git/objects/pack/*.pack`

**vps-master:** `/opt/pd-framework`, `/opt/cadencia-app`, `/opt/lara-ai`, `/opt/insight-artificial`, `/opt/onboarding-webhooks`, `/opt/assessoria-imprensa-cadencia`, `/opt/axis-nfse`, `/opt/stamper-telegram-bot`, `/opt/supabase-advisors`, `/opt/scripts`, `/opt/grafana-webhook`, `/opt/health-check`, `/etc`, `/var/backups/pg`, `/var/spool/cron`, `/root/.config`
**Excludes:** mesmos + `/opt/*/logs`, `/opt/coolify/*/logs`

## Métricas do first-run (2026-08-10 00:20-00:27 UTC)

| VPS | Files | Processed | Stored | Compressão | Tempo |
|---|---|---|---|---|---|
| vps-dev | 111.935 | 8.3 GiB | 5.8 GiB (dedup) → 3.3 GiB (comp) | 43% | 3:51 |
| vps-master | 137.970 | 5.1 GiB | 358 MiB (dedup) → 268 MiB (comp) | 26% | 1:40 |

Dumps Postgres vps-master antes do backup: `coolify-db` (user=coolify) 25 MB + `postgres-otklj...` (user=evogo) 16 MB.

Segundo run diário deve ser << 1 min por VPS (só delta CDC).

## Health-check

Registry `Posicionamento-Digital/health-check`, buckets `master` e `dev`:

```json
{
  "label": "pd-restic backup (VPS -> CAIXA1)",
  "check": "mtime",
  "path": "/var/log/pd-restic/last-stats.json",
  "sudo": true,
  "max_h": 26,
  "crit": true,
  "fix": "issue"
}
```

Se `last-stats.json` >26h, health-check abre issue `own:agente` no Linear.

## Restore

```bash
# Na VPS (source do backup — reusa creds.env root)
source /root/.config/restic/creds.env
source /etc/pd-restic/paths.env    # define CLIENT
export RESTIC_REPOSITORY="rest:http://${REST_USER}:${REST_PASS}@100.107.73.81:8000/${CLIENT}/"
export RESTIC_PASSWORD="${REPO_PWD}"

restic snapshots                                      # lista tudo
restic ls <snap-id> /path/to/file                     # lista dentro do snap
restic restore <snap-id> --target /tmp/rec --include /path/to/file
```

Restore **cross-VPS** (recuperar arquivo da master a partir da dev) exige trocar a URL pra `/vps-master/` mas mesmas credenciais funcionam (o basic auth acessa qualquer path no `--private-repos` se o user bater com o path — user `vps-master` acessa `/vps-master/`, user `vps-dev` acessa `/vps-dev/`). Cross-VPS via CAIXA1 (usa `restic-client` user, que tem acesso amplo).

## Credenciais

**1Password:**
- `restic - CAIXA1 rest-server basic auth` (vault Databases, campo `password`) — mesma senha bcrypt pros 3 users, roles por path via `--private-repos`
- `restic - CAIXA1 backup repo` (vault Databases, campo `password`) — passphrase de encriptação do repo restic (idêntica pros 2 repos vps-dev + vps-master)

**Nas VPSs:**
- `~felipe/.config/restic/creds.env` (600) — origem original
- `/root/.config/restic/creds.env` (600) — copiada pelo `install-on-vps.sh` (cron root usa esta)

**Auth-key Tailscale reusable** (usada 1× pra ativar vps-dev + vps-master, expira em 90d): **não persistida no 1P** porque SA não tem write em vault Hosts. Se precisar adicionar 3ª VPS antes de nov/2026, gerar nova via API.

## Gotchas descobertos no debug

1. **Cloudflare Bot Fight Mode bloqueia restic client** — qualquer futura exposição de protocolo binário via CF Tunnel público precisa de WAF Skip **antes** de testar.
2. **`hostname` na VPS retorna `dev`/`master`**, não `vps-dev`/`vps-master`. CLIENT vem do `paths.env`, não de `$(hostname)`.
3. **`pg_dumpall -U postgres` falha em Coolify** — role não existe. User real vem de `docker inspect --format '{{range .Config.Env}}...' POSTGRES_USER=…`.
4. **`nssm get AppParameters` retorna UTF-16** — `-replace` no PowerShell trata como string mas o `set` reenvia bytes com nulls no meio, resultado quebrado. Setar string literal completa é a saída.
5. **`Set-Content -NoNewline` no htpasswd colapsa linhas** — 3 users viram 1 linha. Escrever htpasswd via Python direto com `newline='\n'`.
6. **SCP falha na CAIXA1** ("Connection closed") — SFTP subsystem não habilitado. Usar `cat > file` via SSH stdin, ou base64 + PowerShell inline.
7. **CRLF em `creds.env`** copiado do Windows quebra `bash source` — `sed -i 's/\r$//'` depois de copiar.
8. **`/etc/health-check/.git/objects` com perms root** — `git pull` como user master falha. Fix: `sudo chown -R master:master .git`.

## Refs

- Repo próprio health-check: [Posicionamento-Digital/health-check](https://github.com/Posicionamento-Digital/health-check)
- Docs restic upstream: https://restic.readthedocs.io/
- rest-server upstream: https://github.com/restic/rest-server
- Linear: [DEV-1735 (F7 fechada)](https://linear.app/cadencia/issue/DEV-1735), [DEV-1736 (F8)](https://linear.app/cadencia/issue/DEV-1736)
- Doc geral CAIXA1: [`../README.md`](../README.md)
- Doc motor restic: [`restic.md`](restic.md)
