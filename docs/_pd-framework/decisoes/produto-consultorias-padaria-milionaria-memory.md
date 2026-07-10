---
type: source
source_kind: decisao
date: 
entities: ["[[produto]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---

# Decisões — produto-consultorias-padaria-milionaria-memory

# Decisions — Padaria Milionária

> Decisões com impacto duradouro no projeto. Mais recente em cima.

---

## 2026-05-27 — Telegram como plataforma do agente

**Contexto:** Felipe propôs trocar WhatsApp por Telegram na reunião de retomada.
**Decisão:** Telegram é a plataforma do Coach de IA.
**Alternativas descartadas:** WhatsApp — menos recursos, sem mini-app nativo com botões.
**Impacto:** Build do agente usa API do Telegram. Mini-app com botões (abrir dia, fechar dia, ficha técnica).
**Quem decidiu:** Felipe + Jailson (reunião 27/05/2026).

---

## 2026-05-27 — Clube da Cotação fora do escopo

**Contexto:** Integração de cotações de compras via API estava listada como "a confirmar" desde o briefing de março.
**Decisão:** Descartada — fora do escopo do MVP.
**Alternativas descartadas:** Manter como fase 2 — decidido que não vale agora.
**Impacto:** Nenhuma integração Clube da Cotação no build atual.
**Quem decidiu:** Felipe (confirmado 27/05/2026).

---

## 2026-05-27 — Pasta de materiais no pd-framework (OneDrive)

**Contexto:** Precisava de local para troca de materiais entre PD e cliente.
**Decisão:** Usar `times/produto/consultorias/padaria-milionaria/materiais/recebidos/` — já está no OneDrive, compartilhável via link do Explorer.
**Alternativas descartadas:** Pasta separada em `Posicionamento Digital Inc\Clientes\` — duplicação desnecessária.
**Impacto:** Materiais do cliente chegam direto na pasta do squad. Workflow: cliente sobe → PD consome.
**Quem decidiu:** Felipe (sessão 27/05/2026).

---

## 2026-02-05 — Proposta simplificada para R$12.500

**Contexto:** Proposta original incluía CRM + RFV — complexidade elevada para o cliente.
**Decisão:** MVP focado em Coach de IA + 6 planilhas + checklists. Valor: R$12.500 (vs R$30.000 inicial).
**Alternativas descartadas:** Proposta completa com CRM/RFV — cliente não estava pronto.
**Impacto:** Escopo reduzido e mais executável. Modelo de parceria pós-piloto em análise (comissão, white-label, licenciamento).
**Quem decidiu:** Felipe + Alvina + Jailson (reunião 05/02/2026).
