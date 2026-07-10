---
date: 2026-05-14
tags: [skill, reuniao, obsidian, documentacao, google, drive, ia, tecnologia, automacao, ata]
moc: "[[MOC-Skills]]"
---
# Ata Reuniao

Ciclo completo pós-reunião: localiza transcrição no Google Drive, extrai decisões e próximas etapas, cria nota estruturada no Obsidian Time PD e entrega texto formatado para enviar no grupo.

## Quando usar
"cria ata", "faz a ata de [cliente]", "registra a reunião", "gera o texto para o grupo", "documenta a call de [nome]". Qualquer pedido de registrar, documentar ou comunicar resultado de reunião.

---

## Conteúdo da Skill

```markdown
---
name: ata-reuniao
description: >
  Automatiza o ciclo completo de documentação pós-reunião: localiza a transcrição no Google Drive, extrai decisões e próximas etapas, cria nota estruturada no Obsidian com todas as propriedades preenchidas, e entrega o texto formatado pronto para copiar e colar no grupo.
---

## O que essa skill faz

1. Localiza e carrega a transcrição no Google Drive
2. Extrai decisões, participantes e próximas etapas
3. Cria nota estruturada no Obsidian no vault correto
4. Entrega texto formatado para o grupo

---

## Configuração fixa

| Recurso | Valor |
|---|---|
| Google Drive — Pasta transcrições | `1VDTfLneMss9JHFvzh_Pubi8ZjtFqvkVw` |
| Obsidian CLI | `C:\Users\felip\AppData\Local\Programs\Obsidian\Obsidian.com` |

## Roteamento de vault

| Tipo de reunião | Vault | Pasta |
|---|---|---|
| Cliente (NSkin, H&Co, GCI GO) | Pessoal | `Clientes/[NomeCliente]/` |
| Comercial / vendas / proposta | Pessoal | `Comercial/Propostas/` |
| Reunião interna PD | Pessoal | `Reunioes/` |
| Reunião técnica com Luiz / time dev | Time PD | `Time/Reunioes/` |
| Dúvida → usar | Pessoal | `Reunioes/` |

---

## Passo 1 — Localizar a transcrição no Google Drive

Buscar na pasta de transcrições:

```
api_query: "'1VDTfLneMss9JHFvzh_Pubi8ZjtFqvkVw' in parents"
order_by: "modifiedTime desc"
```

- Se o usuário mencionou um nome/cliente → adicionar `and name contains '[nome]'`
- Se pediu "de hoje" ou "mais recente" → usar o primeiro resultado
- Se múltiplos arquivos forem candidatos → listar e pedir escolha

---

## Passo 2 — Carregar a transcrição completa

Usar `google_drive_fetch` com o `document_id` encontrado. Trabalhar sempre com o documento inteiro — nunca com o preview truncado.

---

**REGRA ABSOLUTA — ACENTUAÇÃO:**
Todo texto gerado DEVE usar acentuação correta do português brasileiro. NUNCA gerar texto sem acentos.

---

## Passo 3 — Extrair dados estruturados

Da transcrição, extrair:

- **Título**: nome do evento
- **Data e hora**: do cabeçalho do documento Gemini
- **Participantes**: lista de convidados com emails quando disponível
- **Resumo executivo**: 2–3 frases sobre o foco central da reunião
- **Principais decisões**: o que foi *decidido* (não apenas discutido)
- **Próximas etapas**: ações concretas com responsável identificado quando possível

**Classificar automaticamente:**

| Propriedade | Lógica |
|---|---|
| `Tipo` | Reunião com time do cliente → "Alinhamento semanal cliente"; call de fechamento/vendas → "Call de vendas"; reunião interna sem cliente → "Reunião interna" |
| `Setor` | Implementação/CS/onboarding → "Customer Sucess"; vendas/CRM → "Comercial"; estratégia/planejamento → "Planejamento" |

---

## Passo 4 — Criar nota no Obsidian

**Nome do arquivo:** `YYYY-MM-DD [Cliente ou Tipo] Ata.md`

**Conteúdo com frontmatter obrigatório + wikilinks:**

```markdown
---
date: YYYY-MM-DD
tags: [reuniao, cliente-ou-tipo, setor]
---

## Participantes
- Nome 1 (email@exemplo.com)
- Nome 2

---

## Resumo
[Resumo executivo de 2–3 frases]

---

## Principais Decisões

### 1. [Título da Decisão]
[Contexto e o que foi decidido.]

---

## Próximas Etapas

- [ ] **[Responsável]** [Descrição da ação]

---

## Fonte
[Transcrição Google Drive](https://docs.google.com/document/d/[DOC_ID]/edit)

## Notas Relacionadas
[[pasta/do/cliente/README]] · [[Comercial/Pipeline/README]]
```

**Criar via CLI Python:**

```python
import subprocess

CLI = r'C:\Users\felip\AppData\Local\Programs\Obsidian\Obsidian.com'
r = subprocess.run(
    [CLI, 'create', f'path={path}', f'content={content}'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(r.stdout)
```

---

## Passo 5 — Gerar texto para o grupo

```
📋 **Ata — [Nome da Reunião]**
📅 [Data por extenso, ex: 17 de março de 2026]

---

**Principais decisões:**

- **[Decisão 1]** — [descrição curta e direta]
- **[Decisão 2]** — [descrição curta e direta]

---

**Próximas etapas:**
✅ [Responsável] → [ação]
✅ [Responsável] → [ação]

---

🔗 Ata completa: [URL da página criada]
```

---

## Casos especiais

| Situação | Ação |
|---|---|
| Múltiplas reuniões do mesmo cliente no mesmo dia | Listar e pedir escolha |
| Reunião sem transcrição (só notas) | Continuar com o que tiver disponível |
| Reunião interna (sem cliente externo) | Omitir campo "Lead ou Cliente" |
| Usuário já tem a transcrição aberta na conversa | Usar o conteúdo já carregado, pular os Passos 1 e 2 |
```

## Notas Relacionadas
[[Reunioes-Docs/Busca Reunioes]] · [[Reunioes-Docs/Documentar]] · [[Stamper-Operacionais/Registrar Notas]]
