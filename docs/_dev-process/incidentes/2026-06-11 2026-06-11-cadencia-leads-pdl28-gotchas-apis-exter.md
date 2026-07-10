---
type: source
source_kind: incidente
date: 2026-06-11
entities: ["[[Cadencia]]", "[[qualidade]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-06-11_cadencia-leads-pdl28-gotchas-apis-externas-debug

# Incidente: Aba Leads (PDL-28) — 7 defeitos corrigidos em produção no dia do lançamento (gotchas de APIs externas + UI mascarando erro)

**Data:** 11/06/2026
**Severidade:** Média (feature nova; nenhum dado perdido; créditos sempre estornados em falha)
**Projeto:** Cadência
**Duração do impacto:** ~4h de iteração teste-fix entre o primeiro teste do Felipe e a busca funcionando
**Tags:** #cadencia #datastone #api-externa #frontend #billing #debug-polya #leads

## Contexto

PDL-28 (enriquecimento DataStone como add-on) foi do zero a produção no mesmo dia: waterfall portado do openclaw-legacy, créditos, GHL por tenant, busca de leads. Os testes do Felipe em produção revelaram uma sequência de defeitos — todos corrigidos e validados contra as APIs reais. Registro consolidado pra ninguém reaprender essas pegadinhas.

## Defeitos corrigidos (em ordem de descoberta)

1. **CNPJ como NUMBER no JSON da DataStone** (`/company/list/`, `/b2b/companies/`): CNPJ com zero à esquerda perderia dígitos e seria rejeitado (ex.: Banco do Brasil `00.000.000/0001-91`). Fix: `cnpjFromApi()` com padStart(14) quando origem é numérica. Commit `23b6c5c`.
2. **Placeholder `"NÃO INFORMADO"` da DataStone é truthy**: pulava indevidamente os fallbacks B2B e Apollo. Fix: `informed()` trata placeholders como vazio. Commit `3698fed`.
3. **Filtro `setor` NÃO existe na API B2B** (`Bad request`) e zera resultados quando combinado. O parse extraía setor → busca morta. Fix: setor incorporado ao `nome_empresa`. Commit `c86ec57`.
4. **Parse LLM morto em silêncio** (OPENAI_API_KEY da Vercel — suspeita = chave da PDL-491 pendente de rotação): fallback jogava a FRASE INTEIRA como termo → B2B retorna 0. Fix: parser heurístico determinístico + sanity-check do LLM. Commit `94e1172`.
5. **Busca por razão social não acha nome fantasia** ("Padaria Real Sorocaba" = razão "Real Alimentos Ltda"). Fix: cascata razão social → B2B fuzzy → Perplexity (nome popular → CNPJ), com Perplexity rodando também quando nenhum resultado é da cidade citada. Commits `2cbc89b` + `9e63a6d`.
6. **Filtro de cidade do B2B é FROUXO** (busca por Sorocaba retornava Barueri/Embu). Fix: ranking prioriza localização que bate com a cidade pedida, nos dois modos. Commit `e14d732`.
7. **CAUSA RAIZ FINAL da busca "nenhuma empresa encontrada"** (debug-polya completo): o match do B2B exige **frase natural NO SINGULAR** — `"clinica de estetica"` acha 3, `"clinicas estetica"` acha 0 — e cidade sem preposição/fora do mapa ficava embutida no termo. Fix: `term-variants.ts` gera até 4 variantes determinísticas (singulariza, reconstrói "X de Y", move última palavra pra cidade) com retry em cadeia. Validação: achou HARMONIE CLÍNICA DE ESTÉTICA ARARAQUARA LTDA pro input real do Felipe. Commit `b60a629`.

Hipóteses refutadas com evidência durante o debug-polya: Cloudflare/proxy cortando resposta (DNS aponta direto pra Vercel) e maxDuration não aplicado (rota de sleep 90s respondeu 200 pelo stack completo).

## Causa raiz sistêmica

1. **UI mascarava o erro real**: "Erro de conexão na busca" cobria QUALQUER falha (HTML em vez de JSON, 4xx, exceção JS, e até o caso "0 resultados"). 3 ciclos de fix foram gastos em sintomas porque o texto na tela não distinguia nada. Fix estrutural: instrumentação exibindo HTTP status + código + mensagem real (commit `ecb8ba9`).
2. **Comportamento real das APIs externas ≠ doc/expectativa**: DataStone tem semântica não documentada (number vs string, placeholders, filtros inexistentes, sensibilidade singular/frase). Só teste contra a API real revela — o e2e local com bundle esbuild do código real (sem deploy) foi a ferramenta decisiva.
3. **Falha silenciosa de dependência LLM**: o fallback "gracioso" do parse escondeu por horas que a OpenAI key está quebrada. Graciosidade sem telemetria = bug invisível.

## Prevenção

- **Toda integração externa nova: validar cada filtro/campo contra a API real ANTES do deploy** (bundle esbuild + node local custa minutos e pegou 5 dos 7 defeitos).
- **Mensagem de erro de UI nunca genérica**: sempre status + código; "0 resultados" não é erro e precisa de copy própria.
- **Fallback silencioso de LLM precisa registrar o motivo** (steps/log) — e a PDL-491 (rotação OpenAI key) virou bloqueadora de qualidade do parse.
- **Pedir o texto EXATO do erro ao usuário antes de hipotetizar** — "erro na busca" gerou 3 fixes de sintoma; o texto real ("nenhuma empresa encontrada") fechou a causa em 1 ciclo.

## Refs

- Issue: PDL-28 (Done) · Follow-ups: PDL-530 (busca censitária CNAE), PDL-531 (location tokens), PDL-532 (CSV em massa)
- Plano técnico: `times/produto/cadencia/context/plano-PDL-28.md`
- Reviews: `cadencia-app/docs/runtime-fix-reviews/runtime-fix-review-11-06-2026.md`
