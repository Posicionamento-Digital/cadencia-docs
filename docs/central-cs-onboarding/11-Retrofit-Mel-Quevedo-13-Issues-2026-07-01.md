---
date: 2026-07-01
tags: [documentacao, projeto]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Central CS Onboarding]]", "[[Mel Quevedo]]"]
---
# Retrofit Mel Quevedo — 13 gaps do pipeline de ativação (DEV-979..996 + 989)

> Doc técnica da feature. Origem: retrofit da cliente **Melissa Quevedo** (Cadência Bundle) — cliente pagante há 27 dias que travou no briefing sem os processos de pós-provisionamento rodarem. A organização manual dela virou 13 issues, todas fechadas nesta sessão.
> Doc técnica completa (repo): `times/cs/context/doc-retrofit-mel-quevedo-13-issues.md`.

## O que é

O retrofit da Mel revelou que a skill `/ativar-cliente` (já robustecida em DEV-956) ainda não cobria o **relacionamento contínuo pós-provisionamento** — fases contratuais, recarga de créditos, posicionamento em pipelines de pós-venda, reativação de base de contatos — e tinha 2 bugs de infra que travavam toda transcrição local.

## Entregas principais

- **`contrato_fases.py`** (novo) — detecta a fase contratual (Onboarding/Operação Assistida/Autônoma) pelo T-0 do contrato. Validado: Mel em Fase 1, dia 11/15.
- **`importar_base_cliente.py`** (novo) — generaliza o ETL manual de reativação de base (dedup, e-mails compartilhados, gate de tenant crítico, enriquecimento). Validado contra dados reais: 222 titulares/190 PJ, números idênticos ao original.
- **Worker `recarga-creditos-mensal`** — reset automático de créditos no dia do ciclo. **Deployado na VPS Master** (systemd timer 18:25 BRT), mantido em dry_run (billing crítico) até validação ao vivo do Felipe.
- **Fix real no `cadencia-cli`** — `tenants provision` criava tenant em `status=trial` (conceito que não existe mais no Cadencia, créditos puros). Corrigido pra sempre `active`; tenant real da Mel corrigido em produção. PR #20 mergeada.
- **Sweep "planos→créditos" em 2 repos** (`pd-framework` + `cadencia-app`) — achado mais crítico: a **landing page pública** (`cadencia-app`) tinha um **erro de preço real** na FAQ ("Planos a partir de R$199,90/mês" quando o modelo real é pacotes avulsos). Corrigido, revisado (Opus, 0 P1) e **deployado em produção**.
- **Bloco F (Relacionamento por fase)** + 7 gates novos/reforçados na skill `/ativar-cliente` (e-mail ausente, Asaas customer_id, briefing heurística, ata de vendas, pipelines de pós-venda, dados de contato, referência de reuniões no Linear).

## Validação real (não mock)

- `contrato_fases.fase_atual('melissa-quevedo')` → Fase 1, T-0 19/06, dia 11/15 ✅ (bate com o gap relatado)
- `importar_base_cliente` dry_run → 222 titulares/177 com email/190 PJ ✅ (idêntico ao script original)
- Worker de recarga rodou via systemd na VPS Master → exit 0/SUCCESS contra clientes reais ✅
- `tenants verify` Mel pós-fix → `status: active` (era `trial`) ✅
- Deploy `cadencia-app` PR #83 → Vercel READY, autoria correta, não BLOCKED ✅

## Don'ts reforçados

- Nunca `--apply` real de billing em produção sem Felipe validar ao vivo, mesmo com deploy autorizado.
- Nunca assumir frontmatter YAML nos CLAUDE.md de cliente — convenção real é bullet inline.
- Nunca presumir que sweep no framework cobre o repo do produto — são fontes distintas.
- Nunca mutação em massa de dados de clientes sem confirmação explícita (27 tenants legados intocados por decisão consciente).

## Referências

- Issues: DEV-979, 980, 981, 982, 983, 984, 986, 987, 989, 993, 994, 995, 996
- PRs: `cadencia-cli#20`, `cadencia-app#83`
- Caso de referência: [[Mel Quevedo]]
- Robustez anterior: [[Robustez ativar-cliente DEV-956]]

## Notas Relacionadas

[[00-Visao-Geral]] · [[Robustez ativar-cliente DEV-956]] · [[10-Gate-A6-Treinamento-Kit-Cadencia-2026-06-28]]
