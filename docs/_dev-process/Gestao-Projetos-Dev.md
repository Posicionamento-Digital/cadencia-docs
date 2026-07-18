---
date: 2026-05-14
tags: [processos, linear, github, claude-code, dev, luiz, ia, tecnologia, automacao]
moc: "[[MOC-Inbox]]"
---
# Gestão de Projetos de Desenvolvimento — Time PD

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.




Processo completo de como projetos de desenvolvimento são criados, acompanhados e entregues no time PD (Felipe + dev externo).

## Notas Relacionadas
[[Projetos/gci-go-whatsapp/README]] · [[Time/Luiz/README]]

---

## 1. Stack de gestão

| Ferramenta | Papel |
|---|---|
| **Linear** | Tracker de issues, projetos e ciclos (sprints) |
| **GitHub** (org `Posicionamento-Digital`) | Repositórios de código |
| **Claude Code** | Execução de tarefas de código + skills de gestão |
| **VPS Hostinger** `72.60.4.71` | Ambiente de desenvolvimento do dev externo |

---

## 2. Estrutura no Linear

### Workspace
`posicionamento-digital` — acesso via linear.app/posicionamento-digital

### Membros
- **Felipe** (`felipeluissalgueiro@gmail.com`) — cria projetos, define prioridades, revisa
- **Luiz** (`luiz@cadencia.ia.br`, `luizsidiao`) — implementa as issues

### Labels padrão

**Labels de epic** (agrupam issues por fase do projeto):
- `epic:infra-base` — Docker, Redis, Supabase, Webhook
- `epic:middleware-ecuro` — Middleware FastAPI eCuro
- `epic:integracoes` — GHL, Stevo, LLM client
- `epic:agentes` — Lara, Humanizador, pipeline
- `epic:unidades` — Bots por unidade
- `epic:jobs` — Jobs assíncronos
- `epic:hardening` — Testes E2E, deploy

**Labels de estado**:
- `bloqueado` — aguardando dependência externa
- `aguardando-felipe` — precisa de decisão ou recurso do Felipe

**Labels de trilha** (para issues da Rotina):
- `trilha:sprint`, `trilha:manutencao`, `trilha:rotina`

### Convenção de branch
```
luiz/pdl-XX-descricao-da-issue
```
Gerada automaticamente pelo Linear baseado no título da issue.

---

## 3. Ciclo de vida de uma issue

```
Felipe cria issue no Linear
        ↓
Luiz roda /start-issue PDL-XX
        ↓
Branch criada + issue → In Progress
        ↓
Luiz implementa + commita na branch
        ↓
Luiz roda /close-issue PDL-XX
        ↓
Merge na main + issue → Done
```

### Convenção de commit
```
tipo(escopo): descrição no imperativo

Closes PDL-XX

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

Tipos: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `revert`

---

## 4. Skills de gestão — Felipe

### `/gestao-atividades-projeto`
Cria issues no Linear a partir de uma conversa ou instrução. Vincula ao projeto, cycle e assignee corretos. Cria branch no GitHub automaticamente.

**Quando usar:** ao iniciar um novo projeto ou feature — deixa o escopo todo mapeado em issues antes de começar a codar.

### `/daily-luiz`
Roda antes ou durante a call diária. Mostra:
- Issues em andamento
- Backlog priorizado (top 5 por prioridade)
- Issues atrasadas
- Issues bloqueadas
- 3 perguntas sugeridas para a call

**Uso:** `/daily-luiz`

### `/ver-dia-luiz [data]`
Mostra o que dev externo fez num dia específico:
- Commits por repo (GitHub API)
- Issues movimentadas no Linear

**Uso:** `/ver-dia-luiz` (hoje) ou `/ver-dia-luiz 2026-05-12`

### `/fechar-semana-luiz`
Resumo semanal: o que entregou, o que está em andamento, o que atrasou.

**Uso:** sextas ou início de semana antes da review

---

## 5. Skills de gestão — dev externo (na VPS)

### `/start-issue [PDL-XX]`
1. Busca issues atribuídas ao dev externo no Linear
2. Apresenta lista por prioridade
3. dev externo escolhe qual começar
4. Cria branch `luiz/pdl-XX-descricao` no repo correto
5. Marca issue como **In Progress** no Linear

**Uso:** `/start-issue` (lista) ou `/start-issue PDL-58` (direto)

**Configuração necessária:** `LINEAR_API_TOKEN` em `/root/.claude/.env`

### `/close-issue [PDL-XX]`
1. Faz commit com `Closes PDL-XX`
2. Merge na main
3. Marca issue como **Done** no Linear
4. Dispara deploy conforme plataforma do projeto

**Uso:** `/close-issue PDL-58`

### `/claude-review`, `/gemini-review`
Code review automatizado antes de fechar uma issue.

---

## 6. Como criar um novo projeto

### Via skill (recomendado)
```
/gestao-atividades-projeto
```
Informa o projeto, descreve as features — a skill cria as issues, labels e vincula ao projeto no Linear.

### Manual (quando a skill já fez parte)
1. Criar projeto no Linear com nome + descrição
2. Criar labels de epic específicas do projeto
3. Criar issues com descrições detalhadas:
   - Objetivo
   - Escopo técnico (arquivos, interfaces)
   - Critério de aceite (checkboxes)
   - Referências (arquivos, docs, decisões)
4. Atribuir todas ao dev externo
5. Linkar o repo GitHub em cada issue

---

## 7. Ambiente de trabalho do dev externo

### Acesso VPS
```bash
ssh root@72.60.4.71
```
Chave: `~/.ssh/hostinger_gci_go`

### Repos disponíveis na VPS
| Repo | Path |
|---|---|
| `gci-go-whatsapp` | `/root/gci-go-whatsapp` |
| `cadencia-app` | `/root/cadencia-app` |
| `assessoria-imprensa-cadencia` | `/root/assessoria-imprensa-cadencia` |

### Fluxo de trabalho do dev externo
```bash
ssh root@72.60.4.71
cd /root/gci-go-whatsapp
claude   # abre Claude Code
# dentro do Claude Code:


/start-issue PDL-58
# ... implementa ...


/close-issue PDL-58
```

### Claude Code na VPS
- Binário: `/root/.local/bin/claude` (v2.1.140)
- PATH: `/root/.local/bin` adicionado ao `.bashrc`
- Token Linear: `/root/.claude/.env`
- Skills disponíveis: `start-issue`, `close-issue`, `gemini-review`, `claude-review`, `registrar-incidente`, etc.

---

## 8. REPO_MAP — repos por label

A skill `start-issue` usa labels para identificar o repo correto:

| Label | Windows (Felipe) | VPS (dev externo) |
|---|---|---|
| `repo:cadencia-app` | `...Projetos BMAD/Cadencia` | `/root/cadencia-app` |
| `repo:gci-go-whatsapp` | `..._repos/gci-go-whatsapp` | `/root/gci-go-whatsapp` |
| `repo:ecuro-mcp` | não clonado | `/root/ecuro-mcp` |
| `repo:assessoria-imprensa` | `...Projetos BMAD/assessoria-imprensa` | `/root/assessoria-imprensa-cadencia` |

---

## 9. Rotina semanal

| Momento | Quem | Skill |
|---|---|---|
| Início de semana | Felipe | `/issue-semana` — lista issues do ciclo atual |
| Diariamente | Felipe | `/daily-luiz` — antes da call |
| Fim do dia | Felipe | `/ver-dia-luiz` — o que dev externo fez |
| Fim de semana | Felipe | `/fechar-semana-luiz` — revisão semanal |

---

## 10. Onde achar documentação técnica dos projetos

| Projeto | Documentação |
|---|---|
| `gci-go-whatsapp` | `CLAUDE.md` + `docs/REFERENCE.md` + `docs/DECISOES.md` no repo |
| `cadencia-app` | `CLAUDE.md` no repo |
| Incidentes | `Hub Projetos/Incidentes/INDEX.md` |
| Credenciais | `1Password` (vaults: Hosts, Databases, Serviços & Tools) |

---

## 11. Checklist ao criar issues

- [ ] Título claro no imperativo (`Recriar`, `Implementar`, `Validar`)
- [ ] Label de epic correta
- [ ] Label `repo:X` para a skill `start-issue` funcionar
- [ ] Descrição com: Objetivo, Escopo técnico, Critério de aceite, Referências
- [ ] Atribuída ao dev externo
- [ ] Link para o repo GitHub na issue


---

## 12. Passo a passo — Cenários completos

### Cenário A: Iniciar um projeto novo

**Felipe faz:**

1. Abre Claude Code na pasta do projeto (ou na Rotina)
2. Roda:
   ```
   /gestao-atividades-projeto
   ```
3. Descreve o projeto e as features em linguagem natural
4. A skill cria as issues no Linear com descrições, labels e assignee
5. Revisa as issues criadas em linear.app — ajusta prioridade ou descrição se necessário
6. Avisa o dev externo que as issues estão prontas

**Resultado:** issues criadas, atribuídas, com label de repo e epic corretas.

---

### Cenário B: dev externo começa o dia de trabalho

**dev externo faz (na VPS):**

```bash
ssh root@72.60.4.71
cd /root/gci-go-whatsapp   # ou o repo da issue
claude
```

**Dentro do Claude Code:**

```
/start-issue
```

1. A skill lista todas as issues atribuídas ao dev externo por prioridade
2. dev externo digita o número ou o identificador (ex: `PDL-58`)
3. A skill:
   - Faz `git fetch` + `git checkout -b luiz/pdl-58-descricao`
   - Marca a issue como **In Progress** no Linear
4. dev externo começa a implementar

---

### Cenário C: dev externo implementa e commita

**Durante o trabalho:**

```bash
# Ver o que mudou


git status

# Adicionar arquivos específicos (nunca git add -A)


git add src/agents/lara.py tests/test_lara.py

# Commitar


git commit -m "feat(lara): implementar tool criar_agendamento direto

Closes PDL-58"

# Pushar a branch


git push origin luiz/pdl-58-validacao-ghl-stevo-webhook-supabase
```

**Opcionalmente antes do commit — rodar review:**
```
/claude-review
```
ou
```
/gemini-review
```

---

### Cenário D: dev externo fecha uma issue

**Dentro do Claude Code na VPS:**

```
/close-issue PDL-58
```

A skill:
1. Faz commit final com `Closes PDL-58` (se houver mudanças pendentes)
2. Merge da branch na `main`
3. Push para o GitHub
4. Marca a issue como **Done** no Linear

**Felipe vê no Linear:** issue aparece como Done automaticamente.

---

### Cenário E: Felipe acompanha o dia do dev externo

**Felipe faz (a qualquer hora):**

```
/ver-dia-luiz
```

Resultado: commits do dia por repo + issues movimentadas no Linear.

```
/ver-dia-luiz 2026-05-12
```

Para ver um dia específico.

---

### Cenário F: Felipe prepara a daily

**Felipe faz antes da call:**

```
/daily-luiz
```

Resultado:
- O que está **Em andamento** agora
- **Backlog** priorizado (próximas 5 issues)
- **Atrasadas** (dueDate vencido)
- **Bloqueadas** (label `bloqueado`)
- 3 perguntas sugeridas para a call

---

### Cenário G: Felipe cria uma issue avulsa (sem projeto)

**Felipe faz no Claude Code:**

```
/gestao-atividades-projeto PDL-99 fix bug duplicação agendamentos
```

Ou via Linear direto:
1. Acessa `linear.app/posicionamento-digital` (slug técnico legado do workspace)
2. Cria issue no time **Produto & Dev**
3. Define: título, descrição, prioridade, assignee (dev externo), label de repo e epic
4. Vincula ao projeto correto

**Checklist antes de salvar:**
- [ ] Label `repo:X` presente (necessário para `start-issue` funcionar)
- [ ] Atribuída ao dev externo
- [ ] Critério de aceite descrito

---

### Cenário H: Issue bloqueada (aguardando credencial, decisão, etc.)

**dev externo faz:**
1. Adiciona label `bloqueado` na issue via Linear
2. Comenta na issue o motivo (`aguardando tokens eCuro do Alex`)

**Felipe vê:**
- Na `/daily-luiz`: aparece na seção ⛔ BLOQUEADAS
- Na `/ver-dia-luiz`: aparece nas "outras movimentações"

**Quando desbloqueada:**
1. Felipe remove label `bloqueado`
2. Adiciona contexto necessário na issue (credencial, link, decisão)
3. Avisa dev externo

---

### Cenário I: Review semanal

**Felipe faz (sexta ou segunda):**

```
/fechar-semana-luiz
```

Resultado:
- O que dev externo entregou na semana
- O que está em andamento
- O que atrasou (com justificativa se houver)

---

### Cenário J: dev externo precisa de ajuda técnica

dev externo usa Claude Code diretamente na VPS:

```
/debug-polya    # debugging estruturado
/mp-diagnose    # diagnóstico de bug/regressão
/claude-review  # code review antes de commitar
```

Se precisar de decisão arquitetural → avisar Felipe antes de implementar.
