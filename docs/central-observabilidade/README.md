---
date: 2026-07-05
tags: [projeto, produto, cadencia]
moc: "[[MOC-Projetos]]"
type: entity
entity_kind: projeto
status: ativo
aliases: [central de observabilidade, central-de-observabilidade]
---
# Central de Observabilidade

> Entidade (projeto). Hub de conexão do graph.

## Sources ligadas
```dataview
TABLE source_kind AS Tipo, date AS Data
FROM ""
WHERE contains(entities, this.file.link)
SORT date DESC
```

## Notas Relacionadas
[[Central De Observabilidade]]
