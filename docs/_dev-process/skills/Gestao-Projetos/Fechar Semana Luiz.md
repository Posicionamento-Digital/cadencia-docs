---
date: 2026-05-14
tags: [skill, gestao, linear, luiz, semana, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Fechar Semana Luiz

Fim de semana — resumo do que Luiz entregou, o que está em andamento e o que está atrasado. Útil para Felipe acompanhar a produção do time.

## Quando usar
"/fechar-semana-luiz", "resumo da semana do Luiz", "o que o Luiz entregou", "fechamento semanal".

---

## Conteúdo da Skill

```markdown
---
name: fechar-semana-luiz
description: Fim de semana — resumo do que Luiz entregou, em andamento e atrasado. Util para Felipe.
---

# /fechar-semana-luiz

## Quando ativar
- "/fechar-semana-luiz", "resumo da semana do Luiz", "o que o Luiz entregou", "fechamento semanal"

## Implementação

```python
import subprocess, json, os
from datetime import datetime, timedelta

def get_token():
    try:
        for line in open('/root/.claude/.env'):
            if line.startswith('LINEAR_API_TOKEN='):
                return line.strip().split('=',1)[1]
    except: pass
    return os.environ.get('LINEAR_API_TOKEN','')

TOKEN = get_token()
LUIZ_ID = "0085bb23-2b19-49ba-8179-8f41d499d969"

hoje = datetime.now().date()
segunda = hoje - timedelta(days=hoje.weekday())
inicio_semana = segunda.strftime('%Y-%m-%dT00:00:00.000Z')

# IMPORTANTE: branchName (nao gitBranchName), sem orderBy: priority
QUERY = f"""{{
  completadas: issues(filter: {{
    assignee: {{ id: {{ eq: "{LUIZ_ID}" }} }}
    state: {{ type: {{ eq: "completed" }} }}
    completedAt: {{ gte: "{inicio_semana}" }}
  }}, first: 50) {{ nodes {{ identifier title project {{ name }} completedAt }} }}

  abertas: issues(filter: {{
    assignee: {{ id: {{ eq: "{LUIZ_ID}" }} }}
    state: {{ type: {{ nin: ["completed","cancelled"] }} }}
  }}, first: 50) {{ nodes {{
    identifier title priority dueDate
    state {{ name type }}
    project {{ name }}
    labels {{ nodes {{ name }} }}
  }} }}
}}"""

r = subprocess.run(['curl','-s','-X','POST','https://api.linear.app/graphql',
    '-H', f'Authorization: {TOKEN}', '-H', 'Content-Type: application/json',
    '-d', json.dumps({'query': QUERY})
], capture_output=True)

data = json.loads(r.stdout)['data']
completadas = data['completadas']['nodes']
abertas = data['abertas']['nodes']

hoje_str = str(hoje)
atrasadas = [i for i in abertas if i.get('dueDate') and i['dueDate'] < hoje_str]
em_andamento = [i for i in abertas if i.get('state',{}).get('type')=='started']
aguardando = [i for i in abertas if any(l['name']=='aguardando-felipe' for l in i.get('labels',{}).get('nodes',[]))]

print(f"SEMANA {segunda.strftime('%d/%m')} a {hoje.strftime('%d/%m/%Y')} — Luiz\n")

print(f"ENTREGUE ({len(completadas)})")
for i in completadas:
    proj = i.get('project',{}).get('name','?') if i.get('project') else '?'
    print(f"  {i['identifier']:7} | {i['title'][:45]} | {proj}")

print(f"\nEM ANDAMENTO ({len(em_andamento)})")
for i in em_andamento:
    print(f"  {i['identifier']:7} | {i['title'][:45]} | vence {i.get('dueDate','?')}")

if atrasadas:
    print(f"\nATRASADO ({len(atrasadas)})")
    for i in atrasadas:
        bloq = ' [aguardando-felipe]' if any(l['name']=='aguardando-felipe' for l in i.get('labels',{}).get('nodes',[])) else ''
        print(f"  {i['identifier']:7} | {i['title'][:45]}{bloq}")

if aguardando:
    print(f"\nAGUARDANDO FELIPE ({len(aguardando)})")
    for i in aguardando:
        print(f"  {i['identifier']:7} | {i['title'][:45]}")

print(f"\nRESUMO: {len(completadas)} entregues | {len(em_andamento)} em andamento | {len(atrasadas)} atrasadas")
```

## Regras
1. `aguardando-felipe` = não conta como falha do Luiz
2. `branchName` (não `gitBranchName`)
3. `orderBy: priority` não existe — não usar
4. LUIZ_ID fixo: `0085bb23-2b19-49ba-8179-8f41d499d969`
```

## Notas Relacionadas
[[Gestao-Projetos/Issue Semana]] · [[Gestao-Projetos/Daily Luiz]] · [[Gestao-Projetos/Ver Dia Luiz]] · [[Stamper-Operacionais/Fechar Semana]]
