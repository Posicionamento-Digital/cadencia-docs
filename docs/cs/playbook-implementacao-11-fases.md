---
title: Playbook de Implementação — 11 fases
tags: [cs, canon]
---

# Playbook de Implementação de Novos Clientes Cadencia — 11 fases

> Doc constitutivo. Define como qualquer Squad de consultoria (`times/produto/consultorias/<cliente>/`, `times/produto/gci-go/`) implementa um cliente novo, do contrato à transição. CS é dono do template; consultorias executam.
> Fonte: Notion "Playbook Checklist de Implementações" (`29ba96f9516a80db936fd57b1bfe7340`). Consolidado 2026-05-25.

---

## Princípio fundador

**Nenhuma etapa começa sem que o checklist da fase anterior esteja completo.** Validar critério de saída antes de mover de fase. Registrar TUDO que for decisão em ata vinculada ao card do cliente.

Responsável transversal: **Felipe (CS Lead)** + **Squad de consultoria executor** (Cadencia: CS, Gestor de IA, Dev, Tráfego, Suporte; Cliente: Responsável projeto, Operação, Marketing/Vendas, TI quando houver).

---

## Fase 0 — Abertura Oficial do Projeto

🚫 **O projeto só começa após este checklist estar completo.**

- Criar projeto do cliente no Linear (substituiu Todoist) com tarefas e subtarefas organizadas por fase → ver `/linear-criar-projeto` (skill global)
- Criar documento do cliente no Obsidian (vault Time PD, pasta Projetos/<cliente>) com info inicial (nome, responsável Cadencia, data início, status "Em abertura") + registrar o cliente no CRM Cadencia (pipeline `ciclo-vida`/`cliente-novo`)
- Confirmar registros vinculados e acessíveis pelo time

**Entregáveis:** projeto Linear estruturado + página Obsidian criada + contato no CRM Cadencia
**Critério de saída:** Linear com tarefas e prazos + página com status "Em andamento"
**Responsável:** CS + Gestor do projeto na Cadencia

---

## Fase 1 — Pré-onboarding

Validar requisitos mínimos e preparar cliente pro kickoff.

- Validar contrato e dados fiscais
- Confirmar responsáveis (lado cliente + lado Cadencia)
- Checar pré-requisitos técnicos (domínios, acessos, integrações)
- Enviar e coletar **Formulário de Briefing** (ver `checklist-briefing.md`)
- Usar dados do briefing pra cadastrar: **Hub/Esteira** (suporte e conexões IA — Obsidian, vault Time PD), **CRM Cadencia** (contato + pipeline `ciclo-vida`), **Asaas**, página do cliente no Obsidian

**Entregáveis:** contrato assinado + briefing organizado + lista de acessos mapeada
**Critério de saída:** cliente apto pro kickoff com informações essenciais em mãos

---

## Fase 2 — Onboarding / Kickoff

Reunião de alinhamento sobre contrato, responsabilidades, escopo, cronograma. Apresentar visão do CRM e do HUB.

- Reunião de apresentação de soluções, papéis e cronograma
- Definir canais de comunicação e SLAs
- Apresentar o HUB e como abrir chamados
- **Gerar e validar Checklist de Responsabilidades por Parte** (documento visual com obrigações separadas por: Cadencia, Equipe do Cliente, Gestor de Tráfego)
- Materiais obrigatórios enviados ANTES do kickoff: 📊 Apresentação Institucional + 🎬 Vídeo de Onboarding

**Entregáveis:** ata com decisões/próximos passos/responsáveis + Checklist de Responsabilidades assinado por cada parte
**Critério de saída:** time do cliente sabe acessar o HUB e pedir suporte + todos cientes das obrigações antes de iniciar

---

## Fase 3 — Setup do CRM e Pipelines

Configurar funis, estágios, regras e rotinas operacionais.

- Parametrizar pipelines e estágios
- Ajustar regras operacionais, automações essenciais e campos padrão
- Criar páginas orientativas para uso inicial

**Entregáveis:** CRM funcional com pipelines acordados
**Critério de saída:** fluxo feliz `lead → oportunidade → negócio` funcionando em testes

---

## Fase 4 — Cadastro Asaas (Cobrança)

Habilitar cobrança recorrente e documentos fiscais ANTES das IAs.

- Registrar CNPJ, razão social, dados fiscais
- Cadastrar dados financeiros, métodos e regras de cobrança no Asaas
- Validar emissor, webhooks e ambiente de testes (quando aplicável)

**Entregáveis:** conta/cliente configurado no Asaas com cobrança ativa
**Critério de saída:** dados fiscais e financeiros validados e prontos pra faturamento
**Observação:** esta fase PRECEDE integrações e IAs pra evitar bloqueios operacionais

---

## Fase 4.5 — Aquecimento de Chip WhatsApp (14 dias)

⚠️ Operação crítica. Risco de banimento Meta. Detalhes completos em `protocolo-aquecimento-chip-14d.md`.

**Pré-requisitos (validar antes do Dia 1):**
- Dispositivo físico dedicado (não reaproveitar aparelho banido sem factory reset)
- IMEI não banido
- Conexão 4G/5G obrigatória na ativação (Wi-Fi proibido)
- Foto de perfil real configurada
- 2FA ativado no Dia 1

**Protocolo por fase:**
- **Fase 1 — Nascimento Digital (Dias 1-3)**: ativação, círculo de confiança, aquecimento passivo
- **Fase 2 — Validação de Humanidade (Dias 4-6)**: chamadas de voz, engajamento fantasma, primeiro outbound
- **Fase 3 — Enriquecimento (Dias 7-10)**: variação de mídia, micro-compromissos, spintax manual
- **Fase 4 — Consolidação e Escala (Dias 11-14)**: backup nuvem, links na 2ª mensagem, automação com delay alto, validação final

**Quality Score monitorado:** 🟢 Verde / 🟡 Amarelo (interromper campanhas) / 🔴 Vermelho (risco ban em 7d, acionar protocolo crise)

**Regra de escalonamento:** crescimento máximo 20% ao dia (logarítmico, não exponencial).

📩 Envio obrigatório ao cliente ANTES do Dia 1: apresentação do protocolo + vídeo de expectativas.

**Critério de saída:** 14 dias concluídos + Quality Score Verde + equipe cliente apta + número entregue à Cadencia pra integração

---

## Fase 5 — Integrações e IAs

Conectar canais, configurar IAs, validar fluxos em ambiente real.

- **Verificação BM e Conta de Anúncios** (responsabilidade Gestor de Tráfego do cliente, acionado pela Cadencia ao final dos 14 dias):
  - Verificar Business Manager (BM) Meta
  - Verificar conta de anúncios vinculada
  - Conectar o número WhatsApp aquecido ao BM
- Conectar WhatsApp, Instagram, telefone e outras fontes
- Definir distribuição de leads e regras de roteamento
- Rodar testes controlados fim-a-fim

**Entregáveis:** BM e conta de anúncios verificados + canais conectados e testados
**Critério de saída:** número conectado ao BM sem pendências; mensagens/atendimentos fluindo sem erros críticos

---

## Fase 6 — Comunicação com o Cliente

Garantir clareza, consistência e registro das interações.

- Disparar comunicações padrão de alinhamento
- Registrar decisões e próximos passos após reuniões
- Padronizar follow-ups semanais

**Entregáveis:** histórico de comunicação centralizado
**Critério de saída:** cliente entende status atual e próximos passos

---

## Fase 7 — Treinamento e Adoção

Conduzir cliente no uso diário do CRM e das rotinas.

- Sessões guiadas com usuários-chave
- Entregar materiais de referência e boas práticas
- Orientações específicas por produto/serviço

**Entregáveis:** usuários treinados com tarefas práticas concluídas
**Critério de saída:** time do cliente executa as rotinas essenciais de forma autônoma

---

## Fase 8 — Acompanhamento de Implementação

Garantir geração de valor no dia a dia e ajustar o que for preciso.

- Reuniões semanais CS x Cliente (template em `relacionamento/context/template-reuniao-semanal.md` — 6 blocos)
- Checar o que já está útil na rotina e remover bloqueios
- Priorização de melhorias

**Entregáveis:** plano de ação vivo com responsáveis e prazos
**Critério de saída:** indicadores mínimos de sucesso atingidos (ex: tempo de resposta, taxa de conversão)

---

## Fase 9 — Suporte Contínuo via HUB

Registrar e tratar demandas com prioridade correta. **Respeitar separação CS vs Suporte Técnico** (`separacao-cs-suporte.md`).

- Abrir chamados com descrição, impacto e prioridade
- Documentar correções e mudanças
- Alinhar diretrizes entre IA e atendimento humano

**Entregáveis:** base de conhecimento e histórico de chamados
**Critério de saída:** redução de incidentes recorrentes e tempo de resolução

---

## Fase 10 — Transição para Monitoramento e Evolução

Estabilizar operação e planejar próximos incrementos.

- Revisões periódicas de KPIs e qualidade
- Backlog de otimizações e roadmap de expansão
- Planejamento de novos produtos/integrações

**Entregáveis:** relatório de estabilização e plano de evolução
**Critério de saída:** operação estável e ciclo de melhoria contínua ativo

---

## Métricas sugeridas (transversais)

- Tempo de resposta inicial
- Taxa de conversão por etapa do funil
- No-shows e taxa de reagendamento
- Tempo médio de resolução de chamados

---

## Papéis típicos

- **Cadencia:** CS, Gestor de IA, Dev (Luiz), Tráfego, Suporte
- **Cliente:** Responsável de projeto, Operação (ex: CRC no caso GCI), Marketing/Vendas, TI (se houver)

---

## Observações operacionais

- Registre TUDO que for decisão em ata e mantenha links no card do cliente
- Sempre valide critérios de saída antes de mover de fase
- A skill `/linear-criar-projeto` cria 12 fases (legado) — CS é dono do template e ajusta pra refletir estas 11 fases conforme migração
