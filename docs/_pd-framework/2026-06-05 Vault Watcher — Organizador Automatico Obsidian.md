---
date: 2026-06-05
tags: [ia, tecnologia, automacao]
moc: "[[MOC-IA-Tecnologia]]"
type: source
entities: ["[[Cadencia]]", "[[comercial]]", "[[financeiro]]", "[[marketing]]", "[[pd-portal]]"]
---
## Contexto

Worker determinístico que organiza automaticamente as notas dos dois vaults Obsidian
(Pessoal e Time PD) criadas no celular. Sem IA, sem API, 100% local.

## Como funciona

### Fluxo completo

```
Felipe cria nota no celular (Obsidian mobile)
  → Obsidian Sync sobe para nuvem
  → Obsidian no PC baixa o arquivo para o vault local
  → vault-watcher detecta o arquivo novo (watchdog filesystem)
  → Aguarda 3s (debounce — Sync dispara vários eventos por arquivo)
  → Classifica por keywords do conteúdo
  → Move para pasta certa + injeta frontmatter + wikilinks semânticos
```

### Regras por tipo de arquivo

**Na raiz do vault** (onde notas do celular chegam):
1. Keywords do conteúdo → pasta destino
2. Data extraída do nome do arquivo ou `LastWriteTime`
3. Renomeia para `YYYY-MM-DD Título.md`
4. Move para pasta (`IA-Tecnologia/`, `Comercial/`, `Sessoes/`, etc.)
5. Injeta frontmatter: `date`, `tags`, `moc`
6. Adiciona `## Notas Relacionadas` com wikilinks do title index

**Em subpasta, sem frontmatter:**
- Não move — injeta frontmatter no lugar

**Sempre pula:** `README.md`, `000-INDEX.md`, `MOC-*.md`, `.obsidian/`, `.trash/`

### Pastas do vault Time PD

| Pasta | Keywords |
|---|---|
| `IA-Tecnologia` | llm, claude, mcp server, webhook, vps, docker, pd-framework |
| `Projetos` | cadencia.app, pd-portal, pdl-, roadmap do produto |
| `Comercial` | lead pd, crm pd, proposta comercial pd, pipeline de vendas |
| `CS` | onboarding do cliente, churn pd, nps pd |
| `Marketing-PD` | conteudo para pd, lancamento pd, nocode startup |
| `Infra` | vps master, deploy pd, nginx pd, ssl pd |
| `Financeiro` | nota fiscal pd, dre pd, asaas pd |
| `Reunioes` | ata de reuniao, kickoff pd, briefing de projeto |
| `Skills` | skill de automacao, playbook de automacao |
| `Sessoes` | (fallback) |

## Catch-up automático

Na inicialização, o watcher faz um **catch-up pass** completo:
varre os dois vaults e organiza tudo que ficou pendente enquanto o PC estava off/suspenso.

Isso garante que notas criadas no celular durante viagens, fins de semana ou com o PC desligado
sejam organizadas na próxima vez que o PC ligar — sem intervenção manual.

## Arquivos

| Arquivo | Path |
|---|---|
| Lógica de classificação | `C:\Users\felip\.claude\workers\vault-organizer.py` |
| Watcher + catch-up | `C:\Users\felip\.claude\workers\vault-watcher.py` |
| Log de operações | `C:\Users\felip\.claude\workers\vault-watcher.log` |
| Task Scheduler | `VaultWatcher-Obsidian` (At Logon, felip) |

## Operação manual

```powershell
# Ver o que seria organizado (sem aplicar)
& "C:\Python314\python.exe" "C:\Users\felip\.claude\workers\vault-organizer.py" --dry-run

# Aplicar manualmente
& "C:\Python314\python.exe" "C:\Users\felip\.claude\workers\vault-organizer.py"

# Ver log do watcher
Get-Content "C:\Users\felip\.claude\workers\vault-watcher.log" -Tail 20

# Reiniciar o watcher
schtasks /run /tn "VaultWatcher-Obsidian"
```

## Limitações

| Situação | Comportamento |
|---|---|
| Obsidian fechado no PC | Sync não desce — catch-up resolve no próximo boot |
| PC desligado | Igual — catch-up resolve |
| Nota sem keyword reconhecível | Vai para `Sessoes/` |
| Arquivo com frontmatter completo | Ignorado |
| Watcher crashou | Task Scheduler reinicia até 3x |

## Notas Relacionadas
[[MOC-IA]] - [[MOC-Infra]]
