---
date: 2026-05-22
tags: [infra, vps, arquitetura]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]", "[[marketing]]"]
---
# VPS Master — Arquitetura Geral

> Documento de referência da VPS de produção da Cadencia.
> Última atualização: 22/05/2026 — reconfiguração completa.

---

## Identificação do servidor

| Campo | Valor |
|---|---|
| **IP público** | `72.60.4.71` |
| **Hostname** | `srv1692513.hstgr.cloud` |
| **Provedor** | Hostinger (KVM) |
| **OS** | Ubuntu 24.04.4 LTS |
| **Arquitetura** | x86_64 |
| **Kernel** | 6.8.0-117-generic (atualizado em 22/05/2026) |
| **CPUs** | 1 vCPU |
| **RAM** | ~4GB |

---

## Papel na infraestrutura Cadencia

Esta VPS é o servidor de produção principal da Cadencia. Ela hospeda:

- **Lara AI** — assistente de atendimento para clientes Sorria (OpenClaw)
- **Cadência Growth** — motor de geração de conteúdo para todos os tenants Cadência
- **Stamper** — bot Telegram de gestão interna
- **Cadência n8n** — automações de workflow (INTOCÁVEL)
- **Ecuro Middleware** — API middleware para integração com o sistema ecuro
- **GCI GO WhatsApp** — bots de WhatsApp para o cliente GCI GO (INTOCÁVEL)
- **Coolify** — painel de deploy automático (CI/CD via GitHub)
- **Cloudflare Tunnel** — expõe o ecuro sem abrir portas

---

## Visão geral da arquitetura

```
Internet
   │
   ▼
Cloudflare (proxy, DDoS, WAF)
   │
   ├── :80/:443 → Traefik (coolify-proxy) → containers gerenciados
   │
   └── Cloudflare Tunnel (cloudflared) → ecuro.cadencia.app.br:8881
   
VPS 72.60.4.71
├── UFW Firewall
│   ├── :22   → ALLOW (SSH)
│   ├── :80   → ALLOW só IPs Cloudflare
│   ├── :443  → ALLOW só IPs Cloudflare
│   └── todo o resto → DENY por padrão
│
├── user: master (único acesso SSH)
│   ├── sudo irrestrito
│   ├── grupo docker
│   └── Claude Code (manutenção manual — nunca por cron)
│
├── /opt/          → projetos migrados (dono: master)
├── /cadencia/     → Cadência Growth pipeline (migração pendente para /opt/)
├── /root/         → pd-marketing + gci-go-whatsapp (legado, a migrar)
│
├── Docker Engine 29.x
│   ├── Traefik v3.3.5 (coolify-proxy) — reverse proxy
│   ├── Coolify 4.1.0 — painel de deploy
│   ├── Cadência n8n stack — INTOCÁVEL
│   ├── Lara Central + Ceilandia (OpenClaw) — cliente Sorria
│   └── Ecuro Middleware — API ecuro
│
├── Systemd services
│   ├── cadencia-webhook.service (User=master)
│   └── stamper-bot.service (User=master)
│
├── Crons root — pd-marketing e Cadência Growth (legado, a migrar)
├── Crons master — monitor-vps.sh a cada 5 min
│
└── Observabilidade
    ├── Netdata (porta 19999, só via SSH tunnel)
    ├── Cockpit (porta 9090, só via SSH tunnel)
    └── Grafana Alloy → Grafana Cloud (conta dev externo, stack 1632821)
```

---

## Domínios e endpoints

| Domínio | Aponta para | O que serve |
|---|---|---|
| `coolify.cadencia.ia.br` | VPS via Cloudflare | Painel Coolify |
| `ecuro.cadencia.app.br` | Cloudflare Tunnel | Ecuro Middleware API |
| `cadencia.app.br` | Vercel | Frontend Cadência |
| `cadencia.ia.br` | (zona Cloudflare) | subdomínios Cadência |

---

## Regra de ouro — o que NUNCA tocar sem janela de manutenção

| Container / Serviço | Motivo |
|---|---|
| `cadencia-n8n-main`, workers, postgres, redis | Cadencia — cliente ativo |
| `cloudflared` (pid ativo) | Tunnel do ecuro — derrubar quebra a API |
| `lara-central`, `lara-ceilandia` | Cliente Sorria ativo — atendimento em produção |
| `ecuromiddleware-*` | Criado pelo dev externo — não mexer sem ele |
| `gci-go-whatsapp` (em `/root/`) | Cliente GCI GO — ativo |
| Crons SOAP em `/root/pd-marketing/` | Lançamento Cadência em andamento até 29/05 |

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Acesso-e-Usuarios]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Servicos]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Projetos-opt]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Coolify]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Seguranca]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Monitoramento]]
