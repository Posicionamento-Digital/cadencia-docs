---
date: 2026-05-18
tags: [documentacao, projeto, portal-pd, multi-tenant]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Nathalia-Galardo]]", "[[pd-portal]]"]
---
# Portal de Clientes PD — Visao Geral

## Identidade
- **Tipo:** frontend multi-tenant
- **Stack:** Next.js 16, Tailwind v4, Supabase, Vercel
- **URL:** https://portal.cadencia.ia.br/[tenant-slug]
- **Repo:** Posicionamento-Digital/pd-portal
- **Status:** ativo (primeiro tenant Nathalia Galardo em 18/05/2026)

## O que e
Portal onde clientes, alunos e consultorias da PD acessam documentacao, arquivos, videos e materiais curados. Isolado por tenant, autenticado, sem interface de admin - gerenciado via skills Claude Code.

## Para que serve
Centralizar a entrega de conteudo para clientes da PD. Substitui envio por WhatsApp/Drive. Cliente tem area propria com tudo organizado.

## Componentes
- [[auth]] - login PD + middleware
- [[portal-shell]] - header + 4 tabs
- [[skills-portal]] - 5 skills de gestao

## Fluxo de onboarding de tenant
1. Felipe roda /portal-setup-tenant <ghl_contact_id>
2. Skill busca dados no GHL, cria pasta no repo, cria usuario Supabase
3. Felipe roda /portal-wiki para publicar notas do Obsidian
4. Felipe roda /portal-arquivos para upload de planilhas
5. Portal no ar para o cliente

## Don'ts
- NUNCA expor service_role key no client
- NUNCA redirecionar para Cadencia em caso de erro
- Storage paths precisam ser ASCII (sem acentos)

## Historico
- 2026-05-18 - v0.1.0 - Launch com tenant Dra. Nathalia Galardo

## Notas Relacionadas
[[Clientes/Nathalia-Galardo/Nathalia-Galardo]] - [[MOC-Trabalho-PD]]
