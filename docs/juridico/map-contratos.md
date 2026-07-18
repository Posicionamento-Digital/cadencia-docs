---
title: Mapa Produto → Contrato
tags: [juridico, canon]
doc: Mapa Produto → Contrato
status: ativo
ultima_revisao: 2026-06-09
mantido_por: Vitória (Time Jurídico) + Felipe
---

# Mapa Produto → Contrato

> Regra única de roteamento: qual produto comercial da Cadencia usa qual template jurídico. Quando vender X, abrir o template Y. Consultado pelo `/elaborar-contrato`.

---

## 1. Princípio

**Um produto = um template.** Se o produto não está mapeado aqui, não há template — Felipe + Vitória decidem em sessão e atualizam este doc. Nunca improvisar contrato sem template ou misturar 2 templates sem antes consolidar num novo.

**Quando há combinação** (cliente compra treinamento + agente, ou consultoria + agente): usar 1 contrato base + **aditivo** específico, ou (se virar recorrente) criar template combinado novo.

---

## 2. Mapa principal

| # | Produto comercial | Tipo de relação | Template | Status |
|---|---|---|---|---|
| 1 | **Treinamento Prático Claude Code 30 dias** | Cadencia ensina, aluno aprende a criar agentes | `treinamento-claude-code/Contrato-Treinamento-Claude-Code-30d-Template.md` | ✅ ativo |
| 2 | **Consultoria de Gestão Empresarial** (5 fases) | Cadencia consultora, cliente implementa | `consultoria-gestao/V01-Contrato-Consultoria-Treinamento-Gestao-Empresarial-5fases.docx` | ✅ ativo |
| 3 | **Desenvolvimento de Agente IA Modular** (Agente + CRM + Agendamento + Tráfego) | Cadencia entrega software, cliente opera | `agente-ia/Contrato-Desenvolvimento-Agente-IA-Modular-Template-2025-12-18.docx` | ✅ ativo |
| 4 | **Jornada do Gestor de IA** (3 meses + revenue share) | Cadencia capacita cliente pra revender Cadencia | (versão Nicole 2025-12-18 em `contratos-emitidos/historico/`) | ⚠️ falta template puro |
| 5 | **Cadencia SaaS** (plano self-service) | Cadencia oferece SaaS, cliente assina | (não há contrato escrito hoje — usa termo de uso/política) | ❌ pendente decisão |
| 9 | **Cadência Bundle** (acesso + implantação + créditos + suporte CS + consultoria mensal) | Cadencia entrega onboarding white-glove + licença 6m com créditos inclusos | `cadencia-bundle/Contrato-Cadencia-Bundle-6meses-Template.md` (gerado caso Mel Quevedo 2026-06) | ✅ ativo |
| 6 | **Tráfego Pago** | Cadencia nunca prestou — só **contratou** Vortex | n/a (só `contratos-recebidos/`) | n/a |
| 7 | **Mentoria / Acompanhamento avulso** (caso Daniela Lima 2024) | Cadencia orienta marca pessoal | (legado em `contratos-emitidos/historico/Daniela-Lima-...`) | ⚠️ sem template puro |
| 8 | **MVP Customizado / Desenvolvimento sob medida** (projeto único) | Cadencia entrega sistema de IA/automação one-shot, cliente opera | `contratos-emitidos/<cliente>/Contrato-MVP-<Escopo>-<Cliente>-v1.md` (gerado caso a caso — base: template 3 adaptado) | ✅ ativo (caso Iasmin 2026-06) |

---

## 3. Detalhamento por produto

### 1. Treinamento Prático Claude Code 30 dias ⭐ ativo

**Quando usar:** cliente paga pra **aprender** a criar agentes IA usando Claude Code. Vai sair do treinamento com 1 agente rodando no caso real dele e capacidade de comercializar pros clientes próprios.

**Características do produto:**
- 30 dias corridos a partir do pagamento da 1ª parcela (T-0)
- 4 sessões individuais ao vivo (S1-S4) + 1 briefing (gratuito)
- Suporte WhatsApp 48h úteis durante 30 dias
- Bônus: Cadência grátis 30d + bônus específico do deal
- Requisito aluno: Claude Pro contratado antes da S1
- Preço atual: R$ 6.000 (12x R$ 500) ou R$ 5.000 à vista
- Sem reembolso (Cláusula 12.4)

**Cláusulas-chave a personalizar:** PARTES (qualificação completa), 1.3 (vi) bônus específico, 1.4 caso-base (Vayne tem Plug and Charge; Eliseu casos abertos), 3.1.1 data/hora briefing, 3.3 T-0 e fim vigência, 12.2 dia vencimento parcelas, 11.1 contatos.

**Casos emitidos:**
- Eliseu Batista Rocha (PDL-453, T-0 10/06/2026, briefing 12/06 9h)
- Vayne Antônio Saccaro (PDL-464, T-0 08/06/2026, briefing 12/06 14h)

---

### 2. Consultoria de Gestão Empresarial — 5 fases ⭐ ativo

**Quando usar:** cliente paga pra a Cadencia **consultar** e estruturar a gestão dele (Diagnóstico → Financeiro/CRM → Processos → OKRs → Consolidação). Foco em organização operacional, previsibilidade financeira e base pra escalar.

**Características do produto:**
- 18 cláusulas, 36k chars (versão completa da advogada)
- Vigência paramétrica
- Cadência: 1 reunião semanal 60-90min + acompanhamento diário 15-30min na implementação inicial
- Repositório oficial: Notion
- Remarcação por ciclo de 30 dias (2 grátis, 3ª com taxa, 4ª perdida)
- Matriz de rescisão proporcional por fase concluída

**Cláusulas-chave a personalizar:** PARTES, 3.4 vigência em meses, 5.3 valor hora técnica, 12.1 valor total, 12.2.b dia vencimento parcelas.

**Casos emitidos histórico:** Cadencia-Consultoria assinada por cliente A-IDENTIFICAR (em `contratos-emitidos/historico/`).

---

### 3. Desenvolvimento de Agente IA Modular ⭐ ativo

**Quando usar:** cliente paga pra a Cadencia **entregar e licenciar** um sistema de IA composto por até 4 módulos: (i) Agente IA — atendimento automatizado; (ii) CRM Cadencia; (iii) Sistema de Agendamentos e Automação; (iv) Gestão de Tráfego Pago. **Cliente opera depois.**

**Características do produto:**
- 15 cláusulas, 62k chars (versão completa da advogada — mesma estilo do V01)
- Módulo "Agente IA" obrigatório; outros 3 opcionais (checkboxes na cláusula 1.2)
- White-label sobre plataformas de terceiros (cliente arca com licenças)
- **Cláusula de FIDELIDADE** (Cl.10) — período mínimo sem rescisão livre
- **Limitação de Responsabilidade explícita** (Cl.7) — protege contra erros de IA em produção
- Custos operacionais de terceiros granulares (Cl.8)

**Cláusulas-chave a personalizar:** PARTES, 1.2 módulos contratados (X nas checkboxes), 3 fases de implementação (datas), 8 valor + custos operacionais, 10 período de fidelidade.

**Status emitidos:** nenhum em `contratos-emitidos/` atual — só template puro.

---

### 4. Jornada do Gestor de IA ⚠️ falta template puro

**Quando usar:** cliente paga pra ser **capacitado a operar e revender** os produtos da Cadencia como gestor próprio (mistura licenciamento de infraestrutura + treinamento + parceria comercial revenue share).

**Características do produto:**
- 87k chars (versão Nicole 2025-12-18)
- 3 meses de aceleração
- Licença de uso temporário de infraestrutura (servidor + n8n + CRM + Agendamento) + produtos digitais (templates + scripts)
- Parceria comercial após o programa com remuneração variável (revenue share)
- **NÃO inclui:** sociedade, vínculo empregatício, exclusividade comercial

**Status:** versão Nicole Berti Girotto está em `contratos-emitidos/historico/Nicole-Berti-Girotto-Jornada-Gestor-IA-Licenciamento-Aceleracao-3meses-2025-12-18.docx`.

**Pendência:** extrair template puro da versão Nicole (substituir qualificação Nicole por `[QUALIFICAÇÃO]`) e salvar em `templates/contratos/jornada-gestor-ia/Contrato-Jornada-Gestor-IA-3meses-Template.docx`. Ação: rodar quando a Cadencia voltar a vender esse produto.

---

### 5. Cadência (SaaS) ❌ decisão pendente

**Quando usar:** cliente contrata o SaaS Cadência (automação de prospecção). Recorrência mensal/anual.

**Situação atual:** não há contrato escrito hoje. Vinculação é por:
- Cadastro na plataforma → aceite implícito de Termos de Uso / Política de Privacidade
- Cobrança via Asaas/Stripe → recibo é o vínculo financeiro

**Decisões pendentes (Felipe + Vitória):**
- (a) Criar **Termos de Uso + Política de Privacidade** públicos no site Cadência (não exige assinatura individual — aceite por uso)
- (b) Criar contrato de SaaS por assinatura pra clientes enterprise (com SLA, fidelidade, valor anual)
- (c) Manter como está (risco: sem instrumento de cobrança ou rescisão se houver disputa)

**Recomendação Vitória:** opção (a) cobre 95% dos tenants normais, opção (b) entra quando vier o primeiro enterprise (deal acima de R$ 5k/mês).

---

### 6. Tráfego Pago n/a

**Quando usar:** **a Cadencia não vende esse serviço.** Felipe pessoa física CONTRATOU Vortex (VTX Charão) em 2024-12-04 e renovou 2025-01-14 — esses contratos estão em `contratos-recebidos/Felipe-PF/`.

Se algum dia a Cadencia passar a vender tráfego pago: criar template novo em `templates/contratos/trafego-pago/`. Por ora, **vetar** (escopo da Cadencia é IA, não mídia).

---

### 7. Mentoria/Acompanhamento avulso ⚠️ sem template puro

**Quando usar:** cliente paga acompanhamento de marca pessoal / mentoria pontual (não é treinamento técnico, não é consultoria estruturada). Caso histórico: Daniela Lima 2024 (mentoria de marca pessoal, 3 meses, 10 encontros, fases Diagnóstico+Branding+Storytelling+Vendas).

**Pendência:** se a Cadencia voltar a vender mentoria avulsa, extrair template puro da versão Daniela e salvar em `templates/contratos/mentoria-avulsa/`. Por ora, raramente vendido (último caso 2024).

---

## 4. Casos especiais (combinações)

### Cliente contrata Treinamento + Agente IA depois

**Fluxo:**
1. Emite **Contrato Treinamento Claude Code 30d** (template 1) na 1ª venda.
2. Após conclusão da S4, se cliente quiser que a Cadencia entregue o agente em produção pra ele (não fazer o cliente operar): emite **Contrato Agente IA Modular** (template 3) como **novo contrato** (não aditivo).
3. Cláusula de PI do treinamento (3 camadas) continua valendo — o agente do aluno é dele; a Cadencia entregando outro sistema é negócio novo.

### Cliente contrata Consultoria Gestão + Agente IA juntos

**Fluxo:**
1. Tentar separar em **2 contratos** (template 2 + template 3) — escopos jurídicos diferentes (consultoria = obrigação de meio; agente = entrega de produto).
2. Se cliente insistir em 1 contrato único: criar **versão combinada nova** (Vitória redige, Marcelo carimba) e salvar como template novo em `templates/contratos/consultoria-mais-agente-ia/`. Documentar a fusão nesse mapa.

### Cliente contrata Cadencia SaaS + Agente IA customizado

Misturar SaaS com entrega customizada é arriscado juridicamente (regimes de responsabilidade muito diferentes). **Recomendação:** dois instrumentos separados:
- Termos de Uso Cadência (sem assinatura)
- Contrato Agente IA Modular (assinado)

---

## 5. Fluxo de escolha (decision tree)

```
Cliente paga pra...
├── APRENDER a fazer agentes IA com a Cadencia? → template 1 (Treinamento Claude Code)
├── A Cadencia CONSULTAR / estruturar gestão dele? → template 2 (Consultoria Gestão)
├── A Cadencia ENTREGAR um sistema IA pra ele operar? → template 3 (Agente IA Modular)
├── REVENDER produtos Cadencia como gestor próprio (revenue share)? → template 4 (Jornada Gestor IA — pendente template puro)
├── Usar SaaS de prospecção (Cadência)? → Termos de Uso (não há contrato individual hoje)
├── Mentoria de marca pessoal / acompanhamento avulso? → template 7 (pendente — recriar a partir da versão Daniela)
└── Algo que não bate em nenhum acima? → sessão Felipe + Vitória + Marcelo
```

---

## 6. Regras de manutenção deste mapa

1. **Toda nova venda inédita** (produto novo) → atualizar este mapa **antes** de emitir o contrato. Sem template aqui, sem envio.
2. **Toda evolução do produto** (novas cláusulas, mudança de bônus padrão, novo SLA) → atualizar o template canônico em `templates/contratos/<tipo>/` **e** registrar no campo "Última revisão" deste mapa.
3. **Templates legados** (Daniela 2024, Jornada Nicole) ficam em `contratos-emitidos/historico/`. Quando virarem template puro, mover pra `templates/contratos/<tipo>/` e marcar aqui como ✅ ativo.
4. **Marcelo Oliveira** carimba qualquer mudança estrutural em cláusulas de PI, fidelidade, rescisão proporcional ou limitação de responsabilidade. Vitória rascunha; Marcelo aprova; Felipe decide.

---

## 7. Refs

- `templates/contratos/` — pasta dos templates canônicos
- `contratos-emitidos/` — adaptações por cliente (ativo) + histórico
- `contratos-recebidos/` — contratos que a Cadencia/AXIS/Felipe-PF receberam (n/a pra este mapa)
- `skills/elaborar-contrato.md` — consulta este mapa pra resolver `<tipo>` → template
- `context/marcelo-talissa.md` — escopo dos assessores externos
- `memory/decisions.md` — D1 (criação Time Jurídico), D2 (renomeação/organização inicial)
