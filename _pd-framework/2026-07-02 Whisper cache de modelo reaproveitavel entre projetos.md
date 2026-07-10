---
date: 2026-07-02
tags: [ia, tecnologia, automacao, aprendizado]
moc: "[[MOC-IA-Tecnologia]]"
type: source
entities: ["[[meeting-transcriber]]"]
---

## Contexto

Fork de [savbell/whisper-writer](https://github.com/savbell/whisper-writer) para montar ditado por voz em tempo real (hotkey -> grava -> transcreve com Whisper local -> digita direto no cursor ativo, equivalente ao ditado por voz nativo do Windows). Fork em `github.com/felipeluissalgueiro/whisper-writer`, clonado em `C:\dev\whisper-writer`.

## O que foi discutido

Ao planejar o setup, a duvida era se dava pra reaproveitar o que ja existe do [[meeting-transcriber]] (pipeline de transcricao de reunioes ja em producao, Whisper local via WhisperX + pyannote).

### Cache de modelo e global, nao por projeto

O modelo `faster-whisper large-v3` (~2.9GB) ja estava baixado em `~/.cache/huggingface/hub/models--Systran--faster-whisper-large-v3` por causa do meeting-transcriber. Esse cache do Hugging Face vive por **usuario**, nao por projeto — qualquer outro projeto Python que use a mesma lib (`faster-whisper`) e aponte pro mesmo model id reaproveita automaticamente, sem novo download.

### Venv nao e reaproveitavel

Ja o ambiente Python (venv) precisa ser proprio por projeto, mesmo usando o "mesmo" Whisper por baixo dos panos:

- **meeting-transcriber**: `WhisperX` + `torch 2.8.0+cu128`, venv em `C:\Venvs\meeting-transcriber`
- **whisper-writer**: `faster-whisper==1.0.2` puro + `ctranslate2==4.2.1`, precisa de venv proprio

Sao versoes de dependencia incompativeis entre si — misturar no mesmo venv quebra um dos dois. A confusao natural e achar que "mesmo modelo" implica "mesmo ambiente", mas sao camadas diferentes: o modelo (pesos, arquivo binario) e generico e cacheavel; o ambiente (codigo + libs) e especifico de cada projeto.

### Diferenca de proposito entre os dois projetos

Apesar de convergirem no mesmo backend (`faster-whisper`), tem objetivos distintos:

- **meeting-transcriber**: pipeline pos-gravacao, com diarizacao (pyannote identifica quem fala), gera nota estruturada no Obsidian.
- **whisper-writer**: ditado ao vivo, sem diarizacao, escreve direto no campo de texto ativo via hotkey.

## Decisoes e Conclusoes

- Antes de configurar qualquer projeto novo que use Whisper/faster-whisper localmente, checar primeiro `~/.cache/huggingface/hub/` antes de assumir que precisa baixar o modelo de novo.
- Sempre criar venv proprio por projeto, mesmo quando o modelo de IA por baixo e compartilhavel.

## Proximos Passos

- Criar venv proprio em `C:\Venvs\whisper-writer`
- Instalar dependencias (corrigir encoding UTF-16 quebrado do `requirements.txt` do fork)
- Configurar `config.yaml` apontando pro modelo em cache
- Testar hotkey + digitacao no cursor ativo

## Notas Relacionadas

[[meeting-transcriber]]
