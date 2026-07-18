---
title: Protocolo de Aquecimento de Chip WhatsApp — 14d
tags: [cs, canon]
---

# Protocolo de Aquecimento de Chip WhatsApp — 14 dias

> Doc constitutivo. **Operação crítica** — risco de banimento Meta. Aplicado na Fase 4.5 do Playbook 11 fases.
> Fonte: Notion "Playbook Checklist de Implementações", seção 4.5. Consolidado 2026-05-25.

---

## Princípio fundador

> ⚠️ **Maturação não é ciência exata, é gestão de risco. Consistência vence velocidade.**

**Regra de escalonamento absoluta:** crescimento máximo de 20% ao dia (**logarítmico, não exponencial**). Tentar acelerar = risco de ban.

📩 **Envio obrigatório ao cliente ANTES do Dia 1:**
- 📊 Apresentação do processo de implementação (próximas semanas)
- 🎬 Vídeo do protocolo de maturação (define expectativas corretas)

Sem alinhamento prévio, cliente pressiona pra acelerar → quebra protocolo → ban.

---

## Pré-requisitos (validar ANTES do Dia 1)

- [ ] **Dispositivo físico dedicado** (não reaproveitar aparelho banido sem factory reset)
- [ ] **IMEI não banido** (verificar histórico do aparelho)
- [ ] **Conexão 4G/5G obrigatória** na ativação — Wi-Fi proibido (Meta diferencia metadata de IP móvel vs fixo)
- [ ] **Foto de perfil real configurada** (não logo, não imagem genérica)
- [ ] **2FA ativado no Dia 1**

Sem QUALQUER um desses, NÃO iniciar protocolo.

---

## Protocolo por fase

### Fase 1 — Nascimento Digital (Dias 1-3)

**Objetivo:** estabelecer presença autêntica antes de qualquer outbound.

- **Dia 1:** Ativar via 4G, foto real, ativar 2FA, cadastrar em app externo (Uber/iFood) pra receber SMS de verificação (sinaliza número "vivo" pra Meta)
- **Dia 2:** Círculo de Confiança — 3 a 5 contatos salvam o número e mandam mensagem PRIMEIRO (whitelisting natural)
- **Dia 3:** Aquecimento passivo — entrar em grupos SEM falar; scroll pra gerar "Time on App" (métrica que Meta usa)

### Fase 2 — Validação de Humanidade (Dias 4-6)

**Objetivo:** provar que é humano operando, não bot.

- **Dia 4 (crítico):** Chamadas de voz em movimento pra triangulação de torres (Proof of Mobile Device — algoritmo Meta valida que dispositivo se move geograficamente)
- **Dia 5:** Engajamento fantasma — postar Status; reagir com emojis em grupos (SEM texto ainda)
- **Dia 6:** Primeiro outbound — 5 a 10 mensagens MANUAIS, apenas texto, sem links; objetivo: Double Check Azul

### Fase 3 — Enriquecimento (Dias 7-10)

**Objetivo:** diversificar tipos de interação pra simular comportamento humano completo.

- **Dia 7:** Variação de mídia — enviar áudios gravados na hora (**live recording**); sistema diferencia metadata de áudio ao vivo vs encaminhado
- **Dia 8:** Micro-compromissos — perguntas que forçam um "Sim"; se taxa de resposta < 40%, PARAR (sinal de que abordagem não está convertendo, ajustar antes de seguir)
- **Dia 10:** Spintax manual — 40-50 mensagens com variação de saudações (Olá/Oi/E aí) pra evitar hash repetitivo

### Fase 4 — Consolidação e Escala (Dias 11-14)

**Objetivo:** transferir gradualmente pra operação automatizada com salvaguardas.

- **Dia 11:** Backup na nuvem (Google Drive/iCloud) — sinaliza valor da conta pro algoritmo
- **Dia 12:** Links APENAS na 2ª mensagem (após resposta); usar domínios HTTPS próprios (não shorteners)
- **Dia 13:** Iniciar automação com **delay alto (60-180s) e jitter aleatório**; monitorar notificações do sistema
- **Dia 14:** Validação final; acionar a Cadencia para conexão ao BM (Business Manager Meta)

---

## Monitoramento de Quality Score

Acompanhamento **diário** durante os 14 dias e contínuo após.

| Status | Significado | Ação |
|---|---|---|
| 🟢 **Verde** | Alta Qualidade — operação normal | Prosseguir |
| 🟡 **Amarelo** | Média Qualidade | **Interromper campanhas IMEDIATAMENTE**, aguardar normalização |
| 🔴 **Vermelho** | Baixa Qualidade / Flagged | **Risco de ban em 7 dias**; acionar protocolo de crise |

### Protocolo Soft Ban (recurso)

Quando cair em Amarelo persistente ou suspensão temporária:
- NÃO usar termos técnicos no recurso
- Alegar roubo do aparelho OU hack via engenharia social reversa
- (técnica do playbook original — funciona em muitos casos)

### Protocolo Hard Ban (limpeza)

Quando banido em definitivo:
1. **Descartar o chip** (sem tentar reativar)
2. Limpar cache/dados ou **factory reset** no aparelho
3. **Reiniciar modem** (troca de IP)
4. Reiniciar do **Dia 1 com novo número**

NUNCA reutilizar aparelho banido sem limpeza completa — ban se propaga.

---

## Responsabilidades

| Parte | Responsabilidade |
|---|---|
| **Equipe do Cliente** | Executar protocolo diário; comparecer aos treinamentos; listar dúvidas; entregar número do Gestor de Tráfego à Cadencia ainda nessa fase |
| **Cadencia (CS + Luiz)** | Conduzir treinamentos; **monitorar Quality Score**; acionar protocolo de crise se necessário; fazer conexão do número ao BM ao final dos 14 dias |
| **Gestor de Tráfego do Cliente** | Disponibilizar número; aguardar acionamento da Cadencia pra verificação do BM (Fase 5 do Playbook) |

---

## Entregáveis e Critérios de Saída

**Entregáveis:**
- Número com Quality Score Verde e pronto pra conexão
- Equipe do cliente treinada e operando com autonomia

**Critérios de saída (TODOS os 4):**
- [ ] 14 dias concluídos
- [ ] Quality Score Verde
- [ ] Equipe apta (treinada)
- [ ] Número entregue à Cadencia pra integração (Fase 5)

Se algum dos 4 não bater → estender protocolo ou reiniciar conforme severidade.

---

## Observações operacionais

⚠️ **Não conectar o número antes dos 14 dias**, independente de pressão do cliente. Pressão é gerenciada com alinhamento de expectativas (apresentação + vídeo do Dia 1).

⚠️ **Jamais reutilizar aparelho banido sem limpeza completa.**

⚠️ **Não enviar links na primeira mensagem de nenhuma fase.** Links apenas após resposta do cliente.

⚠️ **Monitoramento de Quality Score é responsabilidade da Cadencia durante os 14 dias** — não delegar ao cliente. Cliente executa; Cadencia monitora.

---

## Roadmap automação (backlog Linear)

- **cron monitor Quality Score chip durante aquecimento** — alerta diário status amarelo/vermelho por cliente em maturação
- Dashboard centralizado de chips em aquecimento (qual dia, qual quality, qual cliente)
- Lembrete automático Dia 1 com checklist de pré-requisitos

Ver `times/cs/workers/README.md` pra lista completa de workers candidatos.
