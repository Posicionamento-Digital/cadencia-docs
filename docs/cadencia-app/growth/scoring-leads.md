# scoring-leads — scoring via Resend/Svix

## TL;DR

O daemon `scoring/resend_webhook.py` recebe eventos de email do Resend na porta
`8767`, valida a assinatura Svix, resolve tenant/contato/post pelas tags do envio
e atualiza score, temperatura e supressão no CRM Cadencia (Supabase).

O antigo handler da porta `8766` é código histórico até o cleanup e não deve
receber tráfego nem ser reativado.

## Identidade

- **Tipo:** daemon HTTP Python
- **Path:** `/cadencia/scoring/resend_webhook.py` (VPS Master)
- **Porta:** `RESEND_WEBHOOK_PORT`, default `8767`
- **Status:** ativo
- **Deps:** Resend, assinatura Svix, Supabase `contacts` e `scoring_events`

## Como funciona

1. Resend envia `email.opened`, `email.clicked`, `email.bounced` ou `email.complained`.
2. O handler valida a assinatura quando `RESEND_WEBHOOK_SECRET` está configurado.
3. `svix-id` fornece a chave de idempotência.
4. As tags `tenant_id`, `contact_id` e `post_id` atribuem o evento.
5. Se tags faltarem no payload, `GET /emails/{id}` recupera os metadados.
6. Open soma 2 pontos e click soma 5; as bandas são Frio (<30), Aquecendo (>=30), Quente (>=60) e Hot (>=80).
7. `email.bounced` e `email.complained` atualizam a supressão do contato.
8. O evento atribuído é persistido em `scoring_events`.

O processamento responde HTTP 200 cedo para não estourar o timeout do Svix,
mas o shutdown drena o trabalho pendente. Cache e patches condicionais evitam
perda de eventos concorrentes.

## Limite atual

O scoring atualiza score, banda e eventos no CRM Cadencia. Movimento automático
de oportunidade deve usar as automações do CRM próprio; não existe fallback ou
ação a jusante em serviço externo.

## Gotchas

- Não aceitar webhook sem validar Svix em produção.
- Não remover `post_id` das tags: ele liga o evento ao conteúdo correto.
- Não assumir ordem de entrega dos eventos.
- Não reabrir a porta histórica `8766`.
- O endpoint público do Resend precisa de HTTPS, mesmo que o daemon interno use HTTP.

## Como validar

```bash
pytest -q tests/test_resend_webhook.py
```

Validar também assinatura inválida, evento duplicado, fallback de tags,
bounce/complaint e drenagem no shutdown.

## Referências

- [email-scoring-hardening-2026-07](email-scoring-hardening-2026-07.md)
- [seinfeld-email](seinfeld-email.md)
- [newsletter](newsletter.md)
