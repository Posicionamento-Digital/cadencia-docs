# seinfeld-email — geração e dispatch Resend

## TL;DR

Gera email narrativo a partir de `published_posts`, agenda e envia via Resend
para contatos assinantes do CRM Cadência.

## Identidade

- **Path:** `pipeline/seinfeld_generate.py`
- **Modos:** `--generate` e `--dispatch`
- **Provider:** Resend
- **Contatos:** `public.contacts`, `status=subscribed`

## Generate

1. seleciona post elegível ainda não usado;
2. gera assunto, corpo, CTA e preheader;
3. encontra o próximo slot livre;
4. grava `seinfeld_scheduled_at` e conteúdo sem marcar envio.

## Dispatch

1. seleciona o item vencido mais antigo (`scheduled_at <= hoje`, limite 1);
2. aplica cap de warm-up e priorização por engajamento;
3. reserva dedup atômico por contato/post;
4. envia HTML/texto via Resend com tags de tenant, contato e post;
5. grava audit log e marca o post quando não há falha transitória pendente.

## Invariantes

- `config.email` é a configuração canônica do sender.
- `seinfeld_daily_sent` impede duplicação cross-day.
- Falha técnica de dedup não autoriza envio.
- Bounce/complaint removem o contato dos próximos dispatches.
- Rodapé, endereço e `List-Unsubscribe` são obrigatórios quando aplicáveis.
- Backlog retoma um post por execução para evitar rajada.

## Validação

```bash
pytest -q tests/test_seinfeld_classify_send.py \
  tests/test_seinfeld_crossday_dedup.py \
  tests/test_seinfeld_generate_gate.py \
  tests/test_seinfeld_sb_insert.py \
  tests/test_seinfeld_slots.py
```

## Troubleshooting

| Sintoma | Verificar |
|---|---|
| não gera | post elegível, créditos, `email_sending_enabled` |
| não envia | contatos assinantes, cap diário, domínio/sender verificado |
| evento sem atribuição | tags e fallback `GET /emails/{id}` |
| duplicação | constraint/audit de `seinfeld_daily_sent` |

## Referências

- [email-domain-provisioning](email-domain-provisioning.md)
- [email-scoring-hardening-2026-07](email-scoring-hardening-2026-07.md)
- [newsletter](newsletter.md)
