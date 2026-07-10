---
date: 2026-06-29
tags: [projeto, produto, cadencia]
moc: "[[MOC-Projetos]]"
type: entity
entity_kind: projeto
---
# ecuro-mcp

> Entidade (projeto). Hub de conexão do graph.

## Sources ligadas
```dataview
TABLE source_kind AS Tipo, date AS Data
FROM ""
WHERE contains(entities, this.file.link)
SORT date DESC
```

## Notas Relacionadas
[[Ecuro-Mcp]]
