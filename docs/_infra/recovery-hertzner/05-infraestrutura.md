---
date: 2026-05-19
tags: [documentacao, recovery, hetzner, docker, infraestrutura, devops, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
---
# 05 — Infraestrutura Docker

## O que é
24 Docker Compose stacks + configurações de rede/volumes da infraestrutura Hetzner.

## Docker stacks

**n8n (9 arquivos):** editor, webhook, worker, mcp_api, runners — arquitetura distribuída de alta disponibilidade

**Bancos:** `postgres.yml`, `mongodb.yml`, `redis.yml`, `redisdb.yml`, `redis_posicionamento.yml`, `rabbitmq2.yml`

**Aplicações:** `baserow.yml`, `calcom-api.yml`, `metabase.yml`, `minio.yml`, `kestra_migrate.yml`, `smtp2http.yml`

## Topologia resumida
```
Internet → Traefik → n8n_editor, n8n_webhook, Baserow, Metabase
n8n_worker ← RabbitMQ ← n8n_webhook
n8n_worker → PostgreSQL, Redis, Evolution API (WhatsApp)
```

## Ordem de deploy
1. PostgreSQL → Redis → RabbitMQ
2. Evolution API
3. n8n (editor + webhook + worker)
4. Metabase, Baserow, MinIO

## Notas Relacionadas
[[00-indice]] · [[04-banco-dados]] · [[03-n8n-workflows]]
