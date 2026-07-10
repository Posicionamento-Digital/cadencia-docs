---
date: 2026-05-19
tags: [documentacao, recovery, hetzner, banco, dados, postgresql, mongodb, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
---
# 04 — Banco de Dados

## O que é
9 dumps PostgreSQL + 1 archive MongoDB capturados em 09/05/2026.

## Dumps PostgreSQL (619 MB total)

| Arquivo | Tamanho | Prioridade |
|---|---|---|
| `evolution.dump` | 329 MB | Alta — conversas WhatsApp |
| `n8n_host.dump` | 282 MB | Alta — workflows n8n |
| `n8n_queue2.dump` | 1 MB | Média |
| `baserow.dump` | 4.8 MB | Média |
| `metabase.dump` | 2.5 MB | Média |
| `kestra_db.dump` | 80 KB | Baixa |

## Como restaurar
```bash
createdb -U postgres <nome_banco>
pg_restore -U postgres -d <nome_banco> -Fc <arquivo>.dump
```
Guia completo: `BLUEPRINT/docs/guides/restore-postgres.md`

## Observação
Mesmos dumps existem em `06-backups-brutos/` (original) e aqui (organizado para uso).

## Notas Relacionadas
[[00-indice]] · [[05-infraestrutura]] · [[06-backups-brutos]]
