# Lê data/pix_mensal.csv e data/pix_anual.csv, imprime os números citados em docs/04 e gera os gráficos.
# Uso: python scripts/analise.py   (precisa de pandas e matplotlib)
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# keep_default_na=False: a categoria "null" (campo vazio na origem) não pode virar NaN
mensal = pd.read_csv("data/pix_mensal.csv", keep_default_na=False)
anual = pd.read_csv("data/pix_anual.csv", keep_default_na=False)
Path("graficos").mkdir(exist_ok=True)

AZUL, CINZA, LARANJA, VERDE = "#118DFF", "#9AA5B1", "#E66C37", "#2E9E6B"
plt.rcParams.update(
    {
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
    }
)
data_mes = lambda ano_mes: pd.to_datetime(ano_mes.astype(str), format="%Y%m")

# P1: quanto o Pix cresceu e o que aconteceu com o valor médio de cada transação?
total = mensal[mensal["dimensao"] == "total"].set_index("ano_mes")
total["ticket"] = total["valor_reais"] / total["quantidade"]
print("Quantidade mensal ago/2026 vs dez/2020: x", round(total.loc[202608, "quantidade"] / total.loc[202012, "quantidade"], 1))
print("Valor mensal ago/2026 vs dez/2020: x", round(total.loc[202608, "valor_reais"] / total.loc[202012, "valor_reais"], 1))
print("Ticket médio: dez/2020 R$", round(total.loc[202012, "ticket"]), "| mínimo R$", round(total["ticket"].min()), "em", total["ticket"].idxmin(), "| ago/2026 R$", round(total.loc[202608, "ticket"]))
por_ano = total.assign(ano=total.index // 100).groupby("ano")[["valor_reais", "quantidade"]].sum()
por_ano["ticket"] = por_ano["valor_reais"] / por_ano["quantidade"]
print("\nPor ano (2020 e 2026 incompletos):\n", por_ano.assign(valor_tri=por_ano["valor_reais"] / 1e12, qtd_bi=por_ano["quantidade"] / 1e9).round(2)[["valor_tri", "qtd_bi", "ticket"]])

x = data_mes(total.index.to_series())
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
ax1.plot(x, total["quantidade"] / 1e9, color=AZUL, lw=2.5)
ax1.set_ylabel("Transações por mês (bilhões)")
ax1.set_title("O Pix passou de 125 milhões a 7,4 bilhões de transações por mês")
ax2.plot(x, total["ticket"], color=LARANJA, lw=2.5)
ax2.set_ylabel("Valor médio por transação (R\\$)")
ax2.set_ylim(0)
ax2.set_title("O valor médio caiu de R\\$ 858 para cerca de R\\$ 430")
fig.tight_layout()
fig.savefig("graficos/01_volume_e_valor_medio.png", dpi=130)
plt.close(fig)

# P2: sazonalidade da quantidade (dezembro vs novembro, janeiro vs dezembro)
q = total["quantidade"]
print("\nVariação da quantidade: dezembro vs novembro | janeiro seguinte vs dezembro")
for ano in range(2021, 2026):
    print(ano, f"{q[ano * 100 + 12] / q[ano * 100 + 11] - 1:+.1%}", f"{q[(ano + 1) * 100 + 1] / q[ano * 100 + 12] - 1:+.1%}")


def participacao(dimensao, coluna="quantidade"):
    g = mensal[mensal["dimensao"] == dimensao].pivot_table(index="ano_mes", columns="categoria", values=coluna, aggfunc="sum").fillna(0)
    return g.div(g.sum(axis=1), axis=0)


# P3: quem paga a quem (natureza da transação)
nat = participacao("natureza")
print("\nNatureza, participação na quantidade:\n", (nat.loc[[202012, 202112, 202312, 202512, 202608], ["P2P", "P2B", "B2P", "B2B"]] * 100).round(1))
nat_valor = participacao("natureza", "valor_reais")
print("Natureza, participação no valor em ago/2026:\n", (nat_valor.loc[202608, ["B2B", "P2P", "P2B", "B2P"]] * 100).round(1).to_dict())

fig, ax = plt.subplots(figsize=(9, 5))
x3 = data_mes(nat.index.to_series())
ax.plot(x3, nat["P2P"] * 100, color=CINZA, lw=2.5, label="pessoa para pessoa (P2P)")
ax.plot(x3, nat["P2B"] * 100, color=AZUL, lw=2.5, label="pessoa para empresa (P2B)")
ax.plot(x3, nat["B2P"] * 100, color=LARANJA, lw=2, label="empresa para pessoa (B2P)")
ax.plot(x3, nat["B2B"] * 100, color=VERDE, lw=2, label="empresa para empresa (B2B)")
ax.set_ylabel("% das transações")
ax.set_title("Pagar uma empresa passou a ser o uso mais comum")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("graficos/02_natureza.png", dpi=130)
plt.close(fig)

# P4: como o pagamento é iniciado (chave, QR Code, manual)
ini = participacao("forma_iniciacao")
ini = ini[ini.index >= 202107]  # até jun/2021 a forma de iniciação quase não era informada (em jun/2021 só 13%)
print("\nForma de iniciação, participação na quantidade:\n", (ini.loc[[202112, 202312, 202512, 202608], ["DICT", "QRDN", "QRES", "MANU"]] * 100).round(1))

fig, ax = plt.subplots(figsize=(9, 5))
x4 = data_mes(ini.index.to_series())
ax.plot(x4, ini["DICT"] * 100, color=CINZA, lw=2.5, label="chave Pix (DICT)")
ax.plot(x4, ini["QRDN"] * 100, color=AZUL, lw=2.5, label="QR Code dinâmico (QRDN)")
ax.plot(x4, ini["MANU"] * 100, color=LARANJA, lw=2, label="dados digitados (MANU)")
ax.plot(x4, ini["QRES"] * 100, color=VERDE, lw=2, label="QR Code estático (QRES)")
ax.set_ylabel("% das transações")
ax.set_title("O QR Code dinâmico passou a chave como forma mais usada")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("graficos/03_forma_de_iniciacao.png", dpi=130)
plt.close(fig)

# P5: quem paga (idade, só pessoas físicas) e de onde (região)
idade = anual[anual["dimensao"] == "idade_pagador"].pivot_table(index="ano", columns="categoria", values="quantidade", aggfunc="sum").fillna(0)
idade = idade.drop(columns=["Nao se aplica", "Nao informado", "null"], errors="ignore")
print("\nIdade do pagador (só PF com idade informada), % da quantidade:\n", (idade.div(idade.sum(axis=1), axis=0).loc[[2021, 2023, 2025]] * 100).round(1).T)
regiao = anual[anual["dimensao"] == "regiao_pagador"].pivot_table(index="ano", columns="categoria", values="quantidade", aggfunc="sum").fillna(0)
regiao = regiao.drop(columns=["Nao informado", "null"], errors="ignore")
print("\nRegião do pagador, % da quantidade:\n", (regiao.div(regiao.sum(axis=1), axis=0).loc[[2021, 2025]] * 100).round(1).T)
fluxo = anual[(anual["dimensao"] == "regiao_pagador_recebedor") & (anual["ano"] == 2025)].set_index("categoria")["quantidade"]
fluxo = fluxo[~fluxo.index.str.contains("Nao informado|null")]
mesma = sum(v for k, v in fluxo.items() if k.split(">")[0] == k.split(">")[1])
print("\nTransações em 2025 em que pagador e recebedor estão na mesma região:", f"{mesma / fluxo.sum():.1%}")
