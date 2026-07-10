> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/adr/0001-stripe-em-vez-de-asaas.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0001-stripe-em-vez-de-asaas.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

---
adr: 0001
titulo: Stripe em vez de Asaas como gateway do Cadencia
data: 2026-05-11
status: aceito
---

# ADR-0001 — Stripe em vez de Asaas como gateway do Cadencia

## Contexto

Cadencia operava com Asaas v3 (Epic 5 DONE em produção). Felipe quer centralizar visualização de pagamentos no GHL Cadencia (subaccount agência nova). Asaas não tem integração GHL. GHL tem integração nativa com Stripe (Axis é a conta Stripe do Felipe).

Adicionalmente, há clientes B2B legados no Asaas (Sorria Rio, Vamos Sorrir, GCI GO, Nathalia, Rogéria, Alvina) que precisam ser migrados ou cancelados.

## Decisão

Trocar Asaas por Stripe **em big bang** (sem feature flag, sem convivência). Stripe vira fonte da verdade. Cancelamentos no Asaas executados em massa (33 subs + 82 boletos). 47 customers Asaas migrados pra Stripe pra preservar histórico/cadastro.

Pra ver pagamentos no GHL: webhook custom Stripe → GHL (cria Invoice paga + tags no Contact via API GHL).

## Alternativas avaliadas

| Opção | Por que descartada |
|---|---|
| Manter Asaas + sync paralelo pro GHL | Acumula 2 gateways. Asaas não integra nativamente com GHL nem com Customer Portal hospedado. |
| Stripe + criar subs como GHL Invoice Schedule | GHL Invoice recurring é menos refinada que Stripe Subscriptions (sem proration automática, trial complexo, etc). Cadencia tem lógica de créditos/addons que exige flexibilidade do Stripe. |
| Stripe com Custom Provider GHL apontando pra Asaas | Direção inversa (GHL→Asaas). Não resolve "ver no GHL o que rola no Stripe". |
| Sync Stripe→GHL via integração nativa GHL | NÃO funciona pra subscriptions criadas via Stripe API direto. Integração nativa só conhece transações que nascem no GHL. Validado empiricamente em 11/05. |

## Consequências

### Positivas
- Cadencia SaaS ganha flexibilidade do Stripe (proration, Customer Portal, addons one-time programáticos, trial Stripe se quisermos)
- Visualização unificada no GHL (via webhook custom)
- Cancelamento de 33 contratos Asaas obsoletos limpou base
- Conta Stripe Axis é livemode, BRL nativo, suporta cartão internacional

### Negativas
- Stripe BR não tem boleto nativo refinado (B2B GCI GO usa `send_invoice` que hospeda página, mas é diferente do boleto direto Asaas)
- Stripe BR cobra ~3,99% + R$0,39 por transação cartão (Asaas era ~2,99%)
- Refund precisa ser feito em 2 lugares se quiser fluxo perfeito (Stripe API faz; GHL API com PIT não permite void de invoice paga retroativamente — fica apenas como tag/nota)
- Nicole Berti permanece no Asaas (8 parcelas R$417 com cartão pré-autorizado já garantidas até nov/2026) — split parcial da base

### Neutras
- Migration Supabase mínima: tabela `stripe_webhook_log` + colunas `stripe_subscription_id`/`stripe_invoice_id` em `tenant_plans`. `tenant_config.config` JSONB acomoda `stripe_customer_id`.
- Bridge GHL existente via Workers Railway (`/api/v1/ghl/payment`) continua funcionando (recebe `tenant_id` + plan + value). Webhook Stripe novo chama o mesmo endpoint.

## Validação

Pagamento real R$199,90 (essencial) + addon R$49,90 + refunds completos rodaram E2E em 11/05/2026:
- Stripe Checkout funciona
- Webhook → Supabase libera créditos
- Webhook → GHL cria Invoice paga + tags automaticamente
- Refund → Supabase muda status='refunded' + tag GHL `refund-stripe`
- Tempo entre Stripe event → GHL invoice criada: ~1 segundo

3 bugs descobertos durante validação e corrigidos:
- `createInvoice` GHL exige `name`, `businessDetails`, `currency` por item (commit `1a1d565`)
- `charge.refunded` puxava tenant_id de `charge.metadata` (vazio) — agora cascata por subscription/PI (commit `24e2634`)
- Mirror GHL exigia `session.invoice` — não funciona pra addons one-time (commit `866e27b`)

## Referências

- Doc da feature: [docs/features/billing-stripe-ghl/README.md](../features/billing-stripe-ghl/README.md)
- Commits: `74634b8`, `674f620`, `1a1d565`, `24e2634`, `866e27b`
- Log de sessão: `Hub Projetos/Rotina/sessions-log/2026-05-11/cadencia-migracao-asaas-stripe-ghl_2026-05-11_2229.md`
