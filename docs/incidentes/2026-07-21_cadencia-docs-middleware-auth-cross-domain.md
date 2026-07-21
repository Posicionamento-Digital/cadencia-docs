---
category: human_error
severity: alta
service: cadencia-docs
duration_hours: 2
detected_by: felipe
date: 2026-07-21
---

# Incidente: cadencia-docs inacessível — middleware cross-domain + env vars com newline + over-engineering

**Data:** 21/07/2026  
**Severidade:** Alta  
**Projeto:** cadencia-docs + cadencia-app  
**Duração do impacto:** ~2h (acesso ao docs completamente bloqueado)  
**Tags:** #auth #vercel #middleware #config-drift #frontend #silenciosa

## O que aconteceu

Ao implementar proteção por auth no site `docs.cadencia.app.br`, o usuário era redirecionado em loop para a tela de login do Cadencia mesmo estando autenticado como super_admin. Cada tentativa de correção introduzia novos problemas, gerando ~6 PRs desnecessários em cadencia-app e cadencia-docs antes de chegar na solução correta: remover o middleware inteiramente.

## Causa raiz

1. **Over-engineering**: middleware de auth foi implementado para proteger um site que já é acessível apenas via sidebar admin do Cadencia (gate `super_admin` já existe no app). O problema não existia.

2. **Env vars com `\n`/`\r\n` no Vercel**: todas as 4 env vars do cadencia-docs foram cadastradas com newline no final (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `CADENCIA_APP_URL`, `SUPABASE_PROJECT_REF`). Resultado: cada fetch ao Supabase usava URL malformada (`https://...supabase.co\n`) e falhava silenciosamente, redirecionando para login.

3. **`COOKIE_DOMAIN` com `\n` no cadencia-app**: o cookie de sessão era gravado com `domain=.cadencia.app.br\n`, que nunca casava com `docs.cadencia.app.br` — usuário logado no Cadencia não era reconhecido pelo middleware do docs.

4. **`Response.redirect()` no Vercel Edge cria headers imutáveis**: ao tentar adicionar `Set-Cookie` via `res.headers.set(...)` após um `Response.redirect()`, o header era silenciosamente descartado. Cookie `docs_session` nunca era gravado no browser — abordagem de token via URL não funcionou por esse motivo.

## Por que não foi detectado

- Nenhum `curl -I https://docs.cadencia.app.br` antes de considerar o middleware funcional.
- Env vars foram cadastradas sem usar `echo -n` — trailing newline não visível na UI do Vercel.
- `Response.redirect()` com `headers.set()` posterior compila sem erro — falha é silent.
- A pergunta "esse problema precisa ser resolvido?" nunca foi feita antes de implementar.

## Como foi corrigido

1. Constatado que o gate já existe no sidebar admin (apenas super_admin vê o link "Docs").
2. Removido `middleware.ts` do cadencia-docs completamente — commit `b087b31`.
3. `AppLayoutWrapper.tsx` restaurado para abrir `https://docs.cadencia.app.br` diretamente — PR #212.
4. Env vars corrigidas via `echo -n` no Vercel CLI (cadencia-docs e cadencia-app).
5. Force redeploy via `vercel deploy --prod --yes`.

## Prevenção

### Checklist / regras pra evitar recorrência

- [ ] Antes de implementar qualquer proteção de rota: perguntar "o gate já existe em outro layer?" (sidebar, route guard, etc.)
- [ ] Env var nova no Vercel: sempre `echo -n "valor" | vercel env add VAR env` — nunca `echo` com newline
- [ ] Após cadastrar env vars: rodar `vercel env pull` e inspecionar o arquivo — `\n` aparece explícito
- [ ] Smoke test obrigatório após mudança de middleware: `curl -sI https://subdominio.app.br | head -5`
- [ ] `Response.redirect()` no Vercel Edge → usar `new Response(null, {status:302, headers:{...}})` se precisar setar headers junto

### Pattern correto (Vercel Edge redirect com Set-Cookie)

```typescript
// ERRADO — headers imutáveis no Edge
const res = Response.redirect(url, 302);
res.headers.set("Set-Cookie", "...");  // silenciosamente ignorado

// CORRETO
return new Response(null, {
  status: 302,
  headers: {
    "Location": url,
    "Set-Cookie": "nome=valor; Path=/; HttpOnly; Secure; SameSite=Lax",
  },
});
```

### Pattern correto (env var Vercel sem newline)

```bash
# ERRADO — adiciona \n no final
echo ".cadencia.app.br" | vercel env add COOKIE_DOMAIN production

# CORRETO
echo -n ".cadencia.app.br" | vercel env add COOKIE_DOMAIN production

# VERIFICAR após cadastrar
vercel env pull /tmp/check.env && grep COOKIE_DOMAIN /tmp/check.env
```

### Regra atualizada em

- [x] Skill `/criar-site-protegido` (Passo 0 — verificar gate existente; Passo env vars — sempre `echo -n`)
- [ ] CLAUDE.md global (opcional — já coberto pela skill)

## Commits relacionados

- `b087b31` — cadencia-docs: remove middleware.ts completamente
- `cf91dc0` — cadencia-docs: middleware.ts desabilitado (passo intermediário)
- `4f841a1` — cadencia-app: AppLayoutWrapper volta para URL direta (PR #212)
- `1657f36` — cadencia-app: rota /api/app/admin/docs-token (criada e depois abandonada)
- `23695e0` — cadencia-app: proxy.ts trim() COOKIE_DOMAIN (PR #208)

## Links relacionados

- PR cadencia-app #212: restaura link direto para docs
- PR cadencia-docs #6/#7: tentativas de token auth (revertidas pela remoção do middleware)
- DEV-1485: issue Linear registrada para o fix de COOKIE_DOMAIN

---
*Registrado via sistema de incidentes. Ver INDEX.md para histórico completo.*
