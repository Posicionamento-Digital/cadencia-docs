---
date: 2026-05-19
tags: [documentacao, recovery, hetzner, infraestrutura, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Recovery Hertzner]]"]
---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

# Recovery Hertzner — Índice

Arquivo completo da operação de recuperação da infraestrutura Hetzner após sequestro por Michael Jhonatan em 07/05/2026.

**Status:** Concluído (95% — 39/41 stories BMAD)
**Período de captura:** 09–11 mai 2026

## Pastas

| Pasta | Conteúdo |
|---|---|
| [[01-documentacao]] | Emails Hetzner, inventário, credenciais, recon |
| [[02-codigo-fonte]] | 11 projetos GitHub recuperados |
| [[03-n8n-workflows]] | 188 workflows + 92 credenciais n8n |
| [[04-banco-dados]] | 9 dumps PostgreSQL + MongoDB |
| [[05-infraestrutura]] | 24 Docker Compose stacks |
| [[06-backups-brutos]] | 8.6 GB capturas SSH brutas |

## Ordem de reimplantação
1. Ler `BLUEPRINT/docs/ARCHITECTURE.md`
2. Subir infraestrutura → [[05-infraestrutura]]
3. Restaurar bancos → [[04-banco-dados]]
4. Importar workflows → [[03-n8n-workflows]] (41 ativos primeiro)
5. Importar credenciais n8n
6. Verificar código → [[02-codigo-fonte]]

## Notas Relacionadas
[[Incidentes/Takeover-GHL-2026-05-07]]
