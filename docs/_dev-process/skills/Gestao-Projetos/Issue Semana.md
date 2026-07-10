---
date: 2026-05-14
tags: [skill, gestao, linear, semana, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Issue Semana

Inicio de semana — lista todas as issues do ciclo atual no Linear por prioridade e prazo.

## Quando usar
Segunda de manhã, "/issue-semana", "o que tenho essa semana", "planejamento da semana".

---

## Conteúdo da Skill

```markdown
---
name: issue-semana
description: Inicio de semana — lista todas as issues do ciclo atual por prioridade e prazo.
---

# /issue-semana

## Quando ativar
- Segunda de manhã, "/issue-semana", "o que tenho essa semana", "planejamento da semana"

## Implementação

```python
import subprocess, json, os
from datetime import datetime

def get_token():
    try:
        for line in open('/root/.claude/.env'):
            if line.startswith('LINEAR_API_TOKEN='):
                return line.strip().split('=',1)[1]
    except: pass
    return os.environ.get('LINEAR_API_TOKEN','')

TOKEN = get_token()

# IMPORTANTE: branchName (nao gitBranchName)
# IMPORTANTE: sem orderBy: priority — ordenar client-side
QUERY = """{ viewer { name } issues(filter: {
  assignee: { isMe: { eq: true } }
  state: { type: { nin: ["completed","cancelled"] } }
}, first: 50) { nodes {
  identifier title priority dueDate
  state { name type }
  project { name }
  branchName
  labels { nodes { name } }
} } }"""

r = subprocess.run(['curl','-s','-X','POST','https://api.linear.app/graphql',
    '-H', f'Authorization: {TOKEN}', '-H', 'Content-Type: application/json',
    '-d', json.dumps({'query': QUERY})
], capture_output=True)

data = json.loads(r.stdout)['data']
issues = sorted(data['issues']['nodes'], key=lambda x: x.get('priority') or 99)
hoje = datetime.now().date()

pri = {1:'URGENT',2:'HIGH',3:'MEDIUM',4:'LOW',0:'NONE'}
print(f"=== SEMANA {hoje.strftime('%d/%m')} — {data['viewer']['name']} ===\n")

for p, nome in [(1,'URGENT'),(2,'HIGH'),(3,'MEDIUM'),(4,'LOW')]:
    grupo = [i for i in issues if i.get('priority')==p]
    if not grupo:
        continue
    print(f"--- {nome} ---")
    for i in grupo:
        prazo = i.get('dueDate','?')
        if prazo and prazo != '?':
            from datetime import datetime as dt
            dias = (dt.strptime(prazo,'%Y-%m-%d').date() - hoje).days
            flag = '⚠️ ' if dias < 0 else ''
            prazo_str = f"{flag}{prazo[8:10]}/{prazo[5:7]} ({'+' if dias>=0 else ''}{dias}d)"
        else:
            prazo_str = 'sem prazo'
        proj = i.get('project',{}).get('name','?') if i.get('project') else '?'
        print(f"  {i['identifier']:7} | {i['title'][:42]:42} | {prazo_str:18} | {proj}")
    print()

vencidas = [i for i in issues if i.get('dueDate') and i['dueDate'] < str(hoje)]
if vencidas:
    print(f"⚠️  {len(vencidas)} issue(s) vencida(s) — prioridade máxima!")
print(f"\nTotal: {len(issues)} abertas | Para começar: /start-issue")
```

## Regras
1. `branchName` (não `gitBranchName`)
2. Ordenar por prioridade client-side — `orderBy: priority` não existe na API
3. Prazo em dias relativos (+3d, -1d)
4. Destacar vencidas com ⚠️
```

## Notas Relacionadas
[[Gestao-Projetos/Start Issue]] · [[Gestao-Projetos/Daily Luiz]] · [[Gestao-Projetos/Fechar Semana Luiz]]
