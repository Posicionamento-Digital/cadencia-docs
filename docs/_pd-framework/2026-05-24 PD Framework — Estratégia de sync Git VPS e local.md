---
date: 2026-05-24
tags: [ia, framework, git, infraestrutura, vps]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Estratégia de Sync Git (VPS ↔ Local)

> Decisão de arquitetura: 24/05/2026
> Arquivo técnico: `Hub Projetos/pd-framework/docs/git-sync-strategy.md`

---

## Premissa

O `pd-framework` é um monorepo clonado em dois lugares:
- **VPS Master** (`72.60.4.71`) — workers autônomos escrevem STATE.md via cron
- **Máquina local (Windows)** — Felipe abre squads interativamente, escreve STATE.md ao fechar

O **GitHub é o hub central**. Toda sincronização passa por ele.

---

## Fluxo padrão

### VPS (autônomo)

```
cron → harness.sh
  → git pull --rebase origin main   ← estado mais recente antes de rodar
  → worker executa
  → state-updater.py atualiza STATE.md
  → git commit + git push
  → log em /var/log/pd-framework/<squad>.log
```

### Local (interativo)

```
/abrir-squad <area>
  → git pull --rebase origin main   ← sempre antes de começar
  → Claude lê CLAUDE.md + STATE.md
  → Felipe trabalha
  → /fechar-squad <area>
  → STATE.md substituído + decisions.md appendado se houve decisão
  → git commit + git push
```

---

## Quem escreve o quê

| Arquivo | VPS | Local |
|---|---|---|
| `STATE.md` | escreve (workers) | escreve (sessões) |
| `decisions.md` | não toca | escreve (/fechar-squad) |
| `CLAUDE.md` | só lê | escreve (Felipe) |
| `skills/`, `workers/`, `_shared/` | só lê/executa | escreve (Felipe) |
| `queue/obsidian/` | escreve (workers) | lê e limpa (Task Scheduler) |

**Regra:** VPS nunca escreve em CLAUDE.md, skills/, workers/, _shared/. Só em STATE.md e queue/.

---

## Por que conflitos são raros

1. **Crons escalonados por squad** — Infra: :05, Marketing: :10, Comercial: :15, CS: :20, Produto: :30. Janelas nunca se sobrepõem.
2. **Sessões interativas têm timing humano** — Felipe começa de manhã, depois das primeiras execuções de cron.
3. **STATE.md é substituído, não appendado** — harness.sh detecta rejected no push antes de commitar lixo.

---

## Se conflito acontecer

`harness.sh` detecta `git push` rejected e executa:

```bash
git pull --rebase origin main
# Se rebase falhar:
git checkout --theirs squads/$SQUAD/memory/STATE.md  # VPS vence
git add squads/$SQUAD/memory/STATE.md
git rebase --continue && git push
# Alerta via WhatsApp:
# "⚠️ conflito STATE.md em $SQUAD resolvido (VPS venceu). Revisar se sessão local estava aberta."
```

**VPS vence porque:** o worker acabou de rodar e tem o estado mais recente da execução autônoma. A sessão local que estava aberta provavelmente não sabia do que o worker fez. Felipe recebe alerta e reabre o squad para ver o que mudou.

---

## Integração queue/obsidian/

```
VPS worker → queue/obsidian/YYYY-MM-DD-titulo.md → git push
  ↓
Windows Task Scheduler (a cada 15min):
  git pull → obsidian-cli cria nota → limpa queue/ → git push
  ↓
Obsidian Sync → mobile, outros dispositivos
```

Script: `pd-framework/scripts/process-obsidian-queue.ps1`

---

## Resumo das decisões

| Decisão | Escolha | Motivo |
|---|---|---|
| Hub de sync | GitHub | Padrão git, audit trail, sem infra extra |
| Pull strategy | `--rebase` | Histórico limpo, sem merge commits de sync |
| Conflito STATE.md | VPS vence | Worker tem estado mais recente |
| Alerta conflito | WhatsApp Stevo | Felipe precisa saber que sessão foi sobrescrita |
| STATE.md no git | Sim | Memória operacional precisa viajar entre clones |
| Logs de execução | Fora do git | Volume alto, sem valor no histórico |

---

## Notas Relacionadas

[[IA-Tecnologia/2026-05-24 PD Framework — Arquitetura completa e mapeamento de stack]] · [[IA-Tecnologia/2026-05-24 PD Framework — Mapeamento real de squads e infraestrutura]] · [[IA-Tecnologia/2026-05-23 PD Framework — arquitetura de squads e Stamper como orchestrator]]
