---
title: Template — Manual da Marca
tags: [cs, canon]
---

# Template — Manual da Marca / Análise de Marca & Posicionamento

> **Quando gerar:** SEMPRE, para todo cliente novo, logo após o briefing ser transcrito e analisado (cadeia pós-briefing). É entregável padrão do onboarding — junto com Ata e Manual do Cliente. Automação: CSE-101 (gerador + PDF branded); enquanto não pousa, gerar via agente seguindo este template.
>
> **Casos de referência (ler antes de gerar um novo):**
> - Dra. Nathalia Galardo — `Obsidian_Vaults_Empresa/Clientes/Nathalia-Galardo/Dra. Nathalia Galardo - Marca Pessoal.md` (original que definiu o padrão)
> - Ariane Farrapo — `Obsidian_Vaults_Empresa/Clientes/Ariane-Farrapo/` (piloto do processo padronizado, 04/07/2026)

## O que é (e o que NÃO é)

- **É** o documento estratégico de marca que o **cliente recebe**: posicionamento, público, narrativa, diretrizes. Linguagem de negócio, denso, personalizado — nunca genérico.
- **NÃO é** o dossier técnico do tenant (motor de conteúdo interno) nem o debrief (atesta entendimento). São 3 documentos distintos gerados da mesma transcrição.

## Fontes de geração (ordem)

1. **Transcrição completa do briefing** (fonte primária — ler INTEIRA; extrair citações literais do cliente)
2. Form de briefing (Tally), quando existir
3. Contrato (produto, escopo)
4. Ata da call de vendas, quando existir

## Estrutura obrigatória (seções, na ordem)

```markdown
---
title: "<Nome> - Marca Pessoal"
cliente: "<Nome completo>"
date: YYYY-MM-DD
tags: [<slug>, cliente, marca-pessoal, posicionamento, arquetipo, publico, conteudo, <nicho>]
moc: "[[MOC-Inbox]]"
---

# 🎯 POSICIONAMENTO ESTRATÉGICO
## Objetivo e Função Principal      ← o que o perfil sinaliza + recorte de mercado definido no briefing
### KPIs — Primeiros 90 Dias        ← metas REALISTAS do nicho (consistência, formatos, resultado comercial)
### Etapa do Funil                  ← topo/meio/fundo + objetivo de conversão

## Essência e Proposta de Valor
### Essência da Marca               ← frase-síntese + parágrafo (a ferida/história que legitima)
### Proposta de Valor Única (USP)   ← diferencial combinado + promessa + frase-conceito
### Filosofia de Atendimento        ← como o cliente é tratado (métodos concretos, citações reais)

## Autoridade e Diferenciação
### Pilares de Legitimidade         ← provas: números, casos reais, vivência
### Diferenciais Próprios           ← + Regra de Ouro (nunca atacar concorrente nominalmente)

## Público-Alvo e Persona
### Segmentação (primário/secundário/terciário) + dores + gatilho de conversão

## Canais e Estratégia de Conteúdo
### Plataforma principal · Linhas editoriais (3-4, com nomes próprios) · Formatos · Regra de encerramento

## Território Simbólico
### Jornada de Transformação (Origem → Queda → Reconstrução → Missão) + Valores Centrais + Personalidade

# ⚔️ ARQUÉTIPO E NARRATIVA
## Arquétipo nomeado + necessidade psicológica + ferida que legitima
## Estrutura narrativa (X conflito / Y resolução · herói=cliente, mentor=marca)
## Gatilhos mentais ativados
## Mensagem central

# 📏 DIRETRIZES PRÁTICAS
## Sempre / Nunca / Critério final de publicação
```

## Regras de qualidade (não-negociáveis)

1. **Citações literais do cliente** (da transcrição) na Essência, Filosofia e Diretrizes — é o que torna o doc dele, não um template preenchido.
2. **Compliance por nicho:** saúde (CFM/CRO — sem promessa de resultado), imobiliário (CRECI — sem promessa de valorização), financeiro (CVM). Sempre na seção "Nunca".
3. **Temas sensíveis da call** (política, polêmicas passadas, vulnerabilidades pessoais) → decisão explícita: ou viram diretriz "Nunca", ou entram com aval do cliente. Nunca ignorar.
4. **Cliente como herói** de toda história; a marca é o guia/mentor.
5. **KPIs realistas** pro estágio digital atual do cliente — não copiar metas de outro caso.
6. **Divergências factuais na transcrição** (datas, fatos biográficos ambíguos) → manter ambíguo no doc e apontar pro Felipe na entrega.
7. **Felipe revisa antes do envio.** Sem exceção — conteúdo específico de cliente.

## Destinos após aprovação

| Destino | O quê |
|---|---|
| Obsidian `Clientes/<Nome>/` (vault Empresa) | o .md (fonte) |
| OneDrive `Customer Success/<área>/<Nome>/Materiais/Entregues/` | PDF branded (via doc_generator, quando CSE-101 pousar; até lá, PDF manual) |
| Cliente | email formal (PDF anexado) + PDF no grupo WhatsApp (canal de entrega completo — regra 03/07/2026) |
| CRM | marker `email.documentacao` na timeline |
| Tenant | insumo pro dossier v3 + soul_md (gerados juntos, da mesma transcrição) |
