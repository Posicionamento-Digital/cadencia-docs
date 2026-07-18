---
title: Sistema de Comunicação com Cliente
tags: [cs, canon]
---

# Sistema de Comunicação com Cliente — E-mail + WhatsApp por Etapa

> **Doc constitutivo. Leitura obrigatória para qualquer agente que vá comunicar com cliente.** Define como a Cadencia dispara e-mails e WhatsApps padronizados, determinísticos, por etapa do Playbook CS — sem perder tempo redigindo e sem enviar comunicação de cliente para lead.
> Criado 2026-06-17. Owner: Time CS (Letícia).

---

## Princípio

Toda **etapa concluída** e toda **reunião realizada** com um cliente gera uma comunicação registrada (e-mail formal + WhatsApp de toque rápido), a partir de **templates versionados** — nunca texto improvisado. Isso padroniza tom, reduz tempo e garante rastro.

## Componentes (onde tudo vive)

| Peça | Caminho | Função |
|---|---|---|
| Templates e-mail | `times/cs/foundation/templates-email/` | 1 `.md` por evento (frontmatter + `{{placeholders}}`) |
| Templates WhatsApp | `times/cs/foundation/templates-whatsapp/` | versão curta/informal de cada evento |
| Motor | `_shared/email_templates.py` | `render(evento, vars, canal)`, `send(...)`, `list_templates(canal)` |
| Gate de cliente | `_shared/cliente_registry.py` | `resolve()`, `is_cliente()` — bloqueia lead |
| Envio e-mail | `_shared/email_client.py` | SMTP Hostinger (felipe@cadencia.ia.br) |
| Envio WhatsApp | `_shared/stevo_client.py` + skill `/mandar-whatsapp` | número pessoal Felipe |
| Skill orquestradora | `/email-cliente <evento> <cliente>` | gate → template → preenche → envia |

## REGRAS ABSOLUTAS (não-negociáveis)

1. **GATE DE CLIENTE PRIMEIRO, SEMPRE.** Antes de qualquer disparo, rodar `cliente_registry.resolve("<nome>")`. Se `is_cliente=false` → **NÃO enviar** (é lead/prospect). Comunicação de etapa é só para cliente registrado (pasta / linear-squad-map / contrato emitido).
2. **WhatsApp NUNCA auto-envia.** Sai do número pessoal do Felipe → exige confirmação textual explícita ("manda", "pode enviar") antes de disparar. Todos os templates WhatsApp são `auto:false`.
3. **E-mail em modo híbrido:** `auto:true` (baixo risco: boas-vindas, go-live, treinamento) envia direto; `auto:false` (conteúdo específico: resumo de reunião, kickoff, cobrança) exige preview de 1 toque.
4. **Nada sai pela metade.** Variável faltando → o motor bloqueia. Não inventar conteúdo: puxar de fonte real (pasta do cliente, ata, contrato, Linear) ou perguntar.
5. **Grafia do produto: "Cadencia" (sem acento).** Sempre.
6. **Novo evento/etapa → criar template novo** em `templates-email/` e `templates-whatsapp/`. Nunca hardcodar corpo de e-mail na skill ou no código.
7. **Sem títulos ("Dr.", "Dra.", "Sr.", "Sra.") ao se dirigir ao cliente**, mesmo quando o cliente tem título profissional (médico, dentista, advogado etc.) — usar primeiro nome direto. Decisão Felipe: tratar o cliente por título o coloca numa posição hierárquica acima dele na relação comercial; ele quer ser visto como igual ou autoridade na conversa, nunca subordinado ao status do cliente. Vale para qualquer squad/persona que escreva em nome do Felipe (caso concreto: sócios da OP Odontopenha, ambos dentistas, tratados só como "Guilherme"/"Rodrigo").

## Catálogo de eventos ↔ fases do Playbook 11 fases

| Fase do playbook | Evento (template) | E-mail | WhatsApp | Disparo |
|---|---|:--:|:--:|---|
| 0 — Abertura oficial | `00-boas-vindas` | auto | confirma | contrato assinado + pagamento (T-0) |
| 1 — Pré-onboarding | `01-briefing-e-insumos` | preview | confirma | enviar form + pedir acessos/materiais |
| 2 — Onboarding/Kickoff | `02-pos-kickoff` | preview | confirma | após a reunião de kickoff |
| 4.5 — Aquecimento chip 14d | `045-protocolo-chip` | preview | confirma | antes do dia 1 (só CRM-PD/IA WhatsApp) |
| 5 — Integrações/Go-Live | `05-go-live` | auto | confirma | sistema migrado para produção |
| 7 — Treinamento | `07-treinamento-agendado` | auto | confirma | datas + materiais |
| 8 — Acompanhamento | `reuniao-realizada` | preview | confirma | toda reunião de acompanhamento |
| 10 — Transição | `10-transicao` | preview | confirma | estabilização + plano de evolução |
| Transversal — reunião | `reuniao-realizada` | preview | confirma | qualquer reunião com cliente |
| Transversal — pendências | `cobranca-insumos` | preview | confirma | cobrar materiais que faltam |

**Fases sem e-mail de etapa:** 3 (Setup CRM), 4 (Asaas) e 9 (Suporte) são internas/contínuas. 6 (Comunicação) é o próprio uso deste sistema.

**Adaptação por produto:** nem toda etapa aplica a todo produto (ex.: Cadencia Bundle de conteúdo não tem chip/CRM/Asaas). Ver matriz em `template-checklist-projeto-linear.md`.

## Cascatas (gatilhos automáticos)

- **`/ata-reuniao` (Passo 7):** após a ata de uma reunião, roda o gate; se cliente → oferece `reuniao-realizada` (e-mail de resumo, preview) + WhatsApp de aviso. **Reunião com lead não dispara.**
- **`/linear-close-issue`:** ao fechar uma issue de fase de implementação, oferece o e-mail de etapa correspondente (kickoff→02, go-live→05, treinamento→07, transição→10).

## Como usar (manual)

```bash
# 1. Gate
python _shared/cliente_registry.py "Mel Quevedo"
# 2. Ver templates
python _shared/email_templates.py list                 # e-mail
python _shared/email_templates.py render <evento> --var nome=Mel ...
```
Ou simplesmente invocar a skill `/email-cliente <evento> <cliente>`, que faz tudo (gate, e-mail, preenche, híbrido, registra).

## Refs
- `playbook-implementacao-11-fases.md` — as fases
- `templates-email/README.md` + `templates-whatsapp/README.md` — mapas dos canais
- `template-checklist-projeto-linear.md` — adaptação por produto
- skill `/email-cliente`, `/mandar-whatsapp`, `/ata-reuniao`, `/linear-close-issue`
