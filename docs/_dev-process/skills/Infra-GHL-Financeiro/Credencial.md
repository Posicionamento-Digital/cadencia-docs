---
date: 2026-05-14
tags: [skill, infra, credenciais, 1password, seguranca, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Credencial

Gerencia credenciais via 1Password CLI (`op`). Valores sensíveis nunca passam pelo contexto do agente.

## Quando usar
"/credencial", "salva essa key no 1P", "pega a senha do X", "lista minhas credenciais", "cria credencial nova", "usa a credencial do W pra rodar isso", "atualiza a key do Y".

---

## Conteúdo da Skill

```markdown
---
name: credencial
description: >
  Gerencia credenciais (API keys, senhas, tokens) via 1Password CLI (`op`) com fluxo
  seguro — valores sensíveis nunca passam pelo contexto do agente. Ativar quando
  Felipe disser "/credencial", "salva essa key no 1P", "salva no 1password",
  "guarda essa senha", "pega a senha do X", "lista minhas credenciais",
  "atualiza a key do Y", "roda [comando] com a key do Z", "usa a credencial do W
  pra rodar isso", "cria credencial nova".
---

# Credencial — Gestão de Segredos via 1Password CLI

Skill que padroniza o uso do 1Password CLI (`op`) com fluxo seguro: valores sensíveis nunca passam pelo contexto do Claude.

## Mapa de credenciais — CONSULTAR SEMPRE

**ANTES de procurar/listar items no 1P**, ler `VAULT_MAP.md` (mesma pasta desta skill):
- Caminhos: `C:\Users\felip\.claude\skills\credencial\VAULT_MAP.md` (master) e `C:\Users\felip\OneDrive\Documentos\ClaudeCode\Hub Projetos\Rotina\docs\1password-vault-map.md` (mirror)

## Pré-requisitos

- 1Password CLI instalado: `op --version` deve responder
- 1Password app rodando e desbloqueado
- Integração CLI ↔ app habilitada em: 1Password → Settings → Developer → "Integrate with 1Password CLI"

## Regra de ouro de segurança

| Operação | Quem executa | Valor passa pelo contexto? |
|---|---|---|
| **Criar/editar item** (valor sensível novo) | Felipe roda manualmente | ❌ Não |
| **Listar items** / metadados | Agente | ❌ Não |
| **Executar comando** com `op run` | Agente | ❌ Não (injetado no subprocesso) |
| **Ler valor explicitamente** (`op read`, `op item get --reveal`) | Agente, **só com pedido explícito** | ⚠️ Sim |

## Comandos / Intenções

### 1. Salvar credencial nova

Entregar o comando pronto pra Felipe rodar:

```powershell
op item create --category="API Credential" --title="<TITULO>" --vault="<VAULT>" credential="<COLA AQUI>" --tags="<tags>"
```

Se Felipe quiser sem deixar no histórico do PowerShell:
```powershell
$key = Read-Host "Cola a key" -AsSecureString | ConvertFrom-SecureString -AsPlainText
op item create --category="API Credential" --title="<TITULO>" --vault="<VAULT>" credential="$key"
Remove-Variable key
```

### 2. Listar credenciais

```powershell
op item list --format=json | ConvertFrom-Json | Select-Object title, vault, tags
op item list --tags cadencia
```

### 3. Atualizar credencial existente

```powershell
op item edit "<TITULO>" credential="<COLA NOVO VALOR>"
```

### 4. Usar credencial pra rodar comando

**Preferir SEMPRE `op run`** — não passa pelo contexto:

```powershell
op run --env-file=".env" -- <comando>
```

### 5. Ler valor explicitamente (último recurso)

Avisar Felipe que o valor entrará no contexto e pedir confirmação. Depois:

```powershell
op read "op://Private/<TITULO>/credential"
```

### 6. Templated config files com `op inject`

```powershell
# arquivo config.yml.tpl contém: api_key: op://Private/X/credential
op inject --in-file config.yml.tpl --out-file config.yml
```

⚠️ Output é arquivo com secrets em plaintext. Adicionar ao `.gitignore`.

### 7. Gerar senhas/secrets fortes

```powershell
op item create --category=login --title="X" --generate-password=32,letters,digits,symbols
```

### 8. Anexar/baixar documentos

```powershell
op document create ./private-key.pem --title="SSH Cadencia VPS" --vault=Private
op document get "SSH Cadencia VPS" --output ./private-key.pem
```

### 9. Shell plugins (biometric auth pra outras CLIs)

```powershell
op plugin init gh     # plugin pro GitHub CLI
op plugin init claude # plugin pro Claude Code CLI
```

### 11. Service accounts pra VPS/CI

```bash
export OP_SERVICE_ACCOUNT_TOKEN="ops_eyJ..."
op run --env-file=.env -- python orchestrator.py
```

### 12. Migrar `.env` existente pra refs `op://`

1. Ler o `.env` do projeto (valores ficam no contexto — avisar Felipe)
2. Pra cada chave, gerar comando `op item create` (Felipe roda)
3. Após Felipe confirmar criação, reescrever `.env` substituindo valor por `op://...`
4. Ajustar comando de start pra prefixar com `op run --env-file=.env --`

## Quando usar `op run` vs `op inject` vs `op read`

| Necessidade | Ferramenta |
|---|---|
| App lê secrets de **env vars** (dotenv, process.env, os.environ) | `op run --env-file=.env -- <cmd>` |
| App lê secrets de **arquivo de config** (yml/json/tfvars) | `op inject --in-file tpl --out-file final` |
| Preciso do **valor cru** num shell pipeline | `op read "op://..."` (último recurso) |
| CLI de terceiro (aws/gh/stripe/claude) | **Shell plugin** — `op plugin init <nome>` |

## Convenções de nomenclatura

- **Título:** `<Serviço> - <Projeto>` (ex: `OpenAI - Cadencia`, `Notion - Cadencia`)
- **Reusáveis:** `<Serviço> - principal` quando a mesma key roda em vários projetos
- **Tags:** sempre adicionar tag do projeto e do serviço
- **Vault:** `Private` por default; `Production` pra service accounts da VPS

## Formato de referência `op://`

```
op://<vault>/<titulo-do-item>/<campo>
```

Exemplo: `op://Private/OpenAI - Cadencia/credential`

Campos comuns: `credential` (API keys), `password` (Logins), `username`.

## Output esperado da skill

Após executar o que foi pedido, devolver pra Felipe:
- ✅ O que foi feito
- 📋 A referência `op://...` se item foi criado
- 🔧 Próximos passos
- ⚠️ Avisos de segurança se valor passou pelo contexto
```

## Notas Relacionadas
[[Infra-GHL-Financeiro/Criar User GHL]] · [[Stamper-Operacionais/Registrar Incidente]]
