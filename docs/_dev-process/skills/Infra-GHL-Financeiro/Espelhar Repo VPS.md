---
date: 2026-05-14
tags: [skill, infra, vps, github, deploy, key, ssh, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Espelhar Repo VPS

Provisiona clone git autenticado de repositório privado na VPS para que Luiz trabalhe via SSH + Claude Code com git pull/push funcionando sem autenticação manual. Usa deploy key SSH ed25519 exclusiva.

## Quando usar
"/espelhar-repo-vps", "espelha esse repo na vps", "gera deploy key pra vps", "quero o Luiz codar direto na vps", "clone na vps".

---

## Conteúdo da Skill

```markdown
---
name: espelhar-repo-vps
description: >
  Provisiona um clone git autenticado de um repositório privado numa VPS pra
  permitir que um dev (ex: Luiz) trabalhe direto lá via SSH + Claude Code, com
  git pull/push funcionando sem autenticação manual. Usa deploy key SSH ed25519
  exclusiva por VPS (Felipe cola no repo GitHub uma única vez).
---

# /espelhar-repo-vps — Espelhar repo git numa VPS com deploy key

Automatiza o setup que faz uma VPS virar "ambiente de dev espelhado" do repositório GitHub.

## Resultado final

Após rodar:
```bash
ssh root@<vps>
cd /root/<repo-name>
claude
git add . && git commit -m "..." && git push
```

Sem o dev ter conta no GitHub, sem PAT, sem login.

## Inputs

| Input | Como obter |
|---|---|
| `vps_host` | IP ou hostname. Perguntar. |
| `vps_user` | default `root`. Perguntar só se for diferente. |
| `vps_ssh_key` | path local da chave SSH (ex: `~/.ssh/hostinger_gci_go`). |
| `repo_full_name` | `owner/name` no GitHub. Inferir do `git remote -v` do cwd se aplicável. |
| `target_path` | default `/root/<repo-name>`. |
| `branch` | default `main`. |
| `deploy_key_title` | default `VPS <vps_host>`. |
| `git_identity_name` / `git_identity_email` | default `<repo>-vps-deploy` / `deploy@<dominio>`. |

## Fluxo

```
1. Coletar/confirmar inputs
2. SSH check: ping VPS + git + claude code
3. Gerar deploy key ed25519 na VPS (idempotente)
4. Mostrar pubkey pro Felipe colar no GitHub (ou adicionar via API com PAT)
   ⏸ AGUARDAR confirmação inequívoca (se manual)
5. Validar autenticação SSH GitHub
6. Backup envs/secrets se pasta já existir
7. Clone fresco via SSH (após confirmação destrutiva)
8. Restaurar envs
9. Configurar git user.name/email + ssh config
10. Validar push (commit dummy + revert)
11. Reportar pronto + comandos pro dev
```

## Implementação

### Passo 3 — Deploy key (idempotente)

```bash
KEY_NAME="<repo-name>_deploy"
$SSH "test -f /root/.ssh/$KEY_NAME && echo 'já existe' || (ssh-keygen -t ed25519 -f /root/.ssh/$KEY_NAME -N '' -C '<repo>-deploy-vps' -q && echo 'criada')"
$SSH "grep -q '^github.com' /root/.ssh/known_hosts 2>/dev/null || ssh-keyscan -t ed25519 github.com 2>/dev/null >> /root/.ssh/known_hosts"
```

### Passo 4 — Adicionar deploy key no GitHub

**Tem PAT no 1Password?** A skill checa primeiro:

```bash
OP="/c/Users/felip/AppData/Local/Microsoft/WinGet/Packages/AgileBits.1Password.CLI_Microsoft.Winget.Source_8wekyb3d8bbwe/op.exe"
# Prioridade 1: Classic PAT (Serviços & Tools → ClaudeCode_ClassicToken)
PAT_ITEM_ID=$($OP item list 2>/dev/null | grep -iE "claudecode_classictoken" | awk '{print $1}' | head -1)
```

**Se PAT existe** → caminho automático:
```bash
PAT=$($OP item get $PAT_ITEM_ID --field credencial --reveal 2>/dev/null)
PUBKEY=$($SSH "cat /root/.ssh/$KEY_NAME.pub")

curl -s -w "\n%{http_code}" -X POST \
  "https://api.github.com/repos/<owner>/<repo>/keys" \
  -H "Authorization: Bearer $PAT" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d "{\"title\":\"<deploy_key_title>\",\"key\":\"$PUBKEY\",\"read_only\":false}"
```

- `201` → criada com sucesso, prosseguir
- `422` "key is already in use" → idempotência ok
- `401`/`403` → cair pro caminho manual

**Se PAT NÃO existe** OU API falhou → mostrar pubkey e pedir que Felipe cole manualmente no GitHub.

### Passo 8 — Clone

```bash
$SSH "
rm -rf <target_path>
cd $(dirname <target_path>) && git clone git@github.com:<owner>/<repo>.git $(basename <target_path>)
cd <target_path> && git checkout <branch>
git log --oneline -3"
```

### Passo 10 — Validar push

```bash
$SSH "
cd <target_path>
git config user.name '<git_identity_name>'
git config user.email '<git_identity_email>'

echo '# VPS deploy test' > .vps-deploy-test
git add .vps-deploy-test
git commit -m 'test(vps): valida deploy key write access' -q
git push origin <branch> 2>&1 | tail -3
git rm .vps-deploy-test -q
git commit -m 'revert(vps): remove deploy test marker' -q
git push origin <branch> 2>&1 | tail -3"
```

### Passo 11 — Reportar

```
✅ VPS pronta pra trabalhar

| Item | Status |
|---|---|
| Deploy key | /root/.ssh/<key_name> (write ✓) |
| Repo clonado | <target_path> (branch <branch>) |
| Auth SSH GitHub | OK |
| git pull/push | OK (validado com commit + revert) |
| Envs/secrets restaurados | [N arquivos] |
| Backup | <backup_path> |

Comandos pro dev:
  ssh <user>@<host>
  cd <target_path>
  claude
  git add . && git commit -m "..." && git push
```

## Histórico de uso

- 2026-05-11 — `felipeluissalgueiro/gci-go-whatsapp` em `72.60.4.71:/root/gci-go-whatsapp` (primeira aplicação manual que originou esta skill)
- 2026-05-11 — PAT fine-grained configurado em `op://Serviços & Tools/Git Hub - ClaudeCode_Skill - Repo_VPS`. Caminho automático funcional.
```

## Notas Relacionadas
[[Gestao-Projetos/Gestao Atividades Projeto]] · [[Infra-GHL-Financeiro/Credencial]]
