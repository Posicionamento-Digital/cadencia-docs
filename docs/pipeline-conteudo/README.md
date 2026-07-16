---
date: 2026-05-13
tags: [pipeline-conteudo, documentacao, tecnico, automacao, marketing, vps]
---

# Docs — Pipeline de Conteúdo

Documentação técnica do **pipeline automatizado de geração de conteúdo da Posicionamento Digital** — scripts na VPS que geram e publicam posts, newsletters e carrosséis.

## O que é

Conjunto de scripts Python na VPS Hostinger que automatizam a criação e publicação de conteúdo para os canais da PD:

| Script | Frequência | Função |
|---|---|---|
| `seinfeld.py` | Diário 11h BRT | Gera post usando método Seinfeld |
| `newsletter.py` | Sextas 12h BRT | Curadoria e envio de newsletter |
| Cadência (sob demanda) | Manual / via formulário | Gera carrosséis para clientes |

## O que fica aqui

- Arquitetura do pipeline (scripts, crons, fluxo de dados)
- Integração com Gemini, CRM Cadencia e canais de publicação ativos
- Configuração dos crons na VPS
- Referência de variáveis de ambiente (referência ao .env)
- Guia de onboarding para novo desenvolvedor

## Crons ativos na VPS

```
0 14 * * *    /scripts/seinfeld.py
0 15 * * 5    /scripts/newsletter.py
```

## Notas Relacionadas

- [[Projetos/Pipeline-Conteudo/Runbooks/README]]
- [[Infra/VPS-Hostinger/README]]
- [[Incidentes/Pipeline-Conteudo/README]]
