---
title: Playbook Treinamento Claude Code 30d
tags: [cs, canon]
---

# Playbook — Treinamento Prático Claude Code 30 dias

> Doc constitutivo. Define como CS opera o produto "Treinamento Claude Code 30d" do contrato assinado ao follow-up pós-treinamento. **Não é consultoria** — não usa Asaas (Asaas só pra recorrência), não usa aquecimento de chip, não usa BM Meta. Substituído pelo Playbook 11 fases para esse produto.
>
> Criado 2026-06-09 a partir dos 2 primeiros deals (Eliseu Rocha + Vayne Sacaro, fechados 08/06).

---

## Princípio

Treinamento é **autoaprendizado guiado**, não delivery. CS garante:
1. Aluno chega na S1 com tudo configurado (Claude Pro, caso real, briefing preenchido)
2. As 4 sessões acontecem no ritmo combinado (1/semana)
3. WhatsApp ativo nos 30 dias (resposta em 24h úteis)
4. Aluno termina com agente próprio rodando no caso dele
5. NPS coletado D+30; aluno migra para Relacionamento se virar cliente Cadência ou consultoria

---

## Premissas do produto

| Item | Valor |
|---|---|
| Preço | R$ 6.000 (12x R$ 500) ou R$ 5.000 à vista |
| Duração | 30 dias corridos a partir da S1 |
| Sessões | 4 ao vivo individuais (~1h30 cada, 6h total), 1 por semana |
| Suporte | WhatsApp direto com Felipe, 30 dias, SLA 24h úteis |
| Bônus | Cadência grátis 30d + material posicionamento (ou escopo IA, conforme deal) |
| Requisito aluno | Claude Pro (US$20/mês) contratado antes da S1 + caso real de cliente próprio |
| Canal de aula | Videoconferência (Teams ou Google Meet) |
| Material | Frameworks PD, templates, doc da sessão |

---

## Fases — cronograma do contrato à transição

### Fase 0 — Fechamento (D+0)

**Quem:** Felipe (Comercial) + Letícia (CS receberá handoff).
**Dispara:** call de vendas que terminou no stage `fechamento` do pipeline `geracao-negocios` no CRM Cadencia.

Checklist:
- [ ] Oportunidade movida para `geracao-negocios`/`fechamento` no CRM Cadencia
- [ ] Primeira parcela cobrada via Asaas (R$ 500)
- [ ] Issue Linear "Criar contrato" criada (P1, due D+1)
- [ ] Issue Linear "CS Handoff — Onboarding" criada (P2)
- [ ] Briefing agendado no Google Calendar (sexta da semana seguinte)
- [ ] Mensagem de confirmação enviada via WhatsApp no mesmo dia

**Saída:** handoff explícito para CS no mesmo dia.

---

### Fase 1 — Contrato + Briefing (D+1 a D+3)

**Quem:** Time Jurídico (Vitória) elabora e envia; Felipe (assina) + cliente (assina).

**🆕 Fluxo via Time Jurídico (2026-06-09):** o CS **não elabora** o contrato manualmente — delega ao Jurídico via 2 skills:

1. **`/elaborar-contrato treinamento-claude-code "<Nome do Aluno>"`** (skill do Jurídico)
   - Consulta `times/juridico/foundation/map-contratos.md` (mapa Produto → Contrato)
   - Carrega o template canônico em `times/juridico/templates/contratos/treinamento-claude-code/Contrato-Treinamento-Claude-Code-30d-Template.md`
   - Puxa dados do cliente: **Asaas API** (nome oficial + CPF + email + mobile) + **transcrição da call de vendas** (estado civil, contexto, caso-base, profissão) + **ViaCEP** (endereço normalizado)
   - Salva em `times/juridico/contratos-emitidos/<slug-aluno>/Contrato-Treinamento-Claude-Code-<Aluno>-v1.md` com frontmatter de rastreio (PDL, cadencia_contact_id, asaas_customer_id)
   - **Inclui automaticamente**: 4 sessões S1-S4, WhatsApp 30d com SLA 48h úteis, Cadência 30d, bônus específico do deal, T-0 = 1ª parcela paga, caso-base se já definido pelo handoff CS

2. **`/enviar-contrato-assinatura "<slug-aluno>"`** (skill do Jurídico)
   - Converte MD → PDF (markdown-pdf)
   - Upload no **Autentique** API GraphQL (substitui Clicksign nos fluxos novos)
   - Gera **link curto** `https://assina.ae/...` via mutation `createLinkToSignature(public_id)`
   - Atualiza frontmatter com `autentique_document_id` + `autentique_short_link` + `sent_at`
   - Compõe mensagem WhatsApp (com **preview obrigatório pro Felipe** confirmar) com link de assinatura + link do form Tally `KYGZDM`
   - Dispara via Stevo (WhatsApp do Felipe)
   - Atualiza Linear (PDL contrato → In Review) + STATE Jurídico

**Papel do CS nesta fase:**
- ✅ Garantir que **handoff Comercial → CS** trouxe contexto do caso-base (transcrição da call de vendas no Vault Obsidian + perfil no Linear PDL handoff)
- ✅ Avisar Jurídico do bônus específico fechado no deal (posicionamento de marca, escopo de vendas IA, etc.)
- ✅ Acompanhar **status no painel Autentique** (`https://painel.autentique.com.br/documentos/<doc_id>`) — `email_events.sent`/`delivered`/assinado
- ✅ Se aluno não receber email Autentique em 24h: pedir Jurídico reenviar via painel ou regenerar link curto

**Checklist resumido:**
- [ ] Handoff CS → Jurídico com PDL + caso-base + bônus específico
- [ ] Jurídico roda `/elaborar-contrato` + Felipe revisa o MD (5-10 min — só campos personalizados; cláusulas operacionais V01 são intocáveis)
- [ ] Jurídico roda `/enviar-contrato-assinatura` → contrato enviado via Autentique + WhatsApp (com form Tally `KYGZDM` na mesma mensagem)
- [ ] CS confirma entrega via `email_events.delivered` no painel Autentique
- [ ] CS cobra preenchimento do form até D-1 do briefing

**Saída:** contrato no Autentique aguardando assinatura + form briefing enviado em mensagem única.

**Refs Jurídico:**
- `times/juridico/skills/elaborar-contrato.md`
- `times/juridico/skills/enviar-contrato-assinatura.md`
- `times/juridico/context/autentique-api.md` — guia completo Autentique
- `times/juridico/foundation/map-contratos.md` — mapa Produto → Contrato (consulta obrigatória)

---

### Fase 2 — Preparação para o Briefing (D+3 a D-1 da call)

**Quem:** Letícia (acompanhamento) + Felipe (preparação técnica).

Checklist do CLIENTE (cobrar antes de sexta):
- [ ] Preencher form Tally `KYGZDM` (7 seções) — até quarta da semana do briefing
- [ ] Contratar Claude Pro (US$ 20/mês) — pode esperar até a S1
- [ ] Trazer caso real de cliente próprio para usar como projeto-piloto
- [ ] Confirmar dispositivo com webcam + microfone funcionais

Checklist do CS (preparar antes de sexta):
- [ ] Ler form do cliente (ou ter pronto pra preencher em tempo real se atrasou)
- [ ] Pesquisa rápida sobre o cliente do aluno (site, redes) — 15 min
- [ ] Pasta cliente criada em `times/produto/treinamentos/<nome-aluno>/` (ou usar Vault)
- [ ] Projeto Linear `Treinamento Claude Code — <Nome>` com 9 issues (S1-S4 + entregáveis)
- [ ] Materiais da S1 separados (CLAUDE.md template, exemplos PD Framework)

**Gatilho de cancelamento:** sem form preenchido 24h antes = remarcar (regra CS — adesão 100%).

**Saída:** call de briefing acontece no horário e Felipe entra com contexto pleno do aluno.

---

### Fase 3 — Briefing (Sexta-feira, D+5)

**Quem:** Felipe + aluno.
**Duração:** 2h (9h-11h ou 14h-16h, conforme combinado). Prever até 2h30 se aluno tiver setup pendente.

**Pré-call obrigatório (D-1):** verificar via WhatsApp se `claude --version` funciona no terminal do aluno. Se não funcionar, resolver antes da call — não durante. Isso evita consumir 40min de briefing em PATH.

Estrutura (não-rígida, adaptar ao fluxo):
1. **Apresentação mútua** (10min) — Felipe se reapresenta como mentor, aluno conta trajetória de onde vem
2. **Mapeamento do caso real** (40min) — cliente do aluno, problema, contexto, stack atual, restrições + **"o que você faz melhor do que todo mundo?"** (extrai background único do aluno)
3. **Definição do MVP** (30min) — fechar 1 MVP com nome + critério de feito. Não sair sem isso
4. **Setup técnico ao vivo** (20min) — confirmar Claude Code, criar pasta, primeiro CLAUDE.md
5. **Cronograma e expectativas** (20min) — criar 4 eventos Calendar ao vivo, regras WhatsApp

**Demo do produto (inserir no Bloco 2):** se o aluno tiver cliente-caso, abrir Cadência ao vivo (5min) e buscar o CNPJ do cliente. Enriquecimento de lead ao vivo demonstra valor imediatamente e abre oportunidade de parceria (white label).

**Saída obrigatória antes de encerrar:**
- [ ] Ata da reunião (skill `/ata-reuniao`)
- [ ] MVP com nome + o que faz + critério de feito registrado no Linear
- [ ] **4 eventos Calendar criados ao vivo** (S1-S4, não deixar para depois)
- [ ] Aluno sai com Claude Code funcionando no terminal
- [ ] Tarefas da semana passadas (instalação de CLIs + leitura de doc de API externa)
- [ ] Acessos críticos para S3 mapeados + prazo explícito (ex: "sem acesso Kommo até S2, a S3 não rola")

**Atenção — fenômeno "aula 0":** alunos engajados chegam com dúvidas técnicas e o briefing vira uma sessão de fundamentos. Isso é sinal positivo — não interromper o fluxo. Documentar como "aula 0", ajustar datas (S1 uma semana depois), e usar como contexto para a S1.

**Ref detalhada:** `foundation/checklist-briefing-treinamento-claude-code.md` — checklist completo + lições do primeiro encontro (Vayne, 12/06/2026).

---

### Fase 4 — S1 a S4 (Semanas 1 a 4 do treinamento)

**Quem:** Felipe (mentor) + aluno.
**Cadência:** 1 sessão por semana, mesmo horário fixado no briefing. Cada sessão tem entregável.

| Semana | Sessão | Foco | Entregável do aluno |
|---|---|---|---|
| 1 (16/06) | S1 | Setup, CLAUDE.md, fundamentos, PD Framework por dentro | CLAUDE.md raiz + primeiro skill rodando no caso real |
| 2 (23/06) | S2 | PRD, núcleo da solução, primeira skill reutilizável | PRD do agente + 1 skill que resolve dor concreta |
| 3 (30/06) | S3 | MCPs, APIs, integrações | Conexão funcional com sistema externo do caso (CRM Cadencia, n8n, Supabase etc.) |
| 4 (07/07) | S4 | Deploy, documentação, como apresentar e cobrar | Agente rodando em prod + pitch comercial pro cliente do aluno |

**Entre sessões:**
- WhatsApp ativo — aluno manda dúvidas + screenshots + logs
- Felipe responde em até 24h úteis
- Aluno deve dedicar 4-6h/semana de prática solo (não há acompanhamento daily)

---

### Fase 5 — Marcos e Check-ins

| Quando | Quem | Ação |
|---|---|---|
| D+1 após cada sessão | Letícia | Mensagem WhatsApp curta: "Como foi? Travou em algo?" |
| Sexta da semana 2 (meio do treinamento) | Letícia | Check-in NPS provisório + pergunta "está atingindo o que esperava?" |
| D+1 após S4 | Letícia | NPS final (escala 0-10 + comentário livre) + pergunta "vai continuar com Cadência?" |
| D+15 pós-treinamento | Letícia | Follow-up: "agente está rodando? gerou venda?" |

**Critério de fracasso:**
- 2 sessões remarcadas pelo aluno = alerta ao Felipe + conversa franca
- NPS provisório <7 na metade = sessão extra de alinhamento sem cobrar

---

### Fase 6 — Transição (D+30 do início do treinamento)

**Quem:** Letícia + Felipe.

**Gatilhos do handoff:**

1. **Aluno aderiu Cadência (paga)** → vira cliente Cadência pleno → migra pra `times/produto/cadencia/` como tenant ativo + Relacionamento assume cadência de contato.

2. **Aluno virou parceiro** (vende a metodologia pros clientes dele) → registra em `times/comercial/foundation/programa-indicacao.md` + acompanhamento trimestral.

3. **Aluno ficou autônomo, sem follow-up comercial** → fecha o ciclo, mantém apenas check-in trimestral via WhatsApp + caso de sucesso documentado (se autorizado) em `times/marketing/foundation/`.

**Checklist de fechamento:**
- [ ] NPS final coletado e registrado
- [ ] Issue Linear "CS Handoff" marcada `Done`
- [ ] Pasta do aluno arquivada (Linear projeto: `Completed`)
- [ ] Se NPS ≥ 9 e autorizado: pedir depoimento + autorização de caso de sucesso
- [ ] Acesso Cadência: confirmar se quer renovar ou desativa após o 30º dia

**Saída:** Aluno tem agente próprio em prod + decidiu trilha pós-treinamento (Cadência paga / parceria / autônomo).

---

## Diferenças vs Playbook 11 fases (consultoria)

| Item | Consultoria | Treinamento Claude Code |
|---|---|---|
| Asaas | Obrigatório (Fase 4) | Não — pagamento único 12x cartão |
| Aquecimento chip WhatsApp | Obrigatório (Fase 4.5) | Não — aluno usa próprio dispositivo |
| BM Meta / conta anúncios | Obrigatório (Fase 5) | Não |
| HUB chamados | Obrigatório (Fase 9) | Não — canal é WhatsApp direto Felipe |
| Treinamento adoção (Fase 7) | Para uso CRM | É o próprio produto |
| Cadência mensal | KPIs (Fase 10) | NPS final + 1 follow-up D+15 |
| Owner do projeto | Squad consultoria (`times/produto/consultorias/<cliente>/`) | Sem Squad próprio — vive em `times/cs/onboarding/` até fim, depois arquivado ou migra |

---

## Skills associadas

- `/tally-form-briefing-cs` — gera form Tally (já existe v2 `KYGZDM`)
- `/consultar-checklist-briefing` — guia durante a call
- `/ata-reuniao` — ata da call de briefing e de cada sessão
- `/linear-criar-projeto` — projeto Linear com S1-S4 (já feito Vayne PDL-455-463)

---

## Refs

- `playbook-implementacao-11-fases.md` — referência base (consultoria)
- `checklist-briefing.md` — 11 seções (usar parcialmente — seções 1, 2, 3, 5, 7 são as mais relevantes pra treinamento)
- `times/comercial/foundation/learnings-calls-vendas.md` — perfil ideal do aluno
- Form Tally v2: `https://tally.so/r/KYGZDM`
