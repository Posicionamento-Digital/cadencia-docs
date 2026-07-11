"""
MkDocs hooks — limpeza automática de artefatos do Obsidian e links quebrados.

Roda no evento `page_markdown` (antes do parse) para:
1. Remover wikilinks [[...]] — vira texto simples ou link clicável quando possível
2. Remover links relativos que apontam para arquivos fora do site (CLAUDE.md, src/, etc.)
"""

import re


def on_page_markdown(markdown, page, config, files):
    # 1. Wikilinks [[Texto|Alias]] → Alias ; [[Texto]] → Texto
    def replace_wikilink(m):
        inner = m.group(1)
        if "|" in inner:
            _, alias = inner.split("|", 1)
            return alias.strip()
        return inner.strip()

    markdown = re.sub(r"\[\[([^\]]+)\]\]", replace_wikilink, markdown)

    # 2. Links quebrados — remove links que apontam para arquivos não-markdown
    # (CLAUDE.md, src/, .ts, .py, .js, Hub Projetos, etc.)
    broken_patterns = [
        r"\[([^\]]+)\]\([^)]*CLAUDE\.md[^)]*\)",
        r"\[([^\]]+)\]\([^)]*\.ts[^)]*\)",
        r"\[([^\]]+)\]\([^)]*\.js[^)]*\)",
        r"\[([^\]]+)\]\([^)]*src/[^)]*\)",
        r"\[([^\]]+)\]\([^)]*Hub%20Projetos[^)]*\)",
        r"\[([^\]]+)\]\([^)]*Hub Projetos[^)]*\)",
        r"\[([^\]]+)\]\([^)]*\.canvas[^)]*\)",
        r"\[([^\]]+)\]\([^)]*obsidian://[^)]*\)",
    ]
    for pattern in broken_patterns:
        # Substitui o link pelo texto do link (sem o href quebrado)
        markdown = re.sub(pattern, r"\1", markdown)

    return markdown
