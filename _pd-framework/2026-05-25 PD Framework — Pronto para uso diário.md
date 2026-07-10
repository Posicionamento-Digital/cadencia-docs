---
date: 2026-05-25
tags: [ia, framework, pd, milestone, uso-diario]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Pronto para uso diário

> Sessão maratona 2026-05-25 (manhã→madrugada). Framework saiu de "estrutura desenhada" pra "pronto pra trabalhar diariamente dentro dele".

## Status final do dia

**5 Times bootstrappados (regra "criar com Felipe" seguida):**
- ✅ Marketing (PDL-253) — Maria líder + 4 sub-squads (Conteúdo/Brand/Performance + 3 aninhados Comunicação)
- ✅ Comercial (PDL-262) — Eduardo líder + 2 sub-squads (Geração Demanda + Geração Negócios)
- ✅ Dev (PDL-256) — 8 personas BR como Squads (Vitor/Amélia/Paloma/Sofia/Camila/Paula/João/Bruno)
- ✅ Infra (PDL-257 refator) — Diego DevOps+SecOps + foundation completo
- ✅ CS (PDL-265) — Letícia líder + 3 sub-squads (Onboarding/Relacionamento/Suporte com Bot Telegram aninhado)
- ✅ Financeiro (PDL-231) — monolítico, 9 foundation docs (DRE+NFSe+ciclo faturamento)
- ⏳ Cadência em curso (Squad pai + 4 sub-squads aninhados, sessão paralela rodando)

**Operacional:** decisão Felipe pular (empresa Felipe+Luiz, sem demanda RH/cerimônias)

## Conquistas técnicas hoje

### Skills criadas/refatoradas (15+)
- `/criar-squad`, `/abrir-squad`, `/fechar-squad` — squad lifecycle com Modo Foco + agregação A+B+C
- `/<time>-debate` em cada Time + `/debate` global cross-Time (PDL-255)
- 8 skills Linear integradas com Squad system (start/close/criar-projeto/etc) + v2 com Project Types
- `/documentar` — persona Paula, 3 destinos sincronizados
- `/rotacionar-credencial`, `/hardening-check`, `/restart-container` (PDL-259/260/261)
- 4 skills knowledge management globalizadas: `/brief-leitura`, `/highlights-para-conteudo`, `/nota-de-livro`, `/estudar-youtube`

### Infra de meta-framework
- Memory híbrida A+B+C determinística (state-aggregator.py — A manual, B on-demand, C cron noturno)
- 19 projetos Linear → Squads mapeados (linear-squad-map.json)
- 15 personas BR no catálogo (PERSONAS.md)
- Gotchas auto-detect script + 54 templates em todos os Squads
- Backup VPS Master artefatos prontos (sh + restore runbook + age encrypt)
- Cron state-aggregator artefatos prontos (deploy depende PDL-242 Fase 7)

### Migração legacy
- **352 auto-memories migradas** de 9 projetos pra Squads correspondentes:
  - Cadência: 124 entries
  - Marketing: 74 entries
  - Stamper: 69 entries (Felipe home + Estudo + raiz)
  - Comunicação: 5 entries (Insight + Site PD)
  - CS, PD Portal: 1 cada
  - Archive (openclaw 45, legacy-aula 23, recovery 10)
- Script sync-legacy-memories.py idempotente, não destrói originais

## Como trabalhar a partir de amanhã

### Setup
```powershell
code "C:\Users\felip\OneDrive\Documentos\ClaudeCode\Hub Projetos\pd-framework"
# Terminal integrado:
claude
```

Junction `.claude/skills` → `stamper/skills/` já configurada — todas skills do framework aparecem no autocomplete.

### Fluxo padrão
1. **Manhã:** `/abrir-dia` (Stamper) — Linear issues atribuídas + Daily Note + Calendar
2. **Quando trabalhar em área específica:** `/abrir-squad times/<area>` — carrega CLAUDE+STATE+L1 agregado
3. **Quando criar nova issue:** `/linear-criar-issue` ou `/linear-criar-projeto` (v2 com Project Types)
4. **Começar issue:** `/linear-start-issue PDL-XX` — auto-abre Squad + marca In Progress
5. **Decisões cross-Time:** `/debate marketing,comercial,dev` (party mode multi-Time)
6. **Decisões intra-Time:** `/<time>-debate` (party mode do Time)
7. **Fechar issue:** `/linear-close-issue PDL-XX` — propaga L1 pro Time pai
8. **Fim do dia:** `/fechar-dia` (Stamper)

### Onde está cada coisa
- Auto-memories antigas: indexadas via `python _core/lookup.py "<query>" --source memory`
- Sessions log histórico: `python _core/lookup.py "<query>" --source sessions`
- Incidents Hub: `python _core/lookup.py "<query>" --source incidents`
- Foundation docs por Time: `times/<time>/foundation/`
- Mapa completo paths externos: `_core/PATHS.md`

## Backlog pra outros dias

**Times pendentes (sessão guiada com Felipe):**
- Produto/Cadência (em curso agora)
- Produto/PD Portal, NSkin, GCI-GO, Consultorias, Cadência-Contato (1 por sessão)

**Issues Linear pendentes (backlog real):**
- PDL-254 — Redefinir porco-espinho (motor econômico atualizado)
- PDL-219 — Reorganizar pastas OneDrive (estrutural, decisão sua)
- PDL-242 — Fase 7 deploy VPS (Stamper na VPS Master)
- PDL-243 — Fase 8 auditoria credenciais
- PDL-244 — Knowledge Lookup v1 (embeddings semantic)
- PDL-223 — Fase 4 Auto-fix observabilidade
- PDL-225 — Fase 6 framework Luiz

## Refs

- Repo: github.com/felipeluissalgueiro/pd-framework
- Constituição: `_core/CONSTITUICAO-TIMES.md`
- Hierarquia: `_core/HIERARCHY.md`
- Memory schema: `_core/memory-schema.md`
- Paths externos: `_core/PATHS.md`
- Criação Time (briefing): `_core/CRIACAO-TIME-BRIEFING.md`

## Notas relacionadas

- [[IA-Tecnologia/2026-05-25 PD Framework — Constituição dos Times]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Hierarquia Time-Squad e memory híbrida]]
- [[IA-Tecnologia/2026-05-24 PD Framework — Mapa final e decisões consolidadas]]
