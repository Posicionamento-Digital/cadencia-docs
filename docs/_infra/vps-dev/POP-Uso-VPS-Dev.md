---
date: 2026-05-22
tags: [infra, vps, pop, processo, dev, time]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]"]
---
# POP — Uso da VPS de Desenvolvimento

**Responsável:** Dev (dev externo ou qualquer colaborador com acesso)
**Gatilho de entrada:** Início de qualquer sessão de trabalho na VPS
**Objetivo:** Garantir que todo trabalho na VPS segue o fluxo correto — da conexão ao fechamento da issue — sem deixar processo solto, credencial exposta ou sessão sem log.

---

## Visão Geral do Fluxo

```
Conectar na VPS
      ↓
Abrir tmux
      ↓
Iniciar issue no Linear (/linear-start-issue)
      ↓
Codar com Claude Code
      ↓
Commit + Push
      ↓
Fechar issue (/linear-close-issue)
      ↓
Registrar sessão (/log-sessao)
      ↓
Desconectar (Ctrl+B, D)
```

---

## Etapa 1 — Conectar na VPS

**Objetivo:** Estabelecer conexão SSH segura com a chave correta.

```bash
ssh -i ~/.ssh/hostinger_dev_luiz luiz@2.24.117.172
```

- [ ] Entrou no diretório `/home/luiz/`
- [ ] Sem mensagem de erro de autenticação

> **Se der erro de conexão:** ver [[Infra/VPS-Hostinger/VPS-Dev/Acesso-VPS-Dev-Luiz#Problemas comuns]]

---

## Etapa 2 — Abrir tmux (obrigatório)

**Objetivo:** Proteger o trabalho contra quedas de conexão. Qualquer processo iniciado dentro do tmux continua rodando mesmo se o SSH cair.

```bash
# Primeira conexão do dia — nova sessão
tmux

# Reconectando após queda ou pausa
tmux attach
```

- [ ] Está dentro de uma janela tmux (barra inferior visível)

| Ação | Atalho |
|---|---|
| Desconectar sem matar | `Ctrl+B, D` |
| Nova janela | `Ctrl+B, C` |
| Próxima janela | `Ctrl+B, N` |
| Dividir horizontal | `Ctrl+B, "` |

> **Nunca trabalhe fora do tmux.** Se esquecer e a conexão cair no meio de um processo longo (build, clone, install), recomeça do zero.

---

## Etapa 3 — Iniciar a issue

**Objetivo:** Garantir que o trabalho está vinculado a uma issue do Linear antes de começar a codar.

```bash
# Dentro do diretório do repo correto:
cd ~/gci-go-whatsapp   # ou o repo da issue

# Iniciar a issue
claude
# Dentro do Claude Code:
/linear-start-issue
```

O `/linear-start-issue` vai:
1. Listar as issues In Progress atribuídas a você
2. Fazer `git checkout` da branch da issue escolhida
3. Marcar a issue como **In Progress** no Linear

- [ ] Branch criada e ativa (`git branch` mostra `feature/pdl-XX`)
- [ ] Issue marcada como In Progress no Linear

> **Se a issue não tiver branch:** significa que não passou pelo `/linear-planejar-issue`. Falar com Felipe antes de codar.

---

## Etapa 4 — Codar com Claude Code

**Objetivo:** Executar a issue usando Claude Code como par de programação.

```bash
claude
```

### Boas práticas durante a sessão

| Situação | O que fazer |
|---|---|
| Precisa de credencial | `/credencial` — nunca hardcodar token no código |
| Travou em bug | `/debug-polya` — framework estruturado antes de tentar na força |
| Quer revisar antes de fechar | `/gemini-review` ou `/claude-review` |
| Precisa validar script antes de subir | `/validar-deploy-vps` |
| Descobriu algo que pode quebrar depois | `/registrar-incidente` |

### Regras de código

- [ ] Nenhuma credencial hardcoded — usar `op item get` ou variável de ambiente
- [ ] Nenhum `console.log` ou `print` com valores sensíveis
- [ ] Código testável localmente antes do push

---

## Etapa 5 — Commit e Push

**Objetivo:** Registrar o trabalho feito com mensagem padronizada e enviar para o repositório.

```bash
git add .
git commit -m "feat: PDL-XX descrição objetiva do que foi feito"
git push origin feature/pdl-XX
```

### Padrão de mensagem de commit

| Prefixo | Quando usar |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `refactor:` | Melhoria sem mudar comportamento |
| `docs:` | Apenas documentação |
| `chore:` | Config, deps, CI |

- [ ] Mensagem inclui `PDL-XX` (número da issue)
- [ ] Push feito sem erro
- [ ] Nunca commitou arquivo `.env`, token ou senha

---

## Etapa 6 — Fechar a issue

**Objetivo:** Marcar a issue como concluída no Linear e registrar o fechamento com o commit correto.

```bash
# Dentro do Claude Code:
/linear-close-issue
```

O `/linear-close-issue` vai:
1. Verificar critério de aceite da issue
2. Fazer commit final com `Closes PDL-XX`
3. Push para a branch
4. Marcar issue como **Done** no Linear

- [ ] Issue marcada como Done no Linear
- [ ] Commit de fechamento feito com `Closes PDL-XX`
- [ ] Felipe notificado se necessário (Linear notifica automaticamente)

> **Não feche issue sem ter validado o critério de aceite.** Se estiver incerto, deixar In Progress e falar com Felipe.

---

## Etapa 7 — Registrar a sessão

**Objetivo:** Deixar rastro do que foi feito para consulta futura e para Felipe acompanhar.

```bash
# Dentro do Claude Code:
/log-sessao "título descritivo do que foi feito"
```

Exemplos de título:
- `"PDL-45 — filtro de horário no pipeline Lara"`
- `"PDL-52 e PDL-53 — refactor worker Cadência"`
- `"debug conexão CRM — encontrado bug na autenticação do tenant"`

- [ ] Log criado em `Rotina/sessions-log/YYYY-MM-DD/`
- [ ] Título reflete o que foi feito, não só o número da issue

---

## Etapa 8 — Desconectar

**Objetivo:** Encerrar a sessão sem matar processos em background.

```bash
# Desconectar do tmux sem matar (processos continuam)
Ctrl+B, D

# Sair do SSH
exit
```

- [ ] Usou `Ctrl+B, D` (não `exit` dentro do tmux)
- [ ] Nenhum processo importante ficou rodando sem querer

---

## Referência Rápida — Skills do dia a dia

| Skill | Quando usar |
|---|---|
| `/linear-start-issue` | Sempre antes de codar |
| `/linear-close-issue` | Ao terminar uma issue |
| `/linear-planejar-issue` | Issue nova sem branch definida |
| `/credencial` | Precisou de API key ou token |
| `/debug-polya` | Bug travado há mais de 30 min |
| `/gemini-review` | Revisão antes do PR (rápido, gratuito) |
| `/claude-review` | Revisão profunda com Opus |
| `/validar-deploy-vps` | Script que vai rodar em produção |
| `/registrar-incidente` | Algo quebrou e você aprendeu como consertar |
| `/log-sessao` | Final de qualquer sessão |
| `/ja-fiz` | Ver o que já entregou na semana |
| `/status` | Ver o que está pendente no projeto |

---

## Referência Rápida — CLIs disponíveis

```bash
# Após source ~/.profile (carregado automaticamente ao conectar)
claude        # Claude Code
codex         # OpenAI Codex CLI
gemini        # Gemini CLI
railway       # Railway CLI
vercel        # Vercel CLI
gh            # GitHub CLI
op            # 1Password CLI
docker        # Docker (sem sudo)
```

---

## O que NÃO fazer

| Proibido | Motivo |
|---|---|
| Trabalhar fora do tmux | Perde trabalho se cair a conexão |
| Hardcodar credenciais no código | Risco de vazar via git |
| Fazer push direto na `main` sem fechar issue | Quebra rastreabilidade do Linear |
| Usar `sudo` | Não tem permissão; pedir pro Felipe se precisar |
| Acessar `/home/felipe/` | Isolamento de usuário |
| Fechar issue sem validar critério de aceite | Felipe vai reabrir |
| Deixar sessão sem `/log-sessao` | Felipe não consegue acompanhar |

---

## Problemas comuns

| Problema | Causa provável | Solução |
|---|---|---|
| SSH não conecta | Chave errada ou IP mudou | `ssh -i ~/.ssh/hostinger_dev_luiz luiz@2.24.117.172 -v` |
| CLI não encontrado | PATH não carregado | `source ~/.profile` |
| `op item get` falha | SA expirou | Falar com Felipe para renovar |
| Branch não existe | Issue sem planejamento | `/linear-planejar-issue` primeiro |
| Push negado | Branch protegida ou conflito | `git pull origin feature/pdl-XX` e resolver conflito |
| Docker: permission denied | Usuário fora do grupo | Falar com Felipe (`usermod -aG docker luiz`) |

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Dev/Acesso-VPS-Dev-Luiz]] · [[Infra/VPS-Hostinger/VPS-Dev/VPS-Dev-Documentacao-Tecnica]] · [[Time/Luiz/Manual-VPS-Dev]]
