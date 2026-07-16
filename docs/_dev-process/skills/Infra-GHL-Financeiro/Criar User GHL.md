---
date: 2026-05-14
tags: [skill, infra, ghl, usuario, clinica, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Criar User GHL

Cria usuário em subconta GHL usando perfis predefinidos (secretaria, proprietaria), gera senha forte, salva no 1Password vault Clientes e devolve o ID.

## Quando usar
"/criar-user-ghl", "cria user no ghl", "adiciona usuário em [clínica]", "cria secretária na [clínica]", "novo usuário ghl pra [clínica]", "adiciona [nome] na [clínica] como secretária/proprietária".

---

## Conteúdo da Skill

```markdown
---
name: criar-user-ghl
description: >
  Cria usuário em uma subconta GHL (GoHighLevel) da agência nova de Felipe usando
  perfis predefinidos (secretaria, proprietaria), gera senha forte, salva credencial
  no 1Password vault Clientes e devolve o ID do user.
---

# criar-user-ghl

Cria usuário em subconta GHL com perfil predefinido + salva credencial no 1Password.

## Subcontas conhecidas

Mapa em `locations.json` (mesma pasta). Slugs e aliases:
- `clinica-og` (og, dra nathalia)
- `pd` (identificador técnico legado da Cadencia)
- `hco`
- `sorria-ceilandia` (sorria cei, ceilandia)
- `sorria-central` (sorria central, central)
- `plano-piloto` (plano, piloto)
- `template-cadencia` (template)

Quando Felipe falar o nome da clínica em linguagem natural, mapear pelo alias.

## Perfis disponíveis

Em `templates/`:

| Perfil | Arquivo | Role | O que destrava |
|---|---|---|---|
| **Secretária / Recepção** | `secretaria.json` | `user` | Contacts, Conversations, Opportunities, Tags, Lead Value, Dashboard Stats, Bulk Requests, Invoice, Content AI, Record Payment, Payments, Reporting básico, Ad Publishing readonly. **Sem** settings, workflows, marketing, ads, social, appointments. |
| **Proprietária / Dona** | `proprietaria.json` | `admin` | Quase tudo: campaigns, workflows, triggers, appointments, conversations, marketing, reporting completo, social planner, payments completo, media storage, ad publishing full. |

## Fluxo padrão

1. **Coletar dados do user**: nome (first + last), email, telefone (opcional), perfil, subconta.
2. **Validar perfil e subconta**: olhando os arquivos. Se algum não bater, perguntar.
3. **Montar payload** via `build_payload(...)` do `create_user.py`.
4. **Confirmar com Felipe**: mostrar lista resumo (nome/email/perfil/subconta) ANTES de disparar. Pular só se Felipe já autorizou a leva inteira ("manda todos").
5. **Criar via API**: `POST /users/` com `GHL_NEW_AGENCY_PIT`.
6. **Salvar no 1Password vault `Clientes`**:
   ```powershell
   op item create --category=login \
     --title="GHL - <Subconta> - <Nome Completo>" \
     --vault="Clientes" \
     --url="https://app.gohighlevel.com" \
     --tags="GHL,<Subconta>,Cliente" \
     "username=<email>" "password=<senha gerada>" \
     "notesPlain=Usuario GHL (role: <role>) na subconta <Subconta>. locationId: <id>. userId: <id>."
   ```
7. **Reportar**: tabela com nome, email, role, userId, ref 1P (`op://Clientes/<titulo>/password`).
8. **Mensagem de entrega (opcional)**: quando Felipe disser "cria a mensagem", gerar texto pronto para copiar/colar (WhatsApp/email) com link do GHL, email, link 1Password share e resumo das permissões.

## Geração de link 1P share

```powershell
op item share "<TITULO DO ITEM>" --vault=Clientes --expires-in 7d
```

Retorna URL `https://share.1password.com/s#...`. Opções:
- `--expires-in 24h` / `7d` / `1w` — default 7d
- `--view-once` — expira após primeira visualização

**Sempre rodar `op item share` no momento da mensagem** — não reutilizar link antigo.

## Padrões fixos

- Endpoint: `POST https://services.leadconnectorhq.com/users/`
- Version header: `2023-02-21`
- Vault 1P: **Clientes** (NÃO `Acessos Clientes`)
- Nomenclatura item 1P: `GHL - <Subconta legível> - <Nome Completo>`
- Tags 1P: `GHL`, `<Subconta legível>`, `Cliente`
- Senha: 16 chars, mix obrigatório de classes

## Como usar o helper (Python)

```python
import sys
sys.path.insert(0, r"C:\Users\felip\.claude\skills\criar-user-ghl")
from create_user import (
    build_payload, create_user, gen_password,
    resolve_subconta, load_profile, capture_profile_from_user,
)

pw = gen_password()
payload = build_payload(
    first_name="Karine", last_name="Freitas",
    email="...", phone="+5511...",
    password=pw, subconta="clinica-og", profile="secretaria",
)
resp = create_user(payload)
print(resp["id"])
```

## Edge cases

- **Email duplicado**: GHL retorna 4xx. Mostrar o erro e perguntar se atualiza.
- **Senha rejeitada (422)**: `gen_password` já garante; se ainda assim falhar, regenerar e re-tentar 1x.
- **Subconta ambígua** (ex: "sorria"): perguntar qual unidade.
- **Perfil customizado**: aceitar `overrides={"permissions": {...}}` no `build_payload`.

## Captura de perfil novo

Quando Felipe configurar um user na UI como referência:

```python
from create_user import capture_profile_from_user
capture_profile_from_user("<userId>", "dentista", source_note="Configurado por Felipe em <data>")
```

Salva em `templates/dentista.json` automaticamente.

## Arquivos da skill

- `SKILL.md` — este arquivo.
- `locations.json` — mapa de subcontas + companyId + agency PIT fallback.
- `templates/secretaria.json` — perfil Recepção.
- `templates/proprietaria.json` — perfil Dona.
- `create_user.py` — helper Python (importável pelo agente).
```

## Notas Relacionadas
[[Infra-GHL-Financeiro/Credencial]] · [[Infra-GHL-Financeiro/Analise Funil Ecuro]]
