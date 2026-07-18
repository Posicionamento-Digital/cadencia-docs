---
date: 2026-05-22
tags: [infra, vps, hostinger]
---

# Infra — VPS Hostinger

Documentação da infraestrutura VPS da Cadencia (Hostinger).

## Servidores

| Servidor | IP | Propósito | Docs |
|---|---|---|---|
| **VPS Master** | `72.60.4.71` | Produção — Lara, Cadência, n8n, pipelines | [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Arquitetura]] |
| **VPS Dev** | `2.24.117.172` | Desenvolvimento — dev externo codifica aqui | [[Infra/VPS-Hostinger/VPS-Dev/VPS-Dev-Documentacao-Tecnica]] |

---

## VPS Master — índice rápido

- [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Arquitetura]] — visão geral, regras de ouro
- [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Acesso-e-Usuarios]] — como conectar, SSH, CLIs
- [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Servicos]] — containers, crons, systemd
- [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Projetos-opt]] — projetos em /opt/
- [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Seguranca]] — UFW, Cloudflare, hardening
- [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Coolify]] — CI/CD, deploys automáticos
- [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Monitoramento]] — Netdata, Grafana, alertas
- [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Credenciais]] — mapa 1Password

## VPS Dev — índice rápido

- [[Infra/VPS-Hostinger/VPS-Dev/VPS-Dev-Documentacao-Tecnica]] — arquitetura e configuração
- [[Infra/VPS-Hostinger/VPS-Dev/Acesso-VPS-Dev-Luiz]] — como o Luiz acessa
- [[Infra/VPS-Hostinger/VPS-Dev/Manual-VPS-Dev]] — manual operacional
- [[Infra/VPS-Hostinger/VPS-Dev/POP-Uso-VPS-Dev]] — procedimentos operacionais
