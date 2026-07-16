# Email e scoring — hardening do ciclo 2026-06/07

## Escopo

Complementa [email-domain-provisioning](email-domain-provisioning.md), [email-resend-migration](email-resend-migration.md), [scoring-leads](scoring-leads.md), [seinfeld-email](seinfeld-email.md) e [newsletter](newsletter.md) com os invariantes adicionados depois da última documentação completa de 27/06.

## Atribuição e ingestão de eventos

- Senders adicionam `post_id` às tags do Resend; `scoring_events.post_id` liga abertura/clique ao email correto.
- O webhook responde 200 ao Svix antes do processamento pesado para evitar timeout do provedor.
- `svix-id` é a chave de idempotência; eventos repetidos não somam score novamente.
- Evento é normalizado para o vocabulário interno com underscore.
- Ausência da tag é recuperada via `GET /emails/{id}`.
- Em `SIGTERM`, o processo drena o trabalho em andamento; cache usa lock e updates são condicionais.

## Provisionamento e configuração

`config.email` é a casa canônica. Leitores usam objeto-primeiro e fallback flat; writers chamam `merge_tenant_config_email`, que preserva alterações concorrentes. O provisionamento cria domínio, DNS e tracking, mas só habilita Resend quando o domínio está verificado. O save final também usa merge atômico.

## Envio e compliance

- `cta_label` e `preheader` são customizáveis por tenant/canal.
- Resend é limitado para respeitar rate limit.
- Retry cross-day do Seinfeld não reenvia o mesmo post ao mesmo contato.
- Rodapé inclui unsubscribe e omite endereço postal vazio; nenhum placeholder falso vai para produção.
- LinkedIn usa sua integração própria; Seinfeld e newsletter usam Resend.

## Gotchas

- Responder 200 cedo sem dedupe e durabilidade perde ou duplica eventos.
- `post_id` ausente degrada atribuição; monitore o fallback da API do Resend.
- Flat keys são espelho temporário e não podem receber write isolado.
- Provider não deve virar Resend antes da verificação do domínio.
- Tracking depende do DNS de links, não apenas DKIM/SPF.

## Validação

```bash
pytest -q
python scripts/email_resend_preflight.py
```
