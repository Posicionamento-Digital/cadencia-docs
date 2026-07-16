# pipeline/ — geração, dispatch e provisioning

## Responsabilidade

Scripts Python que geram conteúdo, enviam email, executam cadências e
provisionam recursos do tenant.

## Componentes

| Arquivo | Função |
|---|---|
| `trigger_server.py` | endpoint on-demand `:39090` |
| `blog_generate.py` | geração/publicação de blog |
| `seinfeld_generate.py` | geração + dispatch Resend |
| `newsletter_generate.py` | newsletter semanal via Resend |
| `linkedin_generate.py` | geração/publicação LinkedIn |
| `instagram_generate.py` | geração/publicação Instagram |
| `cadence_tick.py` | scheduler único de cadências |
| `provision_tenant.py` | CRM, blog, domínio Resend e DNS |
| `email_warmup.py` | warm-up, cap diário e priorização |
| `sending_domains.py` | domínio/sender por tenant |
| `lib_api.py` | helpers Supabase e integrações compartilhadas |

## Fluxo diário

1. carrega tenants/configuração;
2. sincroniza o estado necessário do CRM Cadência;
3. executa os canais solicitados isoladamente;
4. aplica gates de provider e créditos;
5. registra estado e erros sem abortar tenants independentes.

## Regras

- Toda query/mutação inclui `tenant_id`.
- Email usa Resend e destinatários de `public.contacts`.
- Credenciais vêm do ambiente/1Password, nunca do repositório.
- Não duplicar helpers de `lib_api.py` em código novo.
- Não marcar canal como enviado antes da confirmação do provider.
- Não transformar erro técnico de insert em dedup legítimo.

## Validação

```bash
python -m compileall -q -x 'prompts_before\.py' pipeline
pytest -q tests
```
