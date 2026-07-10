#!/usr/bin/env python3
"""
Espelha zonas DNS Cloudflare: conta origem (Michael) -> conta destino (Felipe).
Idempotente: pode rodar várias vezes. Não ativa zonas (não troca nameservers).

Uso:
    python espelhar.py

Lê credenciais de .env no mesmo diretório.
"""
import json
import os
import sys
import time
from pathlib import Path

import urllib.request
import urllib.error


SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
BACKUP_DIR = SCRIPT_DIR / "backup"
LOG_FILE = SCRIPT_DIR / f"espelhar_{time.strftime('%Y%m%d_%H%M%S')}.log"


def load_env():
    env = {}
    if not ENV_FILE.exists():
        sys.exit(f"ERRO: {ENV_FILE} não existe")
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def log(msg):
    print(msg)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def _do_request(method, url, headers, data=None):
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_resp = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(body_resp)
        except Exception:
            return {"success": False, "errors": [{"message": f"HTTP {e.code}: {body_resp}"}]}
    except Exception as e:
        return {"success": False, "errors": [{"message": str(e)}]}


def cf_request(method, url, token=None, email=None, key=None, data=None):
    """Faz request à Cloudflare API.
    Tenta Bearer primeiro; se falhar com permission/auth error, tenta Global Key+Email.
    """
    base_headers = {"Content-Type": "application/json"}

    attempts = []
    if token:
        h = dict(base_headers)
        h["Authorization"] = f"Bearer {token}"
        attempts.append(("bearer", h))
    if email and key:
        h = dict(base_headers)
        h["X-Auth-Email"] = email
        h["X-Auth-Key"] = key
        attempts.append(("globalkey", h))

    if not attempts:
        raise ValueError("Forneça token OU email+key")

    last = None
    for label, headers in attempts:
        result = _do_request(method, url, headers, data=data)
        if result.get("success"):
            return result
        # Detecta erros de auth/permissão pra tentar próxima credencial
        errs = result.get("errors") or []
        msgs = " ".join(str(e.get("message", "")) for e in errs).lower()
        codes = [e.get("code") for e in errs]
        retry = any(
            kw in msgs for kw in ("authentication", "permission", "requires permission", "invalid request headers")
        ) or 10000 in codes or 9109 in codes or 9106 in codes
        last = result
        if not retry:
            return result
    return last


def list_zones(token=None, email=None, key=None):
    """Lista todas as zonas (paginação)."""
    zones = []
    page = 1
    while True:
        url = f"https://api.cloudflare.com/client/v4/zones?per_page=50&page={page}"
        r = cf_request("GET", url, token=token, email=email, key=key)
        if not r.get("success"):
            log(f"  ERRO listando zonas: {r.get('errors')}")
            return zones
        zones.extend(r.get("result", []))
        info = r.get("result_info", {})
        if page >= info.get("total_pages", 1):
            break
        page += 1
    return zones


def get_zone_records(zone_id, token=None, email=None, key=None):
    """Pega todos os DNS records de uma zona."""
    records = []
    page = 1
    while True:
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?per_page=100&page={page}"
        r = cf_request("GET", url, token=token, email=email, key=key)
        if not r.get("success"):
            log(f"    ERRO listando records: {r.get('errors')}")
            return records
        records.extend(r.get("result", []))
        info = r.get("result_info", {})
        if page >= info.get("total_pages", 1):
            break
        page += 1
    return records


def export_bind(zone_id, token=None, email=None, key=None):
    """Exporta zona em formato BIND."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/export"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif email and key:
        headers["X-Auth-Email"] = email
        headers["X-Auth-Key"] = key
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        return f"# Erro exportando BIND: {e}\n"


def create_zone(domain, account_id, token=None, email=None, key=None):
    """Cria zona na conta destino. Retorna o zone_id ou None."""
    url = "https://api.cloudflare.com/client/v4/zones"
    data = {
        "name": domain,
        "account": {"id": account_id},
        "type": "full",
    }
    r = cf_request("POST", url, token=token, email=email, key=key, data=data)
    if r.get("success"):
        return r["result"]["id"]
    log(f"    ERRO criando zona: {r.get('errors')}")
    return None


def find_zone_in_dst(domain, dst_zones):
    for z in dst_zones:
        if z["name"].lower() == domain.lower():
            return z
    return None


# Records que não devem ser copiados (gerados automaticamente pela CF ou inválidos pra recriar)
SKIP_TYPES = {"SOA"}


def create_record(dst_zone_id, record, token=None, email=None, key=None):
    """Cria um record DNS na zona destino."""
    if record["type"] in SKIP_TYPES:
        return {"success": True, "skipped": True}

    payload = {
        "type": record["type"],
        "name": record["name"],
        "ttl": record.get("ttl", 1),
    }

    # content / data
    if "content" in record and record["content"]:
        payload["content"] = record["content"]
    if "data" in record and record["data"]:
        payload["data"] = record["data"]

    # priority (MX, SRV, URI)
    if "priority" in record and record["priority"] is not None:
        payload["priority"] = record["priority"]

    # proxied
    if "proxied" in record:
        payload["proxied"] = record["proxied"]

    # comment
    if record.get("comment"):
        payload["comment"] = record["comment"]

    # tags
    if record.get("tags"):
        payload["tags"] = record["tags"]

    url = f"https://api.cloudflare.com/client/v4/zones/{dst_zone_id}/dns_records"
    return cf_request("POST", url, token=token, email=email, key=key, data=payload)


def get_existing_records_signature(records):
    """Gera set de assinaturas pra checar duplicatas."""
    return {
        (r["type"], r["name"].lower(), r.get("content", ""))
        for r in records
    }


def main():
    env = load_env()
    BACKUP_DIR.mkdir(exist_ok=True)

    src_token = env.get("CF_SRC_API_TOKEN")
    src_email = env.get("CF_SRC_EMAIL")
    src_key = env.get("CF_SRC_GLOBAL_KEY")

    dst_token = env.get("CF_DST_API_TOKEN")
    dst_account = env.get("CF_DST_ACCOUNT_ID")
    dst_email = env.get("CF_DST_EMAIL")
    dst_key = env.get("CF_DST_GLOBAL_KEY")

    if not src_token and not (src_email and src_key):
        sys.exit("ERRO: faltam credenciais de origem (CF_SRC_API_TOKEN ou CF_SRC_EMAIL+CF_SRC_GLOBAL_KEY)")
    if not dst_account:
        sys.exit("ERRO: falta CF_DST_ACCOUNT_ID")
    if not dst_token and not (dst_email and dst_key):
        sys.exit("ERRO: faltam credenciais de destino")

    log(f"=== Espelhamento iniciado em {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    # 1. Lista zonas da origem
    log("Listando zonas na conta ORIGEM (Michael)...")
    src_zones = list_zones(token=src_token, email=src_email, key=src_key)
    if not src_zones:
        # tenta com global key se token falhar
        if src_email and src_key:
            log("  Tentando com Global API Key...")
            src_zones = list_zones(email=src_email, key=src_key)
    log(f"  {len(src_zones)} zonas encontradas:")
    for z in src_zones:
        log(f"    - {z['name']} (id: {z['id']})")
    log("")

    # 2. Lista zonas do destino (pra checar duplicatas)
    log("Listando zonas na conta DESTINO (Felipe)...")
    dst_zones = list_zones(token=dst_token, email=dst_email, key=dst_key)
    log(f"  {len(dst_zones)} zonas já existentes:")
    for z in dst_zones:
        log(f"    - {z['name']}")
    log("")

    # 3. Pra cada zona da origem, espelhar
    summary = {"created": [], "skipped": [], "errors": []}

    for src_zone in src_zones:
        domain = src_zone["name"]
        src_zone_id = src_zone["id"]
        log(f"\n>>> Processando: {domain}")

        # Backup
        zone_backup_dir = BACKUP_DIR / domain
        zone_backup_dir.mkdir(exist_ok=True)

        log("  - Exportando BIND...")
        bind_text = export_bind(src_zone_id, token=src_token, email=src_email, key=src_key)
        (zone_backup_dir / "zone.bind.txt").write_text(bind_text, encoding="utf-8")

        log("  - Exportando JSON dos records...")
        src_records = get_zone_records(src_zone_id, token=src_token, email=src_email, key=src_key)
        (zone_backup_dir / "records.json").write_text(
            json.dumps(src_records, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        log(f"    {len(src_records)} records exportados")

        # Existe no destino?
        dst_zone = find_zone_in_dst(domain, dst_zones)

        if dst_zone:
            log(f"  - Zona já existe no destino (id: {dst_zone['id']})")
            dst_zone_id = dst_zone["id"]
            dst_records = get_zone_records(dst_zone_id, token=dst_token, email=dst_email, key=dst_key)
            existing_sig = get_existing_records_signature(dst_records)
        else:
            log("  - Criando zona no destino...")
            dst_zone_id = create_zone(domain, dst_account, token=dst_token, email=dst_email, key=dst_key)
            if not dst_zone_id:
                log("    FALHOU. Pulando.")
                summary["errors"].append(domain)
                continue
            log(f"    Criada (id: {dst_zone_id}). Status: pending NS update.")
            existing_sig = set()
            summary["created"].append(domain)

        # Importa records
        log("  - Importando records...")
        ok = 0
        skip = 0
        err = 0
        for rec in src_records:
            sig = (rec["type"], rec["name"].lower(), rec.get("content", ""))
            if sig in existing_sig:
                skip += 1
                continue
            if rec["type"] in SKIP_TYPES:
                skip += 1
                continue
            r = create_record(dst_zone_id, rec, token=dst_token, email=dst_email, key=dst_key)
            if r.get("success"):
                ok += 1
            else:
                err += 1
                errors_msg = r.get("errors", [{}])
                msg = errors_msg[0].get("message", "?") if errors_msg else "?"
                log(f"    ! Falha em {rec['type']} {rec['name']}: {msg}")
        log(f"    Resultado: {ok} criados, {skip} pulados, {err} erros")

        if dst_zone:
            summary["skipped"].append(f"{domain} (records: +{ok})")

    # 4. Resumo
    log("\n=== RESUMO ===")
    log(f"Zonas criadas no destino: {len(summary['created'])}")
    for d in summary["created"]:
        log(f"  + {d}")
    log(f"Zonas que já existiam (records sincronizados): {len(summary['skipped'])}")
    for d in summary["skipped"]:
        log(f"  ~ {d}")
    log(f"Erros: {len(summary['errors'])}")
    for d in summary["errors"]:
        log(f"  ! {d}")

    log("\nProximos passos:")
    log("  1. Verificar zonas criadas no painel Cloudflare (sua conta) — devem estar 'Pending NS Update'")
    log("  2. Replicar manualmente: Page Rules, Workers, SSL/TLS settings, WAF, Email Routing")
    log("  3. NÃO trocar nameservers no registrador ainda (mantém tudo dormente)")
    log("  4. ROTACIONAR tokens da conta origem (Michael) — eles foram expostos")
    log(f"\nLog salvo em: {LOG_FILE}")
    log(f"Backups em: {BACKUP_DIR}")


if __name__ == "__main__":
    main()
