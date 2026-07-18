---
title: Matriz de Responsabilidades por Produto
tags: [cs, canon]
---

# Matriz de Responsabilidades por Produto

> Espelho legível da fonte canônica `_shared/matriz_responsabilidades.py` (DEV-799).
> Define, por produto, o que é responsabilidade da **PD**, do **Cliente** e do **Gestor de tráfego** (quando há).
> Alimenta o **Checklist de Responsabilidades** (onboarding) e o bloco `{{itens_especificos_produto}}` do **Doc A**.
>
> **Status:** conteúdo DRAFT — Felipe valida/refina o texto dos itens antes de produção. A estrutura (produtos × papéis × segmentos) é estável.

## Papéis de stakeholder (lista fixa)

`decisor` · `owner_ia` (Owner da IA) · `gestor_trafego` (Gestor de tráfego) · `operacional` · `financeiro` · `ti`

Esses papéis são o `role` gravado no CRM (company_contacts.role) na ingestão de stakeholders.

---

## Cadencia Bundle  *(tem gestor de tráfego)*

**PD**
- Configuração do tenant Cadencia (identidade, editorias, visual, agentes).
- Produção da cadência de conteúdo e aprovação editorial.
- Setup e operação do CRM Cadencia (pipelines, contatos, oportunidades).
- Onboarding e treinamento de uso da plataforma.
- Acompanhamento mensal de métricas e ajuste de estratégia.

**Cliente**
- Acesso à conta Meta Business (Facebook/Instagram) com permissão de admin.
- Acesso ao número de WhatsApp Business a ser usado nas cadências.
- Aprovação de identidade visual, tom de voz e editorias.
- Fornecimento de cases, depoimentos e materiais de prova social.
- Indicação dos stakeholders (decisor, owner da IA, operacional).
- Verba de mídia (se houver tráfego pago) — definição de budget.

**Gestor de tráfego**
- Estruturação e gestão das campanhas de tráfego pago.
- Gestão do Gerenciador de Anúncios Meta e pixel/Conversions API.
- Otimização de criativos e públicos junto à cadência de conteúdo.
- Relatório de performance de mídia integrado ao acompanhamento.

---

## Cadencia (solo)  *(sem gestor de tráfego)*

**PD**
- Configuração do tenant Cadencia (identidade, editorias, visual, agentes).
- Produção da cadência de conteúdo e aprovação editorial.
- Setup e operação do CRM Cadencia.
- Onboarding e treinamento de uso da plataforma.
- Acompanhamento mensal de métricas.

**Cliente**
- Acesso aos perfis sociais a serem geridos (Instagram/LinkedIn).
- Acesso ao número de WhatsApp Business (se usado nas cadências).
- Aprovação de identidade visual, tom de voz e editorias.
- Fornecimento de cases, depoimentos e materiais de prova social.
- Indicação dos stakeholders (decisor, owner da IA).

---

## Treinamento Claude Code 30d  *(sem gestor de tráfego)*

**PD**
- Currículo das sessões de treinamento (4 sessões).
- Mentoria ao vivo e acompanhamento da evolução do treinando.
- Material de apoio e exercícios práticos.
- Suporte assíncrono durante os 30 dias.

**Cliente**
- Disponibilidade do treinando nas sessões agendadas.
- Máquina com ambiente de desenvolvimento (acesso de admin pra instalar).
- Conta Anthropic / Claude Code ativa (ou setup na 1ª sessão).
- Caso de uso real do próprio negócio pra aplicar no treinamento.

---

## Consultoria IA  *(sem gestor de tráfego)*

**PD**
- Diagnóstico do processo atual e desenho da solução de IA.
- Plano de implementação e roadmap.
- Mentoria e acompanhamento da execução.
- Entregáveis acordados no escopo da consultoria.

**Cliente**
- Acesso aos sistemas/ferramentas a serem integrados.
- Fornecimento de dados e documentação de processos.
- Disponibilidade do time para entrevistas e validações.
- Indicação dos stakeholders (decisor, owner da IA, TI, operacional).
- Decisões de negócio dentro do prazo acordado.

---

## MVP Meta Ads  *(tem gestor de tráfego)*

**PD**
- Estruturação inicial das campanhas Meta Ads (MVP).
- Configuração de pixel / Conversions API.
- Criativos e copy do MVP.
- Relatório de resultados do piloto.

**Cliente**
- Acesso à conta Meta Business com permissão de admin.
- Acesso ao site/landing page (ou autorização pra criar).
- Verba de mídia definida para o MVP.
- Aprovação de criativos e oferta.
- Indicação dos stakeholders (decisor, financeiro pra verba).

**Gestor de tráfego**
- Operação diária das campanhas durante o MVP.
- Otimização de públicos, lances e criativos.
- Gestão do Gerenciador de Anúncios e pixel/CAPI.

---

## Automação escritório jurídico  *(sem gestor de tráfego)*

**PD**
- Mapeamento dos fluxos do escritório a automatizar.
- Desenvolvimento das automações (intake, triagem, follow-up).
- Integração com ferramentas existentes do escritório.
- Treinamento da equipe no uso das automações.

**Cliente**
- Acesso aos sistemas do escritório (gestão, e-mail, WhatsApp).
- Documentação dos processos atuais a automatizar.
- Validação jurídica dos templates e fluxos.
- Indicação dos stakeholders (decisor, owner da IA, TI).

---

## Como o sistema usa esta matriz

- **Checklist de Responsabilidades:** `matriz_responsabilidades.render_checklist(produto, ajuste_cliente=...)` gera o markdown por produto (com ajuste por cliente).
- **Doc A (`{{itens_especificos_produto}}`):** `render_itens_especificos_produto(produto, html=True)` devolve os `<li>` do que o cliente precisa reunir (inclui itens de tráfego só nos produtos que têm gestor).
- **Resolução de nome:** `resolve_produto("Cadência Bundle")` → slug canônico, tolerante a acento/alias.
- **Stakeholders:** papéis validados contra a lista fixa em `STAKEHOLDER_ROLES`; ingestão em `_shared/stakeholders.py`.
