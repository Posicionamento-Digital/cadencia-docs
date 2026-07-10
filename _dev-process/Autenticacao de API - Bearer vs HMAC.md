---
date: 2026-06-24
tags: [dev, seguranca, api, autenticacao, conceito]
moc: "[[MOC-Dev]]"
---
# Autenticação de API — Bearer token vs HMAC

> Como dois sistemas provam pra um endpoint que têm permissão de chamá-lo, e por que a escolha depende de **quem** consome (interno vs terceiros externos). Aprendizado registrado ao cancelar a DEV-582 (endpoint move-card do Cadencia).

## A diferença em uma frase

- **Bearer token:** você **manda o segredo** no header (`Authorization: Bearer <token>`). O servidor compara com o que ele guarda. Simples.
- **HMAC:** você **nunca manda o segredo**. Você usa o segredo pra **assinar** o conteúdo (`assinatura = sha256(timestamp + body + segredo)`) e manda só a **assinatura**. O servidor recalcula com o segredo dele e compara. O segredo nunca trafega pela rede.

Analogia: Bearer é mostrar a **chave** na portaria (se alguém te filmar, copiou a chave). HMAC é usar a chave pra **lacrar um envelope** — quem intercepta vê o lacre, mas não consegue forjar outro envelope sem a chave.

## O que o HMAC ganha (e por que webhooks usam)

1. **O segredo não trafega.** Vazou um log, um proxy, um print de request? Pegaram só a assinatura — inútil pra qualquer outro payload. Com Bearer, vaza o token inteiro e quem pegou usa até você rotacionar.
2. **Integridade do corpo.** A assinatura cobre o `body`. Se alguém adulterar o conteúdo em trânsito, a assinatura quebra. Bearer **não** protege o conteúdo — só diz "quem manda tem o token".
3. **Anti-replay.** A assinatura inclui um `timestamp`; combinada com uma *idempotency key*, impede reenviar a mesma requisição capturada.

É por isso que **Stripe, GitHub, Shopify** usam HMAC nos webhooks deles: o endpoint é **público** e recebe chamadas de **terceiros não totalmente confiáveis**.

## O custo do HMAC (não é de graça)

- O cliente tem que **assinar certo**: usar o **raw body** (antes de parsear/re-serializar), na ordem certa, com o encoding certo. Errar em qualquer detalhe → `401` chato de debugar.
- Mais código dos dois lados (assinar + verificar + skew de timestamp + dedup).

Bearer é muito mais simples: manda o token, compara, pronto.

## Quando usar qual

| Cenário | Escolha | Porquê |
|---|---|---|
| Endpoint **público**, consumido por **terceiros** (parceiros, sistemas que não são seus) | **HMAC** | segredo não vaza + integridade + anti-replay valem o custo |
| Comunicação **interna**, só seus próprios sistemas, sobre **TLS**, com segredos no cofre (1Password) | **Bearer + idempotency + rate-limit** | quase tão seguro, muito mais simples. HMAC seria over-engineering |

## O insight que fechou a decisão (contexto Cadencia)

Quando **tudo é interno** (a CLI consome a VPS Master protegida + o Supabase protegido), a **segurança já vem do controle de acesso ao ambiente** — quem não tem o PAT/chave SSH (guardados no 1Password) não roda nada. Nesse caso, **nem Bearer nem HMAC adicionam segurança**: seriam só mais um segredo no mesmo cofre.

A pegadinha: às vezes uma ação parece precisar de "endpoint seguro" mas o motivo real **não é segurança/acesso** — é **integridade de regra de negócio**. Ex.: um `enrich` que **debita crédito** e **chama API paga**. O risco de fazer direto no banco com a chave admin não é "um atacante", é **você mesmo** corromper o saldo ou gastar dinheiro 2× (sem idempotência). E isso se resolve **roteando a ação por um ponto único que aplica a regra** — tipicamente uma **Postgres function/RPC** — não por um endpoint HTTP com HMAC.

**Regra prática:** antes de construir o aparato de autenticação, pergunte *"o problema é QUEM chama (acesso) ou O QUE a chamada faz (regra de negócio)?"*. Só o primeiro pede token/HMAC. O segundo pede encapsular a lógica num lugar que não dê pra pular.

## Ver também
- [[Processo - PR e Deploy na Vercel]]
- DEV-582 (Linear, Cancelada) — discussão que originou esta nota.
