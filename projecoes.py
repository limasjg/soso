"""Regras de projeção usadas no painel financeiro."""
from __future__ import annotations

import pandas as pd


TIPOS_FINANCEIROS = ("receita", "despesa", "investimento")


def calcular_projecao_anual(mensal: pd.DataFrame) -> dict[str, float]:
    """Projeta 12 meses a partir da média dos meses transcorridos.

    ``mensal`` deve conter uma linha por mês já transcorrido, inclusive linhas
    zeradas. Dessa forma, a projeção não fica artificialmente alta quando um
    mês não possui lançamentos de determinado tipo.
    """
    medias = {
        tipo: float(mensal[tipo].mean()) if tipo in mensal and not mensal.empty else 0.0
        for tipo in TIPOS_FINANCEIROS
    }
    projecao = {tipo: media * 12 for tipo, media in medias.items()}
    projecao["fluxo"] = projecao["receita"] - projecao["despesa"] - projecao["investimento"]
    return projecao
