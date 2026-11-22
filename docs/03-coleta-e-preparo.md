# 03 · Coleta e preparo

Script: `scripts/coleta.py`. Saída: `data/pix_mensal.csv` e `data/pix_anual.csv`.

## O que o script faz
1. Para cada mês de nov/2020 a ago/2026, chama a função `EstatisticasTransacoesPix` com `$filter=AnoMes eq <mês>` (a API devolve todos os meses misturados se o filtro faltar).
2. Soma `VALOR` e `QUANTIDADE` por dimensão.
3. Grava em formato "longo": uma linha por mês (ou ano), dimensão e categoria.

## Decisões
| Problema | Decisão |
|---|---|
| Campo vazio (`null`) em alguma coluna | vira a categoria `"null"`; ao ler o CSV, usar `keep_default_na=False`, senão o pandas converte para NaN |
| Existe a categoria `"Nao disponivel"` / `"Nao informado"` | mantida; só é tirada nas contas em que atrapalha (idade, região) |
| 740 mil linhas é muito para o repositório | guardo só as somas por dimensão, que respondem às perguntas |
| Valores em reais com centavos | arredondados para reais inteiros (diferença irrelevante em somas de bilhões) |
| Idade só existe para pessoa física (PJ aparece como "Nao se aplica") | na análise de idade, tiro "Nao se aplica", "Nao informado" e "null" |

## Conferências
- Para cada mês, a soma da quantidade de cada dimensão fecha com o total.
- A forma de iniciação só passa a ser informada a partir de jul/2021 (em jun/2021 só 13% das transações trazem o campo). Antes disso, a análise dessa dimensão não vale.

## Limites conhecidos
- Somar por dimensão impede cruzar duas dimensões que não guardei (por exemplo idade por região).
- O valor médio (valor / quantidade) é uma média simples e é puxado para cima por transações entre empresas.
