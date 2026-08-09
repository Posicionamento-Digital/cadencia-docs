# Cadencia Cloud — arquitetura geral

## O que é

Sistema self-hosted de cloud pessoal + backup automatizado rodando na CAIXA1 (VPS Local do Felipe: PC Bematech Windows 10, Celeron J1800, 8 GB DDR3L dual-channel, 1,4 TB HD, 24×7 no escritório).

**2 usos principais em 1 sistema:**

1. **Backup diário automatizado** de todos os ambientes/serviços PD — snapshot-based deduplicado + encriptado
2. **Cloud pessoal HTTPS** pra compartilhar arquivos/pastas/links com clientes externos

Ambos rodam no mesmo hardware, com storage segregado (HDs distintos por propósito).

## Camadas do sistema

```
┌────────────────────────────────────────────────────────────────────┐
│ CAMADA 1 — Acesso                                                   │
├────────────────────────────────────────────────────────────────────┤
│ Cliente externo    → https://cloud.cadencia.app.br (público HTTPS) │
│ Felipe (interno)   → RDP + SSH + SMB via Tailscale mesh            │
│ Agentes (CI/cron)  → SSH alias vps-local (chave ed25519)           │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│ CAMADA 2 — Roteamento                                               │
├────────────────────────────────────────────────────────────────────┤
│ Cloudflare Tunnel  → tunnel caixa1-cloud (4 conexões QUIC)         │
│                      ↓ 127.0.0.1:8090 → Filebrowser                │
│ Tailscale mesh     → caixa1.taild6079b.ts.net (IPs 100.107.73.81)  │
│                      ↓ SSH/RDP/SMB via Tailscale                   │
│ OpenSSH server     → porta 22 na CAIXA1                            │
│ SMB PDCloud share  → \\caixa1.taild6079b.ts.net\PDCloud            │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│ CAMADA 3 — Aplicação                                                │
├────────────────────────────────────────────────────────────────────┤
│ Filebrowser (nssm)    → serve D:\PD-Cloud via HTTP local           │
│ restic (Task Sched)   → backup diário 03h + semanal domingo 04h    │
│ Scripts orquestração  → C:\Scripts\backup\*.ps1                    │
│ evo_client (notif)    → WhatsApp comercial em falha                │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│ CAMADA 4 — Storage                                                  │
├────────────────────────────────────────────────────────────────────┤
│ C: (111 GB SSD)   → Windows + tools + scripts + clones git         │
│ F: (596 GB HD)    → PD-Backup: restic-repo + dumps + logs          │
│ D: (453 GB HD)    → PD-Cloud: pastas de cliente + templates        │
│ G: (287 GB HD)    → PD-Arquivo: arquivo morto (cold storage)       │
└────────────────────────────────────────────────────────────────────┘
```

## Fontes de dado que o sistema serve/backupa

### Cloud (D: PD-Cloud) — o que aparece pra cliente

```
D:\PD-Cloud\
├── Clientes\<Nome>\
│   ├── Materiais\Recebidos\    ← cliente sobe via share link
│   ├── Materiais\Entregues\    ← Cadencia entrega
│   └── Planilhas\
├── Templates\                   ← modelos reutilizáveis
├── Public\                      ← share rápido single-file
└── Recebidos\                   ← upload ad-hoc sem cliente identificado
```

**12 clientes migrados 2026-08-09** (do OneDrive `Customer Success\`): Angélica Zolddan Passos, Ariane Farrapo, Atelier Sweet Angels, Dra. Nathalia Galardo, Iasmin Lopes Pinto, MasterBoard, Melissa Quevedo, OP Odontopenha, Padaria Milionaria, Juliana Pereira, Leonardo Alves da Silva, Vayne Saccaro.

### Backup (F: PD-Backup) — o que o restic cobre

| Fonte | Método | Frequência |
|---|---|---|
| VPS Dev (fs + Lara Postgres + EasyApp MySQL + crons) | SSH tar + docker exec pg_dump/mysqldump + restic | diário 03h |
| VPS Master (Coolify dump + apps + fs + crons) | idem + Coolify metadata dump | diário 03h |
| Supabase (Cadencia + HubPD) | pg_dump via connection string 1P | diário 03h |
| Vercel envs | vercel env pull + GPG encrypt | diário 03h |
| GitHub repos privados | gh + git clone --mirror | diário 03h |
| 1Password | snapshot metadata (op vault list + item list) | diário 03h |
| Notebook (pd-framework + Obsidian + .claude + OneDrive) | restic via SMB Tailscale | diário 03h |
| Linear + Cloudflare + Resend | API GraphQL/REST → JSON gzip | semanal domingo 04h |

Retention: 30 diários + 12 semanais + 12 mensais (~54 snapshots vivos simultâneos).

### Não-cobertos (fora de escopo)

- LLM local (Celeron sem GPU/AES-NI)
- Containers Docker pesados
- Compilação Rust/Go grande
- Elasticsearch/Kafka
- Vídeo transcoding sem hw accel

## Fluxo end-to-end — 3 cenários

### Cenário 1: cliente recebe material entregável

1. Cadencia grava PDF em `D:\PD-Cloud\Clientes\<Nome>\Materiais\Entregues\Contratos\` (via RDP ou SMB ou upload pelo Filebrowser)
2. Felipe abre `https://cloud.cadencia.app.br` → login → navega até arquivo → botão Share
3. Configura expiração (ex: 7 dias) + senha opcional
4. Copia URL `https://cloud.cadencia.app.br/share/<hash>`
5. Envia pelo WhatsApp/email pro cliente
6. Cliente clica no link (sem conta) → baixa

### Cenário 2: cliente sobe material recebido

1. Felipe cria share link COM permissão upload apontando pra `D:\PD-Cloud\Clientes\<Nome>\Materiais\Recebidos\`
2. Envia URL pro cliente
3. Cliente clica → vê UI upload → drag-and-drop múltiplos arquivos
4. Arquivos aparecem direto na pasta CAIXA1
5. Próximo backup restic captura tudo (dedup automático se cliente subir mesmo arquivo 2x)

### Cenário 3: restore de emergência (perdeu arquivo)

1. `ssh vps-local` OU RDP CAIXA1
2. Setup env restic:
   ```powershell
   $env:RESTIC_PASSWORD = op item get "restic - CAIXA1 backup repo" --vault Databases --fields password --reveal
   $env:RESTIC_REPOSITORY = "F:\restic-repo"
   ```
3. `restic snapshots` — encontra snapshot do dia desejado
4. `restic restore <id> --target C:\restore\ --include "/path/específico"`
5. Arquivo restaurado byte-idêntico

## Componentes (docs dedicadas)

- [`restic.md`](restic.md) — motor de backup (CDC, retention, restore)
- [`filebrowser.md`](filebrowser.md) — UI web da cloud (upload, share links, users)
- [`cloudflared-tunnel.md`](cloudflared-tunnel.md) — túnel HTTPS (2 tokens API, QUIC, ingress)
- [`migracao-onedrive-cadencia-cloud.md`](migracao-onedrive-cadencia-cloud.md) — processo replicável de migração

## Decisões arquiteturais principais

**Por que single host (não distribuído):**
- Escopo é backup pessoal + cloud pra clientes do Felipe, não infra multi-tenant escalável
- 1 lugar pra debugar, 1 senha 1P, 1 crontab, 1 log central
- CAIXA1 é hardware existente ocioso — R$0/mês incremental

**Por que Filebrowser (não Nextcloud):**
- Nextcloud pede 500+ MB RAM, roda mal no Celeron J1800
- Escopo é "compartilhar com cliente via link", não sync desktop nem colab docs
- Filebrowser: 20 MB RAM, share link nativo, single binary Go

**Por que Cloudflare Tunnel (não expor porta):**
- Zero abertura de firewall no roteador do escritório
- TLS gerenciado pela edge CF (sem Let's Encrypt local)
- DDoS protection incluso
- Funciona atrás de CGNAT do provedor
- Grátis

**Por que restic (não Borg/Duplicati/Nextcloud backup):**
- Snapshot-based com CDC + AES-256 + retention nativa em single binary
- Backend-agnostic (fácil adicionar off-site R2/B2 no futuro)
- Padrão da indústria (Backblaze, Cloudflare internos)
- Roda nativo Windows sem toolchain

**Por que pull-model do CAIXA1 (não push das VPSs):**
- Todos os scripts rodam no CAIXA1 puxando via SSH
- 1 lugar pra debugar, 1 lugar com senha 1P, 1 Task Scheduler
- Se CAIXA1 desligar: backup para até religar (mitigável com deadman 48h)

**Por que 2 tokens Cloudflare separados:**
- Princípio do menor privilégio
- Token do serviço 24/7 (tunnel) tem escopo Account.Tunnel apenas — se vazar, blast radius limitado
- Token DNS separado, usado só em provisioning

**Por que Cadencia Cloud é fonte única (não OneDrive + Cloud):**
- Migração DEV-1726 unificou depois de operar OneDrive por 39 dias (DEV-1043)
- OneDrive Files On-Demand deixava placeholders → backup incompleto
- Share link OneDrive é ruim pro cliente externo
- Uma pasta = uma URL = uma regra pra agentes

## Custos

| Item | Custo/mês |
|---|---|
| Hardware CAIXA1 (Bematech + 3 HDs) | R$0 (existente) |
| Energia (24×7, ~15W médio) | ~R$5 |
| Tailscale (Free tier — 3 usuários, 100 devices) | R$0 |
| Cloudflare (Free tier — Tunnel + DNS + Universal SSL + DDoS) | R$0 |
| **Total incremental** | **~R$5/mês** |

Comparação:
- OneDrive 1 TB pessoal: R$29,90/mês
- Google One 2 TB: R$45,00/mês
- Dropbox 2 TB: R$77,00/mês
- Cloudflare R2 (1 TB): ~R$80/mês (só storage, sem UI)

## Segurança

**Superfície pública:**
- `https://cloud.cadencia.app.br` — Filebrowser atrás de login (user `felipe`)
- Share links geram URL única com hash aleatório + senha opcional + expiração

**Superfície privada (Tailscale mesh, só devices pareados do Felipe):**
- SSH porta 22 (chave ed25519)
- RDP porta 3389 (senha do 1P)
- SMB share `PDCloud` (senha do usuário Windows)

**Não exposto publicamente:**
- `F:\PD-Backup\restic-repo\` (senha do 1P, só acessível na CAIXA1)
- `G:\PD-Arquivo\`

**Encriptação:**
- Repo restic: AES-256 CTR (senha 40-char no 1P)
- Vercel envs backupados: GPG (chave dedicada + senha 1P)
- Transport: HTTPS (CF edge), SSH (chaves ed25519), Tailscale WireGuard

## Monitoramento e falhas

- Log local: `F:\Logs\backup\run-<data>.log` (rotação 30 dias)
- Notif WhatsApp em falha via `evo_client.py --comercial` — silêncio = sucesso
- Digest semanal (planejado, não implementado): resumo dos 7 dias
- Deadman (planejado): alerta se nenhum backup rodar por 48h

## Follow-ups conhecidos

- Rotacionar 3 tokens Cloudflare vazados no debug F5
- Validar restore end-to-end de DB Supabase + Docker volume (após primeiro run automático)
- Observar 7 dias consecutivos limpos antes de considerar regime estável
- Adicionar backup off-site (R2 ou B2) — fase 2 opcional
- Deadman 48h + digest semanal — fase 2

## Refs

- Plano canônico completo: `times/infra/context/plano-backup-caixa1.md`
- Inventário fonte VPS Dev+Master: `times/infra/context/inventario-vps-2026-08.md`
- Scripts + deploy: `_shared/backup-caixa1/README.md`
- Doc Obsidian: `Obsidian_Vaults_Pessoal/Infra/2026-08-08 VPS Local CAIXA1 (Windows).md`
- Matriz storage: `_core/CAIXA1-STORAGE-MAP.md`
- Política arquivos cliente: `_core/CLIENT-FILES-POLICY.md`
- Skills: `/vps-local`, `/vps-local-acesso-remoto`
- Projeto Linear: [Infra — Backup + Cloud CAIXA1](https://linear.app/cadencia/project/infra-backup-cloud-caixa1-6ccf2c5c9ac7)
- Issue-mãe: DEV-1726
