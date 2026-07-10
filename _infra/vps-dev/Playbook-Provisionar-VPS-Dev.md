---
date: 2026-05-22
tags: [infra, vps, playbook, provisioning, onboarding]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]", "[[ecuro-mcp]]", "[[pd-portal]]"]
---
# Playbook — Provisionar VPS de Desenvolvimento do Zero

> Guia completo para recriar a VPS de desenvolvimento (Hostinger KVM1, Ubuntu 24.04) com dois usuários, CLIs, Docker, 1Password, Claude Code, repos e MCPs. Referência de execução real: sessão 2026-05-21, VPS `2.24.117.172`.

**Tempo estimado:** 3–4h manual · 1–1.5h com Claude Code  
**Pré-requisito:** conta Hostinger, 1Password com vault `Hosts`, GitHub org com acesso

---

## Índice

1. [[#Etapa 1 — Contratar e acessar a VPS]]
2. [[#Etapa 2 — Atualizar o sistema e instalar ferramentas base]]
3. [[#Etapa 3 — Criar usuários e chaves SSH]]
4. [[#Etapa 4 — Hardening SSH]]
5. [[#Etapa 5 — Firewall (UFW)]]
6. [[#Etapa 6 — Instalar Docker]]
7. [[#Etapa 7 — Instalar Node.js (system-wide)]]
8. [[#Etapa 8 — Instalar Python, pip e uv]]
9. [[#Etapa 9 — Instalar GitHub CLI (gh)]]
10. [[#Etapa 10 — Instalar 1Password CLI (op)]]
11. [[#Etapa 11 — Instalar CLIs por usuário (nvm)]]
12. [[#Etapa 12 — Configurar Service Account 1Password]]
13. [[#Etapa 13 — Configurar variáveis de ambiente (.profile)]]
14. [[#Etapa 14 — Instalar MCPs]]
15. [[#Etapa 15 — Instalar skills do Claude Code]]
16. [[#Etapa 16 — Clonar repositórios]]
17. [[#Etapa 17 — Validação end-to-end]]

---

## Etapa 1 — Contratar e acessar a VPS

### Manual

1. Acessar [hpanel.hostinger.com](https://hpanel.hostinger.com)
2. Contratar plano **KVM1** (1 vCPU · 4GB RAM · 50GB SSD) — plano mínimo funcional para dev
3. Escolher imagem: **Ubuntu 24.04 LTS**
4. Ao finalizar, copiar o IP público e a senha root gerada
5. Salvar senha root no 1Password: vault `Hosts`, item `Hostinger VPS - Developer - rootpassword`
6. Testar acesso:
   ```bash
   ssh root@<IP>
   # aceitar fingerprint e entrar com senha root
   ```

> [!tip] Com Claude Code
> Peça: *"Acabei de contratar uma VPS Hostinger KVM1 Ubuntu 24.04, IP `X.X.X.X`. Salva a senha root `<senha>` no 1Password vault Hosts como `Hostinger VPS - Developer - rootpassword` e conecta via SSH pra confirmar que o acesso funciona."*
> Claude usa `op` CLI para salvar e `ssh` para validar o acesso.

---

## Etapa 2 — Atualizar o sistema e instalar ferramentas base

### Manual

```bash
apt update && apt upgrade -y
apt install -y git curl wget htop tmux jq unzip
```

> [!tip] Com Claude Code
> Peça: *"Na VPS `root@<IP>`, atualiza o sistema e instala as ferramentas base: git, curl, wget, htop, tmux, jq, unzip."*

---

## Etapa 3 — Criar usuários e chaves SSH

### Manual

#### Criar usuários

```bash
# Criar usuario felipe (com sudo)
adduser felipe --disabled-password --gecos ""
usermod -aG sudo,docker,users felipe
echo "felipe ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/felipe

# Criar usuario colaborador (sem sudo)
adduser luiz --disabled-password --gecos ""
usermod -aG docker,users luiz
```

#### Gerar chaves SSH ed25519 (na máquina LOCAL do Felipe)

```bash
# Chave pra felipe
ssh-keygen -t ed25519 -f ~/.ssh/hostinger_dev_felipe -C "felipe@vps-dev" -N ""

# Chave pra colaborador
ssh-keygen -t ed25519 -f ~/.ssh/hostinger_dev_luiz -C "luiz@vps-dev" -N ""
```

#### Instalar chaves públicas na VPS

```bash
# Na VPS (como root):
mkdir -p /home/felipe/.ssh && chmod 700 /home/felipe/.ssh
echo "<chave-publica-felipe>" > /home/felipe/.ssh/authorized_keys
chmod 600 /home/felipe/.ssh/authorized_keys
chown -R felipe:felipe /home/felipe/.ssh

mkdir -p /home/luiz/.ssh && chmod 700 /home/luiz/.ssh
echo "<chave-publica-luiz>" > /home/luiz/.ssh/authorized_keys
chmod 600 /home/luiz/.ssh/authorized_keys
chown -R luiz:luiz /home/luiz/.ssh
```

#### Salvar chaves privadas no 1Password

Salvar cada chave privada no vault `Hosts`:
- `Hostinger VPS Dev - felipe (SSH Key)` — campo `chave privada`
- `Hostinger VPS Dev - luiz (SSH Key)` — campo `chave privada`

> [!tip] Com Claude Code
> Peça: *"Na VPS `root@<IP>`: cria os usuários `felipe` (com sudo NOPASSWD) e `luiz` (sem sudo, grupo docker). Gera chaves SSH ed25519 para cada um, instala as chaves públicas nos respectivos `.ssh/authorized_keys` e salva as chaves privadas no 1Password vault `Hosts` como `Hostinger VPS Dev - felipe (SSH Key)` e `Hostinger VPS Dev - luiz (SSH Key)`."*
> Claude gera tudo, conecta via SSH para validar cada usuário e salva no 1P sem expor os valores.

---

## Etapa 4 — Hardening SSH

### Manual

Editar `/etc/ssh/sshd_config`:

```bash
nano /etc/ssh/sshd_config
```

Garantir (ou adicionar) estas linhas:

```
PasswordAuthentication no
PermitRootLogin no
AllowUsers felipe luiz
```

Reiniciar SSH (sem fechar a sessão atual):

```bash
systemctl restart sshd
```

**Teste obrigatório antes de fechar a sessão root:** abrir novo terminal e conectar como `felipe` com a chave SSH. Só fechar a sessão root após confirmar que funciona.

> [!warning] Atenção
> Se fechar a sessão root sem testar, e o hardening estiver errado, você perde o acesso. Sempre teste em janela paralela.

> [!tip] Com Claude Code
> Peça: *"Na VPS, aplica hardening no SSH: desativa autenticação por senha, bloqueia login root direto e restringe `AllowUsers` para `felipe luiz`. Reinicia o sshd e valida que consigo conectar como `felipe` antes de confirmar."*
> Claude edita o arquivo, reinicia e abre uma conexão de teste antes de reportar concluído.

---

## Etapa 5 — Firewall (UFW)

### Manual

```bash
ufw allow 22/tcp
ufw --force enable
ufw status
```

Outras portas são abertas conforme necessidade (webhooks, HTTP, HTTPS):

```bash
ufw allow 80/tcp
ufw allow 443/tcp
# Porta específica para webhook:
ufw allow <porta>/tcp
```

> [!tip] Com Claude Code
> Peça: *"Configura o UFW na VPS: abre porta 22 (SSH) e ativa o firewall. Outras portas só abre se eu pedir explicitamente."*

---

## Etapa 6 — Instalar Docker

### Manual

```bash
curl -fsSL https://get.docker.com | sh

# Adicionar usuarios ao grupo docker (se ainda nao foi feito na Etapa 3)
usermod -aG docker felipe
usermod -aG docker luiz

# Verificar
docker --version
docker compose version
```

> [!tip] Com Claude Code
> Peça: *"Instala o Docker Engine na VPS usando o script oficial (get.docker.com). Garante que os usuários `felipe` e `luiz` estão no grupo docker. Valida com `docker ps`."*

---

## Etapa 7 — Instalar Node.js (system-wide)

Instalar via NodeSource para ficar disponível a todos os usuários.

### Manual

```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
apt install -y nodejs
node --version   # deve ser v24.x
npm --version
```

> [!tip] Com Claude Code
> Peça: *"Instala Node.js 24 LTS na VPS via NodeSource (system-wide, disponível para todos os usuários). Valida com `node --version`."*

---

## Etapa 8 — Instalar Python, pip e uv

### Manual

```bash
apt install -y python3 python3-pip

# uv (gerenciador moderno de pacotes Python)
curl -LsSf https://astral.sh/uv/install.sh | sh
cp ~/.cargo/bin/uv /usr/local/bin/uv   # disponível para todos

uv --version
python3 --version
```

> [!tip] Com Claude Code
> Peça: *"Instala Python3, pip e uv na VPS. O uv deve estar disponível para todos os usuários em `/usr/local/bin`."*

---

## Etapa 9 — Instalar GitHub CLI (gh)

### Manual

```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  | tee /etc/apt/sources.list.d/github-cli.list
apt update && apt install -y gh
gh --version
```

> [!tip] Com Claude Code
> Peça: *"Instala o GitHub CLI (`gh`) na VPS via repositório oficial. Valida com `gh --version`."*

---

## Etapa 10 — Instalar 1Password CLI (op)

### Manual

```bash
curl -sS https://downloads.1password.com/linux/keys/1password.asc \
  | gpg --dearmor \
  | tee /usr/share/keyrings/1password-archive-keyring.gpg > /dev/null
echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/amd64 stable main' \
  | tee /etc/apt/sources.list.d/1password.list
apt update && apt install -y 1password-cli
op --version
```

> [!tip] Com Claude Code
> Peça: *"Instala o 1Password CLI (`op`) na VPS via repositório oficial. Valida com `op --version`."*

---

## Etapa 11 — Instalar CLIs por usuário (nvm)

Cada usuário instala no próprio home via nvm. Repetir para `felipe` e `luiz`.

### Manual (executar como cada usuário)

```bash
# Conectar como o usuario
ssh -i ~/.ssh/hostinger_dev_felipe felipe@<IP>

# Instalar nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.profile   # ou ~/.bashrc

# Instalar CLIs npm
nvm install --lts
npm install -g @anthropic-ai/claude-code   # Claude Code
npm install -g @openai/codex               # Codex CLI
npm install -g @google/gemini-cli          # Gemini CLI
npm install -g railway                     # Railway CLI
npm install -g vercel                      # Vercel CLI

# Verificar
claude --version
codex --version
gemini --version
railway --version
vercel --version
```

Repetir via `ssh ... luiz@<IP>`.

> [!tip] Com Claude Code
> Peça: *"Na VPS, instala via nvm para os usuários `felipe` e `luiz` (um de cada vez): Claude Code, Codex CLI, Gemini CLI, Railway CLI e Vercel CLI. Valida cada CLI após instalar."*
> Claude conecta como cada usuário via SSH e roda os comandos de instalação e validação.

---

## Etapa 12 — Configurar Service Account 1Password

O colaborador (Luiz) usa um Service Account read-only para acessar credenciais sem precisar de biometria ou senha.

### Manual

1. Acessar [1password.com/developer](https://1password.com/developer) → Service Accounts
2. Criar SA com nome ex: `Hostinger VPS - Acessos & Credenciais`
3. Escopo: vault `Hostinger VPS` (read-only)
4. Copiar o token gerado (`ops_...`)
5. Salvar o token no 1Password (vault `Hosts`, item `Hostinger VPS - SA - luiz`)
6. No `.profile` do Luiz na VPS (ver Etapa 13), adicionar:
   ```bash
   export OP_SERVICE_ACCOUNT_TOKEN="ops_..."
   ```

> [!tip] Com Claude Code
> Peça: *"No 1Password, cria um Service Account read-only chamado `Hostinger VPS - Acessos & Credenciais` com acesso ao vault `Hostinger VPS`. Salva o token no vault `Hosts` como `Hostinger VPS - SA - luiz`. Depois adiciona o token no `.profile` do usuário `luiz` na VPS."*
> Claude acessa o painel via API se disponível, ou guia passo a passo no browser com você.

---

## Etapa 13 — Configurar variáveis de ambiente (.profile)

### Manual

Editar `~/.profile` de cada usuário na VPS:

**felipe:**
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

export VERCEL_TOKEN="<token>"
export SUPABASE_ACCESS_TOKEN="<pat>"
export GH_TOKEN="<classic-pat>"
```

**luiz:**
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

export OP_SERVICE_ACCOUNT_TOKEN="<sa-token>"
export VERCEL_TOKEN="<token>"
export SUPABASE_ACCESS_TOKEN="<pat>"
export GH_TOKEN="<classic-pat>"
```

Pegar tokens do 1Password:
- `GH_TOKEN`: item `Github - VPS Dev - org access`, vault `Hosts`
- `VERCEL_TOKEN`: item `Vercel - api - cli`, vault `Hosts`
- `SUPABASE_ACCESS_TOKEN`: item `Supabase - ClaudeCode - CLI`, vault `Databases`
- `OP_SERVICE_ACCOUNT_TOKEN`: item do SA criado na Etapa 12

> [!warning] Nunca committar o `.profile`
> Os tokens ficam só na VPS. Nunca entram em nenhum repositório.

> [!tip] Com Claude Code
> Peça: *"Pega os tokens de VERCEL_TOKEN, SUPABASE_ACCESS_TOKEN, GH_TOKEN e OP_SERVICE_ACCOUNT_TOKEN no 1Password (vaults Hosts e Databases) e escreve o `.profile` de `felipe` e `luiz` na VPS com as variáveis corretas. Não exibe os valores no chat."*
> Claude usa `op item get` para buscar cada token e escreve diretamente no arquivo via SSH sem exibir os valores.

---

## Etapa 14 — Instalar MCPs

Os MCPs são configurados em `~/.claude/settings.json` de cada usuário.

### Manual

Conectar como cada usuário e criar/editar `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "linear": {
      "type": "http",
      "url": "https://mcp.linear.app/sse",
      "headers": {
        "Authorization": "Bearer <linear-api-key>"
      }
    },
    "hostinger-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@hostinger/mcp-server"],
      "env": {
        "HOSTINGER_API_KEY": "<hostinger-api-key>"
      }
    },
    "posthog": {
      "type": "http",
      "url": "https://app.posthog.com/mcp"
    }
  }
}
```

Pegar tokens: Linear API em `Serviços & Tools` vault, Hostinger API em `Hosts` vault.

> [!tip] Com Claude Code
> Peça: *"Configura os MCPs `linear`, `hostinger-mcp` e `posthog` no `~/.claude/settings.json` dos usuários `felipe` e `luiz` na VPS. Pega as API keys do 1Password (Linear API em vault `Serviços & Tools`, Hostinger API em vault `Hosts`)."*

---

## Etapa 15 — Instalar skills do Claude Code

As skills ficam em `~/.claude/skills/` de cada usuário. A fonte é o repositório `claude-dev-skills`.

### Manual

```bash
# Como cada usuario na VPS:
mkdir -p ~/.claude/skills

# Clonar repositorio de skills compartilhadas
cd ~/
git clone git@github.com:Posicionamento-Digital/claude-dev-skills.git

# Copiar skills para o diretório do Claude Code
cp -r ~/claude-dev-skills/skills/* ~/.claude/skills/
```

**Skills para Luiz (20):**
`log-sessao`, `linear-start-issue`, `linear-close-issue`, `linear-planejar-issue`, `linear-atualizar-issue`, `linear-criar-issue`, `linear-gestao-atividades`, `gemini-review`, `claude-review`, `codex-review`, `debug-polya`, `runtime-fix-review`, `espelhar-repo-vps`, `registrar-incidente`, `credencial`, `validar-deploy-vps`, `status`, `ja-fiz`, `issue-semana`, `handoff-sessao`

**Skills para Felipe (46):**
Cópia completa das skills locais (incluindo as 20 acima + gestão pessoal, Linear avançado, infra, Obsidian, WhatsApp).

> [!tip] Com Claude Code
> Peça: *"Na VPS, instala as skills do Claude Code para `luiz` (20 skills) e `felipe` (46 skills) copiando do repositório `claude-dev-skills` da org Posicionamento-Digital. Lista as skills instaladas para confirmar."*

---

## Etapa 16 — Clonar repositórios

### Manual

```bash
# Conectar como luiz
ssh -i ~/.ssh/hostinger_dev_luiz luiz@<IP>

# Clonar repos com a chave GitHub configurada
cd ~
git clone git@github.com:Posicionamento-Digital/gci-go-whatsapp.git
git clone git@github.com:felipeluissalgueiro/cadencia-app.git
git clone git@github.com:Posicionamento-Digital/pd-portal.git
git clone git@github.com:Posicionamento-Digital/ecuro-mcp.git
git clone git@github.com:Posicionamento-Digital/claude-dev-skills.git
```

Para que o `git clone` via SSH funcione, a chave pública do usuário na VPS precisa estar cadastrada no GitHub da conta correspondente (`luizsidiao` para Luiz, `felipeluissalgueiro` para Felipe).

> [!tip] Com Claude Code
> Peça: *"Na VPS como usuário `luiz`, clona os repos: `gci-go-whatsapp`, `cadencia-app`, `pd-portal`, `ecuro-mcp` e `claude-dev-skills`. Usa a chave SSH do usuário. Valida que cada repo foi clonado com `git log --oneline -1` em cada um."*

---

## Etapa 17 — Validação end-to-end

### Checklist manual

Conectar como cada usuário e verificar:

```bash
# CLIs básicos
git --version && docker ps && node --version && python3 --version

# CLIs por usuario (requerem nvm)
source ~/.profile
claude --version
codex --version
gemini --version
railway --version
vercel --version

# 1Password
op whoami   # deve retornar o SA ou conta autenticada

# MCPs
cat ~/.claude/settings.json   # confirmar estrutura

# Repos (Luiz)
ls ~/gci-go-whatsapp ~/cadencia-app ~/pd-portal

# Skills
ls ~/.claude/skills/ | wc -l   # 20 para Luiz, 46 para Felipe

# Firewall
ufw status   # porta 22 ALLOW, demais DENY
```

> [!tip] Com Claude Code
> Peça: *"Faz a validação completa da VPS: conecta como `felipe` e como `luiz`, roda todos os CLIs, verifica repos clonados, confirma skills instaladas, MCPs configurados e firewall ativo. Me dá um relatório ✅/❌ por item."*
> Esta é a etapa mais valiosa com Claude Code — ele roda todos os checks em sequência e entrega um relatório consolidado, sem você precisar abrir múltiplos terminais.

---

## Referência rápida — O que vai onde

| Item | Onde fica | Vault 1P |
|---|---|---|
| Senha root | Apenas no 1P | `Hosts` → `Hostinger VPS - Developer - rootpassword` |
| Chave SSH felipe | `~/.ssh/hostinger_dev_felipe` + 1P | `Hosts` → `Hostinger VPS Dev - felipe (SSH Key)` |
| Chave SSH luiz | `~/.ssh/hostinger_dev_luiz` + 1P | `Hosts` → `Hostinger VPS Dev - luiz (SSH Key)` |
| SA token 1P (Luiz) | `~/.profile` da VPS | `Hosts` → `Hostinger VPS - SA - luiz` |
| GH_TOKEN | `~/.profile` da VPS | `Hosts` → `Github - VPS Dev - org access` |
| VERCEL_TOKEN | `~/.profile` da VPS | `Hosts` → `Vercel - api - cli` |
| SUPABASE_ACCESS_TOKEN | `~/.profile` da VPS | `Databases` → `Supabase - ClaudeCode - CLI` |
| Linear API key | `~/.claude/settings.json` da VPS | `Serviços & Tools` → `Linear - API` |

---

## Decisões desta configuração (para referência futura)

- **Sem Coolify na dev** — só na VPS master (produção) quando provisionar
- **Skills por cópia, não symlink** — independência entre usuários; cada um pode customizar sem afetar o outro
- **Sem branch protection** — Luiz pode fazer push direto para `main` por enquanto; revisar quando o volume de commits aumentar
- **cadencia-app** está na conta pessoal `felipeluissalgueiro`, não na org; necessário clonar com esse remote
- **SA token 1P no `.profile`, não `.bashrc`** — `.bashrc` não carrega em sessões não-interativas (cron, scripts)
- **GH fine-grained PAT bloqueado para a org** — usar classic PAT; rever quando org migrar

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Dev/VPS-Dev-Documentacao-Tecnica]] · [[Infra/VPS-Hostinger/VPS-Dev/Acesso-VPS-Dev-Luiz]] · [[Time/Luiz/Manual-VPS-Dev]]
