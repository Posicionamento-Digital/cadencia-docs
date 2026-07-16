---
date: 2026-07-16
tags: [documentacao, framework, motor]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[PD Framework]]", "[[Motor-Autonomo]]"]
---
# Stale-Claim Reaper

> Vigia de claims: recupera issues `own:agente` presas em In Progress quando o executor morreu sem devolver — pinga, espera, e devolve pra fila. Em produção desde 2026-07-16 (DEV-1344).

**Path:** `_core/stale_claim_reaper.py` + wrapper `_core/stale_claim_reaper_cron.sh`
**Issues:** DEV-1131 (spec) · DEV-1286 (implementação, PR #57) · DEV-1344 (agendamento em produção)

## Por que foi construído assim

Executor (agente ou humano) claima uma issue e morre sem release — a issue fica presa em In Progress indefinidamente, ninguém mais pega, e é o único pedaço do lifecycle de claims que o Linear não resolve sozinho. O caso real: DEV-1167 e DEV-1101 presas por 6-7 dias geraram 6 issues duplicadas de health-check até resolução manual. O reaper foi implementado no PR #57 mas ficou **11 dias sem rodar em produção** — existia código, faltava cron. DEV-1344 fechou esse gap.

O fluxo do reaper aparece no diagrama do [Motor Loop](motor-loop.md#como-funciona) (faixa "vigia de claims").

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12, stdlib + `_shared/linear_client` + `_core/linear_claims` |
| Agendamento | cron da VPS Dev, `7 * * * *` com `flock` — fora do container, independente do motor |
| Credenciais | 1Password via wrapper (cron não herda profile; wrapper exporta o service account token) |

## Como funciona

1. Varre issues **In Progress** com label `own:agente` (a identidade de agente vem da label — o assignee é sempre o Felipe, não há usuário-bot).
2. Sinal de vida = `updatedAt` + comentários mais novos que o próprio ping.
3. **Estágio 1** — 48h sem atividade: comenta "⏳ stale-claim-reaper: ping — ainda ativa?".
4. **Estágio 2** — 24h após o ping sem resposta: `release(reason="stale: sem atividade")` — a issue volta pra fila. Nunca cancela nem reatribui.

## Decisões técnicas

- **2 estágios, nunca punitivo de primeira** — mesmo uma issue já muito stale no primeiro run recebe ping antes de release.
- **Dry-run por default** — só o cron roda `--apply`; execução manual sem flag apenas reporta.
- **Cap de 5 ações por run** — reaper enlouquecido não devolve o backlog inteiro.
- **Fora do container** — o reaper protege a fila mesmo com o motor desligado (foi exatamente com o motor OFF que os claims órfãos apodreceram).

## Gotchas & armadilhas

- **Rate-limit do 1Password derruba o run** — o erro sai explícito no log (`op CLI falhou: Too many requests`). O run seguinte recupera; **não** encurtar o intervalo do cron pra compensar — martelar agrava.
- **`In Review` é intocável** — trabalho legítimo em revisão nunca é pingado.
- **Issues `aguardando`/`bloqueado` são isentas** — espera legítima é estado válido.

## Como operar

```bash
# dry-run manual
python3 _core/stale_claim_reaper.py

# log de produção
tail -f pd-framework/.pd/stale-reaper.log

# conferir o agendamento
crontab -l | grep reaper
```

## FAQ

**O reaper devolveu uma issue que eu estava trabalhando — e agora?**
Claime de novo (o release só tira do In Progress; nada é perdido). Pra evitar: responda o ping em até 24h, ou marque `aguardando` se a espera é legítima.

**Por que a issue órfã demorou até 72h pra voltar pra fila?**
48h pro ping + 24h de graça pós-ping. É intencional (spec DEV-1131): falso release em issue viva custa mais caro que um dia extra de espera.

## Refs

- Spec: `times/dev/context/spec-stale-claim-reaper.md` (DEV-1131)
- Doc repo: `pd-framework/_core/docs/stale-claim-reaper.md`
- Incidente-gatilho: auditoria Central de Observabilidade 2026-07-13

---
Fonte repo: `pd-framework/_core/docs/stale-claim-reaper.md`

## Notas Relacionadas
[[Motor-Autonomo]] - [[Motor-Loop]]
