---
date: 2026-05-19
tags: [documentacao, recovery, hetzner, backup, ssh]
moc: "[[MOC-Projetos]]"
---
# 06 — Backups Brutos

## O que é
Capturas SSH brutas dos servidores Hetzner realizadas em 09–10/05/2026, antes do wipe. Fonte primária de todos os dados recuperados. ~8.6 GB total.

## Estrutura

**capturas-tgz/** (~1.4 GB) — arquivos compactados originais
- `m01-system.tgz` — 1.1 GB — sistema completo do manager01
- `bd01-volumes.tgz` — 240 MB
- `bd01-system.tgz` — 68 MB

**sistema-extraido/** (~7.2 GB) — conteúdo descompactado
- `bancodedados01/` — dumps + volumes + sistema do bd01
- `manager01/` — volumes + stacks + sistema do m01
- `_extracted/` — /etc e /root extraídos para inspeção rápida

## Quando acessar
- Arquivo de config específico → `_extracted/m01/etc/` ou `bd01/etc/`
- Dados não encontrados em `04-banco-dados/` → `sistema-extraido/bancodedados01/databases/`
- Variável de ambiente de container → `sistema-extraido/manager01/volumes/`
- Verificar integridade → comparar com `01-documentacao/inventario/CHECKSUMS.sha256`

## Extração (se necessário)
```bash
tar -xzf capturas-tgz/m01-system.tgz -C /destino
```

## Notas Relacionadas
[[00-indice]] · [[04-banco-dados]] · [[05-infraestrutura]]
