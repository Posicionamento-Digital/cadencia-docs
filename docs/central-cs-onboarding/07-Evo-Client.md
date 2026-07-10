---
date: 2026-06-24
tags: [doc, componente, whatsapp, evo, integracao, central-cs]
moc: "[[MOC-Projetos]]"
status: ativo
type: source
entities: ["[[Cadencia]]", "[[comercial]]"]
---
# Evo Client — WhatsApp (Evolution GO)

## Identidade

- **Tipo:** lib Python + CLI (`_shared`)
- **Path:** `_shared/evo_client.py` (291) · shim `_shared/stevo_client.py` (deprecated)
- **Servidor:** `https://evo.cadencia.ia.br` (self-hosted Evolution GO, lineage WuzAPI)
- **Auth:** header `apikey` (token da instância)
- **Status:** 🟢 produção desde 24/06/2026

## Contas

| `account=` | Telefone | Instância | Item 1P |
|---|---|---|---|
| `pessoal` | 5511914912127 | felipe-pessoal | `EVO - API  - Num pessoal` (2 espaços) |
| `comercial` | 5511914956996 | cadencia-comercial | `EVO - API - Num comercial` |

Token = campo `password` do item. Vault `E-mails`.

## Uso

```python
from evo_client import EvoClient
EvoClient().send_text("5511999999999", "oi")          # pessoal
EvoClient(account="comercial").send_text(...)         # comercial
```

CLI: `python _shared/evo_client.py [--comercial] <dest> "<msg>"`.

`StevoClient = EvoClient` (alias compat — drop-in pra código legado).

## Endpoints

- `POST /send/text` `{number, text}`
- `POST /send/media` `{number, type, url, caption?, filename?}`
- `GET /instance/status`
- `GET /group/list`

## Shim stevo_client.py

Reexporta `EvoClient`, emite `DeprecationWarning`. Cobre clones VPS com path hardcoded `python stevo_client.py` até git propagar.

## Don'ts

- Não usar chave global pra enviar mensagem (é admin).
- Não logar/commitar token.
- Não adicionar lógica nova ao shim.

## Relacionadas

- [[02-Receiver]] (dispatch.send_whatsapp)
- [[04-Consolidador]] (alerta)
