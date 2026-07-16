---
date: 2026-05-25
tags: [framework, stamper, squads, personas, bmad]
moc: "[[Projetos/PD Framework/PD Framework MOC]]"
type: source
entities: ["[[Cadencia]]", "[[PD Framework]]", "[[comercial]]", "[[financeiro]]", "[[marketing]]"]
---
# PD Framework — Estrutura Completa Fase 0

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


> Documentação consolidada do que foi construído na PDL-241 (Fase 0.7) — inventário, frameworks de referência, personas, padrões. Data: 2026-05-25.

## Resumo executivo

A Fase 0 do [[Projetos/PD Framework/PD Framework MOC|PD Framework]] está fechada. 9 documentos em `pd-framework/_core/` definem identidade, regras, personas e fluxo. Total catalogado: 139 skills locais + 55 skills BMAD/AIOX externas alocadas + 10 personas BR + 13 seções de DEV-WORKFLOW.

## Arquitetura mental

PD Framework = monorepo único que abriga:
- **Stamper** (orquestrador central, dia a dia Felipe) — não é squad, é camada
- **Squads operacionais** (6): Comercial, CS, Marketing, Infra, Operacional, Financeiro
- **Squad Estudo** (novo) — knowledge base pessoal
- **Área Desenvolvimento** — chapéu transversal aos produtos
- **4 produtos com SOUL**: [[Projetos/Cadencia/Cadencia MOC|Cadência]] (com 4 sub-squads: frontend, growth, workers, blog), PD Portal, NSkin, [[Projetos/GCI-GO/GCI-GO MOC|GCI-GO]]
- **2 consultorias**: Nathalia, Padaria (não viram squad)

## Personas (10 BR)

- **Vitor** (Winston BMAD) — Tech Lead/Arquiteto Squad Dev. Gate técnico, aprova merge final.
- **Amélia** (Amelia BMAD) — Dev Senior Orquestrador. Babysitting do código, audita subagentes, mergeia stories.
- **Paloma** (po AIOX, nova) — PO/Backlog Steward.
- **Sofia** (Sally BMAD) — UX.
- **Camila** (Quinn BMAD) — QA.
- **Paula** (Paige BMAD) — Documentação. Roda `/documentar` obrigatório no fim de cada feature.
- **Maria** (Mary BMAD) — Líder Marketing + Líder Produto.
- **João** (John BMAD) — Segunda opinião transversal, invocável via `/joao`.
- **Bruno** (Barry BMAD) — Quick-Dev opt-in.
- **Diego** (devops AIOX, nova) — Líder Squad Infra (única persona fora de Dev além de Maria).

**Descartados:** Bob (SM BMAD), aiox-master, data-engineer, squad-creator.

**Stamper absorve** 3 capabilities do aiox-master: IDS registry, validate-agents, orchestration explicit.

## Constitution (5 princípios append-only)

1. Executar, não pedir (CLI/API sempre).
2. Linear = fonte de verdade de projetos. Obsidian = fonte de documentação.
3. Processo existente vence ideia nova.
4. Não deletar sem autorização textual.
5. Não reorganizar sem pedido.

Leitura sob demanda (não vai no contexto inicial).

## DEV-WORKFLOW — 13 seções

1. Hierarquia BMAD (Plano → PRD → Epic → Story → Mise-en-place).
2. **Modo A (sequencial) ou Modo B (paralelo)** — agente SEMPRE pergunta, nunca default. Babysitting Amélia obrigatório nos 2 modos.
3. Gate Vitor antes da Amélia executar.
4. Loop de fix com cap de 3 ciclos — escala pra Vitor ou Felipe se esgotar.
5. Regras de paralelismo (Modo B): stories mesma epic = sequenciais salvo arquivos disjuntos; epics diferentes = paralelo; migration/auth/billing nunca paralelo.
6. Reviews por tipo de mudança: `/codex-review` = segunda opinião (código novo / bug difícil); `/runtime-fix-review` = mudança funcional; mudança crítica = 4 reviews + Vitor + Felipe.
7. Merge strategy: `feat/pdl-XX` → `feature/[feature]` → `main`.
8. Decisões técnicas registradas em `decisions.md` ao mergear cada story.
9. Subagentes — 2 tipos: leitor (read-only) vs executor (escrita escopada sob Amélia).
10. Pós-deploy Vercel/Railway + checklist VPS.
11. Rollback: hotfix branch ou `git revert`; nunca `git reset --hard` em main.
12. Linear updates obrigatórios — status (Planning/In Progress/Blocked/In Review/Done) + 7 momentos de comentário.
13. `/documentar` obrigatório antes de merge main (Paula roda, Vitor valida).

## Frameworks de referência

### BMAD (47 skills bmad-* + 8 personas)
- **Adotado:** Distillator (comportamento automático), Critical Actions hard-coded, Quick-Dev opt-in, 7 personas BR.
- **Descartado:** instalador NPX, party-mode, pipeline obrigatório, Bob (SM).

### AIOX Core (12 personas + features)
- **Adotado:** Constitution append-only, Session digest via PreCompact hook (modelo híbrido), Patterns + Gotchas por squad, YAML squad simplificado, Diego, Paloma, capabilities do aiox-master no Stamper.
- **Descartado:** SYNAPSE engine, ADE 7 epics, Agent Immortality, IDE sync multi-CLI, Bracketed loading L1-L5, Hook abstraction layer.

## Mecanismo de busca (Patterns + Gotchas + Incidentes)

- 1 script consolidado: `_core/lookup.py` parametrizado por source.
- v0 BM25 keyword (agora) → v1 embeddings (futuro).
- Auto-populate proposed → approved, nunca commit cego.
- Triggers: CLI direto, skill `/check-context`, hook UserPromptSubmit opt-in com whitelist enxuta.

## Skills

- **Globais** (`~/.claude/skills/`, 22): linear-*, claude-review, codex-review, gemini-review, runtime-fix-review, log-sessao, ja-fiz, ata-reuniao, busca-reunioes, transcrever-reuniao, registrar-notas, debug-polya, documentar, tally-form-custom, limpar-transcripts.
- **Stamper** (18): abrir-dia, fechar-dia, fechar-semana, chefe-de-staff, status, mandar-whatsapp, compartilhar-dados, etc.
- **Squad Marketing** (60): pipeline completo PD Marketing (yt-*, gerar-*, blog/reels/newsletter).
- **Squad Comercial** (10): proposta, touchpoint, reativação, abordagem-rep, em-conversa, ghl, agendar-call.
- **Squad Infra** (5): vps-master, vps-dev, conectar-vps, validar-deploy-vps, espelhar-repo-vps.
- **Squad Estudo** (8): sync-readwise, buscar-highlights, brief-leitura, nota-de-livro, etc.
- **Área Desenvolvimento** (10 mp-*): pendente alocação por produto.
- **Produto Cadência** (3): criar-tenant-agencia, tally-form-cadencia, cadencia-review-deploy.
- **Produto PD Portal** (5): portal-arquivos, portal-materiais, portal-setup-tenant, portal-videos, portal-wiki.

## 9 arquivos consolidados em `_core/`

| Arquivo | Função |
|---|---|
| INVENTORY.md | 139 skills locais classificadas |
| REFERENCE-BMAD.md | Leitura profunda BMAD v6.2.1 |
| REFERENCE-AIOX.md | Leitura profunda AIOX Core |
| REFERENCE-AIOX-PERSONAS.md | 5 personas AIOX restantes |
| SKILLS-IMPORT-MAP.md | 55 skills BMAD+AIOX alocadas |
| CONSTITUTION.md | 5 princípios append-only |
| PERSONAS.md | 10 personas BR + Stamper capabilities |
| DEV-WORKFLOW.md | Padrão dev completo proprietário |
| DECISIONS-PDL241.md | Consolidação 8 itens |

## Próximos passos

- **Fase 1 (PDL-220):** migrar Stamper + Critical Actions + PreCompact hook + lookup.py consolidado + absorver capabilities aiox-master.
- **Fase 2 (PDL-221):** popular squads operacionais com patterns.md + gotchas.md + Critical Actions + YAML squad CLAUDE.md simplificado.
- **Fase 3 (PDL-222):** popular produtos com personas (Maria, Vitor, Amélia, Paloma, Sofia, Camila, Paula, Diego) + estrutura dev seguindo DEV-WORKFLOW.
- **Futuro:** skill `/check-framework`, skill `/criar-squad`, skill `/linear-fechar-projeto`, lookup v1 com embeddings.

## Links

- Repo GitHub: https://github.com/felipeluissalgueiro/pd-framework
- Issue Linear: PDL-241
- Commits Fase 0.7 (2026-05-25): 8 no `main`

## Notas Relacionadas

- [[IA-Tecnologia/2026-05-23 PD Framework — arquitetura de squads e Stamper como orchestrator]]
- [[Projetos/PD Framework/PD Framework MOC]]

## Histórico

- 2026-05-25 — versão inicial, fechamento Fase 0.7 PDL-241.
