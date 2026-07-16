---
date: 2026-06-18
tags: [documentacao, projeto, cadencia]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]"]
---
## Identidade
- **Tipo:** feature de UI (Next.js 15 App Router) + rotas de API
- **Stack:** React + TanStack Table v8 + Tailwind + Supabase (service_role)
- **Path no repo:** `src/app/(app)/app/growth/contatos/` e `.../empresas/`
- **Status:** em produção (branch `master`, deploy 2026-06-18)
- **Issues:** CAD-570, CAD-571, CAD-573, CAD-613, CAD-642

## O que é
Sistema de tabela estilo Linear/Notion para as listas de **Contatos** e **Empresas** do CRM nativo do Cadência. Contatos é a fonte canônica dos componentes; Empresas reusa tudo.

## Para que serve
Dar ao cliente uma lista rica e configurável: filtrar, escolher/reordenar/redimensionar colunas, alternar Lista/Board, agrupar (colunas + swimlanes), salvar visualizações, editar inline e carregar em lotes — sem sair da tela.

## Como funciona
1. `page.tsx` (server) carrega 1º lote (100) enriquecido + total + tags + custom_field_defs.
2. `ContatosView`/`EmpresasView` (client) operam client-side sobre o lote (PRD §3.2).
3. Componentes compartilhados: `FilterMenu`, `DisplayPanel`, `BoardView` (genérico), `ViewsBar` (prop `entity`), `EditableCell`.
4. Motor de filtros genérico em `src/lib/contacts/filters.ts` (reusado por `buildCompanyFields`).
5. Persistência via API com `.eq("tenant_id")` (service_role bypassa RLS) + allowlist de colunas no PATCH.

## Quando usar / NÃO usar
- **Usar:** qualquer lista de entidade do CRM que precise de filtro/colunas/board.
- **NÃO usar:** o motor não é por-filtro no servidor — assume o dataset carregado em memória (cap de lote + "Mostrar mais").

## Decisões (ADRs)
- Filtragem client-side sobre o lote carregado (PRD §3.2), não endpoint por filtro.
- `BoardView` genérico (`BoardRow` + `rowName`/`linkHref`) para servir múltiplas entidades.
- Oportunidade = pill própria "Negócios" (CAD-564/573), não agrupamento de contatos.

## Don'ts
- Sem `setState` no `onDragStart` (cancela o drag); âncora do card `draggable={false}`.
- Revert otimista via `rowsRef.current`, nunca closure de `rows`.
- Board não agrupa por `number`/`date`.

## Troubleshooting
- Card volta ao recarregar → PATCH falhou / groupBy não-direto (gate `DIRECT_GROUP` + revert).
- Menu ⋯ da view cortado → posição `fixed`.
- Repo no OneDrive vira branch sozinho → conferir `git branch` antes de commitar.

## Busca global Ctrl+K (CAD-572)
Command palette global (`AppLayoutWrapper` → `components/app/CommandPalette`), em qualquer rota `/app/*`. DB: `contacts.search_vector` (generated STORED) + GIN + RPC `search_contacts` (ts_rank_cd, EXECUTE só service_role). API: `GET /api/app/search?q=`. UI hand-rolled (sem cmdk): debounce + AbortController, histórico localStorage, teclado. V1 = só contatos.

## Campos estruturados de contato (CAD-616)
Colunas em `contacts` p/ todo tenant: `lead_source` (select 23 fontes), `is_icp` (Sim/Não), 4 datas (última compra/assinatura/vencimento contrato/última interação). Na tabela+filtros+inline+board. Backfill de fonte_do_lead/fit_icp. Migração dos campos duplicados de empresa (cnpj/setor/porte/sócios…) de contact.custom_fields → entidade Empresa associada (por CNPJ; sem CNPJ por nome). 805 empresas / 815 associações. Campos internos (press/stripe/score_ia/ecuro) não migrados.

## Histórico
- 2026-06-18 — Sistema completo em produção (Contatos + Empresas). Review Claude Opus + hardening pós-review. Merge `cad-563` → `feature/crm-proprio` → `master`.
- 2026-06-18 — Busca global Ctrl+K (CAD-572) em produção: search_vector + RPC + CommandPalette global.
- 2026-06-19 — Campos estruturados de contato + migração empresa (CAD-616) em produção.

## Notas Relacionadas
[[Projetos/Cadencia/Docs/crm-redesign-ux-sofia]]
