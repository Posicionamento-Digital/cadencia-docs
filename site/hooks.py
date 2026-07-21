"""
MkDocs hooks — limpeza automática de artefatos do Obsidian e links quebrados.

Roda no evento `page_markdown` (antes do parse) para:
1. Remover wikilinks [[...]] — vira texto simples
2. Remover links relativos que apontam para arquivos fora do site
3. Remover links relativos .md que não existem na coleção de docs do MkDocs
"""

import re
import posixpath


def on_page_markdown(markdown, page, config, files, **kwargs):
    # 1. Wikilinks [[Texto|Alias]] → Alias ; [[Texto]] → Texto
    def replace_wikilink(m):
        inner = m.group(1)
        if "|" in inner:
            _, alias = inner.split("|", 1)
            return alias.strip()
        return inner.strip()

    markdown = re.sub(r"\[\[([^\]]+)\]\]", replace_wikilink, markdown)

    # 2. Links explicitamente quebrados (arquivos fora do site)
    broken_patterns = [
        r"\[([^\]]+)\]\([^)]*CLAUDE\.md[^)]*\)",
        r"\[([^\]]+)\]\([^)]*\.ts[^)]*\)",
        r"\[([^\]]+)\]\([^)]*\.js[^)]*\)",
        r"\[([^\]]+)\]\([^)]*\.sql[^)]*\)",
        r"\[([^\]]+)\]\([^)]*src/[^)]*\)",
        r"\[([^\]]+)\]\([^)]*Hub%20Projetos[^)]*\)",
        r"\[([^\]]+)\]\([^)]*Hub Projetos[^)]*\)",
        r"\[([^\]]+)\]\([^)]*\.canvas[^)]*\)",
        r"\[([^\]]+)\]\([^)]*obsidian://[^)]*\)",
    ]
    for pattern in broken_patterns:
        markdown = re.sub(pattern, r"\1", markdown)

    # 3. Links .md relativos que não existem na coleção de docs
    # Constrói set de src_paths conhecidos
    known = {f.src_path for f in files}

    current_dir = posixpath.dirname(page.file.src_path)

    def check_md_link(m):
        text = m.group(1)
        href = m.group(2)
        # Ignora links absolutos, âncoras e externos
        if href.startswith(("http", "#", "/")):
            return m.group(0)
        # Só verifica links que terminam em .md
        path_part = href.split("#")[0]
        if not path_part.endswith(".md"):
            return m.group(0)
        # Resolve relativo ao diretório da página atual
        resolved = posixpath.normpath(posixpath.join(current_dir, path_part))
        if resolved not in known:
            return text  # strip link, mantém texto
        return m.group(0)

    markdown = re.sub(r"\[([^\]]*)\]\(([^)]+)\)", check_md_link, markdown)

    return markdown
