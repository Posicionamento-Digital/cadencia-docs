---
date: 2026-06-28
tags: [documentacao, projeto, skill, treinamento]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]"]
---
## Identidade
- **Tipo:** skill · gate de provisionamento · ciclo de vida cliente
- **Stack:** Markdown (skill spec) · `gh` CLI · git
- **Path no framework:** `times/cs/skills/ativar-cliente.md` §Bloco A.6
- **Path do template repo:** `times/produto/treinamentos/imersao-claude-code-30d/kit-template/`
- **Repo template GitHub:** `felipeluissalgueiro/cadencia-kit-template` (privado, `isTemplate: true`)
- **Status:** ativo · validado por smoke test 2026-06-28

## O que é

Extensão da skill `/ativar-cliente` (porta única do ciclo de vida cliente da Central de CS) que adiciona o **gate A.6** — provisionamento automático de repo GitHub `<slug>-kit` quando o produto contratado é `[5] Treinamento`. Casa com o produto "Treinamento Claude Code 30d" do CSE, ativado por aluno via `/ativar-cliente <Nome>`.

Sub-componentes acoplados:

- **`cadencia-kit-template`** (repo GitHub) — molde compartilhado dos 30d. 40 arquivos: 12 módulos de curso auto-estudo, 4 skills genéricas, 6 templates de projeto (CLAUDE.md, AGENTS.md, PRD, .gitignore, .env.example, opencode.json), 4 templates de issue S1-S4, biblioteca catalogada de 73 notas, FAQ com 21 perguntas, padrão Claude Code + OpenCode agnóstico.
- **Skill `/linear-e2e-test`** (`~/.claude/skills/linear-e2e-test/SKILL.md`) — enriquecida no mesmo dia com loop auto-fix Replit/Lucas Montano (asserts derivados do critério, `--max-fix-loops`, acumulador de bugs, exemplo concreto DEV-873).

## Para que serve

Eliminar a fricção manual de criar o repo de material do aluno toda vez que entra alguém novo no Treinamento 30d. Antes do A.6, a sequência era: Felipe entrava no GitHub web → "Use this template" → renomeava → clonava local → editava 9 placeholders à mão em README e CLAUDE.md → criava 4 issues uma por uma → convidava aluno → mandava WhatsApp. Estimado 15-20 min por aluno + risco de esquecer passos.

Com A.6: `/ativar-cliente Leonardo Alves` → wizard pergunta produto → responde `[5]` → gate A.6 dispara → repo provisionado + customizado + 4 issues + collaborator + WhatsApp em 1 confirmação textual.

## Como funciona

Gate condicional dentro do Bloco A do wizard:

```
/ativar-cliente <Nome>
  → Passo 0.6 pergunta produto
    → se resposta = [5] Treinamento → A.6 dispara
    → senão → A.6 aparece como [—] no dashboard, não pergunta nada
```

Sequência de 7 passos (idempotente, ver §"Idempotência" abaixo):

1. **Criar repo do template:** `gh repo create felipeluissalgueiro/<slug>-kit --private --template felipeluissalgueiro/cadencia-kit-template`
2. **Clone local:** `gh repo clone` em `Hub Projetos/<slug>-kit/`
3. **Substituir placeholders** dentro de seções específicas (lista exaustiva 9 placeholders no README + 9 no CLAUDE.md) com dados coletados nos Passos 0.x do wizard
4. **Convidar aluno** como collaborator do GitHub
5. **Criar labels** (`sessao`, `setup`, `construcao`, `integracao`, `entrega`) + **4 issues** GitHub S1-S4 com check de idempotência por título
6. **Commit + push** da customização
7. **Registrar link do repo** no CLAUDE.md do aluno dentro do framework (`times/produto/treinamentos/imersao-claude-code-30d/<slug>/CLAUDE.md`)

Daí o wizard segue normal pra A.5 (mensagem confirmação WhatsApp com link do repo + instrução pra ler `FAQ.md` + `INSTALACAO.md` antes da S1).

## Quando usar / Quando NÃO usar

**Usar quando:** aluno fechou contrato de Treinamento 30d (Eliseu, Vayne, Leonardo, próximos). Wizard `/ativar-cliente` detecta sozinho via produto = `[5]`.

**NÃO usar quando:**
- Produto contratado é Bundle/Lite/Consultoria/MVP customizado → gate A.6 aparece `[—]` no dashboard e não dispara
- Aluno ainda não tem GitHub user definido → responder `[2]` na pergunta do A.6 (adia, pasta framework registra pendência em `[L2]`)
- Felipe quer provisionar manual por algum motivo → responder `[3]` (pular)

## Decisões (ADRs)

- **Repo PRIVADO + collaborator individual** (não org pública) — material é exclusivo do aluno, contém adaptações pessoais.
- **Template GitHub nativo, não fork** — `gh repo create --template` desacopla histórico do molde do histórico do aluno, deixa o repo derivado limpo.
- **Mantém `PROVISIONAMENTO.md` no framework, fora do template** — doc interno do Felipe, não vai pro aluno. Template tem `README.md` + `CLAUDE.md` voltados ao aluno.
- **`hive/` reservado, não no MVP** — overkill pra 30d. Pasta com README explicativo de "quando reabrir" no futuro.
- **Curso 60 aulas portado com 2 módulos completos + 10 outline-only** — espinha de auto-estudo do aluno. Felipe expande os outline conforme cada aluno chega ali na sessão correspondente.
- **Skill `/linear-e2e-test` ganhou loop auto-fix no padrão Replit** (Lucas Montano) — origem registrada na própria skill com quote literal + nota Obsidian `Estudo/IA-Tecnologia/2026-06-28_system-design-vibe-coder-dev.md`.

## Idempotência

Skill `/ativar-cliente` é declaradamente idempotente ("detecta onde o cliente está e retoma de onde parou"). A.6 herda:

- Passo 1 (`gh repo create`): falha controladamente com erro `Name already exists on this account` se repo já existe → segue pro passo 2
- Passo 5b (issues): cada `gh issue create` é precedido por check `gh issue list --json title --jq` que pula se issue com mesmo título já existe

Bug detectado no smoke test 2026-06-28 e corrigido na mesma sessão.

## Smoke test 2026-06-28 — origem dos 3 fixes

Roteiro do espírito da `/linear-e2e-test` aplicado ao gate A.6 (não é issue Linear isolada, mas o protocolo cabe). Aluno fake: `Aluno E2E Teste` (slug `aluno-e2e-teste`). Runs: 2 (idempotência).

**Bugs detectados e corrigidos:**

| # | Severidade | Bug | Fix aplicado |
|---|---|---|---|
| 1 | Médio | Critério "substituir `<<ADAPTAR>>` em README + CLAUDE" era ambíguo — sed-blind substituía também menções literais no texto explicativo da skill (linha 3 do README descrevendo o conceito de placeholder, linha 87 da seção "Fluxo Felipe", linha 35 do CLAUDE.md em "Regras"), corrompendo a documentação | Lista exaustiva de placeholders por seção, com 9 entradas pro README e 9 pro CLAUDE.md. Anti-padrão explicitamente listado (3 ocorrências a NÃO tocar). Validação obrigatória: `grep -n "<<" README.md CLAUDE.md` deve retornar exatamente 3 ocorrências. |
| 2 | Médio | `gh issue create --label "sessao,setup"` falhava silenciosamente — labels não vêm do template GitHub | Sub-passo `5a` adicionado: `for label in sessao setup construcao integracao entrega; do gh label create "$label" --force; done` antes das issues |
| 3 | **Severo** | A.6.5 (criar issues) NÃO era idempotente — re-rodar gerava 5ª, 6ª, 7ª issue duplicada (skill pai promete idempotência global) | Função bash `create_issue_idempotent()` que checa por título antes de criar. Validação: `gh issue list --json number --jq 'length'` retorna exatamente 4 (não 5 nem 8) |

**Bonus do smoke test:** os 3 bugs **NÃO** atingem mais o próximo aluno (Leonardo Alves, 13/07). Sem o smoke test, Leonardo entraria com `<<NOME DO ALUNO>>` no título do CLAUDE.md dele.

## Don'ts

- **NÃO** rodar `gh repo create --template` com repo público — kit é privado por design
- **NÃO** substituir TODAS as ocorrências de `<<ADAPTAR>>` cegamente (bug #1)
- **NÃO** usar `--label` em `gh issue create` sem criar as labels antes (bug #2)
- **NÃO** rodar A.6.5 (criar issues) sem check de idempotência por título (bug #3)
- **NÃO** commitar `PROVISIONAMENTO.md` no repo do aluno — é doc interno Felipe
- **NÃO** publicar repo aluno como GitHub Template — só `cadencia-kit-template` é template (botão "Use this template")

## Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| `Could not clone: Name already exists on this account` no passo 1 | Idempotência — repo já existe | Segue pro passo 2 normalmente |
| `gh: must have admin rights` ao deletar | Token gh sem scope `delete_repo` | `gh auth refresh -h github.com -s delete_repo` (interativo, exige browser) |
| `rm: Device or resource busy` no clone local | VS Code ou outro processo segurando handle do `.git/` | Sair do VS Code, ou usar PowerShell `Remove-Item -Recurse -Force` |
| `grep "<<" README.md CLAUDE.md` retorna >3 após adaptar | Bug #1 não tratado — sed cego ou placeholder esquecido | Validar lista exaustiva da skill A.6 §Passo 3, complementar substituições faltantes |
| 5+ issues criadas após reativar | Bug #3 não tratado — falta `create_issue_idempotent()` | Atualizar skill A.6 §5b com a função idempotente |

## Histórico

- 2026-06-28 — gate A.6 criado · template-repo `cadencia-kit-template` publicado · smoke test rodou e capturou 3 bugs · 3 fixes aplicados na skill `/ativar-cliente` e no `PROVISIONAMENTO.md` interno · skill `/linear-e2e-test` enriquecida com padrão Replit/Lucas Montano (loop auto-fix + exemplo concreto DEV-873)

## Notas Relacionadas

[[Projetos/Central CS Onboarding/Docs/00-Visao-Geral]] · [[Projetos/Central CS Onboarding/Docs/09-Coolify-Migration-2026-06-27]] · [[Estudo/IA-Tecnologia/2026-06-28_system-design-vibe-coder-dev]]
