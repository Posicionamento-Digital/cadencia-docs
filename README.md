# cadencia-docs

Base de conhecimento da Cadencia — sistemas, processos, infra e framework de IA.

Publicada em: **https://posicionamento-digital.github.io/cadencia-docs/**

## O que é isso

Documentação centralizada para quem trabalha na Cadencia. Cobre o produto (app, workers, growth, motor gráfico), infraestrutura (VPS, Cloudflare, N8N), o PD Framework (squads, motor autônomo, memória) e onboarding de novos devs.

Construída com [MkDocs Material](https://squidfunk.github.io/mkdocs-material/). O conteúdo vem de três fontes: docs do `cadencia-app`, notas Obsidian exportadas e arquivos criados diretamente aqui.

## Como contribuir

**Atualização automática:** a skill `/documentar` atualiza esta base ao fechar uma issue no Linear. É o caminho padrão — não edite manualmente o que a skill gera.

**Edição manual:**

```bash
# 1. Clone
git clone https://github.com/Posicionamento-Digital/cadencia-docs.git
cd cadencia-docs

# 2. Instale dependências
pip install mkdocs-material mkdocs-minify-plugin

# 3. Rode localmente
mkdocs serve
# → http://localhost:8000

# 4. Commite e faça push na main
# O site atualiza em ~40s via GitHub Actions
```

## Estrutura

```
docs/
├── index.md                    # Home com cards de navegação
├── cadencia-app/               # Produto principal — arquitetura, frontend, workers, ADRs
├── central-cs-onboarding/      # Sistema de onboarding autônomo de clientes
├── central-observabilidade/    # Monitoramento, gate de triagem, auto-correção
├── _infra/                     # VPS Master, VPS Dev, Cloudflare, N8N
├── _pd-framework/              # Framework multi-agente — squads, motor autônomo, memória
├── _dev-process/               # Como trabalhamos — processo, gotchas, incidentes
├── _onboarding/                # Setup para novos devs, IA, harness
└── processos/                  # Processos gerais da empresa
```

## Hooks

`docs/hooks.py` roda antes de cada build e:
- Converte wikilinks `[[...]]` do Obsidian em texto simples
- Remove links relativos quebrados (`.ts`, `.sql`, `CLAUDE.md`, caminhos fora do site)
- Strip de links `.md` que não existem na coleção de docs

## Relacionado

- **Repo do produto:** [Posicionamento-Digital/cadencia-app](https://github.com/Posicionamento-Digital/cadencia-app) (privado)
- **PD Framework:** monorepo de squads e automação (privado)
- **Linear:** [linear.app/cadencia](https://linear.app/cadencia) — time CAD para issues do produto
