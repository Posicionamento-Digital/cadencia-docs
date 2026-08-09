# CAIXA1 — Mapa de armazenamento (matriz de decisão determinística)

> Criado 2026-08-09 (DEV-1726). **Regra dura pra agentes:** ao gravar qualquer arquivo, consultar esta tabela ANTES. Sem consultar Felipe. Sem "onde você prefere". Match por tipo → destino.

## Contexto rápido

**CAIXA1** = VPS Local Windows 10 do Felipe (Celeron J1800, 8 GB RAM dual-channel, 1,4 TB). 24×7 Tailscale mesh, alias SSH `vps-local`. Detalhes: `stamper/skills/vps-local/SKILL.md`.

## Drives — o que cada um significa

| Drive | Label | Tamanho | Modo | Escrita autorizada |
|---|---|---|---|---|
| **C:** | (sistema) | 111 GB SSD | RW automação | git pull + install scripts |
| **F:** | **PD-Backup** | 596 GB HD | 🔒 **READ-ONLY pra agentes** | Só `run-all-backups.ps1` (Task Scheduler CAIXA1 03h) |
| **D:** | **PD-Cloud** | 453 GB HD | RW compartilhamento externo | Agentes gravam quando produzem artefato pra cliente |
| **G:** | **PD-Arquivo** | 287 GB HD | RW frio | Felipe manual; agentes não escrevem |

## Matriz determinística — TIPO DE ARQUIVO × DESTINO

**Regra:** identifique o tipo do arquivo pelas pistas da coluna esquerda. Grava no destino da direita. **Não pergunte, não sugira alternativa.** Só desvie se Felipe interromper explicitamente.

### 1. Artefatos entregues/entregáveis a cliente externo

| Pista | Destino |
|---|---|
| PDF de contrato assinado / a assinar | `D:\PD-Cloud\Clientes\<NomeCliente>\Contratos\` |
| Proposta comercial finalizada (PDF/DOCX) | `D:\PD-Cloud\Clientes\<NomeCliente>\Propostas\` |
| Manual da marca / dossier v3 / soul entregues | `D:\PD-Cloud\Clientes\<NomeCliente>\Marca\` |
| Apresentação final / deck reunião entregue | `D:\PD-Cloud\Clientes\<NomeCliente>\Apresentacoes\` |
| Gravação de reunião liberada pra cliente | `D:\PD-Cloud\Clientes\<NomeCliente>\Reunioes\` |
| Ata em PDF entregue ao cliente (não a fonte no vault) | `D:\PD-Cloud\Clientes\<NomeCliente>\Reunioes\Atas\` |
| Peça de conteúdo (carrossel, blog PDF) entregue | `D:\PD-Cloud\Clientes\<NomeCliente>\Conteudo\<data>\` |
| Template reutilizável (modelo em branco) | `D:\PD-Cloud\Templates\<categoria>\` |
| Arquivo genérico pra share rápido único | `D:\PD-Cloud\Public\` |

**Após gravar em `D:\PD-Cloud\`, se o objetivo é gerar link, retornar `https://cloud.cadencia.app.br/files/<path>` e sugerir gerar share link via UI (agentes ainda não têm API pra criar share programaticamente).**

### 2. Materiais RECEBIDOS de cliente (não confundir com entregues)

| Pista | Destino |
|---|---|
| Áudio/vídeo enviado pelo cliente | OneDrive: `Documentos\Customer Success\<categoria>\<Cliente>\Materiais\Recebidos\` (regra CLIENT-FILES-POLICY §DEV-1043) |
| Planilha/doc que cliente mandou | idem OneDrive |
| Transcrição de reunião com cliente | Vault Empresa `Reuniões/Clientes/<Cliente>/<data>_<slug>.md` (regra CSE-90) |

**NÃO usar `D:\PD-Cloud\Recebidos\`** — essa pasta é pra upload direto do cliente (share link com permissão upload), não pra arquivo que agente cola. Cliente-side path.

### 3. Docs internas (código, framework, playbook)

| Pista | Destino |
|---|---|
| Doc técnica de repo/feature/componente | `<repo>/docs/` no repo próprio + espelho em `cadencia-docs/docs/<mapeamento>/` |
| Plano técnico de issue Linear | `pd-framework/times/<squad>/context/plano-<ISSUE>.md` |
| ADR (decisão arquitetural) | `<repo>/docs/adr/NNNN-<slug>.md` |
| Inventário/análise pontual de sistema | `pd-framework/times/<squad>/context/<slug>-<YYYY-MM>.md` |
| Nota formal de reunião interna | Vault Empresa `Reuniões/Interno/<data>_<slug>.md` |
| Nota rascunho técnico pessoal | Vault Pessoal `<categoria>/YYYY-MM-DD <titulo>.md` |
| Session log de trabalho (auto) | `pd-framework/sessions-log/YYYY-MM-DD/<slug>_<HHMM>.md` |
| Memória Stamper (auto) | `pd-framework/stamper/memory/session_<slug>_<YYYY_MM_DD>.md` + entrada em `MEMORY.md` |
| Incidente técnico | Hub `OneDrive\Documentos\ClaudeCode\Hub Projetos\Incidentes\YYYY-MM-DD_<slug>.md` |

**Nada disso vai pra `D:\PD-Cloud\`.** Cloud é canal externo, não repositório de doc.

### 4. Screenshots, arquivos temporários, evidências pontuais

| Pista | Destino |
|---|---|
| Screenshot pra colar no chat / debug | Windows Explorer padrão: `OneDrive\Imagens\Screenshots\` (não gravar) |
| Arquivo temporário de teste (`.tmp`, dump ad-hoc) | `C:\temp\` (agente notebook) ou `C:\Windows\Temp\` (CAIXA1) — nunca commitar |
| Log de execução de skill | `C:\Users\felip\.claude\logs\` ou output do próprio agente |

### 5. Código, scripts, config

| Pista | Destino |
|---|---|
| Script de automação/worker | repo próprio (`pd-framework`, `cadencia-app`, etc.) — `_shared/`, `_core/`, `times/*/workers/` |
| Config de infra (mkdocs, docker-compose) | repo do serviço |
| Secret / credencial | 1Password — nunca em arquivo (regra CREDENTIALS.md) |

### 6. Arquivo morto (frio, sem SLA)

| Pista | Destino |
|---|---|
| Gravação antiga que não gira mais (>6 meses) | `G:\PD-Arquivo\Gravacoes\<YYYY>\` |
| Export histórico que "vai que" | `G:\PD-Arquivo\Exports\<YYYY>\` |
| Backup manual pontual antes de destrutivo | `G:\PD-Arquivo\Snapshots\<YYYY-MM-DD>_<motivo>\` |

**Nunca referenciar `G:\` de skill/worker ativo** — é cold storage sem garantia.

## Casos de dúvida — algoritmo de fallback

Se o arquivo não casa claramente com nenhuma linha acima, aplicar em ordem:

1. **É pra sair do círculo interno da PD (cliente externo, parceiro, público)?** → `D:\PD-Cloud\`
2. **É doc/nota/plano interno?** → repo relevante (`pd-framework/times/`, `<projeto>/docs/`) ou vault Obsidian
3. **É material físico recebido de cliente?** → OneDrive `Customer Success\`
4. **É temporário/descartável?** → `C:\temp\` (notebook) ou `C:\Windows\Temp\` (CAIXA1)
5. **Ainda em dúvida?** → agente reporta ao Felipe COM proposta única + racional (não menu de opções)

## O que NÃO fazer

- ❌ **Perguntar ao Felipe onde salvar** — matriz acima é determinística; perguntar = violar regra
- ❌ **Gravar em `F:\`** — quebra retention do restic
- ❌ **Duplicar arquivo em 2 destinos "por precaução"** — divergência silenciosa depois
- ❌ **Colocar doc interna em `D:\PD-Cloud\`** — cloud não é repositório
- ❌ **Colocar material de cliente dentro de `pd-framework/times/`** — regra DEV-1043
- ❌ **Gerar share link de junction/pasta linkada** que aponte pra Obsidian/repo (vaza doc interna)

## Onde encontrar o que já foi gravado

| Procuro... | Ver primeiro |
|---|---|
| Doc técnica de um repo | `<repo>/docs/` OU `docs.cadencia.app.br` (autenticado, admin) |
| Ata / transcrição de reunião | Vault Empresa `Reuniões/Clientes/` ou `Reuniões/Interno/` |
| Material entregue a cliente X | `D:\PD-Cloud\Clientes\<X>\` |
| Material recebido de cliente X | OneDrive `Customer Success\<cat>\<X>\Materiais\Recebidos\` |
| Incidente de sistema | Hub `Incidentes\INDEX.md` |
| Backup restaurável de qualquer coisa | `F:\restic-repo\` via `restic snapshots` (senha 1P vault Databases) |
| Plano de issue Linear DEV-XXXX | `pd-framework/times/<squad>/context/plano-DEV-XXXX.md` |
| Session log de X dias atrás | `pd-framework/sessions-log/YYYY-MM-DD/` |
| Skill do framework | `pd-framework/stamper/skills/<nome>/SKILL.md` |
| Convenção/regra do framework | `pd-framework/_core/*.md` |

## Skills relacionadas

- `/vps-local` — SSH headless CAIXA1
- `/vps-local-acesso-remoto` — RDP (área de trabalho)

## Referências

- [`_core/CLIENT-FILES-POLICY.md`](CLIENT-FILES-POLICY.md) — materiais físicos de cliente (OneDrive)
- [`times/infra/context/plano-backup-caixa1.md`](../times/infra/context/plano-backup-caixa1.md) — plano backup completo
- [`_shared/backup-caixa1/README.md`](../_shared/backup-caixa1/README.md) — scripts + deploy
- Doc infra Obsidian Pessoal: `Infra/2026-08-08 VPS Local CAIXA1 (Windows).md`
