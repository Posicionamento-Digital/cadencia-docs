---
date: 2026-06-12
tags: [processo, documentacao, dev, vps, obsidian, automacao]
moc: "[[MOC-Processos]]"
---

# Documentação Dev — VPS para Obsidian

Processo automático que sincroniza documentação técnica gerada na VPS dev com o vault Obsidian da empresa.

## Fluxo completo

```
Dev roda /documentar-software na VPS
        ↓
Docs criadas no repo do projeto (CONTEXT.md, README.md, ADRs)
        ↓
Cópia enviada para /opt/dev-docs/<projeto>/
        ↓  (cron 23h — usuário felipe)
pd-framework/times/dev/docs/ (commit + push GitHub)
        ↓  (Task Scheduler 23:30 — Windows)
Obsidian_Vaults_Empresa/Dev/
        ↓
WhatsApp Stevo para Felipe com resumo dos arquivos sincronizados
```

## Componentes

| Componente | Path | Responsável |
|---|---|---|
| Skill `/documentar-software` (Felipe) | `/home/felipe/.claude/skills/documentar-software/` | VPS dev |
| Skill `/documentar-software` (Luiz) | `/home/luiz/.claude/skills/documentar-software/` | VPS dev |
| Pasta compartilhada | `/opt/dev-docs/` | VPS dev |
| Script sync VPS | `/opt/sync-dev-docs.py` | VPS dev (cron 23h) |
| Script sync Windows | `~/.claude/workers/sync-dev-docs-vault.py` | Windows (23:30) |
| Task Scheduler | `SyncDevDocsVault` | Windows |
| Destino Obsidian | `Obsidian_Vaults_Empresa/Dev/` | Local |

## Como usar (devs)

1. Terminar uma feature, fix ou componente
2. Rodar `/documentar-software` no Claude Code dentro do projeto
3. O Claude pergunta o escopo (projeto inteiro / sessão atual / componente específico)
4. Gera docs no repo + copia para `/opt/dev-docs/`
5. Às 23h commita automaticamente — às 23:30 aparece no Obsidian

## O que documentar

- Decisões técnicas não óbvias (por que X em vez de Y)
- Componentes novos criados
- Bugs complexos resolvidos (causa raiz + fix)
- Qualquer coisa que um dev novo precisaria saber para trabalhar no projeto

## Arquivos de log

- VPS: `/opt/dev-docs/.sync.log` e `/opt/dev-docs/.sync-log.json`
- Windows: output do Task Scheduler

## Projetos monitorados

- `cadencia` — Luiz (`/home/luiz/projetos/cadencia`)
- `pd-portal` — Luiz (`/home/luiz/projetos/pd-portal`)
- Qualquer projeto que Felipe trabalhe na VPS dev
