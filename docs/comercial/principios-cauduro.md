---
title: Princípios Cauduro
tags: [comercial, canon]
---

# Princípios Cauduro (adaptados para operação solo + automação)

> Princípios operacionais baseados em Eduardo Cauduro (SLG, "Como Montar um Time de Vendas que Fatura Milhões" — Excepcionais Podcast 25/05) + Andrew Grove + Jeb Blount.
> Adaptados para realidade PD: operação solo (Felipe Closer único) + automação pesada via Sistema Comercial PD.
> Consolidado 2026-05-25.

---

## 1. Atuação alavancada do gestor (Andrew Grove → Cauduro)

**Princípio:** uma ação que multiplica o output do time inteiro vale muito mais do que executar a tarefa diretamente.

**Cauduro:** "30 minutos no início do dia faz com que todas as horas de trabalho de uma equipe inteira seja muito mais produtiva no dia que vem a seguir."

**Aplicação PD (solo+automação):**
- 6-12h documentando playbook valem mais do que semanas resolvendo dúvidas operacionais repetidas
- Tempo investido em workers/automação > tempo gasto em execução manual repetitiva
- Toda decisão recorrente vira regra escrita em foundation/ ou config do Sistema Comercial PD
- **A hora do Felipe é a mais cara da empresa** — automatize antes de operar

---

## 2. "Se falou e não escreveu, então não falou" (Cauduro citando o sócio Rodrigo)

**Princípio:** processo verbal não existe. Toda decisão, regra, exceção, aprendizado vira documento escrito.

**Aplicação PD:**
- Decisões importantes → `memory/decisions.md` (Time ou sub-squad)
- Aprendizados de objeção → `foundation/playbook-objecoes.md`
- Mudança de cadência → `foundation/cadencia-10d.md` + `decisions.md`
- Config técnica → `context/stack-tecnico.md`
- Nada fica "na cabeça do Felipe"

---

## 3. "Criança de 8 anos" (Cauduro)

**Princípio:** processo de vendas deve ser escrito como instrução para criança de 8 anos. Se não cabe numa folha do Google Drive, está complexo demais para ser seguido.

**Aplicação PD:**
- Foundation docs escritos em linguagem simples e direta
- Scripts da cadência prontos para copiar e colar, sem ambiguidade
- Cada skill tem objetivo, gatilho e ação clara
- Templates de proposta com placeholders explícitos
- Workers do Sistema Comercial PD têm input/output bem definidos

---

## 4. "20×5 bate 100×1" (Jeb Blount → Cauduro)

**Princípio:** entrar em contato 5 vezes com 20 leads via múltiplos canais converte muito mais do que 100 contatos únicos. Profundidade + multicanalidade > volume bruto.

**Aplicação PD:**
- Cadência 10D = 7 touchpoints em ~200 leads/mês (não 1 touchpoint em 1.000 leads)
- Triangulação de canais (Ligação + WhatsApp + LinkedIn + Email + Instagram) elimina percepção de spam
- Mesma mensagem em canais diferentes parece elegante. Mesma mensagem repetida no mesmo canal parece assédio.

---

## 5. Especialização gera escala (Cauduro)

**Princípio original:** separar SDR (prospecção), Closer (fechamento), Farmer (carteira) para ganhar escala sem aumentar custo proporcionalmente.

**Adaptação PD (solo + automação):**
- Não temos pessoas — temos **funções automatizadas**
- `geracao-de-demanda` (Mafê) consolida LDR + SDR + BDR via Sistema Comercial PD (workers determinísticos)
- `geracao-de-negocios` (Roberto) é função humana (Felipe Closer) + skills auxiliares
- Especialização não vem do organograma, vem da **separação de processos**

---

## 6. Comissionamento como comunicação (Cauduro)

**Princípio:** aceleradores e desaceleradores de comissão moldam comportamento com mais precisão do que reuniões.

**Aplicação PD (solo):**
- Não aplicável diretamente (sem time humano)
- Mas: **lógica equivalente** para Sistema Comercial PD — config de workers tem aceleradores (lead de indicação = prioridade) e desaceleradores (lead fora do ICP = arquivar automaticamente)
- Programa de Indicação: comissão escalonada (5-10%) com aceleradores por trilha = mensagem clara pra parceiros

---

## 7. Documentar antes de contratar (Cauduro)

**Princípio:** "Você precisa aprender antes de delegar, e documentar antes de contratar."

**Aplicação PD:**
- Felipe operou cada papel comercial (LDR/SDR/BDR/Closer/Farmer) por anos
- Documentou tudo em wiki + skills + Sistema Comercial PD
- **Não vai contratar para escalar — vai automatizar**
- Se eventualmente contratar (cenário futuro): playbook já estará pronto pra onboarding

---

## 8. Ciclo trimestral de avaliação (Cauduro)

**Princípio original:** 1° mês abaixo da meta → feedback. 2° mês → aviso. 3° mês → desligamento.

**Adaptação PD (solo + automação):**
- Não aplica a pessoas (só Felipe)
- Aplica a **iniciativas/workers**: se cadência 10D não bater meta de 10 reuniões/mês por 3 meses consecutivos → revisar estratégia (mudar trilha alvo, ajustar mensagem, refazer ICP)
- Forecast mensal em `rituais-solo.md` força essa avaliação periódica

---

## 9. Alta performance é angular (Cauduro)

**Princípio:** disciplina em uma área (fisiculturismo, esporte) transborda para outras (negócio).

**Aplicação PD:**
- Felipe respeita ciclo cognitivo (Stamper sabe: pico 10h-13h, encerramento 17:30, blocos 90min, caminhadas obrigatórias)
- Disciplina de rituais comerciais (daily, weekly, forecast) vem do mesmo padrão de honrar compromissos consigo mesmo
- Quem honra compromisso interno honra com cliente e parceiro

---

## 10. IA em vendas hoje (Cauduro identifica 2 usos maduros)

**Uso 1:** Resposta inbound instantânea (tipo Layla)
- Lead form/Instagram/WhatsApp respondido em <1min, sem esperar SDR humano
- **Status PD:** ❌ não existe. Gap a registrar como roadmap (issue Linear futura)

**Uso 2:** Análise de gravações de call cruzada com playbook
- IA escuta call, compara com framework REP-G + Challenger, gera feedback estruturado
- **Status PD:** ❌ não existe. Gap a registrar como roadmap (issue Linear futura)

Ambos devem entrar no escopo do Sistema Comercial PD em fases posteriores.

---

## Aplicação prática diária

**Toda vez que Felipe operar comercial, pergunte:**
- Estou agindo de forma alavancada ou apenas executando?
- Esse aprendizado está escrito ou só na minha cabeça?
- O processo cabe em 1 página simples?
- Estou triangulando canais ou repetindo no mesmo?
- Posso automatizar isso no Sistema Comercial PD em vez de operar manual?
- Tem comissão/aceleração escrita pra parceiros ou só verbal?

---

## Refs

- `rituais-solo.md` — operacionalização desses princípios em rituais semanais/mensais
- `../context/stack-tecnico.md` — Sistema Comercial PD = aplicação prática da "atuação alavancada"
- Estudo Cauduro: `C:\Users\felip\Obsidian_Vaults_Pessoal\Estudo\Vendas\2026-05-25_como-montar-time-vendas-fatura-milhoes.md`
