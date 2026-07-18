---
title: DRE Structure — Padrão S-1
tags: [financeiro, canon]
---

# DRE Structure — AXIS / PD (padrão SaaS NASDAQ-grade)

> Estrutura de DRE no padrão de empresas tech públicas (HubSpot/Atlassian/Shopify S-1).
> **Status:** template definido, dados aguardam fechamento atualizado.
> **Fonte futura:** definir com Felipe quando arquivo atualizado existir (Mar/26 está desatualizado).

---

## Princípio (mindset NASDAQ)

DRE de tech pública obedece 4 princípios:

1. **Receita segmentada por tipo** — Subscription (recorrente) vs Professional Services (one-time) vs Other. Investidor pune empresa que mistura.
2. **Cost of Revenue ≠ OpEx** — separar o que é custo direto de servir o cliente (hosting, partner platforms, customer support direto) do que é OpEx funcional.
3. **OpEx por função, não por natureza** — Sales & Marketing (S&M), Research & Development (R&D), General & Administrative (G&A). Cada uma é uma alavanca de gestão independente.
4. **GAAP + Non-GAAP + métricas SaaS** — Operating Income GAAP é o ponto de partida. Adjusted EBITDA + Rule of 40 + Net Revenue Retention são o que o mercado realmente olha.

---

## P&L — Profit & Loss (formato S-1)

### Template mensal (em R$)

```
                                                Mês XX/AA   % Rev.
─────────────────────────────────────────────────────────────────
REVENUE
  Subscription Revenue
    Clinics Segment                              _______     __%
    Other Recurring                              _______     __%
  Professional Services Revenue                  _______     __%
  ─────────────────────────────────────────────
  TOTAL REVENUE                                  _______    100,0%

COST OF REVENUE
  Third-party Platforms (delivery)               _______
    CRM Cadencia (CRM/automation próprio — substitui HighLevel; HighLevel sendo cancelado, ⏳ CAD-683/CAD-600)
    Bubble (no-code apps)
    HeyGen / AutomArticles / Uzapi
  AI/API Costs (cost-of-goods)                   _______
    OpenAI API
    Elevenlabs (voice)
  Customer Success / Support (direto)            _______
  ─────────────────────────────────────────────
  TOTAL COST OF REVENUE                          _______     __%

GROSS PROFIT                                     _______
GROSS MARGIN                                                  __%  (benchmark SaaS: 70-85%)

OPERATING EXPENSES (por função)
  Sales & Marketing (S&M)                        _______
    Demand gen tools (Selo IG, LinkedIn, etc)
    Sales tools (Pipedrive)
    Ads pagos

  Research & Development (R&D)                   _______
    AI tooling de produto/dev (Claude, Cursor)
    Infra produto (Hetzner, Hostinger)
    Plataformas internas (Obsidian/Linear, Workspace alocação P)

  General & Administrative (G&A)                 _______
    Personnel (pró-labore + payroll + freelancers)
    Legal & Professional fees
    Banking & Financial costs (juros, IOF)
    Income taxes — DAS (porção não-ISS)
    Training (capacitação)
    Travel & Representation
    Equipment / Depreciation
  ─────────────────────────────────────────────
  TOTAL OPEX                                     _______

OPERATING INCOME (LOSS)                          _______
OPERATING MARGIN                                              __%

Net interest / other (juros + IOF)               _______
─────────────────────────────────────────────
INCOME BEFORE TAX                                _______

Income tax (Simples Nacional — porção IR/CSLL embutida no DAS)
─────────────────────────────────────────────
NET INCOME (LOSS) — GAAP                         _______     __%
```

### Reconciliação Gross Revenue → Net Revenue (convenção S-1)

```
GROSS REVENUE                  R$ _______
(-) Discounts (promoções, descontos comerciais)  -_______
(-) Sales taxes (DAS-ISS portion ~5%)            -_______  (confirmar % c/ contador)
= NET REVENUE                  R$ _______  ← linha "Total Revenue" reportada
```

Discount como contra-receita é prática S-1. DAS-ISS porção como dedução de receita também (separar do income tax).

---

## Métricas SaaS (canon — reportar TODO mês)

### Receita

| Métrica | Definição |
|---|---|
| **ARR (Annual Recurring Revenue)** | Subscription MRR × 12 |
| **MRR Total** | Receita recorrente mensal |
| **MRR Clinics Segment** | Subscription clínicas |
| **MRR Other Segment** | Subscription não-clínica |
| **Net New ARR** | ARR ganho - ARR perdido no período |
| **Implementation Revenue %** | Services / Total Revenue (ideal < 20% em SaaS) |

### Retenção (cohorts)

| Métrica | Definição | Benchmark SaaS público |
|---|---|---|
| **GRR (Gross Revenue Retention)** | 100% - churn de receita (sem upsell) | > 90% mundo-classe |
| **NRR (Net Revenue Retention)** | GRR + expansion | > 110% mundo-classe |
| **Logo Retention** | 100% - logos perdidos | > 95% |
| **Gross Logo Churn** | Logos perdidos / logos início mês | < 1% mensal |

### Unit Economics

| Métrica | Definição |
|---|---|
| **CAC** | S&M expense / new customers acquired |
| **CAC Payback (meses)** | CAC / (ARPU × Gross Margin) |
| **LTV** | ARPU × Gross Margin / Churn Rate |
| **LTV/CAC** | benchmark ≥ 3 |
| **ARPU** | MRR / customers |

### Eficiência operacional

| Métrica | Definição | Benchmark |
|---|---|---|
| **Gross Margin %** | Gross Profit / Revenue | 70-85% SaaS |
| **Operating Margin %** | Operating Income / Revenue | > 0 maduro / < 0 growth |
| **Rule of 40** | YoY Revenue Growth % + Operating Margin % | ≥ 40% |
| **Magic Number** | Net New ARR (trimestre) / S&M (trimestre anterior) | ≥ 0,75 |
| **Burn Multiple** | Net Burn / Net New ARR | < 1 ótimo / < 2 ok |
| **CAC Ratio** | S&M / Net New ARR | < 1 ótimo |
| **R&D % of Revenue** | R&D / Revenue | 15-30% SaaS growth |
| **S&M % of Revenue** | S&M / Revenue | 30-50% SaaS growth |
| **G&A % of Revenue** | G&A / Revenue | 10-20% maduro |

### Fluxo de caixa (Non-GAAP)

| Métrica | Definição |
|---|---|
| **Adjusted EBITDA** | Operating Income + Depreciation + Stock-Based Comp |
| **Adjusted EBITDA Margin** | Adj EBITDA / Revenue |
| **Free Cash Flow (FCF)** | Operating CF - CapEx |
| **FCF Margin** | FCF / Revenue |
| **Cash Conversion** | FCF / Adjusted EBITDA |

---

## Segmentação reportada

Padrão S-1 reporta por **segmento E geografia** (linhas separadas).

### Por segmento

| Segmento | Descrição |
|---|---|
| **Clinics (Healthcare AI)** | Clínicas com contrato mensalidade padrão |
| **Other Recurring** | Mensalidades não-clínica |
| **Professional Services** | Projetos pontuais (não-segmento, linha separada) |
| **Cadência SaaS** | (futuro — quando MRR Stripe materializar > 10% revenue, vira segmento próprio) |

### Por geografia

| Região | Reportar |
|---|---|
| **Brasil — Sudeste (RJ/SP)** | logos + receita |
| **Brasil — Centro-Oeste (GO/DF)** | logos + receita |
| **Internacional** | logos + receita (se houver) |

---

## Notas explicativas (em S-1, vão como footnotes)

### Note 1 — Revenue Recognition
- Subscription: reconhecida ratably (linear) ao longo do período de serviço
- Services: reconhecida na conclusão do milestone OU percent-of-completion para projetos longos
- Descontos promocionais tratados como **redução de receita bruta**, não OpEx

### Note 2 — Cost of Revenue
Inclui apenas custos diretamente atribuíveis à entrega do serviço pro cliente:
- Plataformas que escalam com volume de cliente (CRM Cadencia — substitui HighLevel, em cancelamento ⏳ CAD-683; Bubble)
- APIs consumidas em entregas (OpenAI, Elevenlabs)
- Custos de Customer Success diretamente alocados

**NÃO inclui:** ferramentas de produtividade interna (Claude, Cursor — R&D), CRM de vendas (Pipedrive — S&M), DAS (deduções de receita).

### Note 3 — Segment Reporting
Segmentos operacionais reportados: Clinics e Other Recurring. Services é linha separada não-segmento (one-time). Cadência vira segmento quando passar > 10% revenue.

### Note 4 — Stock-Based Compensation
Não aplicável (empresa não-pública, sem ESOP formal). Quando criar, reportar separadamente como reconciliação GAAP → Non-GAAP.

### Note 5 — Income Taxes
Empresa optante pelo Simples Nacional. DAS engloba IRPJ, CSLL, PIS, COFINS, ISS e CPP. Para comparabilidade internacional, separar: porção ISS como sales tax (contra-receita) + restante como income tax.

### Note 6 — Personnel Costs
Pró-labore Felipe (owner-operator) reportado como **personnel expense** em G&A. Distribuições não-formais devem ser reclassificadas com nota explicativa.

---

## Bridge — DRE interno (formato Brasil) → S-1 padrão

| Linha do DRE interno | Reclassificação S-1 | Justificativa |
|---|---|---|
| Desconto promocional | Dedução de Receita Bruta | Práctica S-1 |
| DAS (Simples) | Split: ~ISS → dedução receita; restante → income tax | Separação canônica |
| Claude / Cursor / AI tooling interno | **R&D** | Ferramenta de criação produto |
| Pipedrive | **S&M (sales tools)** | Função vendas |
| LinkedIn Premium / CapCut / Selo IG | **S&M (demand gen)** | Marketing |
| CRM Cadencia (substitui HighLevel; HighLevel em cancelamento ⏳ CAD-683) | **Cost of Revenue** | Plataforma de entrega ao cliente |
| OpenAI API | **Cost of Revenue** | API consumida em entregas |
| Pró-labore Felipe | **G&A — Personnel** | Owner-operator |
| Parcela equipamentos | **G&A — Depreciation** (linearizar) | Norma contábil |
| Juros bancários + IOF | **Other expense (below the line)** | Não é operating |
| Hetzner / Hostinger | **R&D** (infra produto) | Produção interna |

---

## Roadmap de evolução do reporting

| Fase | Entrega |
|---|---|
| **Atual** | Template S-1 + métricas definidas. Dados aguardam fechamento atualizado. |
| **Próximo fechamento** | Popular template com dados reais + reclassificações S-1 |
| **+3 meses históricos** | Cohort retention table (NRR/GRR/Logo retention) |
| **+6 meses** | Cash flow statement formal (Operating/Investing/Financing). FCF reportado. |
| **+12 meses** | Quarterly reporting completo (P&L + BS + CF + KPIs) no formato CPC/IFRS |
| **Quando ARR > R$ 5M** | Migrar para Lucro Presumido + reporting trimestral completo |

---

## Pendências

- [ ] Definir arquivo-fonte atualizado de fechamento (XLSX ou planilha viva)
- [ ] Popular template com dados do mês corrente
- [ ] Confirmar % ISS dentro do DAS com contador (estimativa benchmark: 5%)
- [ ] Definir política de Pró-labore Felipe formal (separar de distribuições eventuais)
- [ ] Alocar Cost of Revenue por cliente (no CRM Cadencia, por tenant/`contacts`; HighLevel sub-conta legado sendo cancelado ⏳ CAD-683)
- [ ] Tracking S&M attribution por cliente (pra CAC real)
- [ ] Cohort retention table (mês de aquisição × retenção mensal)
- [ ] Cash flow statement completo

---

## Refs

- `ciclo-faturamento.md` — revenue recognition
- `politica-fiscal.md` — Simples Nacional, ISS, DAS
- `precificacao-margens.md` — definições CAC/LTV/LHI
- `fluxo-caixa.md` — burn, runway, FCF
- Benchmarks SaaS: Bessemer State of the Cloud, OpenView SaaS Benchmarks, Meritech Public Comps
- Padrão S-1: HubSpot S-1 (2014), Atlassian F-1 (2015), Shopify F-1 (2015) como referência
