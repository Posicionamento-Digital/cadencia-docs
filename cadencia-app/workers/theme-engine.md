> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `cadencia-workers/src/workers/theme-engine/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-workers/src/workers/theme-engine/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# theme-engine — Theme Engine v3

## TL;DR

Resolve qual template visual (preset + sub-preset) aplicar ao renderizar slides de um tenant. Cacheia em `tenant_themes`.

## Identidade

- **Tipo:** Worker Python
- **Stack:** Python + Supabase
- **Path:** `cadencia-workers/src/workers/theme_agent.py`
- **Status:** ativo
- **Deps:** `tenant_config.config.preferred_sub_preset`, `style_configs` table, `tenant_themes` table

## Como funciona

1. Lê `preferred_sub_preset` do `tenant_config`
2. Busca configuração de estilo em `style_configs` (Big5 + signaling do tenant)
3. Resolve paleta de cores, tipografia, espaçamento
4. Salva resultado em `tenant_themes` (cache — evita recalcular a cada render)
5. `slide_renderer` usa o resultado para montar o HTML template

## 15 Sub-presets disponíveis

| Family | Sub-preset | Key |
|---|---|---|
| Creator Personal | Papel Cremoso | `creator_personal_vinci` |
| Creator Personal | Amarelo Vibrante | `creator_personal_daniela` |
| Creator Personal | Caderno Pautado | `creator_personal_marketingharry` |
| Creator Personal | Dark Elegante | `creator_personal_dark_creator` |
| Corporate Premium | Cream Emocional | `corporate_premium_anabrez` |
| Corporate Premium | Cream Factual | `corporate_premium_nicolas` |
| Corporate Premium | Executivo Dark | `corporate_premium_dark_executive` |
| Editorial Sério | Jornal Clássico | `editorial_serious_cream_classic` |
| Editorial Sério | Amarelo Editorial | `editorial_serious_yellow_insper` |
| Tech/Moderno | Neon Glow | `tech_modern_dark_glow` |
| Tech/Moderno | Terminal Mono | `tech_modern_terminal_mono` |
| Bold/Provocativo | Branco Impactante | `bold_provocative_white_giant` |
| Bold/Provocativo | Dark Provocativo | `bold_provocative_dark_brandsdecoded` |
| Quente/Pessoal | Dark Acolhedor | `warm_personal_dark_intimate` |
| Quente/Pessoal | Colorido Vibrante | `warm_personal_saturated_rotativo` |

## Don'ts

- Não editar `tenant_themes` diretamente — deixar o `theme_agent` recalcular
- Cores custom (`palette_custom_primary`, `palette_custom_accent`) em `tenant_config` sobrescrevem o preset

---

## Quando usar

- Step 7 do `pipeline-orchestrator` chama `theme_agent.generate_theme` inline quando `tenant_themes` está vazio para o tenant.
- Após mudança de `preferred_sub_preset` no `tenant_config` (frontend admin) — invalidar cache + recalcular.

## Quando NÃO usar

- ❌ Em hot-path de render (cache em `tenant_themes` já existe — não chamar de novo).
- ❌ Antes do tenant ter completado fase 2 do onboarding (sem `preferred_sub_preset` definido).
- ❌ Para testar paleta custom isolada — usar tabela `tenant_config.config.palette_custom_*` direto.

## Por que funciona assim

- Cache em `tenant_themes` evita recalcular Big5 + DPR a cada render (custo LLM zero — é tabela lookup + cores).
- 15 sub-presets pré-definidos: balanço entre customização (15 opções) e operacional (não é builder de design system livre).

## 🚫 Don'ts

- **Não** editar `tenant_themes` diretamente no Supabase — deixar `theme_agent` recalcular limpo.
- **Não** adicionar sub-preset novo sem atualizar `style_configs` + template HTML correspondente em `slide_renderer`.
- **Não** sobrescrever paleta custom (`palette_custom_primary`/`palette_custom_accent`) com lógica de preset — custom tem prioridade.

## 🪦 Já tentamos

- **2026-04-25 — Renderer 38 bugs visuais**: cores erradas + tipografia inconsistente em batch grande. Fixou no template HTML, não no theme_agent. Ver incident.
- **2026-04-23 — Visual identity prompt sem acentos**: prompt LLM perdia acentuação em palavras-chave. Ver `2026-04-23_visual-identity-prompt-sem-acentos.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Slide renderizado com paleta default ignorando custom | Lógica de prioridade invertida | Verificar `palette_custom_primary` em `tenant_config` antes de aplicar preset |
| Sub-preset não aparece nas opções no onboarding | `style_configs` sem registro para combinação Big5 + signaling | Adicionar registro em `style_configs` |
| `tenant_themes` cresce sem limpar | Sem TTL — esperado | Cache permanente; invalidar manualmente ao mudar `preferred_sub_preset` |

## 📚 Referências cruzadas

- [pipeline-orchestrator](../CLAUDE.md) — Consumidor (step 7)
- [onboarding-workers](../onboarding/CLAUDE.md) — Define `preferred_sub_preset`
- [CONTEXT.md](../../../../CONTEXT.md) — Sub-preset
