import pandas as pd
import pytest

from projecoes import calcular_projecao_anual


def test_projeta_ano_com_base_na_media_dos_meses_transcorridos():
    mensal = pd.DataFrame(
        {
            "receita": [15_000] * 8,
            "despesa": [8_000] * 8,
            "investimento": [2_000] * 8,
        }
    )

    projecao = calcular_projecao_anual(mensal)

    assert projecao == {
        "receita": 180_000,
        "despesa": 96_000,
        "investimento": 24_000,
        "fluxo": 60_000,
    }


def test_considera_meses_sem_movimento_na_media():
    mensal = pd.DataFrame(
        {
            "receita": [10_000, 0],
            "despesa": [4_000, 0],
        }
    )

    projecao = calcular_projecao_anual(mensal)

    assert projecao["receita"] == pytest.approx(60_000)
    assert projecao["despesa"] == pytest.approx(24_000)
    assert projecao["investimento"] == 0
    assert projecao["fluxo"] == pytest.approx(36_000)
