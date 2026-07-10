---
date: 2026-06-29
tags: [documentacao, projeto]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Central CS Onboarding]]"]
---
# Robustez da skill /ativar-cliente (DEV-956)

> Doc técnica da feature. Origem: auditoria lockstep do cliente **OP Odontopenha** → 15 furos no pipeline de ativação CS → 15 correções. **Validado e2e contra os sistemas reais.**

## O que é
A skill `/ativar-cliente` orquestra a ativação de cliente CS sincronizando 4 sistemas (CRM Cadencia, Asaas, Linear, tenant Cadencia). A auditoria revelou gates que assumiam "caminho feliz" e falhavam no mundo real (e-mail compartilhado, pagador terceiro, contatos pré-existentes, docs desatualizados, tenant só casca).

## Padrão das correções
Busca **multi-frente** + **cruzamento de fontes** + **nunca confiar em fonte única**. O `CLAUDE.md` do cliente passou a ser tratado como suspeito (verdade = CRM/Linear/Asaas/Autentique).

## Módulos (pd-framework/_shared/)
- **asaas_customer_lookup.py** (novo) — busca Asaas anti-duplicação: timeline do CRM primeiro, depois CNPJ + CPF de cada sócio/pagador + email + nome; sinaliza customers duplicados. (DEV-967)
- **autentique_status.py** (novo) — estado de assinatura ao vivo por signatário (assinado/parcial/...). (DEV-976)
- **stakeholders.py** — anti-dup por telefone, e-mail compartilhado (só decisor porta), lifecycle por papel, papel→constraint do banco. (DEV-969/968/970/971)
- **produto_inclui_cadencia.py** — fallback no corpo do CLAUDE.md quando falta frontmatter. (DEV-957)
- **cadencia_cli_runner.py** — resolve path por env/descoberta, não layout fixo. (DEV-977)
- **processar_transcricao_kickoff.py** — Obsidian (WhisperX local) como fonte primária + extrator OpenRouter (GLM 5.2) + guard de sanidade. Fireflies opcional/desligado. (DEV-973)

## Skill SKILL.md
Gate Asaas multi-frente, gate contrato via Autentique ao vivo, **B.4.5** (encadeia identidade do tenant após a casca + `tenants verify`), gate produto cedo, gate consistência doc↔realidade, glob anti-pasta-duplicada, marker de confirmação.

## Validação e2e (dados reais OP, 2026-06-29)
Runner resolve path ✅ · produto=True ✅ · Asaas achou 2 customers duplicados ✅ · timeline leu o cus ✅ · Autentique=assinado ✅ · stakeholders 0 duplicatas + roles certos ✅ · pós-kickoff achou briefing + OpenRouter extraiu 2 stakeholders/6 pendências/1 data ✅.

> **Aprendizado-chave:** o teste e2e real pegou um bug que 43 testes mockados não pegaram (matching "op" stopword). Mock verde ≠ funcional.

## Don'ts
- Nunca declarar "sem cliente Asaas" só pelo CNPJ.
- Nunca confiar no CLAUDE.md do cliente como verdade.
- Nunca declarar tenant pronto só com `tenants provision` (é só a casca).
- Nunca marcar contrato pelo frontmatter — Autentique ao vivo.

## Notas Relacionadas
[[Central CS Onboarding]] · `pd-framework/times/cs/context/doc-robustez-ativar-cliente-dev956.md` · `auditoria-ativar-cliente-op-odontopenha.md`
