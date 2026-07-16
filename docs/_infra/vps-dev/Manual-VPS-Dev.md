---
date: 2026-05-21
tags: [infra, vps, luiz, processo, onboarding]
moc: "[[MOC-Time]]"
type: source
entities: ["[[Cadencia]]", "[[ecuro-mcp]]", "[[pd-portal]]"]
---
# Manual da VPS de Desenvolvimento — Luiz

> Tudo que você precisa saber para trabalhar na VPS dev.

---

## Conectando na VPS

Você recebe a chave privada `hostinger_dev_luiz`. Coloca em `~/.ssh/` no seu computador e conecta:

```bash
ssh -i ~/.ssh/hostinger_dev_luiz luiz@2.24.117.172
```

**Primeiro acesso:** ao conectar, você cai direto no seu home `/home/luiz/`. É onde ficam todos os seus repos.

---

## Estrutura do seu ambiente

```
/home/luiz/
├── gci-go-whatsapp/      ← repo principal (Lara)
├── cadencia-app/          ← Cadência workers
├── pd-portal/             ← Portal PD
├── ecuro-mcp/             ← MCP eCuro
├── claude-dev-skills/     ← Skills dev
├── .claude/               ← Claude Code (settings, skills)
├── .nvm/                  ← Node.js e CLIs npm
└── .profile               ← variáveis de ambiente (tokens)
```

---

## Sessões persistentes com tmux

**Regra de ouro:** sempre abra um `tmux` antes de trabalhar. Se a conexão SSH cair, seu trabalho continua rodando.

```bash
tmux              # iniciar sessão nova
tmux attach       # voltar para sessão existente após reconectar
```

Dentro do tmux:
- `Ctrl+B, D` — desconectar sem matar (sessão continua)
- `Ctrl+B, C` — criar nova janela
- `Ctrl+B, N` — próxima janela

---

## Credenciais via 1Password

Você tem o `op` CLI instalado e autenticado com um Service Account read-only. Para pegar qualquer credencial:

```bash
op item get "Nome da credencial" --fields credential
```

Exemplos:
```bash
op item get "Anthropic API Key" --fields credential
```

Você nunca vê as credenciais diretamente no código — sempre via `op`. Felipe adiciona novos itens no vault conforme você precisar.

---

## Fluxo de trabalho com Git

### Iniciando uma issue

1. Pega a issue no Linear (`/linear-start-issue PDL-XX`)
2. Claude Code cria a branch automaticamente
3. Você codifica

### Enviando código

```bash
git add .
git commit -m "feat: descrição do que fez"
git push origin feature/pdl-XX
```

### Deploy

Por enquanto: push para qualquer branch, incluindo `main`. Quando o Coolify estiver configurado na VPS master, o merge para `main` vai disparar o deploy automático.

---

## Claude Code na VPS

O Claude Code está instalado no seu usuário. Para usar:

```bash
claude
```

Suas skills ficam em `~/.claude/skills/`. As principais para o seu dia a dia:

| Skill | Quando usar |
|---|---|
| `/linear-start-issue` | Antes de começar a codar |
| `/linear-close-issue` | Ao terminar e fazer push |
| `/log-sessao` | Registrar o que fez na sessão |
| `/debug-polya` | Quando travar num bug |
| `/gemini-review` | Code review antes do PR |
| `/claude-review` | Code review com Opus |
| `/validar-deploy-vps` | Validar script antes de subir |
| `/credencial` | Gerenciar credenciais via 1P |
| `/status` | Ver pendências do projeto |
| `/ja-fiz` | Ver o que já entregou |

---

## CLIs disponíveis

Todos acessíveis após `bash -l` ou em sessão normal de SSH:

```bash
node --version      # Node.js
docker ps           # containers rodando
gh repo list        # repos GitHub
vercel --version    # Vercel CLI
railway --version   # Railway CLI
gemini              # Gemini CLI (code review)
op item list        # 1Password CLI
uv pip install X    # instalar pacotes Python (mais rápido que pip)
jq '.campo' arq.json  # parse JSON
```

---

## Docker

Você tem acesso ao Docker sem precisar de sudo:

```bash
docker compose up -d         # subir containers
docker compose down          # derrubar
docker compose logs -f app   # ver logs em tempo real
docker ps                    # containers rodando
docker stats                 # uso de recurso
```

---

## Você NÃO pode

- Usar `sudo` — não tem permissão
- Acessar `/home/felipe/` ou outros diretórios fora do seu home
- Acessar a VPS de produção (`72.60.4.71`) via shell
- Ver valores de credenciais direto — só via `op item get`

Se precisar de algo que exige sudo (instalar pacote, alterar config do sistema), fala com o Felipe.

---

## Problemas comuns

**SSH não conecta:**
Verifica se está usando a chave certa: `ssh -i ~/.ssh/hostinger_dev_luiz luiz@2.24.117.172`

**Comando não encontrado (railway, vercel, claude):**
Abre uma nova sessão SSH ou roda `source ~/.profile` para carregar o PATH.

**`op item get` não funciona:**
Token pode ter expirado. Fala com o Felipe para renovar o SA.

**Porta bloqueada para webhook:**
Por padrão só a porta 22 está aberta. Felipe libera a porta necessária no UFW.

---

## Contato

Qualquer problema de infraestrutura ou acesso: fala com o Felipe.
Issues e entregas: Linear, via `/linear-start-issue` e `/linear-close-issue`.
