# adr/ — Architecture Decision Records

Decisões arquiteturais não óbvias do Cadência. Cada ADR responde **"por que isso é assim?"** com contexto, decisão, consequências e alternativas descartadas.

> Formato Matt Pocock minimalista (1-3 frases por seção). Imutáveis — não se reescreve ADR, abre-se um novo que supersede.

## ADRs vigentes

| # | Decisão | Data | Status |
|---|---|---|---|
| [0001](0001-stripe-em-vez-de-asaas.md) | **Stripe** substituiu Asaas como gateway de pagamento | 2026-05-11 | aceito |
| [0002](0002-chat-agent-design.md) | **Chat "Tenho uma ideia"** com SOUL.md por tenant + memória de sessão | 2026-05-27 (retroativo) | aceito |
| [0003](0003-ghl-motor-invisivel.md) | **GHL invisível** — usuário nunca vê referências a GoHighLevel | 2026-05-27 | aceito |
| [0004](0004-carrossel-railway-resto-vps.md) | **Carrossel/reels Railway**, blog/seinfeld/linkedin/instagram/newsletter VPS | 2026-05-27 (decisão original ~10/2025) | aceito |
| [0005](0005-location-pit-token-por-tenant.md) | **`location_pit_token` por tenant** (não `api_key` global) | 2026-05-27 | aceito |
| [0006](0006-multi-tenant-rls-supabase.md) | **Multi-tenant via RLS Supabase**, não DBs separados | 2026-05-27 | aceito |

## Quando consultar uma ADR

- Antes de **reverter decisão** ("não seria melhor X?") — leia o ADR original primeiro.
- Antes de **mexer em algo que parece estranho** — pode ser decisão deliberada documentada aqui.
- Antes de **abrir nova ADR** — verifique se já não há uma cobrindo o tema.

## Como criar uma ADR nova

1. Próximo número sequencial (`0007-*.md`).
2. Use o template de qualquer ADR existente como referência.
3. Status inicial `proposto` → após decisão Felipe, `aceito`.
4. Não edita ADR aceito — supersede com novo (e adiciona "Substituído por ADR-NNNN" no antigo).

## Refs

- Voltar: [`../README.md`](../README.md)
- Skill: `/documentar` cria ADRs automaticamente quando detecta decisão não óbvia no código.
