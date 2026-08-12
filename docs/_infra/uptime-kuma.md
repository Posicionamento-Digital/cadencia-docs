# Uptime Kuma — camada visual de status/monitoring da Cadencia

> **URL:** `https://status.cadencia.ia.br` · **Deploy:** Coolify VPS Master · **Status:** produção desde 2026-08-10
>
> Complementa o Grafana Cloud (investigação profunda de séries temporais) com camada visual "abre e vê tudo verde em <10s" — foco em endpoints externos (HTTP/TCP/DNS/cert) + saúde de infra.

---

## Identidade

| Campo | Valor |
|---|---|
| Tipo | Serviço observabilidade (monitoring visual) |
| Stack | Node.js 18.20 + SQLite + Socket.IO (upstream) |
| Imagem Docker | `louislam/uptime-kuma:1` (tag major pinada, nunca `latest`) |
| Path no host | `/opt/observability/uptime-kuma/data` (bind mount → `/app/data`) |
| Porta interna | 3001 |
| Rede Docker | `coolify` (10.0.1.0/24) |
| Restart policy | `unless-stopped` |
| Status | Ativo em produção desde 2026-08-10 (Epic DEV-1739) |
| Coolify app UUID | `ezo1lljuy1907ucabh51cu0p` |
| Coolify project | Cadencia (`wbaqjeeyabmiy0gylk8ywutf`) |
| Coolify server | VPS Master (`f47nciccwtfzez16d4hlulhy`, 72.60.4.71) |

---

## Por que existe

O stack existente (Grafana Cloud + Alloy + Loki + webhook v2) é ótimo pra **investigação profunda** e **alerta automático em background** — mas exige abrir Grafana + entender PromQL + navegar dashboards custom. Felipe **não abre** Grafana no dia a dia.

Faltava a camada de **verificação humana rápida**: abrir uma URL, ver 15 checks verdes ou identificar o que caiu em <10s. Cliente reclamando = sintoma tardio. Kuma preenche esse gap.

**Não substitui Grafana** — complementa:
- **Grafana** = investigação profunda (correlação log↔métrica, séries históricas, alertas com contexto rico)
- **Kuma** = verificação diária ("tá tudo verde?") + alerta simples (canal único WhatsApp)

---

## Arquitetura

```
Browser Felipe (celular/notebook)
      │ HTTPS + Basic Auth
      ▼
Cloudflare DNS (status.cadencia.ia.br A → 72.60.4.71, proxied=false)
      │
      ▼
VPS Master (Hostinger, IP público 72.60.4.71)
      │ :443
      ▼
coolify-proxy (Traefik)
      │  ├─ TLS Let's Encrypt (cert automático)
      │  └─ Middleware `observability-auth` (Basic Auth bcrypt)
      ▼
container uptime-kuma (network `coolify`, IP interno dinâmico 10.0.1.X:3001)
      │
      ├─► SQLite (/app/data/kuma.db) — persistência bind mount
      │
      ├─► 17 monitores HTTP/TCP/DNS
      │       │
      │       ├─► HTTP: cadencia.app.br, docs.*, masterboard.*, portal.cadencia.ia.br, ...
      │       ├─► TCP: SSH ports Master/Dev/CAIXA1 via Tailscale
      │       └─► DNS: cadencia.app.br A record
      │
      ├─► 1 cert monitor (Certificate Expiry cadencia.app.br, alertas 30/14/7d)
      │
      └─► Notification (webhook)
              ▼
        Evo API (https://evo.cadencia.ia.br/send/text)
              │ apikey header + JSON body
              ▼
        WhatsApp comercial (5511914956996)
```

**Detalhes chave:**
- Bind mount **fora do OneDrive** (`/opt/observability/` na VPS Master, `chown 1000:1000`)
- Basic Auth Traefik na frente (dupla proteção junto com login nativo do Kuma)
- Notification via webhook nativo do Kuma (sem intermediário Python)
- Retention 90 dias (padrão Kuma é 180 — reduzido pra economizar SQLite)

---

## 37 monitores em 8 grupos (estado 2026-08-11 — pós-reorg)

**Mudanças recentes (2026-08-11):**
- ❌ Deletado monitor 28 `Traefik dashboard (interna)` — DOWN por design (porta 8080 fechada), travava grupo "Produção Cadencia" em 0% uptime. Fix: usar Coolify UI → Server → Proxy → View Traefik Dashboard pra acessar dashboard sob demanda.
- ✅ Grupo **Vercel Prod** criado (id 52) — 5 endpoints Vercel-served consolidados
- ✅ Grupo **Blogs Clientes** criado (id 53) — 5 blogs com custom domain

### Grupos ativos

### Produção Cadencia (14)
Prod externa (Vercel/Filebrowser):
- `cadencia.app.br` · `docs.cadencia.app.br` · `masterboard.cadencia.app.br` · `cloud.cadencia.app.br` (Filebrowser CAIXA1, aceita 403 UP)

Prod interna (roteada via **Traefik interno `10.0.1.3:443` + header `Host:` — bypass hairpin NAT**, ver §Hairpin Fix):
- `workers.cadencia.ia.br` · `metrics.cadencia.ia.br` (Beszel Hub `/api/health`) · `status.cadencia.ia.br` (Kuma self) · `lara-api.cadencia.ia.br` · `evo.cadencia.ia.br` · `sentry-bridge.cadencia.app.br` · `onboarding.cadencia.ia.br`

VPS Dev via **Tailscale MagicDNS** (porta pública firewall'd Hostinger):
- `Cadencia Agenda (VPS Dev)` — `vps-dev.taild6079b.ts.net:8085`
- `Lara API (VPS Dev)` — `vps-dev.taild6079b.ts.net:8095`

### Supabase (1)
- `Supabase Cadencia prod` — `elefbabxkaigusjiiflu.supabase.co/rest/v1/` (aceita 401 UP)

### Clientes e Infra (10)
- `portal.cadencia.ia.br` (PD Portal) · `cadencia.ia.br` (institucional) · `lara.cadencia.ia.br /health` (Sorria Goiás — DOWN [DEV-1760](https://linear.app/cadencia/issue/DEV-1760))
- Blogs clientes ativos (5, custom domain `*.cadencia.app.br`): `atelier-sweet-angels` · `angelica-zolddan-passos` · `ana-giglio` · `ai-studio` · `ariane-farrapo-consultoria-imo`
- `Coolify admin UI (interna)` — `http://10.0.1.6:8080`
- `Traefik dashboard (interna)` — `http://10.0.1.3:8080` (DOWN — porta interna fechada por design)

### Infra TCP (7)
SSH (5):
- `VPS Master SSH` (72.60.4.71:22) · `VPS Dev SSH` (2.24.117.172:22)
- SSH via Tailscale: `CAIXA1` · `Dell` · `Galaxybook`

Agents Beszel via Tailscale porta 45876 (3):
- `Beszel Agent vps-dev` · `caixa1` · `dell-notebook` — cobre gap do Beszel v0.14 que não notifica quando agent morre

### APIs Externas (5)
- `Stripe API` — v1/charges (aceita 401)
- `Cloudflare API` — tokens/verify (aceita 400)
- `Vercel status` — `www.vercel-status.com/api/v2/status.json` (SaaS crítico proxy Vercel)
- `Resend API` — email transacional (Cadencia envio cliente)
- `OpenRouter status page` — IA usada pra geração conteúdo

### DNS e Cert (2)
- `DNS cadencia.app.br` — A record via 1.1.1.1
- `Cert TLS cadencia.app.br` — expiryNotification 30/14/7d

**Thresholds uniformes (RFC D2):** interval 60s, timeout 20s, 3 retries, notification delay 2min.
**Todos com notification Evo→WhatsApp comercial (`isDefault=True`) aplicada** — se qualquer monitor DOWN, WhatsApp em <60s.

---

## Hairpin NAT fix (endpoints internos `*.cadencia.ia.br`)

**Bug descoberto 2026-08-11:** container Kuma na rede `coolify` NÃO alcança IP público do próprio Master (hairpin NAT falha silenciosa). Tentativa em `https://workers.cadencia.ia.br` → **timeout 48s**.

**Fix aplicado:** monitores dos 7 endpoints internos apontam pro **Traefik interno `10.0.1.3:443`** com:
- Header `Host: <hostname>` — Traefik roteia pelo virtualhost
- `ignoreTls=true` — cert é do hostname, não do IP
- `accepted_statuscodes` ajustado por endpoint (200-405 conforme raiz da app)

**Trade-off:** monitor não valida cadeia TLS externa. Se cert Let's Encrypt não renovar, monitor **não detecta** — cobertura via monitor 23 `Cert TLS cadencia.app.br`.

**Cobertura funcional:** se Traefik cair OU container-alvo cair OU rota Traefik quebrar → alerta.

Exemplo edit_monitor via lib:
```python
api.edit_monitor(
    id_=31, url="https://10.0.1.3/api/health",
    headers=json.dumps({"Host": "metrics.cadencia.ia.br"}),
    ignoreTls=True, accepted_statuscodes=["200"]
)
```

---

## Deploy (procedimento canônico via API Coolify)

**Pré-requisitos:**
- Cloudflare DNS record A → 72.60.4.71 (proxied=false pra Let's Encrypt funcionar)
- Bind mount preparado no host: `sudo mkdir -p /opt/observability/uptime-kuma/data && sudo chown -R 1000:1000 /opt/observability/uptime-kuma/data`

### 1. Criar app via API Coolify

```bash
COOLIFY_TOKEN=$(op item get "Coolify - API - VPS Master" --vault "Hosts" --fields password --reveal)

cat > /tmp/kuma_payload.json <<'EOF'
{
  "server_uuid": "f47nciccwtfzez16d4hlulhy",
  "project_uuid": "wbaqjeeyabmiy0gylk8ywutf",
  "environment_name": "production",
  "docker_registry_image_name": "louislam/uptime-kuma",
  "docker_registry_image_tag": "1",
  "ports_exposes": "3001",
  "domains": "https://status.cadencia.ia.br",
  "name": "uptime-kuma",
  "description": "Uptime monitoring - dashboard visual",
  "instant_deploy": false
}
EOF

curl -X POST "https://coolify.cadencia.ia.br/api/v1/applications/dockerimage" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/kuma_payload.json
# → retorna {"uuid":"...", "domains":"..."}
```

### 2. Configurar bind mount (workaround SQL — API /storages tem bug)

```bash
# API POST /storages recusa qualquer 'type' — bug conhecido do endpoint
# Workaround: INSERT direto no BD Coolify
ssh master@72.60.4.71
sudo docker exec coolify-db psql -U coolify -d coolify -c \
  "INSERT INTO local_persistent_volumes
   (name, mount_path, host_path, resource_type, resource_id, uuid, created_at, updated_at, is_preview_suffix_enabled)
   VALUES ('uptime-kuma-data', '/app/data', '/opt/observability/uptime-kuma/data',
           'App\\Models\\Application',
           (SELECT id FROM applications WHERE uuid = 'ezo1lljuy1907ucabh51cu0p'),
           LOWER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 24)),
           NOW(), NOW(), false);"
```

### 3. Adicionar Basic Auth Traefik nas labels

```python
# Requer PATCH com custom_labels em BASE64 (endpoint retorna HTTP 422 se text plain)
# Adicionar ao chain de labels Traefik:
#   traefik.http.middlewares.observability-auth.basicauth.users=<user>:<hash_bcrypt>
#   traefik.http.routers.https-0-<uuid>.middlewares=gzip,observability-auth

# Hash bcrypt via htpasswd (apache2-utils instalado na Master):
echo "<senha>" | ssh master 'read -r PWD; htpasswd -nbB felipe "$PWD"'
```

Ver script completo em `_shared/kuma/patch_labels.py` (a criar quando skill `/kuma-maintenance` for implementada — DEV-1754).

### 4. Deploy

```bash
curl -X POST "https://coolify.cadencia.ia.br/api/v1/deploy?uuid=ezo1lljuy1907ucabh51cu0p&force=true" \
  -H "Authorization: Bearer $COOLIFY_TOKEN"
# → retorna {"deployments":[{"deployment_uuid":"...","status":"queued"}]}
```

### 5. Validar

```bash
curl -sk -I https://status.cadencia.ia.br
# → HTTP/2 302 (redirect login Kuma, cert Let's Encrypt válido)

# Sem cred → 401
curl -sk -o /dev/null -w "%{http_code}\n" https://status.cadencia.ia.br
# → 401

# Com cred → 302
SENHA=$(op item get "Traefik Basic Auth - Observability [Cadencia]" --vault "Serviços & Tools" --fields password --reveal)
curl -sk -o /dev/null -w "%{http_code}\n" -u "felipe:$SENHA" https://status.cadencia.ia.br
# → 302
```

---

## Configuração inicial (setup admin + monitors + notification)

**Todas as operações via lib Python `uptime-kuma-api` v1.2.1** (Kuma API é Socket.IO, não REST puro — REST direto quebra).

### Instalar lib

```bash
# Na Master
sudo pip install --break-system-packages uptime-kuma-api
```

### Setup admin (automatizado — dispensa browser)

```python
import os
from uptime_kuma_api import UptimeKumaApi

# IP interno do container (bypass Basic Auth Traefik)
# Descobrir: docker inspect <container> --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
api = UptimeKumaApi("http://10.0.1.X:3001")

# Primeira chamada — cria admin
api.setup("felipe", "<senha do 1P: Uptime Kuma - Admin [Cadencia]>")
```

### Cadastrar monitores

```python
from uptime_kuma_api import MonitorType

api.login("felipe", senha)

# Criar grupo
grupo = api.add_monitor(type=MonitorType.GROUP, name="Produção Cadencia")

# HTTP com accept status codes custom
api.add_monitor(
    type=MonitorType.HTTP,
    name="cadencia.app.br",
    url="https://cadencia.app.br",
    parent=grupo["monitorID"],
    interval=60, retryInterval=60, maxretries=3, timeout=20,
    accepted_statuscodes=["200-299"],
)

# TCP
api.add_monitor(
    type=MonitorType.PORT,
    name="VPS Master SSH",
    hostname="72.60.4.71",
    port=22,
    parent=grupo["monitorID"],
    interval=60, retryInterval=60, maxretries=3, timeout=20,
)

# DNS
api.add_monitor(
    type=MonitorType.DNS,
    name="DNS cadencia.app.br (A record)",
    hostname="cadencia.app.br",
    dns_resolve_server="1.1.1.1",
    dns_resolve_type="A",
    parent=grupo["monitorID"],
)

# Cert Expiry — é HTTP com expiryNotification=True
api.add_monitor(
    type=MonitorType.HTTP,
    name="Cert TLS cadencia.app.br (30/14/7d)",
    url="https://cadencia.app.br",
    parent=grupo["monitorID"],
    interval=3600,  # 1h — cert não muda no minuto
    expiryNotification=True,
    accepted_statuscodes=["200-299", "300-399"],
)
```

### Configurar notification Evo WhatsApp

```python
from uptime_kuma_api import NotificationType
import json

api.add_notification(
    name="Evo WhatsApp Felipe (comercial)",
    type=NotificationType.WEBHOOK,
    isDefault=True,          # aplica automático a monitores futuros
    applyExisting=True,      # aplica retroativamente aos existentes
    webhookURL="https://evo.cadencia.ia.br/send/text",
    webhookContentType="application/json",
    webhookAdditionalHeaders=json.dumps({"apikey": "<token do 1P: EVO - API - Num comercial>"}),
    webhookCustomBody=json.dumps({
        "number": "5511914956996",
        "text": "🚨 [KUMA] {{monitorJSON.name}} — {{status}}\n\n{{msg}}\n\n{{monitorJSON.url}}\n\nhttps://status.cadencia.ia.br"
    }),
)
```

### Retention

```python
api.set_settings(keepDataPeriodDays=90)  # default é 180 — sempre setar explícito
# Verificar após docker restart pra confirmar que persistiu
```

---

## Operação day-to-day

### Adicionar novo monitor

Via lib Python (script em `/tmp/add_monitor.py` na Master), ou UI web em `https://status.cadencia.ia.br` (Add New Monitor).

**Regra:** todo monitor novo herda automaticamente notification Evo WhatsApp (via `isDefault=True` no provider — não precisa aplicar manual).

### Remover monitor

```python
api.delete_monitor(monitor_id)
```

Confirmação textual **obrigatória** antes de rodar (operação destrutiva).

### Pausar/despausar

```python
api.pause_monitor(monitor_id)   # não gera alerta
api.resume_monitor(monitor_id)
```

Útil pra deploys planejados que sabidamente vão fazer serviço ficar DOWN por alguns minutos.

### Ver status agregado

```python
monitors = api.get_monitors()
heartbeats = api.get_heartbeats()
# Somar UP/DOWN/PENDING por status.
```

### Reset senha admin (se perder)

**Rota 1 — API (senha atual conhecida):**
```python
api.change_password(current="<antiga>", new="<nova>")
```

**Rota 2 — SQLite direto (senha atual perdida — validado 2026-08-11):**

```bash
# 1. Gerar hash bcrypt localmente (bcryptjs = $2b$ 10 rounds)
python3 -c "import bcrypt; print(bcrypt.hashpw(b'<nova-senha>', bcrypt.gensalt(rounds=10, prefix=b'2b')).decode())"

# 2. Escrever hash em arquivo (evita interpolação shell de $2b$)
echo -n '$2b$10$...' > /tmp/kuma_hash.txt
scp -O -i ~/.ssh/hostinger_prod_master /tmp/kuma_hash.txt master@72.60.4.71:/tmp/

# 3. Aplicar via SQLite + copy DB de volta + restart
ssh master@72.60.4.71 '
HASH=$(cat /tmp/kuma_hash.txt)
CID=$(sudo docker ps -q -f ancestor=louislam/uptime-kuma:1)
sudo docker cp $CID:/app/data/kuma.db /tmp/kuma.db
sudo sqlite3 /tmp/kuma.db "UPDATE user SET password = \"$HASH\", twofa_status = 0 WHERE username=\"felipe\";"
sudo docker cp /tmp/kuma.db $CID:/app/data/kuma.db
sudo docker restart $CID
'
```

**Gotchas do reset:**
- **Sem escape shell no hash:** use arquivo (`/tmp/kuma_hash.txt`) em vez de variável — bash interpola `$2b`, `$10` como argumentos posicionais e corrompe hash pra `b0`.
- **twofa_status = 0:** reset limpa 2FA junto (senão fica trancado).
- **Cache em memória:** restart do container é obrigatório — Kuma cacheia user.

**Atualizar 1P depois:** item `Uptime Kuma - Admin [Cadencia]` vault `Serviços & Tools` campo `password`.

---

## Rollback / backup

### Rollback deploy (voltar versão anterior)

Coolify guarda últimas N deployments. Via UI: app → Deployments → escolher anterior → Rollback. Via API:

```bash
curl -X POST "https://coolify.cadencia.ia.br/api/v1/deploy?uuid=<APP_UUID>&force=true&tag=<TAG_ANTIGA>" \
  -H "Authorization: Bearer $COOLIFY_TOKEN"
```

### Parar sem perder dados

```bash
sudo docker stop $(docker ps --filter "name=ezo1" --format "{{.Names}}")
# Bind mount preservado. Reiniciar: sudo docker start <name>
```

### Backup SQLite

Bind mount `/opt/observability/uptime-kuma/data/kuma.db` deve estar em `run-all-backups.ps1` da CAIXA1 (ainda pendente — [DEV-1756 S3.4](https://linear.app/cadencia/issue/DEV-1756)). Enquanto não implementa, backup manual:

```bash
ssh master@72.60.4.71 'sudo cp /opt/observability/uptime-kuma/data/kuma.db /tmp/kuma-backup-$(date -u +%Y%m%dT%H%M%S).db'
scp master:/tmp/kuma-backup-*.db /local/backup/
```

### Restore

```bash
sudo docker stop <kuma-container>
sudo cp /caminho/backup/kuma-backup-YYYYMMDD.db /opt/observability/uptime-kuma/data/kuma.db
sudo chown 1000:1000 /opt/observability/uptime-kuma/data/kuma.db
sudo docker start <kuma-container>
```

---

## Acesso SSH bypass Basic Auth (pra automação)

Automação via lib Python precisa conectar **por dentro** (IP interno Docker) — Basic Auth Traefik trava conexão externa via lib.

```bash
ssh master@72.60.4.71
CONTAINER=$(docker ps --filter "name=ezo1" --format "{{.Names}}")
IP=$(docker inspect "$CONTAINER" --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}")
echo "http://$IP:3001"
```

**IP muda em cada restart** — script Python precisa reler `docker inspect` antes de conectar.

---

## Gotchas conhecidos

### 1. Coolify PATCH `custom_labels` exige base64
Retorna HTTP 422 se enviar texto plain (mensagem: `"The custom_labels should be base64 encoded."`). Padronizar `base64.b64encode(labels_text.encode()).decode()` em qualquer PATCH.

### 2. Coolify API `/storages` recusa qualquer valor de `type`
Bug conhecido do endpoint atual do Coolify. Workaround: `INSERT` direto no `local_persistent_volumes` do container `coolify-db` (procedimento acima).

### 3. Kuma API é Socket.IO, não REST puro
Endpoints REST diretos quebram com 404 ou não fazem o esperado. **Sempre usar lib `uptime-kuma-api`** (v1.2.1+) que abstrai a camada Socket.IO. Documentação da lib: https://uptime-kuma-api.readthedocs.io/

### 4. `test_notification()` da API envia body vazio
Bug conhecido — o botão "Test" do Kuma via API não interpola Mustache. Retorna `phone number is required` no webhook Evo. **Validação de notification só funciona com monitor sintético DOWN real** (criar monitor apontando `http://127.0.0.1:19999` → fica DOWN → dispara alerta).

### 5. `applyExisting=True` aplica notification retroativamente
Ao criar notification via `add_notification(applyExisting=True)`, todos os monitores existentes recebem a notification automaticamente. **Não precisa iterar `edit_monitor`** — evita 17+ requests desnecessários.

### 6. Container Coolify → domínio próprio = loopback Traefik
Se um container na network `coolify` tenta acessar um domínio público servido por Traefik da **mesma máquina**, o request faz loop no proxy e trava (timeout). Exemplo real: monitor `workers.cadencia.ia.br /health` timeouted mesmo com endpoint respondendo 200 externo. **Fix:** apontar monitor pro **IP interno Docker** (10.0.1.x) do container alvo, não pro domínio público.

### 7. Wildcard DNS `*.cadencia.app.br` mascara ausência de projeto Vercel
Cloudflare tem CNAME `*.cadencia.app.br → cname.vercel-dns.com`. Se você monitora `app.cadencia.app.br` mas o projeto Vercel só tem `cadencia.app.br` (root) cadastrado, Vercel Edge **aborta TLS silenciosamente** (comportamento anti-probing). Erro típico: `openssl: unexpected eof while reading`. **Sempre verificar `vercel domains ls` antes de adicionar subdomínio Cadencia como monitor.** Detalhado em [DEV-1759](https://linear.app/cadencia/issue/DEV-1759).

### 8. Cloudflared tunnel config vive **remoto** (Zero Trust Dashboard)
`/etc/cloudflared/tunnel.token` só autentica — ingress rules ficam no dashboard CF. Editar via API exige token com scope `Account:Cloudflare Tunnel:Edit` (o token `cfut_...` do 1P só tem `Zone.DNS:Edit`). Ou editar via UI em `one.dash.cloudflare.com → Networks → Tunnels`. Ver [DEV-1760](https://linear.app/cadencia/issue/DEV-1760).

### 9. Endpoint Evo é `/send/text` (não `/message/sendText/{instance}`)
O servidor `evo.cadencia.ia.br` é Evolution/WuzAPI simplificado. Path do Evolution GO padrão retorna 404. Corretos:
- Enviar texto: `POST https://evo.cadencia.ia.br/send/text` — body `{"number":"...", "text":"..."}`
- Enviar mídia: `POST /send/media`
- Header auth: `apikey: <token da instância>`

### 10. `webhookAdditionalHeaders` aceita JSON string com headers custom
Não é um dict Python — precisa ser **string** JSON serializada:
```python
webhookAdditionalHeaders=json.dumps({"apikey": token, "X-Custom": "value"})
```

---

## Riscos residuais + monitoramento

| Risco | Mitigação |
|---|---|
| Kuma cai → sem alertas | Grafana Cloud vigia via `up{job="uptime-kuma"}` — pendente configurar ([DEV-1757](https://linear.app/cadencia/issue/DEV-1757)) |
| Basic Auth Traefik trava mobile | Se atrapalhar, remover basic + manter só login app |
| SQLite corrompe | Backup diário CAIXA1 restic ([DEV-1756](https://linear.app/cadencia/issue/DEV-1756)) — pendente implementar |
| Falso positivo flap | 3 retries × 60s + delay 2min já mitigado. Se >30% dos alertas em semana 1 forem flap, aumentar retries pra 5 |
| Rotação senha Basic Auth | Rotação semestral documentada aqui + item 1P atualizado |
| Ingress lara.cadencia.ia.br | Aguarda ação Felipe ([DEV-1760](https://linear.app/cadencia/issue/DEV-1760)) |
| Kuma container → HTTPS Vercel | Documentado ([DEV-1759](https://linear.app/cadencia/issue/DEV-1759)); usar IP interno pra monitorar serviços na Master |

---

## Follow-ups em aberto (rastreados no Linear)

- **[DEV-1755 S3.3](https://linear.app/cadencia/issue/DEV-1755)** — skill `/check-servicos` (opcional, timebox 4h)
- **[DEV-1754 S3.2](https://linear.app/cadencia/issue/DEV-1754)** — skill `/kuma-maintenance` (add/remove/list/test-notification/maintenance-window)
- **[DEV-1756 S3.4](https://linear.app/cadencia/issue/DEV-1756)** — backup `kuma.db` no CAIXA1 restic
- **[DEV-1757 S3.5](https://linear.app/cadencia/issue/DEV-1757)** — Grafana Cloud alert rule `up{job="uptime-kuma"}` → alerta P1 se Kuma cair
- **[DEV-1760](https://linear.app/cadencia/issue/DEV-1760)** — Cloudflared ingress `lara.cadencia.ia.br` (bloqueio humano — precisa acesso CF Zero Trust dashboard)
- **[DEV-1759](https://linear.app/cadencia/issue/DEV-1759)** ✅ Done — investigação TLS Kuma→Vercel resolvida (RFC assumiu domínios errados)

---

## Credenciais (1Password)

| Item | Vault | Uso |
|---|---|---|
| `Uptime Kuma - Admin [Cadencia]` | `Serviços & Tools` | Login UI Kuma (user `felipe`) |
| `Traefik Basic Auth - Observability [Cadencia]` | `Serviços & Tools` | Basic Auth Traefik (username + password + hash bcrypt) |
| `EVO - API - Num comercial` | `E-mails` | Token API Evo (apikey header no webhook) |
| `Coolify - API - VPS Master` | `Hosts` | Deploy/PATCH via API Coolify |
| `Cloudflare - API Token + Zones` | `Hosts` | DNS record management (scope Zone.DNS:Edit) |

---

## Referências

- Repo Uptime Kuma: https://github.com/louislam/uptime-kuma
- Lib Python: https://uptime-kuma-api.readthedocs.io/
- Epic pai: [DEV-1739](https://linear.app/cadencia/issue/DEV-1739)
- Brief: [Linear Doc](https://linear.app/cadencia/document/brief-camada-visual-uptime-kuma-beszel-dd276ef754a2)
- PRD: [Linear Doc](https://linear.app/cadencia/document/prd-camada-visual-uptime-kuma-beszel-26453ff5f3ea)
- RFC: [Linear Doc](https://linear.app/cadencia/document/rfc-camada-visual-arquitetura-uptime-kuma-beszel-89aba2c45f07)
- Doc irmã (monitoring geral): `times/infra/foundation/monitoring-stack.md`
- Próximo componente da mesma stack: Beszel Hub (Epic [DEV-1740](https://linear.app/cadencia/issue/DEV-1740) — a implementar)

---

*Documento gerado por `/documentar-software` em 2026-08-11. Fonte de verdade: este arquivo (framework agents). Cópias sincronizadas em `cadencia-docs/docs/_infra/uptime-kuma.md` (humanos via docs.cadencia.app.br) e Obsidian `Projetos/Cadencia/Docs/uptime-kuma.md` (consulta Felipe).*
