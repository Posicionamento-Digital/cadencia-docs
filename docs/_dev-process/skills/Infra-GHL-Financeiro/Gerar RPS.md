---
date: 2026-05-14
tags: [skill, infra, financeiro, nfse, rps, barueri, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Gerar RPS

Gera arquivo TXT de RPS em lote para conversão em NFS-e no portal da Prefeitura de Barueri. Layout V4.2 (PMB004).

## Quando usar
"/gerar-rps". Argumentos: data de emissão (AAAAMMDD) + número RPS inicial.

---

## Conteúdo da Skill

```markdown
---
name: gerar-rps
description: Gera arquivo TXT de RPS em lote para conversão em NFS-e no portal da Prefeitura de Barueri. Lê a planilha de clientes e gera o arquivo conforme layout V4.2 (PMB004) com registros Tipo 1, 2, 4 e 9.
argument-hint: "[data-emissao AAAAMMDD] [numero-rps-inicial]"
---

# Skill: Gerador de Arquivo RPS em Lote — Barueri (Layout V4.2 / PMB004)

## Objetivo

Gerar o arquivo TXT de RPS para upload no sistema NFS-e da Prefeitura de Barueri, convertendo RPS em NFS-e em lote. O arquivo segue o layout V4.2 (versão PMB004).

## Fluxo de Execução

### 1. Coletar parâmetros

Pergunte ao usuário os dados que não foram fornecidos como argumento:
- **Data de emissão** (`$0`): formato AAAAMMDD
- **Número do RPS inicial** (`$1`): número inteiro
- **Quais clientes incluir**: todos da planilha ou apenas alguns específicos
- **Meses de referência**: quais meses cobrar de cada cliente

### 2. Ler a base de clientes

Ler o arquivo `clientes/base_clientes_rps.xlsx` da pasta `ClaudeCowork_Finanças` usando Python + openpyxl.

A planilha (aba "Clientes RPS") contém a partir da linha 2 (linha 1 = cabeçalho):

| Coluna | Campo | Descrição |
|--------|-------|-----------|
| A | ativo | S = gerar RPS / N = ignorar |
| B | apelido | Nome curto do cliente |
| C | razao_social | Razão social (sem acentos, maiúsculo) |
| D | tipo_doc | CPF ou CNPJ |
| E | cpf_cnpj | Só números (14 dígitos CNPJ / 11 dígitos CPF) |
| F | email_nfe | E-mail para receber a NF-e |
| G-N | endereco | Rua, numero, complemento, bairro, cidade, uf, cep, ibge |
| O | valor_mensal | Valor mensal em R$ |
| P | descricao_servico | Texto base para discriminação |

**Filtro padrão**: usar apenas clientes com `ativo = S` e `tipo_doc = CNPJ`.

### 3. Dados fixos do prestador

```
Razão Social:     AXIS CONSULTORIA & EMPRESARIAL LTDA
CNPJ:             62.650.127/0001-03
Inscrição Municipal: 4BR4009
Endereço:         AVENIDA COPACABANA, 439, SALA APTO 176
Bairro:           DEZOITO DO FORTE EMPRESARIAL / ALPHAVILL
Cidade:           BARUERI / SP
CEP:              06472001
Código IBGE:      3505708
Código Serviço:   010401220
Simples Nacional: 3 (ME/EPP)
```

### 4. Geração da discriminação do serviço

Formato padrão (sem acentos — usar ASCII puro):
```
Prestacao de servicos de consultoria em tecnologia, implementacao de automacao e agentes de intelig|encia artificial referente aos meses de [MESES]. Contrato de prestacao de servicos continuados - [RAZAO SOCIAL] / CNPJ [CNPJ]. ISS recolhido pelo prestador via DAS - Simples Nacional.
```

Regras:
- Máximo 1000 caracteres
- Usar `|` (pipe) como quebra de linha a cada 100 caracteres no máximo
- Não colocar `|` na última linha
- Remover acentos e caracteres especiais (usar apenas ASCII)

### 5. Estrutura do arquivo TXT

```
1 [Cabeçalho - Registro Tipo 1]        ← 1 único no arquivo
2 [Detalhe - Registro Tipo 2]          ← 1 por nota
4 [ADN - Registro Tipo 4]              ← 1 por nota (logo após o Tipo 2)
...
9 [Rodapé - Registro Tipo 9]           ← 1 único no arquivo
```

Codificação: Latin-1 (ISO-8859-1) | Quebra de linha: CR+LF (ASCII 13 + ASCII 10)

### 6. Layout dos registros

#### Registro Tipo 1 — Cabeçalho (25 chars)

| Pos | Tam | Campo | Valor |
|-----|-----|-------|-------|
| 1 | 1 | Tipo Registro | 1 |
| 2-8 | 7 | Inscrição Contribuinte | 4BR4009 |
| 9-14 | 6 | Versão Layout | PMB004 |
| 15-25 | 11 | ID Remessa | AAAAMMDDxxx (data + sequencial 3 dígitos) |

#### Registro Tipo 2 — Detalhe (1970 chars)

Contém: tipo RPS "RPS  ", série "A   ", número RPS (zeros à esquerda), data RPS, hora "090000", situação "E", código serviço "010401220", local prestação "1", end. local serviço (prestador), qtd "000001", valor × 100, tomador (CNPJ, razão social, endereço), e-mail, discriminação do serviço.

**Regras de preenchimento:**
- Campos Texto: preencher com espaços à direita
- Campos Numérico: preencher com zeros à esquerda
- Valor monetário: valor em centavos (R$10.800,00 = 000000001080000)

#### Registro Tipo 4 — ADN (531 chars)

Contém: tipo 4, enquadramento SN "3", regime apuração "1", país local serviço "000", IBGE local prestação "3505708", IBGE tomador, código NBS "115021000", indOp "100301", cClassTrib "000001", CST IBS/CBS "000".

#### Registro Tipo 9 — Rodapé (38 chars)

| Pos | Tam | Campo | Valor |
|-----|-----|-------|-------|
| 1 | 1 | Tipo Registro | 9 |
| 2-8 | 7 | Total Linhas | soma de todas as linhas |
| 9-23 | 15 | Valor Total Serviços | soma dos valores×100 |
| 24-38 | 15 | Valor Total Retenções | 000000000000000 |

### 7. Gerar o arquivo

Usar Python para gerar o arquivo TXT. O script deve:
1. Ler a planilha com openpyxl
2. Montar cada registro seguindo o layout acima rigorosamente
3. Validar que cada registro tem o tamanho exato (Tipo 1=25, Tipo 2=1970, Tipo 4=531, Tipo 9=38)
4. Gravar com encoding Latin-1 e quebras CR+LF
5. Salvar na pasta `ClaudeCowork_Finanças/rps/enviados/` com nome `RPS_AXIS_[DATA]_v1.txt`

### 8. Validação pós-geração

Após gerar, executar validação automática:
- Verificar tamanho de cada linha
- Verificar que o total de linhas no rodapé está correto
- Verificar que o valor total no rodapé bate com a soma dos valores individuais

### 9. Apresentar resultado

```
Arquivo gerado: RPS_AXIS_AAAAMMDD_v1.txt

| # | RPS | Tomador | Valor |
|---|-----|---------|-------|
| 1 | 0000000011 | STUDIO ORAL PREMIUM LTDA | R$ 10.800,00 |

Total: X notas — R$ XX.XXX,XX
ID Remessa: AAAAMMDDXXX

Faça upload no portal: www.barueri.sp.gov.br/nfe
Menu: Conversão de RPS em Lote → Enviar Arquivo
```

## Referências

- Layout RPS V4.2: https://www.barueri.sp.gov.br/nfe/Manuais/RPS_Layout.pdf
- Lista de Erros: https://www.barueri.sp.gov.br/nfe/Manuais/RPS_ListaErros.pdf
- Guia Conversão Lote: https://www.barueri.sp.gov.br/nfe/Manuais/Guia_Conversao_RPS_Lote.pdf
```

## Notas Relacionadas
[[Infra-GHL-Financeiro/Credencial]]
