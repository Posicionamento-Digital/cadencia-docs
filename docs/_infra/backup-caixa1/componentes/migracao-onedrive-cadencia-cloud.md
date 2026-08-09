# Migração OneDrive → Cadencia Cloud (2026-08-09) — processo replicável

## O que aconteceu

12 pastas de cliente migradas de `OneDrive\Documentos\Customer Success\` (regra anterior DEV-1043) para `D:\PD-Cloud\Clientes\` (regra atual DEV-1726, na CAIXA1). Fonte migrou de OneDrive comercial pra Cadencia Cloud self-hosted.

**Motivo:** OneDrive Files On-Demand deixava placeholders (arquivos não baixados localmente) → backup restic pegava só o que estava baixado, cobertura incompleta. Adicionalmente: share link OneDrive é ruim pro cliente externo (exige conta MS ou expiração toscas), e OneDrive só sincroniza com notebook ligado.

**Solução:** consolidar em Cadencia Cloud (CAIXA1 24×7, HD dedicado, HTTPS via Filebrowser+Tunnel, backup incluso).

## Timeline

| Passo | O quê |
|---|---|
| Análise superfície | grep de refs OneDrive em skills/foundation/CLAUDE.md dos clientes |
| Habilitar share SMB | `New-SmbShare -Name PDCloud -Path D:\PD-Cloud -FullAccess USUARIO` na CAIXA1 |
| Migração física | `robocopy` do notebook → `\\caixa1.taild6079b.ts.net\PDCloud\Clientes\` (SMB Tailscale) |
| Validação | count files + soma tamanho: `20 arquivos = 6,37 MB` (bate origem) |
| Atualizar 10 CLAUDE.md clientes | Script Python `replace()` — path OneDrive → path Cadencia Cloud |
| Atualizar skill `/ativar-cliente` | Skill canônica em `times/cs/skills/` + junction em `stamper/skills/` + `.opencode/agents/` |
| Atualizar docs canônicas | `_core/CLIENT-FILES-POLICY.md` reescrita + `_core/CAIXA1-STORAGE-MAP.md` consolidado |
| Atualizar foundation | `times/cs/foundation/padrao-pasta-cliente.md` + `template-manual-da-marca.md` |
| Atualizar decisions | Nova decisão D em `times/cs/memory/decisions.md` (append-only) |
| Atualizar worker | `times/cs/workers/conferencia-cobranca-pasta/state.json` (path Ariane) |
| Limpeza refs OneDrive | `CLAUDE.md` raiz + `AGENTS.md` + `MEMORY.md` + `reference_caixa1_storage_map.md` |
| Commit + push | 2 commits em main (feat + chore de limpeza) |
| Publicar cadencia-docs | Cópia dos 5 docs pra `docs/_infra/backup-caixa1/` |

## Descoberta importante: Files On-Demand placeholder

**OneDrive Files On-Demand** — feature que deixa arquivos como "shortcuts" na pasta local sem baixar o conteúdo. Ícone com nuvem em vez de check verde. Arquivo aparece no Explorer mas ocupa 0 bytes locais.

**Consequência pro backup/robocopy:** só o que estava marcado "Always keep on this device" (ícone verde) foi migrado. Placeholders **NÃO** foram — robocopy não força download, só copia o que está localmente presente.

**No caso:** 20 arquivos migrados = ~6 MB. Suspeita: OneDrive tem MUITO mais que isso não-baixado. Pra migrar 100%, precisa forçar download antes:

```powershell
# Forçar download recursivo de tudo em Customer Success\
Get-ChildItem "C:\Users\felip\OneDrive\Documentos\Customer Success" -Recurse -File |
    ForEach-Object { attrib -P +A $_.FullName }
```

Depois espera OneDrive baixar tudo (pode levar horas dependendo do volume) → refaz robocopy → migração 100% completa.

**Estado atual:** OneDrive fica como fallback read-only até 2026-09-09. Se algum cliente pedir material antigo que não foi migrado, forçar download só desse arquivo → mover manual pra Cadencia Cloud.

## Processo replicável (se precisar migrar outra fonte no futuro)

### Passo 1 — Preparar destino
```powershell
# Criar estrutura base na CAIXA1
ssh vps-local 'powershell -Command "New-Item -ItemType Directory -Force -Path D:\PD-Cloud\<NovoEscopo>"'

# Habilitar SMB share (se ainda não)
ssh vps-local 'powershell -Command "New-SmbShare -Name PDCloud -Path D:\PD-Cloud -FullAccess USUARIO -ErrorAction SilentlyContinue"'

# Mapear no notebook
$pwd = op item get 'VPS Local - senha acesso' --vault Hosts --fields password --reveal
net use '\\caixa1.taild6079b.ts.net\PDCloud' /user:USUARIO $pwd
```

### Passo 2 — Migrar arquivos
```powershell
robocopy "<origem>" "\\caixa1.taild6079b.ts.net\PDCloud\<NovoEscopo>" /E /NFL /NDL /NJH /NJS /MT:8 /R:1 /W:2
```

Flags:
- `/E` — recursivo incluindo pastas vazias
- `/NFL /NDL` — suprime lista de files/dirs no log
- `/NJH /NJS` — suprime header/summary
- `/MT:8` — 8 threads paralelas
- `/R:1 /W:2` — 1 retry, 2s de wait

### Passo 3 — Validar contagem
```powershell
$srcCount = (Get-ChildItem "<origem>" -Recurse -File -Force).Count
$dstCount = (Get-ChildItem "\\caixa1.taild6079b.ts.net\PDCloud\<NovoEscopo>" -Recurse -File -Force).Count
Write-Host "src=$srcCount dst=$dstCount match=$($srcCount -eq $dstCount)"
```

Se não bater: investigar antes de prosseguir (comum: Files On-Demand, permissões, symlinks quebrados).

### Passo 4 — Atualizar references no framework
1. `grep -rln "<path-antigo>" times/ stamper/ _core/ .opencode/ --include="*.md" --include="*.py" --include="*.ps1" --include="*.json"`
2. Script Python `replace()` sobre a lista
3. Verificar refs residuais (`grep` de novo)
4. Skills com refs: canônica em `times/<squad>/skills/` **E** junction em `stamper/skills/` **E** cópia em `.opencode/agents/` (regenerar da fonte)

### Passo 5 — Atualizar CLAUDE.md e decisions
- `CLAUDE.md` raiz: seção da regra vigente
- `AGENTS.md`: mirror
- `_core/<POLICY>.md`: reescrever regra clean; menção histórica só em `## Histórico`
- `times/<squad>/memory/decisions.md`: append nova decisão com contexto + racional + o que muda

### Passo 6 — Commit + espelhar
```bash
git add -A && git commit -m "feat(<squad>): migrar <origem> → <destino>"
git push
# Cópia em cadencia-docs se público-consumível
```

### Passo 7 — Definir prazo de aposentadoria da fonte antiga
- Fonte antiga fica read-only por N dias como fallback (padrão: 30 dias)
- Depois: arquivar em `G:\PD-Arquivo\legacy-<origem>\` na CAIXA1 e apagar da origem

## Anti-padrões evitados

- ❌ **Migrar sem validar contagem** — descobre depois que Files On-Demand deixou 80% pra trás
- ❌ **Apagar fonte imediatamente** — sempre 30 dias de fallback
- ❌ **Não atualizar CLAUDE.md dos clientes** — próximo agente que abre cliente lê path errado
- ❌ **Deixar refs históricas nas regras vigentes** — agente confuso mistura passado e presente
- ❌ **Migrar 1 cliente por vez** — inconsistência temporária, gap de skill (funciona só pra alguns)
- ❌ **Não atualizar `.opencode/agents/`** — Codex/OpenCode leem daí, ficam com skill velha

## Custos do processo (referência)

Migração 2026-08-09:
- Tempo total: ~2h (planejamento + execução + limpeza)
- Downtime cliente: 0 (migração paralela, sem interrupção)
- Risco de perda: 0 (fonte original preservada como fallback)
- Rollback path: reverter regra + skills apontarem OneDrive de novo (todos os dados originais intactos)

## Refs

- Regra anterior (histórico): DEV-1043 — OneDrive `Customer Success\`
- Regra atual: DEV-1726 — Cadencia Cloud `D:\PD-Cloud\Clientes\`
- Decisão detalhada: `times/cs/memory/decisions.md` § 2026-08-09
- Política atual: `_core/CLIENT-FILES-POLICY.md`
- Matriz storage: `_core/CAIXA1-STORAGE-MAP.md`
- Session log: `sessions-log/2026-08-09/backup-cloud-caixa1-f0-f6-done...md`
