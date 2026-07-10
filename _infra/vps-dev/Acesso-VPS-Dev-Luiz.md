---
date: 2026-05-22
tags: [infra, vps, luiz, acesso, onboarding]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]", "[[ecuro-mcp]]", "[[pd-portal]]"]
---
# Acesso à VPS de Desenvolvimento — Luiz

> Referência completa para o Luiz acessar e trabalhar na VPS dev. Atualizar sempre que mudar chave, IP ou permissão.

---

## Dados de acesso

| Campo | Valor |
|---|---|
| IP | `2.24.117.172` |
| Usuário | `luiz` |
| Porta SSH | `22` |
| Diretório home | `/home/luiz/` |

---

## SSH — configuração inicial (uma vez só)

### 1. Baixar a chave privada

Felipe envia a chave privada via link 1Password. Salvar o conteúdo em:
```
~/.ssh/hostinger_dev_luiz
```

### 2. Ajustar permissões

```bash
chmod 600 ~/.ssh/hostinger_dev_luiz
```

### 3. Conectar

```bash
ssh -i ~/.ssh/hostinger_dev_luiz luiz@2.24.117.172
```

### 4. (Opcional) Alias no ~/.ssh/config

```
Host vps-dev
  HostName 2.24.117.172
  User luiz
  IdentityFile ~/.ssh/hostinger_dev_luiz
```

Com o alias: `ssh vps-dev`

---

## Estrutura de pastas

```
/home/luiz/
├── gci-go-whatsapp/      ← pipeline GCI Goiás (Lara)
├── cadencia-app/          ← workers Cadência
├── pd-portal/             ← Portal PD
├── ecuro-mcp/             ← MCP integração eCuro
├── claude-dev-skills/     ← skills compartilhadas do time
├── .claude/               ← Claude Code (settings, skills)
│   ├── settings.json
│   └── skills/
├── .nvm/                  ← Node.js e CLIs por usuário
└── .profile               ← variáveis de ambiente (tokens via 1P)
```

---

## Variáveis de ambiente (.profile)

Carregadas automaticamente ao conectar via SSH:

```bash
export NVM_DIR="$HOME/.nvm"
export OP_SERVICE_ACCOUNT_TOKEN="..."   # 1P SA read-only (vault Hostinger VPS)
export VERCEL_TOKEN="..."
export SUPABASE_ACCESS_TOKEN="..."
export GH_TOKEN="..."                   # acesso org Posicionamento-Digital
```

Se um CLI não aparecer no PATH, rodar: `source ~/.profile`

---

## CLIs disponíveis

### Sistema (sempre disponíveis)

| CLI | Uso |
|---|---|
| `git` | controle de versão |
| `docker` / `docker compose` | containers (sem sudo) |
| `node` / `npm` | Node.js |
| `python3` / `pip3` / `uv` | Python |
| `gh` | GitHub CLI |
| `op` | 1Password CLI |
| `gemini` | Gemini CLI (code review) |
| `tmux` | sessões persistentes |
| `jq` | parse JSON |

### Por sessão (via nvm — carregar com `source ~/.profile`)

| CLI | Uso |
|---|---|
| `claude` | Claude Code |
| `codex` | OpenAI Codex CLI |
| `railway` | Railway CLI |
| `vercel` | Vercel CLI |

---

## 1Password na VPS

O `op` está instalado e autenticado com um **Service Account read-only** no vault `Hostinger VPS`. O Luiz não vê os valores — só acessa via CLI.

```bash
# Pegar credencial pelo nome do item
op item get "Nome da Key" --fields credential

# Exemplos:
op item get "Anthropic API Key" --fields credential
op item get "GHL - Agency API Key" --fields credential
op item get "Supabase - gci-go" --fields credential
```

Se `op` retornar erro de autenticação: avisar Felipe para renovar o SA token.

---

## Sessões com tmux (obrigatório)

Sempre abrir tmux antes de trabalhar. Se a conexão cair, o processo continua.

```bash
tmux              # nova sessão
tmux attach       # retomar após reconectar
```

Atalhos dentro do tmux:
- `Ctrl+B, D` — desconectar (sessão continua rodando)
- `Ctrl+B, C` — nova janela
- `Ctrl+B, N` — próxima janela
- `Ctrl+B, "` — dividir horizontalmente

---

## Git e Linear

### Iniciar issue

```bash
/linear-start-issue PDL-XX
# Claude Code faz checkout da branch automaticamente
```

### Fluxo de commit e push

```bash
git add .
git commit -m "feat: PDL-XX descrição do que fez"
git push origin feature/pdl-XX
```

### Fechar issue

```bash
/linear-close-issue PDL-XX
# Verifica critério de aceite, commit final, push
```

---

## Claude Code

Instalado em `/home/luiz/.nvm/`. Para usar:

```bash
claude
```

Skills disponíveis (20):

| Skill | Quando usar |
|---|---|
| `/linear-start-issue` | Antes de começar qualquer issue |
| `/linear-close-issue` | Ao terminar e fazer push |
| `/linear-planejar-issue` | Antes de iniciar issue nova (plano técnico) |
| `/linear-criar-issue` | Criar issue nova avulsa |
| `/gemini-review` | Code review antes do PR |
| `/claude-review` | Code review com Opus (mais pesado) |
| `/codex-review` | Code review com Codex |
| `/debug-polya` | Bug difícil — framework Pólya |
| `/validar-deploy-vps` | Validar script antes de subir |
| `/credencial` | Pegar/salvar credenciais no 1P |
| `/status` | Ver pendências do projeto |
| `/ja-fiz` | Ver o que já entregou |
| `/log-sessao` | Registrar sessão |
| `/registrar-incidente` | Documentar erro ou aprendizado |
| `/handoff-sessao` | Passar contexto entre sessões |
| `/issue-semana` | Ver issues do ciclo atual |
| `/espelhar-repo-vps` | Clonar repo privado na VPS |
| `/runtime-fix-review` | Verificar correções em produção |
| `/linear-gestao-atividades` | Criar múltiplas issues de projeto |
| `/linear-atualizar-issue` | Atualizar plano técnico de issue |

---

## Docker

Luiz tem acesso ao Docker sem sudo:

```bash
docker compose up -d          # subir containers
docker compose down           # derrubar
docker compose logs -f app    # logs em tempo real
docker ps                     # containers rodando
docker stats                  # uso de recurso
```

---

## Restrições

| O que | Motivo |
|---|---|
| `sudo` — sem permissão | segurança; se precisar de pacote, avisar Felipe |
| `/home/felipe/` — sem acesso | isolamento de usuário |
| VPS de produção (`72.60.4.71`) — sem acesso shell | Luiz não tem chave para produção |
| Credenciais em texto claro — proibido | só via `op item get` |
| Commit direto na `main` — proibido | fluxo é `feature/pdl-XX` → PR → merge |

---

## Firewall

Somente porta 22 (SSH) está aberta por padrão. Se precisar expor porta para webhook ou teste externo, pedir pro Felipe liberar via UFW.

---

## Problemas comuns

| Problema | Solução |
|---|---|
| SSH não conecta | Verificar chave: `ssh -i ~/.ssh/hostinger_dev_luiz luiz@2.24.117.172 -v` |
| CLI não encontrado (`railway`, `claude`, etc.) | `source ~/.profile` e tentar de novo |
| `op item get` falha com auth error | SA expirou — avisar Felipe |
| Porta bloqueada para webhook | Pedir pro Felipe: `ufw allow <porta>` |
| Processo morreu ao desconectar | Sempre usar tmux antes de iniciar processo longo |
| Branch protegida, push negado | Verificar se está na branch certa (`git branch`) |

---

## Contato

Problemas de infra ou acesso: fala com Felipe diretamente.
Issues e entregas: Linear via `/linear-start-issue` e `/linear-close-issue`.

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Dev/VPS-Dev-Documentacao-Tecnica]] · [[Infra/VPS-Hostinger/README]] · [[Time/Luiz/Manual-VPS-Dev]]
