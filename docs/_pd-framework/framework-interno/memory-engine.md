---
date: 2026-07-03
tags: [doc, componente, pd-framework, documentacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[PD Framework]]"]
---

# Memory Engine — ciclo de vida de memória (D1)

## Identidade
- **Tipo:** lib/CLI determinística (core)
- **Stack:** Python 3.12, zero deps
- **Path:** `_core/memory_engine.py` + re-rank em `_core/lookup.py`
- **Issues:** epic DEV-1107 (stories DEV-1108…1111)
- **Status:** ativo

## O que é
O loop de curadoria automática da memória do framework, portado do estudo do ruflo (ADR-050 deles, código lido): **buscar → servir → registrar uso → boost/decay → ranking melhor → medir**. Markdown+git continua a fonte nobre; o engine mantém índice derivado de USO em `.pd/memory/index.json` (local, regenerável).

## Como funciona
1. **Índice:** fingerprint FNV-1a deduplica por conteúdo; metadados de uso (confidence, access_count) sobrevivem a rebuilds. 398 docs reais (75 incidents + 323 memory).
2. **Ciclo de vida:** acesso +0.03 · feedback +0.05/−0.02 · decay −0.005/dia só em nunca-acessadas (24h graça, piso 0.05). Decay **ancorado** — corrige bug de composição do original.
3. **Re-rank no lookup:** `score × (0.5+confidence)`; hits servidos registram acesso sozinhos (feedback implícito). `--no-memory-rank` = fallback lexical puro.
4. **Medição:** `snapshot`/`trend` → IMPROVING/DECLINING/STABLE pelo drift da confidence média.

## Quickstart
```bash
python _core/memory_engine.py build && python _core/memory_engine.py stats
python _core/lookup.py "deploy vercel"        # re-rank + registro automáticos
python _core/memory_engine.py decay && python _core/memory_engine.py snapshot
python _core/memory_engine.py trend
```

## Decisões
- Ciclo de vida ANTES de embeddings (D1) · curadoria sem deleção · decay ancorado · PageRank adiado (corpus ~400 docs não justifica; snapshots decidem a fase 2).

## Don'ts
- Nunca editar `.pd/memory/index.json` na mão — é derivado; rebuild resolve.
- Nunca portar o decay por idade total do ruflo (compõe desconto — bug documentado).

## Troubleshooting
- **Ranking não muda** → índice existe? (`build`); memória está no corpus dos backends ativos? (auto-memory do `~/.claude` NÃO entra — árvore separada).
- **Trend sempre null** → precisa de ≥2 snapshots.

## Histórico
- 2026-07-03 — epic completo: 0b1c2d6 (índice) · b875ba7 (ciclo de vida) · 27e85e8 (re-rank lookup) · a22c46a (snapshots/trend + docs)

## Notas Relacionadas
[[outcomes-cost]] · repo: `_core/docs/memory-engine.md` · decisão: `times/dev/memory/decisions.md`
