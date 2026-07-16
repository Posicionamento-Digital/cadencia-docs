# scoring/ — eventos Resend/Svix

## Responsabilidade

Receber eventos de email e atualizar score, temperatura, atribuição e supressão
dos contatos no CRM Cadência.

## Serviço ativo

| Arquivo | Porta | Função |
|---|---|---|
| `resend_webhook.py` | `8767` | recebe Resend/Svix, valida assinatura, deduplica e atualiza Supabase |

O handler antigo da porta `8766` é resíduo histórico e não deve receber tráfego.

## Fluxo

1. valida assinatura Svix;
2. deduplica por `svix-id`;
3. normaliza opened/clicked/bounced/complained;
4. resolve `tenant_id`, `contact_id` e `post_id` pelas tags;
5. usa `GET /emails/{id}` como fallback de tags;
6. atualiza `contacts` e grava `scoring_events`;
7. responde cedo e drena trabalho no shutdown.

## Regras

- Sem assinatura válida, rejeitar.
- Não confiar na ordem dos eventos.
- Patches concorrentes precisam ser condicionais.
- Bounce/complaint suprimem novos envios.
- Não registrar payloads com PII desnecessária.

## Testes

```bash
pytest -q tests/test_resend_webhook.py
```
