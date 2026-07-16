---
date: 2026-05-18
tags: [documentacao, skill, portal-pd]
moc: "[[MOC-Projetos]]"
---

# Skills de Conteudo do Portal PD

## Identidade
- **Tipo:** skills Claude Code
- **Path no repo:** .claude/skills/portal-*/SKILL.md
- **Status:** ativo

## Skills disponiveis

| Skill | Interface | Funcao |
|---|---|---|
| /portal-setup-tenant | <cadencia_contact_id> | Onboarding completo via CRM Cadencia |
| /portal-wiki | <slug> "<path>" | Publica MDs do Obsidian |
| /portal-arquivos | <slug> "<path>" | Upload para Storage |
| /portal-videos | <slug> --playlist "Nome" | Sync Tella MCP |
| /portal-materiais | <slug> "<url>" --tipo | Link externo ou PDF |

## Gotchas
- CRM Cadencia: API autenticada por JWT/HMAC
- Storage: paths ASCII apenas (planilhas-e-metricas, nao "Planilhas e Metricas")
- sb_secret key nao funciona na Storage REST API: buscar JWT legacy
- Tella MCP: verificar instalacao antes de usar --playlist

## Historico
- 2026-05-18 - 5 skills criadas no launch

## Notas Relacionadas
[[portal-pd-overview]]
