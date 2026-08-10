# restic — motor de backup CAIXA1

## O que é

Backup **snapshot-based deduplicado + encriptado**. Single binary Go (~27 MB), roda nativo Windows/Linux/Mac. Zero dependência de toolchain. Padrão da indústria pra backup self-hosted (usado por Backblaze e Cloudflare internamente).

Não é sync bidirecional — é fluxo unidirecional (origem → repo). Restic é **arquivo do passado** ("como estava em dia X"), não espelho do presente.

## Como funciona

### Content-Defined Chunking (CDC)

Restic quebra arquivos em pedaços variáveis de ~1-8 MB usando **Rabin fingerprinting** — algoritmo que detecta "fronteiras naturais" no conteúdo, não offsets fixos. Consequências:

- Mesmo conteúdo em arquivos diferentes → mesmo chunk (dedup automático)
- Alteração no meio de arquivo grande → só o chunk afetado muda
- Renomear arquivo → 0 bytes novos (só metadado no manifest)
- Move arquivo entre pastas → 0 bytes novos

Isso explica porque o segundo backup diário roda em minutos e ocupa poucos MB — mesmo com dumps `.sql.gz` de dezenas de MB, 95%+ do conteúdo são chunks já indexados.

### Estrutura do repo

```
F:\restic-repo\
├── config          ← metadados do repo (encriptado)
├── keys\           ← chaves derivadas da senha (PBKDF2 + scrypt)
├── data\           ← pack files (chunks encriptados AES-256 CTR)
├── index\          ← catálogo de chunks (que chunk existe em que pack file)
├── locks\          ← locks pra operações concorrentes
└── snapshots\      ← manifests JSON (que arquivos + chunks + metadata compõem cada snapshot)
```

**Nada em plaintext.** Perdeu a senha → repo é lixo criptográfico irrecuperável. Senha no 1P vault `Databases` item `restic - CAIXA1 backup repo`. Cópia impressa/física fortemente recomendada (fase 2).

### Fluxo de um backup

1. Restic escaneia origem (ex: `restic backup /home/felipe`)
2. Pra cada arquivo:
   - Calcula hashes SHA-256 dos chunks
   - Consulta index: chunk já existe no repo?
   - **Sim** → só referencia (0 bytes gravados)
   - **Não** → encripta chunk (AES-256 CTR) + escreve em pack file + adiciona ao index
3. Cria snapshot manifest: "no dia X, o estado da origem era essa lista de arquivos + esses chunks + esse metadado"
4. Commit atômico do snapshot

Primeira execução: ~100 GB → grava ~90 GB (compressão + dedup interno).
Segunda execução no dia seguinte: ~1-3 GB (só o delta real).

### Fluxo de restore

1. `restic snapshots` — lista todos os snapshots ({id, host, tags, data})
2. Escolhe snapshot (por ID, `latest`, ou filtro `--tag notebook --host caixa1`)
3. Restic lê manifest → sabe exatamente que chunks compõem cada arquivo
4. Descriptografa chunks + remonta arquivos no target
5. Byte-idêntico ao original (verificado por hash)

Modalidades:
- Snapshot inteiro: `restic restore latest --target C:\restore\`
- Arquivo único: `restic restore <id> --include "/path/específico" --target C:\restore\`
- Filesystem mount (read-only): `restic mount M:\` — expõe o repo como FUSE/Dokan, navegável no Explorer

### Retention (retenção)

```powershell
restic forget --keep-daily 30 --keep-weekly 12 --keep-monthly 12 --prune
```

- `forget` — marca snapshots antigos como "não referenciar mais"
- `prune` — reescreve pack files removendo chunks que nenhum snapshot vivo usa
- Retention 30/12/12 = ~54 snapshots vivos simultâneos (com overlap semanal/mensal)

Aplicada 1x/dia pelo wrapper `run-all-backups.ps1` após todos os backups.

### Integridade

- `restic check` — verifica que index + pack files batem (rápido)
- `restic check --read-data` — baixa e re-hasha todos os chunks (garante zero corrupção silenciosa)
- Chunks têm hash SHA-256 embutido → detecta bit-rot do HD automaticamente
- Roda semanal (recomendado; não agendado ainda — follow-up)

### Concurrency

- Múltiplos hosts podem backupar pro mesmo repo simultaneamente
- Cada backup pega lock leve no repo
- No CAIXA1: notebook (Tailscale) + CAIXA1 puxando VPS Dev/Master → todos escrevem em `F:\restic-repo\` sem colisão

### Backends suportados (info)

Hoje: local filesystem (`F:\restic-repo`). Backends alternativos disponíveis sem mudar código:
- SFTP (via SSH)
- S3-compatible (Cloudflare R2, Backblaze B2, MinIO, AWS)
- Azure Blob, Google Cloud Storage
- rclone (qualquer backend rclone — Dropbox, OneDrive, etc)
- REST server dedicado

Adicionar backup off-site é 1 flag: `restic backup --repo b2:bucket/pd-backup ...` — mesma senha, dedup cross-repo se sync.

## Operação diária

### Consultas rápidas

```powershell
# lista snapshots + stats (usa senha do 1P automaticamente)
powershell -File _shared\backup-caixa1\restic-check.ps1
```

Ou manual:

```powershell
$env:RESTIC_PASSWORD = op item get "restic - CAIXA1 backup repo" --vault Databases --fields password --reveal
$env:RESTIC_REPOSITORY = "F:\restic-repo"
C:\Tools\restic\restic.exe snapshots
C:\Tools\restic\restic.exe stats latest
```

### Restore de emergência

Ver `times/infra/context/plano-backup-caixa1.md` §5 pra 6 cenários passo-a-passo:
- §5.0 — Comando setup-free
- §5.1 — Perdi arquivo do notebook
- §5.2 — Supabase apagou tabela
- §5.3 — VPS Master crashou total
- §5.4 — GitHub bloqueou conta
- §5.5 — 1P bloqueou conta
- §5.6 — Restic repo corrompeu (fallback pros dumps crus)

### Validação end-to-end

```powershell
powershell -File _shared\backup-caixa1\validate-restore.ps1
```

Faz backup de 1 pasta + restore em `C:\Temp\restic-test\` + valida contagem + limpa.

## Setup histórico

- Instalado 2026-08-08 (F3, DEV-1730) via download direto do GitHub (`v0.17.3_windows_amd64.exe`) porque `winget install restic` travou em UAC
- Binário em `C:\Tools\restic\restic.exe`, PATH sistema atualizado
- Repo `init` com senha 40-char gerada + salva no 1P (mesma sessão)
- ID do repo: `0d995d09a2`
- Primeiro snapshot validado end-to-end 2026-08-09 (F6): 143 MB, 31 files, restore byte-idêntico

## Diferenças conceituais

| | restic | Syncthing | rsync |
|---|---|---|---|
| Direção | Unidirecional (origem → repo) | Bidirecional | Unidirecional |
| Retém histórico | Sim, N snapshots | Não, só estado atual | Não |
| Dedup | Content-defined chunking global | Não | Não |
| Encriptação | AES-256 obrigatória | TLS transport, arquivo em plaintext | TLS/SSH transport, plaintext no destino |
| Delete no origem | Snapshot antigo ainda tem o arquivo | Delete propaga | Delete propaga (default `--delete`) |
| Uso | "recuperar como estava em dia X" | "manter dois lados iguais" | "cópia rápida" |

**Restic ≠ sync.** Se o objetivo é sincronizar Obsidian vault entre notebook + celular sempre igual, use Syncthing. Restic é backup histórico.

## Dois modos de uso no ecossistema PD

### 1. Restic local (CAIXA1 → `F:\restic-repo`)

Fontes que a CAIXA1 acessa diretamente: notebook via SMB Tailscale, Supabase via `pg_dump` remoto, GitHub via `gh` CLI, Vercel via `vercel env pull`, 1P via `op` CLI. Scripts PowerShell em `_shared/backup-caixa1/*.ps1` rodam agendados no Task Scheduler Windows e escrevem em `F:\restic-repo\` (single repo local).

### 2. Restic remote via rest-server (VPSs → CAIXA1)

**Desde 2026-08-09 (F7+F8).** Restic client roda LOCAL nas VPSs Dev + Master (cron root 03h UTC), pushando delta encriptado pro `rest-server` na CAIXA1 através da rede Tailscale (`100.107.73.81:8000`). Dedup + AES256 acontecem na CPU da VPS (melhor que Celeron do CAIXA1). Cada VPS grava seu próprio repo em `F:\restic-repos-remote\vps-<name>\` — não deduplica entre VPSs, mas deduplica dentro de cada (chunks CDC entre `pg_dump` snapshots por exemplo).

Doc dedicada: [`backup-vps-tailscale.md`](backup-vps-tailscale.md).

## Refs

- README raiz: `_shared/backup-caixa1/README.md`
- Plano canônico: `times/infra/context/plano-backup-caixa1.md`
- Scripts modo 1 (CAIXA1-side): `_shared/backup-caixa1/*.ps1`
- Scripts modo 2 (VPS-side): `_shared/backup-caixa1/vps/*.sh`
- Restic docs oficiais: https://restic.readthedocs.io/
- Issues: F3 DEV-1730 (modo 1), F7 DEV-1735 + F8 DEV-1736 (modo 2)
