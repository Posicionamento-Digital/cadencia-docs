---
date: 2026-06-25
tags: [infra, git, onedrive, worktree, framework]
moc: "[[MOC-Infra]]"
---

# Worktrees fora do OneDrive — junction (DEV-865)

> Aprendizado de infra: por que o OneDrive bagunçava o trabalho dos agentes e como foi resolvido de forma transparente. Consultar quando aparecer "branch trocou sozinha" ou "arquivo reverteu" em repo dentro do OneDrive.

## Sintoma

Em repos dentro de `Hub Projetos/` (sincronizado pelo OneDrive), o trabalho dos agentes era corrompido: **branch trocava sozinha**, **arquivos revertiam no meio da edição**, worktrees viravam lixo. Visto ao vivo em 25/06: um arquivo (`healthcheck.py`) mudou entre o `git add` e o `git commit`.

## Causa raiz

Git **worktrees** (cópias paralelas do repo em branch isolada) eram criadas em `.claude/worktrees/`, **dentro do OneDrive**. Dois processos competindo pelo mesmo arquivo, sem coordenação:

- O **git/agente** escrevendo na worktree o tempo todo (natureza da worktree).
- O **OneDrive** vendo os arquivos mudarem e tentando sincronizar com a nuvem/outras máquinas — às vezes "puxando" uma versão antiga por cima do que o git acabou de escrever.

Pior: o OneDrive marcava `.claude/worktrees` como placeholder **Files On-Demand** (reparse tag `0x9000e01a`), tratando a pasta como gerenciada por ele — veneno para uma worktree que precisa de arquivos 100% locais e estáveis.

## Solução — junction

`<repo>/.claude/worktrees` deixou de ser pasta real e virou uma **junction** (link de diretório a nível de SO) apontando para `C:\pd-worktrees\<repo>`, **fora do OneDrive**.

- O harness (`EnterWorktree`) e o git continuam usando `.claude/worktrees/` exatamente como antes — só o local físico muda.
- O OneDrive **ignora junctions** (reparse points de mount point), então não toca mais nas worktrees.
- **Precedente que validou:** `.claude/skills` já era junction (→ `stamper/skills`) e nunca deu problema. Confirmação empírica: criada a junction, uma `git worktree add` nasceu em `C:/pd-worktrees/...` (fora do OneDrive), não em `Hub Projetos`.

> **Analogia:** a placa na parede ainda diz `.claude/worktrees`, mas atravessar a porta leva a outro prédio (`C:\pd-worktrees`) num bairro que o OneDrive não patrulha. Git e harness entram pela placa e nem percebem; o OneDrive não segue a porta pra fora.

## Operação

- **Aplicar/garantir** (idempotente, todos os repos do Hub Projetos): `pwsh _core/setup-worktree-junction.ps1`
  - Defensivo: pula repo com worktree ativa (não destrói trabalho); slug por caminho relativo (evita colisão entre repos de mesmo nome).
- **Raiz das worktrees:** `C:\pd-worktrees\<repo>` (uma subpasta por repo, isoladas).
- **Ao finalizar:** remover a worktree (`ExitWorktree action:remove` ou limpeza do `/encerrar-sessao` §6.1). Não deixar órfã.
- **Repo novo no Hub Projetos:** rodar o script de novo (cria a junction do novo).

## Refs

- `pd-framework/_core/setup-worktree-junction.ps1` — script de setup
- `pd-framework/CLAUDE.md` § "Worktrees — sempre fora do OneDrive"
- Issue DEV-865
