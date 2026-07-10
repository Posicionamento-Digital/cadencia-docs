---
date: 2026-05-19
tags: [documentacao, recovery, hetzner, codigo, github, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[ecuro-mcp]]"]
---
# 02 — Código-Fonte Recuperado

## O que é
11 projetos GitHub clonados da conta `creeai` (Jhonatan) em 11/05/2026.

## Projetos principais

| Pasta | Stack | Descrição |
|---|---|---|
| `01-plataforma-controll-ai/` | Next.js + FastAPI | SaaS multi-tenant completo |
| `02-agente-gci/` | Python + LangGraph | Agente IA para clínicas GCI |
| `03-frontends-lovable/` | React | UIs geradas no Lovable.dev |
| `05-ecuro-mcp/` | Python | API Ecuro + MCP server |
| `06-agendamento/` | Node + Python | APIs de agendamento + CalCom |
| `07-integracoes-ghl/` | Node | Integrações GoHighLevel |
| `08-kestra-infra/` | YAML | Orquestração com Kestra |

## Observações
- Dependências entre projetos: `agente-gci` consome `ecuro-mcp`
- Credenciais em `01-documentacao/credenciais/CREDENCIAIS.env` ou 1Password
- `PESSOAL-JHONATAN/` arquivado como evidência

## Notas Relacionadas
[[00-indice]] · [[03-n8n-workflows]] · [[05-infraestrutura]]
