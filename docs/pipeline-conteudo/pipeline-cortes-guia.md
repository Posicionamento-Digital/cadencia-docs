---
date: 2026-06-05
tags: [guia, skill, marketing, cortes, uso, instrucoes]
moc: "[[MOC-Projetos]]"
status: ativo
type: source
entities: ["[[marketing]]", "[[qualidade]]"]
---
## Quando usar este guia

Você gravou uma aula/live/podcast e quer transformar em cortes Reels/TikTok/Short de 60s, ou já tem transcrição feita e quer cortes específicos. Este guia mostra como invocar o pipeline `/criar-reel` no chat com Claude Code.

---

## Cenário 1 — Aula nova gravada

**No chat:**

> "Tenho uma aula nova em `D:\Videos\Aulas\<pasta>\C5811.MP4`. Transcreve e me dá 5 cortes."

**Claude vai:**
1. Rodar `/transcrever-conteudo` em background (30min–2h dependendo da duração)
2. Quando voltar, mostrar TL;DR + chapter markers + insights
3. Rodar `propor_cortes.py scout --num-cortes 5` → listar 5 temas
4. Você escolhe quais aprovar
5. Pra cada aprovado: invoca `/selecionar-hook` (2 candidatos) — você escolhe A ou B
6. Render Remotion → MP4s prontos em `OneDrive\Videos\Cortes\<contexto>\`

**Tempo total:** 1–3h (a maior parte em background — você pode trabalhar em outra coisa)

---

## Cenário 2 — Transcrição já existe, quer cortes específicos

> "Da aula 01 do Claude Code, quero 3 cortes: um sobre N8n, um sobre MCP vs API, e um sobre 'harness é gambiarra'."

**Claude vai:** rodar `propor_cortes.py direto` 1x pra cada tema com `--tema "..."` (faz mini-scout achando timestamp real automaticamente). Cada corte sai em 2–3min.

---

## Cenário 3 — Já tem cortes propostos, só renderizar

> "Renderiza o corte #3 do scout que rodamos ontem com hook B."

**Claude vai:** ler `OneDrive\Videos\Cortes\<contexto>\scout.json` + `orchestrate_cortes.py` → render.

---

## Estado atual da automação

| Etapa | Status |
|---|---|
| Transcrição (WhisperX + word-level captions) | ✅ Automatizado (skill global `/transcrever-conteudo`) |
| Propor cortes (Claude + 13 regras duras) | ✅ Automatizado (`propor_cortes.py` 3 modos) |
| Selecionar Hook (2 candidatos por corte) | ✅ Automatizado (skill `/selecionar-hook`) |
| Decisão de aprovar cortes + escolher hook | ⏳ Você escolhe no chat — Claude pergunta |
| Pré-extração ffmpeg + render Remotion | ⚠️ Funciona via script, mas Claude precisa invocar manualmente (orchestrate sem modo interativo no chat ainda) |
| Output em `OneDrive\Videos\Cortes\<contexto>\` | ✅ Padronizado |

---

## Frases que ativam cada skill

| Você diz | Claude invoca |
|---|---|
| "Transcreve essa aula/live/podcast" | `/transcrever-conteudo` |
| "Cria um reel disso" / "monta um corte sobre X" | `/criar-reel` |
| "Quais hooks dá pra fazer dessa aula?" | `/selecionar-hook` ou modo `scout` |
| "Renderiza esse corte" | `orchestrate_cortes` |

Claude identifica pelo contexto e invoca as skills certas.

---

## Tempo real esperado (referência: aula 01 = 2h49m)

| Tarefa | Tempo |
|---|---|
| Transcrição WhisperX large-v3 (GPU CUDA) | 30–60min |
| Word-level captions (CPU fallback) | 30–90min |
| Scout de 5 temas | ~1min |
| Detalhar 1 corte | ~2–3min |
| `/selecionar-hook` por corte | ~1–2min (com retry) |
| Pré-extração ffmpeg dos 5 trechos | ~10s |
| Render Remotion 60s | ~1–2min |
| **Total pra 1 corte (transcrição já existe)** | **~5–10min** |
| **Total aula nova → 5 cortes** | **~2–4h (background)** |

---

## O que sai como output

Pra cada corte renderizado:

- **MP4 final** em `OneDrive\Videos\Cortes\<aula-slug>\corte-NN-<tema-slug>.mp4`
  - 1080×1920 (9:16 vertical)
  - 60s ou 90s
  - Captions word-level com palavra ativa destacada (amarelo `#FFEB00`)
  - Glitch + SFX na transição Hook → Desenvolvimento
- **CorteSpec JSON** em `OneDrive\Videos\Cortes\<aula-slug>\specs\<corte>.json` — editável manualmente pra ajustes finos
- **Nota `cortes-gerados.md`** no Obsidian (Time PD/Cursos/...) — histórico

---

## Quando NÃO usar o pipeline

- Reel original autoral planejado scene-a-scene (use editor visual ou formato `tela-dividida` da skill)
- Vídeos curtos (<10min) — pipeline tem overhead
- Quando precisa de qualidade premium pra cliente final (1–2 cortes finalistas) — pegue o MP4 do pipeline como base e refine no Premiere/DaVinci/CapCut

---

## Pra simplificar ainda mais (próxima evolução)

Pendências que vão melhorar o fluxo (documentadas no README do framework):

- Skill mãe `/criar-reel` automatizar fluxo no chat inteiro (você diz "transcreve e me dá cortes", tudo roda end-to-end sem comandos intermediários)
- `orchestrate_cortes.py` modo interativo (perguntar aprovações no chat)
- Suporte a URL YouTube como input
- `/selecionar-hook` consultar `captions.json` direto pra timestamps mais precisos

Mas o fluxo do **Cenário 1** já funciona hoje — basta pedir e Claude coordena os passos.

---

## Refs

[[criar-reel]] · [[Cursos/Claude Code/Aula 01 - Como Criar Harness Claude Code/transcricao]] · [[MOC-Projetos]] · [[MOC-Marketing]]
