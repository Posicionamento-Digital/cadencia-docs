---
date: 2026-05-14
tags: [skill, gestao, linear, github, dev, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---


# Start Issue

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


Lista issues do Linear atribuídas no ciclo atual, faz checkout da branch correspondente e marca como In Progress.

## Quando usar
`/start-issue` (lista issues), `/start-issue PDL-11` (vai direto para issue específica), "qual minha próxima issue", "começa a PDL-11".

---

## Conteúdo da Skill

```markdown
---


name: start-issue
description: >
  Lista issues do Linear atribuídas ao usuário no ciclo atual, faz checkout da
  branch correspondente no repo correto e marca a issue como In Progress.
  Uso: /start-issue (lista) ou /start-issue PDL-11 (vai direto).
---

# /start-issue

## Quando ativar

- `start-issue` — lista issues e deixa usuário escolher
- `start-issue PDL-11` — vai direto para a issue
- "qual minha próxima issue", "o que eu faço hoje", "começa a PDL-11"

---



## Configuração necessária

`LINEAR_API_TOKEN` em `~/.claude/.env`:
- **VPS (Linux):** `/root/.claude/.env`
- **Windows local:** `C:\Users\felip\.claude\.env`

---

## Mapa de repos — detecção automática de ambiente

```python
import platform
IS_WINDOWS = platform.system() == 'Windows'

REPO_MAP = {
    'repo:cadencia-app': (
        r'C:\Users\felip\OneDrive\Documentos\ClaudeCode\Hub Projetos\Projetos BMAD\Cadencia'
        if IS_WINDOWS else '/root/cadencia-app'
    ),
    'repo:gci-go-whatsapp': (
        r'C:\Users\felip\OneDrive\Documentos\ClaudeCode\Hub Projetos\_repos\gci-go-whatsapp'
        if IS_WINDOWS else '/root/gci-go-whatsapp'
    ),
    'repo:ecuro-mcp': (
        None  # não clonado localmente
        if IS_WINDOWS else '/root/ecuro-mcp'
    ),
    'repo:assessoria-imprensa': (
        r'C:\Users\felip\OneDrive\Documentos\ClaudeCode\Hub Projetos\Projetos BMAD\assessoria-imprensa'
        if IS_WINDOWS else '/root/assessoria-imprensa-cadencia'
    ),
}
```

---



## Passo 1 — Carregar token e buscar issues

```python
import subprocess, json, os, platform

IS_WINDOWS = platform.system() == 'Windows'

def get_token():
    env_path = (
        r'C:\Users\felip\.claude\.env'
        if IS_WINDOWS else '/root/.claude/.env'
    )
    try:
        for line in open(env_path):
            if line.startswith('LINEAR_API_TOKEN='):
                return line.strip().split('=',1)[1]
    except: pass
    return os.environ.get('LINEAR_API_TOKEN','')

TOKEN = get_token()
if not TOKEN:
    print("ERRO: LINEAR_API_TOKEN nao encontrado em ~/.claude/.env")
    exit(1)

QUERY = """
{
  viewer { id name }
  issues(filter: {
    assignee: { isMe: { eq: true } }
    state: { type: { nin: ["completed", "cancelled"] } }
  }, first: 20) {
    nodes {
      id identifier title priority dueDate
      state { id name type }
      project { name }
      branchName
      labels { nodes { name } }
    }
  }
}
"""
```

---

## Passo 2 — Apresentar lista

```
Issues atribuídas a [nome]:

#  | PDL    | Pri      | Título                                      | Prazo   | Repo
---|--------|----------|---------------------------------------------|---------|-------------
1  | PDL-47 | URGENT   | Corrigir duplicação agendamentos           | 18/05   | gci-go-whatsapp
2  | PDL-11 | HIGH     | Criar tabela ghl_stevo_instances           | 15/05   | cadencia-app

Qual começar? (número ou PDL-XX)
```

Prioridade: 1=URGENT 2=HIGH 3=MEDIUM 4=LOW

---



## Passo 3 — Detectar repo e branch

```python
labels = [l['name'] for l in issue['labels']['nodes']]
repo_path = next((REPO_MAP[l] for l in labels if l in REPO_MAP), None)
branch = issue.get('branchName', '')
```

---

## Passo 4 — Checkout da branch

```bash
cd [repo_path]
git fetch origin 2>&1 | tail -3
git checkout [branch] 2>&1 || git checkout -b [branch] 2>&1
git status
```

---



## Passo 5 — Marcar In Progress no Linear

Usar mutation GraphQL para atualizar o estado da issue para o primeiro estado do tipo "started".

---

## Passo 6 — Confirmar ao usuário

```
✅ Tudo pronto!

🎯 PDL-11: Criar tabela ghl_stevo_instances
📁 Repo:   C:\...\Cadencia  (ou /root/cadencia-app na VPS)
🌿 Branch: luiz/pdl-11-criar-tabela-...
📊 Status: In Progress (Linear atualizado)

Para fechar quando terminar:
  git add <arquivos>
  git commit -m "feat: criar tabela ghl_stevo_instances

Closes PDL-11"
  git push

Ou: /close-issue PDL-11
```

---



## Regras

1. Campo da branch na API é `branchName` (não `gitBranchName`)
2. `orderBy` só aceita `updatedAt` ou `createdAt` — ordenar por prioridade client-side
3. Nunca criar branch nova se já existe no remote
4. Sempre mostrar o comando de commit com `Closes PDL-XX`
5. Se `repo_path` for `None` (ex: ecuro-mcp no Windows) — avisar e usar cwd
```

## Notas Relacionadas
[[Gestao-Projetos/Close Issue]] · [[Gestao-Projetos/Gestao Atividades Projeto]] · [[Gestao-Projetos/Issue Semana]]
