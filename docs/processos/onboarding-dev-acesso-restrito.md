# Onboarding de dev com acesso restrito (VPS Dev)

> Como um novo dev entra na VPS Dev conectado ao `pd-framework` real — com acesso só às pastas relevantes pro trabalho dele, e sem alçada de merge direto em `main` até ganhar confiança.

## Por que foi construído assim

GitHub não tem controle de leitura por pasta em nenhum mecanismo — deploy key, PAT fine-grained e collaborator liberam sempre o repo inteiro pra quem tem a credencial. Um servidor git próprio (Gitea/Forgejo ou espelho local) resolveria isso de forma real, mas é infraestrutura desproporcional ao ganho neste estágio.

A solução adotada aceita esse limite conscientemente: o boundary de acesso é por **configuração** (sparse-checkout + usuário de sistema sem privilégio), não uma garantia criptográfica. É adequado a um perfil de confiança direta (contratação por indicação, supervisão de perto) — não é defesa contra ameaça interna deliberada.

Um repo espelho separado (mesmo auto-sincronizado) foi descartado por violar DRY (`_core/CODING-PRINCIPLES.md` §1): duas representações do mesmo conhecimento divergem. A solução usa um único repo — um clone a mais, mesmo padrão já usado entre Windows/VPS Master/VPS Dev do Felipe.

## Stack

| Camada | Tecnologia |
|---|---|
| Host | VPS Dev (Hostinger) |
| Isolamento de usuário | Usuário Linux dedicado, sem grupo `sudo` |
| Filtro de pastas | `git sparse-checkout` (cone mode) + partial clone (`--filter=blob:none`) |
| Acesso remoto | SSH (Zed Remote SSH), chave dedicada por pessoa |
| Push pro GitHub | Deploy key dedicada por pessoa (`Contents: write` via SSH) |
| Abertura de PR | GitHub fine-grained PAT (escopo só no repo, `Contents`+`Pull requests: write`) |
| Credenciais operacionais | 1Password service account por pessoa, `.profile`, escopado a 1 vault |
| Gate de merge | Hook `stop-session-branch.py` — usuário sem alçada nunca mergeia `main` sozinho |

## Como funciona

```mermaid
flowchart TD
    A["Novo dev: usuário Linux criado<br/>(sem sudo)"] --> B["Clone /home/&lt;user&gt;/pd-framework<br/>sparse-checkout: só pastas liberadas"]
    B --> C["Chave SSH de login<br/>(1Password, vault Time)"]
    B --> D["Deploy key SSH dedicada<br/>(push only, registrada no GitHub)"]
    B --> E["PAT fine-grained<br/>(escopo só nesse repo, Contents+PR write)"]
    C --> F["Dev conecta via Zed Remote SSH"]
    F --> G["Trabalha normal — hook cria<br/>session/* automaticamente"]
    G --> H{"Usuário está em<br/>PR_ONLY_USERS?"}
    H -->|"Sim (novo dev)"| I["Publica branch no GitHub<br/>+ abre PR via gh pr create<br/>main local intocada"]
    H -->|"Não (Felipe)"| J["Merge direto em main local<br/>(fluxo original, sem mudança)"]
    I --> K["Felipe revisa e aprova o PR"]
    K --> L["Próximo git pull do dev<br/>já traz o que foi aceito"]
```

Os hooks `pretooluse-session-branch.py` + `stop-session-branch.py` funcionam sem alteração pra qualquer clone. A única mudança é um branch de comportamento em `stop-session-branch.py`: se `getpass.getuser()` está em `PR_ONLY_USERS`, `handle_pr_only_close()` roda no lugar do merge automático — publica a branch e chama `gh pr create`, sem tocar a `main` local.

## Decisões técnicas

- **Sparse-checkout + usuário sem sudo, não repo espelho separado.** Um repo/servidor git à parte violaria DRY (`_core/CODING-PRINCIPLES.md` §1). A solução é um único repo com um clone a mais.
- **PR-only sem exceção trivial.** Diferente do motor autônomo (`_core/PR-ESCALATION-MATRIX.md`), que tem classe de auto-merge pra mudanças triviais — o novo dev fica abaixo do tier "Coordenador" até ganhar histórico, toda mudança dele passa por aprovação humana.
- **1Password: service account por pessoa, não conta compartilhada genérica.** `.profile` com `OP_SERVICE_ACCOUNT_TOKEN` escopado a 1 vault, por pessoa — permite revogação isolada.
- **Repo `pd-framework` continua no GitHub pessoal, não migra pra org.** Migrar pra org exporia o repo à política de permissão padrão da org (outros membros podem ter acesso a todos os repos) — risco maior que o problema que resolveria.

## Gotchas & armadilhas

- **`sparse-checkout` não é garantia de segurança.** Credencial de leitura no GitHub (deploy key, PAT ou collaborator) alcança qualquer pasta do repo se o usuário forçar (`git sparse-checkout add`, ou clone novo sem sparse). O filtro evita exposição acidental, não bloqueia tentativa deliberada.
- **Nunca imprimir valor de credencial em comando de shell/log.** `grep`/`cat` num arquivo com token/chave ecoa o valor no output. Verificar existência/conteúdo sem exibir valor (`grep -c`, ou pipe arquivo→arquivo sem passar por stdout visível).
- **Deploy key ≠ chave de login.** Dois pares SSH diferentes — um autentica a VPS pro GitHub (push/pull), o outro autentica a pessoa pra VPS (login remoto). Nomear os itens 1Password de forma inequívoca evita confusão.
- **`gh pr create` exige token de API — SSH não basta.** SSH (deploy key) só cobre o protocolo git; abrir PR é chamada da API REST/GraphQL do GitHub.
- **Service account do 1Password não cria outro service account.** `op service-account create` só funciona autenticado como membro humano.
- **Item de categoria "SSH Key" criado via `op item create --template=` (import de chave existente) pode ficar malformado e ilegível — pelo próprio `op` CLI e pelo botão de download do app.** Sintoma: `op item get`/`op read` falham com `"private_key" isn't a field`, mesmo o item existindo e tendo o campo visível na UI. Causa: a categoria SSH Key espera campos derivados (`public_key`, `fingerprint`, `key_type`) que o app preenche automaticamente ao gerar a chave, mas que um template CLI mínimo não popula corretamente. **Fix:** sempre criar o item deixando o 1Password gerar a chave (`op item create --category="SSH Key" --ssh-generate-key=ed25519`), nunca importar uma chave pronta via template JSON. Pra extrair a chave depois, usar `op read "op://<vault>/<item>/private key?ssh-format=openssh" -o arquivo.key` (sem esse query param, o valor vem truncado/sem o wrapper PEM).
- **Nunca copiar/colar conteúdo de chave privada em editor de texto (Notepad etc.) pra criar o arquivo manualmente.** Introduz CRLF/BOM, e o SSH rejeita com `error in libcrypto` ou `invalid format`. Entregar sempre como arquivo — download direto do 1Password, ou anexo de arquivo (não texto colado) se for por WhatsApp/chat.
- **Windows costuma adicionar `.txt` ao salvar um anexo sem extensão** (WhatsApp Desktop, "Salvar como" etc.) — o arquivo vira `vps_dev_<user>.txt` mas o `IdentityFile` do `~/.ssh/config` aponta pro nome sem extensão. Sintoma: SSH/cliente (Zed) nunca tenta publickey (sem log de `Failed publickey` no server), cai direto pra prompt de senha — que não existe, looping infinito. Diagnóstico rápido e não-destrutivo: `Get-ChildItem $HOME\.ssh` no PowerShell da pessoa, comparar contra o `IdentityFile` do config.
- **`sshd_config.d/*.conf` só é aplicado se `sshd_config` principal tiver a diretiva `Include /etc/ssh/sshd_config.d/*.conf`.** Encontrado na VPS Dev (2026-07-13): dois arquivos em `sshd_config.d/` (`50-cloud-init.conf` com `PasswordAuthentication yes`, `60-cloudimg-settings.conf` tentando `no`) nunca eram lidos — não existe `Include` no `sshd_config` principal desse host. O valor efetivo vinha do **default do OpenSSH pra `PasswordAuthentication`, que é `yes`** (não `no` como se assume). Login por senha ficou habilitado no servidor inteiro sem ninguém perceber. Verificar sempre com `sudo sshd -T | grep -i passwordauth` (config efetiva real), nunca confiar no que os arquivos individuais dizem. Fix: diretiva direto no `sshd_config` principal (não em `conf.d/`, que é ignorado nesse host) + `systemctl reload ssh` + revalidar login por chave com `ssh -o BatchMode=yes` antes de dar como resolvido (garante que não trava ninguém fora).

## Como operar

```bash
# Ver quais pastas um clone restrito enxerga
git -C /home/<user>/pd-framework sparse-checkout list

# Adicionar/remover usuário do fluxo PR-only
# editar _core/hooks/stop-session-branch.py → PR_ONLY_USERS = {"renan", ...}

# Verificar credencial GitHub configurada pro usuário
sudo -u <user> -H gh auth status

# Verificar acesso ao vault 1Password do usuário
sudo -u <user> -H bash -c 'source ~/.profile && op vault list'
```

## FAQ

**Por que não criar um GitHub collaborator pro novo dev?**
Collaborator dá leitura do repo inteiro — mesma exposição que deploy key ou PAT. Não existe collaborator restrito a pastas específicas.

**Por que não usar 1Password Connect em vez de service account?**
Connect resolve rate limit em alto volume (múltiplos serviços de produção). No volume atual (poucas pessoas, uso interativo), é infraestrutura extra sem ganho.

**O que acontece se o dev tentar acessar uma pasta fora do sparse-checkout?**
Não existe localmente — o clone nunca baixou o conteúdo (partial clone `--filter=blob:none`). Precisaria rodar `git sparse-checkout add <pasta>` deliberadamente, que busca do GitHub (funciona se a credencial tiver acesso de leitura ao repo).

**Como o dev recebe credenciais operacionais (Supabase, Vercel etc.) no dia a dia?**
Vault 1Password compartilhado (service account no `.profile`, escopado só a esse vault) — `op item get "<item>" --vault "<vault>"`. Nunca por mensagem/chat.

**O dev não consegue baixar a chave de login do 1Password — o que fazer?**
Verificar se o item não está malformado (ver gotcha acima) antes de qualquer outra hipótese: `op item get "<item>" --vault "Time" --format json` — se der erro `"private_key" isn't a field`, o item está quebrado e precisa ser recriado (nunca corrigido por edição manual). Rotacionar: gerar item novo com `--ssh-generate-key`, atualizar `authorized_keys` do usuário na VPS com a chave pública nova, validar login end-to-end antes de entregar. Entrega final sempre como arquivo (nunca texto colado).
