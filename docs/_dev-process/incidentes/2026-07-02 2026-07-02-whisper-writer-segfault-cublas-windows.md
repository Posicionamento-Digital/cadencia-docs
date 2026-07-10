---
type: source
source_kind: incidente
date: 2026-07-02
entities: ["[[Cadencia]]", "[[meeting-transcriber]]", "[[whisper-writer]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-07-02_whisper-writer-segfault-cublas-windows

# Incidente: Setup do fork whisper-writer travou em 3 bugs Windows+GPU sobrepostos (segfault, cuBLAS ausente, sound_device silencioso)

**Data:** 02/07/2026
**Severidade:** Baixa
**Projeto:** whisper-writer (fork pessoal, `C:\dev\whisper-writer`)
**Duração do impacto:** ~2h de setup/debug numa sessão (sem impacto em produção — ferramenta pessoal ainda não em uso)
**Tags:** #windows #cuda #dll #ctranslate2 #pyqt5 #silenciosa #infra

## O que aconteceu

Ao montar um fork do [whisper-writer](https://github.com/savbell/whisper-writer) (ditado por voz em tempo real via hotkey → Whisper local → digita no cursor), o app falhou em 3 estágios sucessivos antes de funcionar:

1. `pip install -r requirements.txt` falhava — `av==11.0.0` sem wheel pra Windows/cp311, exigindo MSVC Build Tools pra compilar do zero.
2. Depois de corrigir isso, o app **crashava sem traceback** (segfault, exit code 139) ao ser aberto — nenhuma janela aparecia.
3. Depois de corrigir o segfault, o app abria e reconhecia a hotkey, mas travava em "Transcribing" — o terminal mostrava `RuntimeError: Library cublas64_12.dll is not found or cannot be loaded`.
4. Um quarto problema, silencioso (sem erro visível pro usuário): a hotkey capturava áudio mas nada era digitado — a config de `sound_device` salva pela própria GUI de Settings do app quebrava a gravação.

## Causa raiz

1. **`av==11.0.0` sem wheel Windows** — `requirements.txt` do fork upstream pinava uma versão de `av` (dependência transitiva do `faster-whisper`, não usada diretamente no código) sem build pré-compilado pra `cp311`/Windows. `av==12.0.0` tem wheel e é compatível.

2. **Segfault por conflito de DLL OpenMP** (`src/main.py`) — a ordem de import original do projeto carrega `PyQt5` **antes** de `faster_whisper`/`ctranslate2`. Isso causa um conflito nativo entre a runtime OpenMP do Qt e o `libiomp5md.dll` que o `ctranslate2` carrega — reproduzido de forma determinística: importar PyQt5 antes de `faster_whisper` sempre segfaulta (exit 139), na ordem inversa nunca. Esse é um bug conhecido e **ainda aberto** upstream ([issue #47](https://github.com/savbell/whisper-writer/issues/47)); a variável de ambiente `KMP_DUPLICATE_LIB_OK=TRUE` sugerida na issue **não resolve** (testado e confirmado que ainda segfaulta).

3. **cuBLAS ausente** (`src/transcription.py:15`, via `ctranslate2`) — `ctranslate2==4.2.1` (pin original do fork) exige cuDNN 8 instalado no sistema, que não estava presente. Ao atualizar pra `ctranslate2==4.7.1` (que empacota cuDNN 9 de forma self-contained dentro do próprio pacote pip, resolvendo o problema de cuDNN), sobrou uma segunda lacuna: `ctranslate2` não empacota `cublas64_12.dll` (cuBLAS), que precisa vir de uma instalação CUDA Toolkit separada ou de outro pacote que já a tenha baixado. Bug também conhecido upstream ([issue #33](https://github.com/savbell/whisper-writer/issues/33)).

4. **`sound_device` silenciosamente quebrado** (`src/config_schema.yaml` + `src/result_thread.py:143`) — o schema define `sound_device` como `type: str` (necessário pra `QLineEdit` da tela de Settings não quebrar ao renderizar o valor), mas o código passava esse valor **direto** pro `sd.InputStream(device=...)` da lib `sounddevice`. `sounddevice` trata um `device` do tipo `str` como busca por **nome** (substring), não como índice — `"1"` casava com um device WDM-KS incompatível (`Blocking API not supported`) em vez do índice numérico 1 (microfone correto). Falha silenciosa: sem crash, sem áudio capturado, sem erro visível na UI.

## Por que não foi detectado

Antes de começar o setup, só o README do projeto foi consultado — não as *issues* abertas do repositório. As issues #33 e #47 já documentavam exatamente os problemas de cuBLAS/cuDNN e do segfault OpenMP, respectivamente (embora sem solução funcional publicada em nenhuma delas). Consultar as issues antes de instalar teria antecipado 2 dos 4 problemas.

## Como foi corrigido

1. `requirements.txt`: convertido de UTF-16 (encoding quebrado no fork) pra UTF-8; `av` 11.0.0 → 12.0.0; `ctranslate2` 4.2.1 → 4.7.1; adicionado `setuptools<81` (setuptools ≥82 removeu `pkg_resources`, do qual `ctranslate2` ainda depende).
2. `src/main.py`: reordenados os imports — `from transcription import create_local_model` movido pra antes dos imports do `PyQt5`, forçando as DLLs nativas do `ctranslate2` a carregar primeiro.
3. `cublas64_12.dll` + `cublasLt64_12.dll` copiadas de `C:\Venvs\meeting-transcriber\Lib\site-packages\torch\lib\` (PyTorch já tinha baixado, ~750MB) pra `C:\Venvs\whisper-writer\Lib\site-packages\ctranslate2\` — sem novo download.
4. `src/result_thread.py`: cast de `sound_device` pra `int` quando o valor for uma string numérica, antes de passar pro `sd.InputStream`. `sound_device` continua `str` no `config.yaml` (senão quebra a UI de Settings).
5. Testado ponta-a-ponta com fala real: hotkey `Ctrl+Alt+Space` → grava → transcreve → digita no campo ativo. Funcionou.

## Prevenção

### Checklist / regras pra evitar recorrência

- [ ] Antes de configurar qualquer projeto Python que dependa de bibliotecas nativas GPU (ctranslate2, torch, onnxruntime) no Windows, checar as *issues* abertas do repo por termos como `cuda`, `dll`, `segfault`, `crash` — não confiar só no README.
- [ ] Ao integrar uma lib nativa com GPU (`ctranslate2`/`faster-whisper`) numa app PyQt5/PySide, importar a lib nativa **antes** de qualquer import do Qt — mitiga conflitos de runtime OpenMP conhecidos nesse ecossistema.
- [ ] Ao herdar um "type: str" de schema pra um campo que semanticamente é numérico (índice de device, porta, etc), verificar no código de consumo se há cast — não assumir que a lib downstream aceita string.
- [ ] Considerar abrir PR upstream pro fix do segfault (item 2) — não está documentado em lugar nenhum do issue tracker do projeto original.

### Pattern correto

```python
# src/main.py — ordem de import que evita o segfault
from transcription import create_local_model  # ctranslate2/faster_whisper primeiro

from PyQt5.QtWidgets import QApplication  # PyQt5 depois
```

```python
# result_thread.py — cast defensivo quando o schema força str mas o valor é numérico
sound_device = recording_options.get('sound_device')
if isinstance(sound_device, str) and sound_device.strip().lstrip('-').isdigit():
    sound_device = int(sound_device)
```

### Regra atualizada em

- [x] Memória do agente (Stamper) — `project_whisper_writer_setup.md`
- [ ] CLAUDE.md global (avaliar se vale generalizar a regra de "checar issues antes do README" pra qualquer setup de dependência nativa)

## Commits relacionados

- `770433e` — fix: corrige segfault de import, cuBLAS ausente e sound_device string (repo `felipeluissalgueiro/whisper-writer`, branch `feature/dev-1054-...`)

## Links relacionados

- Issue Linear: [DEV-1054](https://linear.app/cadencia/issue/DEV-1054/chore-setup-fork-whisper-writer-para-ditado-por-voz-em-tempo-real)
- Fork: https://github.com/felipeluissalgueiro/whisper-writer
- Upstream issue #33 (cuBLAS/cuDNN Windows): https://github.com/savbell/whisper-writer/issues/33
- Upstream issue #47 (segfault OMP libiomp5md.dll): https://github.com/savbell/whisper-writer/issues/47

---
*Registrado via sistema de incidentes. Ver INDEX.md para histórico completo.*
