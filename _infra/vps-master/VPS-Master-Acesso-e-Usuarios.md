---
date: 2026-05-22
tags: [infra, vps, acesso, ssh]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]"]
---
# VPS Master — Acesso e Usuários

---

## Usuários do sistema

| Usuário | UID | Shell | Sudo | Grupos | Propósito |
|---|---|---|---|---|---|
| `master` | 1002 | `/bin/bash` | Sim (NOPASSWD) | master, sudo, users, docker | Felipe — único acesso operacional |
| `root` | 0 | `/bin/bash` | — | — | Inacessível via SSH. Acesso só via `sudo su` a partir do master |
| `ubuntu` | 1000 | `/usr/sbin/nologin` | Sim (bloqueado) | ubuntu | User padrão Hostinger — bloqueado, não usar |

### Por que root está inacessível

Root bloqueado via duas camadas:
1. `PermitRootLogin no` no sshd_config
2. `passwd -l root` — senha bloqueada

Para acessar root quando necessário: `sudo su` dentro de uma sessão master.

---

## Como conectar via SSH

### Conexão padrão (Felipe)

```bash
ssh -i ~/.ssh/hostinger_prod_master master@72.60.4.71
```

### Com SSH config (mais prático)

Adicionar em `~/.ssh/config`:

```
Host vps-master
  HostName 72.60.4.71
  User master
  IdentityFile ~/.ssh/hostinger_prod_master
  IdentityAgent none
  IdentitiesOnly yes
```

Depois: `ssh vps-master`

### Chaves SSH

| Arquivo | Vault 1Password | Item |
|---|---|---|
| `~/.ssh/hostinger_prod_master` | Hosts | Hostinger VPS Master - master (SSH Key) |

> As chaves nunca ficam em texto claro em documentos. Sempre buscar no 1Password.

---

## Configuração SSH do servidor

Arquivo: `/etc/ssh/sshd_config`

```
PermitRootLogin no
PasswordAuthentication no
AllowUsers master
PubkeyAuthentication yes
```

---

## 1Password CLI na VPS

O `op` CLI está instalado para o user `master`. Autenticação via Service Account token configurado no `~/.profile`:

```bash
export OP_SERVICE_ACCOUNT_TOKEN="..."  # carregado automaticamente no login
```

O SA token está salvo no 1Password vault **Hosts** → item **Hostinger VPS - Acessos & Credenciais**.

> Nunca copiar o valor do SA token em texto claro. O `.profile` não é commitado em nenhum repo.

Para verificar que o op está autenticado:

```bash
bash -l -c 'op user get --me'
```

---

## CLIs instalados para o user master

| CLI | Versão | Como usar |
|---|---|---|
| `op` | 2.34.0 | 1Password — fonte de credenciais |
| `gh` | 2.92.0 | GitHub CLI |
| `docker` | 29.x | Containers (master está no grupo docker) |
| `git` | sistema | Versionamento |
| `uv` | 0.11.16 | Python — rodar scripts sem venv manual |
| `node` | 24.16.0 | Via nvm (`~/.nvm/`) |
| `npm` | 11.x | Via nvm |
| `htop` | 3.3.0 | Monitor de processos |
| `tmux` | 3.4 | Sessões persistentes |
| `jq` | 1.7 | Parse JSON no terminal |
| `curl` | 8.5.0 | Requisições HTTP |
| `rsync` | 3.2.7 | Transferência de arquivos |
| `ncdu` | 1.19 | Visualizar uso de disco |

### Carregar nvm em sessão

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
```

Ou simplesmente fazer login shell: `bash -l`

---

## Claude Code na VPS

O Claude Code está instalado para o user `master` via nvm. Configurado com guardrails duros:

- `defaultMode: plan` — sempre pede confirmação antes de executar
- Sem permissão de delete
- **NUNCA é acionado por cron** — só uso manual para manutenção

Para acessar: `ssh vps-master` → `claude`

---

## Acesso aos painéis (via SSH tunnel)

Os painéis de monitoramento **não ficam expostos na internet**. Acesso apenas via SSH tunnel:

### Cockpit (gerenciamento do servidor)

```bash
ssh -L 9090:localhost:9090 vps-master
# Abrir: http://localhost:9090
```

### Netdata (métricas em tempo real)

```bash
ssh -L 19999:localhost:19999 vps-master
# Abrir: http://localhost:19999
```

### Coolify (deploy automático)

Coolify tem domínio próprio e fica acessível via browser diretamente:

- URL: `https://coolify.cadencia.ia.br`
- Credenciais: Felipe sabe o login. API token no 1P → vault Hosts → **Coolify - API - VPS Master**

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Arquitetura]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Seguranca]]
