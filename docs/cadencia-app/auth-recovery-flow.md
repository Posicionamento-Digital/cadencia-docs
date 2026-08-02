# Auth — Fluxo de reset de senha (recovery)

> DEV-1684 · fix em prod desde 2026-08-02 (merge commit `3aa514a`).

## O que é

Fluxo de "esqueci a senha" do Cadencia. Baseado em OTP token do Supabase Auth entregue por email; o app precisa distinguir `type=recovery` dos outros tipos de OTP (`signup`, `magiclink`, `email_change`, `invite`) porque cada um vai pra tela diferente após o `verifyOtp`.

## Fluxo

```
Cliente clica "Esqueci a senha" em /auth/login
         │
         ▼
POST forgot-password → Supabase envia email
         │
         ▼
Cliente clica no link do email
         │
         ▼
GET /auth/confirm?token_hash=X&type=recovery
         │
         ├─► verifyOtp({type:"recovery", token_hash})
         │        │
         │        ├── ERROR → /auth/error?error=...&type=recovery
         │        │
         │        └── OK (sessão de recovery criada)
         │
         ├─► if (!user) → /auth/error
         │
         ├─► if (type === "recovery") → /auth/update-password  ← BRANCH DO FIX DEV-1684
         │
         └─► fallback (signup/magiclink/etc): provisionTenantIfNeeded + /auth/login
```

## Componentes

| Arquivo | Papel |
|---|---|
| `src/app/auth/login/page.tsx` | Tela de login com link "Esqueci a senha" (usa `src/app/auth/forgot-password/`) |
| `src/app/auth/forgot-password/` | Formulário que dispara `supabase.auth.resetPasswordForEmail(email)` |
| `src/app/auth/confirm/route.ts` | **Handler crítico** — recebe OTP do email e roteia por `type` |
| `src/app/auth/update-password/page.tsx` | Formulário onde cliente digita a senha nova (com sessão de recovery já ativa) |
| `src/app/auth/error/page.tsx` | Tela de erro amigável (com fallback pra tentar de novo) |
| `src/app/auth/confirm/route.contract.test.ts` | Contract test que trava o comportamento — regex garante que branch `type === "recovery"` continue existindo e venha antes do provisioning |

## Por que branch condicional é obrigatório

Sem o `if (type === "recovery")`, todos os OTPs caem no fluxo padrão que chama `provisionTenantIfNeeded` + redireciona pra `/auth/login`. Recovery é conta ATIVA — user já existe, já tem tenant, não faz sentido rodar provisioning. E mais grave: o redirect pra `/auth/login` faz o cliente pensar que precisa logar de novo, quando na verdade a sessão de recovery só serve pra `/auth/update-password`.

Foi exatamente o bug relatado pela cliente Ariane Farrapo em 2026-07-31 — ela contornou logando por Google (identity dupla). Outros clientes que só usam senha ficavam presos.

## 🚫 Don'ts

- **Nunca reordenar** o branch `if (type === "recovery")` pra depois do `provisionTenantIfNeeded`. Provisioning pode demorar/falhar e recovery é fluxo curto/leve — o cliente já está esperando digitar senha nova.
- **Nunca remover** o contract test `route.contract.test.ts`. Ele existe pra travar esse gotcha específico — sem ele, refactor futuro pode regredir silenciosamente (foi o que aconteceu no bug original).
- **Nunca redirect pra `/auth/login`** quando `type === "recovery"`, mesmo com msg "Email confirmado!". Cliente não quer logar, quer trocar a senha.

## 🔥 Troubleshooting

| Sintoma | Causa | Fix |
|---|---|---|
| Cliente clica no email de reset → cai em `/auth/login` sem tela de senha nova | Regressão do fix DEV-1684 (branch condicional foi removido/reordenado) | Rodar `npx vitest run src/app/auth/confirm/route.contract.test.ts` — vai vermelho apontando qual regra quebrou |
| `/auth/error?error=Email+link+is+invalid+or+has+expired` | Token de recovery expirou (Supabase invalida em ~60min por default) ou já foi usado | Cliente pede novo reset em `/auth/login` |
| Cliente digita senha em `/auth/update-password` mas dá erro "session missing" | Sessão de recovery não foi persistida (cookie de recovery é curto) | Verificar `src/lib/supabase/server.ts` — cookie handling do @supabase/ssr |

## Critério de aceite validado (DEV-1684)

- ✅ `/auth/confirm?token_hash=<X>&type=recovery` redireciona pra `/auth/update-password`
- ✅ Sessão de recovery permanece válida — user POSTa senha nova em `/auth/update-password`
- ✅ Fluxos `signup`, `magiclink`, `email_change`, `invite` mantêm comportamento anterior (regressão zero)
- ✅ Contract test 3/3 PASS
- ✅ Smoke prod: `type=recovery` com token inválido → 307 pra `/auth/error` preservando `type` (comportamento esperado: verifyOtp rejeita token antes do branch de recovery ser avaliado)

## 📚 Referências

- Issue: [DEV-1684](https://linear.app/cadencia/issue/DEV-1684)
- PR: [#281](https://github.com/felipeluissalgueiro/cadencia-app/pull/281) merge commit `3aa514a`
- Cliente afetada relatou: Ariane Farrapo (tenant `b3081636`) em 2026-07-31
- Gotcha original documentado no CLAUDE.md do squad Cadência desde 2026-06-11 (nunca corrigido até DEV-1684)
- Docs Supabase Auth: [verifyOtp](https://supabase.com/docs/reference/javascript/auth-verifyotp)

## Histórico

- **2026-08-02** — Fix aplicado em prod (commit `3aa514a`, PR #281). Contract test criado.
- **2026-07-31** — Bug reportado pela cliente Ariane Farrapo.
- **2026-06-11** — Gotcha documentado no CLAUDE.md do squad Cadência (não corrigido).
