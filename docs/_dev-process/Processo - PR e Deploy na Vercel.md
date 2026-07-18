---
date: 2026-06-17
tags: [dev, processo, vercel, deploy, pr, git, luiz, ia, tecnologia, automacao]
moc: "[[MOC-Dev]]"
---
# Processo — PR e Deploy na Vercel (Time Dev)

> Como mandar código pra produção nos projetos hospedados na Vercel da conta do Felipe
> (hoje: **cadencia-app** → cadencia.ia.br). Vale pra dev externo e qualquer dev do time.

## Por que existe (leia, não pule)

A conta Vercel do Felipe é **plano Hobby**. Nele, o deploy de **produção** só roda se o
**autor do commit no topo da branch de produção** for o dono da conta (`felipeluissalgueiro`).

Quando **outro dev mergeia** um PR (ex: Luiz, conta `luizsidiao`), o merge commit fica autorado
por essa conta → a Vercel marca o deploy de produção como **BLOCKED** e o site **não atualiza**.

Já aconteceu: ~28 merges feitos pela conta do dev externo ficaram bloqueados e a produção do
cadencia-app congelou por dias (previews funcionavam, só produção travava).

**Regra de ouro:** quem mergeia na produção é o **Felipe**. O dev entrega via PR; o merge é do dono.

## O que o dev (dev externo) FAZ

1. **Trabalhe sempre numa branch**, nunca direto no `master`/`main`.
	- Convenção: `feat/pdl-XX-descricao`, `fix/descricao`.
	- Base da branch = branch de produção. No **cadencia-app é `master`** (NÃO `main` — a `main` é morta; PR contra ela não vai pra produção).
2. **Commite e dê push** na sua branch.
3. Quando estiver **pronta pra revisão**, sinalize de **um** jeito:
	- Tag **`[pronto]`** (ou `[ready]` / `[pr]`) na mensagem do **último commit**; **ou**
	- No GitHub, clique em **"Ready for review"** no PR.
4. **Não mergeie.** Pronto.

## O que o dev NUNCA FAZ

- ❌ Mergear PR no `master`/`main` de produção (trava o deploy — é a causa do problema).
- ❌ Push direto no `master`.
- ❌ Abrir PR contra `main` no cadencia-app (use `master`).

## O que acontece automaticamente

- Worker `pr-watcher` (VPS dev, a cada 10 min) detecta sua branch e **abre um PR draft** sozinho.
- Quando você sinaliza **pronto**, o worker **avisa o Felipe no WhatsApp** com o link do PR.
- O **Felipe revisa e mergeia pela conta dele** → o deploy de produção é **liberado**.

## Resumo de 1 linha

> Branch → `[pronto]` no último commit (ou "Ready for review") → **o Felipe mergeia**. Nunca mergeie você mesmo na produção.

## Referências técnicas

- Worker: `pd-framework/times/infra/workers/pr-watcher.py`
- Processo no framework: `pd-framework/times/dev/foundation/processo-pr-deploy-vercel.md`
- Aprovação Felipe: skill `/aprovar-pr` (Claude Code local).

## Notas Relacionadas
[[Processo - Desenvolvimento (Time Dev)]] — processo completo (cascata, modos, reviews, personas)
