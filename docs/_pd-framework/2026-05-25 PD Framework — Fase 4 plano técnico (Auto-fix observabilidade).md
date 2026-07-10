---
date: 2026-05-25
tags: [ia, framework, infra, observabilidade, auto-fix, runbook, plano]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Fase 4 Plano Técnico (Auto-fix observabilidade)

> Plano técnico pra PDL-223. Não implementa código — desenha arquitetura, fluxo, estrutura de runbooks, allowlist, sequência de implementação e riscos. Vira input direto pra sessão que executar a Fase 4.
> Base existente: webhook v2 (`/opt/grafana-webhook` na VPS Master) já tem rotulação por squad + dedup por fingerprint + criação de issue Linear + alerta WhatsApp Stevo.
> Capturado durante sessão paralela à Fase 0.7 (inventário).

---

## Estado atual (o que já funciona)

```
Grafana Cloud (alert rule firing)
    │
    ▼ POST https://alertas.cadencia.ia.br/webhook (X-Webhook-Secret)
    │
/opt/grafana-webhook/main.py (systemd grafana-webhook.service, porta 9300)
    │
    ├── Detecta squad via labels.ruleGroup (vps-infra→infra, vps-security→security)
    ├── Envia WhatsApp Stevo (sempre)
    └── Cria issue Linear com label [ALERTA][squad]:nome (com dedup fingerprint, TTL 30min)
```

**O que falta (escopo PDL-223):**
- (a) Executor determinístico de runbooks pré-aprovados
- (b) Fluxo de aprovação WhatsApp pra alertas sem runbook match
- (c) Webhook escrever STATE.md do Squad Infra ao receber alerta

---

## Arquitetura proposta

### Diagrama do loop completo

```
Grafana → webhook v2 → cria issue Linear (label `auto-fix`)
                    └── escreve STATE.md infra (seção [L2] Alertas ativos)
                    │
                    ▼  (worker cron 5min)
            squads/infra/workers/runbook-executor.py
              ├── lista issues label `auto-fix` (Linear API)
              ├── match alertname → squads/infra/runbooks/<app>/<rule>.sh
              ├── valida ALLOWLIST.md (container/serviço permitido?)
              │     │
              │     ├── tem runbook + allowlist OK → executa → atualiza STATE.md → fecha issue
              │     └── sem runbook OU allowlist viola → escala (label `escalado` + endpoint approve)
              │
              └── relata em log /var/log/pd-framework/infra.log

Endpoint approve (b)
    │
    ▼ alerta novo sem runbook
webhook envia WhatsApp Felipe com menu numerado [1] runbook X [2] runbook Y [3] manual [4] ignore
    │
    ▼ Felipe responde "1" via WhatsApp
Stevo → callback POST /approve/<alert_id>
    │
    ├── valida assinatura Stevo
    ├── executa ação correspondente
    └── atualiza STATE.md + fecha issue
```

---

## Estrutura no monorepo (Fase 2 cria, Fase 4 popula)

```
squads/infra/
├── CLAUDE.md
├── memory/
│   ├── STATE.md            ← seção [L2] "Alertas ativos" é mutável pelo webhook + executor
│   └── decisions.md
├── workers/
│   ├── webhook-receptor.py    ← evolução do /opt/grafana-webhook/main.py atual
│   ├── runbook-executor.py    ← novo (Fase 4)
│   ├── monitor-vps.sh         ← migrado de /opt/scripts/monitor-vps.sh
│   ├── collect-custom-metrics.py ← migrado de /opt/scripts/
│   └── crons/schedule.yaml
├── runbooks/
│   ├── ALLOWLIST.md           ← regra absoluta: containers que executor pode tocar
│   ├── disco/
│   │   └── raiz-log-rotate.sh
│   ├── ram/
│   │   └── disponivel-restart-app.sh
│   ├── traefik/
│   │   └── ram-restart.sh
│   ├── tcp/
│   │   └── close-wait-investigar.sh
│   ├── load/
│   │   └── average-investigar.sh
│   ├── security/
│   │   └── ssh-brute-force-block-ip.sh
│   └── vercel/
│       └── deploy-falhado-retry.sh
└── context/
    ├── topologia-vps.md     ← snapshot containers + systemd + crontab (input do snapshot 25/05 00:40)
    └── alert-rules.md       ← 7 alert rules ativas + thresholds (do Stack-Monitoramento)
```

---

## Estrutura de cada runbook

Convenção: shell determinístico, idempotente, com 4 fases.

```bash
#!/usr/bin/env bash
# squads/infra/runbooks/<categoria>/<rule>.sh
# Runbook: <descrição curta>
# Alertname (Grafana): <ex: traefik_ram_high>
# Allowlist target: <container ou serviço>
# Idempotente: sim/não
# Versão: 1

set -euo pipefail

# ==== 1. CONTEXTO ====
ALERT_ID="${1:?alert_id obrigatório (issue Linear)}"
TARGET="${2:-coolify-proxy}"

# ==== 2. VALIDAÇÃO (allowlist + pré-condições) ====
source "$(dirname "$0")/../../workers/_validate_allowlist.sh"
check_allowlist "$TARGET" || { echo "ALLOWLIST violada: $TARGET"; exit 3; }

# ==== 3. AÇÃO (determinística, sem perguntas) ====
echo "[runbook] restart $TARGET (alert $ALERT_ID)"
docker restart "$TARGET"

# ==== 4. VERIFICAÇÃO + REPORT ====
sleep 5
docker inspect -f '{{.State.Status}}' "$TARGET" | grep -q running || exit 4

echo "OK runbook concluído"
exit 0
```

Códigos de saída padronizados:
- `0` — sucesso, fecha issue
- `2` — não aplicável (condição mudou, alerta auto-resolveu)
- `3` — violou allowlist (NUNCA deve acontecer — bug no executor)
- `4` — ação tentada mas verificação falhou — escala
- `≥10` — erro técnico no runbook — escala

---

## ALLOWLIST.md (regra absoluta)

```markdown
# Runbook Executor — Allowlist

Único arquivo que define o que o executor pode tocar. Tudo que NÃO está aqui é proibido.

## Containers permitidos (restart, stats, exec read-only)

- coolify-proxy (traefik)
- coolify-sentinel
- coolify-realtime
- insight-artificial (quando containerizar)
- assessoria-imprensa-cadencia

## Containers PROIBIDOS (NUNCA tocar autônomo)

- cadencia-n8n-main, cadencia-n8n-worker-*, cadencia-n8n-runner-*
- cadencia-postgres, cadencia-redis, cadencia-redis-db
- coolify, coolify-db, coolify-redis
- ecuromiddleware-* (Ecuro)
- lara-ceilandia, lara-central (cliente em produção)

## Serviços systemd permitidos (restart)

- grafana-webhook
- scoring-webhook
- cadencia-webhook  ← ATENÇÃO: afeta Cadência. Felipe confirma antes de adicionar?

## Serviços PROIBIDOS

- alloy, netdata, cloudflared, sshd, NetworkManager, containerd

## Ações de sistema permitidas

- logrotate manual em /var/log
- ufw block <IP> (com TTL via cron de unblock 24h depois)
- limpeza /tmp/* com 7+ dias

## Ações PROIBIDAS

- rm -rf em qualquer path fora /tmp ou /var/log/*.gz
- iptables direto (usar UFW)
- systemctl stop em qualquer serviço
- docker rm, docker volume rm
- kernel/sysctl
```

---

## runbook-executor.py — esqueleto funcional

```python
#!/usr/bin/env python3
"""runbook-executor — worker cron Squad Infra.

Roda a cada 5min na VPS Master via harness.sh. Lê issues Linear com label
'auto-fix' criadas pelo webhook v2, executa runbook correspondente se houver
match + allowlist OK, fecha issue ou escala.

Determinístico. NUNCA usa LLM, NUNCA shell arbitrário. Toda ação vem de
runbook .sh pré-aprovado.

Fluxo:
  1. lista issues Linear label='auto-fix' state='Triage|Backlog|Todo'
  2. pra cada issue:
     - extrai alertname (de labels) e target (de description)
     - resolve runbook: squads/infra/runbooks/<categoria>/<rule>.sh
     - se runbook não existe → label='escalado' + chama endpoint approve
     - se existe: valida ALLOWLIST → executa → captura exit code
       - 0 → comment + fecha issue + state='Done' + atualiza STATE.md
       - 2 → comment "auto-resolveu" + fecha
       - 4/≥10 → comment com stderr + label='escalado'
"""

import os, sys, subprocess, re
from pathlib import Path

# import _shared/
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_shared"))
from linear_client import graphql
from stevo_client import StevoClient
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core"))
from state_updater import StateUpdater  # noqa

RUNBOOKS_DIR = Path(__file__).resolve().parent.parent / "runbooks"
ALLOWLIST_PATH = RUNBOOKS_DIR / "ALLOWLIST.md"

ALERTNAME_TO_RUNBOOK = {
    # mapeamento explícito (não inferir). Match contra Grafana alertname.
    "vps_load_average_alto":  "load/average-investigar.sh",
    "traefik_ram_alta":       "traefik/ram-restart.sh",
    "tcp_close_wait_excessivo": "tcp/close-wait-investigar.sh",
    "disco_raiz_baixo":       "disco/raiz-log-rotate.sh",
    "ram_disponivel_baixa":   "ram/disponivel-restart-app.sh",
    "ssh_brute_force":        "security/ssh-brute-force-block-ip.sh",
    "vercel_deploy_falhado":  "vercel/deploy-falhado-retry.sh",
}

def list_autofix_issues() -> list[dict]:
    # GraphQL query
    ...

def resolve_runbook(alertname: str) -> Path | None:
    rel = ALERTNAME_TO_RUNBOOK.get(alertname.lower())
    if not rel:
        return None
    p = RUNBOOKS_DIR / rel
    return p if p.exists() else None

def validate_allowlist(target: str) -> bool:
    text = ALLOWLIST_PATH.read_text(encoding="utf-8")
    # busca target na seção "Containers PROIBIDOS" → False
    # busca target na seção "Containers permitidos" → True
    # default → False (deny por padrão)
    ...

def execute_runbook(runbook: Path, alert_id: str, target: str) -> tuple[int, str, str]:
    r = subprocess.run(
        ["bash", str(runbook), alert_id, target],
        capture_output=True, text=True, timeout=120
    )
    return r.returncode, r.stdout, r.stderr

def main():
    issues = list_autofix_issues()
    state = StateUpdater("infra")
    for issue in issues:
        alertname = extract_alertname(issue)
        target = extract_target(issue)
        runbook = resolve_runbook(alertname)
        if not runbook:
            escalate(issue, reason="sem runbook match")
            continue
        if not validate_allowlist(target):
            escalate(issue, reason=f"allowlist viola: {target}")
            continue
        code, out, err = execute_runbook(runbook, issue["id"], target)
        if code == 0:
            close_issue(issue, comment=f"runbook OK\n```\n{out}\n```")
            state.add_l2(f"Resolvido auto: {alertname} ({target})")
        elif code == 2:
            close_issue(issue, comment="alerta auto-resolveu (runbook detectou)")
        else:
            escalate(issue, reason=f"runbook falhou (exit {code})\nstderr:\n{err[:500]}")
    state.save()

if __name__ == "__main__":
    main()
```

---

## Endpoint approve (b) — extensão do webhook v2

Adicionar ao `/opt/grafana-webhook/main.py`:

```python
@app.post("/approve/<alert_id>")
def approve(alert_id):
    # 1. valida assinatura Stevo (X-Stevo-Signature header)
    # 2. parseia callback: {from: "5511914912127", text: "1"}
    # 3. lê cache .pending_approvals[alert_id] (criado quando alerta sem runbook chegou)
    # 4. mapeia resposta:
    #    "1"/"2" → executa runbook X/Y da lista oferecida
    #    "3" → manual: deixa issue aberta, manda "OK, vai investigar manualmente"
    #    "4" → ignore: fecha issue com label `ignorado` + razão
    # 5. atualiza STATE.md infra
```

Fluxo quando alerta novo chega (no `webhook-receptor.py`):

```python
# pseudo
runbook_candidatos = sugerir_runbooks(alertname)  # heurística top-3
if not runbook_candidatos:
    cria issue normal + manda WhatsApp "alerta sem runbook conhecido, abrir Linear"
else:
    cria issue (sem auto-fix)
    cache.pending_approvals[alert_id] = runbook_candidatos
    stevo.send_text(
        FELIPE_PHONE,
        f"⚠️ {alertname}\n"
        f"Sugestões:\n"
        f"[1] {runbook_candidatos[0]}\n"
        f"[2] {runbook_candidatos[1]}\n"
        f"[3] investigar manual\n"
        f"[4] ignorar"
    )
```

Atenção: Stevo callback precisa ser configurado pro webhook receber respostas. Não confundir com envio. Conferir documentação Stevo / verificar se sm-canguru aceita callback.

---

## (c) Webhook atualiza STATE.md infra

Adicionar ao webhook v2:

```python
# em handler do alert
def update_infra_state(alert: dict):
    state_path = REPO_ROOT / "squads/infra/memory/STATE.md"
    # operação atômica: file lock + rewrite
    with filelock.FileLock(f"{state_path}.lock"):
        s = StateUpdater("infra")
        if alert["status"] == "firing":
            s.add_l2(f"[ALERTA] {alert['labels']['alertname']} firing desde {alert['startsAt']}")
        else:  # resolved
            # remove L2 entry correspondente
            s._l2 = [x for x in s._l2 if alert['labels']['alertname'] not in x]
        s.save()
        # git add + commit + push (segue convenção do harness)
        subprocess.run(["git", "-C", str(REPO_ROOT), "add", str(state_path)])
        subprocess.run(["git", "-C", str(REPO_ROOT), "commit", "-m",
                       f"chore(infra): state update — alerta {alert['labels']['alertname']}"])
        subprocess.run(["git", "-C", str(REPO_ROOT), "push"])
```

Atenção a race condition: se webhook v2 escreve STATE.md ao mesmo tempo que executor cron está atualizando, file lock resolve localmente, mas push pode colidir. Solução: webhook usa o mesmo loop de retry/--theirs do `harness.sh`.

---

## Sequência de implementação (estimativa 3-4h)

1. **Pre-req:** Squad Infra existir (Fase 2 PDL-226)
2. **Migrar webhook v2** pra `squads/infra/workers/webhook-receptor.py` (mantendo systemd unit apontando pra novo path via symlink ou refactor de unit file)
3. **Criar ALLOWLIST.md** (10min — colar do plano acima, ajustar `cadencia-webhook` com confirmação do Felipe)
4. **Criar 7 runbooks `.sh`** iniciais (20-30min cada = 2.5h max)
   - Começar pelos 3 mais seguros: traefik-ram-restart, vercel-deploy-falhado-retry, ssh-brute-force-block-ip
   - Deixar disco/ram/close-wait/load por último (envolvem heurística)
5. **runbook-executor.py** (60min)
6. **Cron entry** no Squad Infra `schedule.yaml`: `*/5 * * * *` rodando via `harness.sh`
7. **Dry-run em alerta simulado** — disparar webhook teste via curl, ver issue Linear criada, ver executor pegar, ver runbook rodar (em container teste), ver issue fechar
8. **Endpoint approve (b)** — adicionar último, requer pesquisa Stevo callback
9. **STATE.md update (c)** — adicionar ao webhook após (a) funcionar end-to-end

---

## Decisões abertas (pra Felipe)

1. **`cadencia-webhook` na allowlist?** Restart desse afeta Cadência (produto core). Default sugerido: PROIBIDO. Mas se ele cair, alguém precisa restartar manualmente. Alternativa: deixar permitido mas exigir `--force` flag no runbook (= sempre escalar primeiro).
2. **Stevo callback existe?** sm-canguru.stevo.chat aceita receber mensagens (não só enviar)? Se não, endpoint approve fica via Telegram (stamper-bot já tem listener) ou via comando local "fechar PDL-XXX runbook=1".
3. **STATE.md commit a cada alerta?** Pode poluir histórico git. Alternativa: webhook escreve em arquivo `queue/state-updates/infra-<ts>.json`, executor consolida e commita 1x por execução (5min).
4. **Runbook idempotência:** se executor rodar 2x no mesmo alert_id (ex: rebooto da VPS), runbook executa 2x. Solução: cache em `/tmp/runbook-executor-<alert_id>.done` (TTL 1h) verificado antes de executar.
5. **Escala humana:** quando escalar, mandar WhatsApp imediatamente ou só atualizar Linear? Default sugerido: WhatsApp se severity=high ou critical, só Linear se medium/low.

---

## Riscos

| Risco | Mitigação |
|---|---|
| Runbook destrói produção (restart errado) | ALLOWLIST.md absoluta + denied by default + Felipe confere PR |
| Executor cron loop infinito (issue não fecha após runbook) | rate limit: max 3 execuções por issue, depois escala |
| Webhook race condition STATE.md | filelock + retry com --theirs (mesmo padrão harness) |
| Stevo callback inseguro | validar X-Stevo-Signature + IP allowlist do callback |
| Runbook trava (timeout) | subprocess timeout=120s no executor + kill -9 graceful |
| Felipe offline (escalação sem destino) | mensagem WhatsApp acumula na conversa pessoal; nada explode (alerta crítico já manda WhatsApp via webhook v2 padrão) |

---

## Refs

- Webhook v2 atual: [[Infra/Stack-Monitoramento-VPS-Master]] (credenciais já limpas em 24/05)
- Issue Linear: PDL-223 (Backlog)
- Squad Infra (Fase 2): PDL-226
- Snapshot VPS Master capturado 25/05 00:40: `Rotina/sessions-log/2026-05-24/vps-master-snapshot-2026-05-25_0040.md`
- Convenção de runbook + harness: `pd-framework/_core/harness.sh` + `pd-framework/_core/SECURITY.md`
