---
type: source
source_kind: gotcha
date: 
entities: ["[[Cadencia]]", "[[comercial]]"]
tags: [gotcha, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# Gotchas — comercial-geracao-de-negocios

# Gotchas — times/comercial/geracao-de-negocios

> Armadilhas técnicas validadas (manual review).
> Source: entries promovidas de gotchas-pending.md (auto-detect).

## G002 — Fonte de verdade dos deals é o CRM Cadencia, não o texto do STATE.md

STATE.md acumula texto de fases antigas (época GHL) e fica desatualizado. **Nunca reportar deals/pipeline de memória ou do histórico escrito.** Sempre consultar ao vivo:

```bash
cadencia-cli opportunities list --pipeline geracao-negocios
cadencia-cli opportunities list --pipeline geracao-demanda
cadencia-cli opportunities get <id>
cadencia-cli contacts get <contact_id>
```

Origem: 2026-07-07, Felipe apontou que STATE.md ainda refletia época do GHL (valores errados, deals fechados que já tinham mudado, deal novo não documentado).
