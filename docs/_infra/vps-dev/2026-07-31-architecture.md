# VPS Dev — arquitetura

> Diagrama C4 mermaid + fluxo real de tráfego. Fonte: `docker inspect`, `docker network inspect`, config do `cloudflared` extraído dos logs do systemd.

## C4 nível container

```mermaid
graph TB
  subgraph internet["Internet"]
    tenants["Sorria Goiás<br/>(3 tenants WhatsApp)"]
    scanners["Scanners diversos<br/>(portas 8085 públicas)"]
    felipe_client["Felipe (SSH)"]
  end

  subgraph cf["Cloudflare"]
    dns["DNS + Proxy<br/>lara/queue/ecuro/ue/testes<br/>.cadencia.ia.br"]
  end

  subgraph vps["VPS Dev — 2.24.117.172 (Ubuntu 24.04)"]
    sshd["sshd (:22)<br/>UFW policy DROP<br/>allow 22/tcp"]
    cloudflared["cloudflared.service<br/>tunnel 09c0b304-*<br/>5 hostnames configurados"]
    dockerd["Docker daemon<br/>+ containerd"]

    subgraph lara_stack["Stack Lara GCI-GO<br/>(network: lara-internal + pd-shared)"]
      lara_api["lara-api :8090→:8095<br/>FastAPI uvicorn<br/>PUBLIC_BASE_URL=lara.cadencia.ia.br"]
      lara_worker["lara-worker<br/>Redis Streams + agent"]
      lara_pg[("lara-postgres<br/>pgvector/pg16<br/>vol: lara-postgres-data")]
      lara_redis[("lara-redis<br/>redis:7-alpine<br/>vol: lara-redis-data")]
    end

    subgraph agenda_stack["Stack Cadencia Agenda<br/>(network: cadencia-agenda-network)"]
      agenda_app["cadencia-agenda-app :80→:8085<br/>alextselegidis/easyappointments<br/>Apache+PHP 8.2"]
      agenda_mysql[("cadencia-agenda-mysql<br/>mysql:8.0<br/>vol: cadencia-agenda-mysql-data")]
    end

    subgraph motor_stack["Stack PD Motor<br/>(network: pd-motor_default)"]
      motor["pd-motor<br/>--cpus=1 --memory=2g<br/>MOTOR_IDLE_SLEEP=300s<br/>sobe OFF (kill switch)"]
      motor_claude[/"/home/felipe/.motor/claude<br/>bind mount RW"/]
      motor_codex[/"/home/felipe/.motor/codex<br/>bind mount RW"/]
    end

    ghost_ecuro[/"❌ ecuro-middleware<br/>NÃO EXISTE (env aponta pra hostname)"/]
    ghost_queue[/"❌ confirmation-queue-api<br/>NÃO EXISTE (env aponta pra hostname)"/]

    subgraph cron_felipe["Cron user felipe"]
      autofix["cadencia-autofix (15min)"]
      health_dev["health-dev (10min)"]
      pos_briefing["pos-briefing (5*/h 8-22h)"]
      motor_notify["motor-notify (10min)"]
      stale_reaper["stale-claim-reaper (hourly)"]
      sync_docs["sync-dev-docs (23h)"]
    end

    subgraph cron_root["Cron user root"]
      daily_brief["daily-brief (11h+21h30)"]
      luiz_state_orphan["⚠️ luiz-state (21h40)<br/>ÓRFÃO — user Luiz inerte"]
    end

    subgraph systemd_custom["Systemd custom"]
      pd_syslog["⚠️ pd-syslog.service<br/>--users luiz<br/>vai errar agora"]
    end
  end

  tenants -->|"HTTPS webhook Evolution GO<br/>(hospedado em outro lugar)"| dns
  dns -->|lara.cadencia.ia.br| cloudflared
  cloudflared -->|:8095| lara_api

  scanners -->|":8085 GET / direto"| agenda_app

  felipe_client -->|ssh| sshd

  lara_api --> lara_pg
  lara_api --> lara_redis
  lara_worker --> lara_pg
  lara_worker --> lara_redis
  lara_api -.->|"docker DNS falha"| ghost_ecuro
  lara_worker -.->|"docker DNS falha"| ghost_queue

  agenda_app --> agenda_mysql

  motor --> motor_claude
  motor --> motor_codex
  motor -->|"git clone + gh + linear<br/>(saída only)"| dns

  cron_felipe -.->|logs| dockerd
  cron_root -.->|logs| dockerd

  classDef ghost fill:#ffe0e0,stroke:#c00,color:#900,stroke-dasharray:5
  classDef orphan fill:#fff5cc,stroke:#a80
  classDef critical fill:#d0f0d0,stroke:#080
  class ghost_ecuro,ghost_queue ghost
  class luiz_state_orphan,pd_syslog orphan
  class cloudflared,lara_api critical
```

## Fluxos reais confirmados

### 1. Webhook WhatsApp → Lara GCI-GO (produção viva, cliente encerrado)

```
[tenant Sorria Goiás] → Evolution GO externo (hospedado em outro provedor —
                                                                não é essa VPS)
                     → HTTPS lara.cadencia.ia.br (Cloudflare DNS)
                     → cloudflared tunnel (VPS Dev)
                     → 127.0.0.1:8095
                     → docker-proxy → lara-api:8090
                     → FastAPI processa webhook
                     → enfileira em lara-redis
                     → lara-worker consome, roda agent (OpenRouter gpt-5.4-mini)
                     → tenta chamar ecuro-middleware (FALHA — container sumiu)
                     → tenta chamar confirmation-queue-api (FALHA — sumiu)
                     → grava mensagem em lara-postgres (pgvector)
                     → reconcile.tenant_done nos logs
```

**Modo degradado:** reconcile continua (leitura de mensagens), mas cadeia completa de agendamento via Ecuro API dental está quebrada. A stack processa 3 tenants: `sorria-goias-plano-piloto` (0964f213-*), `sorria-goias-ceilandia` (596f3659-*), `sorria-goias-central` (82bc379f-*). Nenhum existe no Supabase Cadencia — são tenants isolados no Postgres local da Lara (`lara-postgres` volume).

### 2. Motor Autônomo (framework)

```
felipe (SSH) → docker compose start / motor.py on
             → pd-motor sobe worker loop
             → clona pd-framework em /home/motor/pd-framework
             → Claude Code + Codex via CLI (auth em .motor/claude|codex mounts)
             → poll Linear (own:motor issues)
             → git clone + worktree + turnos
             → commit + push pra branch feat/dev-<N>
             → gh pr create
             → devolve o claim ao pool
```

**Estado atual:** subiu OFF por default no reboot (fail-safe do kill switch soberano `motor.py`). Precisa `motor.py on` manual pra trabalhar.

### 3. Cadencia Agenda (Easy!Appointments — POC abandonado)

Endpoint `:8085` recebe GETs de scanners internet (logs mostram User-Agent `Mozilla/5.0 (X11; Ubuntu)`, `Chrome/49`, etc — bots) + acessos legítimos ocasionais. Sem rota `cadencia.ia.br` no Cloudflare tunnel pra ele (não está exposto pelo tunnel).

Provavelmente Luiz deixou porta 8085 aberta pra testar contra tenants Cadencia (DEV-1364 previa Easy!Appointments como provider). **Não é usado por nenhum cliente hoje** (nenhum tenant Cadencia tem esse provider configurado).

### 4. Cron autofix + motor-notify + stale-reaper (framework pd-framework)

Rodam local em `/home/felipe/pd-framework/`, não expõem porta. Interagem com Linear + Motor via CLI. Escrevem em `.pd/*.log`.

## Fluxo de gerência (SSH)

```
felipe local (chave hostinger_dev_felipe)
  → sshd :22
  → grupo felipe (uid 1000) + sudo NOPASSWD
    → docker ps / logs / exec (sudo)
    → journalctl -u cloudflared / pd-syslog
    → crontab -u felipe/-u root
    → /opt/{daily-brief,sync-dev-docs.py}
    → /home/felipe/pd-framework/ (clone do framework)
```

## Componentes que NÃO existem mais (referências mortas no config)

- `ecuro-middleware` (container esperado pelo Lara worker via docker DNS `http://ecuro-middleware:8080`) — sumiu. Env `ECURO_MIDDLEWARE_URL` no `lara-worker` aponta pra hostname que não resolve.
- `confirmation-queue-api` (container esperado pelo Lara worker via `http://confirmation-queue-api:3000`) — sumiu.
- `ue.cadencia.ia.br` (Vite dev :5173) — abandonado.
- `testes.cadencia.ia.br` (localhost :3000) — abandonado.
- `queue.cadencia.ia.br` (:3000) — apontava pra `confirmation-queue-api`; endpoint ativo no Cloudflare mas sem serviço atrás.

**Efeito:** requisições nesses hostnames Cloudflare voltam 5xx/timeout. Não afeta operação atual (nada crítico depende deles).

## Decisões arquiteturais implícitas (não formalizadas em ADR)

- **Cloudflare Tunnel > port forward direto** — VPS Hostinger tem UFW default DROP; tunnel é a única entrada externa. Vantagem: HTTPS grátis, DDoS protection Cloudflare, esconde IP.
- **Sem Coolify na VPS Dev** — só a Master usa. Aqui é `docker compose` manual, o que gera o problema dos compose files sumindo.
- **User luiz + docker group = root efetivo** — enquanto ativo, Luiz podia `docker run -v /:/host` e ler qualquer arquivo. Vetor conhecido, autorizado enquanto era dev interno. Após desligamento, `gpasswd -d luiz docker`.
- **Motor com cap `--cpus=1 --memory=2g`** — decisão explícita em `_core/deploy/motor/compose.yml` pra não competir com o dev interativo do Felipe na mesma VPS.
