---
date: 2026-05-19
tags: [documentacao, recovery, hetzner]
moc: "[[MOC-Projetos]]"
---
# 01 — Documentação da Recuperação

## O que é
Registros da operação: comunicações com Hetzner, inventário dos dados capturados, credenciais e reconhecimento dos servidores.

## Conteúdo

**emails-hetzner/**
- `EMAIL_HETZNER_ABUSE.md` — Notificação de abuso à Hetzner
- `EMAIL_HETZNER_FOLLOWUP.md` — Follow-up técnico

**inventario/**
- `INVENTORY.md` — Inventário mestre (280 workflows, 101+ credenciais, 9 dumps PG, 28 repos GitHub)
- `CHECKSUMS.sha256` — Hashes SHA-256 para verificação de integridade
- `recon/` — Reconhecimento dos servidores bd01 e m01

**credenciais/**
- `CREDENCIAIS.env` — ⚠️ Credenciais em texto claro. Migrar para 1Password antes de usar.

## Quando acessar
- Comunicações legais → `emails-hetzner/`
- Verificar integridade de backup → `inventario/CHECKSUMS.sha256`
- Recuperar senha → `credenciais/CREDENCIAIS.env`

## Notas Relacionadas
[[00-indice]] · [[Incidentes/Takeover-GHL-2026-05-07]]
