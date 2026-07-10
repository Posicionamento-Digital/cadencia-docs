---
date: 2026-05-21
tags: [linux, infraestrutura, aprendizado, dns, webhooks]
moc: "[[MOC-IA-Tecnologia]]"
---

# Domínio apontando para VPS — DNS e HTTPS

## O que significa

Quando você acessa um site, o navegador converte o nome (`cadencia.ia.br`) em um endereço IP (`72.60.4.71`) via DNS, e aí faz a conexão. "Apontar um domínio pra VPS" = criar um registro DNS que diz: "quando alguém acessar `dev.posicionamentodigital.com.br`, manda pro IP da VPS dev".

## Por que importa na VPS de desenvolvimento

Alguns serviços externos só conseguem chamar de volta via URL — não aceitam IP puro. Precisam de URL com HTTPS:

- **WhatsApp Business API** — quando chega mensagem, faz POST para `https://seusite.com/webhook`
- **GHL webhooks** — idem
- **Supabase realtime/webhooks** — idem

Se o projeto recebe webhooks de serviços externos, precisa de URL pública com HTTPS na VPS dev.

## Quando NÃO precisa de domínio

Se o desenvolvimento é só local — rodar código, ver resultado, fazer push — IP puro via SSH basta. Sem domínio, sem HTTPS.

## Como configurar quando precisar

1. Criar registro DNS tipo A apontando para o IP da VPS dev (no painel do provedor de domínio — Cloudflare, Registro.br, etc.)
2. Instalar Nginx, Traefik ou usar o Coolify para terminar SSL automaticamente
3. Apontar o webhook do serviço externo para a nova URL

## Não precisa decidir no provisionamento

Domínio e HTTPS são independentes da configuração base da VPS. A VPS sobe sem domínio, e o registro DNS + SSL entram depois, quando o projeto exigir.

## Notas Relacionadas

[[IA-Tecnologia/2026-05-19 Linux FHS — onde cada coisa mora no sistema de arquivos]] · [[IA-Tecnologia/Playbook-Proteger-VPS-DDoS-SYNFlood]]