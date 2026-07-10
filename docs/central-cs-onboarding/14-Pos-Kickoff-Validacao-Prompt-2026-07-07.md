---
date: 2026-07-07
tags: [documentacao, projeto, cs, arquitetura]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Central CS Onboarding]]", "[[OP-Odontopenha]]"]
---
# Central de CS — Pacote Pós-Kickoff / Validação de Prompt (07/07/2026)

> Gerado por `/documentar` sobre o trabalho da sessão de 07/07/2026: 8 Epics do projeto Linear "Automação do Onboarding CS (Fases 1-7)" (DEV-1237/1227/1232/1241/1247/1252/1258/1219), executados em Modo A, validados end-to-end em produção real com **OP Odontopenha** antes de existir automação (fizemos manual primeiro, depois automatizamos o que provou funcionar). Complementa [[13-Referencia-Tecnica-Componentes-2026-07-05]] — cobre as Fases 5-7 que lá ainda não tinham módulo próprio.

## O que é

Módulo `times/cs/workers/pos_kickoff/` — cobre o trecho do Playbook entre "Integrações & IAs" e "Estabilização pós-Go-Live": form de feedback da Lara, Manual do Sistema + Roteiro de Testes, estágios de pipeline, envio do pacote (email+WhatsApp), controle do ciclo de teste, checklist de aprovação de Go-Live e estabilização.

**Regra de ouro do módulo inteiro:** cada step tem um gate de segurança (`confirmar=False`/`aplicar=False` por padrão) — nenhum email, WhatsApp, mutação de CRM ou de pipeline de produção acontece sem confirmação humana explícita. O orquestrador só monta relatórios de "próximos passos pendentes"; quem decide executar de verdade é sempre uma pessoa.

## Origem: fizemos manual primeiro (CSE-152..159)

Antes de automatizar, o pacote inteiro foi montado e **enviado de verdade** pra OP Odontopenha — email formal + WhatsApp no grupo, formulário Tally real (`https://tally.so/r/MeyGl8`), Manual + Roteiro publicados via nota Obsidian + `/compartilhar-nota` (confirmado que o Quartz renderiza Mermaid nativamente). Essa execução manual é o que validou o desenho antes de qualquer linha de código — decisão registrada por Felipe: "fazer manual primeiro, mas templatizado, pra quando formos automatizar já ter o template pronto".

## Jornada (continuação do passo 7 de [[13-Referencia-Tecnica-Componentes-2026-07-05]])

8. **Validação de prompt** → `/validar-prompt <cliente>` (ou Bloco D.2 do `/ativar-cliente`) → orquestrador gera form Tally + Manual/Roteiro (draft) + preview do pacote
9. **Confirmação humana por etapa** → Felipe revisa e confirma cada step (`confirmar=True`) — publica docs via `/compartilhar-nota`, dispara email+WhatsApp de verdade, registra nota no CRM
10. **Ciclo de teste** → cliente testa a Lara no Playground durante N dias (default 7), lembrete automático nos últimos 2 dias
11. **Checklist Go-Live** → 5 gates (prompt validado, testes concluídos, ajustes feitos, cliente aprovou, issue atualizada) — 4 são manuais por natureza (não dá pra automatizar "o cliente aprovou verbalmente numa call")
12. **Estabilização pós-Go-Live** → N dias (default 7) de acompanhamento intensivo, checklist diário, depois transição pra suporte contínuo

## Os 8 componentes (código no repo, sem MD próprio ainda — ver docstrings)

| # | Componente | Path no repo | O que faz |
|---|---|---|---|
| 1 | Contexto | `times/cs/workers/pos_kickoff/context.py` | `PosKickoffContext` — dados que amarram todos os steps (tenant, slug, contato, URLs acumuladas) |
| 2 | Estado | `times/cs/workers/pos_kickoff/state.py` | checkpoint idempotente em `times/cs/state/pos-kickoff/<slug>.json` |
| 3 | Formulário | `times/cs/workers/pos_kickoff/tally_step.py` | cria form Tally de feedback via `_shared/tally_builder.py` (promovido de script solto pra `_shared/` nesta sessão) |
| 4 | Templates | `times/cs/workers/pos_kickoff/templates_step.py` | gera Manual do Sistema + Roteiro de Testes a partir dos templates mestres (`times/cs/foundation/templates-documentos/`), publicação via Obsidian fica pra confirmação humana |
| 5 | Pipeline | `times/cs/workers/pos_kickoff/pipeline_step.py` | configura estágios novos no pipeline `pd-onboarding` (dry-run por padrão — mutação de CRM de produção compartilhado) |
| 6 | Dispatch | `times/cs/workers/pos_kickoff/dispatch_step.py` | monta e envia o pacote (email+WhatsApp+nota CRM) — gate `cliente_registry` obrigatório antes de qualquer envio |
| 7 | Ciclo de teste | `times/cs/workers/pos_kickoff/test_cycle_step.py` | deadline, lembretes, stub de coleta de respostas Tally (sem webhook configurado ainda) |
| 8 | Checklist Go-Live | `times/cs/workers/pos_kickoff/golive_checklist_step.py` | 5 gates de aprovação, registra aprovação no CRM quando liberado |
| 9 | Estabilização | `times/cs/workers/pos_kickoff/stabilization_step.py` | N dias pós-Go-Live, checklist diário, transição pra suporte contínuo |
| — | Orquestrador | `times/cs/workers/pos_kickoff/orchestrator.py` | `executar_pipeline_pos_kickoff(ctx)` — encadeia tudo, sempre em preview |

## Templates novos (reutilizáveis por qualquer cliente com agente de IA)

- `times/cs/foundation/templates-documentos/manual-do-sistema-cadencia.md` — manual operacional passo a passo com diagramas Mermaid por seção
- `times/cs/foundation/templates-documentos/roteiro-testes-lara.md` — casos de teste reais, o que a Lara deve/não deve responder, limitações
- `times/cs/foundation/templates-email/05a-validacao-prompt.md` + `templates-whatsapp/` — pacote de envio (link manual/roteiro/form/agendamento + acesso, credencial só no email)
- `times/cs/foundation/templates-email/05a-lembrete-validacao-prompt.md` + `templates-whatsapp/` — lembrete de prazo
- `times/cs/foundation/templates-email/05a-checklist-diario-estabilizacao.md` + `templates-whatsapp/` — checklist diário pós-Go-Live

## Comandos novos

- **`/pos-briefing <cliente>`** — dispara manualmente o Bloco D.1 (processar transcrição + cadeia pós-briefing) quando o worker automático não pegou
- **`/validar-prompt <cliente>`** — dispara o orquestrador `pos_kickoff` isolado, sem precisar rodar `/ativar-cliente` completo desde o Bloco A

## Decisões arquiteturais-chave

- **Orquestrar wrappers existentes, não construir engines novas** (gate Vitor, 07/07/2026) — `_shared/tally_builder.py`, `_shared/email_templates.py`, `_shared/evo_client.py`, `_shared/cliente_registry.py` já resolviam tudo; o trabalho real foi encadear com segurança, não reinventar.
- **Documentos entregues via Obsidian + `/compartilhar-nota` → Quartz, não PDF/HTML.** Rescope do plano original — confirmado que o Quartz renderiza Mermaid nativamente antes de publicar (build local de teste).
- **`feat/dev-1227` (branch anterior) estava contaminada** com código de outro projeto (motor-deploy) — cherry-pick seletivo só dos arquivos relevantes (`merge_template.py`, templates), não merge da branch inteira.
- **Todo side-effect real é opt-in explícito** (`confirmar`/`aplicar`) — nenhum step muta produção sozinho, nem dentro do orquestrador.
- **Gotcha recorrente (DEV-1164):** `SUPABASE_ACCESS_TOKEN` de sessão anterior sombreia o token do 1Password → 401 no `cadencia-cli`. Qualquer chamada precisa recarregar o token fresh via `op`, não confiar em env herdado.

## Caso real de validação

**OP Odontopenha** — CSE-152 (issue-mãe) até CSE-159, reunião de validação de prompt real (transcrição 07/07/2026, 55min). Formulário Tally real criado, email formal enviado (Guilherme, cc Felipe), WhatsApp real no grupo `Cadencia | Implementação - Clínica Op🦷`, nota registrada no CRM (contato `ba343f5f`).

## Bug real encontrado ao validar entrega correlata (Motor Autônomo, mesma sessão)

Fora do escopo deste módulo, mas descoberto no mesmo dia ao validar PRs mergeadas (DEV-1207/DEV-1208, paridade de worktree Codex/OpenCode): `close_session.py` não removia worktrees isolados de verdade no Windows (processo pai ficava com cwd travado dentro do worktree enquanto esperava o processo filho — Windows não libera diretório-cwd de processo vivo). Fix em PR #51. Não relacionado a CS, mas achado durante a mesma sessão de validação — registrado aqui pra rastreabilidade temporal.

## Links

- [[13-Referencia-Tecnica-Componentes-2026-07-05]] — componentes das Fases 1-4 (esta nota complementa, não substitui)
- [[00-Visao-Geral]]
- Repo: `times/cs/context/sistema-central-onboarding.md` (atualizado com o componente #12)
- Repo: `times/cs/skills/ativar-cliente/SKILL.md` (Blocos D.2 e G)
- Linear: [Automação do Onboarding CS (Fases 1-7)](https://linear.app/cadencia/project/automacao-do-onboarding-cs-fases-1-7-b37d1d5ef0d7)
- PRs: #49 (8 Epics pos_kickoff), #52 (skills /pos-briefing e /validar-prompt), #51 (fix worktree, correlato)
