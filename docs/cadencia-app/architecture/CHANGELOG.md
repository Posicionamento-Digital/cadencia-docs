> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `CHANGELOG.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/CHANGELOG.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# Changelog

## [Doc Update 2026-05-27]

### Documentação

- **Fase 6 (enrichment):** Os 28 CLAUDE.md de componente foram enriquecidos com seções "Quando usar / NÃO usar", links para ADRs, Don'ts consolidados, "Já tentamos" referenciando incidents, Troubleshooting e Referências cruzadas.
- **Fase 7 (globais):**
  - Novo `CONTEXT.md` raiz — linguagem ubíqua do domínio (tenant, editorial, dossier, location_pit_token, etc.) com relacionamentos e ambiguidades flagadas.
  - Novo `docs/architecture.md` — diagrama C4 (Context + Container) em mermaid.
  - Novas ADRs:
    - ADR-0003: GHL como motor invisível.
    - ADR-0004: Carrossel/reels Railway, resto VPS.
    - ADR-0005: `location_pit_token` por tenant (não global).
    - ADR-0006: Multi-tenant via RLS Supabase.
- **Fase 8 (wiki HTML):** `docs/wiki/` regenerada do zero — index + 28 páginas de componente + architecture + context + changelog. Sidebar dinâmica (placeholders só renderizam HTMLs efetivamente gerados).
- **Fase 9 (Obsidian):** 28 notas atualizadas no vault Time PD (`Projetos/Cadencia/Docs/`) com frontmatter + wikilinks.

### Limpeza

- Material histórico do antigo `_bmad-output/` migrado para `pd-framework/times/produto/cadencia/context/historical/` (104 artefatos). Não é mais fonte de verdade — só referência.

### Pendências

- Credenciais em texto claro em `Credenciais_CLI/` (repo privado) — manter por ora, rotacionar quando definir destino final.
- Migração Railway → Coolify VPS (PDL-18 a 23) muda paths e deploy — doc atual reflete estado **antes** da migração.


