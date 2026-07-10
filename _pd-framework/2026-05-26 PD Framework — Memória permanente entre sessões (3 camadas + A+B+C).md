---
date: 2026-05-26
tags: [framework, memory, arquitetura, persistencia, sessao]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Memória permanente entre sessões

> Como o framework preserva contexto operacional entre sessões de trabalho. Mecanismo híbrido de 3 camadas + 3 mecanismos de atualização (A+B+C).

Relacionado:
- [[2026-05-25 PD Framework — Hierarquia Time-Squad e memory híbrida]] (decisão original do schema)
- [[2026-05-25 PD Framework — Constituição dos Times]] (foundation/STATE/CLAUDE)
- [[2026-05-25 PD Framework — Arquitetura DEFINITIVA consolidada]] (mapa completo)
- [[2026-05-25 Stamper — Chief of Staff PD Framework]] (orchestrator que usa essa memória)
- [[PD Framework — Como funciona (consolidado 2026-05-25)]] (overview operacional)

---

## 3 camadas de memória

| Camada | Onde mora | Quem escreve | Quem lê |
|---|---|---|---|
| **L1 — Time** | `times/<area>/STATE.md` | Só `aggregate_l1()` (determinístico) | Stamper ao abrir Time |
| **L2 — Squad** | `times/<area>/<squad>/memory/STATE.md` | Persona do Squad | Persona ao abrir Squad |
| **L3 — Histórico append-only** | `times/<area>/<squad>/memory/journal.md` + `decisions.md` | Persona ao fechar issue/decisão | Lookup sob demanda |

**L1 é um SQL VIEW** — nunca editado a mão. Agregação determinística dos L2/L3 abaixo. Em conflito, L1 é descartado e recalculado.

**L2 é o estado vivo** — o que o Squad está fazendo agora, decisões recentes (últimas 2 semanas), problemas abertos. Sobrescrito com frequência.

**L3 é a memória de longo prazo** — append-only. Toda decisão arquitetural, gotcha pego em produção, sessão importante vira entry. Cresce pra sempre, nunca apaga.

### Memória paralela do Stamper

Além das 3 camadas estruturais, o Stamper mantém auto-memory pessoal em `stamper/memory/`:
- `session_*.md` — log de sessões cross-Squad
- `feedback_*.md` — correções e validações do Felipe
- `user_*.md` — perfil/preferências Felipe
- `project_*.md` — estado de iniciativas multi-Squad

Esse é o auto-memory tradicional do Claude Code, paralelo à memória por Squad.

---

## 3 mecanismos de atualização — esquema A+B+C

### A — Manual (`/fechar-squad`)
Ao fim de sessão de trabalho num Squad, persona daquele Squad:
1. Lê o que aconteceu na sessão
2. Atualiza L2 (sobrescreve estado atual)
3. Append em L3 (decisões + journal)
4. Re-roda `aggregate_l1()` pra atualizar STATE do Time pai

**Disciplina humana.** Garante consistência se feito.

### B — On-demand (`/abrir-squad`)
Ao abrir Squad em nova sessão, antes de carregar contexto:
1. Verifica se L1 do Time pai está stale (>24h sem atualização)
2. Se sim, dispara `aggregate_l1()` pra recalcular do L2+L3 atual
3. Carrega L1 fresco + L2 do Squad + foundation

**Lazy recompute.** Pega caso "esqueci de fechar ontem".

### C — Cron noturno (state-aggregator)
03h BRT na VPS Master (cron `0 6 * * *` UTC), roda `aggregate_l1()` pra **todos os Times**:
1. Varre `times/*/`
2. Recalcula cada L1 do zero
3. Se diff, commit automático: `chore(state): aggregation cron noturno YYYY-MM-DD`
4. Push pra origin
5. Local + VPS Dev pull no próximo `git pull`

**Fallback garantido.** Mesmo se A e B falharem semanas, L1 está sempre <24h desatualizado.

Script: `times/infra/workers/state-aggregator-cron.sh` → chama `_core/state-aggregator.py`. Log em `/var/log/pd-framework/state-aggregator.log`. Logrotate 14d.

---

## Fluxo prático — como um Squad lembra entre sessões

**Cenário:** trabalho hoje no Squad Cadência/frontend, abro amanhã.

### Hoje
- Entreguei PDL-487 (botão Esqueci Senha)
- Decidi usar `auth.resetPasswordForEmail()` Supabase em vez de endpoint custom
- Encontrei gotcha: RLS policy precisa exception pra anon na tabela `users`

Rodo `/fechar-squad times/produto/cadencia/frontend/`:
- `memory/STATE.md` atualizado — "última sessão 2026-05-26, PDL-487 entregue, próximo foco PDL-488"
- `memory/decisions.md` recebe append — "2026-05-26 — Reset password via Supabase nativo. Why: menos código manter, security já testada"
- `memory/journal.md` recebe append — "PDL-487 fechada em 1h30, gotcha RLS anon"
- `gotchas.md` recebe entry — "RLS policy users precisa anon exception em fluxos reset"
- `aggregate_l1()` roda → atualiza `times/produto/STATE.md`

### Amanhã
Abro nova sessão, digito `/abrir-squad times/produto/cadencia/frontend`:
- Stamper carrega `CLAUDE.md` (manual operacional do Squad)
- Carrega `foundation/*` (princípios não-negociáveis)
- Carrega `memory/STATE.md` (estado vivo — "ontem fiz X, próximo Y")
- Carrega `decisions.md` últimas 10 entries
- Carrega `gotchas.md`

Agente já chega com contexto completo. Eu não explico "ontem trabalhei em auth" — ele sabe.

---

## Lookup retroativo

Pra buscar algo enterrado em qualquer Squad/Time/incident/sessão:

```bash
python _core/lookup.py "rls supabase reset"
```

Varre incidents centralizados + sessions log + memory de todos os Squads + gotchas. Retorna trechos relevantes ranked. Uso antes de operação sensível ("já passei por isso?").

---

## Diferença pro auto-memory tradicional do Claude Code

| Aspecto | Auto-memory tradicional | PD Framework |
|---|---|---|
| Granularidade | 1 caixa por projeto | 1 memory por Squad |
| Crescimento | Linear até estourar contexto | Particionada — Squad carrega só o que precisa |
| Histórico | MEMORY.md + arquivos soltos | L2 vivo + L3 append-only separados |
| Determinismo | Manual via Edit/Write | `aggregate_l1()` determinística |
| Fallback | Nenhum (se esquecer, perdeu) | A+B+C — 3 mecanismos redundantes |
| Cross-context | Tudo misturado | Stamper memory paralela cobre cross-Squad |

Escala pra dezenas de Squads sem inflar contexto. Dev no Squad Cadência/frontend não carrega memória do Squad Comercial/Eduardo. Stamper carrega só o que cruza fronteiras.

---

## Onde isso vive (arquivos chave)

| Arquivo | Função |
|---|---|
| `_core/memory-schema.md` | Spec completo do schema A+B+C |
| `_core/state-aggregator.py` | Função `aggregate_l1()` (208 linhas, determinística) |
| `_core/HIERARCHY.md` | Regras de hierarquia Time → Squad → Sub-squad |
| `_core/CONSTITUICAO-TIMES.md` | Doc fundador (250 linhas) — `CLAUDE/foundation/memory` |
| `times/infra/workers/state-aggregator-cron.sh` | Wrapper cron VPS Master |
| `stamper/skills/abrir-squad/SKILL.md` | Mecanismo B |
| `stamper/skills/fechar-squad/SKILL.md` | Mecanismo A |

---

## Histórico de evolução

- **2026-05-25 manhã** — schema A+B+C decidido na sessão de design ([[2026-05-25 PD Framework — Hierarquia Time-Squad e memory híbrida]])
- **2026-05-25 noite** — foundation/ separado da memory (docs constitutivos ≠ estado vivo) ([[2026-05-25 PD Framework — Constituição dos Times]])
- **2026-05-25/26** — `aggregate_l1()` implementada, smoke real bem-sucedido, 352 entries legacy migradas
- **2026-05-26 madrugada** — Cron noturno deployado na VPS Master, fix timezone (`0 6` UTC = 03h BRT)
- **2026-05-26 manhã** — pd-framework-dev (versão reduzida pro Luiz) com mesma arquitetura de memória — ver [[2026-05-26 Guia pd-framework-dev — Como usar no dia a dia]]
