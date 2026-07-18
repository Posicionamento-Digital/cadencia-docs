---
date: 2026-05-14
tags: [skill, gestao, linear, luiz, daily, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Daily Luiz

Abre a daily com dev externo — mostra o que está em andamento, planejado para hoje (por prioridade), bloqueios e overdue. Formato compacto para leitura rápida.

## Quando usar
"abre a daily", "prepara a daily do Luiz", "daily de hoje", "/daily-luiz". Antes ou durante a call diária com Luiz.

---

## Conteúdo da Skill

```markdown
---
name: daily-luiz
description: >
  Abre a daily com dev externo — mostra o que está em andamento, o que está planejado
  para hoje (por prioridade), bloqueios e overdue. Formato compacto para leitura rápida.
  Uso: /daily-luiz
---

# /daily-luiz

## Quando ativar

- "abre a daily", "prepara a daily do Luiz", "daily de hoje", "/daily-luiz"
- Antes ou durante a call diária com dev externo

---

## Configuração necessária

`LINEAR_API_TOKEN` em `~/.claude/.env`

---

## Passo 1 — Carregar token e buscar issues

```python
import subprocess, json, os, datetime, platform

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
TODAY = datetime.date.today().isoformat()
LUIZ_EMAIL = 'luiz@cadencia.ia.br'

QUERY = f"""
{{
  issues(filter: {{
    assignee: {{ email: {{ eq: "{LUIZ_EMAIL}" }} }}
    state: {{ type: {{ nin: ["completed", "cancelled"] }} }}
  }}, first: 50) {{
    nodes {{
      id identifier title priority dueDate
      state {{ name type }}
      project {{ name }}
      labels {{ nodes {{ name }} }}
      branchName
    }}
  }}
}}
"""
```

---

## Passo 2 — Classificar issues

```python
in_progress = [i for i in issues_sorted if i['state']['type'] == 'started']
bloqueadas  = [i for i in issues_sorted if any(l['name'] == 'bloqueado' for l in i['labels']['nodes'])]
overdue     = [i for i in issues_sorted if i.get('dueDate') and i['dueDate'] < TODAY and i['state']['type'] != 'started']
todo        = [i for i in issues_sorted
               if i['state']['type'] == 'unstarted'
               and i not in bloqueadas
               and i not in overdue]

PRI = {1: 'URGENT', 2: 'HIGH', 3: 'MED', 4: 'LOW', 0: '-'}
```

---

## Passo 3 — Formatar saída

```
🗓️ Daily Luiz — {TODAY}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 EM ANDAMENTO ({len(in_progress)})
  PDL-61  [HIGH]  Agentes base: AgentResult + bot_worker + tools  (Lara Reconstrução)
  PDL-60  [HIGH]  Recriar Middleware eCuro  (Lara Reconstrução)

📋 BACKLOG / TODO ({len(todo)}) — próximas por prioridade
  PDL-62  [HIGH]  Lara agent — agendamento e consulta eCuro direto
  PDL-63  [HIGH]  Agente Humanizador

🚨 ATRASADAS ({len(overdue)})
  PDL-7   [URGENT]  Corrigir Ingress Tunnel CF → localhost:90  📅2026-05-11

⛔ BLOQUEADAS ({len(bloqueadas)})
  (nenhuma)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Em andamento: {len(in_progress)} | Todo: {len(todo)} | Atrasadas: {len(overdue)} | Bloqueadas: {len(bloqueadas)}
```

---

## Passo 4 — Perguntas sugeridas para a daily

Ao final, exibir:

```
💬 Perguntas para a call:
  1. O que vai entregar hoje?
  2. Tem algum bloqueio técnico?
  3. Precisa de revisão ou decisão do Felipe em algo?
```

---

## Regras

1. Mostrar no máximo 5 issues em "Todo" — as de maior prioridade
2. Se não há issues em andamento: destacar com aviso "⚠️ Nada em andamento"
3. Bloqueadas sempre aparecem, mesmo que sejam também todo/overdue
4. Prioridade: 1=URGENT 2=HIGH 3=MED 4=LOW 0=-
5. Não listar issues concluídas ou canceladas
```

## Notas Relacionadas
[[Gestao-Projetos/Ver Dia Luiz]] · [[Gestao-Projetos/Issue Semana]] · [[Gestao-Projetos/Start Issue]]
