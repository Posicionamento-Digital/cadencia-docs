---
type: source
source_kind: incidente
date: 2026-06-30
entities: ["[[meeting-transcriber]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-06-30_meeting-transcriber-onedrive-desidratado

# Incidente: meeting-transcriber desidratado pelo OneDrive — skill de transcrição quebrou

**Data:** 30/06/2026
**Severidade:** Média (quebrou `/obsidian-transcrever-reuniao`; workaround em ~10 min)
**Projeto:** meeting-transcriber / Infra (OneDrive Files On-Demand)
**Tags:** `#onedrive` `#files-on-demand` `#path` `#skill` `#dev-865`

## O que aconteceu

A skill `/obsidian-transcrever-reuniao` falhou ao transcrever uma call de vendas. O `transcriber.bat` no path apontado pela skill (`...\OneDrive\Documentos\ClaudeCode\Hub Projetos\meeting-transcriber\transcriber.bat`) retornou *"is not recognized as a name of a cmdlet, function, script file, or executable program"*.

Investigando, o projeto inteiro estava **desidratado**: as subpastas (`src`, `skills`, `.git`, etc.) existiam como **ReparsePoint** (placeholders OneDrive), mas vinham **vazias** ao listar — `src` só com `__pycache__`, `.git` não-materializado (`git` retornava *"not a git repository"*). `attrib` retornava *"arquivo não encontrado"*.

## Causa raiz

O **OneDrive Files On-Demand descarregou (dehydrate) o projeto inteiro** — moveu o conteúdo pra nuvem e deixou só as pastas-casca no disco. Provável gatilho: política "liberar espaço" sobre um projeto raramente aberto no Explorer. Forçar re-hidratação via CLI (`attrib +P /S /D`) **não recuperou** os arquivos.

Mesmo padrão do incidente **DEV-865** (OneDrive corrompendo/desidratando conteúdo dentro de `Hub Projetos/`).

## Como foi corrigido

1. Confirmado que o projeto é repo no GitHub (`felipeluissalgueiro/meeting-transcriber`, privado).
2. **Re-clonado fora do OneDrive:** `git clone ... C:\dev\meeting-transcriber`. O venv (`C:\Venvs\meeting-transcriber`, WhisperX/CUDA) já era externo ao OneDrive e estava intacto. `transcriber.bat` usa path absoluto do venv → rodou direto do clone novo.
3. Transcrição concluída com sucesso (exit 0).
4. **Migradas as referências de path** do OneDrive → `C:\dev\meeting-transcriber` em 5 arquivos de skill (7 ocorrências): `obsidian-transcrever-reuniao`, `obsidian-transcrever-conteudo` (SKILL.md + build_content_notes.py), `obsidian-estudar-youtube`, `registrar`.

## Resolução DEV-993 (30/06, sessão Time Dev)

- **Device Guard (WDAC) bloqueando o `python.exe` do venv:** **bloqueio era transitório** (efeito do OneDrive tocar nos binários). Na re-validação, `C:\Venvs\meeting-transcriber\Scripts\python.exe` executa normalmente — `--version`, import `torch 2.8.0+cu128` + `whisperx`, `cuda=True`, tudo exit 0.
- **`transcriber.bat` agora é resiliente** (commit no repo): pré-check `"%VENV_PY%" -c "pass"`; se o Device Guard rebloquear o python do venv, cai **automaticamente** pro python-base do uv (`%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11-*\python.exe`) + `PYTHONPATH=...\Venvs\meeting-transcriber\Lib\site-packages` (workaround validado). Ambos os ramos testados — `--help` e import pesado OK nos dois.
- **`.env` (com `HF_TOKEN`) já recriado** em `C:\dev\meeting-transcriber\.env` (diarização restaurada).
- **Skills-fonte do repo corrigidas:** `gravar/parar/pausar/retomar/transcrever-reuniao.md` ainda apontavam pro path OneDrive → migradas pra `C:\dev\meeting-transcriber`. A skill ativa do framework (`stamper/skills/obsidian-transcrever-reuniao`) já estava correta e invoca o `.bat` (herda o fallback).
- **Pendente (não-bloqueante):** casca desidratada vazia ainda em `OneDrive\Documentos\ClaudeCode\Hub Projetos\meeting-transcriber` — remover quando o Felipe confirmar (destrutivo).

## Prevenção

- [ ] **Projetos executáveis não vivem no OneDrive** (regra DEV-865). Clones de trabalho em `C:\dev\`.
- [ ] Skills que invocam binários/scripts apontam pra paths fora do OneDrive.
- [ ] Ao re-clonar projeto com `.env` gitignored, recriar o `.env` a partir do 1Password.

## Refs

- DEV-865 — OneDrive corrompe git worktrees / desidrata `Hub Projetos`
- Repo: `felipeluissalgueiro/meeting-transcriber` · Clone estável: `C:\dev\meeting-transcriber`
- Venv: `C:\Venvs\meeting-transcriber`
