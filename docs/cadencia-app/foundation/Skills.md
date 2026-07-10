---
date: 2026-05-25
tags: [documentacao, cadencia, skill, framework]
moc: "[[Cadencia-Framework/Docs/README]]"
projeto: Cadência
type: source
entities: ["[[Cadencia-Framework]]", "[[Cadencia]]"]
---
# Skills do Squad Cadência

5 skills locais + 2 globais. Detalhes em `times/produto/cadencia/skills/<nome>/SKILL.md`.

## Locais (`times/produto/cadencia/skills/`)

### `/cadencia-debate`
Roundtable Catarina + Vitor + Amélia (opt-in Maria/Pedro/Rafael/Diego/Letícia/João cross-Time). Pra decisões de produto/arquitetura/feature complexa.

### `/cadencia-review-deploy`
Code review (Amélia adversarial) + corrige bugs + commit + push no repo cadencia-app. Opera via `CADENCIA_REPO` path absoluto.

### `/capi-test`
Testa endpoint CAPI Meta + valida eventos no Events Manager.

### `/gerenciar-plano`
Gerencia planos e créditos de tenants via Supabase Service Role Key.

### `/analytics-report`
Relatório cruzado GA4 + PostHog + Mixpanel → Obsidian (vault Time PD `Produtos/Cadencia/Analytics/`). **Migrado de Notion em 25/05.** TODO técnico: adaptar `analytics_notion.py` → `analytics_obsidian.py`.

## Globais (`~/.claude/skills/`)

### `/tally-form-cadencia`
Briefing de marca via Tally — 24 perguntas (identidade visual, perfil marca, público, rosto, prioridade conteúdo).

### `/criar-tenant-agencia`
Provisioning white-glove de tenant — Felipe preenche manualmente identidade, profiling Big5/DPR, visual 15 presets, fotos, logo, editorias, restrições, história. Gera Soul.md, envia credenciais via Stevo.

## Padrão de invocação

Todas as skills locais têm bloco de setup:

```bash
CADENCIA_REPO="C:/Users/felip/OneDrive/Documentos/ClaudeCode/Hub Projetos/Projetos BMAD/Cadencia"
cd "$CADENCIA_REPO" || exit 1
```

Skills invocáveis de qualquer cwd. **Migração futura:** ao migrar repo pra Coolify VPS Master, atualizar path em todas as 4 skills.

## Notas relacionadas

- [[Cadencia-Framework/Docs/README]]
- [[Cadencia-Framework/Docs/Bootstrap-Sessao-2026-05-25]]
