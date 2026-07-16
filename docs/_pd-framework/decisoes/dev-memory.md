---
type: source
source_kind: decisao
date:
entities: ["[[Cadencia]]", "[[Central de Observabilidade]]", "[[PD Framework]]", "[[comercial]]", "[[dev]]", "[[meeting-transcriber]]", "[[qualidade]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

# Decisões — dev-memory

# Decisões — Time Dev

(append-only — decisões relevantes ficam aqui, mais recente em cima)

---

## 2026-07-07 — Gate arquitetural: Automação do pacote pós-kickoff CS (8 Epics, projeto ff96e3e2)

**Contexto:** CS executou manualmente, com envio real a cliente pagante (OP Odontopenha), o pacote pós-validação de prompt (manual + roteiro de testes + formulário feedback + envio email/WhatsApp + link agendamento + credenciais + registro CRM). Objetivo: automatizar dentro do wizard `/ativar-cliente`. Gate Vitor antes da Amélia executar (Modo A, branch única `feature/automacao-pos-kickoff-cs`).

**Verificação do estado real (não confiei nas premissas do brief):**
- Reais na main: `_shared/email_templates.py` (render/send, canais email+whatsapp), `_shared/evo_client.py`, `_shared/cliente_registry.py`, templates `05a-validacao-prompt` (email+whatsapp) já commitados.
- **`tally_builder.py` NÃO está em `_shared/`** — vive em `~/.claude/scripts/tally_builder.py` (script global, não versionado no framework, não importável por worker).
- **`merge_template.py` (DEV-1227) só na branch `feat/dev-1227`, contaminada** com trabalho do motor-deploy (Dockerfile, session_lock, motor_run, new_isolated_session). Não é PR limpo.

**Decisões:**

1. **Orquestrar wrappers existentes — NÃO construir engines novas. Aprovado.** O trabalho é encadear peças prontas, não reinventar. Rejeitado qualquer "engine" nova de email/tally/whatsapp.

2. **Lar da orquestração = módulo-biblioteca `times/cs/workers/pos_kickoff/` (pacote), NÃO dentro de `/ativar-cliente` nem `StandingOrder` cron.** É invocado interativamente pelo wizard, não por cron → não é `StandingOrder`. O wizard chama uma fachada fina; a lógica fica em funções-passo idempotentes, testáveis fora do wizard. Regra 5 do Time (Modo B proibido) já se aplica porque os Epics compartilham esse módulo → **branch única obrigatória** (confirma Modo A).

3. **Contrato entre Epics = 1 dataclass `PosKickoffContext` (dados) + assinatura de cada função-passo (função).** Contexto carrega `tenant_id`, `slug`, contato, URLs (form Tally, docs Quartz, agendamento Cal.com, credenciais). Cada Epic entrega uma função-passo `(ctx) -> ctx'`; DEV-1219 apenas fia no wizard.

4. **Idempotência + resumabilidade obrigatórias** (precedente: wizard/demo já foi interrompido no meio). Checkpoint por cliente em `times/cs/state/pos-kickoff/<slug>.json` (estado de framework, versionado como STATE.md). Cada passo: checa estado → skip se feito → executa → grava. Sem infra nova.

5. **`tally_builder` promovido a `_shared/tally_builder.py` consumindo token via `_shared.secrets`** (SECRETS-PATTERN) — nunca `op` subprocess direto. Deixa de ser script solto e vira dependência importável.

6. **DEV-1227 rescopado + saneado:** (a) entrega muda de PDF/HTML → **publicação Obsidian/Quartz** (Mermaid renderiza nativo, validado); (b) extrair da branch contaminada só `_shared/merge_template.py` + `_shared/test_merge_template.py` + `times/cs/foundation/templates-documentos/*` via cherry-pick para a feature branch limpa — o resto de `feat/dev-1227` (motor-deploy) NÃO entra.

7. **Rebaixamentos:** **DEV-1237 → story/chore** (só wrap do tally_builder + `criar_form_feedback(ctx)`; 3 stories over-decompostas). **DEV-1241 permanece Epic mas simplificado** (orquestração pura de wrappers prontos; 5 stories é excesso — consolidar). Os demais (1232/1247/1252/1258) seguem como Epic.

8. **Gates duros não-negociáveis:** (a) DEV-1241 (envio) **passa por `cliente_registry`** antes de qualquer send — anti-envio-a-lead; (b) qualquer chamada a `cadencia-cli` **recarrega token via `op` a cada invocação** (gotcha DEV-1164 — env stale 401); (c) DEV-1232 se tocar migration/schema → reviews críticos completos (§6), não é trivial.

**Ordem de execução aprovada:** 1237 → 1227(rescopado) → 1241 → 1232 → 1247 → 1252 → 1258 → 1219 (mantida a proposta; 1232 é backbone dos blocos de fase seguintes, fica antes de 1247/1252/1258 ✓).

**Reviews:** cada Epic ao fechar → `/openrouter-review`; feature consolidada antes de merge → `/claude-review` + gate Vitor; DEV-1232 se schema → cascata crítica. **Merge em main só com autorização textual do Felipe** (abre PR + notifica).

**Quem decidiu:** Vitor (gate arquitetural) + Felipe (Modo A autorizado).

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-07-07 — DEV-1213: `max_rows` do PostgREST sobrepõe `.limit()` do client — regra vale pra qualquer produto

**Resumo:** Kanban de Oportunidades do Cadencia perdia opportunities silenciosamente (tenant com 1655 linhas, cap real do PostgREST em `max_rows=1000`, `.limit(5000)` do client não tem efeito nenhum acima desse cap). Fix: paginação real com `.range()` em loop. Detalhe técnico completo em `times/dev/vitor/memory/decisions.md` (2026-07-07).

**Regra pra qualquer squad de produto:** antes de escrever `.select(...).limit(N)` numa tabela que cresce por tenant (contacts, opportunities, activities, content_ideas etc.), checar se N pode superar 1000 — se sim, paginar com `.range()`, nunca assumir que `.limit()` alto resolve.

**Quem decidiu:** Vitor + Felipe.
## 2026-07-07 — Fila do Motor separada (`own:motor`) da fila de bug reativo (`own:agente`) — DEV-1218

**Contexto:** ao decidir apontar o motor pra um backlog real (Central de Observabilidade), a leitura da doc revelou que o motor consumia **a mesma label `own:agente`** que o `autofix_worker` (CAD-689) — o executor que a Central já usa pra bug de código (`health_check` `fix:issue` → `own:agente` → autofix abre PR). Dois executores concorrentes na mesma fila. Não era "bug vs feature": era colisão de fila.

**Decisão (Felipe, opção B — coexistir, não unificar):** duas filas, dois executores, dois propósitos.
- `own:agente` → `autofix_worker` (plantão de **bug reativo**, /15min VPS Dev) — **intacto**.
- `own:motor` → **Motor** (trabalho **planejado/proativo** — "issues chatas que tomam tempo e não geram valor") — nova label workspace (`668bc0c4-2c88-41b4-8bed-c5b815ca71a2`).

**Rationale (dele):** analogia de dois times — um cuida de bug, outro faz issue chata. Fila única faria trabalho relevante esperar atrás de uma fila longa; duas filas é mais eficiente. **Rejeitado** unificar (opção A) mesmo o Motor sendo tecnicamente a generalização do `autofix_worker`.

**Implementação:** `motor_select.py` usa `own:motor` em fila/candidatos/enqueue; auto-enqueue ganha **denylist** (`tipo:bug` → autofix, `own:agente`/`own:felipe`/`own:luiz`/`aguardando-felipe` → outro dono) — mas `eligible_queue` NÃO filtra a denylist: curadoria manual pode aplicar `own:motor` até num bug (override intencional). A skill `/planejar-fila-motor` (DEV-1215, já na main pelo #36) foi convertida pra `own:motor`. Salvaguarda de overlap: `linear_claims` impede dois donos ativos. Docs: `MOTOR-AUTONOMO.md` + `health_check/README.md`.

**Gotcha da sessão:** meu 1º PR (#37) partiu de uma main antiga (pré-#35/#36/#31) e conflitou — a DEV-1215 (fila manual + skill) já tinha sido mergeada nesse meio-tempo, em `own:agente`. Refeito sobre a main atual, absorvendo a fila manual e convertendo skill+manual-queue pra `own:motor`. Lição: em worktree de sessão longa, conferir se a main avançou antes de assumir o PR mergeável.

**Multi-repo (clone sob demanda no container, pra o motor rodar em cadencia-app etc.):** Felipe quer, mas é issue de deploy à parte — não entra aqui.

**Quem decidiu:** Felipe (guiado, com a doc da Central lida antes — a leitura mudou o diagnóstico de "bug/feature" pra "colisão de fila").

---

## 2026-07-06 — Deploy do Motor Autônomo: 5 decisões de arquitetura (VPS Dev, padrão framework)

**Contexto:** motor rodava local no Windows (teste noturno), abrindo consoles e comendo recursos da máquina do Felipe. Decidido tirar do local e dar um lar adequado. A conversa passou por isolamento (user/container), capacidade (VPS Dev era KVM1 saturada), e como integrar ao padrão de deploy da PD sem virar exceção. Antes de extrair o motor pra repo próprio, Felipe pediu relembrar por que ele mora no framework — e a razão invalidou a extração.

**Decisões (5):**

1. **Motor permanece em `_core/` — NÃO extrair pra repo próprio.** Razão: é fundação **runtime-agnóstica** (D5 do brainstorm ruflo — agente↔estado via CLI, operável por Claude/Codex/OpenCode/workers Master), reusa toda a plumbing (`_core/runtime/*`, hooks, `MODEL-MAP`, `budget_guard`, `outcomes`, `linear_claims`, `squad_resolver`) sob o invariante "diff zero em `_core/`", e o kill switch é a branch `motor-state` do próprio repo. Extrair quebraria os três. **Rejeitada** a proposta inicial de repo `pd-motor`.

2. **Deploy = padrão do FRAMEWORK, não de PRODUTO.** A PD tem 2 padrões: produtos (repo próprio + Coolify on-commit) e framework (repo único + `git pull` + serviço). O motor é framework → container na VPS Dev + **auto-`git pull` da main por ciclo** + kill switch OFF. **Rejeitado** Coolify on-commit (torrente de commits rebuildaria à toa; motor commita em si mesmo → loop; `_core/` é classe crítica → contornaria alçada). Auto-pull respeita a alçada naturalmente: o gate é no merge pra main, o pull só pega o aprovado.

3. **VPS Dev upgraded KVM1→KVM2** (2 vCPU / 8 GB). Motor roda em **container com `--cpus=1 --memory=2g`** — confina a 1 core, deixa o outro pro dev interativo do Felipe/Luiz. Causa da limitação de CPU da Hostinger era 1 vCPU saturado (load 7); resolvida pela capacidade. Upgrade preserva dados (resize, não reinstala — desde que não troque o SO).

4. **Fallback na VPS = `claude → codex`** (ambos assinatura, logados no user felipe). `opencode-local` (Ollama/free) fica **só pra execução local** — a VPS Dev não tem GPU. opencode instalado lá mas dormente.

5. **Migrar Coolify da Master → PROJETO SEPARADO.** Não misturar produção (Coolify orquestra 17 containers) com agente tool-use (motor) no mesmo box — viola a separação determinística/agente do `SECURITY.md §1` (mesmo daemon Docker = motor alcançaria containers de produção). Master saturada é problema real, mas se resolve à parte, com brief próprio.

**Próximo passo:** PRD do mini-projeto de deploy (containerização + runtime VPS Dev + auto-pull + secrets/auth + cap de recursos + validação OFF), dentro do projeto "PD Framework V2.0 — Motor Autônomo 24/7".

**Gotchas da sessão:** `pkill -f "device-auth"` casa a própria conexão SSH inline → mata a si mesmo (exit 255); usar critério que não case o comando. SSH inline sem `bash -lc` não carrega PATH do nvm (claude/codex "command not found"). `codex login --device-auth` evita o callback `localhost:1455` (que exigiria túnel SSH). Vault 1P **`Hostinger VPS`** existe na conta do `op` da VPS Dev (não no SA local do Felipe). Token GHL do Luiz exposto em texto claro no `ps` (arg de comando) — vale corrigir pra stdin/env.

**Quem decidiu:** Felipe (todas guiadas, com confronto adversarial em cada opção).

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-07-06 — Trigger do corpus (DEV-1164) vive no C6 close_session, não num git-push hook

**Contexto:** a issue pedia "hook no git push" pra sincronizar o corpus, mas não existe hook de git push no framework (só Claude Code hooks). Precisava ser agnóstico de runtime (Felipe: "tem que ser lido por qualquer harness — Codex, OpenCode, não só Claude").

**Decisão:** o trigger dispara em `_core/hooks/stop-session-branch.py` (C6 close_session), o ponto de merge-pra-main onde **os 3 runtimes convergem** — Codex (`stop.py`→`close_session.py`→`stop-session-branch.py`) e OpenCode (`lifecycle.ts`→`close_session.py`→idem) delegam ao mesmo script. Um ponto de inserção cobre todos. Dispara destacado (não-bloqueante), best-effort.

**Alternativas descartadas:** `.git/hooks/pre-push` (não versionado, cada clone precisa setup; push é separado do merge local) · instrumentar cada skill (frágil).

**Impacto:** padrão pra qualquer capacidade que rode "ao consolidar trabalho" — inserir no C6 compartilhado, não num hook de runtime específico. Gotcha do PAT na memória `reference-corpus-framework-supabase` (env stale sombreia o mapa 1P → alias `SUPABASE_HUBPD_PAT`; sempre `_shared.secrets`, nunca `op` direto).

**Quem decidiu:** Felipe (requisito agnóstico) + análise da cadeia de delegação dos adapters.

---

## 2026-07-06 — Slack por squad (DEV-1165): consulta-primária → Claude Tag + MCP read-only; bridge adiado

**Contexto:** 1 canal Slack por time. Decisão em aberto: Claude Tag nativo (pronto, cego ao framework) vs bridge self-hosted (integrado, infra a manter). Felipe esclareceu: uso é **consulta** ("conversar com cada time como membros da empresa"), NÃO ação — coda via Termius, Slack pra codar é horrível.

**Decisão:** quando construir → Claude Tag nativo + **MCP read-only do framework** (STATE do squad + query no corpus DEV-1164 + lookup). Consulta read-only → some o buraco de segurança que rejeitava o Claude Tag (ação bypassando guards). Bridge só se surgir necessidade real de ação via Slack. **Fica em backlog** — uso indefinido; construir >1 semana sobre uso incerto viola análise-antes-de-codar.

**Alternativas descartadas (por ora):** bridge self-hosted agora (overkill) · Claude Tag puro sem MCP (cego aos squads).

**Impacto:** pré-requisito quando destravar = MCP read-only do framework (transporte-agnóstico). Detalhe no comentário da DEV-1165.

**Quem decidiu:** Felipe.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-07-04 — Sofia ganha skills Astryx para planejamento e bancada Storybook

**Contexto:** depois de rodar o Storybook do Astryx localmente, Felipe definiu que o Time Dev deve aproveitar componentes/bibliotecas prontas, mas adaptando com identidade Cadência em vez de copiar visual genérico.

**Decisão:** criar skills no Squad Sofia: `/astryx-storybook` para subir/abrir/testar componentes no Storybook e `/astryx-planejar-ui` para planejamento UX React/Next com Astryx-first. Storybook vira bancada visual da Sofia para mostrar componentes a Felipe durante planejamento.

**Validação usada como base:** `pnpm install`, `pnpm -F @astryxdesign/core build`, `pnpm storybook` em `http://localhost:6006/` com HTTP 200. Gotchas Windows registrados nas skills.

**Impacto:** em próximas UIs Cadência, Sofia deve primeiro consultar Astryx para componentes/templates e depois especificar tema/ajuste de identidade Cadência antes de handoff para Vitor/Amélia.

**Quem decidiu:** Felipe + Sofia/Vitor.

---

## 2026-07-04 — Astryx incorporado ao Time Dev como referência UX da Sofia

**Contexto:** Felipe forkou `facebook/astryx` em `felipeluissalgueiro/astryx` e pediu que o repo fosse clonado localmente e na VPS Dev, além de incorporar Astryx no modo de trabalho da Sofia para próximas UIs.

**Decisão:** `astryx` vira repo de referência do Time Dev para UX/UI React/Next, sob responsabilidade da Sofia. Local: `C:/dev/astryx`; VPS Dev user Felipe: `/home/felipe/astryx`; label operacional: `repo:astryx` em `_core/REPO-MAP.md`. Sofia aplica Astryx-first em novas UIs, com gate de compatibilidade por produto e sem migração automática de telas existentes.

**Impacto:** próximos planos de UI devem consultar `times/dev/sofia/context/astryx-ui-standard.md` antes de escolher componentes/templates. Vitor ainda decide stack; Amélia/Luiz implementam; Sofia define fluxo, consistência e critério visual.

**Quem decidiu:** Felipe + Sofia/Vitor.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-07-03 — Auto-cost em delta por fonte + estado canônico no claims + decay fiado no Stop (validação viva)

**Contexto:** Validação e2e do Motor v2 nos 3 harnesses (via `codex exec` e `opencode run` headless) expôs 6 bugs, 3 deles com decisão de design embutida.

**Decisão:** (1) `outcomes.py --auto-cost` grava **delta** desde o último evento da mesma fonte — o cumulativo fica em `cost.session_cumulative` pra encadear; o cost_capture continua lendo cumulativos (fonte não muda), a conversão é responsabilidade do append. (2) `linear_claims._state_id` prefere nome canônico dentro do tipo (`started`→"In Progress", `unstarted`→"Todo") — um team pode ter vários estados do mesmo tipo e a ordem da API não é confiável. (3) `apply_decay` fiado no Stop de Claude e Codex via `_core/hooks/stop-memory-decay.py` (best-effort, idempotente por dia via `last_decay_at`) — mecanismo sem gatilho não é ciclo de vida.

**Alternativas consideradas:** deltificar no cost_capture (rejeitado: capture é leitura pura, sem estado); corrigir report em vez do dado (rejeitado: dado errado no log contamina qualquer consumidor futuro); decay via cron VPS (rejeitado por ora: Stop cobre o caso local sem infra nova).

**Impacto:** relatórios de custo por issue ficam honestos daqui pra frente (histórico migrado com backup); claim nunca mais cai em In Review; memória decai sozinha sem intervenção. **Gotcha registrado:** commit com `Refs DEV-X` faz o Linear auto-mover a issue via integração GitHub — transições "de graça" que o motor 24/7 pode aproveitar (ou precisa prever).

**Quem decidiu:** Felipe (validação autorizada) + agente.

---

## 2026-07-03 — Outcomes v1 como sinal estruturado append-only do Motor Autônomo (DEV-1103)

**Contexto:** O projeto PD Framework v2.0 / Motor Autônomo precisa de sinal confiável antes de cost tracker, budget guard, model-map e loop 24/7. O estudo ruflo mostrou que aprendizado de agente depende mais da qualidade do sinal de sucesso do que de mecanismo sofisticado.

**Decisão:** Criar o contrato `pd.outcome.v1` em `_core/OUTCOMES.md` e helper `_core/outcomes.py`, com eventos JSONL append-only em `.pd/outcomes/outcomes.jsonl` (ignorado pelo git). O schema captura tarefa, squad, executor, runtime/harness/modelo, resultado, custo quando houver, evidências e intervenção humana.

**Alternativas consideradas:** Banco desde já (rejeitado por overengineering e sem frota concorrente); eventos versionados em git (rejeitado por poluir histórico com runtime state); dependência externa de JSON Schema (rejeitada para manter core determinístico e portável).

**Impacto:** DEV-1104 pode preencher `cost` sem mudar o contrato; DEV-1105/1106 consomem o mesmo sinal para budget/report; fases futuras do motor aprendem com outcomes estruturados em vez de inferir de texto solto.

**Quem decidiu:** Felipe + Vitor.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-07-02 — Adapter Codex #3: e2e FINAL PASSOU + 2 causas raiz do fail-open (Vitor)

Teste fim-a-fim que faltava, rodado em **clone isolado** (`git clone` → `C:\tmp`, origin = bare dummy, um agente por vez — resolve o gap de método de 2026-07-01). Resultado: **fluxo contratual completo validado sob `codex` real (0.142.5)** — `apply_patch` na main → `hook: PreToolUse Blocked` → agente cria `session/*` com escalonamento → patch na branch → Stop auto-commita e mergeia na main. Antes de passar, o e2e **reprovou** e expôs 2 causas raiz que o smoke (subprocess direto) não pega:

**1. Aspas no `command` do hooks.json quebram o spawn no Windows.** O Codex spawna hooks via `cmd.exe /C "<command>"` (fonte: `codex-rs/hooks/src/engine/command_runner.rs`); o Rust escapa aspas internas como `\"`, que o cmd não parseia → hook morre no spawn → `Failed` → **fail-open silencioso** (nenhum hook rodava de verdade). **Fix:** `command` sem aspas (`C:\Python314\python.exe adapters/codex/pretooluse.py` — path sem espaços).

**2. Exit 2 + stderr NÃO bloqueia na 0.142.5 Windows (contradiz a doc).** Mesmo com o hook rodando e retornando exit 2 + stderr, o Codex marca `Failed` e executa a tool. **O único bloqueio que funciona é o JSON `hookSpecificOutput.permissionDecision:"deny"` no stdout com exit 0** (`hook: PreToolUse Blocked`, isolado com hooks mínimos A/B). **Fix:** `deny()` do `_common.py` agora emite o JSON deny (reason também no stderr como diagnóstico); hardening de exceção idem — fail-closed via JSON, nunca exit 1/2.

**Bugs colaterais corrigidos:** `stop-session-branch.py` não checava o rc do auto-commit — commit falho (ex.: clone sem git identity) mergeava branch vazia e reportava ✅ falso; agora aborta com exit 2 e mensagem. `run_smoke.py` crashava no print do resumo em console cp1252 (reconfigure utf-8).

**Gotchas de teste (pra próxima vez):** hook precisa **drenar o stdin** (sair antes = "failed to write hook stdin" → Failed/fail-open); `codex exec` com stdin-pipe aberto **pende esperando EOF** (usar `</dev/null`); `codex exec` fora de repo git falha silencioso (usar `-C <dir>` explícito); hooklog wrapper de debug tem que ser **binário** (text=True corrompe pipes e contamina o resultado). Payload real confirma `tool_input.command` pro apply_patch e `tool_name:"Bash"` pro shell (matcher OK).

**Smoke: 45/45 verde** (contrato dos testes atualizado pro JSON deny).

**AGENTS.md gerado do CLAUDE.md (terceiro turno, DEV-1100):** o espelho manual do roteador virou bloco **verbatim gerado** entre markers `CLAUDE-MD-MIRROR`, regenerado pelo `bootstrap.py` (`sync_agents_mirror()`); curadoria Codex-específica (regras do CLAUDE.md global) fica fora dos markers. Teste anti-drift no smoke (`test_agents_mirror_synced` — 46/46). Regra: **edite sempre o `CLAUDE.md`**, nunca dentro dos markers, e re-rode o bootstrap.

**Trust sem `/hooks` (segundo turno, DEV-1099):** o `trusted_hash` do `config.toml` é o `version_for_toml` do Codex — sha256 do **JSON canônico** (chaves ordenadas, compacto) da identidade normalizada do hook (`{event_name: <label snake_case>, matcher?, hooks: [{type, command, timeout, async, statusMessage}]}`, `fingerprint.rs`). Replicado em Python no **`adapters/codex/bootstrap.py`**, que também regenera os `command` com `sys.executable` (sem aspas; short path 8.3 pra path com espaço). Resultado: trust persistido por edição direta do `config.toml`, contornando o bug openai/codex#22847 — **validado sem `--dangerously-bypass-hook-trust`** (hooks `Completed` + `apply_patch` na main `Blocked` no repo real). O passo interativo `/hooks` deixou de existir no bootstrap.

**Quem decidiu:** Felipe (autorizou seguir) + Vitor (diagnóstico e fixes).

---

## 2026-07-01 — Adapter Codex #3: validação real sob `codex` + 4 fixes (Vitor + Felipe co-debug)

Sessão de validação abrindo o adapter no `codex` CLI de verdade (não só smoke). Perguntamos ao próprio Codex (gpt-5.5, que conhece o harness) pra diagnosticar. **4 achados/fixes reais que o smoke automatizado não pegou:**

**1. Flag de hooks renomeada + versão.** Testei o design na codex-cli 0.121.0 (`codex_hooks` under-development). Na **0.142.5** (a que o Felipe roda) a flag virou **`[features].hooks` (stable)** — `codex_hooks` está deprecated. Sem `codex features enable hooks`, os hooks não disparam. Config: manter só `hooks = true`.

**2. Sandbox do Codex bloqueia escrita no `.git/` (causa raiz do "exit 1").** Confirmado pelo Codex: o sandbox `workspace-write` deixa escrever no working tree mas **não em `.git/refs`**. `git switch -c` sem escalonamento → "Permission denied"; **com escalonamento funciona** (prova que é sandbox, não lock). Logo o `protect_main` via `git checkout -b` **não funciona** num hook (hooks não escalam). **Fix:** modo **`--check-only`** no `_core/runtime/protect_main.py` — detecta a main e retorna exit 2 **sem tentar criar branch** (não toca `.git`); o shim Codex nega com mensagem acionável e o **agente cria a branch** com escalonamento (opção C, recomendada pelo Codex). Adapters #1/#2 não passam a flag → comportamento inalterado.

**3. Hardening fail-closed (segurança).** O Codex trata **exit 1 como não-bloqueante (fail-OPEN)** — só exit 2 bloqueia. Então qualquer erro inesperado no `pretooluse.py` liberaria a escrita. **Fix:** `try/except` no `__main__` do shim converte qualquer exceção em **exit 2 (fail-closed)**, nunca exit 1.

**4. SKILL.md precisa frontmatter YAML válido SEM BOM.** O Codex pulou 5 skills (`auditar-setup`, `fechar-dia`, `fechar-semana`, `log-sessao`, `montar-harness`): 4 sem frontmatter, 1 (`log-sessao`) com **BOM** antes do `---`. Corrigidas (frontmatter `name`/`description`, salvas UTF-8 sem BOM).

**Confirmado no Codex real (✅):** AGENTS.md/C1 (lê `perfil-felipe` sozinho); 5 hooks reconhecidos+confiados; skills/C7 após fix; payload apply_patch = V4A (como esperado); `sys.executable` correto.

**Gap de método (⚠️):** validação fim-a-fim da proteção-da-main ficou **inconclusiva pela coexistência** — rodar Claude Code e Codex no **mesmo working tree/`.git`** embaralha as session-branches (ambos têm hooks). Teste limpo exige **um agente por vez** no repo.

**Pré-requisitos de bootstrap (README):** `codex features enable hooks` (0.142.5+) · `/hooks` trust na 1ª vez · `python adapters/codex/sync_skills.py` · na main o Codex é bloqueado e cria a branch com **aprovação de escalonamento**.

**Quem decidiu:** Felipe (co-debug, conduziu o Codex) + Vitor (fixes).

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-07-01 — Adapter Codex #3: `codex_hooks` é under-development na 0.121.0 (errata da errata, DEV-1018)

**Achado (Vitor, via `codex features list`):** a errata de 2026-06-30 afirmou que os hooks do Codex são "GA". **Isso é impreciso na versão instalada (codex-cli 0.121.0):** `codex features list` mostra `codex_hooks` como **`under development`, default `false`**. Os hooks só disparam após habilitar a flag:

```
codex features enable codex_hooks   # ou [features] codex_hooks = true no ~/.codex/config.toml
```

E ao habilitar, o próprio Codex avisa: *"Under-development features are incomplete and may behave unpredictably."* Também `apply_patch_freeform` está `under development / false`.

**Consequências:**
1. **Pré-requisito de bootstrap:** o adapter #3 exige `codex features enable codex_hooks` — sem isso, `.codex/hooks.json` é ignorado e o Codex roda sem lifecycle/segurança (viraria runtime de segunda classe de novo). Documentado no README do adapter (DEV-1020) e no AGENTS.md.
2. **Maturidade:** o adapter está **correto e testado** (smoke 40/40 via subprocess — mecânica idêntica à invocação do Codex), mas a camada de disparo dos hooks pelo Codex é **instável** na 0.121.0. A validação fim-a-fim sob `codex` real (hooks disparando de fato + trust via `/hooks`) é gate interativo do Felipe, não automatizável em sessão headless.
3. **Não invalida a arquitetura:** quando a flag amadurece pra estável, zero mudança no adapter — só sai o passo de habilitar a flag.

**Smoke automatizado (DEV-1018):** `python adapters/codex/run_smoke.py` agrega `_core/parity_smoke.py` (6/6) + as 5 suites dos shims (pretooluse 11 · lifecycle 8 · stop 4 · context 6 · skills 5) = **40 testes verdes**. Gate de release: exit 1 se qualquer vermelho.

**Quem decidiu:** Vitor (achado) + Felipe (trabalho autônomo autorizado).

---

## 2026-07-01 — Adapter Codex #3: escopo real pós-análise (Vitor, worktree `codex-adapter`)

**Contexto:** início da execução do projeto Runtime Contract — Adapter Codex (#3). Antes de codar, leitura da doc oficial (`developers.openai.com/codex/hooks`) + auditoria do que o adapter OpenCode (#2) já deixou pronto no core. Três correções ao PRD/errata, todas registradas em comentário nas issues.

**1. `_core/runtime/open_session.py` e `record_memory.py` do PRD NÃO existem nem precisam.** O adapter OpenCode provou que C3 (recuperação de sessão órfã) usa `_core/hooks/userprompt-session-recovery.py` e C5 (record_memory) usa `_core/hooks/posttooluse-state-dirty.py` — hooks Claude existentes, runtime-neutros na prática. `_core/runtime/` tem só 3 módulos hoje (`protect_main.py`, `scan_credentials.py`, `close_session.py`) e o Codex chama **exatamente os mesmos scripts** que o OpenCode. **Invariante: diff zero em `_core/`.**

**2. Achado crítico do `apply_patch` (miolo do DEV-1012).** O Codex não tem tool `Edit`/`Write` — edita via **`apply_patch`**, cujo `tool_input.command` é o texto do patch (`*** Update File: <path>`). O `protect_main.py` espera `{file_path,cwd}`. Logo o shim `PreToolUse` precisa **parsear o(s) path(s) de dentro do patch**. O adapter OpenCode não ajuda aqui (lá `write/edit` já traziam `file_path` explícito). É o único código não-trivial do adapter — o resto é tradução de payload.

**3. `_core/parity_smoke.py` já existe e já é runtime-agnóstico** (DEV-889). DEV-1018 é rodar+registrar sob Codex, não construir. Codex CLI **0.121.0** confirmado local (hooks GA presentes).

**Payload PreToolUse Codex (verbatim):** `session_id`, `cwd`, `hook_event_name`, `model`, `turn_id`, `tool_name`, `tool_use_id`, `tool_input`, `permission_mode`. **Bloqueio:** `permissionDecision:"deny"` em `hookSpecificOutput` OU exit 2+stderr — `protect_main.py` já emite exit 2, então shim usa exit 2 direto.

**Arquitetura confirmada:** adapter Codex = `.codex/hooks.json` (matcher por evento) → shims finos em `adapters/codex/` → shell-out pros mesmos `_core/runtime/*` e `_core/hooks/*`. Casca de tradução de payload, zero lógica nova. Reforça a errata de 2026-06-30 (hooks nativos ⇒ paridade real, sem launcher).

**Modo de execução:** **Modo A** (sequencial, Vitor no gate) numa **worktree dedicada** (`.claude/worktrees/codex-adapter`, branch `worktree-codex-adapter`) — trabalho grande, 9 stories tocando lifecycle/branch/segurança. Regra 5 (Modo B proibido em auth/billing/migração) se aplica por analogia à branch-protection/segurança.

**Quem decidiu:** Felipe (worktree + andamento) + Vitor (análise de escopo).

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-06-27 — systemd timers CS: EnvironmentFile padrão + timezone explícito (DEV-897)

**Contexto:** ao instalar 3 timers systemd na VPS Master pros workers CS (digest-diario, milestones, checkin-3-3), os `.service` originais no repo tinham só 1 `EnvironmentFile` apontando pro `.env` do worker, e os `.timer` usavam `OnCalendar=*-*-* 19:30:00` sem timezone — systemd interpreta isso como **UTC** por default, o que daria 16:30 BRT em vez do horário pretendido.

**Decisão:** padrão pra todo worker CS que rodar na VPS Master via systemd:
1. **Dois `EnvironmentFile`** por service: `/etc/onboarding/op.env` (compartilhado — dá `OP_SERVICE_ACCOUNT_TOKEN` pro `op` CLI puxar credenciais) + `.env` do próprio worker (flags `*_APPLY=0` + `PYTHONUNBUFFERED=1`).
2. **`OnCalendar` com timezone explícito**: `*-*-* HH:MM:SS America/Sao_Paulo` — nunca sem timezone (vira UTC silenciosamente).
3. **Horários escalonados** (5 min entre workers) pra não sobrepor chamadas Linear/CPU. Hoje: digest 18:00, milestones 18:05, checkin 18:10, cron cobrança 18:15.

**Alternativas consideradas:** (a) ajustar horário pra UTC no .timer (mais simples mas confunde quem lê o arquivo); (b) `EnvironmentFile` único por worker com cópia do op.env (duplica segredo, ruim).

**Impacto:** padrão herdável por outros workers VPS Master. DEPLOY-ONDAS-1-3.md desatualizado — refletir no repo no PR cleanup futuro.

**Quem decidiu:** Felipe + agente (gotcha clássico de systemd).

---

## 2026-06-27 — Divisão de issues que tocam repos separados em (a) local + (b) sub-issue

**Contexto:** DEV-896 e DEV-838 cobrem trabalho em 2 repos: `pd-framework` (workers/consumer) + `onboarding-webhooks` (receiver Docker, repo separado não clonado local). Fazer tudo na issue original exige clonar repo externo na sessão, fora do escopo.

**Decisão:** quando uma issue tocar `pd-framework` + repo separado, dividir em:
- **Parte (a) local** — implementada e fechada na issue original (entra em `In Review`).
- **Parte (b)** — sub-issue própria, com label `repo:<nome-do-repo-separado>`, tracking independente.

Aplicado em DEV-896 → DEV-903 (handler Tally em onboarding-webhooks) e DEV-838 → DEV-904 (validar `_extrair_evento` Cal.com).

**Alternativas consideradas:** (a) deixar a issue original aberta até fazer ambas as partes (bloqueia o In Review por dependência externa); (b) fechar a original e abrir issue de continuidade sem hierarquia (perde rastreabilidade).

**Impacto:** rastreabilidade preservada (parent-child no Linear), in-review parcial libera DoD da parte local.

**Quem decidiu:** Felipe + agente.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-06-26 — Hook `pretooluse-session-branch` reconhece `MERGE_HEAD` como exceção (DEV-900)

**Contexto:** o hook intercepta `git commit` na main do pd-framework e cria session-branch nova. Isso quebrava o passo final de `git merge --no-commit` + `git commit --no-edit` do `/encerrar-sessao`: o segundo comando era interceptado, descartando o `MERGE_HEAD` e criando session-branch zumbi.
**Decisão:** o hook checa `<git_root>/.git/MERGE_HEAD` antes da lógica de intercept; se existe, `sys.exit(0)` (deixa passar). Conclusão de merge em curso é uma exceção legítima — o agente já entrou na main intencionalmente pra fechar o merge.
**Alternativas consideradas:** (a) só atualizar a skill `/encerrar-sessao` pra usar `git merge --continue` em vez de `git commit --no-edit` — descartado; mantém a armadilha viva pra qualquer skill futura que finalize merge. (b) merge inline `-m "<msg>"` evitando o segundo `commit` — virou padrão recomendado mesmo, mas não resolve o caso com conflito.
**Impacto:** fluxo canônico do `/encerrar-sessao` (merge `session/*` → main, inclusive com conflito) volta a rodar em 1 turno sem zumbi de branch. Qualquer outra skill que finalize merge na main pelo padrão git fica imune.
**Quem decidiu:** Felipe (Vitor recomendou opção a sobre b por robustez).

---

## 2026-06-23 — Secret Key (service_role) do Cadencia direto na cadencia-cli (DEV-789)

**Contexto:** `content image-upload` precisa escrever no Supabase Storage (bucket `content`). A Management API (PAT) não faz upload de objeto; o caminho óbvio é a Secret Key do projeto. Mas isso colide com a regra "nunca service_role direto" e o classifier bloqueou a primeira tentativa.
**Decisão:** wirar a Secret Key na CLI (`config/credentials.py` → item 1P `Supabase - APIs -Secret Key [cadencia]`, vault Databases, env `CADENCIA_SUPABASE_SECRET`), usada **só** pelo `content image-upload`.
**Alternativas consideradas:** (A) upload via worker SSH na VPS Master (key fora do ambiente local) — mais alinhado ao SECURITY.md, mas exige criar worker; (B) adiar 789+790 até o token escopado do DEV-582. Felipe escolheu a secret key direto pela velocidade de desbloqueio do fluxo editorial.
**Impacto:** 1ª credencial de Storage admin na CLI (bypassa RLS). Documentado na seção de segurança do `_core/CADENCIA-CLI.md`. Hardening futuro: token escopado por tenant (DEV-582).
**Quem decidiu:** Felipe.

## 2026-06-23 — DEV-779 (SOAP na CLI) bloqueada: engine de cadências não existe

**Contexto:** A issue assumia um worker `disparo-soap.py` na VPS (envio via Resend) pra CLI envelopar. Investigação nos repos: esse worker não existe; SOAP é só um tipo de `trigger_condition` no schema de cadências (CAD-567), cujo runtime (scheduler CAD-577 + avaliação no `cadence_tick.py`) está não-construído ("gancho não-exercitado hoje").
**Decisão:** bloquear DEV-779 até o engine de cadências (CAD-579/580/581) existir. Não construir worker SOAP standalone (duplicaria o engine).
**Alternativas consideradas:** rescopar pra `soap-create` só (persistir definição como cadence) — descartado; construir worker standalone — descartado (retrabalho).
**Impacto:** Quando o runtime existir, SOAP entra como `cadence` genérica (possível `cadence-create`), não comando `soap-*`. Comentário registrado na issue.
**Quem decidiu:** Felipe.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-06-21 — Central de Observabilidade: arquitetura determinística Master + agente na Dev

**Contexto:** projeto Linear `91d67a96` precisava transformar erros/alertas (Sentry, Grafana, Supabase, Vercel) em issues no Linear, triar, notificar e auto-corrigir bugs — sem violar `SECURITY.md §1` (Master nunca roda agente Claude com tool use).

**Decisão:**
- **Fronteira determinístico vs tool use** define onde cada componente vive: bridge/gate/dispatcher/health-check/advisors (sem LLM) → **VPS Master**; agente de auto-correção (tool use) → **VPS Dev**.
- **Infra pula o gate** (nasce `own:felipe`): a heurística `classify()` é p/ erro de código; alerta de infra tem dono conhecido → roteia direto, sem round-trip nem WhatsApp dobrado.
- **Integrar, não duplicar**: o dispatcher Grafana já existia (`grafana-webhook.service`) criando issues soltas → CAD-706 só plugou na esteira (labels + projeto), não reescreveu.
- **Grafana como agregador**: Sentry/Supabase/Vercel já são datasources no Grafana → "novas fontes" viraram "alert rule no Grafana" em vez de bridge nova (707/708 encolheram).
- **Agente conservador**: abre PR, NUNCA mergeia; confinado por allowlist (`--allowedTools`); detecção de sucesso por PR aberto (não por label).
- **Anti-flood em workers de polling**: dedup por chave estável (`cache_key`/fingerprint) + estado atômico; 1ª rodada surge o baseline 1x, depois só item novo.

**Alternativas descartadas:** endpoint `/grafana-webhook` novo na bridge (duplicaria o dispatcher + WhatsApp dobrado); comparar commit deployado p/ deploy drift (Coolify API não expõe o commit → optou-se por checar presença/saúde do webhook de auto-deploy).

**Impacto:** padrão replicável p/ futuras fontes (CAD-709) e p/ auto-remediation (CAD-716 — runbooks determinísticos na Master, nunca LLM). Reviews sempre via `/openrouter-review` (GLM 5.2). Deploy em prod sempre exige autorização textual explícita do Felipe (classifier + `DEV-WORKFLOW §12.0b`).

**Quem decidiu:** Felipe.

---

## 2026-06-20 — Cascata de produto técnico CAD: Brief → PRD → Epics → Stories (determinística, por persona)

**Contexto:** A transição brief → PRD era informal — o PRD não tinha skill geradora ("manual"), e a quebra em epics/stories não tinha dono nem template definido. Felipe pediu uma esteira determinística com cada etapa por um agente especializado.
**Decisão:** Esteira formal para projeto técnico CAD: `/linear-criar-projeto` (Brief, **Paloma**) → **`/linear-prd`** (nova skill — PRD por **Paloma** + Epics por **Vitor**) → `/linear-planejar-issue` EPIC (Stories por **Paloma**, sub-issues) → plano técnico (**Vitor** gate → **Amélia**). Cada etapa **delega a um subagente** que assume a persona (`times/dev/<persona>/`). Templates obrigatórios: Brief/PRD em `LINEAR-DOC-TEMPLATES`, Epic/Story em `LINEAR-ISSUE-TEMPLATES` (Feature/Story + label `epic`/`story`). PRD sempre antes de Epic; Epic antes de Story.
**Alternativas consideradas:** embutir PRD no `/linear-planejar-issue` (rejeitado — menos determinístico); centralizar tudo no Vitor (rejeitado — Felipe escolheu Paloma+Vitor); skill assume persona vs subagente (escolhido subagente). Aprimoramento incremental — NÃO reescreveu as skills que funcionam.
**Impacto:** Cliente/CS (COM) não usa PRD — segue 12 fases. Docs sincronizadas (`DEV-WORKFLOW §12.0`, `times/dev/CLAUDE.md` §Cascata, `LINEAR-DOC-TEMPLATES`, `SKILLS-LINEAR-INTEGRATION`).
**Quem decidiu:** Felipe.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-06-20 — Code review padrão migrou pra OpenRouter (GLM 5.2 → Qwen 3.7 Max)

**Contexto:** A cascata de dev exigia `/codex-review` como review padrão. Felipe pediu review via OpenRouter com GLM 5.2 obrigatório e fallback Qwen quando inconsistente.
**Decisão:** `/openrouter-review` (GLM 5.2 obrigatório primeiro; Claude avalia e escala pro Qwen 3.7 Max se vier raso/vago/contraditório) e `/dual-review` (roda os dois sempre) substituem o Codex como review padrão na §6 do DEV-WORKFLOW. Script `~/.claude/scripts/openrouter_review.py` carrega a key via `op` (item `OpenRouter - API - Cadencia app`, vault Providers IA). Codex vira legado on-demand.
**Impacto:** Babysitting obrigado a rodar as skills de review da §6 (não conta como auditado sem isso). Propagado pro felipe na VPS Dev (op SA configurado só no felipe). Custo ~US$0,003 GLM / ~US$0,011 Qwen por review.
**Quem decidiu:** Felipe.

---

## 2026-06-20 — Luiz tem framework de dev próprio (não propagar pd-framework)

**Contexto:** Eu vinha copiando skills do pd-framework pro `~/.claude/skills` do Luiz na VPS. Felipe corrigiu: o Luiz tem framework próprio.
**Decisão:** O framework do Luiz é `/home/luiz/.agents/` (já ativo, não "futuro pd-framework-luiz"), com fluxo próprio `to-prd`/`to-issues` exposto via symlinks. **Não propagar skills do pd-framework pro ambiente dele.** Felipe optou por deixar as cópias já feitas (coexistência, sem reverter). `times/dev/CLAUDE.md` corrigido.
**Impacto:** Propagação de skills do pd-framework é só pro user `felipe` (clone `/home/felipe/pd-framework`, symlink `.claude/skills`→`stamper/skills`). Memória registrada.
**Quem decidiu:** Felipe.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-06-15 — Composio: escopo e limitações no stack PD

**Contexto:** Avaliação completa do Composio como middleware de integrações para o PD Framework. Tentativa de integrar Outlook (`felipe@cadencia.ia.br`) via Composio falhou — OAuth Microsoft não é compatível com email Hostinger SMTP/IMAP.

**Decisão:** Composio documentado em `foundation/composio-api.md` como referência pra uso futuro, mas não integrado ao stack atual. Escopo válido: quando Cadência precisar que tenants conectem seus próprios canais (Gmail, LinkedIn, Instagram do cliente) — OAuth multi-tenant via Composio. Para operações internas PD (email, calendar), usar stack existente (Hostinger SMTP / Google Calendar MCP).

**Alternativas descartadas:** Composio/Outlook para `cadencia.ia.br` — incompatível por ser Hostinger, não Microsoft 365.

**Impacto:** `outlook_client.py` deletado de `_shared/`. Skills `/enviar-email` e `/criar-reuniao` mantidas no estado original (sem canal Outlook).

**Quem decidiu:** Felipe.

---

## 2026-06-15 — Migração GHL → Supabase + Resend aprovada (sem timeline)

**Contexto:** GHL (GoHighLevel) sendo usado pela Cadência e internamente pela PD para CRM, email e appointments. Custo e overhead não justificam o uso atual. Felipe usa Linear + Obsidian + Google Calendar pra gestão interna — não precisa de CRM separado.

**Decisão:** Migrar GHL para: Supabase (CRM/contacts/pipeline), Resend (email transacional — PDL-555), Google Calendar direto (appointments Felipe). Twenty CRM avaliado e descartado — stack Supabase + Next.js já cobre o caso de uso sem adicionar dependência nova.

**Alternativas descartadas:** Twenty CRM — resolve problema de quem não tem infra; PD já tem Supabase + Next.js + Luiz. Composio/Outlook — incompatível com Hostinger.

**Impacto:** `/criar-reuniao` precisará ser migrada do GHL para Google Calendar quando a migração for executada (sem PDL criada ainda — decisão estratégica registrada para referência futura).

**Quem decidiu:** Felipe.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-06-02 — Taxonomia de incidents v1 (PDL-383)

**Contexto:** Hub `incidents/` tem 59 arquivos em texto livre, sem categoria estruturada. `_core/lookup.py` busca por keywords mas não agrega — impossível responder "quantos `silent_failure` no último trimestre?", "qual serviço mais quebra?", "deploy_broken tá subindo ou descendo?". Tags `#vercel`/`#ghl`/`#silenciosa` ajudam mas são ad-hoc — cada incident escolhe livre.

**Decisão:** Adotar taxonomia de **8 categorias técnicas** + frontmatter YAML obrigatório em novos incidents:
`auth_error`, `silent_failure`, `integration_down`, `deploy_broken`, `data_inconsistency`, `runtime_crash`, `config_drift`, `human_error`.

Regra: uma categoria por incident (causa raiz, não sintoma). Tags secundárias continuam livres no corpo. Frontmatter com 6 campos: `category`, `severity`, `service`, `duration_hours`, `detected_by`, `date`.

Doc canônico: `times/dev/foundation/incident-taxonomy.md` (exemplo de cada categoria mapeado a incident real do hub).

**Trade-off:** Categorias **não-técnicas** (processo, comunicação, comercial) ficam fora desta v1. Se entrarem no hub, avaliar v2. Critério: começar simples, evoluir sob demanda real.

**Trade-off 2:** **Não** re-categorizar os 59 legados em massa. Drift residual aceito — lookup texto-livre continua funcionando. Migração opcional caso-a-caso quando agente abrir incident antigo.

**Consequências:**
- **PDL-384** — atualizar skill `/registrar-incidente` pra perguntar categoria + preencher frontmatter automaticamente (input numerado 1-8).
- Futuras automações (dashboard de métricas, alert "categoria X explodindo no mês") ficam possíveis assim que volume novo justificar.
- Foundation `README.md` ganha entrada pra `incident-taxonomy.md` na tabela de consulta obrigatória.

---

## 2026-06-02 — `_shared/standing_order.py` (PDL-382)

**Decisão:** Criar helper base `StandingOrder` (ABC) pra padronizar workers determinísticos da VPS Master. Ciclo único: `execute → verify → report → notify`. Captura `runtime_crash` no `run()` via try/except.

**Por quê:** Workers VPS hoje têm padrões divergentes de log/notify (cada um inventa o seu). Concentrar no helper elimina drift, reduz boilerplate e garante que toda falha vai pro mesmo formato de log + mesma rota de alerta.

**Decisão arquitetural:** ABC com `@abstractmethod execute()` + `verify()` — não Protocol/duck-typing.

**Por quê:** Workers VPS rodam sob cron sem agente — erro de implementação tem que estourar no import/instanciação, não em runtime. `ABC` falha com `TypeError: Can't instantiate abstract class` se subclasse esquecer método. Protocol é estático (mypy-only); aqui queremos hard fail em produção determinística.

**Decisão integração Stevo:** Import tardio dentro de `notify_failed()`, com try/except.

**Por quê:** Worker que não notifica não deve exigir `STEVO_API_KEY` no env. Import top-level forçaria credencial mesmo em cron silencioso. Falha de notify também não deve derrubar o worker — log já foi escrito, alerta é best-effort.

**Decisão dry_run + notify_destination opcional:** Defaults seguros (`dry_run=False`, `notify_destination=None`). Sem destino = no-op silencioso. Exemplo `health_check_worker.py` usa `dry_run=True` pra rodar localmente sem disparar WhatsApp real.

**Fallback PDL-385:** Se algum worker precisar de retry/circuit breaker antes de notificar (ex: API flaky que volta em 30s), abrir issue separada — `StandingOrder` v1 propositalmente NÃO faz retry. Notify é imediato em qualquer FAILED/PARTIAL. Adicionar lógica de retry vira `RetryableStandingOrder` futuro, não mexer na base.

**Formato log:** Pipe-separated `STATUS|WORKER|CATEGORY|TIMESTAMP|DURATION_MS|DETAIL` em `sessions-log/workers/<name>-YYYYMMDD.log`. Newlines e `|` no detail são sanitizados. Fácil de grep + parse simples sem CSV/JSON overhead.



## 2026-05-25 — Bootstrap do Time Dev (PDL-256)

**Decisão:** Criar Time Dev com 8 Squads diretos (3 níveis simples), um por persona BR (vitor/amelia/paloma/sofia/camila/paula/joao/bruno). Sem sub-squads aninhados.

**Por quê:** Consistência > pragmatismo (decisão PDL-241). Mesmo Bruno sendo modo opt-in, vira Squad próprio. Sub-aninhar dentro de persona vira overhead sem ganho — cada persona já é uma especialização clara.

**Decisão:** Skills invocáveis individuais — só 3 transversais agora: `/joao`, `/paula`, `/bruno`. Não criar `/vitor`, `/amelia`, `/paloma`, `/sofia`, `/camila`.

**Por quê:** Essas 5 personas vivem DENTRO de fluxos (Camila no QA durante `/linear-close-issue`, Sofia consulta antes de design, etc). Criar skill standalone pra cada vira ruído. Pra invocar standalone: `/abrir-squad times/dev/<persona>`.

**Decisão:** Foundation docs — 4 populados com conteúdo real, 1 EM REVISÃO, 1 referência inline.

**Por quê:**
- `code-principles.md`, `branch-convention.md`, `padrao-commit.md`, `babysitting-checklist.md` — uso diário, populados com decisões já existentes (CLAUDE.md global + DEV-WORKFLOW + feedback_babysitting)
- `padrao-testes.md` — EM REVISÃO, sem prática consolidada PD hoje (issue Linear a abrir)
- `dev-workflow.md` — não criar doc separado; apontar pra `_core/DEV-WORKFLOW.md` no README (evita duplicação)
- `boilerplate-templates.md` — não criar agora; só quando demanda real (evita doc vazio)

**Decisão:** Nenhum worker próprio do Dev hoje. Pasta `workers/` vazia em cada Squad.

**Por quê:** `/documentar` é manual, code review é on-demand, BMAD skills são manuais, workers Cadência/PD Portal pertencem aos Squads de Produto.

**Decisão:** SRE / Security Engineer / Data Engineer descartados (PDL-241) — não criar.

**Por quê:** Volume baixo. Quando precisar, abre sessão dedicada com Felipe.


---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-06-05 — `/encerrar-sessao` como porta única de saída + hook checkout-warning (PDL-422)

**Problema:** hooks session-branch desenhados pra fluxo único `main → session/* → main` em checkout único. Felipe usa worktrees paralelos + sessões multi-PDL + branches `feat/pdl-X` frequentes. Trabalho órfão (24 modif + 25 untrack travados em feat/pdl-382 ao diagnosticar).

**Decisão Vitor:** `/encerrar-sessao` vira porta única de saída controlada. Hook automático mantém-se como fallback (sem regressão). Lógica por tipo de branch (5 casos). Default em `feat/pdl-X` = salvar sem fechar PDL (Felipe nem sempre fecha PDL em 1 sessão).

**Rejeitadas:**
- Stop automático em qualquer branch ≠ main: quebra atomicidade Linear↔git (`/linear-close-issue` é dono).
- Só documentação: depende de disciplina humana (Felipe TDAH, Luiz pode esquecer).

**Hook novo:** `pretooluse-checkout-warning.py` — tripwire pra evitar mudar de branch dirty (causa raiz da contaminação cross-branch).

**Reviews:** `/codex-review` + `/runtime-fix-review` (não é auth/billing/migration, mas hook em git event-Stop = risco regressão alto).

**Impacto Luiz:** zero mudança visível. Workflow `feat/pdl-X` preservado.


---

## DEV-866 — Snapshot de estado de dev do Luiz (VPS Dev) na memória do Time Dev (2026-06-26)

**Problema:** agentes do Time Dev não tinham visibilidade do estado atual do Luiz sem SSH manual.

**Decisão (híbrido C, adaptado):**
- Gerador `times/dev/workers/luiz_state.py`: lê git **read-only** dos repos do Luiz em `/home/luiz/projetos/**` (branch/unpushed/dirty/últimos commits) + issues In Progress dele no Linear. Roda local (Windows, via SSH `sudo python3` embarcado em base64) ou na VPS (cron, root, direto).
- **Não usa pd-syslog:** o coletor pd-syslog só varre `$HOME` até profundidade 2; o Luiz aninhou os repos em `projetos/<area>/<repo>` (profundidade 3) → `workspaces` do pd-syslog está vazio. Lemos git direto.
- **GitHub API descartada:** git log local já dá os commits; menos credenciais/falhas.
- **Branch dedicada `luiz-state`** (decisão do Felipe): cron diário (root, VPS Dev, 21h40 UTC, `/opt/luiz-state/luiz_state_cron.sh`) publica o snapshot lá via **git worktree isolada** — NUNCA toca a main, NUNCA reseta o clone do Felipe. Os 2 arquivos são gitignored na main, `add -f` na branch.
- **Notificação WhatsApp+Slack todo dia** (decisão do Felipe): cron chama `--notify-only` (reusa config + EvoClient + Slack do daily_brief). Agente nunca mergeia `luiz-state → main` sozinho — Felipe mergeia após o aviso.
- Gerador deployado em `/opt/luiz-state/` (estável); o cron auto-atualiza o /opt a partir da main pós-merge (sem redeploy manual).

**Validado:** coletor como root (8 repos), push na branch `luiz-state` via deploy key felipe, Slack OK. **⚠️ WhatsApp/Evo:** `op` falhou no teste interativo (sem token no env do sudo); depende do mesmo mecanismo de cron-env do daily_brief — confirmar no run real 21h40 (`/var/log/luiz-state.log`).

### DEV-866 — Auto-espelhamento git → Linear (2026-06-26, decisão Felipe)

**Furo detectado:** Luiz trabalha git-cêntrico, não Linear-cêntrico (ex: 22 commits em `feature/dev-862` com a issue parada em Backlog; branches sem issue vinculada). Decisão Felipe: **só auto-espelhar** (instrumentar nosso lado), **não** forçar enforcement no ambiente do Luiz (respeita a regra de não-propagar o pd-framework + framework próprio dele).

**Implementação** (`luiz_state.py --mirror`, roda no cron diário):
- `branch → issue` via `issueVcsBranchSearch` (API Linear, feita pra isso).
- **Move pra In Progress** só se a issue ainda não começou (backlog/unstarted/triage). **Nunca regride** started/completed/canceled.
- **Comenta** 1 espelho/issue (marcador `<!-- luiz-git-mirror -->`, upsert idempotente) com branch + unpushed + dirty + últimos commits. Pula comentário em Done/Cancelada sem trabalho em voo.
- **Flag de furo:** branches sem issue vinculada são listados (rastreio faltando).
- `--mirror-dry` mostra o plano sem escrever. Read-only do lado do Luiz; só muta o Linear.

**Validado:** DEV-862 movida Backlog→In Progress + comentada; DEV-754 (Done, ↑1) comentada sem regredir; idempotente como root na VPS.

### DEV-866 — Auto-criação autônoma de issue (2026-06-26, decisão Felipe)

**Decisão Felipe:** "começou a trabalhar, cria a issue" — autônomo, sem depender do Luiz (qualquer enforcement que dependa dele abre margem de erro humano). O worker **cria a issue sozinho** quando detecta branch do Luiz com trabalho em voo e sem issue vinculada.

**`luiz_state.py --mirror` (no cron diário):**
- Resolve `branch → issue`: (1) `issueVcsBranchSearch` nativo, ou (2) mapa de estado `luiz-branch-map.json`, ou (3) **auto-cria** (team DEV, assignee Luiz, In Progress, marcador `<!-- luiz-auto-branch:repo@branch -->`).
- **Gate:** só cria se `ahead>0 OU unpushed>0 OU dirty>0` (trabalho em voo real; não cria pra branch toda na default).
- **Idempotência:** `luiz-branch-map.json` (`repo@branch → identifier`) vive na branch `luiz-state` (gitignored na main, `add -f` na branch), pré-semeado com DEV-890/891. Sem ele, recriaria duplicatas (as branches do Luiz não têm o ID no nome). Validado: mapa vazio→CRIAR; mapa semeado→0 CRIAR; mirror real 2x→criadas=—.
- IDs estáveis hardcoded: team DEV `3d9699c8…`, Luiz `0085bb23…`, In Progress `e1a71467…`.

**Limite conhecido:** branches do Luiz sem o ID no nome não re-vinculam via `issueVcsBranchSearch` — por isso o mapa. Se o Luiz adotar branch com ID (`feat/dev-XXX`), o vínculo nativo passa a funcionar e o mapa vira backup.

### DEV-892 — PR pronto → In Review (2026-06-26)

Estende o espelhamento (DEV-866) com a transição **In Progress → In Review** quando a branch tem PR pronto.

**Detecção sem credencial nova:** o mirror (root) consulta `sudo -u luiz gh pr list --head <branch> --state open --json isDraft,url` (cwd = repo do Luiz). O `gh` do Luiz já está autenticado — root só pede emprestado via sudo. Descartado: (a) gh pra root (não autenticado), (b) PAT novo, (c) editar pr-watcher (deployado divergiu do repo — `STEVO_DIR`, 283 linhas; não mexer).

**Transição** (`_apply_issue`, ordem de prioridade):
1. PR pronto + não Done/Canceled + ainda não In Review → **In Review** (forward; cobre Backlog/Todo/In Progress).
2. senão, backlog/unstarted/triage → In Progress.
3. nunca regride completed/canceled.
Comentário-espelho ganha o link do PR.

**Validado e2e:** DEV-862 (PR #74 não-draft) → Backlog→In Progress→In Review automático; mirror real 2x → `review=[DEV-862]` depois `review=—` (idempotente). No cron diário (passo `--mirror`).

### DEV-961 — Schema do vault Empresa: LLM Wiki Pattern (2026-06-29)

**Contexto:** Felipe quer um graph no Obsidian (vault Empresa) onde a memória operacional da empresa se conecta. Decisão de não tocar nos arquivos-fonte do pd-framework (crase quebraria parsing de skills/hooks). Aplicado o "LLM Wiki Pattern" (Karpathy): 3 camadas raw→wiki→schema.

**Decisões arquiteturais (gate Vitor):**
1. **Nome/local do schema: `Setup/AGENTS.md`** (não `CLAUDE.md`, não raiz). `AGENTS.md` = padrão cross-runtime, coerente com o trabalho de runtime-agnosticism (F3/RUNTIME-CONTRACT) — schema de dados não carrega nome de vendor de modelo. `Setup/` porque o `vault-organizer.py` já ignora a pasta (`IGNORE_DIRS`) → não polui o graph, não é classificado, mas versionado e lido. NÃO conflita com "não duplicar AGENTS.md por squad" (aquilo era CLAUDE.md de squad de código; aqui é schema único de vault de conhecimento).
2. **3 camadas mapeadas sobre estrutura EXISTENTE** — não cria pasta nova. entities=`Clientes/`+`Projetos/`+`Time/`+squads; sources=`Sessoes/`+`Incidentes/`+`Reuniões/`+`Comercial/Propostas/`; concepts=`Conceitos/`+`Decisões/`+`Cultura/`+`Processos/`.
3. **Mecanismo de conexão: campo `entities:` no frontmatter de cada source** (`entities: ["Juliana"]`). Substitui wikilink-por-busca-de-string (frágil) por link modelado. O backlink na entity forma o graph. Resolve a fragilidade do `find_wikilinks` do vault-organizer.

**Achado da auditoria (subagente-leitor):** ~14 skills já gravam frontmatter canônico (date/tags/moc); higiene madura. Gap real: NENHUMA skill cria/mantém camada de **entities** — todas conectam só por MOC (categoria) e wikilink contextual. 5 fontes sem espelho: sessions-log, decisions.md dos squads, learnings-calls, glossário, split Linear↔Obsidian. Mirror dessas fontes é F3/F4, não F1.

**Escopo fechado:** NÃO espelhar STATE/MEMORY vivos, código, segredos.

**Próximo:** F2 (DEV-963) — Amélia cria camada de entities + piloto Juliana end-to-end, sob gate Vitor.

### DEV-963/964 — Backfill Wiki Pattern executado (2026-06-29)

**F2 (entities + piloto) + F3 (backfill) entregues. 7 guardrails do backfill implementados:**

1. **Reversibilidade — `git init` no vault Empresa** (não tinha git, só livesync). Baseline `7f44556` antes de tocar; resultado em `d2a74dc`. Reversão: `git -C <vault> reset --hard 7f44556` OU apagar notas com `generated: wiki-backfill`. `.gitignore` exclui binários grandes (Attachments, pdf, mp4) e cache volátil.
2. **Resolução de entidades — matcher** em `_shared/wiki_backfill.py`. Catálogo de 47 entities (clientes/projetos do vault + pessoas PEOPLE.md + squads times/*). Aliases por slug/nome; primeiro-nome só p/ pessoa/cliente (evita falso-positivo de projeto composto). Match exige sinal forte (título/arquivo) ou múltiplo no corpo. Squad do frontmatter liga direto.
3. **Dry-run revisável** antes de escrever: 486 sources → 293 ligadas (60%) / 193 órfãs. Órfãs NÃO entram (folha sem entity viola schema). Relatório em scratchpad.
4. **Produtos-core são hubs legítimos** (decisão): cadencia/framework/stamper NÃO no stop-list (Cadencia=159 sources, reflete o negócio). Pessoas onipresentes (felipe/luiz) no stop (não discriminam).
5. **Idempotência + reversão fina:** sources marcadas `generated: wiki-backfill`; hub via `ensure_entity(overwrite=False)` preserva curadoria.
6. **Sanitização de corpo:** wikilinks `...` do corpo copiado são neutralizados (a conexão vem do frontmatter `entities:`). Sem isso, `STATE.md` etc. viravam nós-fantasma. Resultado: **0 link quebrado nas sources geradas**.
7. **Color groups por type** no graph.json (entity=laranja/source=azul/concept=verde) — legibilidade do hairball.

**Resultado:** 27 entities + 293 sources no vault. Hubs: Cadencia 159, PD Framework 22, GCI-GO 8, Juliana 5.
**Dívida pré-existente detectada (não regressão):** 347 wikilinks quebrados em notas ANTIGAS do vault → escopo do lint F5 (DEV-966).
**Migração:** 3 entities unificadas pro formato pasta (Karina README→hub, WGL arquivo→pasta, Quartz README→hub).

### DEV-974 — Wiki Pattern no vault Pessoal (2026-06-29)

Estendido ao vault Pessoal (separado do Empresa). **Natureza diferente:** sem raw layer externo — conteúdo já vive no vault e já semiconectado (`Autor` no corpo, `Estudo/Autores/` pré-existente). Método: **consolidação in-place** (não backfill), via `_shared/wiki_connect.py` que EDITA notas curadas preservando frontmatter+corpo (só adiciona `type/entity_kind`, bloco Dataview, e `entities:`).

- git baseline Pessoal `89348a8` (não tinha git). Reversão: `git -C <Pessoal> reset --hard 89348a8`.
- `upsert()` nunca sobrescreve campo curado existente (moc/tags); só adiciona. `promote` liga via `Nome` literal no corpo (wikilink explícito do Felipe — sem falso-positivo de substring).
- Escala: 21 hubs (14 autores Estudo/Autores + 7 conceitos Conceitos/). Pula `_*`, README/INDEX/MOC.
- entity_kind Pessoal: autor·livro·conceito·pessoa·curso·ferramenta. Schema em `Setup/AGENTS.md`.
- **vault-organizer já cobre o Pessoal:** task `VaultOrganizer-Daily` (18h) chama sem args = `--vault all` (Pessoal+Empresa). Confirmado pela assinatura de normalização no `Mano Deyvin.md`.
- Color groups por type aplicados no graph.json do Pessoal.

### DEV-965/966 — Auto-manutenção da wiki via cron (2026-06-29)

**Decisão arquitetural (gate Vitor):** F4 NÃO foi feito como "patch nas 14 skills" (frágil, diverge). Em vez disso, **um worker central** `_shared/wiki_maintain.py` roda no cron e faz o bookkeeping — modelo Karpathy (o mantenedor é a máquina, não as skills). Cobre os 2 vaults.

- **INGEST (F4/DEV-965):** liga notas-source às entities por menção (texto + wikilink), marca `type:source`. Idempotente. Notas novas (sessão/leitura/incidente) nascem conectadas no dia seguinte sem tocar nas skills.
- **LINT (F5/DEV-966):** relatório de saúde em `Setup/_wiki-lint.md` por vault — hubs órfãos, sources sem entity, wikilinks quebrados. Detector simples (pode super-reportar por path); serve de proxy de dívida.
- **Cron:** task `WikiMaintain-Daily` 18:15 (após `VaultOrganizer-Daily` 18:00), `--apply`. Autorizado por Felipe.
- **Dívida exposta:** 711 links quebrados (Pessoal) / 366 (Empresa) — wikilinks de notas antigas pra notas que nunca existiram. Oportunidade de limpeza futura; 0 introduzido pelo nosso trabalho.

**Epic DEV-955 completo:** F1 schema · F2 entities+piloto · F3 backfill (293 sources) · F4 ingest cron · F5 lint cron. + DEV-974 (Pessoal, 21 hubs + 30 sources). Os 2 vaults são wikis vivas auto-mantidas.

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-06-30 — DEV-993: meeting-transcriber resiliente a Device Guard via fallback no .bat (Vitor)

**Contexto:** OneDrive desidratou o `meeting-transcriber` (incidente 30/06) e, como efeito colateral de tocar nos binários, o Device Guard (WDAC) passou a bloquear `C:\Venvs\meeting-transcriber\Scripts\python.exe`. Issue ofereceu 3 opções: recriar venv, liberar binário no Smart App Control, ou adotar o workaround (python-base do uv + PYTHONPATH) como padrão.

**Decisão:** opção **menos invasiva e auto-curável** — `transcriber.bat` com pré-check + fallback automático. Tenta o python do venv (caminho limpo); se `"%VENV_PY%" -c "pass"` falhar (Device Guard bloqueia o .exe inteiro, então até isso falha → isola exatamente essa causa), cai pro python-base do uv + `PYTHONPATH=site-packages do venv`.

**Por que não recriar o venv:** reinstalar torch+CUDA+whisperx é caro e não impede reincidência (OneDrive pode rebloquear). **Por que não Smart App Control:** exige UI/admin, não-determinístico, não versionável. O `.bat` resiliente é versionado, determinístico e cobre a reincidência.

**Validação:** na re-checagem o Device Guard **já não bloqueava** (era transitório) — venv python rodou `--version` + import `torch 2.8.0+cu128`/`whisperx`/`cuda=True`. Ambos os ramos do `.bat` testados (`--help` + import pesado, exit 0). Transcrição real de 50min já validada na sessão do incidente com o mesmo venv.

**Skills:** skills-fonte do repo (`gravar/parar/pausar/retomar/transcrever-reuniao.md`) ainda apontavam pro OneDrive → migradas pra `C:\dev\meeting-transcriber`. Skill ativa do framework (`stamper/skills/obsidian-transcrever-reuniao`) já usava o `.bat` (herda o fallback de graça).

### Adapter Codex — decisão recomendada após Qwen + GLM + /dev-debate (2026-06-30)

**Contexto:** Felipe quer que Codex use o PD Framework com 100% das capacidades abrindo a mesma pasta `C:\dev\pd-framework`, sem criar segundo sistema e sem mexer no core existente. Codex cru não tem hooks/event bus equivalentes a Claude Code (`PreToolUse`/`PostToolUse`/`Stop`) nem OpenCode (`chat.message`/`tool.execute.*`/`session.idle`), então `.codex/` sozinho não entrega C3-C6 deterministicamente.

**Consenso:** adotar adapter Codex como camada 3, repo-local e fino: `.codex/` só para instruções/config nativas; lógica em `adapters/codex/`; entrada canônica via `Taskfile.yml` (`task codex`) chamando launcher fino `pd-codex.py`. Shadow/alias de `codex` fica para fase posterior, após paridade e testes.

**Handoff completo:** `times/dev/context/debate-adapter-codex-2026-06-30.md`.

### ⚠️ ERRATA (2026-06-30, mesma sessão) — a decisão acima partiu de premissa FALSA

**A premissa "Codex cru não tem hooks/event bus equivalentes a Claude Code" está ERRADA.** Nem Codex, nem Qwen, nem GLM, nem o /dev-debate checaram a documentação oficial do harness do Codex antes de arquitetar (furo dos feedbacks `feedback_ler_doc_antes_de_codigo` e `feedback_analise_profunda_antes_de_issue`). A checagem no doc oficial (`developers.openai.com/codex/hooks`, verificado 2026-06-30) mostra que o Codex tem **sistema de hooks nativo em GA**, quase 1:1 com o do Claude Code.

**Eventos de hook do Codex** (config em `.codex/hooks.json` ou `[hooks]` no `.codex/config.toml`, nível repo): `SessionStart`, `UserPromptSubmit`, `PreToolUse` (bloqueia via `permissionDecision:deny`/exit 2, reescreve input via `updatedInput`), `PermissionRequest`, `PostToolUse`, `Stop`, `PreCompact`/`PostCompact`, `SubagentStart`/`SubagentStop`. Doc oficial garante: **"Hooks fire consistently regardless of launch method (app, CLI, IDE extension, web)"** — ou seja, hook de repo dispara **mesmo no `codex` cru**.

**Consequências que corrigem a decisão:**
1. **Bypass não é problema** — `.codex/hooks.json` no repo é enforcement universal. Cai a justificativa de `Taskfile`/`task codex` como "entrada canônica obrigatória" e o debate inteiro sobre shadow-alias.
2. **C3-C6 viram nativos e determinísticos, não "soft".** O caveat do João ("não é 100%") cai — paridade intrínseca, igual Claude/OpenCode.
3. **`.codex/` NÃO é "só instrução nativa" — é o adapter de verdade**, como `.claude/settings.json`+`_core/hooks/` é o adapter #1. A separação `.codex/`-instruções vs `adapters/codex/`-lógica proposta pelo GLM é artificial com hooks nativos.
4. **Launcher/Taskfile vira conveniência opcional**, não requisito de correção.

**Decisão corrigida (substitui a de cima):** adapter Codex #3 = `.codex/hooks.json` mapeando cada evento Codex → scripts de shim finos em `adapters/codex/` que fazem shell-out pros mesmos `_core/runtime/*` (`open_session`/`protect_main`/`scan_credentials`/`record_memory`/`close_session`) já usados pelos adapters #1 e #2. Único trabalho real: traduzir o payload JSON do Codex (nomes de campo diferentes do Claude) → chamada runtime-neutra do `_core/`. Modo A. Sem launcher obrigatório, sem bypass, paridade real. Fontes: developers.openai.com/codex/hooks · /config-advanced · /agent-approvals-security.

## 2026-07-03 — DEV-1104: captura de custo lê artefatos locais do harness; pricing fica no MODEL-MAP

**Contexto:** o objeto `cost` do `pd.outcome.v1` (DEV-1103) precisava ser preenchido com dados reais sem quebrar quando o harness não expõe usage.

**Decisão:** `_core/cost_capture.py` lê **passivamente** o que cada runtime já grava local — transcript JSONL do Claude Code (`message.usage`), `token_count` do rollout do Codex, tabela `session` do sqlite do opencode (read-only) — e converte pro `cost` do contrato. Sem hook novo, sem rede, sem dependência. Tolerante: fonte ausente → `cost=null`, o `append --auto-cost` nunca falha por causa de custo. **Tabela de preço por modelo NÃO entra aqui** — `amount` só quando o runtime reporta (opencode/API paga); precificar token de assinatura é papel do MODEL-MAP (DEV-1113/1116). Bugs reais achados na validação com dados reais: directory do opencode usa forward slashes no Windows; `model` do opencode é blob JSON.

**Alternativa rejeitada:** hardcodear tabela de preços por modelo (desatualiza e duplica com o MODEL-MAP); instrumentar hooks pra registrar usage por chamada (infra especulativa — a leitura passiva do que já existe cobre o caso).

## 2026-07-03 — Epic DEV-1107 (memory engine D1): ciclo de vida sobre índice derivado; decay ancorado corrige bug do ruflo

**Contexto:** memória do PD só crescia — sem curadoria, sem injeção rankeada, sem medição. D1 do estudo ruflo decidiu portar o ciclo de vida ANTES de embeddings.

**Decisão:** `_core/memory_engine.py` implementa o loop completo em 4 camadas: (1108) índice derivado em `.pd/memory/index.json` reusando `iter_docs()` dos backends do lookup — fingerprint FNV-1a pra dedup por conteúdo, duplicata vira alias, corpus markdown+git segue fonte nobre; (1109) confidence/access/decay com parâmetros da D1 (+0.03 acesso, +0.05/−0.02 feedback, −0.005/dia só nunca-acessadas, piso 0.05) e **decay ancorado em `last_decay_at`** — cada dia desconta uma vez (o ruflo recalcula sobre a idade total a cada consolidate e compõe o desconto; bug não portado); (1110) re-rank no lookup `score_lexical × (0.5+confidence)` com registro automático de acesso dos hits servidos (feedback implícito) e `--no-memory-rank` como fallback; (1111) snapshots (cap 50) + trend IMPROVING/DECLINING/STABLE por drift da confidence média.

**Alternativas rejeitadas:** BM25+embeddings primeiro (ataca busca, não curadoria — gap real era ciclo de vida); PageRank sobre grafo de similaridade nesta fase (custo/benefício ruim pro corpus de 400 docs; edges temporais/similaridade ficam pra fase 2 se os snapshots provarem necessidade); decay em memórias acessadas (curadoria agressiva demais pra memória curada por humano).

## 2026-07-03 — Epic DEV-1112 (MODEL-MAP D2): mapa por harness com regime de cobrança; enforcement no hook; bandit só com dados

**Decisão:** `_core/MODEL-MAP.json` é segmentado por HARNESS (dimensão que o ruflo não tem) com `billing: assinatura|api-paga`; o adapter injeta SÓ o bloco do harness ativo no SessionStart (hook neutro + 3 fiações). A regra dura "assinatura jamais usa modelo pago por token" virou guard executável no PreToolUse (endpoint pago + invocador HTTP → deny JSON; exceção via marcador `PD_PAID_API_SKILL` validado contra `exceptions.skills`). Guard é guarda de CUSTO → fail-open se o mapa quebrar (diferente das barras de segurança, fail-closed). Aprendizado de routing NÃO implementado: `learning_dataset` só agrega outcomes por (harness, model) — o bandit Thompson entra quando houver volume (síntese do estudo ruflo: sinal antes de mecanismo).

**Alternativas rejeitadas:** classificador heurístico de complexidade do ruflo (regex EN frágil — o agente lê o mapa e classifica melhor); pricing hardcodado por modelo (desatualiza; `amount` real só vem do runtime que reporta); bloquear por menção de URL sem invocador (falso-positivo em echo/grep/docs).

## 2026-07-03 — Epic DEV-1117 (recorder D3): black box como camada de resgate, opt-in por design

**Decisão:** `_core/session_recorder.py` captura turnos do transcript com resumo extrativo (sem LLM) e persiste em SQLite (PK=fingerprint, idempotente; fallback JSON). A source `transcripts` do lookup é OPT-IN (fora do ACTIVE) — turno cru não entra na busca default nem no índice do memory engine (higiene de contexto). Limpeza de transcripts do framework passa por `clean_transcripts.py` (arquiva ANTES de deletar, passo não-pulável do --apply). NÃO portado do ruflo: restauração automática pós-compact, autopilot de %, bloqueio de compactação.

**Alternativa rejeitada:** injetar turnos arquivados automaticamente no contexto (flood + compete com a memória curada); capturar via hook a cada prompt desde já (captura sob demanda + no fechamento cobre o caso de resgate sem custo por turno — hook fica pra quando houver evidência de perda entre capturas).

## 2026-07-03 — Epic DEV-1122 (skills tooling D4): nascer válido + regressão visível; consertar legado é trabalho à parte

**Decisão:** qualidade de skill vira tooling em 3 camadas: (1124) `lint_skills.py` em lote — erros estruturais (frontmatter/BOM/limites) vs warnings de qualidade (gatilho, critério ADR-112 "quando NÃO usar") — modo relatório por design pra não quebrar legado válido; (1125) hook Stop com **baseline monotone-decreasing** (semente witness do ruflo): silencioso no legado conhecido, aviso só quando quebradas SOBEM, baseline desce sozinha; (1123) `new_skill.py` scaffolder — skill nasce com frontmatter válido por construção e passa por gate de lint antes de existir. Achado da primeira execução real: **25 skills quebradas em 199** (a classe do Adapter Codex era 5× maior que o conhecido). Consertar as 25 é conteúdo por squad — não entrou no escopo do epic (issue própria se priorizado).

**Alternativas rejeitadas:** linter bloqueante desde o início (25 falsos-bloqueios no legado); aviso incondicional no Stop (ruído a cada sessão ensina a ignorar o hook); YAML parser como dependência (frontmatter simples chave:valor cobre o formato real).

## 2026-07-03 — Epic DEV-1127 (interface D5): contrato formalizado; claims no Linear; reaper gated

**Decisão:** a D5 vira artefatos operacionais: `_core/INTERFACE-CONTRACT.md` (3 canais com custo, teste MCP-vs-CLI, tabela de donos do estado, gatilhos de reabertura → Supabase se um dia); `_core/linear_claims.py` (check/claim/release — claim recusa dono ativo, release com motivo auditável; Linear é a fila, zero infra própria); `_core/HANDOFF-FORMAT.md` (razão tipada + % honesto + becos sem saída obrigatórios, em comentário Linear); spec do stale-claim reaper GATED nos gatilhos da D5 (2 estágios ping→release, dry-run default, isenções, cap).

**Alternativas rejeitadas:** implementar o reaper já (frota não existe — doença do ruflo); claims em arquivo/SQLite local (race condition do próprio ruflo documentada); steal automático no claim (dono ativo é respeitado; steal só via release explícito ou reaper futuro).

## 2026-07-03 — DEV-1153: cascata Linear vira código (issue_flow.py) + Modo A é o padrão

**Decisão:** (1) A cascata do DEV-WORKFLOW §12.0 deixa de ser prosa interpretada e vira `_core/issue_flow.py`: `start <ID> --e2e sim|nao` (In Progress + comentários issue/projeto + project update + declaração E2E gravada em manifest `.pd/issue-flow/<ID>.json`), `step <ID> <gate> --evidence` (registra plan/review/e2e/pr), `close <ID> --report` (BLOQUEIA exit 1 sem review §6, sem E2E declarado-e-rodado, ou com git tracked sujo; pular gate exige `--skip <gate> --reason` e sai declarado). Done via `save_issue` direto fica PROIBIDO. (2) Fiscal no Stop: `_core/hooks/stop-issue-flow.py` cruza a issue da sessão (state do dispatch.py) com o manifest e acusa Done-fora-do-fluxo / manifest ausente / cascata em aberto — nunca bloqueia (estilo baseline lint DEV-1125). (3) **Modo A passa a ser o PADRÃO de execução de qualquer issue** — regra "sempre perguntar A ou B" aposentada (atrito sem ganho em 95% dos casos); Modo B só com pedido explícito do Felipe. Emendas em DEV-WORKFLOW §2/§12.0 + times/dev/CLAUDE.md.

**Origem:** DEV-1142 fechada via save_issue direto (pulou comentário de projeto, status update e relato) → Felipe irritado de cobrar o fluxo manualmente. Memória `feedback-cascata-linear-completa-obrigatoria` gravada.

**Alternativas rejeitadas:** só reforçar a prosa das skills (é exatamente o que falha — agente resume e pula); bloquear no Stop (Stop é relatório best-effort, bloqueio duro mora no `close`, que é o gate natural); label `e2e:obrigatorio` na issue (manifest local é mais barato e o close lê direto).

## 2026-07-04 — DEV-1155: guards da cascata viram PreToolUse nos 3 harnesses

**Decisão:** as 3 regras "só prosa" viram bloqueio real via `_core/hooks/pretooluse-cascade-guards.py` (runtime-neutro, protocolo JSON deny + exit 0, fail-open por ser guard de PROCESSO): (a) deleção de `.jsonl` em `.claude/projects` fora do `clean_transcripts.py`; (b) issue→Done fora do `issue_flow.py close` (MCP save_issue com state Done E GraphQL issueUpdate+stateId via shell); (c) SKILL.md NOVO fora do `new_skill.py` (Write em arquivo inexistente, heredoc/redirect shell, `*** Add File` do apply_patch — Edit/Write em skill existente passa). Cascas: Claude Code (settings.json, matcher `Bash|Write|Edit|mcp__*save_issue`), Codex (shim `pretooluse.py` → `_run_cascade_guard`, mesmo caminho do paid-api-guard), OpenCode (`handlers/guards.ts` em `tool.execute.before`, deny via `throw` — handler registrado ANTES do lifecycle pra abortar antes do side-effect de C4).

**Achado da análise:** a premissa de risco da issue ("OpenCode pode não ter intercept") caiu — `tool.execute.before` existe e o lifecycle já o usa; deny é por throw. Validação viva do throw pendente (junto do critério OpenCode da DEV-1141).

**Alternativas rejeitadas:** matcher `.*` no Claude (spawn de Python em toda tool — caro; matchers cirúrgicos bastam); fail-closed (é guard de processo, não segurança — indisponível não pode travar trabalho legítimo); allowlist por env var (allowlist por conteúdo do comando — os motores citados no próprio comando — é mais simples e não vaza pro ambiente).

## 2026-07-04 — DEV-1133: PR escalation matrix do motor = alçada por nível org

**Decisão (com Felipe, guiada decisão-a-decisão):** a matriz de escalonamento do motor 24/7 mimetiza **níveis de alçada de empresa**, não só classes de risco. 3 níveis: Coordenador/Analista (agente) · Gerente (Luiz) · Diretor/CTO (Felipe). Cada um aprova até um teto; acima, escala. Doc: `_core/PR-ESCALATION-MATRIX.md`. Pontos-chave:
- **Auto-merge só em branch de integração (`feature/*`), NUNCA em prod/main** (Opção B — produção sempre humana, §12.0b intacta).
- **Aprovação é assíncrona e não-bloqueante:** mandou PR → motor pega a próxima issue; retoma quando a aprovação chega. O motor nunca fica ocioso.
- **4 classes:** Trivial (doc comum + teste-only c/ smoke → agente auto-merge) · Review (código normal → Luiz nos repos dele, senão CTO) · Crítico (auth/billing/migration/RLS/deploy/cliente + **settings.json/CLAUDE.md/_core/hooks/guards/adapters** → só CTO) · Proibido (deploy/prod-merge/force-push/destrutivo/cliente → motor nunca executa, mão humana).
- **Classificação híbrida com viés de segurança:** regra determinística por path decide a maioria; agente só pode SUBIR classe; na dúvida escala pra cima.
- **Canais:** notificação = WhatsApp+Slack (crítico) / Slack (rotina); **aprovação/merge = aba Reviews do Linear** (verificado 2026-07-04: dá pra aprovar e mergear de lá); CTO é notificado de toda aprovação do Luiz (visibilidade).
- **Time-box consciente de expediente:** Luiz não respondeu → re-notifica + sobe lembrete pro CTO; urgente/P1 → CTO direto. Framework/fora-de-escopo pula o Gerente.

**Alternativas rejeitadas:** auto-merge em main (aposta num classificador perfeito — a sessão inteira foi consertar falso-positivo de classificador); zero-autonomia (não é motor, é preparador de PR); classificação por julgamento puro do agente (erra; determinístico+viés-de-segurança é mais seguro).

## 2026-07-04 — DEV-1105: budget guard = 2 budgets (dólar + esforço) + DEV-1134 colisão

**Decisão (guiada com Felipe):** budget guard mensal por squad tem **2 naturezas** (dentro de assinatura o custo $ é null, então 1 budget só deixa flanco aberto):
- **Budget de $ (API paga):** escada de tiers via MODEL-MAP conforme o $ acaba — `forte→médio→barato→free (opencode/deepseek-v4-flash-free)`. **Nunca para por falta de dinheiro** — cai pro free. Trabalho crítico perto do teto escala pro CTO.
- **Budget de esforço (tokens/volume):** o freio anti-loop-desgovernado (o free não resolve — também gasta token). 80% avisa (Slack) → 100% adia não-urgente + escala ("já rodou muito sozinho, pit-stop"). **Urgente/P1 nunca bloqueia** — sempre escala.
- Transversal: por squad, reset mensal, medição via cost_capture+outcomes, determinístico. **Números por squad a calibrar com dados** (conservador+uniforme primeiro; `.pd/budget.json`). Doc: `_core/BUDGET-GUARD.md`.

**Colisão humano×agente (DEV-1134, lembrado no meio):** motor confere Linear (assignee+status) + hook de sessão antes de claim; updates em tempo real obrigatórios; aviso bidirecional + pergunta parar/deixar; **colisão simultânea → agente PAUSA aquela issue e vai pra outra** (Opção 1, evita conflito de merge). Regra em `_core/PR-ESCALATION-MATRIX.md` §Coordenação.

**Alternativas rejeitadas:** budget só em $ (não segura loop); budget só em token (não protege o bolso); free como resposta ao budget de esforço (free também gasta token — não freia loop); agente continua na colisão (recria o conflito que a detecção evita).

## 2026-07-04 — MODEL-MAP: seletor do motor + reasoning effort + piso sonnet pra código

**Decisão (com Felipe):** o MODEL-MAP cobria tiers por harness mas tinha 2 lacunas pro motor: (a) reasoning effort não mapeado; (b) sem regra de COMO o motor escolhe tier ao lançar run headless por issue. Adicionado `motor_selector` ao MODEL-MAP.json: regra determinística por sinais da issue (não-código→barato/low · código trivial→médio/low-medium · story normal→médio/medium · epic/arquitetura/bug-duro→forte/high · loop autônomo→fronteira/high) + `reasoning_effort` por tier. **PISO DE CÓDIGO = sonnet** (Felipe: "haiku não tem capacidade de codar" — evidência da própria sessão: bugs sutis de encoding/CRLF exigem raciocínio; haiku codando = retrabalho). Transversais: dúvida→médio (errar pra baixo custa 1 retry — diferente da matriz de risco onde dúvida sobe); budget degrada até o free; retry sobe 1 tier e depois escala humano.

**Alternativas rejeitadas:** haiku pra chore de código (limitado demais); dúvida→forte (queima cota sem necessidade); seleção por julgamento do agente (determinístico é auditável e o launcher headless nem tem agente ainda no momento da escolha).

## 2026-07-08 — DEV-1280: gate executivo pré-merge no /aprovar-pr

**Problema:** trabalho autônomo (motor/subagentes/Luiz) merge via `/aprovar-pr` passava só por review **estático** (`/claude-review`) — nada era **executado** antes do merge. `cadencia-app` não tem CI → erro de build, quebra de tipo e teste flaky chegavam à produção. Os gates do `issue_flow.py` (git/review/e2e) são **declarativos** (só registram evidência) e o `/aprovar-pr` os **pulava** com `--approved-externally` — justo os PRs autônomos entravam com zero gate.

**Decisão (guiada com Felipe, contrapondo 2 premissas erradas do pedido):**
- **Não é "TDD".** TDD é disciplina de escrita (test-first), não gate de merge. O que se quer é **gate de verificação pré-merge** — categoria diferente.
- **Não reusar só o issue_flow.** A matriz de risco §6 e o flag e2e já classificam (reaproveitado), mas os gates dele são declarativos e não existe gate de build/test em lugar nenhum. O delta real é um gate **executivo**.
- **Gate 4.4 (novo):** detecção de stack determinística → **build+typecheck 1×** (determinístico — repetir é desperdício) → **test suite N× com `--sequence.shuffle`** (default 5, crítico 10 — repetir só agrega embaralhado, pega flaky/ordem/estado) → **lint = aviso não-bloqueante**. FAIL bloqueia o merge.
- **Loop N× só onde agrega:** build NÃO (determinístico); test SIM (embaralhado); e2e via `/linear-e2e-test` que **já** loopa o fluxo total (não reinventar). "Corrigir em lote no fim" rejeitado — 1 fix/iteração, re-roda, cap 3 (senão não se sabe qual fix resolveu o quê; e build quebrado mascara teste).
- **Classifier de e2e minúsculo e determinístico:** paths `migrations|auth|billing|rls|schema` + labels sensíveis → CRÍTICO; **fail-safe = em dúvida SOBE** (classificar errado pra baixo = bug em prod).
- **`--approved-externally` deixa de ser padrão** → vira **fallback** (só checkout impossível ou issue sem manifest, ex. PR do motor no container). Caminho normal: registrar steps reais (4.7) e fechar sem bypass.
- **Promoção da skill (achado — regra de análise):** a `aprovar-pr` vivia **só** na global `~/.claude/skills` (dir real, NÃO versionado); a premissa "2 cópias" da issue era falsa. Promovida pro framework: fonte real em `stamper/skills/aprovar-pr/` (git) + **duas junctions** (global + `.claude/skills` do repo) → zero drift (melhor que o resto das skills globais, que são cópias divergentes).

**Alternativas rejeitadas:** loopar build/typecheck (determinístico → resultado idêntico, só queima tempo); repetir test na mesma ordem (pega pouco — shuffle é o que dá eficácia); e2e universal em todo PR (lento/caro/falso-bloqueio — só crítico); classifier por LLM (custo + não-determinismo num gate de segurança; determinístico+fail-safe é auditável); só consumir manifest do issue_flow sem executar (mantém o furo dos PRs autônomos sem manifest).

## 2026-07-10 — DEV-1275 (incidente): motor sem cooldown pós-BLOQUEIO → loop infinito de claim/release

**Problema (achado em produção, não em teste):** DEV-1275 ficou ~3h sendo reclamada e liberada pelo motor a cada ~20-40s (~300 ciclos), cada um rodando um subprocesso `claude --model sonnet` real. Causa raiz: quando o worker declara `BLOQUEIO.md` (0 commits), `motor_run.py` chamava `linear_claims.release()` puro — devolve a issue pra Todo **sem label**. Como `eligible_queue()` (`motor_select.py`) só exclui `EXCLUDE_LABELS = {bloqueado, aguardando, pendente}`, a issue liberada ficava 100% elegível de novo no ciclo seguinte. Bloqueio estrutural (ex.: a issue pede pro motor rebuildar a própria imagem — impossível de dentro do container) nunca é transitório, então o worker declara BLOQUEIO de novo, infinitamente. Não era bug específico da DEV-1275 — qualquer issue "impossível" pro worker cai no mesmo loop.

**Decisão:** reusar o mecanismo já existente `park_waiting_harness` (criado pra harness indisponível — mesmo padrão: Todo + label de espera tira da `eligible_queue`) em vez de inventar um novo. Refatorado em `_park()` privado + 2 wrappers públicos: `park_waiting_harness` (inalterado, prioriza `aguardando`) e `park_blocked` (novo, prioriza label `bloqueado`). `motor_run.py` agora bifurca no caminho "sem commits": `BLOQUEIO.md` presente → `park_blocked` (tira da fila até remoção manual do label); sem `BLOQUEIO.md` → `release()` como antes (não mexido — sem evidência de loop nesse caminho).

**Ação imediata do incidente:** motor desligado (kill switch), label `own:motor` removida manualmente da DEV-1275 pra estancar. DEV-1275 segue aberta (Felipe quer confirmar que o rebuild de 13:20 realmente ficou certo antes de fechar).

**Alternativas rejeitadas:** cooldown por tempo (adiciona estado/complexidade nova; label já resolve e já existe); contador de tentativas N antes de blacklist (mais estado pra manter; BLOQUEIO já é um sinal binário claro — não precisa de tentativas repetidas pra confirmar que é estrutural); mover pra status "Blocked" (teams atuais não têm esse status — mesma razão que already levou o `park_waiting_harness` a usar label em vez de status).

**Cascata formal de review (DEV-1287, mesmo dia):** rodada completa por classe crítica (mudança em `_core/`) — `/claude-review` (Opus 4.7) + `/dual-review` (GLM 5.2 + Qwen 3.7 Max) + `/runtime-fix-review` (agente independente, read-only). GLM apontou um "bug" (falta de `break` no loop de prioridade de label) que na leitura direta do código **não existe** — `break` já estava presente; descartado como falso positivo, não corrigido. 2 achados reais convergentes entre Opus e o runtime-fix-review independente, ambos corrigidos: (1) `reason` passado pra `park_blocked` em `motor_run.py` estava sem o prefixo `"motor_run: "` que o branch `release()` irmão usa (inconsistência de auditoria, não bug funcional); (2) o `except Exception` genérico pós-claim em `run_cycle` caía pra `release()` puro mesmo quando `BLOQUEIO.md` existia — se a própria chamada de `park_blocked()` falhasse (ex.: GraphQL fora do ar), reabria o loop numa janela mais estreita (falha da chamada de parking, não do worker). Fix: o `except` agora refaz a mesma checagem de `BLOQUEIO.md` e prefere `park_blocked` também nesse caminho; `wt` inicializado como `None` antes do `try` pra não quebrar com `NameError` se a exceção ocorrer antes do worktree existir. Self-tests cobrem os dois casos novos (`parked_blocked` e `failed-rolled-back-blocked`).
