---
date: 2026-05-14
tags: [skill, reuniao, fireflies, obsidian, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Busca Reunioes

Busca transcrições de reuniões via Fireflies API, carrega conteúdo completo e cria nota no Obsidian (vault Time PD / pasta Reuniões) com resumo, link Fireflies e wikilinks. Ponto de entrada obrigatório para acesso a transcrições.

## Quando usar
"reunião com [cliente]", "transcrição de [nome]", "busca a transcrição", "acessa a reunião de [data]", "o que ficou da reunião com X". Sempre ANTES de análise, extração de tarefas ou resumo de reunião.

---

## Conteúdo da Skill

```markdown
---
name: busca-reunioes
description: Busca transcrições de reuniões via Fireflies API, carrega o conteúdo completo e cria nota estruturada no Obsidian (vault Time PD / pasta Reuniões) com resumo, link Fireflies e [[wikilinks]] para notas relacionadas.
---

# busca-reunioes

## Fontes

- **Transcrições:** Fireflies API (GraphQL)
- **Credencial:** `op item get "Fireflies - API" --vault "Serviços & Tools" --fields credencial --reveal`
- **Endpoint:** `https://api.fireflies.ai/graphql`
- **Nota de saída:** Vault `Time PD` → pasta `Reuniões/`
- **Vault path:** `C:\Users\felip\OneDrive\Documentos\Time PD\Reuniões\`

---

## Fluxo de Execução

### 1. Obter credencial Fireflies

```python
import subprocess
API_KEY = subprocess.check_output([
    'op', 'item', 'get', 'Fireflies - API',
    '--vault', 'Serviços & Tools',
    '--fields', 'credencial', '--reveal'
]).decode().strip()
```

### 2. Identificar o que buscar

- **Nome/cliente mencionado** → filtrar por `title` ou `participants` na resposta
- **Data mencionada** → converter para timestamp ms e filtrar por `date`
- **Sem especificação** → listar as 5 reuniões mais recentes (`limit: 5`)

### 3. Listar reuniões no Fireflies

```python
import subprocess, json

def fireflies_query(api_key, query):
    body = json.dumps({'query': query})
    cmd = [
        'curl', '-s', '-X', 'POST', 'https://api.fireflies.ai/graphql',
        '-H', f'Authorization: Bearer {api_key}',
        '-H', 'Content-Type: application/json',
        '-d', body
    ]
    r = subprocess.run(cmd, capture_output=True)
    return json.loads(r.stdout.decode('utf-8', errors='replace'))

LIST_QUERY = '''
{
  transcripts(limit: 10) {
    id
    title
    date
    duration
    transcript_url
    participants
  }
}
'''
result = fireflies_query(API_KEY, LIST_QUERY)
meetings = result['data']['transcripts']
```

- Se múltiplos resultados: listar opções com título + data formatada e pedir confirmação
- Se apenas 1 resultado óbvio: prosseguir diretamente

### 4. Carregar transcrição completa

```python
TRANSCRIPT_QUERY = '''
{
  transcript(id: "%s") {
    id
    title
    date
    duration
    transcript_url
    participants
    summary {
      keywords
      action_items
      outline
      shorthand_bullet
      overview
      bullet_gist
      gist
      short_summary
    }
    sentences {
      text
      speaker_name
      start_time
    }
  }
}
''' % meeting_id

full = fireflies_query(API_KEY, TRANSCRIPT_QUERY)['data']['transcript']
```

### 5. Gerar resumo da reunião

Com base em `summary` (se disponível do Fireflies) e `sentences`, produzir:
- **Resumo executivo** (3–5 bullets com o que foi discutido e decidido)
- **Participantes** (da lista `participants`)
- **Action items** (de `summary.action_items` ou extraídos do texto)

Se `summary` vier vazio, gerar a partir das `sentences`.

### 6. Identificar notas relacionadas no vault Time PD

```python
import os

VAULT_PATH = r'C:\Users\felip\OneDrive\Documentos\Time PD'

ROOTS_LINKÁVEIS = ['Projetos', 'Time', 'Incidentes', 'Processos', 'Infra', 'Prompts']

meeting_text = (
    full['title'] + ' ' +
    ' '.join(full.get('participants', [])) + ' ' +
    ' '.join([s['text'] for s in (full.get('sentences') or [])])
).lower()

related_notes = []
seen = set()

for root_folder in ROOTS_LINKÁVEIS:
    root_path = os.path.join(VAULT_PATH, root_folder)
    if not os.path.isdir(root_path):
        continue
    for entry in os.scandir(root_path):
        if entry.is_dir() and entry.name not in seen:
            name = entry.name
            if len(name) > 3 and name.lower() in meeting_text:
                related_notes.append(name)
                seen.add(name)
```

### 7. Classificar a reunião em subcategoria

| Categoria | Sinais no título/conteúdo |
|---|---|
| `Planejamento` | daily, check-in, planejamento, sprint, semana, review semanal |
| `Clientes` | nome de cliente ativo (NSkin, H&Co, GCI, etc.), acompanhamento |
| `Comercial` | diagnóstico, proposta, lead, prospect, vendas, call de vendas |
| `Time` | nome de membro do time atual ou ex-membro, 1:1 |
| `Produto` | Cadencia, OpenClaw, feature, roadmap, produto, dev, release |
| `Parceiros` | parceiro, fornecedor, colaboração externa |
| `Suporte & Manutenção` | suporte, bug cliente, manutenção, incidente, correção |
| `Operacional` | financeiro, jurídico, admin, infra, contrato |

Regra de desempate: preferir na ordem acima.

### 8. Criar nota no vault (escrita direta no filesystem)

**Formato do arquivo:** `YYYY-MM-DD - {título}.md`  
**Subpasta:** categoria classificada no passo anterior

```python
from datetime import datetime

date_str = datetime.fromtimestamp(full['date'] / 1000).strftime('%Y-%m-%d')
safe_title = full['title'].replace('/', '-').replace(':', '-')
filename = f"{date_str} - {safe_title}.md"
note_path = os.path.join(VAULT_PATH, 'Reuniões', categoria, filename)

note_content = f"""# {full['title']}

**Data:** {date_str}
**Duração:** {duration_min} min
**Participantes:** {participants_str}
**Fireflies:** [{full['title']}]({full['transcript_url']})

---

## Resumo

{resumo_executivo}

---

## Action Items

{action_items}

---

## Notas relacionadas

{wikilinks_block}

---

#reuniao #{date_str[:7].replace('-', '/')}
"""

os.makedirs(os.path.dirname(note_path), exist_ok=True)
with open(note_path, 'w', encoding='utf-8') as f:
    f.write(note_content)
```

### 9. Confirmar e entregar

Após criar a nota, informar:
- Título + data da reunião
- Caminho da nota criada no vault
- Wikilinks adicionados
- Link direto no Fireflies

Em seguida, executar o que foi pedido (análise adicional, extração de tarefas, etc.).

---

## Tratamento de erros

| Situação | Ação |
|---|---|
| `summary` vazio no Fireflies | Gerar resumo a partir das `sentences` diretamente |
| Nenhuma reunião encontrada | Informar e pedir que Felipe verifique o nome/data |
| Múltiplos resultados sem critério | Listar 5 mais recentes com data e pedir escolha |
| Erro de autenticação na API | Verificar se a key no 1Password está correta |
| Nota já existe no vault | Sobrescrever e avisar Felipe |

---

## Notas sobre o vault Time PD

- **Vault path:** `C:\Users\felip\OneDrive\Documentos\Time PD`
- **Pasta de reuniões:** `Reuniões\`
- **Estrutura atual do vault:** `Projetos/`, `Time/`, `Processos/`, `Infra/`, `Prompts/`, `Incidentes/`
- Escrita direta no filesystem — Obsidian sincroniza automaticamente via LiveSync
```

## Notas Relacionadas
[[Reunioes-Docs/Ata Reuniao]] · [[Reunioes-Docs/Documentar]]
