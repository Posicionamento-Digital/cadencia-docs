---
date: 2026-05-14
tags: [ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# /espelhar-repo-vps — Espelhar repo git numa VPS com deploy key

Automatiza o setup que faz uma VPS virar "ambiente de dev espelhado" do repositório GitHub. Funciona pra qualquer repo privado.

## Quando usar

- Vai colocar um dev externo trabalhando direto numa VPS (sem máquina local dele)
- Precisa de `git pull/push` funcionando autenticado, sem PAT manual, sem `gh auth login`
- A VPS já tem Claude Code instalado (ou você não se importa — a skill só configura git)

## Resultado final

Após rodar:
```bash
ssh root@<vps>
cd /root/<repo-name>
claude
git add . && git commit -m "..." && git push
```

Sem o dev ter conta no GitHub, sem PAT, sem login.

## Pré-requisitos

1. Acesso SSH à VPS como root
2. Repo GitHub existe (privado ou público)
3. Felipe é admin do repo (pra adicionar Deploy Key)
4. PAT no 1Password: `op://Serviços & Tools/Git Hub - ClaudeCode_Skill - Repo_VPS` (campo `credencial`)
   - Precisa ter `Administration: write` para repos pessoais
   - Para repos na org Posicionamento-Digital: PAT precisa de acesso à org também

## Fluxo

```
1. Coletar/confirmar inputs
2. SSH check: ping VPS + git + claude code
3. Gerar deploy key ed25519 na VPS (idempotente)
4. Adicionar deploy key no GitHub via PAT (automático) ou paste manual
5. Validar autenticação SSH GitHub
6. Backup envs/secrets se pasta já existir
7. Clone fresco via SSH
8. Restaurar envs
9. Configurar git user.name/email + ssh config
10. Validar push (commit dummy + revert)
11. Reportar pronto + comandos pro dev
```

## VPS Hostinger — acesso atual

- IP: `72.60.4.71`
- Usuário: `root`
- Acesso: senha via `op item get "Hostinger - Senha root" --vault Hosts --fields password --reveal`
- A chave `~/.ssh/hostinger_pd` está desatualizada — usar Python/paramiko com senha

## Nota sobre PAT e org GitHub

O PAT `Git Hub - ClaudeCode_Skill - Repo_VPS` funciona para repos no `felipeluissalgueiro` pessoal.
Para repos na org `Posicionamento-Digital`, precisa autorizar o PAT para a org ou adicionar deploy key manualmente.

## Histórico de uso

- 2026-05-11 — `felipeluissalgueiro/gci-go-whatsapp` em `72.60.4.71:/root/gci-go-whatsapp`
- 2026-05-13 — `felipeluissalgueiro/cadencia-app` em `72.60.4.71:/root/cadencia-app` ✅ (automático via PAT)
- 2026-05-13 — `Posicionamento-Digital/gci-go-whatsapp` pendente (PAT precisa acesso à org)

## Conteúdo completo da skill

Ver: `C:\Users\felip\.claude\skills\espelhar-repo-vps\SKILL.md`

## Notas Relacionadas
[[Credencial]] - [[Skill]] - [[Skills]]
