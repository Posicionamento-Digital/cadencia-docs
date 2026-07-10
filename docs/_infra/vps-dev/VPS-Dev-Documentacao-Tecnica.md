---
date: 2026-05-21
tags: [infra, vps, documentacao, dev]
moc: "[[MOC-Infra]]"
projeto: VPS de Desenvolvimento
type: source
entities: ["[[Cadencia]]", "[[ecuro-mcp]]", "[[pd-portal]]"]
---
# VPS de Desenvolvimento — Documentação Técnica

> Referência completa da VPS de desenvolvimento. Provisionada em 21/05/2026.

---

## Especificações

| Campo | Valor |
|---|---|
| Provider | Hostinger |
| Plano | KVM1 (1 vCPU, 4GB RAM, 50GB SSD) |
| OS | Ubuntu 24.04.4 LTS |
| IP | 2.24.117.172 |
| Hostname | srv1692513 |
| Kernel | 6.8.0-117-generic |

---

## Usuários e acesso

| Usuário | UID | Sudo | Grupos | Diretório de trabalho |
|---|---|---|---|---|
| `root` | 0 | — | — | Sem login SSH direto |
| `felipe` | 1000 | Sim (NOPASSWD) | sudo, users, docker | `/home/felipe/` |
| `luiz` | 1001 | Não | users, docker | `/home/luiz/` |

### Chaves SSH

| Usuário | Chave local | Chave pública no servidor |
|---|---|---|
| `felipe` | `~/.ssh/hostinger_dev_felipe` | `/home/felipe/.ssh/authorized_keys` |
| `luiz` | `~/.ssh/hostinger_dev_luiz` | `/home/luiz/.ssh/authorized_keys` |

Chaves também salvas no 1Password vault `Hosts`:
- `Hostinger VPS Dev - felipe (SSH Key)`
- `Hostinger VPS Dev - luiz (SSH Key)`

### Como conectar

```bash
ssh -i ~/.ssh/hostinger_dev_felipe felipe@2.24.117.172
ssh -i ~/.ssh/hostinger_dev_luiz luiz@2.24.117.172
```

### Configuração SSH do servidor (`/etc/ssh/sshd_config`)
- `PasswordAuthentication no` — só chave SSH
- `PermitRootLogin no` — root bloqueado
- `AllowUsers felipe luiz` — só esses dois usuários

---

## Software instalado

### Sistema (disponível para todos)

| Ferramenta | Versão | Instalação |
|---|---|---|
| `git` | 2.43.0 | apt |
| `docker` | 29.5.2 | get.docker.com |
| `docker compose` | v5.1.4 | incluído no Docker |
| `node` | 24.16.0 | NodeSource (system-wide) |
| `npm` | 11.12.1 | NodeSource |
| `python3` | 3.12.3 | apt (sistema) |
| `pip3` | 24.0 | apt |
| `uv` | 0.11.16 | astral.sh (em /usr/local/bin) |
| `gh` (GitHub CLI) | 2.92.0 | apt (github.com/packages) |
| `op` (1Password CLI) | 2.34.0 | apt (downloads.1password.com) |
| `gemini` CLI | 0.42.0 | npm global (sistema) |
| `tmux` | 3.4 | apt |
| `jq` | 1.7 | apt |
| `curl`, `wget`, `htop`, `unzip` | — | apt |

### Por usuário (via nvm em ~/.nvm/)

| Ferramenta | Versão | Usuários |
|---|---|---|
| `claude` (Claude Code) | 2.1.147 | felipe, luiz |
| `codex` (OpenAI Codex CLI) | 0.133.0 | felipe, luiz |
| `railway` | 4.59.0 | felipe, luiz |
| `vercel` | 54.3.0 | felipe, luiz |

---

## Variáveis de ambiente (`.profile` de cada usuário)

### luiz
```bash
export NVM_DIR="$HOME/.nvm"
export OP_SERVICE_ACCOUNT_TOKEN="..."   # SA 1P read-only vault Hostinger VPS
export VERCEL_TOKEN="..."               # Vercel API token
export SUPABASE_ACCESS_TOKEN="..."      # Supabase PAT
export GH_TOKEN="..."                   # GitHub PAT (org Posicionamento-Digital)
```

### felipe
```bash
export NVM_DIR="$HOME/.nvm"
export VERCEL_TOKEN="..."
export SUPABASE_ACCESS_TOKEN="..."
export GH_TOKEN="..."
```

---

## 1Password

### Service Account do Luiz
- **Nome:** `Hostinger VPS - Acessos & Credenciais`
- **Escopo:** Read-only no vault `Hostinger VPS`
- **Como usar:** `op item get "Nome da Key" --fields credential`
- O Luiz nunca vê os valores — só acessa via CLI

### Vault `Hostinger VPS`
Populate pelo Felipe com as keys que o Luiz precisa (Anthropic, GHL, Stevo, Supabase, etc.)

---

## MCPs configurados (`~/.claude/settings.json`)

Ambos os usuários têm os mesmos MCPs:

| MCP | Tipo | O que faz |
|---|---|---|
| `linear` | HTTP (SSE) | Gestão de issues e projetos |
| `hostinger-mcp` | stdio (npx) | Gerenciar VPS via API Hostinger |
| `posthog` | HTTP | Analytics |

---

## Skills do Claude Code

### Felipe (46 skills)
Todas as skills do setup local — incluindo gestão pessoal (abrir-dia, fechar-dia, chefe-de-staff), Linear completo, reviews, infra, Obsidian, WhatsApp.

### Luiz (20 skills)
Skills de desenvolvimento e gestão de tarefas:
`log-sessao`, `linear-start-issue`, `linear-close-issue`, `linear-planejar-issue`, `linear-atualizar-issue`, `linear-criar-issue`, `linear-gestao-atividades`, `gemini-review`, `claude-review`, `codex-review`, `debug-polya`, `runtime-fix-review`, `espelhar-repo-vps`, `registrar-incidente`, `credencial`, `validar-deploy-vps`, `status`, `ja-fiz`, `issue-semana`, `handoff-sessao`

---

## Repos clonados (Luiz)

| Repo | Path | Org/Owner |
|---|---|---|
| `gci-go-whatsapp` | `/home/luiz/gci-go-whatsapp` | Posicionamento-Digital |
| `cadencia-app` | `/home/luiz/cadencia-app` | felipeluissalgueiro (pessoal) |
| `pd-portal` | `/home/luiz/pd-portal` | Posicionamento-Digital |
| `ecuro-mcp` | `/home/luiz/ecuro-mcp` | Posicionamento-Digital |
| `claude-dev-skills` | `/home/luiz/claude-dev-skills` | Posicionamento-Digital |

Repos do Felipe em `/home/felipe/` seguem o mesmo padrão.

---

## Firewall (UFW)

| Porta | Protocolo | Status |
|---|---|---|
| 22 | TCP | ALLOW (SSH) |
| Demais | — | DENY |

Outras portas são liberadas conforme serviços subirem (webhooks, HTTP, HTTPS).

---

## Fluxo de deploy (quando VPS master estiver pronta)

```
[VPS dev — /home/luiz/<projeto>/]
        |
        | git push → GitHub (branch feature/pdl-XX)
                        |
                        | Merge → main
                                   |
                                   | webhook → Coolify (VPS master)
                                               |
                                               | build + deploy containers
```

Luiz não tem acesso shell à VPS master.

---

## Pendências

- [ ] Configurar branch protection nos repos quando fluxo de revisão for necessário
- [ ] Adicionar domínio + HTTPS quando Luiz precisar testar webhooks externos
- [ ] Popular vault `Hostinger VPS` no 1P com todas as keys que Luiz precisa
- [ ] Configurar Railway token quando Luiz precisar do CLI
- [ ] Instalar Coolify na VPS master para fechar o loop de deploy

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/README]] · [[Projetos/GCI-GO/Docs/README]]
