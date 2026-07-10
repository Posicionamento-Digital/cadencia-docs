---
date: 2026-06-05
tags: [documentacao, skill, marketing, cortes, remotion, ia, automacao]
moc: "[[MOC-Projetos]]"
status: ativo
owner: Time Marketing
type: source
entities: ["[[PD Framework]]", "[[marketing]]", "[[meeting-transcriber]]", "[[qualidade]]"]
---
## Identidade

- **Tipo:** Skill PD Framework (pipeline de automação)
- **Stack:** Python 3.10+ · Remotion 4.0.443 · React 19 · WhisperX large-v3 · Claude CLI Sonnet 4.6
- **Path no repo:** `pd-framework/times/marketing/skills/criar-reel/`
- **Status:** Operacional · Validado end-to-end 2026-06-05
- **Acessível por:** Rafael (Social Media), Pedro (Tráfego), AP, Maria — todas personas do Time Marketing

## O que é

Skill mãe `/criar-reel` que orquestra pipeline de **edição automática de Reels/TikTok/Short** a partir de aulas/lives/podcasts longos. Recebe um vídeo bruto (ou transcrição), propõe N cortes não-sequenciais seguindo o arco PD em 5 estágios, deixa Felipe validar e escolher hooks, e renderiza MP4 final via Remotion (engine declarativa).

## Para que serve

Transformar **conteúdo longo gravado** (aula 2-3h, live 1-2h, podcast 1h) em **cortes verticais polidos de 60s/90s** sem trabalho manual em editor visual. Permite escala antes inviável:
- 1 aula → 8-15 cortes em ~3-5h (vs 1-2 dias no editor visual)
- Captions automáticas word-level
- Identidade visual PD preservada (cores, fontes, filete vertical)
- Transição glitch + SFX padronizada

## Como funciona

Pipeline em 4 etapas:

1. **Transcrição** (skill global `/transcrever-conteudo`) — WhisperX gera `transcricao.md` + `resumo.md` + `captions.json` (palavras com timing real)
2. **Proposta de cortes** (`propor_cortes.py` 2-passos paralelizado) — Claude lê transcrição + foundation editorial e propõe N temas; cada tema vira 1 corte com 5 estágios validados por 13 regras duras
3. **Seleção de Hook** (sub-skill `/selecionar-hook`) — agente especializado propõe 2 trechos candidatos a Hook (3-5s, tipos diferentes); Felipe escolhe A ou B
4. **Render** (`orchestrate_cortes.py` + Remotion) — ffmpeg pré-extrai 5 trechos pequenos; Remotion compõe via JSON declarativo (CorteSpec) e gera MP4 final

## Quickstart

```bash
# Transcrição (1x por aula, ~30min-2h)
"C:\Venvs\meeting-transcriber\Scripts\python.exe" \
  "C:\Users\felip\.claude\skills\transcrever-conteudo\build_content_notes.py" \
  --files "<MP4>" --tipo aula --titulo "<título>" --serie "<curso>" --numero N

# Propor corte único direto (mais rápido pra começar)
"C:\Venvs\meeting-transcriber\Scripts\python.exe" \
  "<framework>\times\marketing\skills\criar-reel\scripts\propor_cortes.py" direto \
  --transcricao "<...>\transcricao.md" \
  --resumo "<...>\resumo.md" \
  --tema "<tema do corte>" \
  --tipo-hook Controversa --editoria CONFRONTAR --duracao 60
```

## Quando usar

- Cortar Reels/Shorts de aulas, lives, podcasts, palestras gravadas
- Material com Felipe falando (mono) ou + 1 convidado
- Necessidade de escala (N cortes da mesma fonte)
- Quando a qualidade "rascunho/draft" é aceitável pra publicação OU quando vai virar input pra edição manual fina

## Quando NÃO usar

- Reel original autoral planejado scene-a-scene (use formato `tela-dividida` da mesma skill, ou edição visual)
- Vídeos curtos (<10min) — pipeline tem overhead
- Quando ferramentas reais (Premiere, DaVinci, CapCut) são necessárias pra qualidade premium (1-2 cortes finalistas que vão pro ar)

## Decisões (ADRs)

- **Skill mãe no nível Time Marketing** (não Squad Social Media) — ferramenta compartilhada por múltiplas personas
- **2-passos paralelizado** no propor_cortes.py — resolve timeout Claude CLI
- **Schema multi-source** (`fonteVideo` aceita string OU array) — aulas em N arquivos sem concat
- **Pré-extração ffmpeg** antes do Remotion — resolve seek em MP4 Sony XAVC sem faststart
- **Word-level captions** em `captions.json` separado — transcricao.md mantém compat por parágrafo
- **Outputs em `OneDrive\Videos\Cortes\`** — drive estável, D: pode desconectar

## Don'ts

- Nunca passar MP4 grande direto pro Remotion sem faststart — pré-extrair trechos
- Nunca usar `<Audio>` sem `<Sequence from={frame}>` — não dispara no momento certo
- Nunca confiar em timestamps do `transcricao.md` pra cortes precisos — usar `captions.json`
- Nunca passar `--props` sem wrapper `{ "spec": {...} }` — componente lê `props.spec`
- Nunca usar `src/Root.tsx` como entry point Remotion — precisa `src/index.ts`

## Troubleshooting

- **Vídeo final só com tela azul** → `--props` não foi lido. Verificar wrapper `{spec: ...}` no JSON.
- **`delayRender Fetching timed out`** → seek inviável em MP4 grande. Pré-extrair trechos.
- **Legendas dessincronizadas** → `captions.json` não foi gerado. Conferir `build_content_notes.py` rodou `transcribe_word_level()`.
- **Glitch invisível** → componente já reforçado (flash + bandas + scanlines). Se persistir, aumentar `durationFrames`.
- **SFX não toca** → envolver `<Audio>` em `<Sequence from={frame}>`. Já corrigido em `CorteVideo.tsx`.
- **Claude CLI timeout** → reduzir foundation no Passo 2 (`FOUNDATION_FILES_STAGE`); aumentar `--retry`.

## Histórico

- **2026-06-05** — Pipeline criado e validado. Aula 01 (Como Criar Harness Claude Code, 2h49m) transcrita word-level. 2 cortes 60s renderizados: TDAH (WOW/EXISTIR) + N8n (Controversa/CONFRONTAR). Qualidade aprovada pelo Felipe.

## Notas Relacionadas

[[Cursos/Claude Code/Aula 01 - Como Criar Harness Claude Code/transcricao]] · [[2026-06-05 Remotion edicao declarativa JSON]] · [[MOC-Projetos]] · [[MOC-Marketing]]
