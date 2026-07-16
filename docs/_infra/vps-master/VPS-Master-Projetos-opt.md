---
date: 2026-05-22
tags: [infra, vps, projeto, opt]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]", "[[marketing]]"]
---
# VPS Master — Projetos em /opt/

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


> Todos os projetos em `/opt/` têm dono `master`. Acesso: `ssh vps-master` → arquivos em `/opt/<projeto>/`.

---

## Mapa de /opt/

```
/opt/
├── assessoria-imprensa-cadencia/   → conteúdo editorial (sem serviço ativo)
├── cadencia-app/                   → cópia do monorepo Next.js (backup — não roda aqui)
├── insight-artificial/             → pipeline de publicação Notion→Supabase
├── lara-ai/                        → config da Lara (compose está em ECURO Middleware/)
├── openclaw/                       → código-fonte do OpenClaw (imagem dos containers lara)
├── scripts/                        → scripts de operação da VPS
└── stamper-telegram-bot/           → bot Telegram (rodando via systemd)
```

**Em `/root/` (legado — a migrar):**
- `/root/gci-go-whatsapp/` → INTOCÁVEL, cliente ativo
- `/root/pd-marketing/` → aguarda decisão estratégica (Cadência vs refatoração)

**Em `/cadencia/` (legado — migração agendada):**
- Cadência Growth pipeline — migrar para `/opt/cadencia-growth/` em janela de fim de semana

---

## Projetos detalhados

### /opt/assessoria-imprensa-cadencia/

**O que é:** materiais editoriais e templates de assessoria de imprensa para a Cadência.

**Conteúdo:** narrativas de fundador, press releases, portais de mídia, roteiros.

**Serviços:** nenhum — é um repositório de documentos.

**GitHub:** `felipeluissalgueiro/assessoria-imprensa-cadencia`

**Status:** sem automação ativa. Consultar para criar materiais de PR.

---

### /opt/cadencia-app/

**O que é:** cópia do monorepo completo do Cadência (Next.js + Supabase + workers + growth).

**Por que está aqui:** foi clonado em 13/05/2026 durante uma sessão de desenvolvimento. É uma cópia de trabalho — **não é o serviço em produção**.

**Onde o Cadência realmente roda:**
- Frontend: Vercel (`cadencia.app.br`)
- Workers: Coolify VPS Master (Railway DESLIGADO, DEV-638)
- Growth pipeline: `/cadencia/` nesta VPS

**GitHub:** `felipeluissalgueiro/cadencia-app`

**Status:** pode estar desatualizado. Usar `git pull` antes de consultar como referência.

```bash
cd /opt/cadencia-app
git pull
```

---

### /opt/insight-artificial/

**O que é:** pipeline de publicação do blog Insight Artificial.

**O que faz:**
1. Consulta Notion por artigos aprovados
2. Gera imagem featured via OpenAI GPT-4o
3. Publica no Supabase (banco do portal)
4. Gera posts para Instagram

**Estrutura:**
```
/opt/insight-artificial/
├── .gitignore
├── Dockerfile
├── brand/          → logos e identidade visual
└── scripts/
    ├── cron_publish.py         → pipeline principal (Notion→Supabase)
    ├── generate_featured_image.py  → geração de imagem via OpenAI
    ├── generate_instagram_post.py  → geração de post Instagram
    └── instagram_slots.json    → configuração de slots
```

**Env vars necessárias:** `NOTION_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `REVALIDATION_SECRET`, `PORTAL_API_URL`, `OPENAI_API_KEY`

**GitHub:** `Posicionamento-Digital/insight-artificial`

**Status:** código commitado, Coolify configurado. **Crons ainda não migrados** — os crons ainda estão no crontab do root como comentários (desativados).

**Como rodar manualmente:**
```bash
cd /opt/insight-artificial
python3 scripts/cron_publish.py
```

---

### /opt/lara-ai/

**O que é:** diretório de configuração da Lara AI (containers lara-central e lara-ceilandia).

**Conteúdo:**
```
/opt/lara-ai/
└── ECURO Middleware/
    └── docker-compose.yml   → compose do ecuro middleware (Luiz)
```

> Atenção: os containers `lara-central` e `lara-ceilandia` NÃO são iniciados a partir daqui. Eles são iniciados pelo compose em `/opt/openclaw/docker-compose.yml`.

**GitHub:** `Posicionamento-Digital/lara-ai` (espelho do openclaw-state)

---

### /opt/openclaw/

**O que é:** código-fonte e configuração dos containers Lara.

**Estrutura:**
```
/opt/openclaw/
├── deploy.sh
├── docker-compose.yml   → inicia openclaw + lara-central + lara-ceilandia
├── data/                → dados persistentes do openclaw
└── repo/                → código-fonte (git → Posicionamento-Digital/lara-ai)
    ├── Dockerfile
    ├── entrypoint.sh
    ├── identity/
    └── scripts/
```

**Como subir os containers Lara:**
```bash
cd /opt/openclaw
docker compose up -d
```

**Como ver logs da Lara:**
```bash
docker logs lara-central --tail 100 -f
docker logs lara-ceilandia --tail 100 -f
```

**GitHub do código:** `Posicionamento-Digital/lara-ai`

**Status:** containers rodando e saudáveis. INTOCÁVEL sem janela de manutenção.

---

### /opt/scripts/

**O que é:** scripts de operação da VPS.

**Conteúdo:**
```
/opt/scripts/
└── monitor-vps.sh   → monitoramento a cada 5 min (cron master)
```

**monitor-vps.sh — o que verifica:**
- Load average vs número de CPUs
- Conexões TCP em CLOSE_WAIT (>1000 = possível flood)
- Sockets TCP alocados no kernel (>10.000 = alerta)
- RAM do Traefik (>500MiB = possível memory leak)

**Quando alerta:** envia WhatsApp para o número do Felipe via Stevo API.

**Log:** `/var/log/monitor-vps.log`

```bash
# Rodar manualmente

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

sudo /opt/scripts/monitor-vps.sh

# Ver últimas entradas do log

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

tail -20 /var/log/monitor-vps.log
```

---

### /opt/stamper-telegram-bot/

**O que é:** bot Telegram de gestão interna da PD, alimentado pelo Claude Code.

**Serviço:** `stamper-bot.service` (User=master, sempre rodando)

**Estrutura:**
```
/opt/stamper-telegram-bot/
├── bot.py
├── claude_client.py
├── config.py
├── conversations.db
├── db.py
├── requirements.txt
└── venv/
```

**GitHub:** `felipeluissalgueiro/stamper-telegram-bot`

**Status:** rodando via systemd. Para reiniciar:

```bash
sudo systemctl restart stamper-bot.service
sudo journalctl -u stamper-bot.service -f
```

---

## Projetos em /root/ (legado)

### /root/gci-go-whatsapp/ ⚠️ INTOCÁVEL

**O que é:** stack de bots WhatsApp para o cliente GCI GO.

**Serviços:** múltiplos containers Docker (redis, middleware, bots por unidade).

**Status:** cliente ativo. Não modificar, não mover, não reiniciar sem janela.

**GitHub:** `Posicionamento-Digital/gci-go-whatsapp`

**Coolify:** configurado mas ainda não gerenciando (deploy manual por enquanto).

---

### /root/pd-marketing/ ⚠️ DECISÃO PENDENTE

**O que é:** pipeline de marketing da PD (Seinfeld, newsletter, SOAP, blog, Meta Ads).

**Status atual:** scripts quebrados — API key GHL inválida (PDL-156). SOAP ATO 3 em andamento até 29/05.

**Decisão pendente:** migrar para Cadência como tenant OU refatorar como container próprio.

**Ver:** Linear → Pipeline Marketing PD — Refatoração + Containerização + Restauração

---

## Cadência Growth em /cadencia/

**O que é:** motor de geração de conteúdo para TODOS os tenants Cadência.

**Status:** operacional. Migração para `/opt/cadencia-growth/` agendada para fim de semana (requer atualizar systemd + crons sem downtime).

**GitHub:** `Posicionamento-Digital/cadencia-growth`

**Ver detalhes:** [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Servicos]]

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Arquitetura]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Servicos]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Coolify]]
