# Beszel — métricas de host + containers (Hub + Agents)

> **URL:** `https://metrics.cadencia.ia.br` · **Deploy:** Coolify VPS Master · **Status:** produção desde 2026-08-11
>
> Complementa Uptime Kuma (endpoints externos) com métricas internas: CPU/RAM/disk/load por host + status de containers Docker. Agents em 4 máquinas conectam ao Hub via SSH sobre Tailscale.

---

## Identidade

| Campo | Valor |
|---|---|
| Tipo | Serviço observabilidade (métricas host+container) |
| Stack | Go + PocketBase (SQLite) + SvelteKit UI |
| Imagem Docker (Hub) | `henrygd/beszel:0.14.0` |
| Imagem Docker (Agents Linux) | `henrygd/beszel-agent:0.14.0` |
| Binário (Agents Windows) | `beszel-agent_windows_amd64.zip` v0.14.0 (GitHub release) |
| Path no host (Hub data) | `/opt/observability/beszel/data` (bind mount → `/beszel_data`) |
| Porta interna Hub | 8090 (HTTP + WebSocket) |
| Porta agent SSH | 45876 (TCP, todos os agents) |
| Rede Docker Hub | `coolify` (10.0.1.0/24, IP interno atual `10.0.1.15`) |
| Coolify app UUID | `p357h20lk9ssr8cm5cbs0r6f` |
| Coolify project | Cadencia (`wbaqjeeyabmiy0gylk8ywutf`) |

---

## Por que existe

Kuma responde "o endpoint tá vivo?" — não responde "por que a CPU tá 90% no Master?" ou "o container X reiniciou?". Grafana faz isso, mas exige entrar em dashboard + PromQL. Beszel entrega **overview visual de todas as máquinas + containers em 1 tela** com histórico curto (30d) — ponte entre "tá tudo verde?" (Kuma) e "por que quebrou?" (Grafana).

---

## Arquitetura

```
Hub (VPS Master, Coolify)
  │
  │ SSH sobre Tailscale (porta 45876)
  │ Hub conecta AOS agents (arquitetura invertida — agent não conecta ao Hub)
  ├──────────────────────────────────────────────────────────────────┐
  ▼                                                                  ▼
Agent vps-master (Docker, coolify network)         Agent vps-dev (Docker, --network host)
Agent caixa1  (Windows NSSM service)                Agent dell-notebook (Windows NSSM service)

Hub UI + API expostos por:
  Traefik VPS Master → https://metrics.cadencia.ia.br
                       Basic Auth (Traefik) + PocketBase superuser (dupla auth)
```

**Ponto-chave:** Hub inicia a conexão SSH ao agent, não o contrário. Isso significa:
- Agent expõe porta SSH (45876) no interface Tailscale
- Hub tem 1 keypair `ed25519` (em `/opt/observability/beszel/data/id_ed25519`)
- Todos os agents recebem a MESMA pubkey no env `KEY` (nada exclusivo por agent)

---

## Systems monitorados

| Nome | Host (Tailscale) | Interface agent | Notas |
|---|---|---|---|
| vps-master | localhost (Docker network `coolify`) | Docker `beszel-agent-master` | Mesma rede do Hub (não usa Tailscale) |
| vps-dev | `vps-dev.taild6079b.ts.net` | Docker `--network host` | Necessário `--network host` pra bind na `tailscale0` |
| caixa1 | `caixa1.taild6079b.ts.net` | NSSM service `beszel-agent` | Windows (backup 24×7, escritório) |
| dell-notebook | `dell-notebook.taild6079b.ts.net` | NSSM service `beszel-agent` | Windows (laptop Felipe, offline frequente) |
| galaxybook | `galaxybook.taild6079b.ts.net` | NSSM service `beszel-agent` | Windows (laptop Samsung, `C:\Users\felip\beszel-agent\` — user-space install) |

**Gotcha galaxybook (2026-08-11):** install foi feito com `$InstallDir=C:\Users\felip\beszel-agent\` em vez de `C:\Program Files\beszel-agent\` porque Bash rodando como user `felip` não tem write em `Program Files`. Alternativa se precisar system-wide: usar `Start-Process -Verb RunAs` pra elevação UAC durante install.

---

## Credenciais

**Fonte única — 1Password vault `Serviços & Tools`:**
- `Beszel Hub - Admin [Cadencia]` — login PocketBase (campo `password`, superuser `felipe@cadencia.ia.br`)
- `Traefik Basic Auth - Observability [Cadencia]` — Basic Auth Traefik (compartilhado com Kuma)
- `Beszel Agents - Public Keys [Cadencia]` — pubkey SSH ed25519 usada por todos os agents (opcional; extraível via `ssh-keygen -y -f id_ed25519` no host)

---

## Alertas armados (16)

**Filosofia:** thresholds calibrados **por perfil de máquina** — servidor prod difere de laptop offline.

| System | Alerts | Thresholds |
|---|---|---|
| **vps-master** (prod crítica) | 5 | Status/1m · CPU>85%/5m · Mem>90%/5m · Disk>85%/5m · LoadAvg5>4/5m |
| **vps-dev** (homologação) | 4 | Status/1m · CPU>80%/10m · Mem>90%/10m · Disk>85%/5m |
| **caixa1** (backup 24×7) | 4 | Status/3m · CPU>90%/15m · Mem>95%/10m · Disk>90%/5m |
| **dell-notebook** (laptop) | 3 | Status/10m · CPU>95%/20m · Mem>95%/20m (sem Disk — enche por design) |

---

## Notificações — bloqueio conhecido (bug shoutrrr v0.17)

**Status:** ❌ **webhook Beszel → WhatsApp NÃO funciona** em Beszel v0.14 (com shoutrrr v0.17). Cobertura de push transferida pro Kuma.

**Diagnóstico (2026-08-11, decisions.md §Beszel webhook automático):**
1. Chave correta identificada via source code Beszel: `user_settings.settings.webhooks` (array). PATCH via API salva sem filtro (CREATE filtrava).
2. Alertas TRIGGERED corretamente (`alerts_history` grava evento em <60s após kill agent).
3. Payload capturado via webhook.site prova que shoutrrr generic v0.17 **envia POST sem custom headers** — sintaxe `@apikey=xxx` na URL não vira header `apikey:` no request.
4. Evo rejeita 401 sem header apikey → nenhuma msg WhatsApp.

**Tentado sem sucesso:**
- Proxy Python `beszel-evo-proxy.service` em `/opt/observability/beszel-evo-proxy.py` (systemd disabled + inactive) apontando `generic://10.0.1.1:9977/beszel` — Beszel também não chama proxy local (log Hub não tem "Sent shoutrrr" nem "Failed to send" mesmo com alertas triggered).
- 5 variações de chave JSON (`webhookUrls`, `shoutrrr`, `webhooks`, `urls`, `webhooks.urls`) — Beszel v0.14 tem bug de dispatch, não é problema de config.

**Cobertura de push atual (via Kuma):**
- Monitor Kuma `metrics.cadencia.ia.br/api/health` — se Hub Beszel cair → WhatsApp
- Monitor Kuma TCP `<agent>.taild6079b.ts.net:45876` (Dev, CAIXA1, Dell) — se agent cair → WhatsApp
- Se agent cair na Master (mesmo host do Hub) → Hub perde ele MAS Kuma ainda pega via monitor `cadencia.app.br` (proxy Vercel independente) — cobertura degradada mas ok

**Quando reativar:** aguardar Beszel v0.15+ ou fork com fix upstream. Proxy Python fica dormido pronto pra reenable.

Token EVO no 1P: `EVO - API - Num comercial` vault `E-mails` campo `password`. Número comercial Cadencia: `5511914956996`.

---

## Como criar/gerenciar systems via API

**Basic Auth Traefik REMOVIDO do Beszel (2026-08-11)** por causa de loop de SPA:
- Browser não repassa Basic Auth em POST XHR do form login PocketBase → Traefik retorna 401 → popup volta infinitamente
- **Fix aplicado:** removida label `observability-auth` do middleware Traefik do Beszel (mantido só no Kuma)
- **Segurança:** PocketBase tem auth próprio robusto (bcrypt+JWT+rate limit+session mgmt) — Basic Auth era redundante

**Setup via API interno (bypass Traefik, evita conflict):**

```bash
ssh -i ~/.ssh/hostinger_prod_master master@72.60.4.71 '
# IP muda em restart — reler
IP=$(sudo docker inspect $(sudo docker ps -q -f ancestor=henrygd/beszel:0.14.0) \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(list(d[0][\"NetworkSettings\"][\"Networks\"].values())[0][\"IPAddress\"])")
TOKEN=$(curl -sS -X POST "http://$IP:8090/api/collections/_superusers/auth-with-password" \
  -H "Content-Type: application/json" \
  -d "{\"identity\":\"felipe@cadencia.ia.br\",\"password\":\"<PASS>\"}" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)[\"token\"])")
curl -sS -H "Authorization: Bearer $TOKEN" "http://$IP:8090/api/collections/systems/records"
'
```

**Setup via API externa (agora funciona sem Basic Auth):**
```bash
curl -sS -X POST "https://metrics.cadencia.ia.br/api/collections/_superusers/auth-with-password" \
  -H "Content-Type: application/json" \
  -d '{"identity":"felipe@cadencia.ia.br","password":"<PASS>"}'
```

## Reset senha (se perder)

Beszel v0.14 tem **2 tabelas separadas** — `_superusers` (admin panel `/_/`) e `users` (UI normal). Reset em ambas:

**Superuser (`_superusers`):**
```bash
ssh master@72.60.4.71 'CID=$(sudo docker ps -q -f ancestor=henrygd/beszel:0.14.0)
sudo docker exec $CID /beszel superuser upsert felipe@cadencia.ia.br "<nova-senha>"'
```

**User regular (`users`) — via API superuser:**
```bash
TOKEN=$(curl ... auth-with-password)
curl -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"password":"<nova>","passwordConfirm":"<nova>","verified":true}' \
  "http://$IP:8090/api/collections/users/records/<user_id>"
```

**Gotcha:** UI login usa collection `users`, não `_superusers`. Se resetar só superuser, admin panel funciona mas UI normal não. Sempre resetar ambos com mesma senha.

**Atualizar 1P:** item `Beszel Hub - Admin [Cadencia]` vault `Serviços & Tools` campo `password`.

---

## Instalação Agent Linux (Docker)

```bash
# Master (dentro da network coolify)
docker run -d --name beszel-agent-master --restart unless-stopped \
  --network coolify \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /:/hostfs:ro \
  -e KEY="<PUBKEY>" -e PORT=45876 \
  henrygd/beszel-agent:0.14.0

# Dev (fora do Coolify, precisa --network host pra bind na tailscale0)
docker run -d --name beszel-agent-dev --restart unless-stopped \
  --network host \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /:/hostfs:ro \
  -e KEY="<PUBKEY>" -e PORT=45876 \
  henrygd/beszel-agent:0.14.0
```

`<PUBKEY>` extraído do Hub: `sudo ssh-keygen -y -f /opt/observability/beszel/data/id_ed25519`.

---

## Instalação Agent Windows (NSSM)

**Padrão canônico:** binário nativo GitHub release + NSSM 2.24 como Windows Service. **NÃO usar WinGet** — versão antiga, sem `--network host` semântica, gerenciamento zoado.

Script canônico em `C:\temp\install-beszel-agent-caixa1.ps1` (Windows CAIXA1/Dell):

```powershell
$PubKey = "ssh-ed25519 AAAA..."   # extraído do Hub
$Port = "45876"
$InstallDir = "C:\Program Files\beszel-agent"

# 1. Baixa beszel-agent.exe + nssm.exe pra $InstallDir
# 2. nssm install beszel-agent $InstallDir\beszel-agent.exe
# 3. nssm set beszel-agent AppEnvironmentExtra "KEY=$PubKey" "PORT=$Port"
# 4. nssm set beszel-agent Start SERVICE_AUTO_START
# 5. nssm start beszel-agent
```

Logs: `$InstallDir\agent.log` + `agent.err.log`.

---

## Gotchas conhecidos

1. **DNS público resolve, config Coolify não:** URL correta é `metrics.cadencia.ia.br` (não `infra.cadencia.ia.br` como consta em snapshots antigos). Descoberto em DEV-1750 (memória `reference_uptime_kuma_prod.md` foi corrigida).

2. **`--network host` obrigatório na VPS Dev:** sem Coolify network, agent precisa bind direto na `tailscale0`. Master usa network `coolify` (mesma que o Hub) — comportamento diferente.

3. **Traefik + PocketBase double auth:** header `Authorization` conflita. Setup automation SEMPRE via SSH Master + IP interno; setup humano via UI (browser separa cookie vs header).

4. **`user_settings.settings` é JSON livre no PocketBase:** aceita qualquer schema, mas o backend Beszel só lê 1 chave específica não documentada. Setup de webhook via UI, não via API (bloqueio confirmado em DEV-1752).

5. **Cascade delete de system apaga alerts:** se recriar system, precisa recriar alerts. Verificar antes de deletar system de produção.

6. **Constraint UNIQUE `(user, system, name)` em alerts:** não pode ter 2 alerts iguais pro mesmo system. Se recriar system, UPDATE alerts existentes (PATCH) em vez de POST.

7. **Beszel test_notification bug (Kuma-like):** ainda não testado real via botão "Test" — validar via alerta REAL (kill do container, ou `stress-ng` na Master).

---

## Rollback / recovery

**Se Hub parar:**
```bash
ssh master@72.60.4.71 'sudo docker ps | grep beszel'   # ver se container up
# Coolify UI → app "Beszel Hub" → Restart
```

Data persistido em `/opt/observability/beszel/data` (bind mount) — restart não perde nada.

**Se restaurar de backup:** substituir `/opt/observability/beszel/data/data.db` (SQLite PocketBase) pelo backup + restart container. Retenção: histórico curto (30d), foco é "estado atual", não análise longa.

**Se agent parar:** Beszel Hub marca system como `down` → alerta Status dispara. Restart:
- Linux Docker: `docker restart beszel-agent-master`
- Windows NSSM: `nssm restart beszel-agent`

---

## Skills operacionais (times/infra/skills/)

Criadas 2026-08-11 pra reduzir cliques manuais na UI:

| Skill | Escopo | Subcomandos |
|---|---|---|
| **`/observability-status`** | Read-only overview instantâneo | (sem args — imprime Kuma+Beszel+alerts triggered) |
| **`/beszel-manage`** | CRUD systems + alerts + install agent | `system add/remove/list` · `alert add/remove/list` · `user reset-password` · `agent-install --os linux\|windows` |
| **`/kuma-maintenance`** | CRUD monitores + manutenção | `add` · `remove` · `list` · `maintenance --start\|--end` · `test-notification` |

**Padrão comum:** todas rodam via `ssh master@72.60.4.71` + API interna (bypass Traefik) + credenciais via `op` 1P no runtime.

Doc completa: `times/infra/skills/*/SKILL.md`.

---

## Refs

- `foundation/monitoring-stack.md` — visão geral (Grafana + Kuma + Beszel)
- `foundation/uptime-kuma.md` — complementar visual (endpoints)
- Memory Stamper: `reference_uptime_kuma_prod.md` (URL corrigida) + `reference_coolify_api_gotchas.md`
- Coolify app UUID: `p357h20lk9ssr8cm5cbs0r6f`
- Incident baseline (a criar em S3.6): `incidents/2026-08-11_camada-visual-observabilidade.md`
