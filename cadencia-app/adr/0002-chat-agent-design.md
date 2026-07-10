> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/adr/0002-chat-agent-design.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0002-chat-agent-design.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# ADR-0002 — Design do chat agent "Tenho uma ideia"

**Status:** aceito · **Data:** 2026-05-27 (retroativo — feature em produção desde ~PDL-92)

## Contexto

A geração automática de ideias (`ideas-generator`) entrega cadência, mas tira voz do usuário. Por outro lado, brief manual cego não escala. Precisávamos de um meio-termo: usuário sugere/refina ideia em diálogo, com a IA falando como a marca dele.

## Decisão

Chat conversacional com 3 ingredientes:

1. **SOUL.md por tenant** — gerado no onboarding pelo `dossier.py` via `provision_soul_md`. Contém voz, valores, restrições, exemplos de tom. É o que faz o agente "soar como a marca".
2. **Memória de sessão** — `chat_agent/memory.py` + `session.py`. Persiste contexto da conversa.
3. **Feature flag `flag_chat_ideas`** — controle por tenant (rollout controlado).

Aprovação de ideia: `POST /api/app/ideas/from-chat` cria registro em `content_ideas` que dispara pipeline normal.

## Consequências

- ✅ Usuário sente que está "conversando com a marca dele" — fit muito maior do que ideias geradas frias.
- ✅ SOUL.md reaproveitável — mesmo formato vai para outros agentes (futuramente).
- ✅ Memória persistente permite continuar conversa em outra sessão.
- ❌ Onboarding precisa rodar `provision_soul_md` corretamente — sem SOUL, chat genérico.
- ❌ Custo LLM por mensagem (não é só ideia gerada — toda interação).
- ⚠️ Feature flag por tenant exige toggle manual ou regra de release.

## Não considerado

- Chat genérico sem SOUL — testou em piloto, tom corporativo soltava marca.
- Substituir `ideas-generator` — eles coexistem (chat = interativo, generator = programado).
