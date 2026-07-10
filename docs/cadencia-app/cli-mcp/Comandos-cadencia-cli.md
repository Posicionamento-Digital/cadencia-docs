---
date: 2026-06-24
tags: [doc, cadencia-cli, comandos, referencia, seguranca]
moc: "[[MOC-Projetos]]"
projeto: Cadencia-CLI-MCP
fonte: "_repos/cadencia-cli/docs/COMMANDS.md (gerado do codigo via tools/gen_commands_doc.py)"
type: source
entities: ["[[Cadencia]]", "[[comercial]]", "[[marketing]]"]
---
# cadencia-cli — Referência completa de comandos
> **Gerado automaticamente** do registry (`src/cadencia_cli/registry.py` + `actions/`). Fonte de verdade: o código. Para regenerar: `python tools/gen_commands_doc.py`.
> Resumo operacional para agentes: `pd-framework/_core/CADENCIA-CLI.md`. Projeto Linear: **Cadencia — CLI/MCP de Controle** (`7648831d`).

## Modelo de acesso e segurança
**Não há login nem credencial própria do `cadencia-cli`.** A autenticação é herdada do ambiente:

| Recurso | Credencial usada | Como resolve | Alcance |
|---|---|---|---|
| CRM + Conteúdo (leitura/escrita) | **PAT do Supabase** (item 1P `Supabase - ClaudeCode - CLI`) via Management API | `op` (Service Account headless) **ou** env `SUPABASE_ACCESS_TOKEN` | **Admin de TODOS os projetos Supabase do Felipe** — bypassa RLS |
| Disparo de worker (`growth/newsletter-dispatch`) | **Chave SSH** `hostinger_prod_master` | arquivo `~/.ssh/hostinger_prod_master` | Shell na VPS Master de produção |

**Consequência direta:** quem tiver acesso a um shell onde `OP_SERVICE_ACCOUNT_TOKEN`/`SUPABASE_ACCESS_TOKEN`
esteja disponível **acessa o Cadencia inteiro** (todos os tenants — o PAT é admin e ignora RLS), e quem
tiver a chave SSH dispara workers em produção. A barreira de segurança **é o acesso ao ambiente/credencial**,
não a CLI.

- A blindagem por `tenant_id` no código protege contra **erro de programação** (vazar dado de outro tenant por engano), **não** contra quem detém o PAT — esse pode ignorar a CLI e falar direto com o Supabase.
- **Hardening planejado (DEV-582):** token de serviço dedicado e escopado por tenant, substituindo o PAT admin nas mutações. Reduz o "tudo ou nada".
- **Recomendação:** tratar `OP_SERVICE_ACCOUNT_TOKEN` e `hostinger_prod_master` como segredos de produção; só em máquinas do Felipe / agentes confiáveis.

## Setup
```bash
cd "Hub Projetos/_repos/cadencia-cli" && pip install -e .
# Credencial resolve sozinha pelo 1Password (Service Account). Override opcional:
export SUPABASE_ACCESS_TOKEN=$(op item get "Supabase - ClaudeCode - CLI" --vault databases --fields credencial --reveal)
# Tenant default = PD. Outro tenant:
export CADENCIA_TENANT_ID=<uuid>
```

## Legenda de access-type
- 🟢 **READ** — leitura (Supabase select/search). Seguro.
- 🟡 **WRITE** — CRUD sem lógica de negócio (insert/update blindado por tenant).
- 🔴 **MUTATION** — mutação com lógica de negócio (crédito/idempotência). **Bloqueado até DEV-582.**
- 🟠 **DISPATCH** — dispara worker via **SSH** na VPS Master. Sem `--send` = preview.

## `cadences` — Cadências (CRM — setup/templates)

### `cadencia-cli cadences add-step` — 🟡 WRITE
Adiciona um passo a uma cadência.

```bash
cadencia-cli cadences add-step [--cadence ..] [--channel ..] [--order ..] [--day ..] [--name ..] [--subject ..] [--body ..] [--manual ..]
```

_Opções:_
- `--cadence` — Cadência (id ou system_key).
- `--channel` — Canal: email | whatsapp | call | instagram | linkedin | sms.
- `--order` — Ordem do passo. Auto (último+1) se omitido.
- `--day` (default: `0`) — Dia da cadência em que o passo dispara (offset).
- `--name` — Nome do passo (rótulo).
- `--subject` — Template de assunto (email).
- `--body` — Template do corpo da mensagem.
- `--manual` (default: `False`) — Passo manual (is_auto=false). Default é automático.

### `cadencia-cli cadences create` — 🟡 WRITE
Cria uma cadência custom no tenant.

```bash
cadencia-cli cadences create [--name ..] [--key ..] [--category ..] [--duration-days ..] [--active ..]
```

_Opções:_
- `--name` — Nome da cadência (ex.: Onboarding 14D).
- `--key` — system_key (a-z0-9_). Derivado do nome se omitido.
- `--category` — Categoria (ex.: prospeccao, followup, onboarding).
- `--duration-days` — Duração em dias.
- `--active` (default: `False`) — Marca a cadência como ativa.

### `cadencia-cli cadences list` — 🟢 READ
Lista as cadências do tenant.

```bash
cadencia-cli cadences list 
```

### `cadencia-cli cadences steps` — 🟢 READ
Lista os passos de uma cadência.

```bash
cadencia-cli cadences steps [--cadence ..]
```

_Opções:_
- `--cadence` — Cadência (id ou system_key).

## `companies` — Empresas (CRM)

### `cadencia-cli companies contacts` — 🟢 READ
Lista os contatos vinculados a uma empresa.

```bash
cadencia-cli companies contacts <company_id>
```

_Argumentos:_ `company_id` — ID da empresa.

### `cadencia-cli companies create` — 🟡 WRITE
Cria uma empresa no tenant.

```bash
cadencia-cli companies create [--razao-social ..] [--nome-fantasia ..] [--cnpj ..] [--setor ..] [--cidade ..] [--uf ..] [--telefone ..] [--email ..] [--site ..] [--endereco-logradouro ..] [--endereco-numero ..] [--endereco-complemento ..] [--endereco-bairro ..] [--endereco-cep ..]
```

_Opções:_
- `--razao-social` — Razão social.
- `--nome-fantasia` — Nome fantasia.
- `--cnpj` — CNPJ.
- `--setor` — Setor.
- `--cidade` — Cidade.
- `--uf` — UF (2 letras).
- `--telefone` — Telefone comercial.
- `--email` — E-mail comercial.
- `--site` — Site.
- `--endereco-logradouro` — Logradouro.
- `--endereco-numero` — Número.
- `--endereco-complemento` — Complemento.
- `--endereco-bairro` — Bairro.
- `--endereco-cep` — CEP.

### `cadencia-cli companies get` — 🟢 READ
Mostra uma empresa (campos ricos).

```bash
cadencia-cli companies get <company_id>
```

_Argumentos:_ `company_id` — ID da empresa.

### `cadencia-cli companies link-contact` — 🟡 WRITE
Vincula um contato a uma empresa.

```bash
cadencia-cli companies link-contact <company_id> [--contact ..] [--role ..]
```

_Argumentos:_ `company_id` — ID da empresa.

_Opções:_
- `--contact` — ID do contato.
- `--role` — Papel do contato na empresa (ex.: socio, gestor).

### `cadencia-cli companies list` — 🟢 READ
Lista empresas do tenant.

```bash
cadencia-cli companies list [--limit ..] [--setor ..]
```

_Opções:_
- `--limit` (default: `20`) — Máximo de empresas.
- `--setor` — Filtra por setor.

### `cadencia-cli companies search` — 🟢 READ
Busca empresas por razão/fantasia/CNPJ.

```bash
cadencia-cli companies search <term> [--limit ..]
```

_Argumentos:_ `term` — Termo a buscar.

_Opções:_
- `--limit` (default: `20`)

### `cadencia-cli companies update` — 🟡 WRITE
Edita campos de uma empresa.

```bash
cadencia-cli companies update <company_id> [--razao-social ..] [--nome-fantasia ..] [--setor ..] [--cidade ..] [--uf ..] [--telefone ..] [--email ..] [--site ..] [--endereco-logradouro ..] [--endereco-numero ..] [--endereco-complemento ..] [--endereco-bairro ..] [--endereco-cep ..]
```

_Argumentos:_ `company_id` — ID da empresa.

_Opções:_
- `--razao-social` — Razão social.
- `--nome-fantasia` — Nome fantasia.
- `--setor` — Setor.
- `--cidade` — Cidade.
- `--uf` — UF (2 letras).
- `--telefone` — Telefone comercial.
- `--email` — E-mail comercial.
- `--site` — Site.
- `--endereco-logradouro` — Logradouro.
- `--endereco-numero` — Número.
- `--endereco-complemento` — Complemento.
- `--endereco-bairro` — Bairro.
- `--endereco-cep` — CEP.

## `contacts` — Contatos (CRM)

### `cadencia-cli contacts activities` — 🟢 READ
Lista a timeline de atividades de um contato.

```bash
cadencia-cli contacts activities <contact_id> [--type ..] [--limit ..]
```

_Argumentos:_ `contact_id` — ID do contato.

_Opções:_
- `--type` — Filtra por tipo (ex.: call.made).
- `--limit` (default: `50`) — Máximo de atividades.

### `cadencia-cli contacts activity` — 🟡 WRITE
Registra uma atividade/touchpoint no contato.

```bash
cadencia-cli contacts activity <contact_id> [--type ..] [--note ..] [--direction ..] [--duration ..] [--scheduled-at ..]
```

_Argumentos:_ `contact_id` — ID do contato.

_Opções:_
- `--type` — Tipo (ex.: call.made, email.sent, whatsapp.sent).
- `--note` — Detalhe opcional (vai no payload).
- `--direction` — Sentido do contato (inbound/outbound).
- `--duration` — Duração em minutos (calls).
- `--scheduled-at` — Quando estava agendado (ISO8601).

### `cadencia-cli contacts add-email` — 🟡 WRITE
Anexa um e-mail adicional ao contato (sem trocar o principal).

```bash
cadencia-cli contacts add-email <contact_id> <email>
```

_Argumentos:_ `contact_id` — ID do contato., `email` — E-mail adicional.

### `cadencia-cli contacts add-phone` — 🟡 WRITE
Anexa um telefone adicional ao contato (sem trocar o principal).

```bash
cadencia-cli contacts add-phone <contact_id> <phone>
```

_Argumentos:_ `contact_id` — ID do contato., `phone` — Telefone adicional.

### `cadencia-cli contacts create` — 🟡 WRITE
Cria um contato no tenant.

```bash
cadencia-cli contacts create [--first-name ..] [--last-name ..] [--email ..] [--phone ..] [--status ..] [--lead-source ..] [--temperatura ..] [--is-icp ..] [--lifecycle ..] [--score ..] [--cpf ..] [--registro-profissional ..] [--endereco-logradouro ..] [--endereco-numero ..] [--endereco-complemento ..] [--endereco-bairro ..] [--endereco-cidade ..] [--endereco-uf ..] [--endereco-cep ..]
```

_Opções:_
- `--first-name` — Primeiro nome.
- `--last-name` — Sobrenome.
- `--email` — E-mail.
- `--phone` — Telefone/WhatsApp.
- `--status` — Status.
- `--lead-source` — Origem (evento/indicacao/inbound/linkedin/outbound).
- `--temperatura` — Temperatura (frio/morno/quente/hot).
- `--is-icp` — Marca como ICP (true/false).
- `--lifecycle` — Lifecycle (lead/cliente/ex_cliente; aceita customer→cliente, churned→ex_cliente).
- `--score` — Score 0–100.
- `--cpf` — CPF (com ou sem formatação).
- `--registro-profissional` — Conselho + número (ex: 'CRO RJ 29991').
- `--endereco-logradouro` — Logradouro (rua/avenida).
- `--endereco-numero` — Número.
- `--endereco-complemento` — Complemento.
- `--endereco-bairro` — Bairro.
- `--endereco-cidade` — Cidade.
- `--endereco-uf` — UF (2 letras).
- `--endereco-cep` — CEP.

### `cadencia-cli contacts emails` — 🟢 READ
Lista todos os e-mails do contato (principal + adicionais).

```bash
cadencia-cli contacts emails <contact_id>
```

_Argumentos:_ `contact_id` — ID do contato.

### `cadencia-cli contacts enrich` — 🔴 MUTATION
[BLOQUEADO até DEV-582] Enriquece um contato (debita crédito).

```bash
cadencia-cli contacts enrich <contact_id>
```

_Argumentos:_ `contact_id` — ID do contato.

### `cadencia-cli contacts find` — 🟢 READ
Resolve contato por nome/e-mail/telefone (inclui adicionais).

```bash
cadencia-cli contacts find [--name ..] [--email ..] [--phone ..] [--limit ..]
```

_Opções:_
- `--name` — Parte do nome (ILIKE).
- `--email` — E-mail (principal ou adicional).
- `--phone` — Telefone (principal ou adicional; compara dígitos).
- `--limit` (default: `10`) — Máximo de resultados.

### `cadencia-cli contacts get` — 🟢 READ
Mostra um contato (campos ricos).

```bash
cadencia-cli contacts get <contact_id>
```

_Argumentos:_ `contact_id` — ID do contato.

### `cadencia-cli contacts import` — 🟡 WRITE
Importa contatos em lote de um CSV (dedupe por email/telefone).

```bash
cadencia-cli contacts import [--file ..] [--delimiter ..] [--map ..] [--lead-source ..] [--dry-run ..]
```

_Opções:_
- `--file` — Caminho do CSV (cabeçalho na 1ª linha).
- `--delimiter` (default: `,`) — Delimitador do CSV (use ';' p/ planilhas BR).
- `--map` — Mapeamento extra 'csvcol=campo;...' (sobrepõe aliases).
- `--lead-source` — lead_source default p/ todas as linhas sem valor.
- `--dry-run` (default: `False`) — Não grava; só reporta o que faria.

### `cadencia-cli contacts link-company` — 🟡 WRITE
Vincula um contato a uma empresa.

```bash
cadencia-cli contacts link-company <contact_id> [--company ..] [--role ..]
```

_Argumentos:_ `contact_id` — ID do contato.

_Opções:_
- `--company` — ID da empresa.
- `--role` — Papel do contato na empresa (ex.: socio, gestor).

### `cadencia-cli contacts list` — 🟢 READ
Lista contatos do tenant.

```bash
cadencia-cli contacts list [--limit ..] [--status ..] [--is-icp ..] [--temperatura ..] [--lead-source ..] [--lifecycle ..] [--pipeline ..] [--stage ..] [--tag ..]
```

_Opções:_
- `--limit` (default: `20`) — Máximo de contatos.
- `--status` — Filtra por status.
- `--is-icp` — Filtra por is_icp.
- `--temperatura` — Filtra por temperatura (frio/morno/quente/hot).
- `--lead-source` — Filtra por origem do lead.
- `--lifecycle` — Filtra por lifecycle (lead/cliente/ex_cliente; aceita aliases EN).
- `--pipeline` — Lista contatos com oportunidade neste pipeline (slug ou id).
- `--stage` — Lista contatos com oportunidade neste stage (slug ou id).
- `--tag` — Lista contatos com esta tag (label ou id).

### `cadencia-cli contacts note` — 🟡 WRITE
Cria uma nota num contato.

```bash
cadencia-cli contacts note <contact_id> [--body ..]
```

_Argumentos:_ `contact_id` — ID do contato.

_Opções:_
- `--body` — Texto da nota.

### `cadencia-cli contacts notes` — 🟢 READ
Lista as notas de um contato.

```bash
cadencia-cli contacts notes <contact_id>
```

_Argumentos:_ `contact_id` — ID do contato.

### `cadencia-cli contacts phones` — 🟢 READ
Lista todos os telefones do contato (principal + adicionais).

```bash
cadencia-cli contacts phones <contact_id>
```

_Argumentos:_ `contact_id` — ID do contato.

### `cadencia-cli contacts remove-email` — 🟡 WRITE
Remove um e-mail adicional do contato (não toca no principal).

```bash
cadencia-cli contacts remove-email <contact_id> <email>
```

_Argumentos:_ `contact_id` — ID do contato., `email` — E-mail adicional a remover.

### `cadencia-cli contacts remove-phone` — 🟡 WRITE
Remove um telefone adicional do contato (não toca no principal).

```bash
cadencia-cli contacts remove-phone <contact_id> <phone>
```

_Argumentos:_ `contact_id` — ID do contato., `phone` — Telefone adicional a remover.

### `cadencia-cli contacts search` — 🟢 READ
Busca contatos por nome/e-mail/telefone.

```bash
cadencia-cli contacts search <term> [--limit ..]
```

_Argumentos:_ `term` — Termo a buscar.

_Opções:_
- `--limit` (default: `20`)

### `cadencia-cli contacts tag add` — 🟡 WRITE
Adiciona uma tag a um contato (label ou id).

```bash
cadencia-cli contacts tag add <contact_id> [--tag ..]
```

_Argumentos:_ `contact_id` — ID do contato.

_Opções:_
- `--tag` — Tag por label ou id.

### `cadencia-cli contacts tag list` — 🟢 READ
Lista as tags de um contato.

```bash
cadencia-cli contacts tag list <contact_id>
```

_Argumentos:_ `contact_id` — ID do contato.

### `cadencia-cli contacts tag remove` — 🟡 WRITE
Remove uma tag de um contato (label ou id).

```bash
cadencia-cli contacts tag remove <contact_id> [--tag ..]
```

_Argumentos:_ `contact_id` — ID do contato.

_Opções:_
- `--tag` — Tag por label ou id.

### `cadencia-cli contacts update` — 🟡 WRITE
Edita campos de um contato.

```bash
cadencia-cli contacts update <contact_id> [--first-name ..] [--last-name ..] [--email ..] [--phone ..] [--status ..] [--lead-source ..] [--temperatura ..] [--is-icp ..] [--lifecycle ..] [--score ..] [--cpf ..] [--registro-profissional ..] [--endereco-logradouro ..] [--endereco-numero ..] [--endereco-complemento ..] [--endereco-bairro ..] [--endereco-cidade ..] [--endereco-uf ..] [--endereco-cep ..]
```

_Argumentos:_ `contact_id` — ID do contato.

_Opções:_
- `--first-name` — Primeiro nome.
- `--last-name` — Sobrenome.
- `--email` — E-mail.
- `--phone` — Telefone/WhatsApp.
- `--status` — Status.
- `--lead-source` — Origem (evento/indicacao/inbound/linkedin/outbound).
- `--temperatura` — Temperatura (frio/morno/quente/hot).
- `--is-icp` — Marca como ICP (true/false).
- `--lifecycle` — Lifecycle (lead/cliente/ex_cliente; aceita customer→cliente, churned→ex_cliente).
- `--score` — Score 0–100.
- `--cpf` — CPF (com ou sem formatação).
- `--registro-profissional` — Conselho + número (ex: 'CRO RJ 29991').
- `--endereco-logradouro` — Logradouro (rua/avenida).
- `--endereco-numero` — Número.
- `--endereco-complemento` — Complemento.
- `--endereco-bairro` — Bairro.
- `--endereco-cidade` — Cidade.
- `--endereco-uf` — UF (2 letras).
- `--endereco-cep` — CEP.

## `content` — Conteúdo / Marketing

### `cadencia-cli content calendar-add` — 🟡 WRITE
Agenda um post num canal (seta *_scheduled_at).

```bash
cadencia-cli content calendar-add <post_id> [--date ..] [--canal ..]
```

_Argumentos:_ `post_id` — ID do post.

_Opções:_
- `--date` — Data/hora ISO8601 (ex.: 2026-06-30T11:00:00).
- `--canal` — blog/linkedin/seinfeld/instagram.

### `cadencia-cli content calendar-gap` — 🟢 READ
Mostra dias sem conteúdo na janela (buraco editorial).

```bash
cadencia-cli content calendar-gap [--week/--no-week ..] [--from ..] [--to ..]
```

_Opções:_
- `--week/--no-week` (default: `True`) — Janela = hoje..+7 dias (default).
- `--from` — Início ISO.
- `--to` — Fim ISO.

### `cadencia-cli content calendar-list` — 🟢 READ
Grade editorial: conteúdo agendado/publicado na janela.

```bash
cadencia-cli content calendar-list [--week/--no-week ..] [--from ..] [--to ..]
```

_Opções:_
- `--week/--no-week` (default: `True`) — Janela = hoje..+7 dias (default).
- `--from` — Início ISO (sobrepõe --week).
- `--to` — Fim ISO.

### `cadencia-cli content carousel-dispatch` — 🔴 MUTATION
[BLOQUEADO até DEV-582] Dispara carrossel/reels.

```bash
cadencia-cli content carousel-dispatch [--content-idea-id ..]
```

_Opções:_
- `--content-idea-id` — ID da ideia (usado quando desbloqueado).

### `cadencia-cli content cover-set` — 🟡 WRITE
Define a capa de um post (capa_url + featured_image_url).

```bash
cadencia-cli content cover-set <post_id> [--image ..] [--alt ..]
```

_Argumentos:_ `post_id` — ID do post.

_Opções:_
- `--image` — URL da imagem de capa.
- `--alt` — Texto alternativo (cover_alt).

### `cadencia-cli content derive` — 🟡 WRITE
Cria uma ideia derivada de um post existente.

```bash
cadencia-cli content derive [--from-post ..] [--to ..]
```

_Opções:_
- `--from-post` — ID do post de origem.
- `--to` — Formato derivado (carrossel/reels/thread/linkedin).

### `cadencia-cli content documents-create` — 🟡 WRITE
Cria um documento de conteúdo.

```bash
cadencia-cli content documents-create [--idea-id ..] [--caption ..] [--carousel-model ..] [--status ..]
```

_Opções:_
- `--idea-id` — ID da ideia de origem (obrigatório).
- `--caption` — Legenda do documento.
- `--carousel-model` — Modelo de carrossel.
- `--status` (default: `draft`) — Status do documento (default draft).

### `cadencia-cli content documents-delete` — 🟡 WRITE
Remove um documento de conteúdo de vez (DESTRUTIVO — exige --yes).

```bash
cadencia-cli content documents-delete <document_id> [--yes ..]
```

_Argumentos:_ `document_id` — ID do documento.

_Opções:_
- `--yes` (default: `False`) — Confirma a remoção definitiva (obrigatório — destrutivo).

### `cadencia-cli content documents-get` — 🟢 READ
Mostra um documento de conteúdo.

```bash
cadencia-cli content documents-get <document_id>
```

_Argumentos:_ `document_id` — ID do documento.

### `cadencia-cli content documents-list` — 🟢 READ
Lista documentos de conteúdo.

```bash
cadencia-cli content documents-list [--limit ..] [--status ..] [--idea-id ..]
```

_Opções:_
- `--limit` (default: `20`)
- `--status` — Filtra por status.
- `--idea-id` — Filtra por ideia.

### `cadencia-cli content documents-publish` — 🟡 WRITE
Marca o publish_status de um documento.

```bash
cadencia-cli content documents-publish <document_id> [--status ..]
```

_Argumentos:_ `document_id` — ID do documento.

_Opções:_
- `--status` (default: `published`) — publish_status (default published).

### `cadencia-cli content documents-update` — 🟡 WRITE
Edita um documento de conteúdo.

```bash
cadencia-cli content documents-update <document_id> [--caption ..] [--hashtags ..] [--status ..]
```

_Argumentos:_ `document_id` — ID do documento.

_Opções:_
- `--caption` — Legenda.
- `--hashtags` — Hashtags (texto).
- `--status` — Status.

### `cadencia-cli content growth-dispatch` — 🟠 DISPATCH
Dispara geração no worker growth (via SSH na VPS).

```bash
cadencia-cli content growth-dispatch [--channel ..] [--content-idea-id ..] [--dry-run ..] [--send ..]
```

_Opções:_
- `--channel` — Canal (blog/seinfeld/linkedin/instagram).
- `--content-idea-id` — ID da ideia (só blog).
- `--dry-run` (default: `False`) — Roda o script em modo dry-run (só blog; não publica).
- `--send` (default: `False`) — Dispara de verdade (gera conteúdo + custo).

### `cadencia-cli content ideas-create` — 🟡 WRITE
Cria uma ideia de conteúdo.

```bash
cadencia-cli content ideas-create [--title ..] [--description ..] [--editorial-id ..] [--keywords ..]
```

_Opções:_
- `--title` — Título da ideia.
- `--description` — Descrição.
- `--editorial-id` — Editorial.
- `--keywords` — Palavras-chave separadas por vírgula.

### `cadencia-cli content ideas-delete` — 🟡 WRITE
Remove uma ideia de conteúdo.

```bash
cadencia-cli content ideas-delete <idea_id>
```

_Argumentos:_ `idea_id` — ID da ideia.

### `cadencia-cli content ideas-get` — 🟢 READ
Mostra uma ideia de conteúdo.

```bash
cadencia-cli content ideas-get <idea_id>
```

_Argumentos:_ `idea_id` — ID da ideia.

### `cadencia-cli content ideas-list` — 🟢 READ
Lista ideias de conteúdo do tenant.

```bash
cadencia-cli content ideas-list [--limit ..] [--status ..] [--editorial-id ..]
```

_Opções:_
- `--limit` (default: `20`) — Máximo de ideias.
- `--status` — Filtra por status.
- `--editorial-id` — Filtra por editorial.

### `cadencia-cli content ideas-status` — 🟡 WRITE
Muda o status de uma ideia.

```bash
cadencia-cli content ideas-status <idea_id> [--status ..]
```

_Argumentos:_ `idea_id` — ID da ideia.

_Opções:_
- `--status` — Novo status (draft/pending/used/rejected).

### `cadencia-cli content ideas-update` — 🟡 WRITE
Edita uma ideia de conteúdo.

```bash
cadencia-cli content ideas-update <idea_id> [--title ..] [--description ..] [--editorial-id ..] [--keywords ..]
```

_Argumentos:_ `idea_id` — ID da ideia.

_Opções:_
- `--title` — Título.
- `--description` — Descrição.
- `--editorial-id` — Editorial.
- `--keywords` — Palavras-chave separadas por vírgula (substitui).

### `cadencia-cli content image-upload` — 🟡 WRITE
Sobe uma imagem ao Storage do tenant e retorna a URL pública.

```bash
cadencia-cli content image-upload <arquivo> [--alt ..] [--bucket ..]
```

_Argumentos:_ `arquivo` — Caminho do arquivo de imagem local (png/jpg/jpeg/webp/gif/svg).

_Opções:_
- `--alt` — Texto alternativo (sugere o cover-set pronto na saída).
- `--bucket` (default: `content`) — Bucket de Storage (default: content, público).

### `cadencia-cli content newsletter-dispatch` — 🟠 DISPATCH
Dispara a newsletter (worker growth, via SSH).

```bash
cadencia-cli content newsletter-dispatch [--send ..]
```

_Opções:_
- `--send` (default: `False`) — Dispara de verdade.

### `cadencia-cli content publish` — 🟡 WRITE
Ideia → enfileira → dispara, num passo (blog).

```bash
cadencia-cli content publish [--title ..] [--channel ..] [--keywords ..] [--description ..] [--send ..]
```

_Opções:_
- `--title` — Título da ideia/post.
- `--channel` (default: `blog`) — Canal (blog suporta idea-id).
- `--keywords` — Palavras-chave separadas por vírgula.
- `--description` — Descrição da ideia.
- `--send` (default: `False`) — Dispara o worker de verdade (gera + publica).

### `cadencia-cli content published-create` — 🟡 WRITE
Cria um post de blog com texto próprio (bypass worker).

```bash
cadencia-cli content published-create [--title ..] [--html-content ..] [--slug ..] [--keyword ..] [--meta-description ..] [--capa-url ..] [--status ..]
```

_Opções:_
- `--title` — Título do post (obrigatório).
- `--html-content` — HTML/markdown do corpo.
- `--slug` — Slug do post.
- `--keyword` — Palavra-chave SEO.
- `--meta-description` — Meta description SEO.
- `--capa-url` — URL da capa.
- `--status` (default: `archived`) — Status (published/archived; default archived = fora do ar).

### `cadencia-cli content published-delete` — 🟡 WRITE
Remove um post publicado de vez (DESTRUTIVO — exige --yes).

```bash
cadencia-cli content published-delete <post_id> [--yes ..]
```

_Argumentos:_ `post_id` — ID do post.

_Opções:_
- `--yes` (default: `False`) — Confirma a remoção definitiva (obrigatório — destrutivo).

### `cadencia-cli content published-get` — 🟢 READ
Mostra um post publicado (detalhe rico).

```bash
cadencia-cli content published-get <post_id>
```

_Argumentos:_ `post_id` — ID do post.

### `cadencia-cli content published-list` — 🟢 READ
Lista posts publicados.

```bash
cadencia-cli content published-list [--limit ..] [--status ..] [--formato ..]
```

_Opções:_
- `--limit` (default: `20`)
- `--status` — Filtra por status.
- `--formato` — Filtra por formato.

### `cadencia-cli content published-unpublish` — 🟡 WRITE
Tira um post do ar (status != published).

```bash
cadencia-cli content published-unpublish <post_id>
```

_Argumentos:_ `post_id` — ID do post.

### `cadencia-cli content published-update` — 🟡 WRITE
Edita um post publicado.

```bash
cadencia-cli content published-update <post_id> [--title ..] [--headline ..] [--html-content ..] [--legenda ..] [--capa-url ..] [--status ..] [--linkedin-text ..] [--seinfeld-body ..]
```

_Argumentos:_ `post_id` — ID do post.

_Opções:_
- `--title` — Título.
- `--headline` — Headline.
- `--html-content` — Corpo HTML/markdown.
- `--legenda` — Legenda.
- `--capa-url` — URL da capa.
- `--status` — Status (published/archived).
- `--linkedin-text` — Texto próprio do LinkedIn (published_posts.linkedin_text).
- `--seinfeld-body` — Corpo próprio do e-mail Seinfeld (published_posts.seinfeld_body).

### `cadencia-cli content queue-enqueue` — 🟡 WRITE
Enfileira geração (status dispatched).

```bash
cadencia-cli content queue-enqueue [--content-idea-id ..] [--channel ..] [--priority ..]
```

_Opções:_
- `--content-idea-id` — ID da ideia.
- `--channel` — Canal único (ex.: blog).
- `--priority` (default: `1`) — Prioridade.

### `cadencia-cli content queue-list` — 🟢 READ
Lista a fila de geração.

```bash
cadencia-cli content queue-list [--limit ..] [--status ..] [--channel ..]
```

_Opções:_
- `--limit` (default: `20`)
- `--status` — Filtra por status.
- `--channel` — Filtra por channel.

### `cadencia-cli content seo-update` — 🟡 WRITE
Atualiza campos de SEO de um post.

```bash
cadencia-cli content seo-update <post_id> [--meta-description ..] [--keyword ..] [--slug ..] [--cover-alt ..] [--og-image ..]
```

_Argumentos:_ `post_id` — ID do post.

_Opções:_
- `--meta-description` — Meta description.
- `--keyword` — Palavra-chave SEO.
- `--slug` — Slug.
- `--cover-alt` — Alt da capa (acessibilidade/SEO).
- `--og-image` — Imagem OG (mapeia p/ featured_image_url — schema não tem og_image separado).

### `cadencia-cli content slide-add` — 🟡 WRITE
Adiciona um slide (texto + imagem) ao carrossel de um documento.

```bash
cadencia-cli content slide-add <document_id> [--text ..] [--image ..]
```

_Argumentos:_ `document_id` — ID do documento (carrossel).

_Opções:_
- `--text` — Texto do slide.
- `--image` — URL da imagem do slide (do content image-upload).

### `cadencia-cli content slides-clear` — 🟡 WRITE
Esvazia os slides de um carrossel (slides_content = []).

```bash
cadencia-cli content slides-clear <document_id>
```

_Argumentos:_ `document_id` — ID do documento (carrossel).

### `cadencia-cli content slides-set` — 🟡 WRITE
Substitui todos os slides de um carrossel por uma lista JSON.

```bash
cadencia-cli content slides-set <document_id> [--slides-json ..]
```

_Argumentos:_ `document_id` — ID do documento (carrossel).

_Opções:_
- `--slides-json` — Lista JSON de slides, ex.: '[{"text":"..","url":".."}]'.

## `credits` — credits

### `cadencia-cli credits balance` — 🟢 READ
Mostra o saldo de créditos do tenant atual.

```bash
cadencia-cli credits balance 
```

### `cadencia-cli credits history` — 🟢 READ
Histórico de débitos/créditos do tenant.

```bash
cadencia-cli credits history [--limit ..]
```

_Opções:_
- `--limit` (default: `20`) — Máximo de transações.

## `crm-views` — Views do CRM (metadados)

### `cadencia-cli crm-views list` — 🟢 READ
Lista as views salvas do CRM.

```bash
cadencia-cli crm-views list [--entity ..]
```

_Opções:_
- `--entity` — Filtra por entidade.

## `custom-fields` — Campos customizados (CRM — metadados)

### `cadencia-cli custom-fields create` — 🟡 WRITE
Cria uma definição de campo customizado.

```bash
cadencia-cli custom-fields create [--entity ..] [--label ..] [--key ..] [--type ..] [--options ..] [--position ..]
```

_Opções:_
- `--entity` — Entidade: contact | company | opportunity.
- `--label` — Rótulo exibido (ex.: CNPJ).
- `--key` — Chave técnica (a-z0-9_). Derivada do label (prefixo cf_) se omitida.
- `--type` (default: `text`) — text | textarea | number | date | select.
- `--options` — Opções do select (separadas por ';'). Só para type=select.
- `--position` — Posição na ordenação. Auto (fim) se omitido.

### `cadencia-cli custom-fields list` — 🟢 READ
Lista as definições de campos customizados.

```bash
cadencia-cli custom-fields list [--entity ..]
```

_Opções:_
- `--entity` — Filtra por entidade (contact/company/opportunity).

## `leads` — leads

### `cadencia-cli leads enrich-company` — 🟡 WRITE
Atualiza uma empresa com dados do CNPJ.ws (pelo CNPJ cadastrado).

```bash
cadencia-cli leads enrich-company <company_id>
```

_Argumentos:_ `company_id` — ID da empresa já cadastrada.

### `cadencia-cli leads import` — 🟡 WRITE
Importa um lead (por CNPJ) como empresa + sócios + oportunidade.

```bash
cadencia-cli leads import [--cnpj ..] [--pipeline ..] [--stage ..]
```

_Opções:_
- `--cnpj` — CNPJ do lead (14 dígitos).
- `--pipeline` — Pipeline da oportunidade (slug ou id).
- `--stage` — Stage da oportunidade (slug ou id).

### `cadencia-cli leads search` — 🟢 READ
Busca um lead por CNPJ no CNPJ.ws (não grava no CRM).

```bash
cadencia-cli leads search [--cnpj ..]
```

_Opções:_
- `--cnpj` — CNPJ a consultar (14 dígitos).

## `loss-reasons` — loss-reasons

### `cadencia-cli loss-reasons list` — 🟢 READ
Lista os motivos de perda do tenant.

```bash
cadencia-cli loss-reasons list 
```

## `opportunities` — Oportunidades / Funil (CRM)

### `cadencia-cli opportunities close` — 🟡 WRITE
Fecha uma oportunidade (won/lost) com motivo.

```bash
cadencia-cli opportunities close <opportunity_id> [--status ..] [--reason ..]
```

_Argumentos:_ `opportunity_id` — ID da oportunidade.

_Opções:_
- `--status` — won ou lost.
- `--reason` — Motivo (vira lost_reason quando lost; senão status_reason).

### `cadencia-cli opportunities create` — 🟡 WRITE
Cria uma oportunidade (resolve slug de pipeline/stage).

```bash
cadencia-cli opportunities create [--contact ..] [--pipeline ..] [--stage ..] [--value ..] [--source ..]
```

_Opções:_
- `--contact` — ID do contato.
- `--pipeline` — Pipeline por slug ou id.
- `--stage` — Stage por slug ou id (do mesmo pipeline).
- `--value` — Valor estimado.
- `--source` — Origem da oportunidade (ex.: evento).

### `cadencia-cli opportunities get` — 🟢 READ
Mostra uma oportunidade.

```bash
cadencia-cli opportunities get <opportunity_id>
```

_Argumentos:_ `opportunity_id` — ID da oportunidade.

### `cadencia-cli opportunities list` — 🟢 READ
Lista oportunidades do tenant.

```bash
cadencia-cli opportunities list [--limit ..] [--status ..] [--contact ..] [--pipeline ..] [--stage ..]
```

_Opções:_
- `--limit` (default: `20`) — Máximo de oportunidades.
- `--status` — Filtra por status.
- `--contact` — Filtra por contato (id).
- `--pipeline` — Filtra por pipeline (slug ou id).
- `--stage` — Filtra por stage (slug ou id).

### `cadencia-cli opportunities move` — 🟡 WRITE
Move a oportunidade para outro stage do mesmo pipeline.

```bash
cadencia-cli opportunities move <opportunity_id> [--to-stage ..]
```

_Argumentos:_ `opportunity_id` — ID da oportunidade.

_Opções:_
- `--to-stage` — ID do stage destino.

### `cadencia-cli opportunities update` — 🟡 WRITE
Atualiza valor/source/status_reason de uma oportunidade.

```bash
cadencia-cli opportunities update <opportunity_id> [--value ..] [--source ..] [--status-reason ..]
```

_Argumentos:_ `opportunity_id` — ID da oportunidade.

_Opções:_
- `--value` — Valor estimado.
- `--source` — Origem da oportunidade.
- `--status-reason` — Motivo/observação de status.

## `pipeline` — pipeline

### `cadencia-cli pipeline forecast` — 🟢 READ
Forecast do funil: soma do valor das oportunidades abertas.

```bash
cadencia-cli pipeline forecast [--pipeline ..]
```

_Opções:_
- `--pipeline` — Pipeline (slug ou id). Omitido → todos os pipelines do tenant.

### `cadencia-cli pipeline summary` — 🟢 READ
Relatório do funil por stage: nº de oportunidades abertas + valor total.

```bash
cadencia-cli pipeline summary [--pipeline ..]
```

_Opções:_
- `--pipeline` — Pipeline (slug ou id). Omitido → todos os pipelines do tenant.

## `pipeline-stages` — pipeline-stages

### `cadencia-cli pipeline-stages create` — 🟡 WRITE
Cria um estágio num funil.

```bash
cadencia-cli pipeline-stages create [--pipeline ..] [--name ..] [--slug ..] [--position ..] [--is-terminal ..] [--color ..]
```

_Opções:_
- `--pipeline` — Funil (id ou slug).
- `--name` — Nome do estágio (ex.: Em contato).
- `--slug` — Slug (a-z0-9-). Derivado do nome se omitido.
- `--position` — Posição no funil. Auto (fim) se omitido.
- `--is-terminal` (default: `False`) — Marca como estágio terminal (ganho/perda).
- `--color` — Cor hex (ex.: #6366f1).

### `cadencia-cli pipeline-stages list` — 🟢 READ
Lista os estágios (filtre por --pipeline).

```bash
cadencia-cli pipeline-stages list [--pipeline ..]
```

_Opções:_
- `--pipeline` — Funil (id ou slug).

## `pipelines` — Pipelines / Stages (CRM — metadados)

### `cadencia-cli pipelines create` — 🟡 WRITE
Cria um funil no tenant.

```bash
cadencia-cli pipelines create [--name ..] [--slug ..] [--position ..]
```

_Opções:_
- `--name` — Nome do funil (ex.: Onboarding).
- `--slug` — Slug (a-z0-9-). Derivado do nome se omitido.
- `--position` — Posição na ordenação. Auto (fim) se omitido.

### `cadencia-cli pipelines list` — 🟢 READ
Lista os funis do tenant.

```bash
cadencia-cli pipelines list 
```

## `products` — products

### `cadencia-cli products contacts` — 🟢 READ
Lista os contatos vinculados a um produto.

```bash
cadencia-cli products contacts <product_id> [--kind ..]
```

_Argumentos:_ `product_id` — ID do produto.

_Opções:_
- `--kind` — Filtra por tipo: interesse|adquirido.

### `cadencia-cli products create` — 🟡 WRITE
Cria um produto no tenant.

```bash
cadencia-cli products create [--name ..] [--description ..] [--price ..] [--active/--inactive ..]
```

_Opções:_
- `--name` — Nome do produto (obrigatório).
- `--description` — Descrição.
- `--price` — Preço (numérico).
- `--active/--inactive` (default: `True`) — Produto ativo (padrão) ou inativo.

### `cadencia-cli products get` — 🟢 READ
Mostra um produto (campos ricos).

```bash
cadencia-cli products get <product_id>
```

_Argumentos:_ `product_id` — ID do produto.

### `cadencia-cli products link-contact` — 🟡 WRITE
Vincula um contato a um produto (interesse/adquirido).

```bash
cadencia-cli products link-contact [--product ..] [--contact ..] [--kind ..]
```

_Opções:_
- `--product` — ID do produto.
- `--contact` — ID do contato.
- `--kind` (default: `interesse`) — Tipo de relação: interesse|adquirido.

### `cadencia-cli products list` — 🟢 READ
Lista produtos do tenant.

```bash
cadencia-cli products list [--active/--all ..] [--limit ..]
```

_Opções:_
- `--active/--all` (default: `True`) — Só ativos (padrão) ou todos.
- `--limit` (default: `20`) — Máximo de produtos.

### `cadencia-cli products of-contact` — 🟢 READ
Lista os produtos de um contato.

```bash
cadencia-cli products of-contact <contact_id> [--kind ..]
```

_Argumentos:_ `contact_id` — ID do contato.

_Opções:_
- `--kind` — Filtra por tipo: interesse|adquirido.

### `cadencia-cli products unlink-contact` — 🟡 WRITE
Remove o vínculo de um contato com um produto.

```bash
cadencia-cli products unlink-contact [--product ..] [--contact ..] [--kind ..]
```

_Opções:_
- `--product` — ID do produto.
- `--contact` — ID do contato.
- `--kind` (default: `interesse`) — Tipo de relação: interesse|adquirido.

### `cadencia-cli products update` — 🟡 WRITE
Edita campos de um produto.

```bash
cadencia-cli products update <product_id> [--name ..] [--description ..] [--price ..] [--active/--inactive ..]
```

_Argumentos:_ `product_id` — ID do produto.

_Opções:_
- `--name` — Nome.
- `--description` — Descrição.
- `--price` — Preço (numérico).
- `--active/--inactive` — Marca ativo/inativo.

## `tags` — Tags (CRM — metadados)

### `cadencia-cli tags create` — 🟡 WRITE
Cria uma tag no tenant.

```bash
cadencia-cli tags create [--label ..] [--color ..]
```

_Opções:_
- `--label` — Texto da tag (ex.: gestores-ia).
- `--color` — Cor hex (ex.: #6366f1).

### `cadencia-cli tags list` — 🟢 READ
Lista as tags do tenant.

```bash
cadencia-cli tags list 
```

## `tasks` — tasks

### `cadencia-cli tasks complete` — 🟡 WRITE
Marca uma tarefa como concluída.

```bash
cadencia-cli tasks complete <task_id>
```

_Argumentos:_ `task_id` — ID da tarefa.

### `cadencia-cli tasks create` — 🟡 WRITE
Cria uma tarefa/follow-up no tenant.

```bash
cadencia-cli tasks create [--title ..] [--contact ..] [--opportunity ..] [--due ..] [--note ..]
```

_Opções:_
- `--title` — Título da tarefa (obrigatório).
- `--contact` — ID do contato vinculado.
- `--opportunity` — ID da oportunidade vinculada.
- `--due` — Prazo (YYYY-MM-DD) → due_at.
- `--note` — Anotação livre (vai em actor_metadata).

### `cadencia-cli tasks delete` — 🟡 WRITE
Remove (soft-delete) uma tarefa.

```bash
cadencia-cli tasks delete <task_id> [--yes ..]
```

_Argumentos:_ `task_id` — ID da tarefa.

_Opções:_
- `--yes` (default: `False`) — Confirma a remoção sem prompt.

### `cadencia-cli tasks get` — 🟢 READ
Mostra uma tarefa (campos ricos).

```bash
cadencia-cli tasks get <task_id>
```

_Argumentos:_ `task_id` — ID da tarefa.

### `cadencia-cli tasks hoje` — 🟢 READ
Tarefas pendentes com prazo até hoje (inclusive atrasadas).

```bash
cadencia-cli tasks hoje [--limit ..]
```

_Opções:_
- `--limit` (default: `50`) — Máximo de tarefas.

### `cadencia-cli tasks list` — 🟢 READ
Lista tarefas do tenant.

```bash
cadencia-cli tasks list [--contact ..] [--due-before ..] [--pending ..] [--limit ..]
```

_Opções:_
- `--contact` — Filtra por contato.
- `--due-before` — Só tarefas com due_at antes de (YYYY-MM-DD).
- `--pending` (default: `False`) — Só tarefas pendentes (completed_at IS NULL).
- `--limit` (default: `50`) — Máximo de tarefas.

## `tenants` — tenants

### `cadencia-cli tenants provision` — 🟡 WRITE
Provisiona um tenant (conta + tabelas base). Idempotente por e-mail.

```bash
cadencia-cli tenants provision [--name ..] [--email ..] [--password ..] [--plan ..] [--credits ..] [--tipo ..] [--nicho ..] [--whatsapp ..]
```

_Opções:_
- `--name` — Nome do cliente/usuário (display name).
- `--email` — E-mail de acesso (login).
- `--password` — Senha. Gera uma segura se omitida.
- `--plan` (default: `trial`) — growth_pro|profissional|essencial|trial|custom.
- `--credits` — Créditos (obrigatório quando plan=custom).
- `--tipo` (default: `P`) — Tipo: P (perfil pessoal) | E (empresa/marca).
- `--nicho` — Nicho/segmento.
- `--whatsapp` — WhatsApp com DDD.

### `cadencia-cli tenants set-config` — 🟡 WRITE
Grava chaves no tenant_config.config (merge jsonb, não sobrescreve o resto).

```bash
cadencia-cli tenants set-config <tenant_id> [--soul-md ..] [--temas ..] [--restricoes ..] [--audiencia ..] [--historia ..] [--json ..]
```

_Argumentos:_ `tenant_id` — ID do tenant.

_Opções:_
- `--soul-md` — Persona do chat agent (soul_md).
- `--temas` — temas_prioritarios (separados por ';').
- `--restricoes` — content_restrictions (separadas por ';').
- `--audiencia` — audiencia_descricao.
- `--historia` — historia_cliente.
- `--json` — Objeto JSON extra a mesclar no config.

### `cadencia-cli tenants set-dossier` — 🟡 WRITE
Grava o dossier (tenant_dossier.data) + version + validated_at. Upsert.

```bash
cadencia-cli tenants set-dossier <tenant_id> [--file ..] [--json ..] [--version ..] [--validated ..]
```

_Argumentos:_ `tenant_id` — ID do tenant.

_Opções:_
- `--file` — Arquivo JSON com os blocos do dossier.
- `--json` — JSON dos blocos do dossier (inline).
- `--version` (default: `2`) — Versão do dossier.
- `--validated` (default: `True`) — Marca validated_at = now().

### `cadencia-cli tenants set-editorials` — 🟡 WRITE
Grava editorias (tenant_editorials). topics/audience_pains são text[].

```bash
cadencia-cli tenants set-editorials <tenant_id> [--file ..] [--json ..]
```

_Argumentos:_ `tenant_id` — ID do tenant.

_Opções:_
- `--file` — Arquivo JSON: lista de editorias.
- `--json` — JSON inline: lista de editorias.

### `cadencia-cli tenants set-visual` — 🟡 WRITE
Define sub-preset + cores/fontes custom do tenant.

```bash
cadencia-cli tenants set-visual <tenant_id> [--sub-preset ..] [--cor-primaria ..] [--cor-destaque ..] [--font-headline ..] [--font-body ..]
```

_Argumentos:_ `tenant_id` — ID do tenant.

_Opções:_
- `--sub-preset` — Sub-preset visual (ex.: creator_personal_vinci).
- `--cor-primaria` — Cor primária (#hex).
- `--cor-destaque` — Cor de destaque (#hex).
- `--font-headline` — Fonte de headline.
- `--font-body` — Fonte de corpo.

### `cadencia-cli tenants upload-asset` — 🟡 WRITE
Envia logo/foto ao Supabase Storage e grava a URL no config.

```bash
cadencia-cli tenants upload-asset <tenant_id> [--type ..] [--file ..]
```

_Argumentos:_ `tenant_id` — ID do tenant.

_Opções:_
- `--type` — logo | photo.
- `--file` — Caminho do arquivo local.

### `cadencia-cli tenants verify` — 🟢 READ
Estado consolidado de um tenant (validação do provisionamento).

```bash
cadencia-cli tenants verify <tenant_id>
```

_Argumentos:_ `tenant_id` — ID do tenant.

---

**Total: 111 comandos** em 17 grupos. Bloqueados até DEV-582: `contacts enrich`, `content carousel-dispatch` (mutações com lógica de crédito/sessão).
