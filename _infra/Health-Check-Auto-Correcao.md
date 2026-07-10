---
date: 2026-06-24
tags: [documentacao, infra, observabilidade]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]", "[[Central de Observabilidade]]"]
---
# Health Check + Auto-correção dos Automatismos da PD

> Sistema que vigia **todos os automatismos da PD** (crons, tasks Windows, serviços), detecta quando algum cai — inclusive **morte silenciosa** — tenta **se auto-corrigir** e **avisa no Slack**. Criado em 24/06/2026 (Linear **DEV-832**). Código no framework: `pd-framework/times/infra/workers/health_check/`.

## O problema que resolve

Sentry e Grafana avisam quando algo **dá erro**. Mas um job que simplesmente **para de rodar** não gera erro nenhum — morre calado. Foi assim que o `SyncDevDocsVault` ficou dias falhando e o brief diário do Luiz nunca chegava, sem ninguém perceber. Este sistema monitora se as coisas **estão rodando**, não só se quebraram.

## Como funciona (visão geral)

```
detecta → reconfirma → auto-corrige → avisa no Slack
```

Roda na máquina do Felipe (Windows) — único ponto que alcança os 3 ambientes: o próprio Windows, a VPS Master e a VPS Dev (via SSH). De hora em hora checa os ~24 automatismos; uma vez por dia (18h30) manda o resumo.

## O que ele faz quando algo cai

| Situação | Ação automática |
|---|---|
| **Serviço/processo parou** | Reconfirma que está mesmo parado → **reinicia sozinho**. Se falhar 2x, escala pra um humano. |
| **Bug de código** | Abre uma tarefa pro **agente de auto-correção** (Luiz/IA) resolver e mandar PR. |
| **Falso alarme** | Se na reconfirmação o serviço está vivo, **não faz nada** (não duplica processo). |

## Onde as notificações chegam (Slack)

| Canal | O que chega |
|---|---|
| `#saude-sistemas` | Resumo diário (18h30) + alerta na hora se um sistema crítico cair |
| `#diario` | O que o Luiz trabalhou no dia |
| `#rotina` | PRs prontos pra revisar, deploys |
| `#urgente` | Urgências (espelha no WhatsApp) |

App Slack: **Cadencia Bot**. Token guardado no 1Password (`Slack - API - Token`).

## Regra de ouro

**Todo automatismo novo (cron, task, serviço) tem que ser cadastrado no health check** — senão nasce "invisível" e ninguém saberá se ele parou. Cadastro pela skill **`/cobrir-no-healthcheck`** (sessão guiada, 1 minuto).

## Salvaguardas (por que é seguro deixar reiniciar sozinho)

1. Leitura falha do servidor = "não sei", não "está morto" (não dispara à toa).
2. Reconfirma na hora antes de reiniciar qualquer coisa.
3. Máximo 2 tentativas de restart, depois chama humano.
4. Só avisa quando o estado **muda** (não fica repetindo).

Essas proteções nasceram de um falso positivo real (o `mission_control` apareceu "morto" mas estava vivo) — pego ainda em modo observação, antes de ligar o automático.

## Validação

Testado de ponta a ponta em 24/06: um serviço de teste foi derrubado de propósito → o sistema detectou → reconfirmou → reiniciou → o serviço voltou. Tudo sozinho.

## Estado

- ✅ No ar: vigilância + auto-correção ligada + 4 canais Slack + agendamento
- ⏳ A fazer: deploys Vercel/Coolify no `#rotina`; ajustar o nome do bot nas mensagens

## Referências

- Linear: **DEV-832** (projeto *Central de Observabilidade + Auto-correção com IA*) — histórico completo
- Doc técnica (pros agentes): `pd-framework/times/infra/workers/health_check/README.md`
- [[Stack-Monitoramento-VPS-Master]] — observabilidade Grafana/Sentry da VPS (camada complementar)
