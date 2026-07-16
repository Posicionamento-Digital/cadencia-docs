---
date: 2026-05-14
tags: [skill, gestao, linear, github, obsidian, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

# Gestao Atividades Projeto

Cria e gerencia issues no Linear — extrai tarefas de conversas, cria issues detalhadas, vincula ao projeto/cycle correto, atribui responsáveis, cria branch no GitHub, verifica espelhamento na VPS e documenta no Obsidian Time PD. Substitui o fluxo anterior do Notion.

## Quando usar
"cria atividades pro projeto X", "cria issue pra [tarefa]", "registra essas tarefas no linear", "cria tasks dessa conversa pro Luiz", "/gestao-atividades".

---

## Conteúdo da Skill

```markdown
---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

name: gestao-atividades-projeto
description: >
  Cria e gerencia issues de projetos no Linear — extrai tarefas de conversas ou
  instruções do Felipe, cria issues com descrição detalhada, vincula ao projeto
  e cycle (sprint) corretos, atribui responsáveis e prazos, cria branch no GitHub
  automaticamente, verifica se o repo está espelhado na VPS e documenta o projeto
  no Obsidian (vault Time PD). Substitui completamente o fluxo anterior baseado
  em Notion.
---

# /gestao-atividades-projeto

Cria issues no Linear com tudo que o Luiz precisa pra trabalhar na VPS sem depender de explicação verbal.

## Quando ativar

- "cria atividades pro projeto X"
- "cria issue pra [tarefa]"
- "registra essas tarefas no linear"
- "coloca isso como issue do [projeto/repo]"
- "cria tasks dessa conversa pro Luiz"
- "/gestao-atividades"

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## Configuração fixa

| Recurso | Valor |
|---|---|
| Linear — Team | Posicionamento Digital (`3d9699c8-ee89-466d-804d-8237041080d1`) |
| Linear — Felipe (user ID) | `6feb76c7-f8f5-4d76-b1bc-d58496460cc7` |
| Linear — Luiz (user ID) | `0085bb23-2b19-49ba-8179-8f41d499d969` |
| Linear — Cycle W1 (18-25/05) | `ee8e4dd7-fc2c-4dc8-b281-7dbd06b86bba` |
| VPS IP | `72.60.4.71` |
| VPS SSH key | `~/.ssh/hostinger_pd` |
| GitHub PAT (1Password) | vault `Serviços & Tools` → item `Git Hub - ClaudeCode_Skill - Repo_VPS` → campo `credencial` |
| Obsidian vault Time PD | `C:\Users\felip\OneDrive\Documentos\Time PD` |

### Projetos conhecidos e repos

| Projeto Linear | Repo GitHub | Path na VPS |
|---|---|---|
| Cadência — App | `felipeluissalgueiro/cadencia-app` | `/root/cadencia-app` |
| GCI-GO | `Posicionamento-Digital/gci-go-whatsapp` | `/root/gci-go-whatsapp` |
| ecuro-mcp | `Posicionamento-Digital/ecuro-mcp` | `/root/ecuro-mcp` |
| Pipeline-Conteudo | (VPS direto, sem repo GitHub) | `/root/pipeline-conteudo` |

---

## Passo 1 — Identificar o projeto

Perguntar ao Felipe: **"Para qual projeto?"** (se não ficou claro da conversa).

Buscar projeto no Linear:
```
mcp__linear-server__list_projects  team="Posicionamento Digital"
```

**Se projeto existe:** usar o ID. Não recriar.
**Se NÃO existe:** criar projeto no Linear E criar pasta no Obsidian (ver Passo 6).

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## Passo 2 — Identificar cycle (sprint) atual

```
mcp__linear-server__list_cycles  teamId="3d9699c8-ee89-466d-804d-8237041080d1"  type="current"
```

- **Cycle ativo encontrado:** usar o ID.
- **Nenhum cycle ativo:** avisar Felipe.

---

## Passo 3 — Extrair issues da conversa

Da instrução do Felipe, extrair para cada issue:

| Campo | Descrição | Obrigatório |
|---|---|---|
| Título | Ação clara: verbo + objeto | Sim |
| Responsável | Luiz ou Felipe | Sim |
| Prioridade | Urgent / High / Medium / Low | Sim |
| Label(s) | `trilha:sprint` / `trilha:manutencao` / `trilha:rotina` + `repo:[nome]` | Sim |
| Prazo (due date) | Data limite | Sim |
| Contexto | Por que existe essa issue | Sim |
| O que fazer | Passo a passo | Sim |
| Onde mexer | Arquivos/funções específicas | Quando técnico |
| Critério de aceite | Checkboxes verificáveis | Sim |

**Labels disponíveis:** `trilha:rotina`, `trilha:manutencao`, `trilha:sprint`, `bloqueado`, `aguardando-felipe`

**Se Felipe não especificar prazo:** sugerir por prioridade: Urgent = 2 dias, High = 5 dias, Medium = 7 dias, Low = 14 dias.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## Passo 4 — Criar issues no Linear

```
mcp__linear-server__save_issue
  title: "[título]"
  team: "Posicionamento Digital"
  project: "[ID do projeto]"
  cycle: "[ID do cycle ativo, se houver]"
  assignee: "[user ID]"
  priority: [1-4]
  dueDate: "YYYY-MM-DD"
  labels: ["[label ID]", ...]
  description: |
    (ver template abaixo)
```

### Template de descrição da issue (OBRIGATÓRIO — detalhado)

```markdown
## Contexto

[Situação atual + impacto + exemplo concreto. 2-3 parágrafos.
Quem lê deve entender POR QUE essa issue existe sem ter participado da conversa.]

---

## O que precisa ser feito

1. **[Passo 1]** — detalhe
2. **[Passo 2]** — detalhe
3. **[Passo 3]** — detalhe

**Onde mexer:**
- `[arquivo/função/rota]`

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## Critério de aceite

- [ ] [Critério verificável 1]
- [ ] [Critério verificável 2]

---

## Referências

- Branch: `[gitBranchName gerado pelo Linear]`
- Origem: [conversa/reunião/data]
```

**REGRA:** Descrição com menos de 3 seções preenchidas é inútil pra Luiz. Não criar assim.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## Passo 5 — Criar branches no GitHub

**Só para issues atribuídas ao Luiz.**

```bash
OP="C:\Users\felip\AppData\Local\Microsoft\WinGet\Packages\AgileBits.1Password.CLI_Microsoft.Winget.Source_8wekyb3d8bbwe\op.exe"
PAT=$($OP item get "Git Hub - ClaudeCode_Skill - Repo_VPS" --vault "Serviços & Tools" --field credencial --reveal)
```

Para cada issue do Luiz:

**5a. Pegar SHA do branch base (main):**
```bash
curl -s -H "Authorization: Bearer $PAT" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/[owner]/[repo]/git/ref/heads/main" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['object']['sha'])"
```

**5b. Criar branch:**
```bash
BRANCH_NAME="[gitBranchName da issue]"

curl -s -X POST \
  -H "Authorization: Bearer $PAT" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/[owner]/[repo]/git/refs" \
  -d "{\"ref\":\"refs/heads/$BRANCH_NAME\",\"sha\":\"$SHA\"}"
```

- `201` → branch criada.
- `422` "Reference already exists" → branch já existe. OK.
- Outro erro → mostrar e continuar para próxima issue.

---

## Passo 6 — Verificar repo na VPS

**Só para issues atribuídas ao Luiz.**

Verificar se deploy key existe:
```bash
ssh -i ~/.ssh/hostinger_pd root@72.60.4.71 \
  "test -f /root/.ssh/[repo]_deploy && echo EXISTE || echo NAO_EXISTE"
```

- **EXISTE:** Verificar clone atualizado.
- **NAO_EXISTE:** Chamar `/espelhar-repo-vps`.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## Passo 7 — Obsidian: criar/atualizar pasta do projeto

**Se o projeto É NOVO:** criar estrutura de pastas no vault Time PD.
**Se o projeto JÁ EXISTIA:** não tocar no Obsidian.

---

## Passo 8 — Relatório final

```
✅ [N] issues criadas no projeto "[Nome]" — Cycle [nome ou "sem cycle"]

| Issue | Título | Responsável | Prazo | Prioridade | Branch |
|---|---|---|---|---|---|
| PDL-10 | ... | Luiz | 17/05 | High | luiz/pdl-10-... |

🔗 Projeto Linear: [URL]

🖥️ VPS:
- [repo]: deploy key ✅ | clone ✅ | branches disponíveis pra checkout

📁 Obsidian: [criado/já existia]
```

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## Regras

1. **NUNCA criar issue sem descrição completa.** Issue com título apenas é inútil pra Luiz.
2. **Sempre associar ao projeto e ao cycle ativo** (se existir).
3. **Sempre criar branch no GitHub** para issues do Luiz antes de reportar.
4. **Verificar VPS antes de finalizar** — Luiz não pode trabalhar se o repo não estiver lá.
5. **Se Obsidian falhar:** avisar mas não abortar.
6. **Se a issue for do Felipe:** não criar branch, não verificar VPS.
7. **Labels de repo são obrigatórias** para issues técnicas.
```

## Notas Relacionadas
[[Gestao-Projetos/Start Issue]] · [[Gestao-Projetos/Close Issue]] · [[Infra-GHL-Financeiro/Espelhar Repo VPS]]
