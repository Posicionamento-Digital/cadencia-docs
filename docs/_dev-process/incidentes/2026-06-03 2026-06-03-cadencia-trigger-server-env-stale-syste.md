---
type: source
source_kind: incidente
date: 2026-06-03
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-06-03_cadencia-trigger-server-env-stale-systemd

# Incidente: trigger_server.py daemon rodando 4 dias com env stale — todo tenant novo falhava 403 GHL create_location silenciosamente

**Data:** 03/06/2026
**Severidade:** Alta
**Projeto:** Cadência
**Duração do impacto:** ~20h (02/06 23:40 → 03/06 19:30)
**Tags:** `#backend` `#ghl` `#provisioning` `#env-stale` `#daemon` `#systemd` `#silenciosa` `#regressao`

## O que aconteceu

Durante o onboarding do tenant Marinella/Grupo WGL (`73779837-93ee-4693-9b3e-9a5ae75a4875`) em 03/06 18:07, o provisionamento da subconta GHL falhou silenciosamente com `provisioning_status="partial"` — mesmo erro do incident 02/06 (GHL_COMPANY_ID errado → 403 Forbidden), apesar do fix daquele incident já estar aplicado há ~18h.

Investigação revelou um segundo tenant afetado na mesma janela: **Mel Quevedo / Horus Marcas e Patentes** (`1063c105-b096-46cf-b29c-efe657683314`, provisionado 17:54). Bug silencioso — log captura como `WARN` (não `FATAL`), zero alertas, frontend não bloqueia próximas fases do onboarding.

## Causa raiz

Bug estrutural distinto do incident 02/06 (que era `.env` com valor errado em disco). Aqui o `.env` estava correto desde 02/06 23:40, mas **o processo daemon nunca recarregou em memória**.

1. **`trigger_server.py` daemon longo**: iniciado em 30/05 01:26 via `nohup python3 trigger_server.py >> log &` (PID 2164301, uptime 4d 17h 58min). Lê `/cadencia/.env` na inicialização e mantém todas as vars em `os.environ` em memória.

2. **`trigger_server.py:run_script()` line ~30**: invoca scripts filhos via `subprocess.run(cmd, capture_output=True, timeout=timeout)` **sem** parâmetro `env=`. Sem isso, subprocess herda env do parent (o daemon stale).

3. **`provision_tenant.py:55` (env loader)**: lê `.env` com `os.environ.setdefault(k.strip(), v.strip())`. `setdefault()` **não sobrescreve** se a chave já existe — e ela existe (herdada do parent stale). Logo, `provision_tenant.py` LÊ o `.env` corrigido mas **usa o valor antigo** já em memória do parent.

4. **`provision_tenant.py:create_ghl_location()`**: monta `body = {'companyId': os.environ.get('GHL_COMPANY_ID', ''), ...}` = `yXnyB5pagLHLdjEvGpYe` (valor pré-fix). GHL responde 403 "Forbidden resource" porque `GHL_AGENCY_TOKEN` não tem permissão nessa company.

Cadeia: daemon iniciado 30/05 → fix `.env` 02/06 23:40 sem restart → subprocess herda env stale → `setdefault` impede correção → 403 silencioso em todos provisionings desde então.

## Por que não foi detectado

- **Erro silencioso por design**: `provision_tenant.py` trata o 403 como `WARN`, segue com DNS e blog, marca `provisioning_status=partial`. Frontend não bloqueia onboarding nas fases seguintes (PR #7 do 02/06 só validou pré-condições no `trigger-generation`, não nas fases pós-OB).
- **Nenhuma instrumentação de alerta**: 0 webhooks, 0 mensagem Stevo, 0 dashboard de "tenants com partial". Bug só apareceria quando cliente reclamasse de email/scoring não funcionando.
- **Incident 02/06 não checou o uptime do daemon**: o fix testou `curl /locations/` com env do shell SSH (que lê `.env` atualizado), confirmou 201 Created e considerou resolvido — sem verificar se o daemon em memória também tinha o env atualizado.
- **`provision_tenant.py` reportava `Using static GHL_AGENCY_TOKEN (fallback)` mas não logava o `companyId` no payload** — escondeu a evidência decisiva.

## Como foi corrigido

Fix em 4 camadas (todos aplicados 03/06 19:00-19:43):

### 1. Reprovision manual dos 2 tenants afetados

```bash
TRIGGER_SECRET='L9rgVfb...'
curl -s -X POST http://localhost:39090/provision \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"73779837-...","secret":"'$TRIGGER_SECRET'"}'
# Marinella: location_id=O8AQNUoPg9oIa4vle6Fo, status=OK
# Horus:     location_id=mxAthP6SiONbBLB8rhnI, status=OK
```

### 2. Patch em 9 scripts `/cadencia/pipeline/*.py` (sed em massa)

`os.environ.setdefault(k.strip(), v.strip())` → `os.environ[k.strip()] = v.strip()`

Scripts patchados: `provision_tenant.py`, `trigger_server.py`, `seinfeld_generate.py`, `blog_generate.py`, `linkedin_generate.py`, `instagram_generate.py`, `newsletter_generate.py`, `sync_accounts.py`, `backfill_images.py`. Backups `.bak-env-stale-20260603-1942`.

### 3. Systemd unit `cadencia-trigger.service` criada

```ini
[Unit]
Description=Cadencia Growth Trigger Server (on-demand pipeline)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/cadencia/pipeline
EnvironmentFile=/cadencia/.env
ExecStart=/usr/bin/python3 /cadencia/pipeline/trigger_server.py
Restart=always
RestartSec=5
StandardOutput=append:/cadencia/logs/trigger_server.log
StandardError=append:/cadencia/logs/trigger_server.log

[Install]
WantedBy=multi-user.target
```

`EnvironmentFile=/cadencia/.env` força systemd a reler o `.env` em todo restart. `Restart=always` evita downtime se o processo cair. Habilitado via `systemctl enable cadencia-trigger.service`. PID 1125397, smoke test OK.

### 4. Backup pré-mudança

`/cadencia/pipeline/*.py.bak-env-stale-20260603-1942` para rollback rápido se necessário.

## Prevenção

### Checklist / regras pra evitar recorrência

- [ ] Após mudar `/cadencia/.env` em produção: `sudo systemctl restart cadencia-trigger.service` (obrigatório, não opcional)
- [ ] Antes de declarar "fix de `.env` aplicado": `ps -eo etime,cmd | grep <daemon>` e comparar `etime` com timestamp da última mudança no `.env`. Se etime > idade do fix → daemon ainda stale.
- [ ] Daemons Python que dependem de `.env`: SEMPRE rodar via systemd com `EnvironmentFile=`, nunca `nohup ... &` manual.
- [ ] Em qualquer script Python que lê `.env`: usar `os.environ[k] = v`, NUNCA `os.environ.setdefault(k, v)`. setdefault propaga env stale do parent.
- [ ] Adicionar step 6 ao `/validar-deploy-vps`: comparar `mtime` de `.env` vs `etime` de processos dependentes.

### Pattern correto (Python)

```python
# ❌ ERRADO — herda env stale do parent
env_path = Path('/cadencia/.env')
for line in env_path.read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())  # NÃO sobrescreve

# ✅ CERTO — força valor do .env, ignora herança do parent
for line in env_path.read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ[k.strip()] = v.strip()
```

### Pattern correto (subprocess)

```python
# ❌ ERRADO — subprocess herda env do parent (pode estar stale se parent é daemon)
subprocess.run(cmd, capture_output=True)

# ✅ CERTO se precisar isolar — passar env limpo lido do .env
clean_env = dict(os.environ)
# OR: clean_env = {**os.environ, **load_env_from_file('/cadencia/.env')}
subprocess.run(cmd, capture_output=True, env=clean_env)
```

### Gotcha novo

**G019 — Daemon Python lendo `.env` via `setdefault` herda env stale do parent.** `subprocess.run` sem `env=` propaga env do daemon longo-vivo. Mudanças no `.env` em disco não chegam ao processo até restart. Fix: systemd `EnvironmentFile` + `os.environ[k] = v`.

### Regra atualizada em

- [x] `pd-framework/times/produto/cadencia/EXPERTISE.md` — adicionar G019 (pendente)
- [x] `pd-framework/incidents/INDEX.md` (este incident)
- [ ] `/validar-deploy-vps` — adicionar step de mtime check (sugerido)

## Commits relacionados

- VPS `/cadencia/pipeline/` — 9 arquivos patchados via `sed`, backups `.bak-env-stale-20260603-1942` (não commitados — diretório VPS Master, sync com `cadencia-growth` GitHub pendente)
- `/etc/systemd/system/cadencia-trigger.service` — criado via heredoc

## Links relacionados

- Incident pai (causa correlata, fix incompleto): `2026-06-02_cadencia-aprovou-e-nao-gerou-4-causas-raiz-convergentes.md`
- Tenants afetados:
  - Marinella/Grupo WGL — `73779837-93ee-4693-9b3e-9a5ae75a4875` (reprovisionada 19:29)
  - Mel Quevedo/Horus Marcas e Patentes — `1063c105-b096-46cf-b29c-efe657683314` (reprovisionada 19:41)
- PDL-25 (OAuth GHL bloqueado — força fallback estático e expõe esse bug)

---
*Registrado via sistema de incidentes. Ver INDEX.md para histórico completo.*
