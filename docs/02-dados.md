# 02 · Dados

**Fonte:** API de dados abertos do Pix, do Banco Central do Brasil (serviço Olinda, `Pix_DadosAbertos`). Função usada: `EstatisticasTransacoesPix`. O conjunto de dados está no portal dadosabertos.bcb.gov.br, com licença ODbL (Open Database License).

**Período:** nov/2020 a ago/2026. Novembro de 2020 é um mês incompleto (o Pix começou em 16/11). Os anos de 2020 (2 meses) e 2026 (8 meses) são parciais.

**Estrutura:** cada linha da API é uma combinação de mês, tipo de pessoa do pagador e do recebedor (PF/PJ), região e faixa de idade de cada um, forma de iniciação, natureza e finalidade, com o `VALOR` e a `QUANTIDADE` de transações. Dá entre 2 mil e 17 mil linhas por mês, uns 740 mil no total, valores já somados pelo Banco Central (não há transação individual nem pessoa identificada).

**Campos usados**

| Campo | Significado |
|---|---|
| `VALOR` | soma dos valores das transações, em reais (sem correção pela inflação) |
| `QUANTIDADE` | número de transações |
| `NATUREZA` | quem paga a quem: P2P (pessoa para pessoa), P2B (pessoa para empresa), B2P, B2B, e as combinações com governo (G) |
| `FORMAINICIACAO` | `DICT` chave Pix, `QRDN` QR Code dinâmico, `QRES` QR Code estático, `MANU` dados digitados, `INIC` iniciador de pagamento. Os códigos `APDN`, `APES` e `AUTO` aparecem com participação muito pequena e ficam só com o código |
| `PAG_PFPJ`, `REC_PFPJ` | pagador e recebedor: pessoa física (PF) ou jurídica (PJ) |
| `PAG_IDADE` | faixa de idade do pagador (só faz sentido para pessoa física) |
| `PAG_REGIAO`, `REC_REGIAO` | região do pagador e do recebedor |

**O que ficou no repositório:** os dados já somados, em `data/pix_mensal.csv` (total, tipo de pessoa, natureza e forma de iniciação, mês a mês) e `data/pix_anual.csv` (idade, região do pagador e fluxo entre regiões, ano a ano). O detalhe linha a linha é pesado demais para o repositório; o `scripts/coleta.py` refaz a coleta.
