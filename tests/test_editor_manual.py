import pytest
from streamlit.testing.v1 import AppTest


APP = """
import pandas as pd
import streamlit as st
from app import editor_com_salvamento_manual

for nome in ('despesas', 'receitas', 'investimentos'):
    if nome not in st.session_state:
        st.session_state[nome] = pd.DataFrame({'Descricao': ['Inicial'], 'Valor': [10.0]})

    def salvar(tabela, nome=nome):
        if (tabela['Valor'] <= 0).any():
            raise ValueError('Valor deve ser positivo.')
        st.session_state[nome] = tabela.copy()
        st.session_state['gravacoes'] = st.session_state.get('gravacoes', 0) + 1

    editor_com_salvamento_manual(st.container(), st.session_state[nome], nome, salvar, {})
"""


@pytest.mark.parametrize('indice,nome', enumerate(('despesas', 'receitas', 'investimentos')))
def test_edicoes_so_sao_gravadas_ao_salvar_e_nao_se_repetem(indice, nome):
    app = AppTest.from_string(APP).run()
    assert not app.exception
    assert len(app.button) == 3
    assert all(botao.label == 'Salvar' for botao in app.button)

    edicoes = {
        'edited_rows': {0: {'Descricao': 'Alterada', 'Valor': 20.0}},
        'added_rows': [{'Descricao': 'Nova', 'Valor': 30.0}],
        'deleted_rows': [],
    }
    app.session_state[f'{nome}_v0'] = edicoes
    app.run()
    assert not app.exception
    assert app.session_state[nome]['Valor'].tolist() == [10.0]
    assert 'gravacoes' not in app.session_state

    # AppTest não oferece edição de células; envia o estado que o navegador
    # enviaria junto com a submissão do formulário.
    app.session_state[f'{nome}_v0'] = edicoes
    app.button[indice].click().run()
    assert not app.exception
    assert app.session_state[nome]['Descricao'].tolist() == ['Alterada', 'Nova']
    assert app.session_state[nome]['Valor'].tolist() == [20.0, 30.0]
    assert app.session_state['gravacoes'] == 1
    assert not app.success
    assert len(app.get('toast')) == 1
    assert app.get('toast')[0].value == 'Alterações salvas.'

    app.run()
    assert not app.exception
    assert not app.get('toast')
    assert app.session_state['gravacoes'] == 1
    assert len(app.session_state[nome]) == 2

    app.session_state[f'{nome}_v1'] = {
        'edited_rows': {}, 'added_rows': [], 'deleted_rows': [0],
    }
    app.button[indice].click().run()
    assert not app.exception
    assert app.session_state[nome]['Descricao'].tolist() == ['Nova']
    assert app.session_state['gravacoes'] == 2


def test_erro_de_validacao_mantem_edicoes_para_corrigir():
    app = AppTest.from_string(APP).run()
    app.session_state['receitas_v0'] = {
        'edited_rows': {0: {'Valor': -1.0}}, 'added_rows': [], 'deleted_rows': [],
    }
    app.button[1].click().run()
    assert not app.exception
    assert app.warning[0].value == 'Valor deve ser positivo.'
    assert app.session_state['receitas']['Valor'].tolist() == [10.0]
    assert app.session_state['receitas_v0']['edited_rows'][0]['Valor'] == -1.0

    app.session_state['receitas_v0'] = {
        'edited_rows': {0: {'Valor': 25.0}}, 'added_rows': [], 'deleted_rows': [],
    }
    app.button[1].click().run()
    assert not app.exception
    assert not app.warning
    assert app.session_state['receitas']['Valor'].tolist() == [25.0]
    assert app.session_state['gravacoes'] == 1
