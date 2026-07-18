---
title: Política Fiscal — AXIS / Cadencia
tags: [financeiro, canon]
---

# Política Fiscal — AXIS / Cadencia

> Regime tributário, impostos, retenções e responsabilidades fiscais.
> **Mudança neste doc exige validação com contador externo.**

---

## Identidade fiscal

| Campo | Valor |
|---|---|
| **Razão Social** | AXIS CONSULTORIA & EMPRESARIAL LTDA |
| **CNPJ** | 62.650.127/0001-03 |
| **NIRE** | 35267914112 |
| **Inscrição Municipal (Barueri)** | 4BR4009 |
| **Endereço** | Av. Copacabana, 439, Sala Apto 176 — Dezoito do Forte Empresarial / Alphaville, Barueri/SP, CEP 06472-001 |
| **Código IBGE Barueri** | 3505708 |
| **Nome Fantasia / Marca operacional** | Cadencia |

**Quem é quem:**
- AXIS = razão social que assina contratos e emite NF
- Cadencia = marca operacional e produto SaaS de IA + automação, com implementação, operado dentro da AXIS

Toda NF, contrato e obrigação fiscal sai como AXIS. Marketing e comunicação externa usam Cadencia.

---

## Regime tributário

| Campo | Valor |
|---|---|
| **Regime** | Simples Nacional |
| **Anexo** | **Anexo III** — confirmado pela contadora Talissa (17/06/2026). Empresa tributada como **educação profissional / treinamento e desenvolvimento (CNAE classe 8599)** → alíquota efetiva **~6%**, e NÃO como desenvolvimento de sistemas (que seria ~15,5%) |
| **Recolhimento** | Mensal via DAS |
| **DAS mensal de referência** | ~R$ 3.066 (Fev/26) |
| **ISS** | Recolhido pelo prestador via DAS (não destacado em nota) |
| **Município** | Barueri/SP (confirmar com Talissa — reunião 17/06 falou em portal de prefeitura genérico) |
| **Tipo societário** | **Unipessoal** (Ltda → Unipessoal após destrato/saída do sócio Michael, mai/2026) |

> ℹ️ **Código de serviço da NF — responsabilidade da contadora (Talissa).** A empresa é tributada no DAS como **treinamento (classe 8599, ~6%)**, não como desenvolvimento de sistemas (~15,5%). O foundation tinha registrado o código **115013000 / 010101 (TI)** — esse alinhamento (nota × DAS) **é a Talissa quem revisa e define**, não o Time Financeiro. Felipe dá acesso ao portal da prefeitura; ela revisa as notas emitidas e informa o código correto a usar. **Regra para nós:** seguir o código que a Talissa indicar e "contar a mesma história" (atividade da nota = atividade declarada no DAS) — a reforma de set/2026 passará a cruzar isso automaticamente.

### Distribuição de lucro — regra nova 2026

- **Retirada de lucro agora é obrigatória trimestralmente** (antes era anual e livre).
- **Teto de isenção:** até **R$ 49.999/mês** isento; **acima de R$ 50.000/mês** incide **IR de 10%** sobre o valor retirado.
- **Estratégia (Talissa):** distribuir fracionado ao longo do ano (meta ~R$ 100k declarados/ano) para compor renda — sem renda declarada, banco nega crédito/financiamento. Empresas de fluxo alto migram para retirada mensal para não estourar o teto.
- **Pró-labore:** não recomendado (acima de R$ 5k incide IR + INSS). Distribuição de lucro é mais eficiente.
- **Base:** faturamento − impostos − despesas = lucro distribuível (proporcionalizado por média; não se distribui mais do que se faturou).

### Regime de apuração

- **Atual:** regime de **competência** (imposto integral na emissão da nota).
- **Em estudo:** migração para **regime de caixa** (imposto conforme parcelas entram) — pendente de estudo de 3 meses com planilha de contratos. Caixa tem declaração manual e efeito "bola de neve"; só se sai dele quitando tudo.

### Faixa de faturamento

Faturamento bruto últimos 12 meses: **EM REVISÃO** (Felipe + contador apuram). Necessário pra confirmar faixa Simples e antecipar saída do Simples se aproximar do teto (R$ 4,8M/ano).

---

## Regras vigentes — orientação contábil (Talissa, 17/06/2026)

> Tudo abaixo é **regra do Time Financeiro** (orientação direta da contadora). Mudança exige nova validação com a Talissa/Marcelo.

1. **Classificação fiscal:** manter Anexo III ~6% como **treinamento/educação profissional (8599)**. Não migrar para desenvolvimento de sistemas (TI, ~15,5%) sem orientação da Talissa.
2. **Código na emissão de NF (atenção operacional):** ao emitir qualquer nota, **usar o código de serviço alinhado ao DAS (treinamento)** — nunca o de TI (115013000) por padrão. Quem define o código exato é a Talissa; nós seguimos o que ela indicar. "Contar a mesma história": atividade da nota = atividade declarada no DAS. Exceção: cliente PJ grande pode exigir nota de "desenvolvimento" — é legal fornecer nesses casos pontuais (orientação Talissa).
3. **Distribuição de lucro:** trimestral obrigatória (2026). Teto **R$ 49.999/mês isento**; acima de R$ 50k/mês incide **IR 10%**. Distribuir fracionado ao longo do ano (~R$ 100k/ano declarados) p/ compor renda. **Não fazer pró-labore** (IR+INSS acima de R$ 5k). Talissa conduz trimestralmente.
4. **Regime de apuração:** manter **competência** até concluir estudo caixa × competência (3 meses de planilha de contratos). Só mudar com projeção da Talissa.
5. **Dívida com a Receita:** **não deixar débito de DAS virar o ano** (risco de desenquadramento do Simples + juros). Resolver DAS Fev/26 (~R$ 3.700) via pagamento ou parcelamento (até 12x R$ 314,67) antes de dez/2026.
6. **Regra de ouro — preventivo:** consultar a Talissa ou Marcelo **ANTES** de fechar negócio diferente, criar cláusula contratual nova ou fazer retirada relevante. Prevenir custa zero; corrigir depois do fato custa imposto.
7. **Reforma tributária (set/2026):** novo emissor nacional de NF + cruzamento automático nota × DAS. Acompanhar alíquotas (ainda não divulgadas).

---

## Sistema NFS-e Barueri

**Operacional próprio detalhado em `foundation/nfse-barueri.md`** (sistema, certificado, MCP, fluxo de emissão).

Resumo:
- NFS-e emitida no município de Barueri/SP via portal próprio
- Autenticação SOAP via Certificado Digital A1 (PFX, validade 11/09/2026)
- ISS recolhido via DAS — não destacado em nota
- Código serviço padrão: **115013000** (Serviços de suporte em TI)
- Subitem: **010101** (Análise e desenvolvimento de sistemas)

---

## Impostos federais (Simples Nacional)

DAS engloba (proporcionalmente à faixa):
- IRPJ
- CSLL
- PIS/PASEP
- COFINS
- CPP (Contribuição Previdenciária Patronal)
- ICMS / ISS (conforme atividade — AXIS é ISS)

**Como Simples Nacional NÃO há:**
- Destaque de PIS/COFINS na nota (clientes do Lucro Real não creditam — comunicar)
- ISS retido na fonte (cliente que tentar reter está errado, mostrar Anexo do contrato Simples)

---

## Retenções aplicáveis

| Situação | Retenção | Quem retém |
|---|---|---|
| Cliente PJ contratando serviços Simples Nacional AXIS | **Nenhuma retenção** (Lei Complementar 123/2006) | — |
| Cliente do Lucro Real / Presumido tentar reter ISS | Não retém — AXIS recolhe via DAS | — |
| INSS sobre serviços (CPP) | Recolhido via DAS | — |
| IRRF | Não se aplica (Simples) | — |

**Se cliente questionar:** enviar **Declaração de Optante pelo Simples Nacional** anexo ao contrato.

---

## Sócios e quadro societário

Documentos no repo: `times/financeiro/context/empresa/`
- `CNPJ.pdf` — Cartão CNPJ AXIS
- `Consulta Quadro de Sócios e Administradores - QSA.pdf` — QSA atual
- `Certidao de Inteiro Teor do NIRE_ 35267914112.pdf` — Certidão JUCESP

**Sócios atuais:** consultar QSA (Felipe + saída Michael consumada 07-11/05/2026 — confirmar registro JUCESP).

Outros documentos relevantes em `Finanças/documentos/empresa/`:
- Declarações Felipe assinadas
- Termo de Titularidade
- Certificado CLI (Cadastro Liberatório de Instalação?)

---

## Contador externo

- **Escritório:** Talissa (contadora responsável) + Marcelo (sócio/contato). Substituíram o contador anterior — "revisei o que eles fizeram, está ok". Atendimento consultivo/preventivo.
- **Telefone Talissa (WhatsApp):** +55 11 99832-3265
- **Canal:** Felipe consulta Talissa ou Marcelo ANTES de fechar negócio diferente, criar cláusula nova ou fazer retirada relevante.
- _Preencher: e-mail/CNPJ do escritório (obter com Felipe)._

## Pendências EM REVISÃO

- [ ] **Fechar divergência código NF (TI 115013000 vs treinamento 8599)** com a Talissa — bloqueia emissão de NF nova (ver caixa de alerta acima)
- [ ] Passar senha do portal da prefeitura para a Talissa (revisar notas + taxa anual)
- [x] ~~Confirmar Anexo Simples~~ → **Anexo III, ~6%, tributado como treinamento** (Talissa, 17/06/2026)
- [x] ~~Nome + escritório do contador externo~~ → **Talissa + Marcelo** (falta telefone/e-mail/CNPJ)
- [x] ~~Atualização QSA pós-saída Michael~~ → **empresa virou Unipessoal** após destrato (confirmar registro JUCESP)
- [ ] Faturamento bruto últimos 12 meses (reunião: ~R$ 450k declarado ano anterior; meta recorrente R$ 100k/mês)
- [ ] Resolver DAS Fev/2026 em aberto (~R$ 3.700, parcelável 12x R$ 314,67) — não deixar virar o ano
- [ ] Decisão regime caixa × competência (após estudo de 3 meses com planilha de contratos)
- [ ] Política de retenção de tributos quando cliente é PJ Lucro Real
- [ ] Códigos serviço para outras trilhas (Cadência B2B, consultoria, Gestores IA) se diferentes do código de treinamento
- [x] ~~Política de Pró-labore Felipe~~ → **não fazer pró-labore** (IR+INSS acima de R$ 5k); usar distribuição de lucro fracionada

---

## Refs

- `nfse-barueri.md` — sistema NFS-e operacional
- `ciclo-faturamento.md` — onde NFSe entra no fluxo
- `dre-structure.md` — registro contábil da receita
- `context/empresa/` — docs societários no repo
- Fonte original: `ClaudeCode/Finanças/CLAUDE.md` + `documentos/empresa/`
- Obsidian: `Time PD/Financeiro/Manual-Emissao-NFSe.md` (Manual GCI — operacional)
