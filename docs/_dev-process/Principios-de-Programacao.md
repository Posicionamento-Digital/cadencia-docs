---
date: 2026-07-11
tags: [dev, principios, qualidade, dry]
---

# Princípios de Programação da Empresa

> Como escrevemos código na Cadência — não é preferência de estilo, é redução de risco real.

Esses princípios vêm da leitura de *O Programador Pragmático* (Hunt & Thomas), aplicada
diretamente no dia a dia do pd-framework e do Cadência. Não são regras abstratas — cada uma existe
porque já vimos (ou identificamos) o problema real que ela evita. A lista cresce conforme
avançamos na leitura; hoje tem um princípio, os próximos entram como novas seções aqui (não em
páginas separadas — ver princípio 1).

## 1. DRY — Don't Repeat Yourself

**O que é de verdade:** não é sobre copiar/colar texto. É sobre **conhecimento** — uma regra de
negócio, uma decisão, uma estrutura, um mapeamento — que deve existir em **um único lugar
autoritativo**. Toda cópia desse conhecimento em um segundo lugar **vai divergir** da primeira mais
cedo ou mais tarde; não é hipótese, é questão de tempo.

Vale igual para três tipos de duplicação:
- **Lógica/config** — a mesma regra escrita em 2 funções, 2 scripts, 2 mapeamentos diferentes.
- **Documentação** — a mesma estrutura ou decisão redigitada em 2+ documentos.
- **Templates/critérios** — o mesmo critério (ex: o que é bug crítico) copiado entre processos parecidos.

### Como aplicamos

1. Toda vez que uma regra/decisão precisa aparecer em mais de um lugar, **um lugar é a fonte** e
   os outros são **derivados** dela — gerados por script, linkados, ou lidos em runtime. Nunca
   reescritos à mão.
2. Se ainda não dá pra gerar automaticamente, no mínimo **linkamos pra fonte** em vez de reescrever
   o conteúdo.
3. A mesma frase de regra de negócio aparecendo pela 2ª vez em prosa solta já é sinal de criar a
   fonte única antes da 3ª.

### O que NÃO é violação

Ter a mesma informação em formatos ou públicos diferentes (ex: um resumo técnico pra dev e uma
página aqui pro time todo) não é duplicação — é tradução de audiência, desde que o **fato em si**
(a decisão, o número, o critério) tenha uma fonte e o resto derive dela.

## Gotchas & armadilhas

- **Duplicação de doc é mais fácil de ignorar que duplicação de código** — não quebra em produção
  na hora, quebra meses depois quando alguém segue a cópia desatualizada. Trate documentação
  divergente com a mesma seriedade que código duplicado.

## FAQ

**Isso significa nunca copiar nada?**
Não. Significa que, se copiar, alguém tem que saber qual cópia é a fonte e garantir que as outras
derivam dela — automaticamente sempre que possível.

**Onde entra isso no meu dia a dia?**
Antes de escrever lógica nova: um grep rápido pra ver se já existe algo parecido em outro
componente. Antes de escrever doc nova: verificar se a informação já vive em outro lugar e, se
sim, linkar em vez de reescrever.

## Refs técnicas

- Fonte operacional completa (agentes/devs no pd-framework): `_core/CODING-PRINCIPLES.md`
- Enforcement: gate de code review (`_core/DEV-WORKFLOW.md` §15) + cascata Linear
  (`/linear-planejar-issue`, `/linear-close-issue`)
- Exemplo aplicado: geração automática do Playbook Obsidian a partir desta mesma fonte
  (`_core/lib/cadencia_docs_to_playbook.py`)
- Livro: *O Programador Pragmático*, Hunt & Thomas — cap. "The Evils of Duplication"
