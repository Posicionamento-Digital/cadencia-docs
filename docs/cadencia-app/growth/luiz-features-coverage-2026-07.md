# Cobertura das entregas do Luiz — cadencia-growth

Baseline documental: `0c1c332` (execução de `/documentar-software` em 27/06/2026). Commits funcionais do ciclo posterior estão agrupados abaixo.

| Documento | Capacidades | Commits |
|---|---|---|
| [email-scoring-hardening-2026-07](email-scoring-hardening-2026-07.md) | atribuição, Svix, idempotência, compliance | `ea89d69`, `f9e10b5`, `a500daf`, `add3363`, `335c9e8`, `b9be83b`, `1dfae9f`, `dff0d92` |
| [email-domain-provisioning](email-domain-provisioning.md) | objeto canônico, writers e save atômicos | `f012d1b`, `562559b`, `8bc4ad8`, `c573e1d`, `c51ca68`, `b8bec9c`, `6d4aafd` |
| [email-scoring-hardening-2026-07](email-scoring-hardening-2026-07.md) | personalização, rate limit e gates por provider | `32cfa32`, `5a1e110`, `7f7e6f6`, `2e41357`, `a8fe562`, `2cecbf8` |
| [cadence-engine](cadence-engine.md) | scheduler único e gatilhos | `80dc7d7`, `87e8e81`, `ddfe418`, `d832dac`, `04f5892` |

Commits posteriores de observabilidade, newsletter timeout e retry de provisioning feitos por outros fluxos/agentes permanecem nos documentos próprios, mas não foram atribuídos ao Luiz nesta matriz.

## Verificação

```bash
git log 0c1c332..main --no-merges --pretty='%h %an %cn %s'
```
