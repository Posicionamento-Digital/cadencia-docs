# Stack PD Motor Autônomo — VPS Dev

> **Doc canônica:** `_core/deploy/motor/` (compose + Dockerfile + build.sh + README) — este arquivo é o **complemento operacional** do que roda na VPS Dev especificamente.
> **Skills relacionadas:** `/motor`, `/ligar-motor`, `/desligar-motor`, `/logar-motor`, `/planejar-fila-motor`, `/nova-sessao-isolada`.
> **Issues fundadoras:** DEV-1196 (Epic B — deploy runtime), DEV-1198 (Epic D — secrets root-only).

## O que é

Container `pd-motor` — worker autônomo 24/7 que pega issues Linear com label `own:motor`, roda ciclo Claude Code/Codex isolado em worktree, commita e abre PR. Gate Vitor 2026-07-06 aprovou runtime standalone com `restart=unless-stopped`, **sem systemd por cima** (`_core/motor.service` está DEPRECATED).

## Estado atual (2026-07-31)

```
container: pd-motor
image: pd-motor:latest (build local, sha 418353f570ee)
status: Up 5h — sobe OFF por default (fail-safe do kill switch soberano motor.py)
network: pd-motor_default (isolado, saída-only)
ports: nenhum exposto (zero superfície inbound)
cpus: 1.0 (limite hard)
memory: 2g (limite hard)
```

**Logs recentes:**
```
2026-07-30T20:23:03 [motor][...] runtime pronto. kill switch soberano (motor.py) — sobe OFF por default fail-safe.
```

Última entry de ciclo de trabalho (antes do reboot):
```
2026-07-14T21:53:24 status=parked_blocked reason="bloqueio declarado: # BLOQUEIO — DEV-778 (épico em repo externo cadencia-cli)"
```

Ou seja: motor parado desde 14/07, subiu no reboot mas ainda OFF. Precisa `motor.py on` pra retomar.

## Mounts críticos (Epic D)

```
/home/felipe/.motor/claude → /home/motor/.claude    (bind mount RW)
/home/felipe/.motor/codex  → /home/motor/.codex     (bind mount RW)
```

Superfície mínima intencional — só o dir de auth de cada CLI é montado, não o `~/.claude` completo. Refresh de token (rename atômico) exige mount como DIRETÓRIO, não arquivo único.

## ENV vars

```
CODEX_HOME=/home/motor/.codex
CLAUDE_CONFIG_DIR=/home/motor/.claude
MOTOR_REPO_DIR=/home/motor/pd-framework
MOTOR_IDLE_SLEEP=300           # segundos entre polls quando não há trabalho
MOTOR_WORK_SLEEP=15            # segundos entre turnos de trabalho
OP_SERVICE_ACCOUNT_TOKEN=***   # 1Password SA — resolve STEVO/Slack/Linear/etc sob demanda
GH_TOKEN=***                    # GitHub — clone/push/PR
# runtime Python 3.12 + Node 22 dentro do container
```

Secrets carregados via `env_file: /etc/pd-motor/motor.env` no host (chmod 600 root:root, fora do git). Container não persiste creds em disco.

## Como ligar / desligar / ver logs

Preferir skills (encapsulam SSH + comando + verify):

```
/ligar-motor         # invoca motor.py on + monitora primeira run
/desligar-motor      # motor.py off (kill switch soberano)
/logar-motor         # tail dos logs em tempo real
/motor              # status/toggle geral
```

Manual (se skill quebrar):
```bash
ssh -i ~/.ssh/hostinger_dev_felipe felipe@2.24.117.172
sudo docker exec -it pd-motor bash
python motor.py on          # dentro do container
python motor.py off
tail -f /var/log/motor/*.log
```

## Fila do Motor — como Felipe controla o que ele pega

Skill `/planejar-fila-motor` — Felipe define ordem manual das issues `own:motor` num JSON versionado `.pd/motor-queue.json`, motor processa nessa sequência. Alternativa ao Modo B (daemon 24/7 pegando qualquer own:motor sem curadoria).

Modo A (curado, default recomendado) — Felipe controla exatamente o que roda.
Modo B (autônomo) — Motor pega qualquer own:motor em ordem de prioridade Linear + created_at.

## Compose file — LOCALIZAÇÃO

Único compose file que **sobreviveu ao userdel** — vive em `/home/felipe/pd-framework/_core/deploy/motor/compose.yml`, dentro do clone do framework do Felipe.

```yaml
# resumo do que está lá — canônico é o arquivo no repo
name: pd-motor
services:
  motor:
    build: .
    image: pd-motor:latest
    container_name: pd-motor
    restart: unless-stopped
    cpus: "1.0"
    mem_limit: 2g
    env_file: /etc/pd-motor/motor.env
    environment:
      CLAUDE_CONFIG_DIR: /home/motor/.claude
      CODEX_HOME: /home/motor/.codex
      MOTOR_REPO_DIR: /home/motor/pd-framework
      MOTOR_IDLE_SLEEP: "300"
      MOTOR_WORK_SLEEP: "15"
    volumes:
      - /home/felipe/.motor/claude:/home/motor/.claude:rw
      - /home/felipe/.motor/codex:/home/motor/.codex:rw
    # sem ports: — zero superfície inbound
```

## Cron notify (host, user felipe)

`_core/motor_notify_cron.sh` roda a cada 10min (ver [`crons-e-services.md`](crons-e-services.md)). Detecta eventos do motor (novos PRs, blocked, done) e notifica Felipe no WhatsApp via Evo/Stevo.

`_core/stale_claim_reaper_cron.sh` roda hourly (DEV-1344) — libera claims `own:agente` que ficaram órfãos (worker morreu no meio do turno).

## Riscos

- **Container sobe OFF, mas sobe** — se cair, `docker restart` traz de volta OFF (safe). Se Felipe esperava trabalho contínuo e não checou, motor pode ficar OFF em silêncio por dias.
- **`.motor/claude` e `.motor/codex` são bind mounts do host** — se Felipe tocar nesses arquivos com outro processo (login CLI simultâneo), race condition possível. Só rodar CLI dentro do container.
- **Rate limit Anthropic/OpenAI** — motor consome cota do plano Claude Code do Felipe. Sessões grandes drenam o pool diário. Sem quota alerting hoje.

## Refs

- Doc canônica: `_core/deploy/motor/` (compose + Dockerfile + build.sh + README no repo)
- PRD: `times/dev/context/prd-deploy-motor-autonomo.md`
- Plano detalhado: `times/dev/context/plano-DEV-1286.md`
- Plano falha observável: `times/dev/vitor/context/plano-motor-falha-observavel-2026-07-14.md`
- Sessões relevantes:
  - `stamper/memory/session_motor-observacao-live-fila-maint-cadencia_2026_07_10.md`
  - `stamper/memory/session_motor-p0-completo-ruff-1410-universal-parte-a-ops-54-55-60-48-49_2026_07_18.md`
  - `stamper/memory/session_central-observabilidade-auditoria-motor-desligado-claims-orfaos_2026_07_13.md`
- Incidentes:
  - `incidents/2026-07-10_motor-loop-infinito-claim-release-bloqueio.md`
  - `incidents/2026-07-10_park-blocked-fallback-silencioso.md`
  - `incidents/2026-07-10_stale-claim-abandonado-own-agente-spec-nunca-implementada.md`
