# architecture/ — Visão sistêmica

Documentos que valem para o sistema como um todo, não para um componente isolado.

## Arquivos

| Arquivo | O que tem | Quando ler |
|---|---|---|
| [CONTEXT.md](CONTEXT.md) | **Linguagem ubíqua** — tenant, CRM, editorial, dossier, cadência, generation queue e demais contratos | **Primeiro contato** com o sistema. |
| [architecture.md](architecture.md) | **Diagrama C4** (Context + Container) em mermaid + tabela de componentes por área + fluxos críticos (onboarding, geração diária, trigger on-demand, scoring) | Pra entender **o desenho** do sistema antes de mexer em código. |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de mudanças relevantes (migração Stripe, refator RLS, etc.) | Pra entender **o que mudou** desde a última vez que você viu o projeto. |

## Por onde começar

**Agente nunca viu o Cadência:** `CONTEXT.md` → `architecture.md` → componente que vai tocar.

**Agente já conhece, vai mexer em algo específico:** `architecture.md` § "Fluxos críticos" → componente.

## Refs

- Voltar: [`../README.md`](../README.md)
- ADRs (decisões): [`../adr/`](../adr/)
- Implementação real: [`../../context/how-it-works.md`](../../context/how-it-works.md)
