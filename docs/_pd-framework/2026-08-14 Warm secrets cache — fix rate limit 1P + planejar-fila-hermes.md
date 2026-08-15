# 2026-08-14 — Warm secrets cache (fix rate limit 1P) + skill `/planejar-fila-hermes`

> Sessão que resolveu problema recorrente de rate limit do 1Password em hosts Windows do framework (Galaxy Book, Dell, CAIXA1) e entregou a skill de curadoria de fila do Hermes runtime autônomo. Doc técnica consolidada.

---

## TL;DR

- **Problema:** cada skill/agente/worker em host Windows chamava `op` CLI toda vez que precisava de secret. Quota compartilhada da Service Account do 1P → um agente autônomo (Motor/Hermes) esgotava e travava sessões de outros hosts. Recorrência diária, 40min+ por incidente.
- **Solução:** cache local `%USERPROFILE%\.pd-hooks\op.env` populado via `pwsh _core/warm-op-env.ps1`. `_shared/secrets.py` lê daí (Etapa 2 do cascata) — zero hit no 1P no uso rotineiro. Padrão canônico já usado na VPS Master/Dev via `/etc/onboarding/op.env` (DEV-1347), agora estendido pra Windows.
- **Extra:** skill nova `/planejar-fila-hermes` (análoga a `/planejar-fila-motor`) — Felipe cura fila de issues Linear pro Hermes rodar autônomo no Dell via `hermes chat -q` com prompt versionado.

## Artefatos criados/alterados

### Novos

| Arquivo | Papel |
|---|---|
| `_core/warm_secrets.py` | Motor Python. Lê `SECRETS-1P-MAP.json`, faz 1 leitura por chave via `op` CLI, escreve `op.env` no formato `KEY=value`. Rate limit resolvido no ponto — 1 hit por chave, não N por skill. |
| `_core/warm-op-env.ps1` | Wrapper Windows idempotente. Valida `OP_SERVICE_ACCOUNT_TOKEN`, roda `warm_secrets.py`, seta `PD_SECRETS_ENV_FILE` persistente no User env, restringe ACL do arquivo (só user atual lê). ASCII-only pra rodar em PowerShell 5.1 legado (Dell/CAIXA1 não têm pwsh 7). |
| `_core/HERMES-TRIGGER.md` | Fonte única do comando pra disparar job Hermes one-shot no Dell. Comando canônico: `ssh dell-notebook 'hermes.exe chat --in "C:/c/c/pd-worktrees/pd-framework/hermes-main" --yolo --accept-hooks -q "<prompt>"'`. Documenta flags essenciais, pré-condição da worktree, debug. |
| `stamper/skills/planejar-fila-hermes/SKILL.md` | Skill nova (via `python _core/new_skill.py`). Top 10 candidatas, seleção por números na ordem, grava `.pd/hermes-queue.json` + label `own:hermes`, pergunta se dispara, SSH ao Dell (ou local se já no Dell). |
| `stamper/skills/planejar-fila-hermes/prompt-hermes.md` | Prompt versionado entregue ao Hermes. Cascata Linear + DEV-WORKFLOW estritos, PR sempre draft (Felipe aprova via `/aprovar-pr`), Telegram nativo, remove issue da fila individualmente (nunca zera sem processar). |
| `.pd/hermes-queue.json` | Fila com 9 issues do projeto Runtime Contract Adapter Hermes (DEV-1720/1719/1718/1717/1716/1715/1714/1708/1707). |
| Label Linear `own:hermes` | Workspace-level, cor `#5E7CE2` (azul). Aplicada nas 9 issues da fila. Distinta de `own:motor` (verde) e `own:agente` (autofix worker). |

### Alterados

| Arquivo | Mudança |
|---|---|
| `_core/SECRETS-PATTERN.md` | Tabela por-plataforma ganhou linha "Dev local (Windows)" com receita warm-op-env.ps1. Nova seção "Rate limit 1P — recorrência e mitigação" (sintoma, causa, remédio canônico, histórico dos 2 incidentes 2026-07-16 + 2026-08-13). Refs atualizados. |
| `_core/DELL-NOTEBOOK-SETUP.md` | §6.2 nova "Cache de secrets" — receita de bootstrap no Dell, rotação, fallback pra serviços Windows (Machine scope). |
| `_core/motor_select.py` | Novo profile `hermes` no `candidates_queue` (permite `assignee=Felipe` e `tipo:bug` — curadoria manual é delegação, não autonomia cega; ainda exclui P1, bloqueadas, own:* cruzados, sem roteamento). Filtro adicional: exclui issues de projeto `canceled`/`completed`. Argparse expandido: `--profile {safe,hermes}`. |
| `.gitignore` | Whitelist `!.pd/hermes-queue.json` (análoga à `!.pd/motor-queue.json`). |

## Como funciona o padrão warm cache

```
[Cascata de _shared/secrets.py]

1. os.environ[KEY]                     ← Coolify/systemd injetam aqui
      │ miss
      ▼
2. $PD_SECRETS_ENV_FILE (op.env)       ← ESTE É O NÍVEL ONDE WARM CACHE OPERA
      │ miss                              (Windows local: ~/.pd-hooks/op.env
      ▼                                    populado por warm-op-env.ps1)
3. op CLI + SECRETS-1P-MAP.json         ← só se cache stale/faltando entry
      │ miss
      ▼
4. raise SecretMissing
```

Fluxo típico após setup:

1. Felipe (ou agente) roda skill → chama `secrets.get('LINEAR_API_KEY')`
2. Etapa 1 (env var direta) miss
3. Etapa 2 lê `op.env` → **hit** → retorna valor
4. `op` CLI **nunca é chamado** → quota da SA preservada

Contraste com estado anterior (sem cache Windows):

1. Felipe roda skill → chama `secrets.get('LINEAR_API_KEY')`
2. Etapa 1 miss
3. Etapa 2 miss (arquivo não existe)
4. Etapa 3 chama `op` → consome quota
5. Próxima skill na mesma sessão → repete 1-4 → outra quota
6. Depois de N chamadas: `Too many requests. Your client has been rate-limited.`
7. Sessão trava por 15-60min até destravar

## Setup por host

**Windows (Galaxy Book, Dell, CAIXA1):**
```powershell
pwsh _core/warm-op-env.ps1     # ou powershell -File se pwsh não instalado
```
- Cria `%USERPROFILE%\.pd-hooks\op.env` com 14 secrets
- Seta `PD_SECRETS_ENV_FILE` persistente no User env
- Restringe ACL

**POSIX (macOS/Linux desktop):**
```bash
python _core/warm_secrets.py --output ~/.pd-hooks/op.env
export PD_SECRETS_ENV_FILE=~/.pd-hooks/op.env
```

**Rotação:** rerodar `warm-op-env.ps1`. Chave única: `-Only NOME_CHAVE`.

## Status atual (2026-08-14)

| Ambiente | Cache | Notas |
|---|:---:|---|
| VPS Master (Ubuntu) | ✅ | Já tinha (systemd EnvironmentFile) |
| VPS Dev (Ubuntu) | ✅ | Já tinha (DEV-1347) |
| Coolify workers (container) | ✅ | env vars diretas |
| Galaxy Book (Windows) | ✅ | Feito nesta sessão |
| Dell notebook (Windows) | ✅ | Feito nesta sessão |
| CAIXA1 (Windows) | ⏳ | Decisão do Felipe: adiado (workers da CAIXA1 não usam `_shared/secrets` hoje) |

## Riscos residuais

1. **Cache stale ao rotacionar** — sem auto-refresh. Rotacionar chave = rerodar `warm-op-env.ps1` manualmente. Se esquecer, chave antiga fica no cache até re-warm.
2. **Auth 401 não dispara warm automático** — sentinel de rate limit já existe (`PD_OP_RATELIMIT_SENTINEL`) mas cobre só rate limit, não expiração de chave. Fase 3 (não implementada): detecção de 401 → warm da chave específica.
3. **Superfície de ataque** — cache em disco tem mesma superfície das env vars atuais. ACL restrita ao user (só felip/claude leem).
4. **CAIXA1 fora do cache** — se algum agente rodar lá e chamar `op`, pode disparar rate limit e travar os outros hosts. Aplicar quando/se necessário.

## Roadmap (fases futuras — não implementadas)

- **Fase 3 (curto prazo se dor voltar):** auto-refresh do op.env (hook em `/abrir-dia` ou cron leve; detecção de 401 → warm da chave)
- **Fase 4 (estrutural):** 1P Connect self-hosted (era DEV-1349/1361 do projeto Resiliência 1Password cancelado 2026-08-13). Só se cache + auto-refresh não bastarem.

## Histórico de incidentes (contexto)

- **2026-07-16 (DEV-1347)** — 10h+ de travamento na VPS Dev. Crons re-chamando `op` a cada processo esgotaram quota. Fix: `/etc/onboarding/op.env`. Solução POSIX que virou padrão.
- **2026-08-13** — 40min+ de travamento cross-ambiente (Galaxy Book + Dell) durante primeira execução do Hermes runtime. Windows hosts não tinham cache; motor Hermes consumiu 93 tool calls em 18min55s, bateu rate limit e abortou fila. Fix nesta sessão: warm-op-env.ps1 promovido a bootstrap oficial Windows.

## Refs

- `_core/SECRETS-PATTERN.md` — padrão completo do adapter + tabela por plataforma + seção rate limit
- `_shared/secrets.py` — implementação do cascata (DEV-906)
- `_core/warm_secrets.py` + `_core/warm-op-env.ps1` — artefatos da fase 1 desta sessão
- `_core/DELL-NOTEBOOK-SETUP.md §6.2` — receita Dell
- `_core/HERMES-TRIGGER.md` — comando canônico Hermes
- `stamper/skills/planejar-fila-hermes/` — skill nova
