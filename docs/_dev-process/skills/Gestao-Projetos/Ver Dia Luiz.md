---
date: 2026-05-14
tags: [skill, gestao, linear, github, luiz, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---


# Ver Dia Luiz

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


O que Luiz fez hoje — commits por repositório e movimentações de issues no Linear.

## Quando usar
"/ver-dia-luiz" (hoje), "/ver-dia-luiz 2026-05-12" (data específica), "o que o Luiz fez hoje", "resumo do Luiz".

---

## Conteúdo da Skill

```markdown
---


name: ver-dia-luiz
description: >
  O que Luiz fez hoje — commits por repo e movimentações de issues no Linear.
  Uso: /ver-dia-luiz (hoje) ou /ver-dia-luiz 2026-05-12 (data específica).
---

# /ver-dia-luiz

## Quando ativar

- "o que o Luiz fez hoje", "me mostra o dia do Luiz", "resumo do Luiz"
- `/ver-dia-luiz` — dia atual
- `/ver-dia-luiz 2026-05-12` — data específica

---



## Configuração necessária

`LINEAR_API_TOKEN` em `~/.claude/.env`

---

## Passo 1 — Definir data e credenciais

```python
import subprocess, json, os, datetime, platform, sys

ARGS = sys.argv[1] if len(sys.argv) > 1 else None
TARGET_DATE = ARGS if ARGS else datetime.date.today().isoformat()

IS_WINDOWS = platform.system() == 'Windows'

def get_token():
    env_path = r'C:\Users\felip\.claude\.env' if IS_WINDOWS else '/root/.claude/.env'
    try:
        for line in open(env_path):
            if line.startswith('LINEAR_API_TOKEN='):
                return line.strip().split('=', 1)[1]
    except: pass
    return os.environ.get('LINEAR_API_TOKEN', '')

TOKEN = get_token()
LUIZ_GH = 'luizsidiao'
LUIZ_LINEAR_EMAIL = 'luiz@cadencia.ia.br'
REPOS = [
    'Posicionamento-Digital/gci-go-whatsapp',
    'Posicionamento-Digital/cadencia-app',
    'Posicionamento-Digital/ecuro-mcp',
]

GH_TOKEN = subprocess.check_output('gh auth token', shell=True, text=True).strip()
```

---



## Passo 2 — Commits do Luiz no GitHub

```python
def get_commits(repo, date):
    since = f"{date}T00:00:00Z"
    until = f"{date}T23:59:59Z"
    cmd = [
        'curl', '-s',
        f'https://api.github.com/repos/{repo}/commits?author={LUIZ_GH}&since={since}&until={until}&per_page=30',
        '-H', f'Authorization: token {GH_TOKEN}',
        '-H', 'Accept: application/vnd.github.v3+json'
    ]
    r = subprocess.run(cmd, capture_output=True)
    try:
        commits = json.loads(r.stdout)
        if isinstance(commits, list):
            return [{
                'sha': c['sha'][:7],
                'msg': c['commit']['message'].split('\n')[0],
                'time': c['commit']['author']['date'][11:16]
            } for c in commits]
        return []
    except:
        return []
```

---

## Passo 3 — Issues movimentadas no Linear

```python
QUERY = f"""
{{
  issues(filter: {{
    assignee: {{ email: {{ eq: "{LUIZ_LINEAR_EMAIL}" }} }}
    updatedAt: {{ gte: "{TARGET_DATE}T00:00:00.000Z" }}
  }}, first: 30) {{
    nodes {{
      identifier title
      state {{ name type }}
      updatedAt
      project {{ name }}
    }}
  }}
}}
"""
```

---



## Passo 4 — Formatar e exibir

```
📅 Luiz — {TARGET_DATE}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 COMMITS ({total_commits})
──────────────────
gci-go-whatsapp:
  14:32  a3f9c1e  fix(pipeline): corrigir debounce em mensagens simultâneas
  15:10  b72d3aa  test(pipeline): cobertura de sendlock

cadencia-app:
  (nenhum)

📋 ISSUES LINEAR
──────────────────
✅ Concluídas hoje:
  PDL-58  Validação: GHL + Stevo + Webhook + Supabase

🔄 Em andamento:
  PDL-61  Agentes base: AgentResult + bot_worker + tools

📌 Outras movimentações:
  PDL-60  Recriar Middleware eCuro  →  In Review
```

Se nenhum commit e nenhuma issue movimentada:
```
📅 Luiz — {TARGET_DATE}
Nenhuma atividade registrada no GitHub ou Linear hoje.
```

---

## Regras

1. Hora dos commits exibida no formato HH:MM (UTC — não converter)
2. Mostrar apenas repos com atividade; omitir os vazios
3. Não mostrar issues que não foram tocadas hoje
4. Se data não passada como argumento: usar `datetime.date.today()`
```

## Notas Relacionadas
[[Gestao-Projetos/Daily Luiz]] · [[Gestao-Projetos/Fechar Semana Luiz]]
