---
date: 2026-05-14
tags: [cadencia, prd, ux, jornada, usuario, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]"]
---
# PRD — User Journeys (Cadencia.app)

## Journey 1 — Mariana, Nutricionista (Success Path)

**Perfil:** 43 anos, Goiânia, R$12k/mês, 800 seguidores. Canva instalado mas nunca abre. Tentou ChatGPT — "não entendi, larguei."

**Onboarding:**
- Responde perguntas via botões → paleta + slide preview em 2 min
- Dossiê dia seguinte (valida por seção)
- 3 editorias como cards
- ID Visual ("agências cobram R$3-5k")

**3 grátis:**
- Recebe 3 posts com SUA paleta. Copia, salva, posta. 2 min/post.

**Paywall:**
- 4º post → planos → checkout Asaas → paga → créditos liberados.

**1 mês:** 12 posts. "Nunca postei tanto." Renova.

---

## Journey 2 — Regeneração (Edge Case)

- Tom agressivo → "Gerar outro" → 30s novo carrossel
- 3x seguidas → "Quer ajustar preferências?" → ajusta editorias
- Offline → "Sem conexão. Posts salvos."

---

## Journey 3 — Felipe, Super Admin

- Desktop, sidebar completa
- Vê todos os tenants, custo médio, taxa de regeneração
- Troca modelo via Supabase sem deploy
- Paralisa tenant via feature flag
- Roda blog pipeline para si

---

## Journey 4 — Ricardo, Freelancer (V1.1)

- V1 (MVP): 5 clientes, 5 contas separadas
- V1.1: plano Agência — 1 login, 5 workspaces

---

## Journey 5 — Paywall + Pagamento

1. 3 grátis usados → tela de planos (10/30/60 posts)
2. Redirect Asaas → paga → webhook → créditos liberados
3. Não converteu: mantém histórico, bloqueia geração
4. Notificação 3 dias depois: "5 ideias esperando!"

---

## Notas Relacionadas

- [[Projetos/Cadencia/Docs/PRD-Executive-Summary]]
- [[Projetos/Cadencia/Docs/PRD-Functional-Requirements]]
- [[Projetos/Cadencia/Docs/PRD-Scoping-Roadmap]]
