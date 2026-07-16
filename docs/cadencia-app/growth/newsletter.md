# newsletter — compilação semanal via Resend

## TL;DR

Compila os artigos elegíveis da semana e envia newsletter via Resend na sexta,
respeitando contatos assinantes, warm-up, compliance e dedup.

## Identidade

- **Path:** `pipeline/newsletter_generate.py`
- **Execução:** cron semanal; não roda no trigger on-demand
- **Provider:** Resend
- **Fonte:** `published_posts` + `public.contacts`

## Fluxo

1. seleciona posts ainda não incluídos na janela semanal;
2. monta digest e HTML do tenant;
3. carrega contatos `status=subscribed`;
4. aplica cap de warm-up e priorização;
5. envia com tags de tenant, contato e post;
6. grava logs/dedup e marca `newsletter_included` somente após processamento.

## Regras

- Newsletter não entra no trigger on-demand; o 202 deve devolver aviso.
- Não marcar posts antes de concluir a compilação/dispatch.
- Falhas transitórias precisam permanecer retomáveis.
- Bounce/complaint suprimem envios futuros.
- Sender, domínio e endereço vêm de `config.email`.

## Validação

```bash
pytest -q tests/test_newsletter_window.py \
  tests/test_dev477_newsletter_channel_ignored.py \
  tests/test_dev496_seinfeld_backlog_newsletter_feedback.py
```

## Troubleshooting

| Sintoma | Verificar |
|---|---|
| sexta sem envio | cron, timezone, posts elegíveis e contatos assinantes |
| duplicação | `newsletter_included` e logs idempotentes |
| baixa audiência | status dos contatos e cap de warm-up |
| eventos sem post | tags do envio e fallback Resend |

## Referências

- [seinfeld-email](seinfeld-email.md)
- [email-domain-provisioning](email-domain-provisioning.md)
- [scoring-leads](scoring-leads.md)
