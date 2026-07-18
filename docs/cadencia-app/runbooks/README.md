---
date: 2026-05-13
tags: [cadencia, runbook, operacional, deploy, vps]
---

# Runbooks — Cadência

Procedimentos operacionais passo a passo para o produto Cadencia. Cada runbook descreve **como executar uma operação específica** sem precisar raciocinar do zero.

## O que fica aqui

- Como fazer deploy de nova versão na VPS (rsync + reload)
- Como reiniciar o pipeline quando travar ou parar silenciosamente
- Como corrigir erros comuns: render 0kb, font error, timeout de API
- Como rodar geração manual para um cliente específico
- Como verificar se os crons estão ativos (`crontab -l`)
- Como acessar e ler logs de produção na VPS

## Acesso à VPS

```bash
ssh -i ~/.ssh/hostinger_pd root@72.60.4.71
```

Credenciais: `Hub Projetos/Credenciais/Hostinger/.env`

## Convenção de nomes

`RB-[numero]-[descricao-slug].md` — ex: `RB-01-deploy-vps.md`

## Notas Relacionadas

- [[Projetos/Cadencia/Docs/README]]
- [[Infra/VPS-Hostinger/README]]
- [[Incidentes/Cadencia/README]]
