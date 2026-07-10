---
date: 2026-06-26
tags: [ia, tecnologia, framework, llm, arquitetura, agnostico]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework Agnóstico — core, contrato e adapters

> Doc de arquitetura derivado dos insights de 19/06. Espelho do doc canônico no repo: `pd-framework/_core/FRAMEWORK-AGNOSTIC-ARCHITECTURE.md` (+ `_core/RUNTIME-CONTRACT.md`).

## Insight central

Parar de perguntar **"como porto o framework pro Codex?"** e passar a **"como faço qualquer runtime implementar o contrato do framework?"**. Quando o contrato é explícito, Claude Code / Codex / Cursor / Gemini / harness próprio viram apenas **clientes** de uma plataforma maior — nenhum é o centro.

Não é só Codex. Agnóstico em **três eixos**:
- **Modelo** (Opus, GPT, Gemini, Qwen, local)
- **Harness / runtime** (Claude Code, Codex, Cursor, Gemini CLI, harness próprio do Felipe)
- **Provider** (Anthropic, OpenAI, Google, self-hosted)

## Tese

**Framework agnóstico = core estável + contrato explícito + adapters finos.**

Regra-mãe de fronteira: se uma convenção depende de produto específico (`CLAUDE.md`, `.claude/settings.json`, slash command, hook de fornecedor), ela mora no **adapter** — nunca no core.

## Três camadas

1. **Core agnóstico** — conteúdo de squads, `STATE.md`, `decisions.md`, memória, `_core/lookup.py`/`state-aggregator.py`, `_shared/*.py`, políticas (Constitution/Hierarchy/Security/memory-schema). Markdown + Python determinístico, não conhece Claude Code.
2. **Runtime contract** — 8 capacidades obrigatórias (load_context, detect_active_squad, open/close_session, protect_main, record_memory, invoke_skill, knowledge_lookup) + 1 opcional (resolve_issue). Especificação, não código.
3. **Adapters por runtime** — o acoplamento isolado. Descoberta-chave: **os 10 hooks de `_core/hooks/` já são o adapter Claude Code do contrato** — só não foram nomeados assim.

## Ambição aninhada

- **(a)** Agnostizar *o* pd-framework — trabalho interno, MVP.
- **(b)** Produto "tradutor universal de frameworks para LLMs": scanner → contrato canônico → geração de adapters multi-runtime + sync contínuo. Posicionamento: *"Seu framework já existe. Nós o tornamos legível e operável por qualquer agente."* A (a) é o dogfooding da (b).

## Notas-fonte (vault Pessoal)

- `IA-Tecnologia/2026-06-19 Ideia - sistema agnóstico para IAs` — semente
- `IA-Tecnologia/2026-06-19 Framework agnostico para LLMs - core, contrato e adapters` — tese
- `IA-Tecnologia/2026-06-19 Ideia de produto - tradutor universal de frameworks para LLMs` — produto

## Relacionadas

- [[IA-Tecnologia/2026-05-24 PD Framework — Arquitetura completa e mapeamento de stack]]
