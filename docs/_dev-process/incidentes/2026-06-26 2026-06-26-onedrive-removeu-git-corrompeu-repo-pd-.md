---
type: source
source_kind: incidente
date: 2026-06-26
entities: ["[[PD Framework]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---

# 2026-06-26_onedrive-removeu-git-corrompeu-repo-pd-framework

# OneDrive removeu o `.git` ao desmarcar a sync — repo principal do pd-framework corrompido (recuperado com histórico)

**Data:** 2026-06-26
**Severidade:** Alta
**Projeto:** pd-framework (Infra — armazenamento / git / OneDrive)
**Duração:** ~1h de pânico + diagnóstico + recuperação completa. Zero perda final.
**Tags:** #infra #git #onedrive #corrupcao #recuperacao #silenciosa #dev-865

## O que aconteceu

No meio de uma sessão de trabalho intensa (runtime-agnosticismo: F1/F2/Modo B/DEV-885 + paralelamente DEV-868 Ondas 1-3 e DEV-866), o git parou de funcionar no repo `C:\Users\felip\OneDrive\…\pd-framework`: `fatal: not a git repository`. O VS Code passou a mostrar **~10k pending changes**.

Causa: o Felipe **desmarcou a sincronização da pasta Documentos no OneDrive** ("choose folders" / parar de sincronizar). O OneDrive então começou a **remover a cópia local dos arquivos** (eles passam a existir só na nuvem). Isso atingiu o **`.git` do repo principal**: os arquivos soltos `HEAD`, `config`, `index` foram **removidos do disco** e as subpastas de `objects`/`refs` viraram **placeholders Files-On-Demand** (ReparsePoint). Sem `HEAD`/`config`, o git não reconhece o diretório como repositório.

Os "10k pending changes" do VS Code eram **deleções feitas pelo OneDrive**, não trabalho — commitá-las teria apagado metade do framework.

## Causa raiz

- **OneDrive + git são incompatíveis sob remoção de sync.** Desmarcar a pasta faz o OneDrive deletar/desidratar arquivos locais; o `.git` é um diretório de muitos arquivos pequenos críticos (HEAD/config/index/objects), e perder qualquer um quebra o repo. É o **DEV-865 escalado**: antes corrompia worktrees; agora atingiu o `.git` principal.
- **Agravante de processo:** o trabalho da sessão **nunca foi pushado** pro GitHub. Os hooks Stop mergeiam na `main` **local** mas não dão push. O último push fora `2c7d31a` (~13:30 BRT); ~70 commits de 26/06 (DEV-868 Ondas 1-3, DEV-866, agnóstico) viviam **só no `.git` local** — exatamente o que corrompeu.

## Por que não foi detectado antes

- A remoção da sync é silenciosa e gradual — arquivos somem aos poucos. O git só "quebra" quando o arquivo crítico certo é removido.
- Sem push automático, não havia cópia remota do trabalho do dia — a corrupção do `.git` local era um single point of failure.

## Impacto

- Repo principal inutilizável por git. Risco real de perder ~70 commits de trabalho não-pushado (DEV-868 Ondas 1-3 inteiras, DEV-866, runtime-agnóstico).
- **Mitigado a zero:** os `.git/objects` (pack 122MB + 4197 objetos) e os `refs/heads/*` continuavam **legíveis** (materializados), então o histórico era recuperável.

## Recuperação (o que funcionou)

1. **Estancar:** encerrar o OneDrive (parar a remoção em andamento).
2. **Proteger (read-only no `.git` morto):** copiar `.git` inteiro pra fora do OneDrive (`C:\temp\…-rescue\.git`). Pack e loose objects copiaram íntegros.
3. **Reconstruir refs:** recriar `HEAD` (`ref: refs/heads/main`) e `config` mínimos no resgate → `git fsck` ok, `git log` legível. Confirmado `refs/heads/main = 9f42ea9` com as Ondas 1-3.
4. **Clone limpo:** `git clone` do GitHub em `C:\dev\pd-framework` (**fora do OneDrive**) = base íntegra até `2c7d31a`.
5. **Reaplicar o trabalho** que só existia em memória/contexto (a versão limpa do agnóstico) por cima do clone → 4 commits → push.
6. **Unificar os históricos:** `git fetch` dos objetos resgatados → `git merge` do `9f42ea9` (65 commits do morto) no `main`. **113 arquivos sem conflito** (todo o DEV-868/866/evo entrou íntegro); **4 docs agnósticos** em conflito resolvidos a favor da versão limpa. Merge `6c3aca3` pushado.

Resultado: **GitHub com histórico completo dos dois lados, 3097 arquivos, zero perda.** Repo de trabalho migrado pra `C:\dev\pd-framework`.

## Prevenção (lições)

1. **Repos git NUNCA dentro do OneDrive.** Mover todos os repos ativos pra fora (ex.: `C:\dev\`). O OneDrive é pra documentos, não pra `.git`. (Reforça e escala o DEV-865.)
2. **Push automático ao fim de sessão.** O hook Stop mergeia local mas não pusha — o trabalho do dia fica sem cópia remota. Adicionar `git push` ao encerramento (ou um cron de push) elimina o single point of failure. **Se o trabalho estivesse pushado, a corrupção do `.git` local seria irrelevante.**
3. **Nunca commitar "10k pending changes" em massa** sem inspecionar a natureza — deleções em massa = sinal de corrupção/sync, não de trabalho.
4. **Ao desmarcar sync do OneDrive numa pasta com repos:** mover os repos pra fora ANTES, ou a remoção desidrata o `.git`.
5. **Reavaliar a junction de worktrees (DEV-894)** — virou urgente com o OneDrive fora.

## Refs

- DEV-865 (worktrees fora do OneDrive — origem da incompatibilidade OneDrive×git)
- DEV-894 (reavaliar estratégia worktree/OneDrive — escalar prioridade)
- Resgates: `C:\temp\onedrive-git-rescue\` + `C:\temp\pd-onedrive-rescue\` (manter até validação 100%)
- Commits da recuperação: `6b116cc`…`ff1b5e5` (reaplicação) + merge `6c3aca3` (unificação)
