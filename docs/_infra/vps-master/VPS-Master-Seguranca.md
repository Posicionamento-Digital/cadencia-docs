---
date: 2026-05-22
tags: [infra, vps, seguranca, ufw, cloudflare]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]"]
---
# VPS Master — Segurança

> Configurações implementadas em 22/05/2026. Baseadas no checklist pós-incidente DDoS (Deyvin).

---

## Camadas de proteção

```
Ataque externo
      │
      ▼
[1] Cloudflare — DDoS, WAF, proxy (esconde IP real)
      │
      ▼
[2] UFW — firewall do kernel (bloqueia IPs não-Cloudflare em 80/443)
      │
      ▼
[3] Kernel TCP — SYN cookies, backlog 65k, timeouts otimizados
      │
      ▼
[4] Docker + Traefik — isolamento de containers, sem raiz
      │
      ▼
[5] SSH hardening — só user master, só chave, root bloqueado
```

---

## 1. Cloudflare

Todos os domínios ativos passam pelo Cloudflare (nuvem laranja). O IP real da VPS não fica exposto.

**Proteções ativas por padrão:**
- Proteção DDoS HTTP — sempre ativa
- Proteção DDoS camada de rede — sempre ativa
- Proteção DDoS SSL/TLS — sempre ativa
- Bot Fight Mode — ativado com detecção JS

**Sobre "Modo Sob Ataque":**
O Cloudflare recomenda ativar **apenas durante um ataque real**, não permanentemente (desafia todos os visitantes incluindo legítimos). Durante um incidente: Security → Security Level → "I'm Under Attack".

**Zonas configuradas:** `cadencia.app.br`, `cadencia.ia.br`

**Cloudflare Tunnel:**
- O ecuro roda na porta 8881 (não-padrão, CF não proxia)
- Exposto via tunnel: `ecuro.cadencia.app.br → localhost:8881`
- Tunnel ID: `67645024-1a6c-487b-9086-dc0153001cdc`
- Configurado no Cloudflare Zero Trust → Networks → Tunnels
- `cloudflared` roda como processo na VPS (pid variável, porta 20241 localhost)

---

## 2. UFW (Uncomplicated Firewall)

Estado: **ativo**

### Regras de entrada

| Porta | Ação | De onde | Observação |
|---|---|---|---|
| 22/tcp | ALLOW | Anywhere | SSH — único acesso direto |
| 80 | ALLOW | IPs Cloudflare (13 ranges) | HTTP — só via CF |
| 443 | ALLOW | IPs Cloudflare (13 ranges) | HTTPS — só via CF |
| 80 | DENY | Anywhere | Bloqueia acesso direto ao IP |
| 443 | DENY | Anywhere | Bloqueia acesso direto ao IP |
| 8000 | DENY | Anywhere | Coolify — acesso só via domínio |
| 19999 | DENY | Anywhere | Netdata — só via SSH tunnel |
| 8765 | ALLOW | Anywhere | trigger_server Cadência Growth |
| 8766 | ALLOW | Anywhere | cadencia-webhook service |
| 39090 | ALLOW | Anywhere | (porta pré-existente — verificar) |

> Atenção: as portas 8765, 8766 e 39090 estão abertas para qualquer IP. Verificar se devem ser restritas.

### Comandos UFW

```bash
# Ver regras numeradas
sudo ufw status numbered

# Adicionar regra
sudo ufw allow from <IP> to any port <PORTA>

# Remover regra
sudo ufw --force delete <NUMERO>

# Recarregar após mudanças
sudo ufw reload
```

---

## 3. Kernel TCP — hardening anti-SYN flood

Configurado em `/etc/sysctl.conf` (persiste após reboot):

```bash
# SYN cookies — não aloca memória antes do handshake completar
net.ipv4.tcp_syncookies = 1

# Reduz retentativas de handshake incompleto
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 3

# Backlog aumentado (256 → 65535)
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535

# Libera conexões fechadas mais rápido
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_tw_reuse = 1
```

**Por que isso importa:** no incidente Deyvin, 34k conexões falsas esgotaram a memória. Com SYN cookies, conexões falsas não consomem memória.

**Verificar valores atuais:**
```bash
sysctl net.ipv4.tcp_syncookies net.core.somaxconn net.ipv4.tcp_max_syn_backlog
```

---

## 4. Docker — file descriptors

Configurado em `/etc/systemd/system/docker.service.d/override.conf` e `/etc/security/limits.conf`:

- Limite de file descriptors por container: **65.000** (padrão era 1.024)
- live-restore: ativo (containers sobrevivem ao restart do daemon)

Verificar:
```bash
docker exec <container> sh -c 'ulimit -n'
# deve retornar: 65000
```

---

## 5. SSH hardening

Arquivo: `/etc/ssh/sshd_config`

```
PermitRootLogin no
PasswordAuthentication no
AllowUsers master
PubkeyAuthentication yes
```

- Root: `passwd -l root` (senha bloqueada — impossível login direto)
- User ubuntu: `nologin` + senha bloqueada (user padrão Hostinger desabilitado)
- Apenas `master` com chave SSH pode entrar

---

## Traefik — versão travada

O Coolify normalmente atualiza o Traefik automaticamente. Isso foi **desativado** porque uma versão bugada (3.6.16) gerou memory leak de 4.7GB em 40min.

- Versão fixada: `traefik:v3.3.5`
- Arquivo: `/data/coolify/proxy/docker-compose.yml`
- **Antes de qualquer atualização:** checar changelog por "memory", "CPU", "leak"

---

## Protocolo de resposta a incidente

### Sinais de ataque em andamento

```bash
# Verificar conexões TCP anormais
ss -s
ss -nt state close-wait | wc -l  # >1000 = alerta

# Verificar consumo por container
docker stats --no-stream

# Verificar RAM do Traefik (proxy)
docker stats coolify-proxy --no-stream
# >500MiB = memory leak ou flood
```

### Se estiver sob ataque agora

1. Acessar Cloudflare → zona relevante → Security → "I'm Under Attack"
2. `ssh vps-master`
3. `sudo systemctl restart docker` (reinicia Traefik — libera memória)
4. Monitorar com `watch -n5 'docker stats --no-stream'`

### Backup de emergência

Antes de qualquer operação de risco:
- Painel Hostinger → VPS → Backups → criar snapshot

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Arquitetura]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Monitoramento]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Acesso-e-Usuarios]]
