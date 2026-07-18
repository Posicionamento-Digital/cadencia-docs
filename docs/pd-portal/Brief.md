---
date: 2026-05-18
tags: [brief, projeto, portal-clientes, briefing]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Nathalia-Galardo]]", "[[pd-portal]]"]
---
# Brief — Portal de Clientes PD

**Projeto Linear:** https://linear.app/posicionamento-digital/project/portal-de-clientes-pd-cadencia-26e3c7f0a7c2
**Repo local:** `C:\Users\felip\OneDrive\Documentos\ClaudeCode\pd-portal`
**Atualizado em:** 2026-05-18

---

## O que é e por que existe

Portal multi-tenant para clientes, alunos e consultorias da PD acessarem documentação, arquivos, vídeos e materiais complementares — tudo isolado por tenant, acesso só por URL direta.

Felipe hoje entrega docs e planilhas por WhatsApp e Drive — disperso, sem rastreamento, sem experiência profissional. O portal centraliza tudo num lugar com acesso controlado. Clientes também podem fazer upload dos próprios materiais diretamente pelo portal.

Usuários: clientes PD (consultorias, IAs personalizadas, sistemas, alunos de cursos).

---

## Stakeholders

- Felipe (product lead, CS, conteúdo — gerencia tenants via skills Claude Code)
- dev externo (dev — implementação)
- Clientes PD como usuários finais (não participam do desenvolvimento)

---

## Estado atual

- `/staff/wiki` no Cadencia com padrão MD renderer já implementado (referência de arquitetura)
- Auth Supabase + Vercel do Cadencia disponível para reutilizar
- Domínio `portal.cadencia.ia.br` configurado (CNAME Cloudflare — será reaproveitado)
- 10 notas do vault Time PD da Nathalia Galardo prontas para publicar
- 4 planilhas prontas para upload
- 6 issues no Linear (PDL-135 a PDL-140) — serão revisadas após PRD

---

## Arquitetura e stack

- **Repo:** `pd-portal` (separado do cadencia-app) em `C:\Users\felip\OneDrive\Documentos\ClaudeCode\pd-portal`
- **Frontend:** Next.js 15, React 19, Tailwind
- **Auth:** Supabase (mesmo projeto do Cadencia — reutiliza sessão e usuários)
- **Storage:** Supabase Storage (bucket `client-portal`) — upload via UI do portal e via skill
- **Deploy:** Vercel (projeto separado)
- **Domínio:** `portal.cadencia.ia.br` → CNAME para Vercel
- **Rota:** `/portal/[tenant]` com 4 tabs fixas: Wiki | Arquivos | Vídeos | Materiais
- **Conteúdo wiki:** MDs em `docs/portal/[tenant]/wiki/` no repo
- **Vídeos/materiais/config:** `docs/portal/[tenant]/config.json`
- **Controle de acesso:** tabela `client_portal_access(user_id, tenant_slug)` no Supabase do Cadencia

---

## Decisões técnicas tomadas

- **Repo separado do Cadencia** — evita acoplamento, facilita virar produto independente
- Reutiliza Supabase do Cadencia (mesmos usuários, mesma auth) — sem duplicar infra de auth
- Nova tabela `client_portal_access` — sem tocar em `user_tenant_roles` do Cadencia
- Acesso sem permissão retorna `notFound()` — não revelar existência da rota
- Wiki gerenciada via skill Claude Code (Obsidian → MD → git push → Vercel deploya)
- Clientes fazem upload de arquivos pela UI do portal (sem depender do Felipe)
- Signed URLs para download geradas no server (nunca expor service_role no client)

---

## Skills Claude Code para gestão do portal

| Skill | Função |
|---|---|
| `/portal-setup-tenant` | Cria novo tenant: pasta no repo + config.json + registro no Supabase + usuário se necessário |
| `/portal-wiki` | Converte notas do Obsidian em MDs do portal para um tenant |
| `/portal-videos` | Adiciona vídeos Tella.tv ao config.json do tenant |
| `/portal-materiais` | Adiciona links externos ao config.json do tenant |
| `/portal-arquivos` | Faz upload de arquivos para o Supabase Storage no bucket do tenant |

Todas as skills terminam com `git push origin main` — Vercel deploya automaticamente.

---

## O que NÃO fazer

- Não misturar com `/staff/wiki` do Cadencia (público interno diferente de portal de cliente)
- Não expor `service_role` no client — signed URLs geradas no server
- Não redirecionar 403 para nenhuma página interna — retornar `notFound()`
- Não criar mais de uma tabela de acesso — `client_portal_access` é a fonte única
- Não subir conteúdo de um tenant em pasta de outro

---

## Dependências críticas pendentes

- Vídeos Tella.tv da Nathalia ainda não gravados (tab Vídeos sobe vazia — sem blocker)
- Fotos e brand book da Nathalia prometidos em 2026-05-18 (para logo no header)

---

## Critério de conclusão

Portal da Dra. Nathalia Galardo no ar:

- [ ] Repo `pd-portal` criado e deployado no Vercel
- [ ] Domínio `portal.cadencia.ia.br` apontando para o novo deploy
- [ ] Acesso configurado para Nathalia (conta Supabase + `client_portal_access`)
- [ ] 10 notas wiki publicadas em `/portal/nathalia-galardo/wiki`
- [ ] 4 planilhas disponíveis para download na tab Arquivos
- [ ] Nathalia consegue fazer upload de arquivo pela UI
- [ ] Tab Vídeos e Materiais renderizando (mesmo que vazias)
