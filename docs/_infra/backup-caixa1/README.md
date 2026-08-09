# Backup + Cloud CAIXA1

Sistema completo de backup diário automatizado + cloud pessoal HTTPS rodando na VPS Local CAIXA1 (Windows 10, Celeron J1800, 8 GB RAM dual-channel, 1,4 TB HD).

- **Projeto Linear:** [Infra — Backup + Cloud CAIXA1](https://linear.app/cadencia/project/infra-backup-cloud-caixa1-6ccf2c5c9ac7)
- **Issue-mãe:** [DEV-1726](https://linear.app/cadencia/issue/DEV-1726)
- **Plano canônico:** [`times/infra/context/plano-backup-caixa1.md`](../../times/infra/context/plano-backup-caixa1.md)
- **Inventário fonte:** [`times/infra/context/inventario-vps-2026-08.md`](../../times/infra/context/inventario-vps-2026-08.md)
- **Doc infra:** `Obsidian_Vaults_Pessoal/Infra/2026-08-08 VPS Local CAIXA1 (Windows).md`

## O que faz

1. **Backup diário 03h** (`restic` snapshot-style, deduplicado, encriptado) cobrindo:
   - VPS Dev: filesystem + `pg_dump` Lara Postgres + `mysqldump` EasyAppointments + crontabs
   - VPS Master: Coolify dump + `pg_dump` apps gerenciados + filesystem + docker volumes + crontabs
   - Supabase: `pg_dump` por project (Cadencia + HubPD)
   - Vercel: env vars encriptadas GPG
   - GitHub: mirror clone de todos os repos privados
   - 1Password: snapshot metadata (estrutura)
   - Notebook: pd-framework + Obsidian vaults + `.claude` + OneDrive (via SMB Tailscale)

2. **Backup semanal domingo 04h**: Linear + Cloudflare DNS + Resend events

3. **Cloud pessoal HTTPS**: [https://cloud.cadencia.app.br](https://cloud.cadencia.app.br) via Filebrowser + Cloudflare Tunnel, expondo `D:\PD-Cloud` pra compartilhar arquivos/links com clientes

4. **Notificação em falha**: WhatsApp comercial via Evo (`evo_client.py`) — silêncio = sucesso

## Componentes internos

### Backup runtime (rodam agendados no Task Scheduler Windows)

| Script | Papel |
|---|---|
| `_common.ps1` | Helpers: log, notif Evo em falha, restic env (senha via 1P), retention 30-12-12 |
| `backup-github.ps1` | `gh repo list` + `git clone --mirror` de repos privados → `F:\Backups\GitHub\` |
| `backup-supabase.ps1` | `pg_dump` por project via connection string 1P → `F:\Backups\Supabase\*.sql.gz` |
| `backup-vps-dev.ps1` | SSH + `docker exec pg_dumpall/mysqldump` + `restic backup` tar-over-SSH de `/home` + `/opt` |
| `backup-vps-master.ps1` | SSH + Coolify metadata dump + `pg_dump` apps + `restic` filesystem `/data/coolify` |
| `backup-vercel.ps1` | `vercel env pull` por project + GPG encrypt → `F:\Backups\Vercel\*.gpg` |
| `backup-1p.ps1` | `op vault list` + `op item list` snapshot metadata → `F:\Backups\1P\*.json.gz` |
| `backup-notebook.ps1` | `restic backup` do notebook via SMB Tailscale (pd-framework + Obsidian + `.claude` + OneDrive) |
| `backup-semanal.ps1` | Linear API GraphQL + Cloudflare DNS API + Resend events API → JSON gzip |
| `run-all-backups.ps1` | Wrapper: chama todos os `backup-*.ps1` + restic consolidation `F:\Backups\` + retention 30-12-12 |

### Instalação e utilidades (rodam manualmente, 1×)

| Script | Papel |
|---|---|
| `install-scheduled-tasks.ps1` | Cria 2 Tasks Windows: `PD-Backup-Daily` (03h) + `PD-Backup-Weekly` (domingo 04h) |
| `install-filebrowser.ps1` | Instala Filebrowser v2.32.0 + admin user (senha 1P) + serviço Windows via nssm |
| `install-cloudflared-tunnel.ps1` | Cria tunnel via Cloudflare API + configura ingress + DNS CNAME + serviço nssm |
| `restic-check.ps1` | Lista snapshots + stats do repo restic |
| `validate-restore.ps1` | Teste end-to-end: backup 1 pasta → restore em `C:\Temp` → valida arquivos |
| `test-evo-notif.ps1` | Dispara notificação Evo simulada pra validar canal de falha |
| `cf-check-token.ps1` / `cf-get-account.ps1` / `cf-test-credentials.ps1` / `cf-test-cloudfare-item.ps1` / `cf-inspect-items.ps1` | Diagnóstico Cloudflare (permissões de token, discovery de account/zone) |

## Deploy na CAIXA1

```powershell
# 1. Setup inicial (roda 1×, via SSH ou RDP)
cd C:\dev\pd-framework
git pull
Copy-Item _shared\backup-caixa1\*.ps1 C:\Scripts\backup\ -Force

# 2. Instalar tasks agendadas (roda 1×)
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Scripts\backup\install-scheduled-tasks.ps1

# 3. Setup Filebrowser + Cloudflare Tunnel (roda 1×, se ainda não estiver)
powershell -NoProfile -ExecutionPolicy Bypass -File _shared\backup-caixa1\install-filebrowser.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File _shared\backup-caixa1\install-cloudflared-tunnel.ps1

# 4. Deploy de atualizações (roda sempre que scripts mudam)
cd C:\dev\pd-framework && git pull && Copy-Item _shared\backup-caixa1\*.ps1 C:\Scripts\backup\ -Force
```

## Storage layout no F: (PD-Backup)

```
F:\
├── restic-repo\                   ← repo restic encriptado (todas fontes filesystem)
├── Backups\
│   ├── VPS-Dev\db-dumps\          ← pg_dump/mysqldump + crontabs
│   ├── VPS-Master\coolify-dump\   ← Coolify metadata dump
│   ├── VPS-Master\db-dumps\       ← pg_dump apps gerenciados
│   ├── Supabase\                  ← *.sql.gz por project
│   ├── Vercel\                    ← *.gpg encriptado
│   ├── GitHub\<owner>\<repo>.git\ ← mirror bare clones
│   ├── 1P\                        ← snapshot metadata *.json.gz
│   ├── Linear\ Cloudflare\ Resend\ ← semanais
└── Logs\backup\run-<data>.log     ← rotativo 30 dias
```

## Credenciais no 1Password

| Item | Vault | Campo | Uso |
|---|---|---|---|
| `restic - CAIXA1 backup repo` | Databases | password | Senha do repo restic (gerada 40-char) |
| `Filebrowser CAIXA1 admin` | Databases | password | Login admin Filebrowser (user `felipe`) |
| `Cloudflare Tunnel caixa1-cloud` | Hosts | token | Tunnel run token (regerável via API) |
| `Cloudfare` (typo) | Hosts | credencial | CF API token com Account.Tunnel |
| `Cloudflare - API Token + Zones` | Hosts | api_token | CF API token com Zone.DNS |
| `Supabase - Cadencia [ClaudeCode]` | Databases | password | Connection string pg_dump |
| `Supabase - HubPD - [ClaudeCode]` | Databases | password | Connection string pg_dump |

## Regras absolutas

- **READ-ONLY sobre sistemas alvo** — jamais delete/update/drop em VPS/Supabase/Vercel/GitHub/1P/Cloudflare/Resend/Linear. Escrita só em `F:\` da CAIXA1.
- **Nunca imprimir credencial** — usar `--fields <name> --reveal` mas nunca `Format-Table` com type STRING que contém segredos.
- **Senha restic no 1P + cópia impressa** — perder senha = perder repo inteiro (dados irrecuperáveis).
- **Notif falha obrigatória** — silêncio ≠ sucesso; wrapper dispara WhatsApp comercial em qualquer script que retornar exit ≠ 0.

## Retention e restore

- **Retention:** `--keep-daily 30 --keep-weekly 12 --keep-monthly 12 --prune` (aplicada pelo wrapper após todos os backups)
- **Restore de emergência (setup-free):**
  ```powershell
  $env:RESTIC_PASSWORD = op item get "restic - CAIXA1 backup repo" --vault Databases --fields password --reveal
  $env:RESTIC_REPOSITORY = "F:\restic-repo"
  C:\Tools\restic\restic.exe snapshots
  C:\Tools\restic\restic.exe restore latest --target C:\restore\
  ```
- **6 cenários de disaster + procedimento passo-a-passo:** ver `times/infra/context/plano-backup-caixa1.md` §5

## Cloud pessoal (Filebrowser)

- **URL:** [https://cloud.cadencia.app.br](https://cloud.cadencia.app.br)
- **Login:** user `felipe`, senha em 1P vault Databases item `Filebrowser CAIXA1 admin`
- **Root:** `D:\PD-Cloud` (na CAIXA1)
- **Serviço Windows:** `Filebrowser` (auto-start, nssm)
- **Tunnel:** `caixa1-cloud` (id `447af324-...`), 4 conexões QUIC ativas gru02/07/11/18
- **Serviço Windows:** `CloudflaredTunnel` (auto-start, nssm)
- **Share links:** geráveis pelo Filebrowser UI com expiração + senha opcional

## Troubleshooting

| Sintoma | Causa | Fix |
|---|---|---|
| Backup falha silenciosamente | Silêncio ≠ sucesso, mas verificar `F:\Logs\backup\run-<data>.log` | Rodar `run-all-backups.ps1` manual e observar |
| Serviço Filebrowser parado | nssm serviço travou | `Get-Service Filebrowser; Start-Service Filebrowser` (ou `nssm start Filebrowser`) |
| HTTPS cloud.cadencia.app.br 404 | Cloudflare Universal SSL propagando (após criar tunnel) | Aguardar 5-15 min |
| CloudflaredTunnel Paused | Token inválido ou expirado | Regenerar via `install-cloudflared-tunnel.ps1` |
| Restic snapshots vazio após backup | Script não passou pelo restic (só criou dump cru) | Verificar se `run-all-backups.ps1` rodou o step `restic backup F:\Backups` |

## Pendências conhecidas

- [ ] Rotacionar 3 tokens Cloudflare vazados durante debug de F5 (rastreamento no Linear)
- [ ] Validar restore de DB Supabase + Docker volume após primeiro run automatizado
- [ ] Observar 7 dias consecutivos de backup limpo (até 16/08/2026)
- [ ] Deploy off-site opcional (Cloudflare R2 ou Backblaze B2) — fase 2, fora de escopo atual
