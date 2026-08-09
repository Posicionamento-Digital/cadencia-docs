# Política — Arquivos de cliente vivem no Cadencia Cloud (CAIXA1)

> Regra dura desde 2026-08-09 (DEV-1726). Fonte única. Sem alternativa, sem "no meu caso...".

## Regra

**Materiais físicos de cliente (recebidos/entregues, planilhas) vivem SOMENTE em:**

```
\\caixa1.taild6079b.ts.net\PDCloud\Clientes\<Nome do Cliente>\
├── Materiais\
│   ├── Recebidos\      ← cliente sobe via share link com upload
│   └── Entregues\      ← Cadencia entrega (contrato, dossier, deck, PDF branded)
└── Planilhas\
```

Path local na CAIXA1: `D:\PD-Cloud\Clientes\<Nome>\`.
URL público (share link): `https://cloud.cadencia.app.br/share/<hash>`.

**Nunca duplicar esses arquivos dentro do repo `pd-framework`** (nem em `times/produto/consultorias/<slug>/materiais/`, nem em `reunioes/`, nem em `.claude/` ou outro subdir do git). O `CLAUDE.md` do cliente **linka** pro path — não copia o conteúdo.

## Como o cliente acessa

- **Link público:** `https://cloud.cadencia.app.br/share/<hash>` — Filebrowser gera share link com senha/expiração; cliente não precisa de conta, abre no browser e baixa/sobe
- **Acesso Felipe:** RDP na CAIXA1 (`/vps-local-acesso-remoto`) OU SMB via Tailscale (`\\caixa1.taild6079b.ts.net\PDCloud\Clientes\`)
- **Backup:** `D:\PD-Cloud\` é backupada diariamente pelo restic → `F:\restic-repo\` (03h automatizado, sem ação humana)

## Exceção — atas e transcrições de reunião (CSE-90)

**Fonte única de ata/transcrição de cliente = Obsidian vault Empresa, `Reuniões/Clientes/`** — não em `\PDCloud\Clientes\<Nome>\`. Motivos: é o precedente real de todos os clientes ativados, é buscável/linkável no vault, e é o que o pipeline consome (skill `/obsidian-transcrever-reuniao` grava lá; gatilho `pos-briefing-trigger` e gate "Ata da call de vendas" do `/ativar-cliente` leem de lá).

- Subpasta `Reunioes\` **NÃO existe** na estrutura do Cadencia Cloud.
- O que o CLIENTE recebe (ata em PDF entregue) vai em `Materiais\Entregues\Atas\` — é entrega, não fonte.

## Convenção de nomenclatura

Nome humano completo, sem abreviar (ex: `Melissa Quevedo`, `OP Odontopenha`, `Iasmin Lopes Pinto`) — mesma capitalização usada no título do `CLAUDE.md` do cliente no framework. Todos os clientes em `Clientes\` (não separa Consultorias/Treinamentos — o tipo vive no CLAUDE.md do cliente).

## O que muda pra quem cria/edita pasta de cliente

- **Criar cliente novo:** `/ativar-cliente` Bloco A.4 cria a pasta em `\\caixa1.taild6079b.ts.net\PDCloud\Clientes\<Nome>\` automaticamente
- **CLAUDE.md do cliente:** sempre incluir linha `**Pasta compartilhada (Cadencia Cloud):** \\caixa1.taild6079b.ts.net\PDCloud\Clientes\<Nome>\` na seção `## Links`
- **Cliente manda arquivo:** share link com permissão upload em `Materiais\Recebidos\` → cliente sobe pelo browser, aparece direto
- **Cadencia entrega arquivo:** grava em `Materiais\Entregues\<categoria>\`; gera share link no Filebrowser; envia pelo WhatsApp/email
- **Arquivos internos do agente** (`CLAUDE.md` do cliente, `memory/STATE.md`, `decisions.md`) continuam **só no git** — não são pra cliente ver, não vão pro Cloud

## Refs

- `_core/CAIXA1-STORAGE-MAP.md` — matriz determinística por tipo de arquivo → destino
- `times/cs/foundation/padrao-pasta-cliente.md` — estrutura de pastas do cliente no framework (git) + onde cada coisa vai
- `times/cs/skills/ativar-cliente/SKILL.md` — Bloco A.4 (gate de criação da pasta compartilhada)
- `_shared/backup-caixa1/README.md` — sistema de backup da CAIXA1

## Histórico

Migrado de `OneDrive\Documentos\Customer Success\` (regra anterior DEV-1043 vigente 2026-07-01 → 2026-08-09). 12 pastas movidas via robocopy sobre SMB Tailscale. Ver `times/cs/memory/decisions.md` §2026-08-09 pra racional completo da migração.
