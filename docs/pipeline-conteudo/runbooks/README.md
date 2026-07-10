---
date: 2026-05-13
tags: [pipeline-conteudo, runbook, operacional, cron, vps]
---

# Runbooks — Pipeline de Conteúdo

Procedimentos operacionais para o pipeline de conteúdo da PD.

## O que fica aqui

- Como verificar se os crons estão ativos (`crontab -l`)
- Como rodar um script de geração manualmente (dry-run e produção)
- Como diagnosticar falha silenciosa (cron rodou mas não publicou)
- Como reiniciar o pipeline após atualização de credenciais
- Como verificar e ler logs de geração na VPS
- Como forçar publicação de conteúdo já gerado

## Acesso rápido

```bash
ssh -i ~/.ssh/hostinger_pd root@72.60.4.71
crontab -l          # verificar crons
journalctl -u cron  # logs do cron
```

## Convenção de nomes

`RB-[numero]-[descricao-slug].md` — ex: `RB-01-rodar-seinfeld-manual.md`

## Notas Relacionadas

- [[Projetos/Pipeline-Conteudo/Docs/README]]
- [[Infra/VPS-Hostinger/README]]
- [[Incidentes/Pipeline-Conteudo/README]]
