> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/adr/0003-ghl-motor-invisivel.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0003-ghl-motor-invisivel.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# ADR-0003 — GHL como motor invisível

> **REGISTRO HISTÓRICO / SUPERSEDED.** Preserva a decisão original; o CRM nativo Cadencia é a arquitetura atual.

**Status:** superseded · **Data:** 2026-05-27

## Contexto

GoHighLevel é nosso backbone de CRM, email, WhatsApp e scoring. Mas o usuário do Cadência é PME/empreendedor que não quer aprender outra ferramenta — ele quer "post no Instagram + leads no WhatsApp + email automático".

## Decisão

GHL fica **completamente invisível** na UI do Cadência:

- Frontend nunca mostra "GHL", "GoHighLevel", "subconta".
- Links para CRM abrem o domínio white-label do tenant (`config.ghl.white_label_url`).
- Botões dizem "Cadencia Growth", "meus contatos", "minhas conversas" — não "abrir GHL".
- Onboarding nunca pede ao usuário para criar subconta — `provision_tenant.py` cria automaticamente.

## Consequências

- ✅ UX simples — usuário não precisa entender CRM.
- ✅ Lock-in baixo (do ponto de vista do usuário) — ele só vê a Cadência.
- ❌ Quando GHL muda API/UI brancada, agente precisa atualizar fluxos sem expor a quebra.
- ❌ Bugs no GHL viram bugs na Cadência aos olhos do usuário — suporte precisa diagnosticar sem citar GHL.
- ⚠️ Equipe Cadência precisa saber GHL profundamente (CS + dev).

## Não considerado

- Build próprio de CRM — fora do escopo. GHL resolve com white-label.
- Mostrar "powered by GHL" — diminui percepção de produto próprio.
