# Hardening auth cross-runtime — Cadencia + PD Framework (OPS-75)

> Como o loop de refresh_token que tirou o Cadencia do ar por 17h em 22-23/07/2026 virou padrão enforçável em **todos os 3 runtimes de agente** que operamos (Claude Code, Codex, OpenCode).

**Escopo:** proteção de auth Supabase no browser + processo de reação a debug de auth em qualquer harness.

**Origem:** [Incidente 2026-07-22 — Cadencia loop client-side de refresh_token](../cadencia-app/index.md#incidentes-relacionados).

---

## O que aconteceu (30s)

Em 22-23/07/2026 o Cadencia teve loop client-side de `refresh_token_not_found` que expulsava usuários em qualquer clique. Três PRs sequenciais atacaram o problema no server (middleware, cookies, twin), sem sucesso — porque a causa era 100% cliente: o SDK Supabase detectava erro terminal, emitia `SIGNED_OUT` corretamente, mas o app **não tinha ninguém escutando o evento**. Cada componente que montava dispara nova tentativa de refresh → loop reinicia.

Correção do bug: PR #219 + #220 (singleton client + hook `useSessionGuard` + guard SSR + tipo `SupabaseClient` direto).

Correção do processo (esta doc): **6 mecanismos determinísticos** que impedem a regra de virar bug de novo.

## As 4 regras invioláveis do @supabase/ssr no browser (fonte única)

Formalização completa em `times/produto/cadencia/foundation/supabase-auth-conventions.md`:

1. **`createClient()` do browser É singleton module-level.** Sem singleton, `usePipelineStatus` cria nova instância a cada tick de polling (3s) — dezenas de clients disputam o lock global, amplificam erro de token para ~30 req/s.
2. **Guard SSR obrigatório.** Singleton em module scope persiste entre requests em Vercel serverless → importar `client.ts` do server acidentalmente vira session leak entre users. Guard: `if (typeof window === "undefined") throw`.
3. **Tipo `SupabaseClient` direto, NÃO `ReturnType<typeof createBrowserClient>`.** `createBrowserClient` tem 2 overloads — `ReturnType` pega o deprecated e colapsa o generic `Database`, quebra inferência em consumers. Foi o motivo do hotfix #220.
4. **Listener global de `onAuthStateChange` escutando `SIGNED_OUT`.** SDK Supabase emite o evento após `_removeSession()` (source: `auth-js:3888-3984`). Sem app escutando + redirecionando, o loop reinicia infinitamente.

## Os 6 mecanismos que enforçam

| # | Mecanismo | Onde vive | O que garante |
|---|---|---|---|
| 1 | `client.contract.test.ts` (5 asserts) | `cadencia-app/src/lib/supabase/` | Regressão do singleton + guard SSR + tipo → `npm test` FAIL vermelho |
| 2 | `useSessionGuard.contract.test.ts` (6 asserts) | `cadencia-app/src/hooks/` | Regressão do listener global de SIGNED_OUT → FAIL vermelho |
| 3 | Hook `userprompt-auth-debug-check.py` | `pd-framework/_core/hooks/` | Quando prompt contém keyword de auth debug, injeta protocolo obrigatório (query em `auth.refresh_tokens` + `auth.sessions` ANTES de propor código) |
| 4 | Foundation doc `supabase-auth-conventions.md` | `pd-framework/times/produto/cadencia/foundation/` | POR QUÊ das regras + pattern correto + anti-patterns — carregado sob demanda (não infla CLAUDE.md) |
| 5 | Skill `/aprovar-pr` §4.4 | `~/.claude/skills/aprovar-pr/SKILL.md` | Build local (`next build`) **NÃO PODE ser pulado** em PR que toca `src/lib/supabase/*`, `src/middleware.ts`, `src/hooks/useSessionGuard.ts`, `**/rls/**` — mesmo em hotfix |
| 6 | Skill `/claude-review` | `~/.claude/skills/claude-review/SKILL.md` | Achado P3 sobre tipos/generics em código de auth é reclassificado para P2 automaticamente (evita repetir o hotfix #220) |

## Como propaga em qualquer harness — Runtime Contract cross-runtime

O `_core/RUNTIME-CONTRACT.md` ganhou uma seção nova:

> **Regra transversal — cobertura cross-runtime obrigatória (OPS-75).** Todo novo mecanismo de enforcement/reminder criado no framework (hook, skill, handler) **DEVE ser espelhado em TODOS os adapters ativos** antes de ser considerado entregue.

### Como cada classe de mecanismo espelha nos 3 adapters

| Classe | Claude Code (#1) | Codex (#3) | OpenCode (#2) |
|---|---|---|---|
| Hook UserPromptSubmit | Registrar em `.claude/settings.json` | Chamar em `adapters/codex/userpromptsubmit.py` (shell-out pra `_core/hooks/`) | Handler em `.opencode/plugins/pd-adapter/handlers/` (mesmo shell-out) |
| Hook PreToolUse/PostToolUse | Idem settings.json | `adapters/codex/pretooluse.py` / `posttooluse.py` | `tool.execute.before` / `after` no plugin |
| Skill nova | `stamper/skills/<name>/SKILL.md` | `sync_skills.py` gera `.agents/skills/<name>/` | `.opencode/agents/<name>.md` (copiado do SKILL.md) |
| Foundation doc / regra em texto | 1 fonte única, todos leem via cascata | Idem via `AGENTS.md` MIRROR | Idem via `AGENTS.md`+`instructions` |
| Contract test / lint gate | `npm test` — agnóstico total | Idem | Idem |

### Checklist obrigatório em PR de mecanismo novo

- [ ] Cobertura Claude Code (#1) confirmada?
- [ ] Cobertura Codex (#3) confirmada? Se não, por quê?
- [ ] Cobertura OpenCode (#2) confirmada? Se não, por quê?
- [ ] Se algum adapter foi omitido: registrar sub-issue com prazo.

## Validação end-to-end (23/07/2026)

- **Codex `exec`** com prompt "usuario deslogou em loop de refresh_token no cadencia" → agente **leu o foundation doc**, seguiu o protocolo, pediu email do user pra queriar `auth.refresh_tokens`. Evidência: hook `_auth_debug_check` do shim disparou.
- **Claude Code** — hook registrado no `.claude/settings.json` como 5º UserPromptSubmit. Testado standalone com match + no-match.
- **OpenCode** — handler `reminders.ts` segue o mesmo padrão isomórfico do `knowledge.ts` (validado em runtime DEV-885). Shell-out equivalente testado direto: `node → spawn python _core/hooks/userprompt-auth-debug-check.py` retorna 1435 bytes com `PROTOCOLO`.

## Como testar você mesmo

### Claude Code
Abrir nova sessão em qualquer projeto do framework. Digitar: `"tem um loop de refresh_token no cadencia, o que fazer?"`. Deve aparecer `<system-reminder>` com o protocolo obrigatório de query no banco.

### Codex
```bash
cd C:/dev/pd-framework
codex exec --skip-git-repo-check "loop de refresh_token no cadencia"
```
Agente deve pedir o email do user afetado e referenciar `foundation/supabase-auth-conventions.md`.

### OpenCode
Abrir OpenCode com provider configurado no `opencode.json`. Enviar prompt equivalente. Handler `reminders.ts` injeta o mesmo protocolo via `chat.system.transform`.

## Impacto esperado (~90 min de setup vs. 17h da próxima crise)

- Cliente com storage envenenado **não precisa mais fazer "Clear site data" manual** — hook `useSessionGuard` limpa sozinho no primeiro `SIGNED_OUT`.
- Regressão do padrão de singleton/tipo em `client.ts` **quebra o build** (Vercel Preview + `npm test`), nunca chega em produção.
- Debug de auth futuro **começa pela query no banco**, não por chute — hook injeta o protocolo automaticamente em qualquer harness.

## Referências

- Foundation (fonte única): `pd-framework/times/produto/cadencia/foundation/supabase-auth-conventions.md`
- Incidente completo: `pd-framework/incidents/2026-07-22_cadencia-loop-refresh-token-client-side.md`
- Runtime Contract: `pd-framework/_core/RUNTIME-CONTRACT.md` §"Regra transversal — cobertura cross-runtime obrigatória"
- Arquitetura 3-camadas: `pd-framework/manual/09-runtimes-e-adapters.md`
- Issues: [DEV-1505](https://linear.app/cadencia/issue/DEV-1505/) (fix aplicado) · [OPS-75](https://linear.app/cadencia/issue/OPS-75/) (hardening)
- SDK verificado: `@supabase/auth-js/dist/main/GoTrueClient.js:3888-3984`
