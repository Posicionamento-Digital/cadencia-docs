---
date: 2026-05-19
tags: [documentacao, cadencia, growth, email-dispatch]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
---
## Identidade
- **Tipo:** pipeline de email / feature Growth
- **Stack:** Python 3.12, OpenAI gpt-5.4, GHL API
- **Path no repo:** `cadencia-growth/pipeline/`
- **Status:** Produção — funcional

## O que é
Pipeline de geração e envio de emails Seinfeld e Newsletter para leads dos tenants Growth via GHL.

## Como funciona
Aprovação de ideia → trigger_server.py (VPS :8767) → seinfeld_generate.py --generate (agenda).
Cron 11h BRT → seinfeld_generate.py --dispatch → renderiza HTML → POST /conversations/messages para cada contato GHL.
Cron 15h BRT sexta → newsletter_generate.py → mesmo fluxo de envio.

## Credencial crítica
Scripts usam `ghl.location_pit_token`. Tenants white-glove precisam ter esse campo além de `api_key`.

## 🚫 Don'ts
- Nunca usar GHL workflow para envio — não passa HTML customizado
- Nunca chamar LLM sem verificar contatos GHL antes
- Nunca marcar newsletter_included=true antes de confirmar envio ok > 0

## Notas Relacionadas
[[growth-lead-scoring]] · [[growth-newsletter]]
