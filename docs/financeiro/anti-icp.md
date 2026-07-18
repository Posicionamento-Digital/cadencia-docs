---
title: Anti-ICP Financeiro
tags: [financeiro, canon]
---

# Anti-ICP Financeiro — Quem NÃO atender

> Cliente que destrói margem, gera trabalho desproporcional ou paga mal não é cliente — é prejuízo.
> Esta é a lente do Financeiro complementando o anti-ICP do Comercial.

---

## Princípio

ICP financeiro ≠ ICP comercial. Cliente pode ter perfil comercial perfeito (segmento certo, dor certa, budget aparente) mas ser **anti-ICP financeiro** se:
- Histórico de inadimplência
- Pede desconto agressivo já na primeira proposta
- Quer custom heavy que estoura margem
- Gera retrabalho desproporcional ao ticket
- Não respeita regras de cobrança

**Bárbara tem poder de veto financeiro** mesmo se Comercial aprovou.

---

## Sinais de alerta (red flags)

### Antes do fechamento
- 🚩 Pede desconto > 20% na primeira reunião
- 🚩 Não envia documentação societária (CNPJ, contrato social, CPF responsável)
- 🚩 CNPJ recente sem histórico (< 6 meses) sem garantia
- 🚩 Pede mudanças contratuais nas cláusulas de inadimplência
- 🚩 Negocia o método de pagamento como se fosse vantagem (boleto após entrega, etc)
- 🚩 Quer "começar e ver" sem contrato assinado

### Durante a operação
- 🚩 Atraso > 7 dias na 1ª parcela (sinaliza padrão)
- 🚩 Reclamação não-substanciada como ferramenta de barganha por desconto
- 🚩 Pede serviço fora do escopo sem aceitar aditivo
- 🚩 Múltiplos contatos cobrando entregas que não estão no escopo
- 🚩 Cliente do tipo "rato de suporte" (consumo de tempo desproporcional ao MRR)

### No churn
- 🚩 Cancela com cobrança em aberto + nega o débito
- 🚩 Faz chargeback sem contato prévio

---

## Veto financeiro — quando Bárbara barra

Bárbara recomenda **não fechar** se:

1. **Inadimplência confirmada** — cliente tem histórico em outras empresas (consultar referências comerciais quando ticket > R$ 10k/mês)
2. **CNPJ irregular** — Receita Federal status "inapto" / "baixado" / "suspenso"
3. **Desconto pedido > política** sem justificativa estratégica
4. **Customização que zera margem** — análise do escopo mostra custo entrega > 70% do contrato
5. **Cliente que paga "depois da entrega"** — risco assumido pela PD

Se Comercial discordar do veto, vai pra `/financeiro-debate` com Felipe-CEO mediando.

---

## Política de inadimplência (cliente ativo)

| Atraso | Ação |
|---|---|
| D+1 a D+7 | Notificação automática (gateway) |
| D+7 | Cobrança ativa (email + WhatsApp) — Bárbara aciona |
| D+15 | Suspensão de acesso / pausa de entregas |
| D+30 | Encerramento contratual + envio pra protesto / negativação |
| D+60+ | Considerar como perda contábil — registrar em `decisions.md` |

Renegociação só com aprovação Bárbara, escrita, e SEMPRE com cliente assinando aditivo.

---

## Recuperação (cliente que já fechou e virou anti-ICP)

Quando perceber que o cliente já fechado virou anti-ICP financeiro:

1. **Documentar** sinais em `decisions.md` (datas, episódios, custo de atendimento)
2. **Calcular LHI atual** — se < 1, está destruindo valor
3. **Decidir** via `/financeiro-debate`:
   - Renegociar contrato (aumentar preço / reduzir escopo)
   - Encerrar contrato no fim do ciclo (não renovar)
   - Encerrar antecipadamente (se cláusula permite)

**Não há vergonha em demitir cliente.** Cliente anti-ICP ocupa capacidade que serviria cliente ICP.

---

## Quem NÃO atender por princípio

- Jogos de azar, apostas, criptos de duvidosa procedência (risco regulatório)
- Esquemas piramidais / MLM agressivos
- Política partidária (separa marca)
- Cliente com histórico de processos contra fornecedores de serviços similares
- Cliente que pediu desconto agressivo, foi recusado, e voltou meses depois sem reconhecer o critério original

---

## Refs

- `precificacao-margens.md` — política de desconto
- `ciclo-faturamento.md` — política inadimplência
- `contratos-modelo.md` — cláusulas que dão poder de encerramento
- Time Comercial: `times/comercial/foundation/` — anti-ICP comercial (perspectiva diferente)
- `dre-structure.md` — impacto do anti-ICP na margem
