---
data: 2026-08-08
issue: DEV-1728
projeto: Infra — Backup + Cloud CAIXA1
issue_mae: DEV-1726
depende_de: DEV-1727 (inventário)
---

# Plano de Backup — CAIXA1

Doc canônico do sistema de backup diário automatizado que a CAIXA1 (VPS Local Windows) executa. Baseia decisões nos dados coletados em [DEV-1727](https://linear.app/cadencia/issue/DEV-1727) (`inventario-vps-2026-08.md`).

## 1. Princípios

1. **Backup só é backup se restore funciona** — F6 valida restore em ≥3 tipos de fonte antes de fechar o projeto.
2. **Snapshot-style, deduplicado e encriptado** — `restic` é o motor central (equivalente ao snapshot da Hostinger). Primeiro backup ~100 GB, incrementais diários em MB.
3. **Falha ruidosa** — qualquer job que falha dispara notificação WhatsApp via Evo comercial. Silêncio ≠ sucesso.
4. **Um comando de restore de emergência documentado por cenário** — quem restaurar não deve precisar reconstruir o raciocínio.
5. **Retention determinística** — `--keep-daily 30 --keep-weekly 12 --keep-monthly 12` em todas as fontes. Retention consistente vale mais que retention perfeita por fonte.

## 2. Storage layout no HD `F:` (PD-Backup)

```
F:\
├── restic-repo\                         ← repo restic encriptado (todas fontes filesystem)
│   ├── config
│   ├── data\
│   ├── index\
│   ├── keys\
│   └── snapshots\
├── Backups\
│   ├── VPS-Dev\
│   │   ├── db-dumps\
│   │   │   ├── lara-postgres-<YYYYMMDD>.sql.gz
│   │   │   ├── cadencia-agenda-mysql-<YYYYMMDD>.sql.gz
│   │   │   └── crontabs-<YYYYMMDD>.txt
│   │   └── (fs vai direto pro restic-repo)
│   ├── VPS-Master\
│   │   ├── coolify-dump\
│   │   │   └── coolify-<YYYYMMDD>.tar.gz
│   │   ├── db-dumps\
│   │   │   ├── evolution-<YYYYMMDD>.sql.gz
│   │   │   ├── lara-legada-<YYYYMMDD>.sql.gz
│   │   │   ├── ecuro-<YYYYMMDD>.sql.gz
│   │   │   ├── confirmation-queue-<YYYYMMDD>.sql.gz
│   │   │   ├── cadencia-agenda-master-<YYYYMMDD>.sql.gz
│   │   │   └── crontabs-<YYYYMMDD>.txt
│   │   └── (fs + docker volumes vão direto pro restic-repo)
│   ├── Supabase\
│   │   ├── cadencia-<YYYYMMDD>.sql.gz
│   │   ├── hubpd-<YYYYMMDD>.sql.gz
│   │   └── outros-<YYYYMMDD>.sql.gz
│   ├── Vercel\
│   │   └── <project>-envs-<YYYYMMDD>.txt.gpg
│   ├── GitHub\
│   │   └── <org>\<repo>.git\           ← mirror clones (git fetch --all diário)
│   ├── 1P\
│   │   └── 1p-export-<YYYYMMDD>.zip.gpg
│   ├── Linear\
│   │   └── linear-<YYYYMMDD>.json.gz   ← semanal
│   ├── Cloudflare\
│   │   └── cf-<YYYYMMDD>.json          ← semanal
│   └── Resend\
│       └── events-<YYYYMMDD>.json.gz   ← semanal
└── Logs\
    └── backup\
        └── run-<YYYYMMDD>.log          ← rotativo 30 dias
```

Nota: dumps em `Backups\` são inputs pro `restic-repo\` (o repo dedupa entre versões). Manter arquivos crus em paralelo agiliza restore de casos triviais sem precisar `restic restore`.

## 3. Fontes e estratégia por fonte

### 3.1 VPS Dev (`ssh vps-dev`)

| O quê | Como | Frequência |
|---|---|---|
| `/home/felipe`, `/home/luiz`, `/opt` | `restic backup` via SSH | diário |
| DB Lara nova (`lara-postgres` container) | `docker exec lara-postgres pg_dump -U <user> <db>` → `.sql.gz` → restic | diário |
| MySQL EasyAppointments (`cadencia-agenda-mysql`) | `docker exec cadencia-agenda-mysql mysqldump ...` → `.sql.gz` → restic | diário |
| Redis Lara (`lara-redis`) | ❌ **NÃO backupar** — é cache reconstrível | — |
| Docker volumes não-DB | `restic /var/lib/docker/volumes/` (só volumes que NÃO são de DB) | diário |
| Crontabs (felipe + root via sudo) | `crontab -l; sudo crontab -l` → `crontabs-<data>.txt` → restic | diário |

### 3.2 VPS Master (`ssh -i ~/.ssh/hostinger_prod_master master@72.60.4.71`)

| O quê | Como | Frequência |
|---|---|---|
| Coolify metadata (banco interno) | **Backup nativo Coolify** — dashboard config'do pra dump diário em local mount → copiado pra F: via SCP. Fallback manual: `docker exec coolify-db pg_dump -U postgres coolify` | diário |
| DBs dos apps gerenciados (Evolution, Lara legada, Ecuro, Confirmation-queue, EasyAppointments Master) | `docker exec <container> pg_dump/mysqldump` por container identificado | diário |
| `/data/coolify` | `restic backup` via SSH (contém app configs, deploys) | diário |
| `/var/lib/docker/volumes` — volumes NÃO de DB | `restic backup` via SSH | diário |
| `/opt`, `/etc`, `/root/scripts` | `restic backup` via SSH | diário |
| Crontabs (master + root) | idem VPS Dev | diário |

### 3.3 Supabase

| O quê | Como | Frequência |
|---|---|---|
| Cadencia project | `pg_dump` via connection string (1P: `Supabase - Cadencia [ClaudeCode]`) | diário |
| Hub PD project | idem (1P: `Supabase - HubPD - [ClaudeCode]`) | diário |
| Outros projects | idem — descobertos via `npx supabase projects list` | diário |

Dumps `.sql.gz` vão pra `F:\Backups\Supabase\` e são consumidos pelo restic (dedupe entre versões).

### 3.4 Vercel

| O quê | Como | Frequência |
|---|---|---|
| Env vars de todos os projects | `vercel env pull` por project → encriptar com GPG (chave dedicada, senha 1P) → F: | diário |
| Código | ❌ **NÃO** — GitHub é fonte de verdade |
| Deploys / builds | ❌ **NÃO** — rollback nativo Vercel funciona |

### 3.5 GitHub

| O quê | Como | Frequência |
|---|---|---|
| Repos privados da conta felipeluissalgueiro | `gh repo list --limit 1000 --json name,url` + `git clone --mirror` (ou `git fetch --all` se já existir) | diário |
| Repos da org Posicionamento-Digital | idem, `gh repo list Posicionamento-Digital --limit 1000` | diário |
| Issues / PRs / Wiki | fora de escopo por ora (baixa prioridade) | — |

### 3.6 1Password

| O quê | Como | Frequência |
|---|---|---|
| Export completo | `op export` → zip encriptado com GPG (senha 1P separada, guardar impressa) → F: | diário |

Cuidado: export do 1P sai em plaintext antes de encriptar. Encriptação com GPG é obrigatória; deletar plaintext imediatamente. Senha GPG guardada em `Hosts` no 1P + cópia impressa/física.

### 3.7 Notebook (via Tailscale)

| O quê | Como | Frequência |
|---|---|---|
| `C:\dev\pd-framework` | `restic backup` do CAIXA1 puxando via `\\notebook.tailscale-mesh\C$\dev\pd-framework` OU push direto do notebook | diário |
| `C:\Users\felip\Obsidian_Vaults_*` | idem | diário |
| `C:\Users\felip\.claude` | idem (exclui `.claude/projects/*.jsonl` — transcripts recuperáveis) | diário |
| `C:\Users\felip\OneDrive\Documentos` | idem — cobre `Hub Projetos`, `Customer Success`, `Credenciais` | diário |

Nota: OneDrive já tem versionamento nativo, mas backup local dá restore instantâneo sem depender de conta MS.

### 3.8 Semanal

| Fonte | O quê | Como |
|---|---|---|
| Linear | issues + projects + docs export | API `linear.app` → JSON gzip → F: |
| Cloudflare | DNS records + tunnels + workers configs | API por zone → JSON → F: |
| Resend | events (delivered/bounced/complained) últimos 7 dias | API events → JSON gzip → F: |

## 4. Retention

Aplicada via `restic forget --keep-daily 30 --keep-weekly 12 --keep-monthly 12 --prune` após cada backup.

- **30 dias diários** — restore pontual de última semana/mês
- **12 semanas** — cobre trimestre
- **12 meses** — cobre 1 ano (redundância anti-catástrofe)

Total esperado no F: (596 GB): primeiro backup ~100 GB, delta médio ~2 GB/dia. Depois de 1 ano: ~300 GB dedupados. Folga confortável.

## 5. Restore procedure — cenários

### 5.1 "Perdi arquivo do notebook"

```powershell
# Lista snapshots do notebook
restic -r F:\restic-repo snapshots --tag notebook

# Restaura arquivo específico do snapshot de N dias atrás
restic -r F:\restic-repo restore <snapshot-id> --target C:\restore\ --include "C:\dev\pd-framework\times\infra\<arquivo>"
```

Tempo estimado: < 5 min.

### 5.2 "Supabase apagou tabela"

```powershell
# Restaura dump do último dia
gunzip -c F:\Backups\Supabase\cadencia-20260808.sql.gz > cadencia-20260808.sql

# Sobe Postgres temp local
docker run -d --name pg-restore -p 55432:5432 -e POSTGRES_PASSWORD=temp postgres:15
psql -h localhost -p 55432 -U postgres -f cadencia-20260808.sql

# Extrai só a tabela e re-injeta na produção
pg_dump -h localhost -p 55432 -U postgres -t <tabela> > tabela.sql
psql "postgresql://<supabase-connection>" -f tabela.sql
```

Tempo estimado: 15-30 min.

### 5.3 "VPS Master crashou total"

Sequência:
1. Provisionar nova VM Hostinger
2. Instalar Docker + Coolify
3. Restaurar `/data/coolify` do restic-repo → montar em `/data/coolify` da nova VM
4. Restaurar `coolify-db` dump em Postgres novo (Coolify vai reconectar)
5. Restaurar docker volumes de DBs por app (`docker volume create` + `restic restore` + subir container)
6. Ajustar DNS Cloudflare pro novo IP

Tempo estimado: 3-6 horas dependendo do tamanho dos volumes.

### 5.4 "GitHub bloqueou conta"

```bash
# Cada mirror clone em F:\Backups\GitHub\<org>\<repo>.git é um repo bare completo
cd F:\Backups\GitHub\felipeluissalgueiro\cadencia-app.git
git worktree add /tmp/restore main
# Ou push pra novo remoto (GitLab, Bitbucket, self-hosted)
git remote add new-remote git@gitlab.com:...
git push new-remote --all --tags
```

Tempo estimado: 1-2 horas pra restaurar acesso operacional.

### 5.5 "1P bloqueou conta"

```powershell
# Export mais recente encriptado
gpg --decrypt F:\Backups\1P\1p-export-20260808.zip.gpg > 1p-export.zip
# Descompactar e importar em cliente 1P novo, Bitwarden, ou Vaultwarden self-hosted
```

Tempo estimado: 30 min-1h.

### 5.0 Comando de restore de emergência (setup-free)

Se você precisa restaurar algo agora, sem ler nada além disto:

```powershell
# Na CAIXA1 (via SSH ou local):
$env:RESTIC_PASSWORD = cmd /c "op item get `"restic - CAIXA1 backup repo`" --vault Databases --fields password --reveal < NUL"
$env:RESTIC_REPOSITORY = "F:\restic-repo"

# Lista todos os snapshots
C:\Tools\restic\restic.exe snapshots

# Restaura último snapshot completo pra C:\restore\
C:\Tools\restic\restic.exe restore latest --target C:\restore\

# Restaura arquivo específico
C:\Tools\restic\restic.exe restore <snapshot-id> --target C:\restore\ --include "/path/no/backup"
```

Se `op` não estiver disponível, a senha está no 1P vault `Databases`, item `restic - CAIXA1 backup repo` (ID: `tfso2ux7uajctdq4nbawainkn4`).

### 5.6 "Restic repo corrompeu"

```powershell
# Check integridade (roda semanal automático)
restic -r F:\restic-repo check --read-data

# Se corrompido: fallback pros dumps crus em F:\Backups\ (sem incrementalidade mas dados presentes)
```

Última linha de defesa: os dumps crus em `F:\Backups\<fonte>\` não dependem de restic. Se restic morrer, ainda temos o essencial.

## 6. Monitoramento

### 6.1 Log local
Todo script escreve em `F:\Logs\backup\run-<YYYYMMDD>.log` (formato: timestamp | fonte | ação | status | tamanho | duração). Rotação: 30 dias.

### 6.2 Notificação de falha
Wrapper `run-all-backups.ps1` captura exit code de cada script. Qualquer falha → mensagem WhatsApp via `evo_client.py` pro número comercial de Felipe:

```
[BACKUP CAIXA1] ❌ FALHA <fonte> em <data> <hora>
Erro: <primeira linha do stderr>
Log completo: F:\Logs\backup\run-<data>.log
```

Sucesso silencioso — sem notificação diária de sucesso (evita ruído). Digest semanal (domingo 10h) com resumo dos 7 dias: quantos backups OK, tamanhos, retention aplicada.

### 6.3 Deadman
Se nenhum backup rodar por 48h, cron separado na CAIXA1 dispara alerta ("último snapshot restic tem mais de 48h — CAIXA1 sem backup"). Detecta cenário onde CAIXA1 desligou/travou e ninguém notou.

## 7. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Dump Postgres inconsistente (transações em vôo) | `pg_dump` usa snapshot transacional consistente — seguro em produção |
| Docker volume DB "quente" copiado pelo restic gera dump corrompido | Excluir `docker/volumes/*postgres-data*` do restic; DBs vão só via `pg_dump` |
| HD F: falha | Off-site futuro (Cloudflare R2 ou Backblaze B2) — fora de escopo dessa fase |
| Senha restic perdida | Guardada em 1P vault `Hosts` + cópia impressa/física em envelope selado |
| Senha GPG (Vercel envs, 1P export) perdida | Idem — 1P + cópia impressa |
| CAIXA1 rouba/incendeia | Off-site futuro (fase 2) — hoje risco aceito |
| Backup rodando durante uso pesado da VPS Master | Agendado 03h00 (madrugada); pg_dump usa `--jobs=1` pra minimizar contenção |

## 8. Dependências

- Restic instalado no CAIXA1 (F3 — DEV-1730)
- Senha restic no 1P (F3)
- HDs renomeados (F2 — DEV-1729)
- Chaves SSH CAIXA1 → VPS Dev + Master já validadas (session 08/08 01:02)
- `op` service account rodando no CAIXA1 (validado)
- `evo_client.py` acessível do CAIXA1 (validar em F4)

## 9. Referências
- Inventário fonte: [`inventario-vps-2026-08.md`](./inventario-vps-2026-08.md) — F0/DEV-1727
- Skills: `/vps-local`, `/vps-local-acesso-remoto`
- Doc VPS Local: `Obsidian_Vaults_Pessoal/Infra/2026-08-08 VPS Local CAIXA1 (Windows).md`
- Restic docs: https://restic.readthedocs.io/
- Coolify backup: https://coolify.io/docs/knowledge-base/backup
