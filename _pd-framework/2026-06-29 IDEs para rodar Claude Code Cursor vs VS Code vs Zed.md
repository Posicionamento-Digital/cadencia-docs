---
date: 2026-06-29
tags: [documentacao, llm, automacao]
moc: "[[MOC-IA-Tecnologia]]"
---

## Contexto
Avaliacao de migrar de IDE (VS Code para Cursor) tendo o **Claude Code** como motor principal de trabalho. Pergunta real por tras: como deixar o fluxo do Claude Code **mais visual** sem trocar de motor. Decisao apoiada por segunda opiniao de outro provider (Kimi K2 via OpenRouter).

## O que foi discutido

### Claude Code e OpenCode independem da IDE
Ambos rodam no **terminal/CLI**. A extensao de IDE (VS Code/Cursor/JetBrains/Zed) e so um wrapper que da diff inline, atalhos e selecao de contexto. Todo o framework (skills, hooks PreToolUse/Stop, CLAUDE.md, MCPs, memoria) vive em `~/.claude/` e roda pela CLI, sendo portanto **agnostico de IDE**. Qualquer host que embuta a CLI preserva 100% do fluxo; muda so a camada visual.

### Cursor nao agrega no meu caso
Cursor e fork pago do VS Code. Seus diferenciais (Composer, Cloud Agents, Bugbot, indexacao, MCP, Rules) **competem** com o que Claude Code + PD Framework ja fazem, nao somam. O **unico** diferencial real era o **Tab autocomplete** (completar codigo linha-a-linha enquanto digita). Como **nao escrevo codigo na mao** (dirijo por agente), o Tab nunca dispararia, entao **nao sobra motivo pra pagar Cursor**. Mesma logica derruba Supermaven/Codeium/Copilot: todos sao ferramentas de *escrever codigo*.

### Segunda opiniao (Kimi K2) - convergencia e correcoes
Dois providers independentes (Claude + Kimi) bateram na mesma tese: **nao migrar pro Cursor**. Kimi errou alguns fatos que foram corrigidos: (1) afirmou que app desktop do Claude Code nao existe - existe (Mac/Windows); (2) afirmou que rodar Claude Code dentro do Cursor quebra hooks / Composer intercepta - falso, Cursor e fork do VS Code, a extensao roda a mesma CLI com os mesmos hooks, e o Composer so roda se chamado.

### ACP - Agent Client Protocol
Protocolo aberto criado pela Zed que padroniza a comunicacao entre **editor (client)** e **agente de codigo** que roda como processo separado (subprocess via JSON-RPC/stdio). E o equivalente do **LSP**, mas para agentes de IA em vez de linguagens. **Distincao chave:** ACP = editor para agente; MCP = agente para ferramentas/dados. O agente mantem runtime, auth e selecao de modelo proprios; a UI do editor so mostra threads, diffs e aprovacoes de forma visual.

### Zed como melhor aposta
Editor em Rust, GPU-accelerated (muito mais rapido que Electron do VS Code/Cursor), gratis e aberto. Via ACP roda o **mesmo** Claude Code (em beta) **e** OpenCode (mais maduro no Zed); ambos no ACP Registry oficial (lancado com JetBrains, jan/2026). Permite ter **Claude Code e OpenCode lado a lado**, cada um numa thread, na mesma janela. Porens: Claude Code via ACP ainda e beta; build Windows mais novo que Mac/Linux; precisa validar se os hooks de sessao do framework disparam pela camada ACP.

## Decisoes e Conclusoes
- **Nao migrar pro Cursor.** Sem escrita manual de codigo, zero ganho, so sobreposicao paga.
- **Caminho pra mais visual sem trocar motor:** app desktop nativo do Claude Code (zero custo/migracao) ou **Zed** ao lado.
- **Zed e a aposta principal:** visual sobre o agente + multi-agente nativo (Claude Code + OpenCode) + performance + gratis + sem lock-in.
- **Teste critico antes de adotar de vez:** abrir o pd-framework no Zed e confirmar que o hook de sessao dispara (cria branch session/YYYY-MM-DD-HHMM no primeiro Edit/Write). Se nao disparar, ACP nao repassa os hooks = showstopper.

## Proximos Passos
- Instalar o Zed (ja baixado) e abrir o pd-framework.
- Adicionar Claude Code via ACP no Agent Panel, fazer /login.
- Validar o hook de sessao (branch automatica) e reportar resultado.

## Referencias
- zed.dev/blog/claude-code-via-acp - Claude Code beta no Zed
- zed.dev/docs/ai/external-agents - External Agents (ACP)
- opencode.ai/docs/acp - OpenCode via ACP
- zed.dev/blog/acp-registry - ACP Registry
