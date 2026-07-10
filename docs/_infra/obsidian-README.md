---
date: 2026-05-13
tags: [infra, obsidian, livesync, couchdb, vault, sync]
---

# Infra — Obsidian Self-Hosted

Configuração e manutenção do sistema de sincronização dos vaults Obsidian via **LiveSync self-hosted** com CouchDB.

## Arquitetura

```
Vault local (Windows) ←→ LiveSync plugin ←→ CouchDB (VPS Hostinger)
```

- **CouchDB:** `obsidian.cadencia.ia.br` (rodando na VPS Hostinger)
- **Vaults sincronizados:** Time PD · Pessoal (Felipe Luis Salgueiro) · Posicionamento Digital
- **Plugin:** obsidian-livesync (community plugin)

## Vaults e caminhos locais

| Vault | Caminho |
|---|---|
| Time PD | `C:\Users\felip\OneDrive\Documentos\Time PD\` |
| Pessoal | `C:\Users\felip\OneDrive\Documentos\Pessoal_Felipe Luis Salgueiro\` |
| Posicionamento Digital | `C:\Users\felip\OneDrive\Documentos\Posicionamento Digital\` |

## O que fica aqui

- Configuração do CouchDB (usuário, banco de dados, permissões)
- Como adicionar um novo vault ao LiveSync
- Como diagnosticar falha de sincronização
- Como fazer backup manual do banco CouchDB
- Como restaurar um vault a partir do CouchDB

## Atenção

- O Obsidian precisa estar **aberto** para o CLI funcionar
- Mudanças diretas no filesystem são refletidas no CouchDB na próxima sync
- Plugins devem ser gerenciados via `.obsidian/plugins/` + `community-plugins.json`

## Notas Relacionadas

- [[Infra/VPS-Hostinger/README]]
- [[Infra/Cloudflare/README]]
- [[Incidentes/Infra/README]]
