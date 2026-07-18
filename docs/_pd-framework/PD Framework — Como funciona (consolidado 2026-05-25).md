---
date: 2026-05-25
tags: [ia, framework, pd, playbook, master]
moc: "[[MOC-IA-Tecnologia]]"
---



# PD Framework — Como funciona (playbook consolidado)

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


> Mapa visual: [[PD Framework — Mapa Visual Master.canvas]]
> Constituição: `pd-framework/_core/CONSTITUICAO-TIMES.md`
> Snapshot fim do dia 2026-05-25.

---

## Conceito em 1 frase

Monorepo multi-agente onde o **Stamper** (Chief of Staff Felipe) orquestra **Times** (áreas da empresa) compostos por **Squads** (sub-áreas) com personas, skills, foundation docs e memory hierárquica.

---



## Hierarquia

```
pd-framework/
├── stamper/                ← orchestrator único
├── _core/                  ← runtime compartilhado (HIERARCHY, memory-schema, etc)
├── _shared/                ← Python wrappers (stevo, linear, obsidian, ghl, op, supabase, vercel)
├── times/                  ← áreas da empresa (Time → Squad → Sub-squad)
│   ├── marketing/          (Maria + 4 sub-squads)
│   ├── comercial/          (Eduardo + 2 sub-squads)
│   ├── cs/                 (Letícia + 3 sub-squads + bot-telegram aninhado)
│   ├── dev/                (8 personas BR = 8 Squads)
│   ├── infra/              (Diego — monolítico)
│   ├── financeiro/         (monolítico)
│   └── produto/
│       └── cadencia/       (Catarina + SOUL + 3 sub-squads + features/blog)
└── _archive/               (descontinuados — openclaw, recovery-hertzner, legacy-aula)
```

**Regra de hierarquia:** tem `CLAUDE.md`? É Squad. Sem? Component/Feature (sem memory própria).

---

## Anatomia de um Time

5 elementos canônicos:

| Pasta | Conteúdo | Muda quando |
|---|---|---|
| `CLAUDE.md` | Manual operacional agente | Raramente |
| `memory/` | STATE (vivo L1/L2/L3) + decisions (append-only) | Toda sessão |
| `foundation/` | Docs constitutivos (ICP, posicionamento, narrativa, brand, etc) | Pivot/rebrand |
| `context/` | Refs técnicas profundas | Mudança técnica |
| `skills/` + `workers/` | Automações interativas + determinísticas | Conforme demanda |

Produtos adicionalmente têm `SOUL.md` (identidade imutável — missão/voz/valores/visual/princípios técnicos).

---



## Memory híbrida A+B+C (determinística)

Time pai precisa saber estado dos Squads filhos. **3 mecanismos, mesma função `aggregate_l1()`**:

- **A — Manual** (`/fechar-squad`): propaga L1 pro Time pai cascateado
- **B — On-demand** (`/abrir-squad <time>`): calcula L1 ao vivo (sem escrita)
- **C — Cron noturno** (03h BRT): fallback automático idempotente (artefato pronto, deploy PDL-252 depende PDL-242 Fase 7)

Mesma função core garante consistência cross-mecanismo. Cron só reescreve se diff real.

---

## Personas BR (15 catalogadas em `_core/PERSONAS.md`)

| Time | Personas |
|---|---|
| Marketing | Maria (líder), Pedro (tráfego — Pedro Sobral), Rafael (social — Kizo) |
| Comercial | Eduardo (líder — Cauduro), Mafê (LDR), Roberto (Closer) |
| CS | Letícia (líder — Lincoln Murphy/Nick Mehta) |
| Dev | Vitor (Tech Lead), Amélia (Sr Orquestrador), Paloma (PO), Sofia (UX), Camila (QA), Paula (Tech Writer), João (PM transversal), Bruno (Quick-Dev) |
| Infra | Diego (DevOps+SecOps) |
| Produto/Cadência | Catarina (PM/Owner — Marty Cagan + Teresa Torres) |

Personas têm voz distinta + tensão produtiva entre si — usado em `/<time>-debate` (party mode intra-Time) e `/debate` (cross-Time).

---



## Fluxo padrão do dia

1. **Manhã** — `code pd-framework` + `claude` + `/abrir-dia`
   - Stamper monta plano: Linear issues atribuídas + Daily Note Obsidian + Google Calendar
2. **Trabalhar numa área** — `/abrir-squad times/<area>`
   - Carrega CLAUDE + STATE L1/L2 + foundation relevante
3. **Iniciar issue** — `/linear-start-issue PDL-XX`
   - Resolve Squad dono → auto-invoca `/abrir-squad` → checkout branch repo correto → marca In Progress → registra na [L2]
4. **Trabalhar no código** — edits acontecem no repo do produto (cadencia-app, pd-portal, etc), MAS dentro da sessão do framework (skills do framework continuam disponíveis)
5. **Decisões complexas** — `/debate <times>` (cross-Time) ou `/<time>-debate` (intra-Time)
6. **Documentar feature** — `/documentar-software <feature>` (4 destinos sincronizados: MDs + Wiki + Canvas + Playbook)
7. **Fechar issue** — `/linear-close-issue PDL-XX`
   - Commit "Closes PDL-XX" + merge main + deploy + remove [L2] + propaga L1 pro Time pai
8. **Encerramento** — `/fechar-dia` (Stamper scorecard) + `/log-sessao` se sessão grande

---

## Integração Linear ↔ Squad

Toda issue/projeto tem UM Squad dono. Resolução em cascata:

1. Label `squad:<path>` na issue (override)
2. `_core/linear-squad-map.json` por `project_id` (19 projetos mapeados)
3. Sem dono → skill pergunta + oferece `/criar-squad`

8 skills Linear v2 integradas (criar/start/close/planejar/brief/atualizar/gestao). Project Types: 6 tipos (Cliente CRM-PD, Iniciativa interna, Novo produto, Feature, Operacional, Sprint temporário).

---



## Knowledge Lookup

Antes de operações sensíveis (deploy, drop, SSL, DNS, migration, debug):

```bash
python pd-framework/_core/lookup.py "<keywords>"
```

Cobertura:
- **sessions** — 38+ dias de logs (`Rotina/sessions-log/`)
- **incidents** — 49+ incidents (`Hub Projetos/Incidentes/`)
- **memory** — 63 entries pessoais Stamper + 352 legacy migradas de 9 projetos (sync 2026-05-25)
- **gotchas** — 54 templates (auto-detect script pronto, propostas em `gotchas-pending.md` aguardam aprovação humana)

---

## Skills disponíveis (resumo — 70+)

**Lifecycle Squad/Time:** `/criar-squad`, `/abrir-squad`, `/fechar-squad`

**Stamper dia a dia:** `/abrir-dia`, `/fechar-dia`, `/fechar-semana`, `/log-sessao`, `/status`, `/ja-fiz`, `/mandar-whatsapp`, `/agendar-call`, `/ata-reuniao`, `/busca-reunioes`, `/transcrever-reuniao`, `/chefe-de-staff`

**Linear v2:** `/linear-criar-issue`, `/linear-criar-projeto`, `/linear-gestao-atividades`, `/linear-start-issue`, `/linear-close-issue`, `/linear-planejar-issue`, `/linear-brief`, `/linear-atualizar-issue`

**Code review:** `/codex-review`, `/claude-review`, `/gemini-review`, `/runtime-fix-review`, `/debug-polya`

**Documentação:** `/documentar-software` (destino: cadencia-docs — fonte de verdade cross-time)

**VPS / Infra:** `/vps-master`, `/vps-dev`, `/conectar-vps`, `/espelhar-repo-vps`, `/validar-deploy-vps`, `/rotacionar-credencial`, `/hardening-check`, `/restart-container`

**Knowledge management (globais):** `/brief-leitura`, `/highlights-para-conteudo`, `/nota-de-livro`, `/estudar-youtube`, `/leituras-para-aqui`

**Debate (party mode):** `/debate` (cross-Time, escolhe Times via argumento), `/<time>-debate` (intra-Time — marketing/comercial/cs/dev/infra/cadencia)

**Personas invocáveis transversais:** `/joao` (challenger Dev), `/paula` (ref pra /documentar-software), `/bruno` (Quick-Dev modo opt-in)

**Produto-specific:** `/criar-tenant-agencia` (Cadência), `/tally-form-cadencia` (briefing marca), `/tally-form-briefing-cs`, `/compartilhar-nota`, `/despublicar-nota`

---



## Status atual (2026-05-25 madrugada)

**Times bootstrappados (6 + Cadência):**
- ✅ Marketing (PDL-253)
- ✅ Comercial (PDL-262 + Sistema Comercial PD futuro PDL-263/264)
- ✅ Dev (PDL-256)
- ✅ Infra (PDL-257 refator)
- ✅ CS (PDL-265)
- ✅ Financeiro (PDL-231)
- ✅ Produto/Cadência (PDL-232 + 237/238/239/240)
- ❌ Operacional (PDL-230 cancelado — empresa Felipe+dev externo sem demanda)

**Produtos pendentes (sessão guiada com Felipe):**
- PD Portal (PDL-233)
- NSkin (PDL-234)
- GCI-GO (PDL-235 — Lara + Ecuro + Confirmação Agenda)
- Consultorias (PDL-236 — Nathalia + Padaria)
- Cadência-Contato

**Fases pendentes:**
- Fase 0.5 (PDL-219) — reorganizar pastas OneDrive
- Fase 3 (PDL-222) — Squad Produto completo
- Fase 4 (PDL-223) — Auto-fix observabilidade
- Fase 4.5 (PDL-244) — Knowledge Lookup v1 com embeddings
- Fase 6 (PDL-225) — pd-framework-luiz
- Fase 7 (PDL-242) — Clone VPS Dev + Master deploy final
- Fase 8 (PDL-243) — Auditoria credenciais vazadas

---

## Onde está cada coisa

Mapa completo de paths externos: `pd-framework/_core/PATHS.md`

**Resumo:**
- Vaults Obsidian: `C:\Users\felip\Vaults\{Pessoal, Time PD}`
- Repos código produtos: `Hub Projetos\Projetos BMAD\Cadencia\` + `ClaudeCode\pd-portal\` + `Hub Projetos\_repos\` + na VPS Master `/opt/` ou `/root/`
- Skills globais Claude Code: `~/.claude/skills/`
- 1Password: `op` CLI + SA headless via `OP_SERVICE_ACCOUNT_TOKEN`
- Histórico: indexado via `_core/lookup.py`

---



## Comandos de setup nova máquina

```powershell
# Clone repo
cd C:\Users\felip\OneDrive\Documentos\ClaudeCode\Hub Projetos\
git clone https://github.com/felipeluissalgueiro/pd-framework.git
cd pd-framework

# Junctions skills (3 grupos)
mkdir .claude -Force
cd .claude
cmd /c "mklink /J skills ..\stamper\skills"
cd ..

cd stamper\skills
foreach ($s in @("vps-master","vps-dev","conectar-vps","espelhar-repo-vps","validar-deploy-vps")) {
  cmd /c "mklink /J $s ..\..\times\infra\skills\$s"
}
cd ..\..

# Setup encoding (UTF-8 sempre)
$env:PYTHONIOENCODING="utf-8"

# Validar
python _core/lookup.py "test" --source memory
```

Detalhes: `pd-framework/docs/setup-skills-junction.md`

---

## Notas relacionadas

- [[IA-Tecnologia/2026-05-25 PD Framework — Pronto para uso diário]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Constituição dos Times]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Hierarquia Time-Squad e memory híbrida]]
- [[IA-Tecnologia/2026-05-24 PD Framework — Mapa final e decisões consolidadas]]

## Refs canônicas no repo

- `CONTEXT.md` raiz — arquitetura completa
- `_core/CONSTITUICAO-TIMES.md` — doc fundador (anatomia Time/Squad)
- `_core/HIERARCHY.md` — níveis 3/4/5
- `_core/memory-schema.md` — STATE bracketed + A+B+C
- `_core/CRIACAO-TIME-BRIEFING.md` — Modo Foco pra criar Time
- `_core/SKILLS-LINEAR-INTEGRATION.md` — padrão Linear↔Squad
- `_core/PERSONAS.md` — 15 personas BR
- `_core/PATHS.md` — paths externos completos
