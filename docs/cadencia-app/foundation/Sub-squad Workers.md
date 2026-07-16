# Sub-squad Workers

Responsável pelos workers FastAPI no Coolify VPS Master: onboarding, dossier,
identidade visual, editoriais, ideias, carrossel, reels e publicação Instagram.

## Regras

- Pipeline de carrossel/reels tem 7 steps observáveis.
- Jobs longos são assíncronos e idempotentes.
- Todo acesso Supabase filtra `tenant_id`.
- Assets e prompts pertencem ao tenant correto.
- Deploy é Coolify; Railway permanece apenas em ADR histórico.
