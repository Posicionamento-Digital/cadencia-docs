# Filebrowser — UI web da Cadencia Cloud

## O que é

Cliente web pra navegar/upload/download/compartilhar arquivos de uma pasta local, expondo tudo por HTTP. Single binary Go (~17 MB), roda nativo Windows. Zero dependência.

No CAIXA1: expõe `D:\PD-Cloud\` (o HD PD-Cloud, 453 GB) via `http://127.0.0.1:8090`. Fica atrás do Cloudflare Tunnel pra virar `https://cloud.cadencia.app.br` público.

## Arquitetura

```
Cliente externo (browser)
     │
     ▼ HTTPS (443)
Cloudflare Edge (Universal SSL cert)
     │
     ▼ QUIC (4 conexões ativas: gru02/07/11/18)
cloudflared.exe (serviço Windows CloudflaredTunnel)
     │
     ▼ HTTP local (127.0.0.1:8090)
filebrowser.exe (serviço Windows Filebrowser)
     │
     ▼ filesystem
D:\PD-Cloud\
├── Clientes\<Nome>\Materiais\{Recebidos,Entregues}\
├── Public\
├── Templates\
└── Recebidos\
```

## Config atual

| Campo | Valor |
|---|---|
| Binário | `C:\Tools\filebrowser\filebrowser.exe` (v2.32.0) |
| DB (SQLite) | `C:\Tools\filebrowser\config\filebrowser.db` |
| Root filesystem | `D:\PD-Cloud` |
| Bind | `127.0.0.1:8090` (só localhost — CF Tunnel faz o proxy externo) |
| Auth method | JSON (user+password no DB) |
| Branding | "Cadencia Cloud" |
| Serviço Windows | `Filebrowser` (nssm, start automatic) |
| Logs | `C:\Tools\filebrowser\config\{stdout,stderr}.log` |
| Admin user | `felipe` (senha 1P vault `Databases` item `Filebrowser CAIXA1 admin`) |

## Features usadas

- **Navegação** — tree view + breadcrumb
- **Upload** — drag-and-drop múltiplos arquivos/pastas, upload resumível
- **Download** — arquivo único ou zip de pasta
- **Preview embutido** — imagens (JPG/PNG/WebP), vídeos (MP4/WebM), áudios (MP3/WAV), PDFs, código com syntax highlight, markdown renderizado, arquivos de texto
- **Share links** — gera URL única com senha opcional + expiração opcional; cliente não precisa de conta, abre no browser e baixa (ou sobe, se permissão de upload)
- **Editor embutido** — abre `.md`, `.txt`, `.json`, código em geral direto no browser pra editar
- **Users + permissions** — RBAC simples (admin, read-only, path-scoped)
- **API HTTP** — endpoints JSON pra automação (não usado ativamente)

## Operação

### Login

1. Abrir `https://cloud.cadencia.app.br`
2. User `felipe`, senha do 1P (`Filebrowser CAIXA1 admin`)

### Adicionar arquivo

**Via browser (mais fácil):**
- Login → navegar até pasta → drag-and-drop OU botão `+ New` → Upload

**Direto na CAIXA1 (útil pra volumes grandes):**
- RDP na CAIXA1 (`/vps-local-acesso-remoto`) → copiar em `D:\PD-Cloud\<pasta>\`
- SMB via Tailscale: `\\caixa1.taild6079b.ts.net\PDCloud\<pasta>\`
- SSH: `scp arquivo vps-local:D:/PD-Cloud/<pasta>/`

Filebrowser detecta automaticamente ao próximo acesso do browser (sem rescan).

### Gerar share link pra cliente

1. Selecionar arquivo/pasta na UI
2. Botão **Share** (ícone de link)
3. Configurar:
   - **Expira em:** horas/dias (padrão sugerido: 7 dias pra material entregue)
   - **Senha:** opcional; recomendado pra cliente externo (compartilhar senha por canal separado — WhatsApp/email)
4. Copiar URL gerada: `https://cloud.cadencia.app.br/share/<hash>`
5. Enviar pelo canal de contato

Cliente clica no link → vê listagem se pasta OU baixa direto se arquivo. Sem conta.

### Criar user extra pro cliente (opcional)

Se quiser cliente com conta permanente + scope de pasta específica:

```powershell
& C:\Tools\filebrowser\filebrowser.exe users add cliente-x <senha> --scope /Clientes/Nome/Materiais --database C:\Tools\filebrowser\config\filebrowser.db
```

Usar quando: cliente sobe muito material frequentemente (share link com upload permission funciona mas menos elegante que login próprio).

## Setup histórico

- Instalado 2026-08-09 (F5, DEV-1732) via download direto do GitHub (`v2.32.0/windows-amd64-filebrowser.zip`)
- Config inicial: `filebrowser config init` + `filebrowser config set` com bind, root, branding
- Admin `felipe` criado com senha gerada 1P
- Serviço Windows registrado via nssm (não iniciava sozinho no reboot como Task Scheduler)
- Script de install idempotente: `_shared/backup-caixa1/install-filebrowser.ps1` (roda 1x, atualiza se já existir)

## Backup do Filebrowser

O próprio `D:\PD-Cloud\` é backupado diariamente pelo restic (F:\restic-repo). Config (`C:\Tools\filebrowser\config\filebrowser.db`) também está no path de backup filesystem (via `backup-notebook.ps1` — ou vai virar backup específico se ganhar volume).

Se filebrowser.db corromper, admin user recriado via `install-filebrowser.ps1` (idempotente). Share links antigos perdem — clientes recebem novo link.

## Gotchas conhecidos

- **Universal SSL leva 5-15 min** pra propagar cert em subdomínio novo Cloudflare — teste HTTPS logo após criar tunnel pode dar TLS handshake failed. Aguarda + testa de novo.
- **PowerShell 5.1 default usa TLS antigo** — teste com `Invoke-WebRequest` pode falhar mesmo quando `curl` funciona. Não é bug do Filebrowser, é do cliente PS.
- **Serviço Windows via nssm** — usar `Get-Service Filebrowser; Start-Service Filebrowser` pra controle. `nssm start/stop/remove Filebrowser` pra gerenciar registro.
- **Não expor 127.0.0.1:8090 direto** — sem TLS + sem auth strong; sempre atrás do Cloudflare Tunnel.

## Refs

- Docs oficiais: https://filebrowser.org/
- Script install: `_shared/backup-caixa1/install-filebrowser.ps1`
- Cloudflare Tunnel setup: `_shared/backup-caixa1/docs/cloudflared-tunnel.md`
- Issue F5: DEV-1732
