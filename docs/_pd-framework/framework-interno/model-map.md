---
date: 2026-07-03
tags: [doc, componente, pd-framework, documentacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[PD Framework]]"]
---

# MODEL-MAP — modelos por harness (D2)

## Identidade
- **Tipo:** dado declarativo + lib/CLI + 2 hooks (core)
- **Stack:** JSON + Python 3.12, zero deps
- **Path:** `_core/MODEL-MAP.json` · `_core/model_map.py` · hooks `sessionstart-model-map.py` / `pretooluse-paid-api-guard.py`
- **Issues:** epic DEV-1112 (stories DEV-1113…1116)
- **Status:** ativo

## O que é
"Qual modelo usar, onde, e quem paga" — declarativo e **segmentado por harness com regime de cobrança** (dimensão que o ruflo não tem). Claude Code e Codex = assinatura; OpenCode = API paga por design.

## Como funciona
1. **Mapa:** 3 blocos com tiers ("quando usar" por tier), exceções (skills de review autorizadas a gastar API dentro de assinatura) e bloco `learning` reservado.
2. **Injeção:** ao abrir a sessão, o adapter injeta SÓ o bloco do harness ativo (hook neutro fiado nos 3 adapters).
3. **Enforcement:** guard PreToolUse bloqueia endpoint de LLM pago + invocador HTTP em assinatura (`permissionDecision: deny`); skill autorizada passa com `PD_PAID_API_SKILL=<skill>` no comando.
4. **Dataset:** `learning` agrega outcomes por (harness, model) — pronto pro bandit futuro, que fica gated no volume.

## Quickstart
```bash
python _core/model_map.py show --runtime claude-code
python _core/model_map.py check --runtime claude-code --paid-api --skill openrouter-review
python _core/model_map.py learning
```

## Decisões
Regime de cobrança como atributo de 1ª classe · guard de custo fail-open (≠ barras de segurança fail-closed) · bandit adiado (sinal antes de mecanismo) · sem classificador heurístico (o agente lê o bloco e decide).

## Don'ts
- Nunca hardcodar preço por modelo no código — o mapa é o lugar, e `amount` real só vem do runtime que reporta.
- Nunca chamar OpenRouter/API paga em skill nova dentro de assinatura sem adicionar a skill às `exceptions` (decisão registrada).

## Troubleshooting
- **Guard bloqueou trabalho legítimo** → rodar via skill autorizada com o marcador, ou usar OpenCode.
- **Bloco não aparece na sessão** → Claude: SessionStart no settings vale a partir da PRÓXIMA sessão; OpenCode: handler `modelmap.ts` ainda não exercitado ao vivo (validar na próxima abertura).

## Histórico
- 2026-07-03 — epic completo: f1a589f (mapa+loader) · 228132c (injeção 3 adapters) · 565f052 (guard — bloqueou o próprio teste ao vivo no Claude) · 51eb0e9 (dataset) · 6d06bef (docs)

## Notas Relacionadas
[[outcomes-cost]] · [[memory-engine]] · repo: `_core/docs/model-map.md` · manual §10.4
