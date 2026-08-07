# ADR-0019 — Publicação social assíncrona com estado por canal

**Data:** 2026-08-07
**Status:** aceito

## Contexto

Instagram e LinkedIn podem levar tempos diferentes para concluir uma publicação. Manter o pedido aberto até o provedor terminar fazia a interface parecer travada; responder rápido sem acompanhar o resultado criaria falso sucesso.

## Decisão

O Cadência registra uma publicação independente por conteúdo e canal, responde assim que o pedido está validado e executa os efeitos externos em segundo plano. O app acompanha cada registro até `published` ou `failed`.

As publicações de um lote são processadas em paralelo. Chave de idempotência, lease e token de execução evitam replay. Quando o LinkedIn pode ter criado o post sem devolver uma resposta confiável, o sistema bloqueia retry automático até reconciliar o efeito externo.

## Consequências

**Positivas**

- A interface responde rápido sem declarar sucesso antecipado.
- Um canal lento ou com falha não segura o outro.
- Reload e replay não duplicam publicações conhecidas.
- Sucesso parcial fica representado com clareza.

**Custos aceitos**

- Polling curto enquanto o trabalho está pendente.
- Estado persistido adicional para leases, tentativas e resultado por canal.
- Reconciliação manual quando o resultado externo do LinkedIn é desconhecido.

## Alternativas descartadas

- Manter a requisição aberta até o provider terminar.
- Responder `202` sem acompanhar o estado real.
- Usar uma única linha de resultado para o lote inteiro.
- Repetir automaticamente toda falha do LinkedIn.

## Referência

- [Conexões e publicação social](../features/social-connections/index.md)
