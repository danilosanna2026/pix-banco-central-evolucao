# Baixa as estatísticas do Pix da API de dados abertos do Banco Central, mês a mês,
# soma por dimensão e salva data/pix_mensal.csv e data/pix_anual.csv.
# Os arquivos já estão no repositório; rode este script só para refazer a coleta.
# Uso: python scripts/coleta.py   (leva alguns minutos: ~70 chamadas, de 2 mil a 17 mil linhas cada)
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

BASE = "https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/"
PRIMEIRO_MES = 202011  # o Pix começou em 16/11/2020
ULTIMO_MES = 202608

# dimensões somadas mês a mês e dimensões somadas por ano
MENSAIS = {
    "total": None,
    "tipo_pagador_recebedor": ("PAG_PFPJ", "REC_PFPJ"),
    "natureza": ("NATUREZA",),
    "forma_iniciacao": ("FORMAINICIACAO",),
}
ANUAIS = {
    "idade_pagador": ("PAG_IDADE",),
    "regiao_pagador": ("PAG_REGIAO",),
    "regiao_pagador_recebedor": ("PAG_REGIAO", "REC_REGIAO"),
}


def meses():
    for ano in range(PRIMEIRO_MES // 100, ULTIMO_MES // 100 + 1):
        for mes in range(1, 13):
            ano_mes = ano * 100 + mes
            if PRIMEIRO_MES <= ano_mes <= ULTIMO_MES:
                yield ano_mes


def baixar_mes(ano_mes):
    # a função EstatisticasTransacoesPix exige o parâmetro Database; o $filter garante só o mês pedido
    parametros = urllib.parse.urlencode(
        {"@Database": f"'{ano_mes}'", "$filter": f"AnoMes eq {ano_mes}", "$top": 200000, "$format": "json"},
        quote_via=urllib.parse.quote,
        safe="@'$",
    )
    url = f"{BASE}EstatisticasTransacoesPix(Database=@Database)?{parametros}"
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(url, timeout=120) as resposta:
                return pd.DataFrame(json.load(resposta)["value"])
        except Exception as erro:
            print(f"  {ano_mes}: tentativa {tentativa + 1} falhou ({erro})")
            time.sleep(5)
    raise RuntimeError(f"não consegui baixar {ano_mes}")


def somar(df, colunas):
    # soma valor e quantidade por categoria; campo vazio vira o texto "null"
    if colunas is None:
        return pd.DataFrame({"categoria": ["total"], "valor": [df["VALOR"].sum()], "quantidade": [df["QUANTIDADE"].sum()]})
    chaves = df[list(colunas)].astype(object).where(df[list(colunas)].notna(), "null")
    categoria = chaves.astype(str).agg(">".join, axis=1)
    soma = df.groupby(categoria)[["VALOR", "QUANTIDADE"]].sum().reset_index()
    soma.columns = ["categoria", "valor", "quantidade"]
    return soma


def agregar(mensal_por_mes):
    # mensal_por_mes: {ano_mes: dataframe cru do mês}
    linhas_mensais, linhas_anuais = [], []
    for ano_mes, df in mensal_por_mes.items():
        for dimensao, colunas in MENSAIS.items():
            s = somar(df, colunas)
            s["valor"] = s["valor"].round(0).astype("int64")
            s.insert(0, "dimensao", dimensao)
            s.insert(0, "ano_mes", ano_mes)
            linhas_mensais.append(s)
        for dimensao, colunas in ANUAIS.items():
            s = somar(df, colunas)
            s.insert(0, "dimensao", dimensao)
            s.insert(0, "ano", ano_mes // 100)
            linhas_anuais.append(s)
    mensal = pd.concat(linhas_mensais)
    mensal = mensal[(mensal["valor"] != 0) | (mensal["quantidade"] != 0)]
    anual = pd.concat(linhas_anuais).groupby(["ano", "dimensao", "categoria"], as_index=False).sum()
    anual["valor"] = anual["valor"].round(0).astype("int64")
    anual = anual[(anual["valor"] != 0) | (anual["quantidade"] != 0)]
    colunas = ["dimensao", "categoria", "valor_reais", "quantidade"]
    mensal = mensal.rename(columns={"valor": "valor_reais"})[["ano_mes"] + colunas]
    anual = anual.rename(columns={"valor": "valor_reais"})[["ano"] + colunas]
    return mensal, anual


if __name__ == "__main__":
    dados = {}
    for ano_mes in meses():
        print("baixando", ano_mes)
        dados[ano_mes] = baixar_mes(ano_mes)
    mensal, anual = agregar(dados)
    Path("data").mkdir(exist_ok=True)
    mensal.to_csv("data/pix_mensal.csv", index=False)
    anual.to_csv("data/pix_anual.csv", index=False)
    print(len(mensal), "linhas mensais,", len(anual), "linhas anuais")
