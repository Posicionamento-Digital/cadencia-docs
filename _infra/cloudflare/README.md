# Cloudflare — Espelhamento

## Objetivo
Espelhar todas as zonas DNS da conta do Michael para a conta do Felipe, **sem ativar** (sem trocar nameservers no registrador). As zonas ficam dormentes na conta destino, prontas pra ativar se necessário.

## Credenciais
- `.env` (gitignored) — tokens de origem (Michael) e destino (Felipe)
- **Importante:** rotacionar os tokens da conta do Michael após o uso (eles foram expostos em chat)

## Scripts
- `espelhar.py` — script principal. Lê zonas da origem, cria na destino, copia records. Idempotente.
- `backup/` — gerado pelo script. Contém `.bind.txt` e `.json` por zona.

## Como rodar
```bash
cd "Hub Projetos/Credenciais/Cloudflare"
python espelhar.py
# Output detalhado por zona. Re-execução é segura (skip do que já existe).
```

## O que o script FAZ
1. Lista zonas da conta origem (Michael)
2. Pra cada zona:
   - Backup BIND + JSON em `backup/<dominio>/`
   - Verifica se já existe na conta destino
   - Se não existe: cria zona (status `pending` — sem ativar)
   - Importa todos os records DNS

## O que o script NÃO faz (replicar manual depois)
- Page Rules
- Workers / Pages bindings
- Firewall rules / WAF customizações
- SSL/TLS settings (Full strict, etc)
- Email Routing
- Bulk redirects
- Cache configurations
- Always Use HTTPS / Auto Rewrites

Pra cada zona crítica, abrir as duas contas lado a lado e replicar settings manualmente.

## Status pós-espelhamento
- Zonas continuam **inativas** na conta destino (Cloudflare mostra "Pending Nameserver Update")
- DNS público continua respondendo via conta origem (do Michael) — nada quebra
- Pra ativar: trocar nameservers no registrador (registro.br/etc) pros NS da conta destino
- Após ativação: aguardar 24-48h de propagação, manter ambas zonas idênticas, depois deletar da conta origem

## Rotação pós-uso (OBRIGATÓRIO)
1. Revogar `CF_SRC_API_TOKEN` na conta Michael: My Profile → API Tokens → Roll/Delete
2. Revogar `CF_SRC_GLOBAL_KEY` na conta Michael: My Profile → API Tokens → View Global API Key → Roll
3. Apagar valores deste `.env` ou substituir por placeholders
