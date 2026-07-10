---
date: 2026-07-04
tags: [documentacao, projeto, cs, billing, observabilidade]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Ariane Farrapo]]", "[[Cadencia-Growth]]", "[[Cadencia]]", "[[Central CS Onboarding]]", "[[Central-Observabilidade]]"]
---
# Hardening pós-ativação Ariane — billing, contratos e observabilidade (04/07/2026)

> Sessão Stamper 04/07. Issues Done: CSE-92, CSE-94, CSE-95, CSE-96, DEV-1176 (+ DEV-1168 no render do Cadencia). Worker de recarga em produção real. Fonte técnica: `pd-framework/times/cs/context/mapa-automacao-onboarding.md` + `sistema-central-onboarding.md`.

## O que mudou

### 1. Reconcile Asaas tolerante (CSE-92) — anti-duplicação de cobrança
`_shared/asaas_reconcile.py` agora casa parcelas em **2 passes com consumo 1:1**: exato `(vencimento, valor)` → tolerante (mesmo valor + até 31 dias de deslocamento, ou até 180 dias se o payment já está pago). Parcela reemitida/renegociada com data ajustada é reconhecida como a MESMA parcela.
**Por que importa:** as 6 parcelas da Ariane foram movidas pro dia 03 no Asaas — o match exato antigo listaria as 6 como "faltantes" e um `--apply` teria **duplicado R$6.970** de cobrança. Dry-run real pós-fix: `criar: []`. Direção conservadora: na dúvida, não cria.

### 2. Busca de contato em frentes (CSE-94) — anti-contato-duplicado
`_shared/crm_onboarding.py`: email primeiro (chave única tenant+email) → sobrenome como termo de 1 palavra (única busca que funciona hoje, DEV-946) → nome completo. Termo de 1 token só aceita match **único** — ambíguo vira pendência manual, nunca chute. O consolidador repassa o email pro passo CRM.

### 3. Créditos no frontmatter (CSE-95)
Template do `/elaborar-contrato` já gravava `creditos:`; backfill nos contratos pré-template com Cadencia — Mel = 100, OP Odontopenha = 80 (conferidos nas cláusulas). Desbloqueia o provisionamento automático de créditos do tenant.

### 4. Sync contrato ↔ Autentique (CSE-96)
Novo `_shared/contrato_autentique_sync.py`: consulta o Autentique ao vivo e promove `status:` → `assinado` + `signed_at` no frontmatter (só promove, nunca rebaixa; falha de rede não altera nada). Plugado no consolidador antes do parse.
**Achado da estreia:** a **Mel assinou o contrato em 01/07 e o sistema não sabia** (frontmatter congelado desde o envio em 22/06). Iasmin/Leonardo (não assinaram) e Juliana (parcial) corretamente não promovidos.

### 5. Worker recarga-creditos-mensal → PRODUÇÃO REAL
Autorização Felipe 04/07. Drop-in systemd com `RECARGA_APPLY=1` + log em arquivo. 1ª recarga real E2E: Ariane 2026-07 (UPDATE idempotente + marker na timeline + WhatsApp ao Felipe; re-run pula). Próximos ciclos automáticos: **Mel dia 19/07**, Ariane 03/08. Lembretes manuais CSE-76..80 ficam obsoletos após o dia 19.
**T-0 formalizado:** nota interna de aditivo no contrato da Ariane (T-0 real = 03/07/2026; F1 até 18/07, F2 até 01/10, F3 até 30/12; fidelidade até 03/01/2027; parcelas dia 03).

### 6. Observabilidade DEV-1176 — "tudo chega no Felipe"
- Pipeline carrossel/reels: falha TRATADA de step (`_fail_job`) e `render_failed` agora geram evento Sentry (antes só exception não-tratada).
- Ativações/onboarding: middleware 5xx no FastAPI captura respostas 500/503 tratadas.
- Growth (blog/seinfeld/linkedin/newsletter/instagram + retry provisioning): novo `lib_sentry.py` no `cadencia-growth`.
- Tudo desagua na Central existente: Sentry → bridge → issue Linear → gate → WhatsApp. E2E validado (evento de teste virou DEV-1178 automaticamente).
- Health-check: job novo `recarga-creditos-mensal (billing)` crit=true (PR #3 do repo health-check).

## Pendências que viraram issue
- DEV-1179 — token `gho_*` exposto no remote git do `/cadencia` (rotacionar + deploy key)
- DEV-1173 — enviar carrossel no WhatsApp do cliente (opt-in por tenant)
- Escopo restante do projeto: CSE-97→99→98→101 (cadeia pós-briefing) + CSE-93/103 (skill /ativar-cliente) + CSE-89/90/91/100/102 + DEV-1154

## Decisão organizacional
Projeto Linear **Automação do Onboarding CS (Fases 1-7)** agora concentra TODAS as issues da área autônoma de CS (Felipe, 04/07) — team CSE adicionado ao projeto, CSE-89..103 + DEV-1154 vinculadas.

## Notas Relacionadas
[[Projetos/Central CS Onboarding/Docs/04-Consolidador]] · [[Projetos/Central CS Onboarding/Docs/08-Workers-Acompanhamento]] · [[Projetos/Central CS Onboarding/Docs/11-Retrofit-Mel-Quevedo-13-Issues-2026-07-01]] · [[Central-Observabilidade]]
