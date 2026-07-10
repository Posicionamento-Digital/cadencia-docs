---
date: 2026-07-03
tags: [brief, projeto]
moc: "[[MOC-Projetos]]"
squad: times/dev
type: source
entities: ["[[Cadencia]]", "[[Central de Observabilidade]]", "[[PD Framework]]", "[[comercial]]", "[[financeiro]]", "[[pd-portal]]", "[[qualidade]]"]
---
# Brief — PD Framework v2.0 — Motor Autônomo 24/7

**Projeto Linear:** https://linear.app/cadencia/project/pd-framework-motor-autonomo-247-benchmark-ruflo-visao-c6bfddcd6729  
**Squad PD Framework:** `times/dev`  
**Atualizado em:** 2026-07-03  
**Preenchido por:** Felipe

## O que é e por que existe

O projeto é a evolução do PD Framework para uma **v2.0 de capacidades estruturais**, não apenas a criação de um executor autônomo. O motor 24/7 é a capacidade-síntese no topo da pilha: agentes de squad executando trabalho real sem acionamento constante do Felipe, mas só depois de o framework ganhar memória com ciclo de vida, rastreio de custo/outcome, roteamento consciente de modelos, recorder de sessões, tooling de skills e regras confiáveis de escalonamento.

A visão é transformar o framework de um sistema que hoje depende de interação humana para iniciar e fechar ciclos em uma infraestrutura operacional que aprende, mede, se protege e executa. O modo interativo atual continua existindo, mas passa a ser sustentado por capacidades melhores: cada agente deve carregar contexto mais útil, usar o modelo certo para o harness certo, registrar o que fez, medir custo por tarefa e deixar rastro recuperável mesmo quando uma sessão cai.

O problema de fundo tem duas camadas. A primeira é de **maturidade do framework**: memória cresce sem curadoria automática, decisões se perdem se a sessão não fecha, skills podem quebrar silenciosamente, custo de LLM é invisível e seleção de modelo ainda depende de intuição. A segunda é de **throughput operacional**: 100% da execução ainda depende do Felipe acionar, priorizar ou destravar. Enquanto isso for verdade, a empresa inteira fica limitada pelo gargalo de uma pessoa.

## Stakeholders

Felipe é lead, decisor final e usuário principal da camada de controle: define orçamento, aprova riscos críticos e recebe escalonamentos via WhatsApp e Slack quando o motor encontra algo que não deve resolver sozinho.

Time Dev é o dono técnico da evolução. Paloma conduz o PRD e transforma a visão em requisitos e marcos. Vitor faz gate técnico, define arquitetura e fatia em epics. Amélia executa/babysitta implementação e reviews. João pode entrar como challenge transversal porque o escopo mexe em autonomia, custo, segurança e governança.

Squads consumidores: CS, Comercial, Infra e Produto Cadência. CS é beneficiário direto pelo fechamento do ciclo de onboarding autônomo ligado ao DEV-868. Comercial é beneficiário futuro por prospecção e follow-up via Eduardo/Cadência. Infra/Diego entra pela Central de Observabilidade, budget guard, workers determinísticos e regras de segurança da VPS Master.

Luiz não toca o motor. O escopo dele continua limitado a `cadencia-app` e `pd-portal`; não propagar skills ou runtime do PD Framework para o ambiente dele.

## Estado atual

O PD Framework já tem a base necessária: squads, STATE.md, decisions.md, sessions-log, incidents, lookup, skills, hooks, Runtime Contract, adapters Claude Code/OpenCode/Codex, fluxo Linear e memória curada em git. O Adapter Codex #3 foi concluído e validado em 2026-07-02, com smoke 46/46 e hooks reais funcionando.

Já existem workers determinísticos na VPS Master em dry_run nas Ondas 1-3 do DEV-897. A regra de segurança já está clara: VPS Master não roda agente com tool use; só scripts determinísticos. A Central de Observabilidade já existe como projeto irmão e deve absorver parte das capacidades de medição, alerta e self-healing.

O estudo ruflo foi concluído e virou o doc vivo `times/dev/context/brainstorm-motor-autonomo-ruflo.md`. O saldo do estudo não é "copiar ruflo", mas roubar seletivamente o que resolve gaps reais do PD Framework e descartar o teatro/overengineering. O estudo produziu D1-D6, além de descartes explícitos: hive-mind, swarm, SONA, federation IPFS, Web UI, 314 MCP tools, consensus simulado, workers headless em timer sem budget guard e claims locais em JSON sem transação.

O ponto de partida do projeto não é greenfield. Ele deve expandir capacidades existentes: hooks, lookup, Linear, STATE/decisions, Central de Observabilidade, cadencia-cli como padrão de CLI e fluxo Dev já consolidado.

## Arquitetura e stack

Repo único: `felipeluissalgueiro/pd-framework`. O motor vive no framework; não criar repo novo.

Stack base: Python 3.12 em `_core/`, `_shared/`, `adapters/` e workers. Markdown + git continuam como fonte de verdade da memória curada. Linear é a fila operacional e camada primária de claim: issue = task, assignee/status = claim/lifecycle, prioridade/cycle = ordenação, comentários = auditoria. Worktrees e Modo B seguem resolvendo isolamento de edição.

SQLite local só entra como **black box recorder** de sessão, uma camada de resgate, não como banco canônico do framework. Se algum dia houver necessidade real de estado concorrente compartilhado entre Windows, VPS Dev e VPS Master, a direção provável é Supabase Postgres, não SQLite local. Esse gatilho ainda não existe.

A interface agente ↔ estado compartilhado deve seguir o princípio D5: **CLI via shell-out, não MCP como fundação**. MCP pode existir como adapter fino por cima de CLI pronta, mas não como camada base porque consome contexto, não roda na VPS Master e cria acoplamento desnecessário. Padrão de referência: `cadencia-cli`.

Os três harnesses precisam respeitar o Runtime Contract: Claude Code, Codex e OpenCode. O MODEL-MAP deve ser segmentado por harness e por regime de cobrança: harness de assinatura não pode gastar API por token salvo exceções explícitas de review.

## Decisões técnicas tomadas

D1 — Memória com ciclo de vida. Portar o loop útil do ADR-050 do ruflo: confiança, acesso, decay, ranking e tendência. O objetivo não é só buscar melhor; é curar automaticamente memória que hoje só cresce. Implementar em Python sobre hooks existentes, usando heurísticas baratas antes de embeddings. Medir snapshot/tendência IMPROVING/DECLINING.

D2 — MODEL-MAP por harness. Criar mapa declarativo de modelos por runtime: Claude Code usa modelos cobertos pela assinatura Anthropic; Codex usa modelos cobertos pela assinatura OpenAI; OpenCode pode usar modelos pagos por API/OpenRouter. Regra dura: não gastar token pago dentro de harness de assinatura, exceto skills de review já autorizadas.

D3 — Black box recorder. Arquivar turnos de sessão de forma proativa para recuperar trabalho quando a sessão cai ou `/encerrar-sessao` não roda. É camada de resgate, não memória nobre. A memória curada continua sendo STATE, decisions, sessions-log e incidents.

D4 — `/criar-skill` + linter de skills. Criar ferramenta de autoria guiada e validação em lote para evitar skills quebradas por frontmatter ausente, BOM, descrição ruim ou estrutura inválida. A escala atual de 139+ skills exige tooling, não revisão manual.

D5 — CLI-não-MCP para estado compartilhado. A decisão é princípio arquitetural, não implementação imediata de fila. Linear já cobre a fila/claim no momento; só reabrir implementação própria se houver evidência real de conflito, gargalo ou necessidade transacional.

D6 — Template CAD-Bug com Evidência + Impacto. Bugs precisam puxar prova executável e impacto real: comando/log/query que comprova causa, tenants/clientes afetados, perda/corrupção de dados e origem da descoberta.

Princípios estruturais do projeto: **CLI-não-MCP**, **assinatura-não-API**, **MD-curado-não-banco**. Insight diretor: logar outcomes estruturados desde já, porque a qualidade do aprendizado futuro depende mais da qualidade do sinal de sucesso do que da sofisticação do algoritmo.

## O que NÃO fazer

Não transformar o projeto em uma frota especulativa de agentes. A doença do ruflo é construir infraestrutura para escala inexistente. Toda implementação de fila, claim, swarm, router estatístico ou banco compartilhado precisa de gatilho de evidência.

Não portar hive-mind, SONA, EWC, LoRA/RL, federation IPFS, Web UI, consensus Byzantine/Raft/Gossip ou registry de agents que não executam. O PD já tem alternativas melhores: squads/personas, Modo B com worktrees, Amélia babysitting, Vitor gate, Linear, reviews independentes e `/dev-debate`.

Não usar MCP como fundação do estado. Não criar 300 tools residentes. Não pagar API dentro de Claude Code/Codex por padrão. Não rodar IA em timer recorrente sem cost tracker, budget guard e demanda real.

Não permitir tool use na VPS Master. Não fazer auto-merge de mudança crítica. Não executar deploy, billing, migração, mutação em massa, mensagem para cliente ou alteração destrutiva sem escalation matrix calibrada.

Não substituir a memória curada em Markdown/git por banco opaco. Banco pode existir para recorder ou agregação futura, mas a fonte nobre de decisões e estado operacional continua revisável por diff.

## Dependências críticas pendentes

Cost tracker é bloqueador absoluto. Sem custo por tarefa/modelo/harness, qualquer loop autônomo pode virar vazamento financeiro silencioso.

Outcome schema é pré-requisito do aprendizado. Cada execução precisa registrar tarefa, squad/persona, harness/modelo, custo estimado/real, resultado, evidência de sucesso/falha, issue/PR relacionados e necessidade de intervenção humana.

PR escalation matrix é bloqueador do motor. Precisa definir o que auto-mergeia, o que vai para review humano, o que chama WhatsApp e Slack e o que nunca roda sem aprovação explícita. Essa matriz deve ser calibrada antes de qualquer autonomia real.

Budget mensal por squad precisa de decisão do Felipe. Sem limite por squad, o motor não sabe quando parar, degradar modelo, adiar tarefa ou escalar.

Central de Observabilidade precisa estar alinhada como camada de alerta/medição/self-healing. DEV-868 e DEV-897 são dependências de contexto porque representam os primeiros consumidores reais do motor.

Não há dependência crítica externa de terceiro identificada. O risco está na governança interna, não em API externa.

## Critério de conclusão

A v2.0 está concluída quando D1-D6 estiverem em produção e medidas: memória com ciclo de vida ativo e snapshots de tendência; MODEL-MAP carregado nos três harnesses; black box recorder salvando sessões e consultável; linter zerando skills quebradas; template CAD-Bug atualizado; outcomes/custos registrados por tarefa.

O Motor v1 está concluído quando existir um ciclo autônomo completo em produção: issue entra no Linear, o squad correto assume, agente executa, abre PR, passa por reviews, aplica escalation matrix, faz auto-merge apenas quando permitido, marca Done, atualiza documentação/memória e registra outcome/custo. Caminho feliz sem toque do Felipe; caminho crítico escalando corretamente via WhatsApp e Slack.

KPIs mínimos: issues por semana resolvidas autonomamente; custo por issue; percentual de tarefas que exigiram intervenção humana; zero ações destrutivas sem aprovação; zero uso indevido de API paga em harness de assinatura; zero sessão perdida sem recorder; tendência de memória não-degradante nos snapshots.
