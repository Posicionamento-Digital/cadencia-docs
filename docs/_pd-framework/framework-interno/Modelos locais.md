---
date: 2026-07-05
tags: [documentacao, projeto, llm]
moc: "[[MOC-Projetos]]"
squad: stamper
type: source
entities: ["[[PD Framework]]"]
---
# Modelos locais — Playbook

**Projeto:** PD Framework
**Squad:** `stamper`
**Repo:** `C:\dev\pd-framework`
**Branch merged:** N/A — documentacao operacional em branch de sessao
**Issues:** N/A

## O que essa feature entrega

Registra a opcao local de LLMs via Ollama para o notebook do Felipe.
O objetivo e permitir testes locais com harnesses como OpenCode sem reaprender quais modelos rodam, quais aquecem demais e quais nao servem para agente.
O default operacional fica sendo `qwen3:4b-8k`.

## Como usar

1. Abrir ou manter o Ollama rodando no Windows.
2. Usar `qwen3:4b-8k` como modelo local default.
3. Para chat direto, rodar `ollama run qwen3:4b-8k`.
4. Para teste OpenCode, rodar `opencode run --pure -m ollama/qwen3:4b-8k "Responda exatamente: OK local"`.
5. Depois de testes pesados, conferir `ollama ps` e descarregar modelos com `ollama stop <modelo>` se necessario.

## Como manter

Editar primeiro os arquivos em `C:\dev\pd-framework\docs\modelos-locais\`.
Se mudar modelo, contexto, hardware ou resultado de benchmark, atualizar tambem `CLAUDE.md` e regenerar `AGENTS.md` via `python adapters\codex\bootstrap.py`.
Aliases 8K sao recriados pelos Modelfiles `ollama-qwen3-4b-8k.Modelfile` e `ollama-qwen3-8b-8k.Modelfile`.

## Decisoes importantes

- Ollama e o runtime local principal em Windows para notebook.
- SGLang nao e default: e melhor para serving dedicado, batching e workloads de infra.
- `qwen3:4b-8k` e o default local porque ficou em GPU e contexto controlado.
- `qwen3:8b-8k` roda, mas e mais pesado e cai parcialmente em CPU.
- `gemma3:4b` serve para chat simples, mas nao para OpenCode agent por falta de tools.

## Refs tecnicas

- Docs componentes: `C:\dev\pd-framework\docs\modelos-locais\`
- Wiki HTML: `C:\dev\pd-framework\docs\modelos-locais\index.html`
- Config OpenCode: `C:\dev\pd-framework\opencode.json`
- Canvas: `[[Modelos locais.canvas]]`
