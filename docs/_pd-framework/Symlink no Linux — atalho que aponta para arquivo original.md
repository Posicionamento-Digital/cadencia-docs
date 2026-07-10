---
date: 2026-05-21
tags: [linux, infraestrutura, aprendizado, ata]
moc: "[[MOC-IA-Tecnologia]]"
---
# Symlink no Linux — atalho que aponta para arquivo original

Symlink (symbolic link) é um ponteiro para um arquivo ou diretório. O sistema enxerga o symlink como se fosse o arquivo real — qualquer programa que abrir o symlink está abrindo o original.

## Como funciona

```bash
ln -s /caminho/do/original /caminho/do/symlink
```

Exemplo:
```bash
ln -s /opt/skills-compartilhadas/log-sessao ~/.claude/skills/log-sessao
```

O arquivo em `/opt/skills-compartilhadas/log-sessao` é o original. O que fica em `~/.claude/skills/` é o ponteiro. Quando o original muda, o symlink reflete automaticamente — sem precisar copiar de novo.

## Diferença para cópia

| | Cópia | Symlink |
|---|---|---|
| Atualização | manual — precisa copiar de novo | automática — muda o original, todos recebem |
| Independência | cada cópia é independente | todos apontam para o mesmo arquivo |
| Risco | sem acoplamento | se o original mudar, afeta todos |

## Equivalente no Windows

Atalho (`.lnk`) — mesma ideia, mas o Windows não trata o atalho como arquivo real em todos os contextos. No Linux, o symlink é transparente para qualquer comando.

## Quando usar e quando não usar

**Usar:**
- Compartilhar configurações entre múltiplos usuários que devem ficar sincronizadas
- Manter um único ponto de verdade para arquivos usados em vários lugares

**Não usar:**
- Quando cada usuário precisa de versão própria e independente do arquivo
- Quando há risco de um usuário modificar o original sem querer afetar os outros

## Contexto onde aprendi

Surgiu no planejamento da VPS de desenvolvimento — discutindo como compartilhar skills do Claude Code entre os usuários `felipe` e `luiz`. Optamos por **cópia** em vez de symlink: mais simples, sem acoplamento, e permite que cada um adapte skills ao próprio contexto sem afetar o outro.

## Notas Relacionadas

[[IA-Tecnologia/2026-05-19 Linux FHS — onde cada coisa mora no sistema de arquivos]] · [[IA-Tecnologia/2026-05-19 1Password Service Accounts e isolamento Claude Code VPS]]