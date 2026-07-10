---
date: 2026-07-02
tags: [dev, framework, agentes, benchmark, ruflo, motor-autonomo, decisao]
moc: "[[MOC-Dev]]"
---
# Estudo ruflo — análise completa e decisões (Motor Autônomo)

> Estudo profundo do repo [ruvnet/ruflo](https://github.com/ruvnet/ruflo) (62k★, sucessor do claude-flow) com **leitura de código-fonte** (não só doc), pra extrair o que aprimora o PD Framework. Alimenta o projeto Linear **PD Framework — Motor Autônomo 24/7** (`77090439`). Sessão 2026-07-02/03.
>
> **Fonte da verdade viva:** `pd-framework/times/dev/context/brainstorm-motor-autonomo-ruflo.md` (git) + [índice no Linear](https://linear.app/cadencia/document/brainstorm-decisoes-do-estudo-ruflo-doc-vivo-no-git-542c25d679e5). Esta nota é o retrato consolidado do estudo.
> Aprendizados conceituais pessoais: nota no vault Pessoal (IA-Tecnologia, 2026-07-02).

---

## Método e achado transversal

Cada componente foi estudado **na implementação** (arquivos baixados e lidos: `intelligence.cjs` completo, `model-router.ts`, `context-persistence-hook.mjs`, `hook-handler.cjs`, `headless-worker-executor.ts`, `claims-tools.ts`, comandos `swarm.ts`/`hive-mind.ts`, `openrouter-alts.json`, 4 SKILL.md, ADR-055).

**Achado transversal — 4 casos de doc ≠ código no mesmo repo:** bloqueio de auto-compact que não funciona (o código admite), swarm que não executa (stub #1423), neural router nunca ligado (#2329), HierarchicalMemory stub por meses (ADR-055 deles). Regra derivada: em repo de terceiro, a doc diz a intenção; só o código diz o produto.

## Veredito geral

O que sobreviveu do ruflo é quase tudo **ciclo de vida e disciplina** (memória que decai e ganha confiança por uso, description que ensina quando usar, evidência em issue, bandit sobre outcomes). O que caiu é quase tudo **teatro de escala** (swarm/hive-mind, consensus, 313 MCP tools, redes neurais auxiliares). O PD saiu com 3 decisões estruturais escritas e defendidas: **CLI-não-MCP · assinatura-não-API · MD-curado-não-banco**.

## As 6 decisões (D1–D6)

**D1 — Ciclo de vida de memória** (portar loop ADR-050 deles): injeção automática rankeada por prompt (Jaccard de trigramas + PageRank sobre grafo de memórias, $0, sem embedding), confidence boost por uso + **feedback implícito** (usuário continuou trabalhando = +confidence), decay pra não-usadas, auto-insight de hot paths (arquivo editado 3+×/sessão vira memória), snapshot/trend pra MEDIR se a memória melhora. **Reprioriza o memory engine P1: ciclo de vida antes de embeddings** — o gap do PD é curadoria, não busca. Adendos: fórmula de importância (recência meia-vida 7d × frequência log × riqueza acionável); fase 2 = curva de Ebbinghaus com força (spaced repetition) + consolidação episódico→semântico (automação do sessions-log → MEMORY.md).

**D2 — MODEL-MAP por harness**: mapa declarativo de modelos em `_core/`, segmentado por **regime de cobrança do harness** (dimensão que o ruflo não tem). **REGRA DURA: Claude Code e Codex são assinatura — jamais modelo pago por token dentro deles**, exceto as skills de review que já existem pra isso. OpenCode = harness dos modelos pagos (mapa estilo `openrouter-alts.json`: tier + custo + rationale com benchmark medido). Bandit de routing (Thompson, recompensa ajustada por custo) adiado até o cost tracker existir.

**D3 — Black box recorder de sessões**: arquivador proativo de turnos (hook UserPromptSubmit → Python → SQLite, resumo extrativo sem LLM, dedup por hash) como camada de **resgate** pra sessão que morre sem `/encerrar-sessao`. A memória curada continua sendo a fonte nobre. Vira source `transcripts` no lookup.py.

**D4 — `/criar-skill` + linter de skills**: único sobrevivente das 39 skills deles (skill-builder). Autoria guiada com convenções PD + `lint-skills.py` em lote (caso real: 5 skills quebradas por frontmatter/BOM). Adendo ADR-112: description obrigada a responder "o que faz + quando ativar + quando NÃO usar/alternativa".

**D5 — Princípio de interface: agente ↔ estado via CLI, não MCP** (reescrita após confronto adversarial): o princípio fica (CLI via Bash = zero contexto residente, runtime-agnóstica, cobre workers determinísticos da VPS onde MCP nem é opção); a implementação (CLI `pd` + fila + claims) foi **rebaixada a condicional com gatilhos de evidência** — o Linear já é a fila com claims (assignee/status/priority), zero agentes concorrentes hoje (YAGNI), e SQLite local nem serve à topologia multi-máquina (se um dia, Supabase).

**D6 — Template CAD-Bug ganha campos Evidência + Impacto**: prova executável da causa (não só hipótese) + tenants afetados/perda de dados/como descoberto. Caso real que expôs a lacuna: incidente ingest-stakeholders (2026-07-01).

## Síntese — "agents that learn" decomposto

Fundamento: pesos do LLM nunca mudam; todo aprendizado de agente = experiência fora do modelo + sinal de sucesso + retrieval. Ranking de realidade dos 5 mecanismos deles: (1) loop de memória = real → D1; (2) bandit Thompson = estatística genuína → futuro da D2; (3) ReasoningBank/trajetórias = conceito bom, PD já faz com curadoria melhor (sessions-log=trajetórias, decisions.md=destilação, Felipe+reviews=judge); (4) Q-learning de agentes = roteia metadata rows que não executam; (5) SONA/EWC/RL = teatro (nunca ligado, sem ground truth, benchmark mede ops/sec e não ganho).

**Insight diretor pro Motor Autônomo: aprendizado é limitado pela qualidade do SINAL DE SUCESSO, não pelo mecanismo.** O PD tem sinal melhor que o ruflo (testes reais, deploy validado, cascata de reviews, Felipe). Ação de maior alavancagem: logar outcomes estruturados (tarefa, executor, modelo, resultado, custo) desde já.

## Sementes (retomar no momento certo)

- **Witness CI guard** — fix documentado registra marker verificado em CI (quando houver CI nos repos de produto).
- **8 prompt templates dos workers headless** (audit/testgaps/ultralearn...) — rascunho pro loop de auto-melhoria semanal (pós cost tracker).
- **Stale-claim reaper** — worker determinístico que devolve pra Todo issue In Progress abandonada (quando o motor existir; usa Linear como store).
- **Formato de handoff com contexto** (razão + % progresso + contexto + preferredTypes) — referência pro P3 "handoff estruturado entre personas".

## Descartes fundamentados (não reabrir sem fato novo)

Agent swarm/hive-mind (prova de código: `swarm start` é stub; a "Queen" é um prompt lançando UMA instância claude; "workers" são linhas de metadata; `agent_execute` = chamada one-shot de API paga; o prompt proíbe o Task tool nativo — que é melhor — pra manter a contabilidade deles no loop) · MCP server deles (API do estado + lock-in; flood de 313 schemas que eles mesmos remendam com tool groups) · Claims system (o árbitro de concorrência persiste em JSON sem lock — tem a race condition que existe pra prevenir) · 27 hooks (os úteis JÁ SÃO a fiação da D1; o "security" pre-bash é blocklist de 4 strings) · 12 workers (headless = `claude --print` em timer = incinerador de tokens sem budget guard) · SONA/EWC/RL · federation IPFS · classificador heurístico de complexidade (keywords EN + regex; agente lendo o mapa classifica melhor) · bloqueio de auto-compact (não funciona nem lá) · autopilot de % de contexto (harness atual já expõe) · 34 das 39 skills (wrappers do CLI deles) · rollback-incident template (post-mortem corporativo pra time grande).

## Meta-processo (registrado como feedback do Stamper)

Confronto adversarial vem **antes** de registrar decisão de brainstorm (a D5 original foi registrada rápido demais e reescrita após confronto pedido pelo Felipe). Teste rápido pra proposta de infra: "isso é a doença do ruflo?" (motor pra frota que não existe). Decisão especulativa entra com gatilhos de evidência.

---

**Refs:** projeto Linear Motor Autônomo 24/7 (`77090439`) · doc vivo `times/dev/context/brainstorm-motor-autonomo-ruflo.md` · benchmark original 2026-06-27 (`sessions-log/2026-06-27/`) · [[Processo - Desenvolvimento (Time Dev)]]
