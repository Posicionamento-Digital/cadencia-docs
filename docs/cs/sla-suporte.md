---
title: SLA de Suporte
tags: [cs, canon]
---

# SLA de Suporte — Severidades e Tempos

> Doc constitutivo. Define quanto tempo a Cadencia leva pra responder/resolver chamados. Proposta-baseline 2026-05-25 — itens marcados ⚠️ precisam de validação Felipe + ajuste por cliente quando contratado.

---

## Severidades (4 níveis)

### P1 — Crítico
**Definição:** produção parada, bloqueio total, perda de receita ativa.
**Exemplos:**
- Bot Telegram fora do ar com cliente esperando resposta
- IA/integração não responde, atendimentos param
- Cliente perdendo lead/venda em tempo real

**Canal obrigatório:** Telefone + WhatsApp pessoal Felipe (Stevo)
**Tempo primeira resposta:** **30 min** (horário comercial 09h-17h30 BRT) / **2h** (fora desse horário, 18h-22h)
**Tempo resolução alvo:** **4h** (horário comercial) / **próximo dia útil 09h** (fora)
**Escalation imediata:** Felipe (gestão) + Luiz (técnica) em paralelo

### P2 — Alto
**Definição:** funcionalidade core impactada, contorno possível mas degradado.
**Exemplos:**
- IA respondendo lento (alucinação ocasional)
- CRM sincronizando com atraso
- Bot Telegram responde mas FAQ desatualizado

**Canal:** WhatsApp ou Hub
**Tempo primeira resposta:** **2h** (horário comercial)
**Tempo resolução alvo:** **1 dia útil**
**Escalation:** Luiz (técnica). Felipe só se ultrapassar 1 dia.

### P3 — Médio
**Definição:** bug não-bloqueante, irritante mas operacional.
**Exemplos:**
- Erro de tipografia em mensagem da IA
- Botão do Bot Telegram com texto errado
- Dashboard mostra valor desatualizado

**Canal:** Hub/Esteira (Obsidian — vault Time PD; Notion descontinuado)
**Tempo primeira resposta:** **1 dia útil**
**Tempo resolução alvo:** **3 dias úteis**
**Escalation:** Luiz via Linear backlog.

### P4 — Baixo
**Definição:** melhoria, dúvida resolvível por FAQ, cosmético.
**Exemplos:**
- "Como funciona feature X?"
- Sugestão de cor/copy
- Dúvida de uso

**Canal:** Hub/Esteira (Obsidian — vault Time PD; Notion descontinuado)
**Tempo primeira resposta:** **3 dias úteis**
**Tempo resolução alvo:** sem prazo definido (entra em backlog)
**Escalation:** CS resolve (FAQ + treinamento). Sem envolvimento Dev.

---

## Janela de atendimento

| Horário | Cobertura |
|---|---|
| 09h-17h30 BRT (seg-sex) | Horário comercial Felipe — todos níveis |
| 17h30-22h (seg-sex) | Apenas P1 atende (via telefone + Stevo) |
| Fins de semana | Apenas P1 (Felipe avalia caso a caso) |
| Feriados nacionais | Apenas P1 |

**Regra global:** após 17h30 trabalho é PROIBIDO (anti-burnout — ver `stamper/CLAUDE.md`). P1 é exceção justificada.

---

## Escalonamento

```
Chamado recebido
       ↓
Triagem CS vs Suporte (separacao-cs-suporte.md)
       ↓
   ┌───┴───┐
   ↓       ↓
   CS    Suporte → Severidade P1-P4
                       ↓
                P1 → Felipe (gestão) + Luiz (técnica) imediato
                P2 → Luiz via Linear, Felipe se exceder SLA
                P3 → Luiz backlog
                P4 → CS resolve (FAQ/treinamento)
```

**Quando CS escala pro Luiz:**
- Sempre que demanda virar Suporte Técnico (bug técnico)
- Sempre via Linear (registro), não WhatsApp direto

**Quando Luiz escala pro Felipe:**
- Bug que ele não consegue replicar
- Decisão de prioridade conflitando com Cadência/PD Portal
- Mudança que afeta múltiplos clientes (decisão de arquitetura)

---

## Diferenciação por contrato

⚠️ **EM ABERTO — Felipe definir.** Proposta inicial:

| Tipo de contrato | SLA aplicado |
|---|---|
| **Cadencia Consultorias** (R$10k-50k/mês, high-touch) | SLAs acima sem alteração — clientes high-touch já estão no nível premium |
| **Cadência self-serve** (R$119-499/mês) | SLAs P2-P4 com prazos +50% — sem suporte direto Felipe, escalation só via Bot ou Linear |
| **GCI GO** (contrato grande, multi-unidade) | SLAs como Cadencia Consultorias + ponto de contato dedicado (Felipe pessoalmente) |
| **Franquia Gestor de IA** | SLAs como Cadencia Consultorias (alta dependência relacional) |

Validar com Felipe antes de comunicar SLA a cliente novo.

---

## Comunicação ao cliente

No Kickoff (Fase 2 do Playbook), incluir SLA no **Checklist de Responsabilidades por Parte**:
- Canal oficial pra cada nível
- Tempo de resposta esperado
- O que NÃO é coberto (mudança de escopo = nova proposta, não chamado P3)
- Como abrir chamado (qual canal pra qual severidade)

Documento padrão a desenvolver: template "SLA por contrato" anexável ao Kickoff.

---

## Métricas e auditoria

- **SLA aderência por severidade** — % chamados respondidos dentro do prazo
- **Tempo médio de resolução por severidade** — vs alvo
- **Distribuição de severidades** — saudável: P3-P4 dominam, P1 raro. Se P1-P2 dominam, produto está instável.

KPI 5 do CS (Eficiência de Resolução >60%) — relacionado mas não igual. SLA é tempo; KPI 5 é taxa de resolução sem escalar.

---

## ⚠️ Itens pendentes de Felipe validar

1. **Tempos P1-P4** — números acima são proposta; ajustar conforme capacidade real
2. **Janela após 18h** — confirmar regra "P1 atende via telefone" ou criar exceção
3. **Diferenciação por contrato** — confirmar SLAs por tipo de cliente
4. **Template SLA pro Kickoff** — criar versão pronta pra anexar ao contrato

Validar e ajustar via `linear-atualizar-issue PDL-267` ou edição direta deste arquivo.

---

## Refs

- `rotina-cs.md` KPI 5 Eficiência de Resolução
- `separacao-cs-suporte.md` — PEDRA ANGULAR (CS vs Suporte)
- `playbook-implementacao-11-fases.md` Fase 2 (definir SLA no Checklist Responsabilidades)
- `checklist-briefing.md` seção 10 (SLA esperado pelo cliente)
- `suporte/skills/abrir-chamado-hub.md` (skill usa estas severidades)
- `stamper/CLAUDE.md` regra global "depois das 17:30 PROIBIDO"
