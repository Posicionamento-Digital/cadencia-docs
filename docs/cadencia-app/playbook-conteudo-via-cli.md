---
date: 2026-06-23
tags: [documentacao, projeto, cadencia]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[marketing]]"]
---
# Playbook — Produção de Conteúdo via Cadencia CLI

## O que é
Fluxo para produzir conteúdo editorial (blog, carrossel, LinkedIn, e-mail) operando o Cadencia 100% por linha de comando (cadencia-cli), sem tocar no banco nem na UI. Duas skills do Squad Social Media orquestram tudo:
- **/conteudo** — skill mestre guiada (de uma ideia ao pacote multi-canal)
- **/rafael-email** — e-mail avulso, criar e disparar sob demanda

## Princípios
- **Só via CLI.** Nunca SQL/Storage/service_role na mão. Gap vira issue no projeto Cadencia CLI/MCP de Controle.
- **Guiar, não adivinhar.** Cada decisão criativa passa pelo Felipe.
- **Travessões proibidos** em todo texto gerado (usar ponto/vírgula/dois-pontos).
- **2 OKs até o ar:** aprovar no chat (grava archived/draft) e dizer "publica" (vai a published).

## /conteudo — fluxo guiado
- **A0 Fonte da ideia (5):** digitar / ideia já no Cadencia / link de reportagem (WebFetch) / Readwise (highlights) / rede social via Apify.
- **A1 Canais:** blog / carrossel / LinkedIn (multi).
- **A2 Editoria:** a skill sugere Decifrar/Confrontar/Existir com justificativa, Felipe confirma.
- **A3 Headline:** gera 5, Felipe escolhe 1.
- **Por canal:** Blog (post + capa via image-upload + blog_url) · Carrossel (slides + imagens via slides-set) · LinkedIn (linkedin_text).
- **Fechamento:** marca ideia como used; publicar (2º OK) agenda Seinfeld + Newsletter automático.

## /rafael-email — avulso
- **Seinfeld:** corpo próprio via published-update --seinfeld-body + growth-dispatch --channel seinfeld --send.
- **Newsletter:** newsletter-dispatch --send.
- **SOAP:** bloqueado (engine de cadências CAD-579/580/581 não construído).

## Comandos cadencia-cli (grupo content) usados
ideas-create/update/status/get/list/delete · published-create/update/get/list/delete/unpublish · seo-update · image-upload · cover-set · documents-create/update/delete · slide-add/slides-set/slides-clear · growth-dispatch · newsletter-dispatch · calendar-add/gap/list

## Estado dos canais (jun/2026)
| Canal | Status |
|---|---|
| Blog (com capa + blog_url) | OK |
| Carrossel (slides + imagens) | OK (render PNG final: DEV-582) |
| LinkedIn | OK |
| E-mail Seinfeld / Newsletter | OK |
| SOAP | bloqueado (CAD-579/580/581) |
| Reels/TikTok / Threads | fora (Cadencia nao produz) |

## Issues (projeto Linear: Cadencia — CLI/MCP de Controle)
- DEV-777 (linkedin_text/seinfeld_body), DEV-789 (image-upload), DEV-790 (carrossel estruturado), DEV-791 (blog_url), DEV-792 (delete) — entregues.
- DEV-779 (SOAP) — bloqueada: premissa falsa (worker disparo-soap.py nao existe).

## Setup
```
cd Hub Projetos/_repos/cadencia-cli
export PYTHONIOENCODING=utf-8
CLI="python -m cadencia_cli.cli"
```
Tenant default = PD. Credencial via 1Password (Service Account). HTML/caption longos: chamar a CLI por subprocess (lista de args).

## Referências
- Skills: `times/marketing/comunicacao/social-media/skills/{conteudo,rafael-email}/SKILL.md`
- CLI: `_repos/cadencia-cli/docs/COMMANDS.md` + `_core/CADENCIA-CLI.md`
- Projeto Linear: Cadencia — CLI/MCP de Controle (7648831d)

## Histórico
- 2026-06-23 — Playbook criado. Skills /conteudo + /rafael-email construídas e validadas (blog + carrossel gravados via CLI no test-drive). 6 comandos novos entregues pelo time dev.