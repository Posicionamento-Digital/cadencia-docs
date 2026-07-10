---
type: source
source_kind: decisao
date: 
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]", "[[comercial]]", "[[infra]]", "[[marketing]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# Decisões — infra-memory

# Decisões — Squad Infra

## 2026-07-06 — Gate: incerto sempre tem dono humano; bug exige culprit, não título

**Contexto:** bug do worker growth (culprit vazio) ficou 1 dia órfão em own:triagem — o gate classifica bug pelo culprit e deixava "incerto" sem dono.
**Decisão:** (1) `incerto → own:felipe` no run_gate (nunca órfão em own:triagem). (2) NÃO adicionar heurística de "bug pelo título": o autofix só cobre cadencia-app; erro sem culprit (worker/dado-faltando) não é corrigível por ele — mandar pra lá é trabalho inútil. A garantia contra órfã vive no roteamento, não em adivinhar bug.
**Impacto:** nada fica invisível em triagem; autofix não recebe worker/dado-faltando. PR #7 health-check.
**Quem decidiu:** Felipe + Vitor (06/07).

## 2026-07-06 — Erro operacional recorrente resolve-se na origem (pre-gate), não mutando dados de cliente

**Contexto:** 12/39 tenants com canal blog habilitado mas sem blog provisionado geravam [blog] FAIL diário → issue Sentry recorrente. Minha recomendação inicial era desabilitar o canal (mutar growth_channels).
**Decisão:** pre-gate no growth_pipeline (mesmo padrão do pre-gate GHL de 2026-06-11) — pula o canal com SKIP quando não pode entregar, ANTES de rodar o script. NÃO muta growth_channels: presumir que o tenant não deve ter blog é decisão de produto que não temos. Quando provisionar, gera normal.
**Alternativas:** desabilitar canal (mutação de 12 clientes, presunção); rebaixar log ERROR→WARNING (não elimina o FAIL).
**Impacto:** flood do Sentry eliminado na origem, zero mutação de dado de cliente. PR #69 cadencia-growth.
**Quem decidiu:** Vitor (Felipe autorizou "sigo sua recomendação").

## 2026-07-06 — Check de drift de deploy via Coolify API, não GitHub hooks

**Contexto:** healthcheck da Central listava webhooks GitHub (GET /repos/org/hooks) pra checar auto-deploy — 404 porque nenhum token do cron acessa a org privada via REST (gh local usa OAuth de usuário; PATs disponíveis não veem a org).
**Decisão:** check via Coolify API (último deploy não-failed) — o Coolify é a fonte autoritativa do estado de auto-deploy e temos token funcional.
**Impacto:** healthcheck confiável sem depender de admin token da org. Padrão pra checks de deploy futuros.
**Quem decidiu:** Vitor (06/07).

## 2026-07-04 — Vigias validam marcador de sucesso, não mtime de log

**Contexto:** 3 incidentes silenciosos no mesmo dia (health check morto 8d por exec bit; pull do framework morto 8d; credenciais do watchdog nunca funcionais na Master) — em todos, o cron quebrado gravava erro no log e mantinha o mtime fresco, enganando o vigia.
**Decisão:** todo automatismo novo grava um MARCADOR tocado só em rodada bem-sucedida (ex.: `~/.self-test/last_ok.txt`), e o health check vigia o marcador. Content-aware por construção. Estrutural pros vigias antigos: DEV-1169.
**Alternativas:** validar conteúdo do log (frágil a formato); vigiar exit code do cron (cron não persiste).
**Impacto:** self_test_suite já nasce nesse padrão; deadman/heartbeat migram na DEV-1169.
**Quem decidiu:** Felipe + Vitor (sessão 04/07).

## 2026-07-04 — Deploys via poller único, não webhook por plataforma

**Contexto:** DEV-1160 previa webhook Vercel, mas webhook de deploy é Pro-only (conta Hobby).
**Decisão:** `deploy_watcher.py` na Master polla Vercel + Coolify a cada 10min → `deploy_log.record()` idempotente (unique deployment_id) → Slack só em novidade/terminal; backfill em bulk silencioso. Supabase (sem API de histórico) registra no ponto de disparo.
**Impacto:** cobertura uniforme das 2 plataformas sem depender de plano pago; dedup webhook×poller garantido pela tabela.
**Quem decidiu:** Felipe (aprovou desvio declarado) + Vitor.

## 2026-07-04 — Secrets headless do user master via ~/.config/pd/op.env

**Contexto:** `/etc/onboarding/op.env` é root-only; crons do user master (deploy_watcher, suite, watchdog) não resolviam credencial — 2 caminhos de ação do watchdog nunca funcionaram em produção.
**Decisão:** `~/.config/pd/op.env` (600, só SA token) sourceado pelos crons do master; o adapter `_shared/secrets` resolve o resto via op CLI. `run.sh` do health check exporta também `LINEAR_API_KEY`.
**Impacto:** padrão pra qualquer cron novo do user master; 1P segue fonte única (só o SA token toca disco).
**Quem decidiu:** Vitor (validado no voo supervisionado DEV-1174).

Append-only. Mais recente em cima.

---

## 2026-06-29 — Limpeza inteligente de worktrees + vault 1P é acento-sensível (secrets map)

**Contexto:** 10 worktrees órfãs acumuladas (subagentes `isolation:worktree` + worktrees de feature) poluindo `git worktree list`. Ao automatizar a limpeza no `/encerrar-sessao`, descobriu-se que o critério "issue fechada → limpa" nunca funcionava: `secrets.get('LINEAR_API_KEY')` sempre falhava. Investigação revelou bug no `SECRETS-1P-MAP.json`.

**Decisão / achados:**
1. **Worktree `locked` exige `git worktree remove --force --force`** (duplo force). O single force e o `git worktree prune` não removem `locked` — daí o acúmulo. Helper `_core/cleanup_worktrees.py` encapsula a decisão (preserva se dirty / não-mergeada / issue Linear aberta; limpa caso contrário) e roda no passo 6.1 do `/encerrar-sessao`.
2. **Vault do 1Password é ACENTO-SENSÍVEL no Service Account.** `op item get --vault "Servicos & Tools"` falha; só `"Serviços & Tools"` (com ç + acento) resolve. Vários secrets estavam quebrados por isso. Regra nova no `_meta` do mapa + validação obrigatória de cada entry via `secrets.get`.
3. **Mapa de secrets só contém SEGREDO real, com consumidor real.** Removidas `CADENCIA_SUPABASE_REF` (project ref público, lido via env+default), `ASAAS_API_KEY` e `STEVO_API_KEY` (sem consumidor via `secrets.get` + item 1P duplicado).
4. **Bug invisível em produção:** em Coolify/Master os secrets vêm por env var direta, então o mapa (caminho `op` CLI) nunca é exercitado lá — só quebra em estação local. Por isso passou despercebido.

**Alternativas consideradas:** deletar worktrees cegamente (descartado — perderia trabalho não mergeado); mapear `ASAAS`/`STEVO` no chute (descartado — item duplicado no 1P torna a resolução por nome ambígua; entry quebrada é pior que ausência).

**Impacto:** `/encerrar-sessao` agora varre worktrees com segurança; `secrets.get` resolve 10/10 entries. Pendente higiene 1P (deletar duplicatas Asaas/STEVO — destrutivo, aguarda Felipe).

**Quem decidiu:** Felipe.

---

## 2026-06-29 — Health check: notificar resolução (loop fechado) + canal por tipo de evento

**Contexto:** o watchdog avisava quando um crítico caía (🟢→🔴), mas a recuperação (🔴→🟢) era silenciosa — só zerava o state. Felipe pediu ser avisado também quando algo se resolve. Investigação paralela: o digest de 28/06 acusou `cadencia-webhook` como CRÍTICO, mas o serviço foi aposentado de propósito (envios migraram p/ Resend); e o `HealthCheck-Digest` se auto-acusava por causa do código `267009`.

**Decisão:**
1. **Canal por tipo de evento:** queda de crítico → Slack **+** WhatsApp (urgência); recuperação → **só Slack** (boa notícia, não trava o celular). Watchdog detecta transição 🔴→🟢 só em jobs `crit` (simetria com a regra de queda) pra evitar spam.
2. **`267009` (SCHED_S_TASK_RUNNING) não é falha** — o check `wintask` agora ignora esse código e cai na checagem de idade. "Task executando neste instante" ≠ erro.
3. **Serviço aposentado sai do `jobs.json`** — não se "auto-corrige" o que foi desligado de propósito. Restart cego de serviço `disabled` reverteria decisão do Felipe; a postura DRY do digest foi a correta.

**Alternativas consideradas:** notificar recuperação de não-críticos também (descartado — spam); manter `cadencia-webhook` no registry com `fix:none` (descartado — ruído permanente no painel); read-back das mensagens via Slack API (bloqueado por `missing_scope` no bot — usado `ts`+`chat.delete` como prova de persistência no E2E).

**Impacto:** loop de notificação fechado (caiu → avisa, voltou → avisa). Menos falso CRÍTICO no digest. Validado E2E 5x = 40/40 PASS, cleanup 5/5/0. Bug latente `_SHARED_WIN` (crash no import) corrigido de quebra.

**Quem decidiu:** Felipe.

---

## 2026-06-25 — Robustez do health check (DEV-864): 3 vigias independentes + auto-reporte do Dev

**Contexto:** o `#saude-sistemas` ficou mudo e ninguém percebeu — o health check (o vigia) estava cego. Investigação achou 6 defeitos convergentes (incidente `2026-06-25_health-check-cego`); o principal era o `watchdog.py` da Master com python path do Windows hardcoded (`C:/Python314/python`), que fazia `notify_slack` falhar silencioso no Linux. O vigia 24/7 rodava mas nunca avisava, e o `deadman.sh` não pegava (vigia execução, não entrega).

**Decisão:**
1. **Heartbeat de ENTREGA** (cron Master 18h50, não Grafana) — `digest_heartbeat.sh` lê um marcador (`last_digest_ok.txt`, gravado só quando o post tem sucesso) e alerta WhatsApp se o digest não chegou hoje. Marcador-em-arquivo em vez de ler o histórico do Slack (o bot token só tem `chat:write`).
2. **Auto-reporte do Dev** (cron local no Dev, não jump SSH via Master) — `dev_selfreport.py` (/10min) grava `status.json`; o health check lê o arquivo em vez de sondar cada job pela rota Windows→Dev instável (~50% trava). Frescura **fail-closed** (sem `ts` confiável → trata como velho).
3. **Path de binário sempre `sys.executable`**, nunca hardcode — e `notify_*` best-effort deve logar o erro (não `except: return False` mudo, que escondeu o defeito por dias).

**Alternativas consideradas:** heartbeat via alert rule Grafana (depende do Windows pushar — descartado); probe Dev via jump SSH Master→Dev (rota estável 1.6s, mas Felipe preferiu auto-reporte por não depender de SSH na checagem); manter retry client-side (não elimina ⚪ em janela ruim).

**Impacto:** 3 vigias independentes (deadman=execução, heartbeat=entrega, auto-reporte=Dev). `#saude-sistemas` volta a receber digest 24/7 e falhas de notificação são detectadas. VPS Dev passou a ter cron. Checklist de criação de task PD documentado.

**Quem decidiu:** Felipe.

---

## 2026-06-24 — Health check de automatismos na VPS Master (24/7) + auto-correção autônoma

**Contexto:** Sistema de health check (DEV-832) nasceu rodando no Windows do Felipe — único ponto que alcançava os 3 ambientes. Mas criava 2 furos: o vigia não era vigiado, e produção ficava sem monitoramento quando o PC dormia. Felipe identificou o gap ("tenho impressão que falta algo").

**Decisão:** (1) Mover o core pra **VPS Master** (sempre ligada, determinística — respeita SECURITY §1), vigiando produção 24/7; código ambiente-aware (`HEALTHCHECK_LOCAL`/`HEALTHCHECK_SCOPE`) roda tanto no Windows (tudo SSH) quanto na Master (master=local, dev=SSH). (2) **Ligar a auto-correção autônoma (`--apply`)** com 3 salvaguardas: leitura-vazia→UNKNOWN (não FAIL), re-check inline antes de restart, cap 2 tentativas→escala issue. (3) **Dead man's switch** (`deadman.sh` /30min) fecha o "quem vigia o vigia". (4) Windows reduzido a vigiar só as 4 tasks locais.

**Alternativas consideradas:** manter no Windows (rejeitado — ponto único de falha que dorme); deixar `--apply` desligado em observação por dias (rejeitado — Felipe esquece e perde contexto; salvaguardas + 1 falso positivo já calibrado dão confiança).

**Impacto:** produção (cadencia-webhook, growth_pipeline, cadence_tick, etc.) auto-corrigida 24/7 sem depender do PC. Restart de serviço via SSH = ação determinística, não viola regra VPS Master. Crons novos na Master: digest 18h30, watch horário, deadman /30min. SSH Master→Dev criado (`~/.ssh/dev-access`).

**Quem decidiu:** Felipe.

## 2026-06-19 — Deploy key e env vars do cadencia-app entregues via 1P, nunca por WhatsApp

**Contexto:** Luiz pediu (via WhatsApp) pra adicionar a deploy key dele no repo `cadencia-app` e mandar **todas as env vars do Railway via WhatsApp** pra configurar o Coolify (migração Railway→Coolify). Despejar env de produção (service_role Supabase, OpenAI, Asaas, GHL PIT, etc.) em texto claro no WhatsApp viola a regra de credenciais.

**Decisão:** (1) Deploy key — a chave que Luiz mandou já era deploy key de outro repo (GitHub rejeita a mesma chave em 2 repos); gerei par ed25519 novo exclusivo pro cadencia-app, pública no GitHub via `gh api` (read-only), privada no 1P. (2) Env vars — puxadas direto da Railway via project token (sem login interativo) com `RAILWAY_TOKEN` + `railway variables --service cadencia-app --kv`, filtradas (removidas RAILWAY_* internas), salvas no 1P como Secure Note. Entrega ao Luiz **só via 1Password** (vault Hostinger VPS, que ele acessa), nunca por WhatsApp.

**Alternativas consideradas:** mandar via WhatsApp (descartado — vazamento); share link 1P (descartado — Service Account não gera share, 403; usar vault compartilhado em vez disso); reusar a chave do Luiz (impossível — GitHub bloqueia duplicação de deploy key).

**Impacto:** Padrão para entregar credenciais de infra ao Luiz = vault `Hostinger VPS` no 1P. SA não enxerga esse vault — criar no vault acessível e Felipe move pelo app, ou adicionar o vault ao SA. ANTHROPIC_API_KEY foi exposta no transcript durante debug → rotação pendente.

**Quem decidiu:** Felipe.

---

## 2026-06-09 — Netdata removido permanentemente; Alloy como único stack de monitoramento

**Contexto:** Incidente PDL-440/PDL-471 — VPS Master sob throttling da Hostinger por excesso de CPU (steal ~90%). Diagnóstico revelou Netdata rodando em paralelo com Grafana Alloy, consumindo ~11% de CPU sem nenhum benefício adicional (Alloy já coleta todas as métricas).

**Decisão:** Netdata desativado e desabilitado permanentemente (`systemctl stop netdata && disable`). Grafana Alloy permanece como único sistema de monitoramento da VPS Master. Regra: uma ferramenta por responsabilidade — Alloy coleta, Grafana Cloud visualiza, webhook v2 alerta.

**Alternativas consideradas:** manter Netdata como backup local — descartado (overhead constante sem uso ativo; Alloy cobre o mesmo escopo).

**Impacto:** ~11% CPU liberados permanentemente. Elimina risco de reincidência de throttling por consumo duplo. Health checks Coolify (4–5s em 9 containers) continuam existindo mas ficaram dentro dos limites do plano após remoção do Netdata.

**Quem decidiu:** Felipe.

---

## 2026-06-09 — Projeto Linear dedicado "Infraestrutura — VPS, Monitoramento & Deploy" criado

**Contexto:** Antes desta sessão, issues de infra ficavam dispersas sem projeto dedicado. PDL-440 estava no backlog geral sem agrupamento.

**Decisão:** Criar projeto Linear "Infraestrutura — VPS, Monitoramento & Deploy" como destino de todas as issues do Squad Infra. Issues existentes (PDL-440) e novas (PDL-471) movidas para o projeto.

**Alternativas consideradas:** manter issues no backlog geral — descartado (dificulta visibilidade e priorização de infra).

**Impacto:** Todas as issues de infra futuras vão para este projeto. Rastreabilidade centralizada de incidentes, deploys, hardening e monitoramento.

**Quem decidiu:** Felipe.

---

## 2026-06-09 — Aprendizado: throttling do provedor ≠ noisy neighbor

**Contexto:** Diagnóstico inicial de steal ~90% assumiu noisy neighbor (hipervisor sobrecarregado). Causa real era throttling ativo da Hostinger por excesso de CPU da nossa VPS.

**Decisão:** Adicionar ao runbook de diagnóstico de lentidão na VPS: **checar painel do provedor nos primeiros 2 minutos** antes de investigar causa interna. Steal alto pode ser punição do provedor, não problema do host físico. Sintomas são visualmente idênticos.

**Impacto:** Próximo incidente com steal alto → primeiro passo é painel Hostinger + `sar -u 1 5`. Alerta `cpu.steal > 25%` no Grafana a criar (PDL futuro).

**Quem decidiu:** Felipe.

---

## 2026-06-05 — vault-watcher: watchdog local para Obsidian Sync

**Contexto:** Notas criadas no celular chegam na raiz do vault após Obsidian Sync, sem frontmatter e sem pasta. Solução anterior era manual (vault-organizer.py --dry-run + aplicar).

**Decisão:** Worker local determinístico em `C:\Users\felip\.claude\workers\` (fora do pd-framework, escopo pessoal). `vault-organizer.py` para organização em lote; `vault-watcher.py` com watchdog para eventos ao vivo. Task Scheduler At Logon (pythonw, sem console). Catch-up pass na inicialização resolve acúmulo com PC desligado. Documentado em `times/infra/workers/vault-watcher.md`.

**Alternativas descartadas:** hook Obsidian (requer plugin, não determinístico), cron periódico (latência vs watchdog ao vivo).

**Impacto:** Qualquer .md ou anexo (jpg/m4a/pdf/png) na raiz dos vaults Pessoal e Time PD é automaticamente classificado e movido. Regras em `RULES_PESSOAL` / `RULES_TIMEPD` — IA-Tecnologia sempre primeiro para evitar falsos positivos.

**Quem decidiu:** Felipe.

---

## 2026-05-25 — Refator Time Infra pós-Modo Foco (PDL-257)

**Contexto:** Squad Infra foi criado em PDL-226 ANTES da regra "criar com Felipe" + Modo Foco (decisão 2026-05-25). Estrutura ficou divergente do padrão consolidado nos demais Times (Marketing/Comercial/Dev): STATE.md L3 estava como "histórico recente" em vez de "Onboarding", sem `foundation/`, sem `skills/infra-debate.md`, persona Diego só mencionada como "futura" no CLAUDE.md.

**Decisão:**
- Refatorar STATE.md L3 pra "Onboarding — o que você precisa saber pra começar" (8 seções padrão populadas com info real do Infra). Histórico atual migrado pra este arquivo em formato estruturado.
- Adicionar `foundation/` com 5 docs constitutivos: README, security-principles, runbook-overview, allowlist-policy, monitoring-stack. Mais 1 doc EM REVISÃO (backup-recovery — não existe backup automatizado hoje).
- Adicionar `skills/infra-debate.md` (party mode adaptado, modelo `times/marketing/skills/marketing-debate.md`).
- Formalizar persona Diego no CLAUDE.md como **DevOps + SecOps acumulado** (até demanda justificar persona SecOps separada — revisitar quando PDL-243 tiver mais entradas).
- Estrutura monolítica (sem sub-squads) — Felipe é único operador, Diego é persona única. Promove pra sub-squads (`security/`, `observability/`, `deploy/`) quando auto-fix engine PDL-223 trouxer agentes especializados.
- Cadastrar 3 workers existentes em `workers/legacy/` como ponteiros (não migrar agora — webhook v2 estável em produção; migração formal em PDL-223 Fase 4).
- Criar 4 issues Linear filhas de PDL-221: backup automatizado VPS Master + 3 skills futuras (/rotacionar-credencial, /hardening-check, /restart-container).

**Preservado intacto:** `CLAUDE.md` base operacional, 5 skills VPS (vps-master, vps-dev, espelhar-repo-vps, validar-deploy-vps, conectar-vps), `runbooks/ALLOWLIST.md`, `context/<topologia-vps.md, alert-rules.md>`, `workers/legacy/README.md` + `workers/crons/schedule.yaml`, entrada bootstrap 2026-05-25 e demais migradas neste arquivo.

**Alternativas consideradas:**
- (b) Manter variante STATE atual (L3=histórico): descartada por quebrar consistência cross-Time. Agente lendo `/abrir-squad` em qualquer Time precisa receber onboarding em L3.
- (c) Adiar refator: descartada — sessão de bootstrap é o momento certo, custo de adiar = retrabalho cada vez que Squad Infra ganha novo contexto.
- Criar sub-squads agora (security/observability/deploy): descartada — overhead operacional (STATE/decisions/boilerplate por sub-squad) sem ganho concreto enquanto Felipe é único operador e Diego é persona única.
- Persona SecOps separada agora: descartada — volume PDL-243 (2 vazamentos) é sinal mas não frequência. Diego acumula até >2/mês justificar separação.

**Impacto:**
- STATE.md segue padrão consolidado pós-2026-05-25. Cross-Time consistente.
- foundation/ disponível pra runbook-executor (PDL-223 Fase 4) consultar critério de criação de runbook + ALLOWLIST policy formalizada.
- `/infra-debate` invocável (uso real: decisões cross-Time com Vitor como 2ª voz; reflexão estruturada Diego solo por ângulos seg/obs/op/custo/deploy).
- 4 issues Linear novas no backlog (backup VPS + 3 skills) — visibilidade pra Felipe priorizar.

**Quem decidiu:** Felipe.

---

## 2026-05-25 — Squad Infra bootstrap + ALLOWLIST inicial

**Contexto:** Fase 2 PDL-226 — primeiro squad operacional populado. Webhook v2 já existia em produção, faltava enquadrar no framework + ALLOWLIST formal pra runbook-executor (PDL-223 Fase 4).

**Decisão:**
- Squad Infra no framework com CLAUDE.md persona + STATE.md inicial + 3 context (topologia, alert-rules, ALLOWLIST) + 5 skills migradas + runbooks/ stubs por categoria
- ALLOWLIST com **5 containers permitidos** (coolify-proxy, sentinel, realtime + insight-artificial e assessoria-imprensa-cadencia quando containerizados) e **8 categorias proibidas** (cadencia-n8n-*, postgres/redis, ecuromiddleware-*, lara-*, cloudflared, sshd, NetworkManager, containerd)
- Webhook v2 em `/opt/grafana-webhook` mantido vivo — PDL-223 migra pra `workers/webhook-receptor.py` quando rodar

**Alternativas consideradas:**
- Reescrever webhook v2 já: descartado (já está rodando bem, sem regressão valendo o risco agora)
- ALLOWLIST mais permissiva: descartado (princípio deny-by-default — `_core/SECURITY.md` §1)

**Impacto:**
- Squad Infra navegável no framework com tooling vivo
- Stamper pode delegar tema infra via `/abrir-squad infra`
- PDL-248 (gotchas) destrava (depende deste squad existir)
- PDL-223 Fase 4 fica clara sequência de implementação

**Quem decidiu:** Felipe (escopo seguindo PDL-226 + alinhamento com plano técnico Fase 4)

---

## 2026-05-24 — Snapshots VPS Master + VPS Dev capturados

**Contexto:** Reconfiguração da VPS Master havia sido concluída em 2026-05-22 (ver entrada abaixo) e o ambiente Dev foi consolidado em paralelo. Faltava registro estruturado do estado completo das duas VPS pra servir de baseline pra qualquer mudança futura (deploy, troubleshooting, auditoria).

**Decisão:** Capturar snapshot completo das duas VPS em arquivos no repo:
- `docs/snapshots/vps-master-2026-05-25.md` — 17 containers Docker, 4 systemd customizados (grafana-webhook, cadencia-webhook, scoring-webhook, stamper-bot), crontab root com 38 entries, /opt/ com 8 projetos (master:master) + scripts (root:root) + containerd.
- `docs/snapshots/vps-dev-2026-05-25.md` — Ubuntu 24.04, node v24.15, python 3.12.3, **sem cron**, **sem systemd customizado** (só ambiente SSH interativo), /opt/ vazio (só containerd), /home/felipe/ com 3 repos + /home/luiz/ com 5 repos.

**Alternativas consideradas:** — (não documentado na época; provável que snapshot ad-hoc tenha sido a única opção considerada)

**Impacto:**
- Baseline auditável pra qualquer reconfiguração futura
- Squad Infra (CLAUDE.md) referencia esses snapshots como fonte primária da topologia
- `foundation/monitoring-stack.md` e `foundation/security-principles.md` puxam contexto desses arquivos
- Refresh manual quando mudar estado real (não há cron automático ainda)

**Quem decidiu:** Felipe.

---

## 2026-05-24 — Webhook v2 reconfigurado

**Contexto:** Versão anterior do webhook Grafana tinha problemas de duplicação de alertas (mesmo alerta gera N issues Linear + N mensagens WhatsApp) e não diferenciava alertas por squad responsável. Operação ficava ruidosa.

**Decisão:** Reconfigurar webhook v2 (`/opt/grafana-webhook/main.py`, systemd `grafana-webhook.service` porta 9300) com:
- **Rotulação por squad** via `labels.ruleGroup` na alert rule do Grafana → roteamento explícito pro Squad dono (Infra/Marketing/Cadência/etc).
- **Dedup fingerprint TTL 30min** — hash de (alertname + instance + severity) cacheado em `alert_cache.json`. Alerta dentro da janela = silenciado.
- **Saída dupla:** WhatsApp Stevo (notificação imediata Felipe) + Linear (issue com label `auto-fix` pra runbook-executor PDL-223 consumir).

**Alternativas consideradas:** — (não documentado na época formalmente; refator orgânico durante operação)

**Impacto:**
- 4 systemd webhooks em produção (grafana-webhook, cadencia-webhook, scoring-webhook, stamper-bot)
- 7 alert rules ativas conectadas (load, traefik RAM, CLOSE_WAIT, disco, RAM, SSH brute force, Vercel deploy)
- Base pra PDL-223 Fase 4 (runbook-executor consome issues label=auto-fix)
- Nota Obsidian `Time PD/Infra/Stack-Monitoramento-VPS-Master.md` documenta detalhes — credenciais hardcoded ali foram limpas em 24/05 (PDL-243 rotação pendente).

**Quem decidiu:** Felipe.

---

## 2026-05-22 — VPS Master reconfigurada do zero

**Contexto:** VPS Master estava operando como `root` direto, com histórico de configuração orgânica acumulada desde criação. Falta de baseline auditável + risco de segurança (root SSH ativo) + Coolify desatualizado.

**Decisão:** Reconfigurar VPS Master do zero com:
- **User `master`** (sudo OK), root SSH desabilitado, hardening SSH (chave-only, fail2ban, UFW)
- **UFW + allowlist Cloudflare** (only Cloudflare IPs nas portas 80/443; SSH em porta padrão restrita por IP)
- **Coolify 4.1.0** instalado limpo
- **Traefik v3.3.5** como reverse proxy gerenciado pelo Coolify
- Migração dos projetos PD pra `/opt/<projeto>/` com owner `master:master`

**Alternativas consideradas:** — (reconfiguração feita em sessão dedicada; alternativas não registradas formalmente — provável que upgrade incremental tenha sido considerado e descartado por dívida acumulada)

**Impacto:**
- Baseline auditável pra Squad Infra (snapshot 2026-05-25 captura estado pós-reconfig)
- Bloqueio PDL-242 ainda aberto: migrar `/root/` legados → `/opt/apps/` (paths Marketing/CS/Comercial dependem)
- PDL-213 também pendente: mover `/cadencia/` → `/opt/cadencia-growth/`
- Pre-requisito pra deploy pd-framework na VPS (Fase 7 PDL-242)

**Quem decidiu:** Felipe.
