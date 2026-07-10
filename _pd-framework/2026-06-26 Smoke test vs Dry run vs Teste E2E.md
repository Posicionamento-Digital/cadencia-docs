---
date: 2026-06-26
tags: [aprendizado, tecnologia]
moc: "[[MOC-IA-Tecnologia]]"
---

## Contexto
Esclarecimento de três termos de teste que costumam ser confundidos — smoke test, dry run e teste E2E — surgido ao validar uma implementação (o Client Activity Logger do pd-framework). A confusão comum é tratá-los como níveis da mesma escala; na verdade são eixos diferentes.

## O que foi discutido

### Smoke test
Teste raso de "acende ou explode?". Roda o caminho principal **uma vez** pra ver se não quebra na cara — não cobre casos de borda, só o básico. A origem do nome: ligar o aparelho e ver se sai fumaça.

### Dry run
Execução de mentira, **sem efeito colateral real**. O código roda a lógica toda mas não comita a ação (não grava no banco, não envia email, não cria nada). Serve pra inspecionar o que *aconteceria*. É um **modo de execução**, não um tipo de teste.

### Teste E2E (end-to-end)
Valida o fluxo inteiro, **ponta a ponta, com as integrações reais** — da entrada até o efeito final no sistema externo, sem mocks no meio.

## Decisões e Conclusões

As distinções que importam:

- **Smoke x E2E** — ambos rodam de verdade, diferem em **profundidade**. Smoke = 1 caminho feliz, não morreu. E2E = fluxo completo com bordas e integração real.
- **Dry run x os outros** — dry run é o oposto de "real": **não toca o sistema externo**. Smoke e E2E reais tocam.
- **São dois eixos independentes:** *profundidade* (smoke -> E2E) e *realidade do efeito* (dry run -> real). Dá pra ter um E2E em dry run (fluxo todo sem comitar) ou um smoke real (1 caminho, com efeito).

Exemplo concreto (DEV-873, Client Activity Logger):
- **Dry run** (`apply=False`): resolve cliente + projeto + slug e monta tudo, mas nao cria o registro real no Linear.
- **Smoke E2E real** (create -> list -> delete): prova que a integracao com a API fecha o ciclo inteiro de ponta a ponta.