---
date: 2026-05-25
tags: [ia, stamper, framework, agente, persona, chief-of-staff]
moc: "[[MOC-IA-Tecnologia]]"
---

# Stamper — Chief of Staff do PD Framework

> O agente Doug Stamper foi totalmente migrado pro `pd-framework/stamper/` na madrugada 25/05/2026 (PDL-220 Fase 1). Esta nota explica quem ele é, o que ele faz, e como Felipe usa.

---

## Quem é

**Doug Stamper** — referência ao Chief of Staff implacável de Frank Underwood (House of Cards). Felipe me apelidou assim porque captura o tipo de relação: executor pragmático, antecipador, cobrador, que cuida das pontas soltas pro chefe focar no estratégico.

**Felipe é Felipe** — NÃO chamar de Frank (regra explícita 10/04/2026). O apelido é só meu.

## O que Stamper faz pela PD

- **Plano do dia** (`/abrir-dia`) — puxa Linear + Daily Note Obsidian + Google Calendar, monta blocos com entregável por issue
- **Fechamento do dia** (`/fechar-dia`) — scorecard de entregas, pendentes, energia, prioridade de amanhã
- **Fechamento da semana** (`/fechar-semana`) — relatório com nota + aprendizados + avaliação por frente
- **Captura de tarefas** — quando Felipe menciona algo a fazer, registra no Linear (profissional) ou Daily Note Obsidian (pessoal) sem precisar pedir 2x
- **Acompanhamento Luiz** (`/daily-luiz`, `/ver-dia-luiz`, `/fechar-semana-luiz`)
- **Reuniões** (`/ata-reuniao`, `/transcrever-reuniao`, `/busca-reunioes`) — ciclo completo: transcrição → ata → tarefas Linear
- **WhatsApp** (`/mandar-whatsapp`) — envia do número pessoal Felipe via Stevo, **com confirmação textual explícita**
- **Status e cobrança** (`/status`, `/chefe-de-staff`, `/issue-semana`)
- **Linear** (`/linear-criar-issue`, `/linear-gestao-atividades`)
- **Logs** (`/log-sessao`, `/ja-fiz`) — registra/consulta sessões no `Rotina/sessions-log/`
- **Entry points pra squads** (`/abrir-squad`, `/fechar-squad`) — novas, criadas na Fase 1

## Onde Stamper vive

```
pd-framework/stamper/
├── CLAUDE.md                      ← persona Doug Stamper completa
├── README.md                      ← sumário humano
├── index.html                     ← visualização gerada por render-html.py
├── memory/                        ← 56 entries auto-memory Felipe (snapshot versionado)
│   ├── MEMORY.md                  ← índice carregado em todo contexto
│   ├── user_*.md (12)             ← perfil, apelido, ritmo, pessoas-chave
│   ├── feedback_*.md (14)         ← regras aprendidas
│   ├── project_*.md (12)          ← decisões em curso
│   ├── reference_*.md (3)         ← pointers stack/infra/Stevo
│   ├── session_*.md (~15)         ← resumos sessões marcantes
│   └── README.md                  ← arquitetura sync (manual hoje)
├── context/
│   ├── perfil-felipe.md           ← perfil detalhado (síntese retratos 09/04)
│   ├── stack-ativa.md             ← projetos + pessoas + ferramentas ativos
│   ├── regras-globais.md          ← resumo CLAUDE.md global
│   └── posicionamento-pd.md       ← marca + ICP + voz/tom pro agente
└── skills/                        ← 17 skills dia-a-dia + 2 entry points
    ├── abrir-dia/, fechar-dia/, fechar-semana/
    ├── log-sessao/, ja-fiz/
    ├── status/, chefe-de-staff/, issue-semana/
    ├── mandar-whatsapp/
    ├── ata-reuniao/, transcrever-reuniao/, busca-reunioes/
    ├── daily-luiz/, ver-dia-luiz/, fechar-semana-luiz/
    ├── linear-criar-issue/, linear-gestao-atividades/
    └── abrir-squad/, fechar-squad/    ← novas Fase 1.5
```

## Capabilities absorvidas do AIOX

Stamper absorveu 3 capabilities do `aiox-master` (orchestrator de referência do AIOX Core):

1. **IDS Registry** — mantém catálogo de personas + IDs únicos do framework, evita duplicação
2. **`*validate-agents`** — verificação periódica de saúde dos squads (futura skill `/check-framework`)
3. **Orchestration explicit** — recebe instrução formal sobre quem delega pra quem, baseado em `delegate_to` declarado em cada `squads/<area>/CLAUDE.md`

Por isso o agente `aiox-master` foi descartado: Stamper já é orquestrador central.

## Princípios operacionais (do `stamper/CLAUDE.md`)

- **Operador que decide e executa**, não "assistente que pergunta tudo"
- **Cobra colheita** — interrompe ciclo TDAH "abre nova frente antes de fechar atual"
- **Sem elogios** (exceto se Felipe pedir avaliação)
- **Brutalmente honesto** — jamais inventar, sempre citar fontes
- **Linguagem direta** — máximo 3 parágrafos por resposta
- **Captura sem pedir 2x** — tarefa mencionada → Linear ou Daily
- **Knowledge lookup obrigatório** antes de operação sensível (`python _core/lookup.py "<keywords>"`)
- **Linear Done imediato** — status atualizado na hora, não esperar Felipe pedir
- **Anti-burnout** — nada após 17:30, blocos máximos 90min, pausas obrigatórias

## Memory pessoal vs squad

Felipe é uma pessoa só, então memória pessoal nunca duplica:
- **`stamper/memory/`** — pessoal Felipe (perfil, feedback, decisões, preferências)
- **`squads/<x>/memory/STATE.md`** — operacional do squad (status, decisões de área, bloqueios)

Quando Felipe trabalha dentro de squad (`squads/comercial/`), memória pessoal continua centralizada no Stamper. Squad só carrega seu STATE.md operacional.

## Personas BR adjacentes (Fase 2-3, NÃO são Stamper)

Stamper é o orchestrator. Personas operacionais que vão existir em squads:

| Persona BR | Squad | Origem |
|---|---|---|
| Vitor | Dev (arquitetura) | BMAD Architect |
| Amélia | Dev (implementação) | BMAD Dev |
| Paloma | Dev (PO) | AIOX po |
| Sofia | Dev (UX) | BMAD Sally |
| Camila | Dev (QA) | BMAD Quinn |
| Paula | Dev (Tech Writer) | BMAD Paige |
| João | (transversal — segunda opinião) | BMAD PM |
| Bruno | Dev (quick) | BMAD Barry |
| Maria | Marketing+Produto (discovery) | BMAD Mary |
| Diego | Infra (DevOps) | AIOX devops |

Demais squads (Comercial, CS, Operacional, Financeiro, Estudo) **não** usam persona nomeada — agente genérico com escopo definido no `CLAUDE.md` do squad.

Detalhes: [[../IA-Tecnologia/2026-05-25 PD Framework — Arquitetura DEFINITIVA consolidada]] + `pd-framework/_core/PERSONAS.md`.

## Como começar a usar Stamper (próxima sessão Felipe)

1. Abrir Claude Code com cwd:
   ```
   C:\Users\felip\OneDrive\Documentos\ClaudeCode\Hub Projetos\pd-framework\stamper
   ```
2. Claude carrega automaticamente `stamper/CLAUDE.md` + `MEMORY.md` (cascata Claude Code)
3. Testar `/abrir-dia` ou `/fechar-dia` ou qualquer skill familiar
4. Reportar pra mim se algo quebrou (paths internos das skills podem precisar adaptação — algumas referenciam `Rotina/` que continua vivo como fallback)

## O que NÃO mudou

- `Rotina/sessions-log/` continua sendo destino do `/log-sessao` (auditoria humana fora do framework)
- `~/.claude/skills/` e `Rotina/.claude/skills/` continuam funcionando — Stamper é cópia versionada, não substitui
- Skills globais (Spec-Kit, Matt Pocock, BMAD) seguem em `~/.claude/skills/` — não migram pro Stamper

## O que vem por aí

- **PDL-247** — Skill `/check <topico>` agregando lookup em incidents + sessions + memory + gotchas (45min, desbloqueada agora)
- **PDL-221 Fase 2** — Squads operacionais (Infra, Comercial, CS, Marketing, Operacional, Financeiro)
- **PDL-222 Fase 3** — Squad Produto (Cadência 4 níveis + PD Portal + NSkin + GCI-GO + Consultorias)
- **PDL-248** — Gotchas auto-detect por squad

## Refs

- [[../IA-Tecnologia/2026-05-25 PD Framework — Arquitetura DEFINITIVA consolidada]]
- [[../IA-Tecnologia/2026-05-24 PD Framework — Mapa final e decisões consolidadas]]
- `pd-framework/stamper/CLAUDE.md` (persona completa, 11KB)
- `pd-framework/_core/PERSONAS.md` (10 BR + capabilities Stamper)
- `pd-framework/_core/CONSTITUTION.md` (5 princípios append-only)
- `pd-framework/_core/DEV-WORKFLOW.md` (padrão dev proprietário)
- Commits Fase 1: `f7b3db6`, `86f27d0`, `464f33e`, `215828d` no `felipeluissalgueiro/pd-framework`
