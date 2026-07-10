---
date: 2026-05-14
tags: [skill, gestao, linear, github, deploy, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Close Issue

Fecha issue no Linear (Done), faz commit com "Closes PDL-XX", merge para main e dispara deploy conforme plataforma do projeto.

## Quando usar
`/close-issue PDL-11`, `/close-issue` (lista In Progress), "fechar PDL-11", "terminei", "entregue".

---

## Conteúdo da Skill

```markdown
---
name: close-issue
description: Fecha uma issue no Linear (Done), faz commit com "Closes PDL-XX", merge para main e dispara deploy conforme plataforma do projeto.
---

# /close-issue

## Quando ativar
- `close-issue PDL-11` / `close-issue` (lista In Progress)
- "fechar PDL-11", "terminei", "entregue"

## Plataformas de deploy por projeto

| Projeto | Plataforma | Deploy |
|---|---|---|
| cadencia-app | Vercel + Railway | automático ao mergear main |
| gci-go-whatsapp | VPS Hostinger | manual: pull + restart |
| lara (confirmação de agenda) | VPS Hostinger | manual: pull + restart |
| bot-telegram | VPS Hostinger | manual: pull + restart |

## Passo 1 — Identificar issue

```python
import subprocess, json, os

def get_token():
    try:
        for line in open('/root/.claude/.env'):
            if line.startswith('LINEAR_API_TOKEN='):
                return line.strip().split('=',1)[1]
    except: pass
    return os.environ.get('LINEAR_API_TOKEN','')

TOKEN = get_token()

QUERY = """{ issues(filter: {
  assignee: { isMe: { eq: true } }
  state: { type: { eq: "started" } }
}, first: 10) { nodes { id identifier title project { name } branchName } } }"""

r = subprocess.run(['curl','-s','-X','POST','https://api.linear.app/graphql',
    '-H', f'Authorization: {TOKEN}', '-H', 'Content-Type: application/json',
    '-d', json.dumps({'query': QUERY})
], capture_output=True)
issues = json.loads(r.stdout)['data']['issues']['nodes']
```

## Passo 2 — Verificar git status

```bash
git status
git log --oneline -3
```

Tem arquivos não commitados? Avisar antes de fechar.

## Passo 3 — Confirmar entrega

Mostrar critérios de aceite da issue e perguntar se está tudo feito.

## Passo 4 — Commit + merge para main

```bash
git add <arquivos>
git commit -m "feat: [descricao]

Closes PDL-XX"
git push origin <branch-da-issue>

# Merge direto para main (sem PR)
git checkout main
git pull origin main
git merge <branch-da-issue> --no-ff -m "merge: PDL-XX [descricao]"
git push origin main
```

**OBRIGATORIO:** `Closes PDL-XX` no corpo do commit fecha a issue no Linear automaticamente.

## Passo 5 — Deploy conforme plataforma

### Vercel / Railway — deploy automático
O push para main já dispara o deploy. Apenas confirmar:
```bash
echo "Deploy disparado automaticamente. Vercel/Railway detecta o push no main."
```

### VPS Hostinger — deploy manual
```bash
VPS_IP="72.60.4.71"
SSH_KEY="/root/.ssh/hostinger_pd"
REPO_PATH="/root/<nome-do-repo>"

ssh -i $SSH_KEY root@$VPS_IP "
  cd $REPO_PATH
  git pull origin main
  if command -v pm2 &>/dev/null && pm2 list | grep -q $REPO_PATH; then
    pm2 restart all
  elif command -v docker &>/dev/null && docker ps | grep -q <container-name>; then
    docker compose pull && docker compose up -d
  else
    echo 'Reiniciar manualmente — nao detectei pm2 nem docker'
  fi
  echo 'Deploy VPS concluido'
"
```

## Passo 6 — Marcar Done no Linear

Usar mutation GraphQL para atualizar o estado da issue para o primeiro estado do tipo "completed".

## Regras
1. Verificar git status antes de fechar
2. Sempre mergear para main — sem PR, merge direto
3. `Closes PDL-XX` no commit fecha automaticamente no Linear
4. Vercel/Railway: deploy é automático após push no main
5. VPS: sempre rodar pull + restart após merge
6. Não fechar se usuário não confirmou que terminou
```

## Notas Relacionadas
[[Gestao-Projetos/Start Issue]] · [[Gestao-Projetos/Gestao Atividades Projeto]]
