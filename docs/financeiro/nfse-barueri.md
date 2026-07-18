---
title: NFS-e Barueri — Sistema Operacional
tags: [financeiro, canon]
---

# NFS-e Barueri — Sistema operacional

> Sistema de emissão NFS-e da AXIS (Barueri/SP). Inclui portal manual, WebService SOAP, MCP automatizado e skill local.
> **Fonte da verdade operacional:** `ClaudeCode/Finanças/CLAUDE.md`.

> 🚨 **ATENÇÃO AO EMITIR — código de serviço (orientação Talissa, 17/06/2026):** a empresa é tributada no DAS como **treinamento (8599, ~6%)**. Ao emitir NF, **usar o código alinhado ao DAS (treinamento)** que a Talissa indicar — **não usar 115013000 (TI) por padrão**. Emitir como TI e declarar treinamento gera divergência que aciona fiscalização (e a reforma de set/2026 vai cruzar nota × DAS automaticamente). O código padrão GCI abaixo está sob revisão da contadora. Ver regra completa em `politica-fiscal.md` → "Regras vigentes (Talissa)".

---

## Identidade emitente

| Campo | Valor |
|---|---|
| **CNPJ** | 62.650.127/0001-03 |
| **Razão Social** | AXIS CONSULTORIA & EMPRESARIAL LTDA |
| **Inscrição Municipal** | 4BR4009 |
| **Município** | Barueri/SP (IBGE 3505708) |

---

## Caminhos de emissão (3 opções)

### 1. Portal manual (fallback)
- URL: https://www.barueri.sp.gov.br/nfe/
- Credencial: CPF responsável (consultar `ClaudeCode/Finanças/CLAUDE.md`)
- Fluxo: login → "Enviar RPS em Lote" → upload `.txt` PMB004

### 2. WebService SOAP (integração direta)
- Endpoint: `https://www.barueri.sp.gov.br/nfeservice/wsrps.asmx`
- Namespace: `http://www.barueri.sp.gov.br/nfe` (sem barra final)
- Limite: 50 RPS por lote
- **Autenticação:** Certificado Digital A1 (PFX) — NÃO aceita login/senha
- **Certificado:** `ClaudeCode/Finanças/certificado digital/AXIS...pfx`
- **Validade:** 11/09/2026 (renovar até esta data)
- **Senha PFX:** consultar `Hub Projetos/Credenciais/mapa-1password.md` (mover do CLAUDE.md original pro 1Password — pendência)

### 3. MCP barueri-nfse (recomendado)
- Instalado em: `ClaudeCode/Finanças/skill_gerar_rps/mcp/barueri_nfse_mcp.py`
- Configurado em: `~/.claude/.mcp.json`
- 10 ferramentas (`barueri_emitir_nfse`, `barueri_enviar_lote`, `barueri_status_lote`, `barueri_listar_lotes`, `barueri_baixar_retorno`, `barueri_processar_retorno`, `barueri_baixar_nfse_xml`, `barueri_enviar_nfse_email`, `barueri_enviar_lote_emails`, `barueri_testar_conexao`)

---

## Formato técnico (SOAP / RPS)

### Campos obrigatórios no MensagemXML

```
InscricaoMunicipal: 4BR4009
CPFCNPJContrib:     62650127000103
VersaoSchema:       1
```

**NUNCA usar Login/Senha no XML** — autenticação é via certificado SSL.

### Schemas XSD oficiais

- Download: `C:/tmp/schemas_out/XML_RPS_Schemas_V01/`
- Doc oficial: https://www.barueri.sp.gov.br/nfe/Manuais/XML_RPS_Versao_01.pdf
- Cópia no repo: `times/financeiro/context/fiscal/NFE_Manual.pdf` + `RPS_ListaErros.pdf`

### Formato PMB004 (arquivo manual)

Script: `ClaudeCode/Finanças/skill_gerar_rps/scripts/gerar_rps.py`

```bash
python3 gerar_rps.py \
  --nfs nfs_lote.json \
  --remessa 005 \
  --data YYYYMMDD \
  --template rps/enviados/RPS_AXIS_GCI_GO_20260325_v3.txt \
  --out rps/enviados/RPS_AXIS_CLIENTE_YYYYMMDD_v1.txt
```

**Regras críticas (não negociar):**
- Registros Tipo 2: exatamente **1970 bytes**
- Line endings: **CRLF (`\r\n`)** — LF causa rejeição (erros 900/901)
- `FIXED_BLOCK_478_503`: exatamente 25 bytes

---

## Sequência de remessas e RPS (estado atual)

| Remessa | RPS início | RPS fim | Data | Cliente |
|---------|------------|---------|------|---------|
| 001 | 1 | 5 | — | — |
| 002 | 6 | 10 | 25/03/2026 | GCI GO |
| 003 | 11 | 25 | 30/03/2026 | GCI GO (lote anterior) |
| 004 | 26 | 56 | 31/03/2026 | GCI GO (individual por mês) |

**Próxima remessa: 005, próximo RPS: 57**

⚠️ **Atualizar `ClaudeCode/Finanças/CLAUDE.md` (fonte) após cada envio aprovado** — remessa e RPS são únicos, nunca repetir.

---

## Clientes recorrentes — Grupo GCI GO

| Apelido | CNPJ | Cidade/UF | IBGE | Email contábil |
|---|---|---|---|---|
| Oral Gold Ceilândia | 55.942.954/0001-05 | Brasília/DF | 5300108 | contabil@clinicasinteligentes.com.br |
| Parque Anhanguera | 56.045.279/0001-84 | Goiânia/GO | 5208707 | administracao@yacp.com.br |
| Escritório/Holding | 51.039.604/0001-82 | Goiânia/GO | 5208707 | legalizaqcao.go@gci.com.br |
| Plano Piloto | 57.993.993/0001-67 | Brasília/DF | 5300108 | contabil@clinicasinteligentes.com.br |
| Castelo Branco | 57.443.744/0001-06 | Goiânia/GO | 5208707 | contabil@clinicasinteligentes.com.br |

**Valor mensal padrão:** R$ 1.800,00 (180000 centavos) por clínica.

---

## Clientes recorrentes — NoCode StartUp (Treinamentos IA)

| Apelido | CNPJ | Cidade/UF | IBGE | Email fiscal |
|---|---|---|---|---|
| NoCode StartUp | 49.612.202/0001-83 | Barueri/SP | 3505708 | fiscal@nocodestartup.io |

**Razão social:** No-Code Start-Up Negócios Digitais Ltda
**Decisor:** Matheus Castelo Branco Monho · fiscal@nocodestartup.io · +55 48 99970-0506
**Dados completos no 1Password:** vault Clientes → "NoCode StartUp — Dados Fiscais [Cliente]"
**Valor:** variável por emissão (treinamentos IA sob demanda — não recorrente fixo).
**Código serviço:** ⚠️ aguardar definição da Talissa (treinamento, NÃO 115013000/TI).

---

## Erros conhecidos — não repetir

| Erro | Causa | Fix |
|---|---|---|
| 900/901 | Registro Tipo 2 com tamanho ≠ 1970 bytes | Verificar `FIXED_BLOCK_478_503` = 25 bytes exatos |
| 900/901 | Line endings LF | Usar `b'\r\n'.join(linhas)` no gerador |
| RPS duplicado | Remessa nova ausente do mapeamento | Adicionar entrada no dict antes de gerar |
| E0017 "Versão 0" | MCP usa Login/Senha direto sem VersaoSchema | Usar formato XSD: VersaoSchema=1 + MensagemXML com CDATA |
| E0018 "Schema incompatível" | Campos Login/Senha não existem no XSD | Usar InscricaoMunicipal + CPFCNPJContrib |
| E0001 "Certificado inválido" | SOAP chamado sem certificado A1 | Carregar PFX e montar ssl_ctx com cert+key PEM |
| HTTP 500 NFePDF.ashx | Endpoint PDF da Prefeitura instável | Gerar PDFs localmente com `fpdf2` via `gerar_pdf_nfse.py` |

---

## Fluxo completo testado (31/03/2026)

```
1. Gerar arquivo RPS  → gerar_rps.py → .txt PMB004
2. Enviar lote        → SOAP com certificado (ou portal manual)
3. Listar lotes       → NFeLoteListarArquivos → pegar NomeArqRetorno
4. Baixar retorno     → NFeLoteBaixarArquivo → salvar .TXT
5. Parse retorno      → regex auth_code + nfse_num + cnpj_tomador
6. Gerar PDFs         → gerar_pdf_nfse.py (fpdf2) → 1 PDF por NF
7. Copiar PDFs        → pasta do cliente
8. Enviar emails      → barueri_enviar_lote_emails (MCP) → tomadores
```

### Atalho MCP (sem arquivo)

```
barueri_emitir_nfse(dados) → protocolo
barueri_status_lote(protocolo) → aguardar "Aprovado"
barueri_baixar_retorno(protocolo, salvar_em=".../retornos/Ret_YYYYMMDD.TXT")
barueri_processar_retorno(caminho_retorno) → lista de NFS-e com auth_code
barueri_enviar_nfse_email(auth_code, nfse_num, email, razao) → enviado
```

---

## Pendências

- [ ] Mover senha do PFX do `Finanças/CLAUDE.md` pro 1Password (vault `databases`)
- [ ] Renovar certificado A1 até 11/09/2026
- [ ] Refatorar MCP `barueri_nfse_mcp.py` que ainda tinha bug Login/Senha (verificar se corrigido)
- [ ] Onboarding de novos clientes não-GCI no fluxo (códigos serviço diferentes?)

---

## Refs

- `politica-fiscal.md` — regime + retenções
- `../skills/emitir-nfse.md` — skill que opera este sistema
- `../context/fiscal/NFE_Manual.pdf` — manual oficial Barueri (cópia)
- `../context/fiscal/RPS_ListaErros.pdf` — lista de erros oficial (cópia)
- Fonte: `ClaudeCode/Finanças/CLAUDE.md` + `skill_gerar_rps/`
- Script testado: `ClaudeCode/Finanças/skill_gerar_rps/scripts/barueri_soap.py`
