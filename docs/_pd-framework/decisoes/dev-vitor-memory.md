---
type: source
source_kind: decisao
date:
entities: ["[[Cadencia]]", "[[Iasmin Lopes Pinto]]", "[[PD Framework]]", "[[comercial]]", "[[dev]]", "[[marketing]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---


# Decisões — dev-vitor-memory

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


# Decisões — Squad Vitor

(append-only — decisões arquiteturais relevantes ficam aqui, mais recente em cima)

---

## 2026-07-07 — DEV-1213: PostgREST max_rows sobrepõe .limit() do client — paginar sempre com .range()

**Contexto:** Kanban de Oportunidades (Cadencia CRM) só mostrava 1 card no funil Geração de Negócios (18 reais no banco). Investigação (não chute): a query em `page.tsx` pedia `.limit(5000)`, mas o projeto Supabase tem `max_rows=1000` configurado no PostgREST (confirmado via Management API `/v1/projects/{ref}/postgrest`) — esse cap é server-side e **sobrepõe qualquer `.limit()` do client**. Tenant tinha 1655 opportunities não-deletadas; sem `.order()`, o corte de 1000 era arbitrário (ordem física da tabela), sumindo com registros recentes (ex.: opp criada 01/07).

**Decisão:** nunca confiar em `.limit(N)` alto pra "resolver" o cap do PostgREST — é ilusório, o servidor ignora acima de `max_rows`. Toda query que pode potencialmente ultrapassar 1000 linhas (crescimento de tenant real) DEVE paginar de verdade com `.range()` em loop + `.order()` determinístico + propagar erro por página (não engolir resultado parcial).

**Invariante que fica pra qualquer squad de produto:** se uma tabela pode crescer além de 1000 linhas por tenant (contacts, opportunities, activities, etc.) e a tela lista "tudo", a query PRECISA paginar — subir `max_rows` do projeto não é solução (afeta todos os endpoints, é band-aid que volta a estourar).

**Fix aplicado:** `fetchAllOpportunities()` em `cadencia-app/src/app/(app)/app/growth/oportunidades/page.tsx` — PR #115, branch `feature/dev-1213-...`. `/codex-review`: 1 P2 corrigido (erro de página não tratado), sem P1.

**Quem decidiu:** Vitor (gate) + Felipe (aprovou plano).

---



## 2026-07-06 — DEV-1201: isolamento de sessões concorrentes por worktree

**Decisão:** worktree por sessão para isolar agentes concorrentes no mesmo clone (`C:\dev\pd-framework`). Direção fechada com Felipe (não reabrir). Ref aprendizado: Obsidian pessoal `IA-Tecnologia/2026-07-06 Git worktree vs branch`.

**Gate — furo corrigido:** "criar worktree no C3 via hook, transparente" é INVIÁVEL. Hook PreToolUse/PostToolUse não muda o cwd do processo do agente nem reescreve o file_path das tools Edit/Write; o agente lê/grava em caminho absoluto do clone principal. Portanto o isolamento tem de acontecer NO LANÇAMENTO da sessão (cwd = worktree antes do 1º tool), não via hook. Felipe aprovou o design (2026-07-06).

**Design adotado (2 camadas):**
1. Isolamento no lançamento — agentes spawnados/headless (motor, Modo B, Codex/OpenCode headless, 2ª sessão) nascem com cwd num worktree próprio (`.claude/worktrees/session-<id>`, branch `session/*`). Motor já faz isso (`motor_run.spawn_worker cwd=wt`).
2. Trava de posse (`session_lock`, `.pd/session-owner.json`) — a sessão interativa do Felipe segue dona do clone principal; 2ª sessão concorrente no MESMO tree é negada (deny barulhento) em vez de corromper silenciosamente. Fail-open em erro interno (guard de processo).

**Implicação de workflow (aceita por Felipe):** a mistura de trabalho acaba; em troca, um 2º Claude Code interativo manual no mesmo clone é BARRADO com aviso (relançar via `nova-sessao-isolada`), não isola sozinho (não dá pra relocar sessão interativa em curso).

**Worktree local:** DEV-865/junction NÃO se aplica — `C:\dev\pd-framework` está fora do OneDrive. Worktrees em `.claude/worktrees/` (gitignored), convenção do motor. Namespaces distintos: `session-*` (sessão) vs `motor-*` (motor) — cleanup nunca cruza.

**C6:** merge da `session/*` na main SEM checkout-duplo (merge pelo clone dono da main) + `git worktree remove` + `prune` + sweep de órfãos + release do lock. Ponto técnico mais escorregadio — provado em harness de sandbox antes do código vivo.

**Teste:** NUNCA validar no clone real. Sandbox `git clone --local` em `C:\temp`, hooks dirigidos por payload JSON (padrão `run_smoke`), guard-rail que aborta se cwd = produção.

**Faseamento:** Claude Code (core) → Codex → OpenCode. Core (`session_lock` + worktree) runtime-neutro; adapters só shell-out.

**Classe crítica** (`_core/hooks/` + contrato de runtime): merge exige claude+codex+runtime-fix review + Vitor + Felipe.

**Stories:** DEV-1201 fatiado em 8 (harness → session_lock → launcher → C6 → coexistência motor → Codex → OpenCode → contrato/docs).

---

## 2026-07-06 — Gate técnico do deploy do Motor Autônomo: runtime, systemd e bind mount de credenciais

**Contexto:** gate do PRD "Deploy do Motor Autônomo — runtime containerizado na VPS Dev" (Epics DEV-1195 a DEV-1199). O PRD deixou 2 trade-offs explícitos pro gate: (1) systemd-wrapper vs container puro; (2) escopo/modo do bind mount de credenciais.

**Decisão 1 — Container standalone com `--restart unless-stopped`, SEM systemd. Aposentar `_core/motor.service`.** Reboot já coberto pelo restart policy do Docker (daemon enabled no boot); systemd por cima = supervisão dupla, conflito, zero ganho. `motor.service` aponta pra Python-no-host (modelo incompatível com container) → marcado deprecated. Unidade de deploy = `compose.yml` versionado em `_core/deploy/motor/` (cap/restart/volumes/env_file declarativos, auditável por `docker inspect`). **Rejeitado** systemd chamando `docker run`.

**Decisão 2 — Bind mount rw escopado, nunca ro, sem montar `~/.claude` inteiro.** claude/codex fazem refresh de token → ro falha silencioso ao expirar. Escopo mínimo via `CLAUDE_CONFIG_DIR`/`CODEX_HOME` apontando dir dedicado (`~/.motor/{claude,codex}`) com só o credencial, montado rw de **diretório** (rename atômico do refresh quebra mount de arquivo único). Fallback: full-dir rw se CONFIG_DIR não isolar, mitigado por non-root + zero inbound. `gh` via `GH_TOKEN` do 1P (sem mount); `op` via `OP_SERVICE_ACCOUNT_TOKEN` (env).

**Ajustes ao PRD:** (a) caminho de auth do `gh` não estava definido → `GH_TOKEN` do 1P; (b) `op` CLI na imagem é exceção consciente ao SECRETS-PATTERN (motor spawna agentes que resolvem secret sob demanda) — registrar no Dockerfile; (c) guarda de drift imagem×deps = hash requirements committado vs baked → WARN+park, auto-pip rejeitado; (d) auto-pull per-ciclo na camada de deploy (entrypoint wrapper), não na lógica do motor.

**Epics derivados:** A (DEV-1195, imagem) → B (DEV-1196, runtime+clone+aposenta service) → C (DEV-1197, auto-pull+guarda drift) e D (DEV-1198, secrets+auth) em paralelo após B → E (DEV-1199, kill switch+dry-run+go-live). Todos `repo:pd-framework`. D vai em Modo A (toca secrets — Regra 5).

**Quem decidiu:** Vitor (gate), sobre as 5 decisões de arquitetura já fechadas com Felipe em 2026-07-06 (`times/dev/memory/decisions.md`).

---



## 2026-07-01 — Gate técnico "Cadencia: Gestão de Tráfego" (DEV-1046 a DEV-1052)

**Contexto:** PRD de nova feature multi-tenant do Cadencia (aba "Gestão de Tráfego", tenant piloto Iasmin Lopes Pinto/Agência Brokers), portando a engine de Meta Ads já validada em produção na conta própria da Cadencia (`/pd-marketing/.claude/scripts/meta-ads/`, VPS Master). PRD original (Paloma) tratava isso como "adaptação" — gate técnico encontrou 3 riscos subestimados.

**Decisões:**

1. **Credenciais de BM Meta por tenant NÃO usam `_shared/secrets.py`/1Password.** Esse padrão é pra credenciais globais/estáticas da própria Cadencia. Credencial de BM é dinâmica por tenant (cardinalidade N, gerada no onboarding) — vai em `tenant_config.config.meta_ads` (jsonb), mesmo padrão do `location_pit_token` do GHL (ADR-0005). Registrar isso evita reinventar o padrão errado no Epic 1 (DEV-1046).

2. **`config.py`/`meta_ads.py` do sistema legado (VPS) NÃO são portáveis 1:1** — usam credenciais globais de módulo (1 `.env`, 1 conta). Multi-tenant exige reescrita da camada de acesso a dado/credencial, recebendo `tenant_id` como parâmetro. Isso é o Epic 1 (DEV-1046) inteiro, não um detalhe de setup.

3. **`campaign_manager.py` legado tem o MESMO furo (threshold fixo: `CPP_PAUSE_MULTIPLIER=3.0`, `CTR_PAUSE_THRESHOLD=0.5`) que o motor de decisão novo precisa corrigir** (análise Pedro/Marketing achou isso no processo manual da cliente-piloto). Conclusão: o legado serve de referência ESTRUTURAL (fetch insights → aplica regra → loga decisão → ação supervisionada), não de regra de negócio a copiar. Motor de decisão (DEV-1048) é reescrita da lógica, não port.

4. **Chat de tráfego pago (DEV-1050) NÃO usa SOUL.md.** O padrão ADR-0002 (chat-agent "Tenho uma ideia") foi desenhado pra voz de marca/conteúdo — tráfego pago precisa de explicabilidade data-driven (por que essa sugestão, quais métricas pesaram), não personalidade. Reusar só a infra de sessão/memória do ADR-0002, prompt próprio orientado a `decisions_log`. Forçar SOUL.md aqui = retrabalho garantido.

5. **Sequência de Epics é linear nos 3 primeiros, não paralela** (o agrupamento original da Paloma sugeria paralelismo): DEV-1046 (fundação/credencial) → DEV-1047 (Tintim, com spike de API não mapeada) → matriz de decisão validada com a Manuela (artefato de produto, fora do Linear) → DEV-1048 (motor). DEV-1048 é bloqueador de arquitetura até a matriz existir — não estimar sprint antes disso.

**Epics criados:** DEV-1046 (Fundação Multi-Tenant), DEV-1047 (Tintim), DEV-1048 (Motor de Decisão), DEV-1049 (UI/Dashboard), DEV-1050 (Chat), DEV-1051 (Briefing/Criativo — candidato a corte v2), DEV-1052 (Relatório — candidato a corte v2). Todos no projeto `prod: Cadência — Roadmap` (não no projeto CS da Iasmin — é feature de produto, cliente é só tenant piloto).

---

## 2026-06-27 — Wrappers `_core/runtime/*.py` (DEV-907/908/909): casca fina cumprida 100%

**Contexto:** Os 3 wrappers sinalizados pelo subagente Modo B no DEV-886 foram codados sequencialmente.

**Entregue:**

1. **`scan_credentials.py` (DEV-908)** — fonte única canônica com 10 padrões (incluindo aws_access_key e private_key_block que o JS não tinha). lifecycle.ts C5 não tem mais regex inline.

2. **`protect_main.py` (DEV-907)** — tool-agnostic. lifecycle.ts C4 (Edit/Write/Patch) delega 100%. JS reduzido de ~25 linhas de lógica git pra ~15 de shell-out + roteamento. Caso `bash:git-commit` continua no hook original (já maduro, regex de cd/git -C/ssh é cara de portar).

3. **`close_session.py` (DEV-909)** — wrapper aceitando `session_id`. Mapping em `~/.local/share/pd-framework/sessions.json` (JSON, não SQLite). C3 registra ao abrir; C6 resolve ao fechar. Degrada gracefully sem mapping. Path Windows normalizado (bug `/c/path` cygwin descoberto e fixado).

**Princípio "casca fina + shell-out" cumprido 100% no adapter OpenCode.** Nenhuma lógica de git/branch/credencial vive em JS — só roteamento de eventos e idempotência in-memory (Set).

**Caveat:** `posttooluse-state-dirty.py` e outros hooks Claude que façam scan inline ainda usam código próprio (não delegam ao `scan_credentials.py`). Limpeza global de DRY entre hooks Claude e wrappers runtime fica como item de hygiene futura — não bloqueia nada hoje.

**Próximo passo natural:** DEV-910 (deploy VPS Dev) + DEV-889 (paridade real cross-runtime, depende do Felipe rodar nos 2 runtimes).

---



## 2026-06-27 — CLAUDE.md vs AGENTS.md: não duplicar por squad (decisão Felipe)

**Contexto:** Pergunta Felipe sobre se cada squad/projeto precisaria de um `AGENTS.md` próprio agora que o adapter OpenCode existe. Hoje cada squad tem só `CLAUDE.md`.

**Análise:**
- OpenCode lê `AGENTS.md`/`CLAUDE.md` da raiz via `instructions` no `opencode.json`, MAS não faz cascata por-cwd nativamente.
- A cascata por-cwd foi resolvida em DEV-887 pelo plugin `pd-adapter/handlers/context.ts` + `_core/context_resolver.py` (Python compartilhado), que lê o `CLAUDE.md` do squad correto via shell-out e injeta no system prompt do modelo OpenCode.
- Portanto, OpenCode "vê" o squad correto sem precisar de `AGENTS.md` em cada pasta.

**Decisão Felipe (2026-06-27):** **NÃO** duplicar `AGENTS.md` em cada squad. Manter como está — `CLAUDE.md` por squad é a fonte canônica, lida nativamente pelo Claude Code e via plugin pelo OpenCode. `/criar-squad` e `/criar-time` **NÃO mudam**.

**Caveat filosófico não-bloqueante:** o NOME "CLAUDE.md" tecnicamente viola a invariante C1 do contrato ("conteúdo vem de fonte neutra, não de arquivo cujo nome seja específico de um fornecedor"). Conteúdo já é neutro (F2 / DEV-884 limpou). Renomear pra nome neutro (ex: `SQUAD.md`) custaria refator de ~70 arquivos + risco de quebrar cascata Claude — não compensa hoje. Se um dia adotarmos um 3º runtime que não saiba ler `CLAUDE.md`, o resolver Python abstrai: mudar o nome canônico é 1 linha em `context_resolver.py`.

**Mudança no contrato:** nenhuma — invariante C1 cumprida pelo conteúdo, nome é detalhe de implementação.

---

## 2026-06-27 — DEV-886+DEV-888 (F3 lifecycle + skills): integração Amélia das 2 worktrees Modo B

**Contexto:** 2 subagentes spawnados em paralelo (Modo B) com worktree isolada, cada um editando seu próprio handler na estrutura modular criada pelo DEV-887. Voltaram em ~3min (888) e ~7min (886). Modo B funcionou: zero conflito no merge porque cada um editou só seu arquivo.

**Auditoria Amélia (sem 3 ciclos de fix consumidos):**

1. **`skills.ts` (DEV-888):** stub deliberado pra C7 (OpenCode lê `.claude/skills/` nativo, código adicional violaria "casca fina") + O1 soft mode com dedupe por sessão e regex multi-team (`PDL|DEV|CAD|COM|CSE|OPS|INF`). 2 mismatches menores de assinatura com `util.ts` (subagente assumiu `makeLog(ctx, namespace)` e `extractText(output)` em vez de `(client)` e `(parts)`) — fix Amélia: ampliei `util.ts` pra aceitar ambas assinaturas sem quebrar `knowledge.ts`/`context.ts`.

2. **`lifecycle.ts` (DEV-886, 357 linhas):** C3 idempotente, C4 com 2 fluxos (bash:git-commit delega 100% ao hook Python; write/edit faz inline mas só git CLI), C5 com varredura anti-credencial multi-pattern ANTES de propagar pro hook, C6 com lock anti-reentrante + alerta Stevo em conflito. Gotcha DEV-900 implementado (checa `.git/MERGE_HEAD`). Define `LifecycleCtx` local com `log` (não `client`) — fix Amélia: entry monta `{$, directory, log}` pra esse handler especificamente.

3. **Composição no entry:** ampliei lista de eventos compostos de 2 (`chat.message`, `experimental.chat.system.transform`) pra 6 (+`tool.execute.before`, `tool.execute.after`, `event`, `dispose`). Cada handler escuta os que precisa.

**Follow-ups técnicos sinalizados pelo subagente DEV-886 (não bloqueiam merge):**
- `_core/runtime/protect_main.py` — versão tool-agnostic do session-branch (atualmente só existe pra `git commit`)
- `_core/runtime/scan_credentials.py` — fonte única dos padrões regex de credenciais (hoje duplicados em `lifecycle.ts` e provavelmente hook pre-commit)
- `_core/runtime/close_session.py` — wrapper sobre `stop-session-branch.py` aceitando `session_id` por arg

**Gate Vitor pendente:** DEV-886 toca auto-merge na `main` + branch protection — categoria CRÍTICA (DEV-WORKFLOW §6 tabela: "Mudança crítica (auth, billing, deploy, **migração**, RLS) → TODOS reviews + Vitor + Felipe"). Análogo a "migration": auto-merge é mudança irreversível na fonte de verdade. **Mover pra In Review, não Done.** Roteiro de validação obrigatório:
- `/claude-review` na branch consolidada
- Vitor lê e aprova invariantes (C6 nunca dispara deploy; conflito STATE → VPS vence; gotcha DEV-900 preservado)
- Felipe sanity-check em sessão OpenCode real antes do merge `feature → main`

**DEV-888 (low risk):** pode fechar como Done direto — C7 stub + O1 soft não quebra contrato.

---



## 2026-06-27 — DEV-886 gate Vitor + claude-review inline (fechamento)

**Code review inline (Vitor agindo via Amélia, sessão corrente):**

Invariantes do contrato (C3-C6) auditados linha-a-linha:

- ✅ **C6 nunca dispara deploy.** `lifecycle.ts:257-304` só chama `git merge` via `stop-session-branch.py` e `stevo_client.py`. Zero chamada a vercel/coolify/railway/ssh. Invariante de segurança preservada.
- ✅ **Conflito STATE → VPS vence.** Delegado a `stop-session-branch.py` (que já tem `checkout --theirs` — DEV-WORKFLOW + SECURITY.md). Exit 2 → só alerta, não força resolução em JS.
- ✅ **Gotcha DEV-900 preservado.** `isMergeInProgress()` checa `.git/MERGE_HEAD` antes de qualquer interceptação em C4. Mesma lógica do `pretooluse-session-branch.py` que fixou DEV-900.
- ✅ **Anti-credencial em C5.** 7 padrões regex (sk-, Bearer, ghp_, sbp_, sb_secret_, xoxb, api_key/secret/password/token) varrem `args.content + args.new_string + args.newText` ANTES do shell-out. Hit → bloqueia + log error.
- ✅ **C4 idempotente.** `Set<sessionID>` previne re-checagem de branch protection.
- ✅ **Repos externos isentos.** `isWithinFramework` via `git rev-parse --show-toplevel` com normalização Windows+POSIX.

**1 bug encontrado e corrigido inline (Amélia):**

`lifecycle.ts:291` passava `"felipe"` como destino pro Stevo CLI. CLI real (`_shared/evo_client.py`) espera **número com DDI**: "felipe" seria normalizado pra "55felipe" → endpoint Evolution rejeita. Fix: constante `FELIPE_PESSOAL_PHONE = "5511914912127"` (instância `felipe-pessoal`). Trade-off: hardcode de número viola "credencial sempre via 1P" no espírito, mas número de telefone público não é credencial — aceitável até wrapper Python existir.

**Follow-ups técnicos (não bloqueiam Done):**

1. `event.type` casts `as any` no wire-up — schema OpenCode v1 é union; precisa narrowing por type guard quando OpenCode SDK estabilizar.
2. C5 cobre `Edit` single (`new_string`) mas não `MultiEdit` (precisaria iterar `args.edits[].new_string`). Hoje MultiEdit em STATE.md silenciosamente passa anti-credencial. **Issue follow-up sugerida** pra Amélia integrar.
3. 3 wrappers Python sinalizados pelo subagente continuam pendentes (não-bloqueantes): `_core/runtime/{protect_main,scan_credentials,close_session}.py`.

**Veredito Vitor:** APROVADO pra Done. Os 6 invariantes críticos estão preservados. Bug do destino WhatsApp era trivial (1 linha). Validação em runtime real OpenCode fica pra DEV-889 (F4 teste paridade).

**Patch pós-fechamento (Felipe, 2026-06-27):** "Stevo" descontinuado como nome — o `_shared/stevo_client.py` já era só um shim que importava `evo_client.main`. Lifecycle.ts atualizado pra chamar `_shared/evo_client.py` diretamente; logs/comentários renomeados pra "WhatsApp via Evo". Convenção a propagar pras demais skills/workers que ainda referenciam Stevo (item de limpeza global, fora deste epic). Constante `FELIPE_PESSOAL_PHONE` mantida — Evo CLI exige número.

---

## 2026-06-27 — DEV-887 (F3 contexto C1/C2): resolvedor unificado + modularização do plugin

**Contexto:** Implementação de C1 `load_context(cwd)` e C2 `detect_active_squad()` no adapter OpenCode. Anti-divergência entre adapters é critério não-negociável (decisão 3 de 2026-06-26). Decisão de design adicional pra viabilizar Modo B nas próximas issues (DEV-886, DEV-888).

**Decisões:**

1. **Resolvedor único em `_core/context_resolver.py`.** Modos `--routing` (C2) e `--context` (C1) num só script Python. Recebe `{prompt, cwd}` via stdin JSON, devolve `{squad, path_abs, context}` via stdout JSON. Adapters (Claude hooks + OpenCode plugin) consomem por shell-out idêntico. Anti-divergência cumprida.

2. **Cascata por cwd reescrita — "mais profundo com CLAUDE.md vence".** A lógica anterior (`userprompt-squad-context.py`) só testava 2 níveis (time/sub-squad). Nova implementação itera do path completo até a raiz; retorna o primeiro nível com CLAUDE.md presente. Suporta paths como `times/produto/cadencia/growth` corretamente. Hooks legados foram refatorados pra delegar.

3. **C2 invariante "tolerante a falso-positivo" → cwd > prompt.** Quando cwd já está dentro de um squad, prompt não pode rotear pra outro (menção casual a "cadência" enquanto trabalha em `times/dev` não desvia). Testado.

4. **Plugin OpenCode modularizado em `.opencode/plugins/pd-adapter/handlers/*.ts`.** O `pd-adapter.ts` monolítico virou wire-up que compõe `knowledge.ts` (C8) + `context.ts` (C1+C2) + `lifecycle.ts` (placeholder DEV-886) + `skills.ts` (placeholder DEV-888). Cada módulo é editável independentemente → Modo B com worktree em DEV-886/888 não conflita no merge final.

5. **Composição de handlers no `index`.** Entry exporta um único objeto onde cada chave de evento (`chat.message`, `experimental.chat.system.transform`) é uma função composta que itera os handlers de cada módulo em ordem. Padrão extensível pros próximos.

**Hooks Claude refatorados:** `userprompt-squad-routing.py` e `userprompt-squad-context.py` viraram thin wrappers (~30 linhas cada) que fazem `subprocess.run` pro resolver. Mapa SQUAD_ROUTING legado preservado como `_LEGACY_*` pra referência histórica até a próxima limpeza (não é lido em runtime).

**Trade-off:** dois shell-outs por mensagem do usuário (knowledge + context) onde antes era um. Cada um <100ms em loja local. Aceitável até evidência contrária.

**Refs:** `_core/context_resolver.py`, `.opencode/plugins/pd-adapter/handlers/context.ts`, `_core/hooks/userprompt-squad-{routing,context}.py`.

---



## 2026-06-26 — Runtime-Agnosticismo: gate do PRD + fatiamento em 7 Epics (DEV-883→889)

**Contexto:** etapa "Runtime-Agnosticismo & Adapter OpenCode" do projeto guarda-chuva PD Framework (`7c31c484`). PRD pela Paloma (`times/dev/context/prd-runtime-agnostico.md` + Linear Document `4729d90f8743`). Continuação de DEV-869 (F0 Done). Gate do PRD + derivação de Epics.

**Veredito:** APROVADO COM 3 AJUSTES. A pesquisa OpenCode (C4/C6 nativos, nada ❌) elimina o risco que mataria o projeto.

**Decisões Vitor:**
1. **Fatiamento final = 7 Epics, não 6.** Promovi o "scaffold do adapter" (DEV-885) a Epic próprio, separado do lifecycle. Razão: scaffold (`.opencode/plugins/` + `opencode.json` + `AGENTS.md` + padrão shell-out + fix snapshot/OneDrive) é fundação compartilhada por lifecycle/contexto/skills. Enterrado no lifecycle, serializaria artificialmente os outros dois.
2. **Ordem com travas explícitas:** F1 (DEV-883) → F2 (DEV-884) → scaffold (DEV-885) → {lifecycle 886 ‖ contexto 887 ‖ skills 888} → paridade (DEV-889). F2 depende de F1 (não se limpa o que não está nomeado). Os 3 handlers dependem do scaffold mas são independentes entre si. Registrado como `blockedBy` no Linear.
3. **C1/C2 (DEV-887) — resolvedor de cascata é função Python no core, NÃO JS no plugin.** Decisão dura. OpenCode não tem cascata por-cwd nativa; reimplementar "squad mais específico vence" em JS faria os adapters Claude e OpenCode divergirem → quebra a tese "core não se move". Mitigação obrigatória: extrair resolução de cascata pra função determinística no `_core/`, consumida por shell-out pelos dois adapters. **Maior risco arquitetural do projeto.**
4. **Padrão do adapter OpenCode = casca fina + shell-out.** Todo handler (C3–C8) faz shell-out pro mesmo Python do `_core/` que o adapter Claude usa. Nenhuma lógica de memória/lookup/cascata reimplementada em JS.
5. **C6 (close_session) automático é critério de conformidade, não feature.** Encerramento sem ação manual (`session.idle`/`session.deleted`) resolve o caso Luiz/VPS Dev melhor que o hook `Stop`. Validação em headless/idle é mandatória no Epic paridade — sem evidência, o caso Luiz fica não-provado e deve ser declarado como tal.
6. **Coexistência Claude+OpenCode no mesmo repo = não suportado** (corrida de session-branch). Limite declarado, não bug a resolver nesta rodada.

**Refs:** PRD Linear Document `4729d90f8743`, `RUNTIME-CONTRACT.md` (matriz OpenCode), `_core/BRIEF-RUNTIME-AGNOSTICO.md`.

---

## 2026-06-26 — DEV-868: Comunicação & Acompanhamento de Cliente automatizado (gate do épico)

**Contexto:** épico DEV-868 (projeto Automação do Onboarding CS, `ff96e3e2`) — camada de relacionamento contínuo pós-kickoff: grupo WhatsApp, log de interações, milestones, engajamento, agente de atendimento. PRD pela Paloma (`times/cs/context/prd-comunicacao-acompanhamento-cliente.md` + Linear Document). Gate do épico, não de uma story.

**Veredito:** APROVADO COM AJUSTES. Reusa infra em produção (receiver→fila→consumer, workers-cron, `cliente_registry`, APPLY×dry_run, Evo).

**Decisões Vitor:**
1. **Client Activity Logger = helper `_shared/client_activity_logger.py`** (não worker). Função pura `log_activity(cliente_slug, tipo, payload, *, apply)`, JSONL append-only por cliente (padrão estado-JSON, não DB → determinismo, zero dep da Master). Resolve cliente via `cliente_registry` + `linear-squad-map.json` — **não inventar mapa novo**. É a interface-contrato que destrava o Modo B.
2. **DEV-873 quebrada** em 873a (logger helper, DEV-873) + 873b (worker digest diário, **DEV-881**) — ciclos de vida distintos.
3. **Workers temporais (digest/milestone/check-in) = systemd-timer próprio**, NÃO fila do consumer (fila é reativa a webhook externo; estes são temporais).
4. **Ingestão inbound do WhatsApp (DEV-876) = webhook do Evo** (novo endpoint no receiver → job `whatsapp_msg`), nunca polling. Receiver só enfileira.
5. **Inferência do agente WhatsApp roda na VPS Dev** (decisão Felipe) — Master não roda agente com tool-use (`_core/SECURITY.md`). Rejeitada a opção de microserviço na Master (linha fina demais).
6. **DEV-879 (scaffolding pasta) subida pra Onda 1** — estrutura de pasta é pré-condição do logger/workers.
7. **DEV-877 fora do Modo B** — modifica worker vivo de produção (DEV-797, estado JSON); exige snapshot + `/runtime-fix-review` + regressão `test_workers.py`.

**Passo 0 (antes de spawnar Modo B):** fechar 3 contratos de interface — (a) assinatura/formato JSONL do logger; (b) schema do job inbound `whatsapp_msg`; (c) mapping repo↔cliente (DEV-878).

**Ondas:** 1 (Modo B) DEV-870/872/873/879 · 2 DEV-871/874/881 · 3 (seq) DEV-875/877/878 · 4 (épico) DEV-876.

**Riscos sub-dimensionados no PRD:** ingestão inbound é arquitetura nova; loop de eco (resposta→atividade→digest); latência de resposta no grupo; custo de API sem rate-limit; regressão DEV-797.

**Refs:** PRD Linear Document `prd-onboarding-cs-comunicacao...`, comentário gate em DEV-868.

---



## 2026-06-26 — DEV-873: Client Activity Logger — fonte única = Linear, não JSONL local

**Contexto:** plano técnico do logger (Passo 0 do DEV-868). O logger é chamado de **múltiplos hosts**: Felipe local (Windows) via `/log-sessao`, VPS Dev, VPS Master (workers/consumer). O digest (DEV-881) roda só na Master.

**Problema:** se a atividade fosse gravada num JSONL local (como o PRD/gate inicial assumiu), o digest na Master não enxergaria atividades logadas no clone do Felipe → fonte fragmentada por host.

**Decisão Vitor:** a fonte da verdade é o **project update no Linear** (`projectUpdateCreate`), compartilhado entre todos os hosts. O digest **lê os project updates do dia** via `list_project_updates`. O JSONL local (`_shared/_state/activity/<slug>/`, gitignored) vira só cache/auditoria, não fonte.

**Implica:** DEV-873 também **implementa `save_project_update` + `list_project_updates` no `_shared/linear_client.py`** (hoje só tem `graphql()` esqueleto). `is_cliente` NÃO bloqueia o status update (registro interno vale pra qualquer projeto/solo); o gate `cliente_registry` aplica só no outbound (digest/email/WhatsApp).

**Descoberta colateral:** DEV-872 deve **estender** `times/cs/foundation/templates-email/` + `templates-whatsapp/` + `render()` existentes — NÃO criar `templates-comunicacao/` nova (evita duplicação).

**Refs:** contrato completo em `times/cs/context/plano-DEV-873.md`.

---

## 2026-06-22 — Cadencia CLI/MCP: repo dedicado `cadencia-cli` (não dentro de cadencia-app)

**Contexto:** projeto novo "Cadencia — CLI/MCP de Controle" (Linear `7648831d`, team DEV) — lib Python + CLI (+ MCP futuro) pra operar o Cadencia por terminal/agente. Decisão de onde mora o código. Felipe inclinava pra dentro de `cadencia-app` (é feature do produto).

**Decisão Vitor:** **repo dedicado `cadencia-cli`** (org Posicionamento-Digital).

**Razões:**
1. `cadencia-app` é Next.js/TS com deploy automático Vercel — uma lib/CLI Python lá dentro mistura runtime, polui o build/deploy e acopla o versionamento da CLI ao app.
2. A lib é **ferramenta de operação** (fala Supabase/SSH/Resend, lê 1Password), não código de produto que vai ao browser/Vercel.
3. Vida e versionamento independentes do app; pode ser instalada/rodada por cron e por qualquer agente via shell.

**Rejeitadas:**
- Dentro de `cadencia-app`: acoplamento de runtime + deploy (acima).
- `pd-framework/_shared/cadencia/`: reusaria os clients existentes (supabase_client/ghl_client/stevo_client) e a infra 1P — mais barato —, mas amarra a ferramenta ao framework pessoal e dificulta uso multi-cliente/standalone futuro. Pode-se **importar/portar** esses clients pro `cadencia-cli` como ponto de partida.

**Arquitetura:** 3 camadas (lib → CLI → MCP futuro), registry/plugin auto-registrável, camada de acesso decidida por comando (read→Supabase; mutação com lógica→/api/app quando houver token de serviço, ver DEV-582; disparo→HTTP HMAC). Não hardcodar destino de worker (migração DEV-21 In Progress).

**Epics:** DEV-726 (Fundação) → DEV-727 (Comercial) + DEV-728 (Conteúdo) → DEV-729 (E2E). Repo nasce no `/linear-planejar-issue DEV-726`.

**Refs:** PRD `times/produto/cadencia/context/prd-cli-mcp-controle.md`, levantamento `context/cli-mcp-levantamento-20260622.md`.

---



## 2026-06-10 — generation_queue: semântica única + dedupe como invariante (PDL-171)

**Contexto:** `generation_queue` operava com 2 semânticas na mesma tabela — fila de jobs do Railway (carrossel, consumida por `queue_id`) e bookkeeping de aprovação multi-canal do frontend (rows com `channels[]`, sem consumidor). Resultado: órfãs `pending` acumulando, cron da VPS consumindo rows alheias e gerando blog duplicado em prod (3 pares confirmados no tenant felipe-salgueiro), drift de schema desde abril.

**Decisão (invariantes a preservar):**
1. **A fila é do Railway.** Row de bookkeeping do frontend nasce `status='dispatched'` — registro, nunca trabalho pendente. Não existe consumidor pra ela e não deve existir.
2. **Despacho de canais Growth vai por HTTP body** (trigger direct-mode), nunca pela coluna `channels` — a coluna é registro do que foi pedido, não contrato de execução.
3. **Dedupe é invariante do blog:** `blog_generate.py` nunca gera se `published_posts` já tem o `content_idea_id` (ambos os modos). Qualquer caminho novo de geração deve preservar isso.
4. **Consumo da fila sempre filtra canal** (`channels cs {blog}`) — consumidor nunca pega row que não é dele.
5. **Pipelines do mesmo tenant serializam** (lock por tenant no trigger_server). Tenants distintos seguem paralelos.
6. **Toda coluna em prod tem migration versionada** — `channel`/`topic` versionadas em `20260610210000`. Critério: `pg_dump --schema-only == migrations`.

**Não resolvido (issues próprias, não inflar PDL-171):** dispatch fire-and-forget sem reconciliação na aprovação (PDL-168 — endpoint atômico), watchdog pra `processing` órfão (PDL-167), flags de bookkeeping `linkedin_sent`/`newsletter_included` (PDL-476/477/478).

**Gotcha técnico:** `sb_get` na VPS usa curl — curl faz globbing de `{}` na URL; operador PostgREST `cs.{blog}` precisa ir URL-encoded (`cs.%7Bblog%7D`).

**Reviews pendentes pré-merge (mudança crítica — migration):** `/claude-review` + `/codex-review` + `/runtime-fix-review` na branch `felipeluissalgueiro/pdl-171-fix-definitivo-generation-queue` (cadencia-app).

**Refs:** incidente `2026-06-10_cadencia-generation-queue-4-defeitos-design-despacho.md`, incidente origem `2026-04-25_race-condition-generation-queue-railway-vps.md`.

---

## 2026-05-25 — Squad criado (PDL-256)

Squad Vitor criado como parte do bootstrap do Time Dev. Sem decisões arquiteturais ainda.


---



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

## 2026-06-11 — PDL-28: Enriquecimento DataStone como add-on Cadência — arquitetura

**Problema:** issue pede "expor waterfall como API no backend Cadência", mas o waterfall é Python avulso (openclaw-legacy) hard-coded pra location GHL da PD (custom field IDs fixos). Cadência é multi-tenant sem entidade de leads própria.

**Decisões Vitor:**
1. Port pra TypeScript dentro do cadencia-app (subset ~6 endpoints, não os 35 métodos do client). Waterfall = cadeia de HTTP calls, sem compute pesado.
2. Enriquecimento persiste no Supabase (`lead_enrichments`), não em custom fields GHL. No GHL do tenant escreve só campos universais + nota (sem field ID).
3. Fila própria `enrichment_jobs` + Vercel cron processor. Não reusar `generation_queue` (domínio distinto, evita repetir G-PDL-171).
4. Débito upfront por lead via RPC `debit_credits` existente + estorno em falha. `operation_type: "lead_enrichment"`. Regularizar RPC ad-hoc em migration formal (débito PDL-169).
5. Keys DataStone/Perplexity globais da PD (env Vercel); custo embutido no preço em créditos.

**Rejeitadas:**
- Worker Python na VPS reusando código original: repo cruzado, auth service-to-service, débito de créditos remoto — débito técnico pior que o port.
- Replicar custom fields GHL por tenant no onboarding: caro, frágil, sem rollback limpo. v2 se houver demanda.

**Reviews:** mudança crítica (billing) → `/claude-review` + `/codex-review` + `/runtime-fix-review` + Vitor + Felipe.

**Plano completo:** `times/produto/cadencia/context/plano-PDL-28.md`

---



## 2026-07-02 — Gestão de Tráfego: adendo do gate de 01/07 REVOGADO — credencial Meta Ads via Composio

Debate cross-Time (produto/marketing/dev, síntese Stamper, aprovado Felipe). O adendo "credencial de BM em `tenant_config.config.meta_ads` (padrão ADR-0005)" foi escrito sem considerar o DEV-844 — ADR-0005 é padrão do GHL legado em desligamento. **Decisão nova:** DEV-1046 monta sobre ADR-0010 (Composio OAuth único) + `social_integrations` + wrapper `src/lib/composio.ts` (DEV-845, pendente de merge — pré-requisito). Toolkit Meta Ads: GET_INSIGHTS (ctr/cpm/reach/frequency) + UPDATE_CAMPAIGN (status/orçamento). Spike obrigatório antes de estimar: (1) ausência de UPDATE_AD_SET — troca de segmentação pode exigir Graph API direto com token gerenciado (dissenso Pedro×Vitor registrado, spike arbitra); (2) fields de Ranking; (3) escopos/App Review Meta pra GA. Demo 03/07 = token direto descartável, não migra. Registro completo: Obsidian Decisões/Cross-Time/2026-07-02 + comentário no DEV-1046 + PRD atualizado.
