---
title: Padrão — Pasta de Cliente Consultoria
tags: [cs, canon]
---

# Padrão — Pasta de Cliente Consultoria

> Estrutura padrão para squads de clientes em `times/produto/consultorias/<slug-cliente>/`.
> Criado em 2026-05-27. Validado com Padaria Milionária (primeiro cliente).
> Atualizado em 2026-06-26 (DEV-879): toda pasta nova nasce com a **camada de Comunicação & Acompanhamento** do épico DEV-868 já no CLAUDE.md (seção Comunicação + plano de comunicação + bloco de config de automação).
> **Atualizado em 2026-07-01 (DEV-1043): `reunioes/`, `materiais/` e `planilhas/` saem do framework git e passam a viver só no OneDrive** (`OneDrive\Documentos\Customer Success\<Consultorias|Treinamentos>\<Cliente>\`) — motivo e detalhe completo em `_core/CLIENT-FILES-POLICY.md`. O `CLAUDE.md` do cliente linka o path (seção Links); não copia conteúdo.

---

## Estrutura de pastas

```
times/produto/consultorias/<slug-cliente>/     ← SÓ controle interno do agente (git)
├── CLAUDE.md                    ← perfil + contatos + links Linear, CRM Cadencia e pasta OneDrive
├── memory/
│   └── STATE.md                 ← L1 (status geral) + L2 (em progresso) + L3 (decisões)
├── foundation/
│   └── README.md                ← contexto do negócio + contatos + dores + solução
└── workers/                     ← automações específicas deste cliente (quando tiver)

OneDrive\Documentos\Customer Success\Consultorias\<Nome do Cliente>\   ← materiais físicos (fora do git)
├── Materiais\
│   ├── Recebidos\               ← materiais enviados pelo cliente para a Cadencia
│   └── Entregues\               ← materiais entregues pela Cadencia ao cliente
└── Planilhas\                   ← planilhas e relatórios do projeto
```

> Atas/transcrições de reunião: **fonte única = Obsidian vault Empresa `Reuniões/Clientes/`** (CSE-90, decisão 2026-07-05) — o OneDrive recebe só o PDF ENTREGUE em `Materiais\Entregues\`.

---

## Informações obrigatórias para criar um cliente novo

| # | Campo | Descrição |
|---|---|---|
| 1 | Slug da pasta | nome-kebab-case (ex: `padaria-milionaria`) |
| 2 | Nome completo | razão social ou nome do projeto |
| 3 | Contatos | nome, papel, WhatsApp, email — e quem é o decisor |
| 4 | Projeto Linear | ID ou URL do projeto vinculado |
| 5 | Contato CRM Cadencia | nome + ID do `contact` ou pipeline `ciclo-vida` no CRM Cadencia |
| 6 | Fase Playbook | 0–11 (ver `times/cs/foundation/playbook-implementacao-11-fases.md`) |
| 7 | Nicho/segmento | ex: padaria, clínica odontológica, infoprodutor |
| 8 | Serviços contratados | lista do escopo fechado |
| 9 | Investimento | valor + forma de pagamento |
| 10 | Data de início | data de kick-off ou assinatura |
| 11 | Próxima reunião | recorrência ou data da próxima |

---

## Convenções INLINE que os WORKERS leem (OBRIGATÓRIAS — CSE-103)

> **Por que existe esta seção:** na ativação da Ariane Farrapo (03-04/07/2026) o A.1 do
> `/ativar-cliente` gravou essas chaves em frontmatter YAML e **3 workers ficaram cegos**
> pro cliente até auditoria manual. Os workers leem **regex no CORPO do CLAUDE.md**
> (convenção inline `**chave:** valor`), não YAML. Todo CLAUDE.md de cliente novo DEVE
> conter as linhas abaixo (lacuna → `_a definir_`, mas a LINHA existe):

| Linha inline (exata) | Quem lê | O que quebra sem ela |
|---|---|---|
| `**contact_id:** \`<uuid>\`` | `contrato_fases._contact_id_do_cliente` (DEV-959) + `envio_pos_briefing` | fallback Asaas do T-0 cego; markers CRM não gravam |
| `**recarga_creditos_mensal:** <N>` | worker `recarga-creditos-mensal` (regex `\*\*recarga_creditos_mensal:\*\*\s*(\d+)`) | recarga do ciclo NÃO roda — cliente sem créditos |
| `- JID: \`<jid>\` · comercial` (seção Comunicação) | `grupo_resolver.resolver_jid_grupo` | entrega no grupo (CSE-98) e checagens C.4 falham |
| `**E-mail:** <email>` e `**WhatsApp:** <tel>` (do decisor) | `envio_pos_briefing._dados_do_claude_md` | entrega dual-canal sem destino |
| `produto: <Produto>` (frontmatter) | `produto_inclui_cadencia` (senão cai em heurística com WARNING) | gates de tenant imprecisos |
| `**link_pasta_cliente:** <url>` | `consolidador._gerar_manual` (Doc B) | Manual sai com placeholder no lugar do link de upload (CSE-91 — decisão 05/07: link criado 1x manual no OneDrive, SEM Graph API) |

**E no frontmatter do CONTRATO** (`times/juridico/contratos-emitidos/<slug>/*.md`, não no CLAUDE.md):
`t0: YYYY-MM-DD` (lido por `contrato_fases._t0_do_contrato` — Bloco F inteiro) e `creditos: <N>`
(provisionamento do tenant). O `status:`/`signed_at:` são promovidos pelo sync Autentique (CSE-96).

**Stakeholder de cliente PF (sem empresa — CSE-102):** o vínculo vive na TIMELINE do contato
principal, como activity `stakeholder.link` com note `<contact_id> | <papel> | <nome>`.
Criar via `stakeholders.vincular_stakeholder(slug, contact_id, papel, nome, dry_run=False)`;
`stakeholders_do_cliente(slug)` resolve automaticamente (empresa primeiro, timeline como fallback).

---

## Seções canônicas do `CLAUDE.md` do cliente

O `CLAUDE.md` de **todo cliente novo** (DEV-879) deve conter, além de perfil/produto/comercial:

1. **Links** — Grupo WhatsApp (nome + JID + conta) · Form Stakeholders (Tally) · Projeto Linear (id + url) · Issues por fase · Contrato · Contato/Tenant CRM Cadencia · **Pasta compartilhada (OneDrive)** — path completo, ver `_core/CLIENT-FILES-POLICY.md`.
2. **Comunicação** — canal oficial = grupo WhatsApp (JID + regra de só usar o grupo) + comando de envio.
3. **Plano de comunicação** — etapas com template DEV-872 aplicável, cadência de check-in 3/3, digest diário, milestones.
4. **Config de automação** — bloco por cliente (CC de email, frequência de check-in, flags on/off por automação).

Referências da camada: épico **DEV-868** (`times/cs/context/prd-comunicacao-acompanhamento-cliente.md`), templates **DEV-872** (`times/cs/foundation/templates-email/` + `templates-whatsapp/`), sistema de comunicação (`times/cs/foundation/sistema-comunicacao-cliente.md`), **milestones** do projeto Linear vinculado.

### Template de bloco reutilizável (a skill `/registrar-cliente` injeta isto)

> Copiar e substituir os `<placeholders>`. Não inventar JID/dados — lacuna vira `_a definir no briefing_` ou `(?)`.
> Modelo real de referência: `times/produto/consultorias/op-odontopenha/CLAUDE.md`.

```markdown
## Comunicação

**Canal oficial: Grupo WhatsApp `<nome-do-grupo>`**
- JID: `<JID>` · `<conta: comercial|pessoal>`
- Toda comunicação com o cliente (updates, pendências, entregas, dúvidas) vai por esse grupo
- Para enviar: `python3 _shared/evo_client.py --comercial "<JID>" "<msg>"`
- Não usar WhatsApp pessoal nem email como canal principal com esse cliente

### Plano de comunicação (DEV-868)

- **Milestones:** acompanhamento pelos milestones do projeto Linear `<project_id>` — cada virada de fase gera comunicação registrada.
- **Etapas ↔ templates (DEV-872):** disparar o template de e-mail/WhatsApp da etapa concluída (nunca texto improvisado):
  | Etapa | Template (e-mail + WhatsApp) |
  |---|---|
  | Abertura (T-0) | `00-boas-vindas` |
  | Briefing/insumos | `01-briefing-e-insumos` |
  | Pós-kickoff | `02-pos-kickoff` |
  | Go-Live | `05-go-live` |
  | Treinamento | `07-treinamento-agendado` |
  | Reunião realizada | `reuniao-realizada` |
  | Cobrança de pendências | `cobranca-insumos` |
  | Transição | `10-transicao` |
  > Gate `cliente_registry` sempre antes de qualquer disparo. Catálogo completo: `times/cs/foundation/sistema-comunicacao-cliente.md`.
- **Check-in 3/3 dias:** resumo amigável dos commits traduzidos + progresso de milestones, no grupo WhatsApp (DEV-878).
- **Digest diário:** 1 e-mail-resumo/dia com as interações do dia (status no Linear na hora; e-mail consolidado 1x/dia) — DEV-873.

### Config de automação (por cliente)

```yaml
# config de comunicação/acompanhamento — DEV-879
cliente: <slug>
canal_oficial_jid: "<JID>"
canal_oficial_conta: comercial          # comercial | pessoal
email_cc:                                # CC fixo em todo e-mail (DEV-868)
  - <stakeholder-1@cliente>
  - <stakeholder-2@cliente>
  - felipe@cadencia.ia.br
  - felipeluissalgueiro@gmail.com
checkin_frequencia_dias: 3               # cadência do check-in (default 3/3)
milestones_source: linear:<project_id>   # de onde vêm os milestones
automacoes:
  digest_diario: on                      # 1 e-mail-resumo/dia
  checkin_3_3: on                        # resumo de commits + milestones a cada 3 dias
  logger_interacoes: on                  # registra toda interação automaticamente
  agente_whatsapp: off                   # responde factual / escala sensível (DEV-876)
```
```

> O bloco `yaml` acima fica **dentro** do `CLAUDE.md` do cliente (documental/declarativo). Os workers da camada DEV-868 leem essas flags para decidir o que automatizar por cliente; até os workers existirem, serve de contrato de configuração.

---

## Variante — MVP / Sistema Personalizado (DEV-1037)

Cliente que contratou **sistema/MVP sob medida** (código novo escrito especificamente pra ele — ex:
MVP tráfego Meta Ads, automação jurídica interna), **não** o playbook padrão Cadencia (sem tenant,
sem CRM+IA prontos). Produto `[3] Projeto customizado` no Passo 0.6 do `/ativar-cliente`. Caso de
referência: **Iasmim Lopes** (MVP Meta Ads, 2026-07-01).

**Diferenças em relação à estrutura padrão:**

- **Repo dedicado** — sempre tem um repo GitHub próprio do cliente (`Posicionamento-Digital/<slug>`)
  com o código do MVP. A pasta `times/produto/consultorias/<slug>/` continua sendo só controle
  interno do agente (git do framework); o **código do sistema vive no repo dedicado**, nunca aqui.
- **Projeto Linear** — template `MVP Personalizado` (não `Cliente — Implementação`), milestones
  **Especificação & Contrato → Desenvolvimento → Homologação com cliente → Entrega & Suporte**
  (`_core/LINEAR-PROJECT-TEMPLATES.md` §4b). Issues técnicas usam o template CAD **Feature/Story**.
- **`CLAUDE.md` do cliente** — seção **Links** ganha entrada extra `Repo do sistema: <url>`. As demais
  seções canônicas (Comunicação, Plano de comunicação, Config de automação) valem igual — o cliente
  ainda passa pelo mesmo ritmo de check-in/digest, só o "produto" entregue é código sob medida em vez
  de tenant Cadencia configurado.
- **Sem tenant Cadencia obrigatório** — `produto_inclui_cadencia(<slug>)` deve resolver `False` pra
  esse tipo (a menos que o MVP rode sobre a infra Cadencia, caso a caso). Não forçar provisionamento
  de tenant só porque o cliente é CS.

## Regras de uso

- **STATE.md** = o que está acontecendo agora (status, pendências, próximas ações)
- **foundation/README.md** = quem é o cliente, o negócio dele, as dores, o que foi vendido
- **Nunca misturar** contexto de cliente com processo CS — processo fica em `times/cs/foundation/`
- **Reuniões:** usar `/transcrever-reuniao` para transcrições + `/ata-reuniao` para atas formais — arquivo final salvo no OneDrive (`Reunioes\Transcricoes\` / `Reunioes\Atas\`), não no git
- **Materiais:** sempre nomear com data `YYYY-MM-DD_<descricao>.<ext>` — salvos direto no OneDrive (`Materiais\Recebidos\` / `Materiais\Entregues\`), nunca no framework git (DEV-1043)

---

## Retrofit de cliente existente (sem executar)

Para um cliente que já tem pasta mas nasceu antes do DEV-879 (ex.: OP Odontopenha já tem Comunicação + Links; falta-lhe Plano + Config):

1. Manter as seções já existentes (não sobrescrever Links/Comunicação).
2. Anexar ao `CLAUDE.md` os blocos `### Plano de comunicação (DEV-868)` e `### Config de automação (por cliente)` do template acima.
3. Preencher `<placeholders>` com os dados reais já presentes na pasta (JID, project_id, stakeholders do contrato). Sem fonte → `_a definir no briefing_`.
4. Idempotente: se já houver Plano/Config, completar lacunas em vez de duplicar.

Não modificar pastas de clientes existentes em massa — retrofit é por cliente, sob demanda.

## Referências

- `times/cs/context/prd-comunicacao-acompanhamento-cliente.md` — PRD da camada Comunicação & Acompanhamento (épico DEV-868)
- `times/cs/foundation/sistema-comunicacao-cliente.md` — catálogo de eventos ↔ templates (DEV-872) + gate
- `times/cs/foundation/templates-email/` + `templates-whatsapp/` — templates por etapa
- `times/cs/foundation/playbook-implementacao-11-fases.md` — playbook que este squad executa
- `times/cs/foundation/rotina-cs.md` — rotina semanal CS (Letícia audita, squad executa)
- `times/cs/foundation/checklist-briefing.md` — checklist de kickoff
- `times/produto/consultorias/op-odontopenha/CLAUDE.md` — modelo real da seção Comunicação + Links
