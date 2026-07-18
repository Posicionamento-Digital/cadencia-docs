---
date: 2026-05-22
tags: [infra, vps, credenciais, 1password]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]", "[[marketing]]"]
---
# VPS Master — Mapa de Credenciais

> **REGRA ABSOLUTA:** nenhum valor sensível (senha, token, chave) é registrado neste documento.
> Todos os segredos estão no **1Password**. Este arquivo é um mapa de onde encontrar cada um.

---

## Como buscar credenciais via CLI

```bash
# Buscar por nome do item
op item get "<NOME DO ITEM>" --vault "<VAULT>" --fields <campo> --reveal

# Exemplos:
op item get "Hostinger VPS Master - master (SSH Key)" --vault Hosts --reveal
op item get "Coolify - API - VPS Master" --vault Hosts --fields password --reveal
```

---

## Acesso SSH

| Credencial | Vault | Item | Campo |
|---|---|---|---|
| Chave SSH master (VPS prod) | Hosts | Hostinger VPS Master - master (SSH Key) | private key |
| Chave SSH felipe (VPS dev) | Hosts | Hostinger VPS Dev - felipe (SSH Key) | private key |
| Chave SSH luiz (VPS dev) | Hosts | Hostinger VPS Dev - luiz SSH Key (nova 2026-05-22) | private key |

**Arquivos locais (máquina Felipe):**
- `~/.ssh/hostinger_prod_master` — acesso master VPS prod
- `~/.ssh/hostinger_dev_felipe` — acesso felipe VPS dev
- `~/.ssh/hostinger_dev_luiz_new` — acesso luiz VPS dev

---

## VPS e Hostinger

| Credencial | Vault | Item |
|---|---|---|
| Senha root VPS master (emergência) | Hosts | Hostinger VPS - Developer - rootpassword |
| API Hostinger (para DNS/VPS management) | Hosts | Credencial API - Hostinger [ClaudeCode] |
| 1Password SA token (leitura da VPS prod) | Hosts | Hostinger VPS - Acessos & Credenciais |

---

## Coolify

| Credencial | Vault | Item | Campo |
|---|---|---|---|
| API token Coolify | Hosts | Coolify - API - VPS Master | password |
| GitHub App credentials | Hosts | Coolify - GitHub App coolify-vpsmaster | vários campos |
| GitHub App private key | Hosts | Github - App Coolify - Private key | — |

---

## Cloudflare

| Credencial | Vault | Item | Campo |
|---|---|---|---|
| API token (DNS + Zone) | Hosts | Cloudflare - API Token + Zones | api_token |
| Zona cadencia.app.br | Hosts | Cloudflare - API Token + Zones | zone_cadencia_app_br |
| Zona cadencia.ia.br | Hosts | Cloudflare - API Token + Zones | zone_cadencia_ia_br |

> O API token atual tem permissões de Zone DNS. **Não tem** permissão de Zone Settings (security level, etc.) — configurar manualmente no dashboard se necessário.

---

## GitHub

| Credencial | Vault | Item | Campo |
|---|---|---|---|
| PAT org (leitura + escrita repos Posicionamento-Digital) | Hosts | Github - VPS Dev - org access | password |
| SSH key VPS prod para GitHub | Hosts | Hostinger VPS Master - master (SSH Key) | — |

---

## Grafana / Alloy

| Credencial | Vault | Item |
|---|---|---|
| API key Grafana Cloud (Alloy) | Configurado no systemd da VPS | Verificar com dev externo |

> O valor está no `env.conf` do systemd em `/etc/systemd/system/alloy.service.d/env.conf`. A conta Grafana Cloud foi criada pelo dev externo — login pendente de confirmação.

---

## Supabase

| Credencial | Vault | Item |
|---|---|---|
| PAT CLI (acesso management API) | databases | Supabase - ClaudeCode - CLI |
| Hub PD service_role | databases | Supabase - HubPD - [ClaudeCode] |

---

## Stevo (WhatsApp API)

| Credencial | Vault | Item |
|---|---|---|
| API key Stevo | Posicionamento Digital | STEVO |

URL: `https://sm-canguru.stevo.chat`

---

## Pending — itens a registrar

- [ ] Credenciais Grafana Cloud (após dev externo confirmar email)
- [ ] Env vars do pd-marketing (60+ variáveis) — mover para 1P quando containerizar

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Arquitetura]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Acesso-e-Usuarios]]
