# Stack Cadencia Agenda — VPS Dev

> **Origem:** spike/POC do Luiz em sessão Claude Code (compose vivia em `/tmp/claude-1001/-home-luiz/e47f0661-*/scratchpad/agenda-spike/`).
> **Contexto:** DEV-1364 previa **Easy!Appointments** como um dos providers de agenda da Lara Cadencia (junto com Google Calendar e Cal.com — ver `times/produto/cadencia/docs/features/lara/agendamento.md`).
> **Status:** UP em modo isolado — sem integração ativa com nenhum tenant Cadencia. Provavelmente **abandonado** (POC nunca virou produto formal).

## O que é

Instalação padrão do **Easy!Appointments** (open-source, `alextselegidis/easyappointments`) — sistema de agendamento self-hosted, PHP+Apache+MySQL. UI web exposta na porta host `:8085`.

Não tem branding customizado nem integração — é a UI padrão do projeto ([easyappointments.org](https://easyappointments.org/)) rodando com config default.

## Containers

### `cadencia-agenda-app`

```
image: alextselegidis/easyappointments:latest    # pinned em 'latest' — risco de mudança silenciosa
entrypoint: docker-entrypoint.sh
restart: unless-stopped
ports: 80 → host 8085
network: cadencia-agenda-network
depends_on: mysql (service_healthy)
```

**ENV:**
```
DB_HOST=mysql                      ← hostname docker DNS
DB_NAME=easyappointments
DB_USERNAME=easyappointments
DB_PASSWORD=***
BASE_URL=http://localhost:8085     ← default, não customizado
DEBUG_MODE=TRUE                    ← ⚠️ debug em prod
# resto = defaults PHP 8.2 + Apache
```

Confirmado nos logs: `Apache/2.4.66 (Debian) PHP/8.2.30 configured -- resuming normal operations`.

### `cadencia-agenda-mysql`

```
image: mysql:8.0
cmd: mysqld
volume: cadencia-agenda-mysql-data → /var/lib/mysql
network: cadencia-agenda-network
healthcheck: healthy
```

**ENV:**
```
MYSQL_ROOT_PASSWORD=***
MYSQL_DATABASE=easyappointments
MYSQL_USER=easyappointments
MYSQL_PASSWORD=***
```

## Tráfego real

Logs `docker logs cadencia-agenda-app` (últimos dias):
- **Scanners de internet** — GETs em `/` de IPs residenciais/VPS aleatórias, User-Agent `Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0)`, `Chrome/49.0.2623.112`, etc. Alguns 400 com `\x16\x03` (SSL handshake em HTTP).
- **Uso real:** zero evidência de tenant Cadencia usando. Nenhum GET com header de tenant, sem POST de agendamento, sem session cookie legítimo.

**Interpretação:** porta 8085 exposta direto na internet (não via Cloudflare tunnel — cloudflared não roteia pra `:8085`). Scanners fazem varredura na internet buscando serviços expostos.

## Por que existe

DEV-1364 (`feat(agenda): agendamento NATIVO no Cadência`) previa múltiplos providers de agenda:
- Google Calendar API v3
- Cal.com API v2
- **Easy!Appointments API** — este spike

O plano era: cliente escolhe provider no painel, tenant tem `lara_scheduling_config.provider = 'easyappointments'`, Lara chama a API do Easy!Appointments pra checar disponibilidade / agendar. Ver `times/produto/cadencia/docs/features/lara/agendamento.md`:

> Configuração visual do terceiro provedor é um gap de UI.

Ou seja: **backend Lara suporta Easy!Appointments, mas UI do Cadencia ainda não expõe.** Luiz provavelmente subiu essa instância pra ter contra o que testar quando fosse implementar o dropdown UI. **Testes acabaram não acontecendo** e a instância ficou.

## Volume de dados

`cadencia-agenda-mysql-data` — provavelmente vazio (poucos KB, tabelas default do Easy!Appointments + 0 agendamentos reais).

## Compose file — RECONSTITUÍDO

Original vivia em `/tmp/claude-1001/-home-luiz/e47f0661-b438-4ad1-9f65-920e1e6df876/scratchpad/agenda-spike/docker-compose.yml` — **SUMIU no reboot** (`/tmp/` é efêmero). Reconstituído a partir de `docker inspect`:

```yaml
# Reconstituído em 2026-07-31 a partir de docker inspect
# Original: /tmp/claude-*/scratchpad/agenda-spike/docker-compose.yml
name: cadencia-agenda

services:
  easyappointments:
    image: alextselegidis/easyappointments:latest
    container_name: cadencia-agenda-app
    restart: unless-stopped
    ports:
      - "8085:80"
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      - cadencia-agenda-network
    environment:
      BASE_URL: http://localhost:8085
      DEBUG_MODE: "TRUE"          # ⚠️ trocar pra FALSE se manter em prod
      DB_HOST: mysql
      DB_NAME: easyappointments
      DB_USERNAME: easyappointments
      DB_PASSWORD: ${DB_PASSWORD}

  mysql:
    image: mysql:8.0
    container_name: cadencia-agenda-mysql
    restart: unless-stopped
    volumes:
      - cadencia-agenda-mysql-data:/var/lib/mysql
    networks:
      - cadencia-agenda-network
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: easyappointments
      MYSQL_USER: easyappointments
      MYSQL_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  cadencia-agenda-network:
    external: true         # já criado

volumes:
  cadencia-agenda-mysql-data:
    external: true         # já existe
```

Onde salvar novo compose: `/home/felipe/compose/cadencia-agenda/docker-compose.yml`.

## Decisões a tomar

1. **Desligar?** POC abandonado, sem uso real, expõe porta 8085 pra scanners. Mais seguro derrubar:
   ```bash
   sudo docker stop cadencia-agenda-app cadencia-agenda-mysql
   sudo docker rm cadencia-agenda-app cadencia-agenda-mysql
   sudo docker volume rm cadencia-agenda-mysql-data
   sudo docker network rm cadencia-agenda-network
   ```
2. **Manter pra retomar DEV-1364?** Se o roadmap ainda inclui Easy!Appointments como provider Lara Cadencia, vale manter. Mas mover pra Master (Coolify) — VPS Dev não é lugar de POC persistente.
3. **Fechar porta 8085 mesmo mantendo?** Se manter, tirar bind `0.0.0.0:8085` (deixar só docker network interna acessível ao Lara worker do Cadencia). Muda pra `expose: 80` em vez de `ports: 8085:80`.

## Riscos atuais

- **`DEBUG_MODE=TRUE`** — Easy!Appointments em debug expõe stack traces + config em erros. Se algum scanner acertar endpoint de erro, revela detalhes internos.
- **`image: latest`** — próximo restart pode puxar versão nova incompatível. Prod dev evitar `latest`, pinar em `alextselegidis/easyappointments:1.5.0` (versão atual estimada).
- **Porta 8085 pública** — sem WAF, sem rate limit, sem auth na home page. Superfície pra scanner + brute force login.
- **Sem backup automático** — se `cadencia-agenda-mysql-data` corromper, dados vão. Não relevante hoje (banco vazio), mas se virar produto sim.

## Refs

- Projeto Easy!Appointments: https://easyappointments.org/
- Doc oficial: https://github.com/alextselegidis/easyappointments
- Contexto DEV-1364 (agenda nativa Cadencia): `times/produto/cadencia/docs/features/lara/agendamento.md`
- Provider registry Lara Cadencia (aceita `easyappointments`/`easy!appointments`): idem doc acima
