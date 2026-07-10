---
type: source
source_kind: decisao
date: 
entities: ["[[Cadencia]]", "[[Iasmin Lopes Pinto]]", "[[dev]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# Decisões — dev-sofia-memory

# Decisões — Squad Sofia

(append-only — decisões de UX/fluxo relevantes, mais recente em cima)

---

## 2026-07-04 — Storybook Astryx vira bancada visual da Sofia

**Contexto:** Felipe abriu `http://localhost:6006/` e pediu que a Sofia ajude, em planejamentos futuros, a mostrar/testar componentes Astryx no browser antes de decidir UI.

**Decisão:** criar duas skills do Squad Sofia: `/astryx-storybook` para subir/abrir/testar o Storybook do Astryx, e `/astryx-planejar-ui` para planejar UI React/Next usando Astryx como biblioteca de referência com adaptação de identidade Cadência/PD. Storybook passa a ser a bancada visual padrão para inspecionar componentes, estados e templates Astryx com Felipe.

**Validação real:** `pnpm install` concluído; `pnpm -F @astryxdesign/core build` passou; `pnpm storybook` subiu em `http://localhost:6006/` com HTTP 200. Gotchas: `pnpm build` completo falha no Windows em `@astryxdesign/lab` por `rm -rf`; não passar flags extras para `pnpm storybook`.

**Critério Sofia:** usar componentes prontos e bibliotecas para não reinventar roda; não copiar visual cru. Astryx deve ser tematizado/adaptado com identidade Cadência quando entrar em produto.

---

## 2026-07-04 — Astryx-first como padrão de referência da Sofia para novas UIs React/Next

**Contexto:** Felipe forkou `facebook/astryx` para `felipeluissalgueiro/astryx` e pediu clonar local/VPS Dev, invocar Sofia e avaliar se o repo deve virar padrão para próximas UIs.

**Decisão:** Sofia passa a usar Astryx como referência padrão para novas UIs React/Next internas: consultar CLI/docs/templates/component docs antes de desenhar tela do zero; preferir templates e componentes Astryx quando forem compatíveis com o fluxo; validar contra o design system vivo do produto antes de recomendar implementação. Isso NÃO é migração automática nem substituição cega de Cadência/PD Portal.

**Clones:** `C:/dev/astryx` no Windows e `/home/felipe/astryx` na VPS Dev (user Felipe). Repo mapeado em `_core/REPO-MAP.md` como `repo:astryx`.

**Opinião sincera da Sofia:** forte sim para ferramenta interna/SaaS operacional. Astryx tem componentes, tokens, temas, Table/PowerSearch, AppShell/Layout, CLI, agent-docs, JSON API, doctor e vibe-tests — é muito mais útil para agentes do que shadcn/copypaste solto. O risco é beta/pre-1.0 e visual genérico se não houver tema PD/Cadencia; portanto adoção deve começar por spike e tema, não por migração em massa.

**Refs:** `times/dev/sofia/context/astryx-ui-standard.md`.

---

## 2026-07-02 — Gestão de Tráfego (Cadencia): exceção ao ux-patterns-crm §0 + design da aba

**Contexto:** UX da aba "Gestão de Tráfego" (PRD Iasmin/Agência Brokers, Epics DEV-1046..1052). Spec completa em `Obsidian_Vaults_Empresa/Projetos/Iasmin Lopes Pinto/Docs/ux-gestao-trafego.md`.

**Exceção registrada (Critical Action 2):** a tabela de tradução engenharia→Tiazinha (`foundation/ux-patterns-crm.md §0`) NÃO se aplica dentro da aba Gestão de Tráfego. Usuária é a Manuela — gestora de tráfego profissional; CTR/CPM/CPL/CAC/frequência/Quality Ranking são a linguagem nativa dela e aparecem crus. Continuam valendo sem exceção: erros humanizados (§3), empty/loading/toast (§1/§2/§4), badge de atribuição (§5), voz Maga/Sábia.

**Decisões estruturais:**
- 3 níveis sem modal no fluxo principal: dashboard (lista ordenada por urgência) → drawer lateral de campanha → chat Pedro dentro do drawer, ancorado na campanha+sugestão.
- Único modal do sistema: confirmação de escrita real no Meta (irreversível — undo §4 não se aplica; sem UI otimista, só confirma quando o Meta responder OK).
- "Por quê" da sugestão sempre visível no drawer (decisions_log); chat é pra debater, não pra descobrir a justificativa.
- CAC com gate ≥5 leads mostra `—` + tooltip — nunca número estatisticamente inválido.
- Pós-ação: campanha trava em "Em observação" até o ciclo seguinte (motor não pode parecer bipolar).
- Rejeição pede motivo via chips (opcional) — insumo pra calibrar a matriz do DEV-1048.

**Adendo 2026-07-02 (pedido do Felipe):** spec amarrada aos componentes REAIS do CRM (leitura de `origin/master` do cadencia-app, módulos contatos+oportunidades — os mais refinados). Base obrigatória: kit `crm-ui.tsx` (Card/Pill/LinearTabs/CollapsibleSection), drawer 560px (OpportunityDrawer), faixa-resumo no padrão DailyGoalsHUD, status tabs com contador, tabela ContatosView (TanStack v8), Toast custom do app (2s, sem undo — Sonner e undo-8s do foundation NÃO existem no código), botões CVA variants, tokens `var(--color-*)`. NÃO reusar: FilterMenu/DisplayPanel/ViewsBar (overkill v1), board/drag, confetti. Única superfície visual nova: chat Pedro (montar com primitives do kit). Detalhe: §9 da spec.

---

## 2026-05-25 — Squad criado (PDL-256)

Squad Sofia criado como parte do bootstrap do Time Dev. Sem decisões UX ainda.
