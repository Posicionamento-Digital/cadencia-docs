---
date: 2026-05-18
tags: [cadencia, skill, onboarding, white, glove, agencia, direct, pdl, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Karina Vieira]]", "[[qualidade]]"]
---
# /criar-tenant-agencia — White-Glove Onboarding

## O que é e quando usar

Skill CLI que Felipe usa para provisionar um tenant completo no Cadencia para qualquer cliente — agência, direct, teste ou parceria. O cliente não preenche nada — Felipe configura tudo à mão com dados muito mais ricos do que o onboarding self-service permite.

**Usar quando:**
- Qualquer cliente que não vá pelo onboarding self-service: agência, direct, teste, parceria
- Felipe tem briefing detalhado (presencial ou formulário Tally)
- O cliente precisa de Soul.md rico para o chat de ideias funcionar desde o primeiro dia

**NÃO usar quando:**
- Cliente vai fazer onboarding self-service normalmente
- Dados insuficientes para preencher os blocos B-F com qualidade

## Os 7 Blocos (resumo)

| Bloco | Campos | O que captura |
|---|---|---|
| A | 1-4 | Conta: nome, email, senha, plano — 5 opções sem default (growth_pro/profissional/essencial/trial/personalizado) |
| B | 5-11 | Identidade: sexo, WhatsApp, tipo PF/PJ, empresa, nicho, profissão, detalhe da profissão |
| C | 12-17 | Visual: rosto, fotos (min 3), logo, sub-preset (15 opções), cores e fontes custom |
| D | 18-20 | Profiling cliente: Big5 (personalidade), DPR (diferencial), COM (comunicação) |
| E | 21-24 | Profiling audiência: público-alvo, por que escolhe, o que valoriza, como decide comprar |
| F | 25-27 | Conteúdo: restrições, temas prioritários (5-10), história do cliente |
| G | 28-30 | Ativações: flag_chat_ideas, enviar WhatsApp (Felipe informa destinatário), gerar primeiras 5 ideias |

## Quickstart

```
/criar-tenant-agencia
```

Ou: "cria conta para [nome]" / "provisiona tenant para [nome]" / "onboarding white-glove para [nome]" / "cria user no cadencia para [cliente]"

A skill apresenta o Bloco A e aguarda cada bloco antes de executar qualquer coisa.

## Os 11 Passos de Execução

1. Credenciais via 1Password CLI
2. Criar usuário em `auth.users` (email já confirmado, sem envio de email)
3. Provisionar tabelas: `tenants`, `users`, `user_tenant_roles`, `tenant_onboarding` (fase 3), `tenant_plans`
4. Popular `tenant_config` com 30+ campos JSONB
5. Inserir `profile_responses` (6 registros) + `tenant_profile` (consolidado, confidence=0.9)
6. Upload de logo e fotos para Supabase Storage
7. Workers Coolify VPS Master: dossier (~30s) + visual-identity + editorials + sub-preset-choice
8. Gerar Soul.md via endpoint admin; se falhar, gera manualmente com dados do briefing
9. Gerar primeiras 5 ideias (se `GERAR_IDEIAS = true`)
10. Verificação final — query consolidada em todas as tabelas
11. Pergunta destinatário do WhatsApp (Bloco G) → mensagem para aprovação → `/mandar-whatsapp`

## Regras críticas

- Coletar todos os blocos A-G antes de executar — a skill não roda sem dados completos
- Senha nunca exposta no relatório — sempre `***`
- Verificar email duplicado antes de criar — erro silencioso no auth
- Se workers falharem, documentar quais passos falharam e oferecer continuar manualmente
- Soul.md manual > automático quando há briefing rico
- Não declarar "entregue" sem validar login funcional, ao menos 1 post gerado e chat operacional

## Issues relacionadas

- [[PDL-106]] — criar tenants white-glove para Karina Vieira (3 clientes)
- [[PDL-101]] — white-glove onboarding — definição e escopo

## Link para o chat de ideias (ativado neste onboarding)

- [[Brief-Feature-Tenho-Uma-Ideia]] — contexto da Karina e origem da demanda pelo chat

## Referências técnicas

- Skill fonte: `C:\Users\felip\.claude\skills\criar-tenant-agencia\SKILL.md`
- Doc completa no repo: `docs/features/criar-tenant-agencia/README.md`
- Wiki HTML: `docs/wiki/criar-tenant-agencia.html`

## Notas Relacionadas
[[Readme]] - [[Documentar]] - [[Skill]] - [[Brief]] - [[Criar-Tenant-Agencia]]
