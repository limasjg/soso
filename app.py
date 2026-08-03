"""SOSO — Sistema Operacional que Salva o Orçamento."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import delete, func, select

from database import Categoria, GastoPlanejado, Lancamento, criar_engine, criar_sessao, criar_tabelas

st.set_page_config(page_title="SOSO", page_icon="💸", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
    html, body {
        background: #03111d;
        color: #e2e8f0;
        scroll-behavior: smooth;
    }
    .stApp {
        background: linear-gradient(180deg, #041a2d 0%, #020d18 100%);
    }
    [data-testid="stHeader"] {
        display: none;
    }
    [data-testid="stToolbar"] {
        display: none;
    }
    .topbar {
        position: sticky;
        top: 0;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.9rem 1.4rem;
        background: rgba(3, 17, 29, 0.88);
        backdrop-filter: blur(18px);
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
        margin: 0 0rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        color: #f8fafc;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }
    .brand-badge {
        width: 0.8rem;
        height: 0.8rem;
        border-radius: 50%;
        background: linear-gradient(135deg, #34d399, #2dd4bf);
        box-shadow: 0 0 18px rgba(52, 211, 153, 0.8);
    }
    .status {
        color: #cbd5e1;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.9;
    }
    .block-container {
        max-width: 1200px;
        padding-top: 1.2rem;
        padding-bottom: 2.8rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .soso-title {
        font-size: clamp(2rem, 3vw, 2.7rem);
        font-weight: 700;
        margin: 0.2rem 0 0.35rem;
        color: #f8fafc;
        letter-spacing: -0.06em;
        line-height: 1.1;
    }
    .soso-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0 0 1.35rem;
    }
    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.80);
        border: 1px solid rgb(32 42 62) !important;
        border-radius: 18px;
        padding: 18px 16px 14px;
        min-height: 140px;
        box-shadow: 0 12px 32px rgba(2, 8, 23, 0.18);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-align: center !important;
    }
    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: clamp(1.5rem, 2.1vw, 2.2rem) !important;
        line-height: 1.2 !important;
        font-weight: 700 !important;
        letter-spacing: -0.04em !important;
        text-align: center !important;
    }
    [data-testid="stMetricDelta"],
    [data-testid="stMetricDelta"] * {
        color: #f8fafc !important;
        opacity: 1 !important;
    }
    .kpi-card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgb(32 42 62) !important;
        border-radius: 18px;
        padding: 1rem 1.1rem;
        min-height: 110px;
        box-shadow: 0 10px 30px rgba(2, 8, 23, 0.18);
    }
    .kpi-card .label {
        color: #cbd5e1;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.85;
    }
    .kpi-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.05em;
    }
    .kpi-card .delta {
        font-size: 0.8rem;
        color: #34d399;
    }
    .panel,
    [data-testid="stVerticalBlockBorderWrapper"],
    .st-emotion-cache-1ne20ew {
        background: rgba(15, 23, 42, 0.84);
        border: 1px solid rgb(32 42 62) !important;
        border-radius: 20px;
        padding: 1rem 1.1rem 0.8rem;
        box-shadow: 0 12px 32px rgba(2, 8, 23, 0.18);
    }
    .panel-title {
        color: #f8fafc;
        font-size: 1.15rem;
        font-weight: 600;
        margin: 0 0 0.85rem;
    }
    .selection-wrap {
        display: flex;
        gap: 0.75rem;
        align-items: end;
        margin-bottom: 1rem;
    }
    .selection-wrap > div {
        flex: 1;
    }
    [role="tablist"] [role="tab"]::before,
    [role="tablist"] [role="tab"]::after,
    .react-aria-SelectionIndicator {
        display: none !important;
        content: none !important;
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    .year-toggle {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .year-pill {
        background: rgba(15, 23, 42, 0.8);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 600;
    }
    .year-pill.active {
        background: rgba(52,211,153,0.18);
        border-color: rgba(52,211,153,0.45);
        color: #d1fae5;
    }
    .sheet-table {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 18px;
        overflow: hidden;
    }
    .sheet-table .stDataFrame {
        border-radius: 18px;
    }
    .stSelectbox label, .stDateInput label, .stTextInput label, .stNumberInput label, .stCheckbox label {
        color: #e2e8f0 !important;
    }
    h1, h2, h3, [data-testid="stHeading"] {
        color: #f8fafc !important;
    }
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    .stForm label {
        color: #e2e8f0 !important;
        opacity: 1 !important;
    }
    [data-testid="stForm"] input,
    [data-testid="stForm"] textarea,
    [data-testid="stForm"] [data-baseweb="select"] input {
        color: #0f172a !important;
        background: #f8fafc !important;
    }
    [data-testid="stSegmentedControl"] button[aria-pressed="true"],
    [data-testid="stSegmentedControl"] button[aria-selected="true"],
    [data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"],
    [data-testid="stSegmentedControl"] [aria-checked="true"],
    [data-testid="stSegmentedControl"] [data-checked="true"] {
        background: #00b547 !important;
        border-color: #00b547 !important;
        color: #ffffff !important;
    }
    button[data-variant="segmented_control"][data-selected="true"]:not([data-disabled]) {
        background-color: rgba(0, 181, 71, 0.18) !important;
        border-color: #00b547 !important;
        color: #00b547 !important;
    }
    [data-testid="stSegmentedControl"] button[aria-pressed="true"] *,
    [data-testid="stSegmentedControl"] button[aria-selected="true"] *,
    [data-testid="stSegmentedControl"] [aria-checked="true"] *,
    [data-testid="stSegmentedControl"] [data-checked="true"] * {
        color: #ffffff !important;
    }
    button[data-variant="segmented_control"][data-selected="true"]:not([data-disabled]) * {
        color: #00b547 !important;
    }
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stButton"] button[kind="primary"] {
        background: #00b547 !important;
        border-color: #00b547 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stFormSubmitButton"] button:hover,
    [data-testid="stButton"] button[kind="primary"]:hover {
        background: #008f38 !important;
        border-color: #008f38 !important;
    }
    .stTabs [role="tablist"] {
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .stTabs [role="tab"] {
        border-radius: 12px;
        padding: 0.7rem 1rem;
        border: 1px solid rgba(148, 163, 184, 0.15);
        background: rgba(15, 23, 42, 0.55);
        color: #cbd5e1;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: rgba(0, 181, 71, 0.14);
        border-color: #00b547;
        color: #f8fafc;
    }
    @media (max-width: 640px) {
        .topbar {padding: 0.8rem 1rem; margin: 0 -0.8rem;}
        .block-container {padding-left: 0.75rem; padding-right: 0.75rem;}
        [data-testid="stMetric"] {min-height: 120px;}
    }
</style>""", unsafe_allow_html=True)

st.markdown('''
<div class="topbar">
    <div class="brand">💸 SOSO</div>
    <div class="status"></div>
</div>
''', unsafe_allow_html=True)


@st.cache_resource
def sessao_factory():
    engine = criar_engine()
    criar_tabelas(engine)
    return criar_sessao(engine)


def moeda(valor: Decimal | float | int) -> str:
    return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_resumo(Sessao) -> pd.DataFrame:
    with Sessao() as sessao:
        linhas = sessao.execute(select(Lancamento.data, Lancamento.tipo, Lancamento.valor)).all()
        planejamentos = sessao.execute(
            select(GastoPlanejado.mes_referencia, func.sum(GastoPlanejado.valor_previsto))
            .group_by(GastoPlanejado.mes_referencia)
        ).all()
    dados = pd.DataFrame(linhas, columns=["data", "tipo", "valor"])
    if dados.empty:
        dados = pd.DataFrame(columns=["mes", "tipo", "valor"])
    else:
        dados["mes"] = pd.to_datetime(dados["data"]).dt.to_period("M").dt.to_timestamp()
        dados = dados.groupby(["mes", "tipo"], as_index=False)["valor"].sum()

    # Quando existe uma planilha mensal salva, ela representa a previsão de
    # despesas daquele mês e substitui os lançamentos históricos no Dashboard.
    if planejamentos:
        previstos = pd.DataFrame(planejamentos, columns=["mes", "valor"])
        previstos["mes"] = pd.to_datetime(previstos["mes"])
        previstos["tipo"] = "despesa"
        dados = dados[~((dados["tipo"] == "despesa") & dados["mes"].isin(previstos["mes"]))]
        dados = pd.concat([dados, previstos[["mes", "tipo", "valor"]]], ignore_index=True)
    return dados.groupby(["mes", "tipo"], as_index=False)["valor"].sum()


def primeiro_dia_do_mes(valor: pd.Timestamp | date) -> date:
    timestamp = pd.Timestamp(valor)
    return date(timestamp.year, timestamp.month, 1)


def carregar_planejamento_mensal(Sessao, mes_referencia: pd.Timestamp) -> pd.DataFrame:
    """Carrega o mês ou cria sua primeira versão a partir do mês anterior."""
    referencia = primeiro_dia_do_mes(mes_referencia)
    anterior = (pd.Timestamp(referencia) - pd.DateOffset(months=1)).date().replace(day=1)

    with Sessao.begin() as sessao:
        planejados = sessao.execute(
            select(GastoPlanejado, Categoria.nome)
            .join(Categoria)
            .where(GastoPlanejado.mes_referencia == referencia)
            .order_by(GastoPlanejado.descricao)
        ).all()

        if not planejados:
            origem = sessao.execute(
                select(GastoPlanejado, Categoria.nome)
                .join(Categoria)
                .where(GastoPlanejado.mes_referencia == anterior)
                .order_by(GastoPlanejado.descricao)
            ).all()
            if origem:
                planejados = []
                for gasto, categoria in origem:
                    novo = GastoPlanejado(
                        categoria_id=gasto.categoria_id,
                        descricao=gasto.descricao,
                        valor_previsto=gasto.valor_previsto,
                        dia_vencimento=gasto.dia_vencimento,
                        status=gasto.status,
                        observacao=gasto.observacao,
                        mes_referencia=referencia,
                    )
                    sessao.add(novo)
                    planejados.append((novo, categoria))
            else:
                # O primeiro mês sem planejamento usa as despesas reais do mês anterior.
                despesas = sessao.execute(
                    select(Lancamento, Categoria.nome)
                    .join(Categoria)
                    .where(
                        Lancamento.tipo == "despesa",
                        Lancamento.data >= anterior,
                        Lancamento.data < referencia,
                    )
                    .order_by(Lancamento.descricao)
                ).all()
                planejados = []
                for lancamento, categoria in despesas:
                    novo = GastoPlanejado(
                        categoria_id=lancamento.categoria_id,
                        descricao=lancamento.descricao,
                        valor_previsto=lancamento.valor,
                        dia_vencimento=10,
                        status="Pendente",
                        observacao="",
                        mes_referencia=referencia,
                    )
                    sessao.add(novo)
                    planejados.append((novo, categoria))

        linhas = [
            {
                "Conta": gasto.descricao,
                "Categoria": categoria,
                "Valor previsto": float(gasto.valor_previsto),
                "Vencimento": gasto.dia_vencimento or 10,
                "Status": gasto.status,
                "Observação": gasto.observacao,
            }
            for gasto, categoria in planejados
        ]
    return pd.DataFrame(linhas, columns=["Conta", "Categoria", "Valor previsto", "Vencimento", "Status", "Observação"])


def salvar_planejamento_mensal(Sessao, mes_referencia: pd.Timestamp, tabela: pd.DataFrame) -> None:
    referencia = primeiro_dia_do_mes(mes_referencia)
    linhas = []
    for registro in tabela.fillna("").to_dict("records"):
        descricao = str(registro["Conta"]).strip()
        categoria_nome = str(registro["Categoria"] or descricao).strip() or descricao
        try:
            valor = Decimal(str(registro["Valor previsto"])).quantize(Decimal("0.01"))
            vencimento = int(registro["Vencimento"])
        except (ArithmeticError, TypeError, ValueError):
            raise ValueError(f"Revise o valor e o vencimento de '{descricao or 'nova conta'}'.")
        if not descricao or valor <= 0 or not 1 <= vencimento <= 31:
            raise ValueError("Cada linha precisa de conta, valor positivo e vencimento entre 1 e 31.")
        linhas.append((descricao, categoria_nome, valor, vencimento, str(registro["Status"] or "Pendente"), str(registro["Observação"] or "")))

    with Sessao.begin() as sessao:
        sessao.execute(delete(GastoPlanejado).where(GastoPlanejado.mes_referencia == referencia))
        for descricao, categoria_nome, valor, vencimento, status, observacao in linhas:
            categoria = sessao.scalar(select(Categoria).where(Categoria.nome == categoria_nome))
            if categoria is None:
                categoria = Categoria(nome=categoria_nome, tipo="despesa")
                sessao.add(categoria)
                sessao.flush()
            sessao.add(GastoPlanejado(
                categoria_id=categoria.id,
                descricao=descricao,
                valor_previsto=valor,
                dia_vencimento=vencimento,
                status=status,
                observacao=observacao,
                mes_referencia=referencia,
            ))


def detalhamento_mes(Sessao) -> None:
    ano = st.session_state.get("ano_selecionado", date.today().year)
    mes_selecionado = pd.Timestamp(st.session_state.get("mes_selecionado", date.today())).to_period("M").to_timestamp()
    if mes_selecionado.year != ano:
        mes_selecionado = pd.Timestamp(f"{ano}-{mes_selecionado.month:02d}-01")
    proximo_mes = mes_selecionado + pd.DateOffset(months=1)

    st.markdown('<div class="soso-title" style="font-size: 2rem;">Detalhamento do mês</div>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="soso-subtitle">Lançamentos de {mes_selecionado.strftime("%m/%Y")}. Altere o período no Dashboard para consultar outro mês.</p>',
        unsafe_allow_html=True,
    )
    with Sessao() as sessao:
        registros = sessao.execute(
            select(Lancamento, Categoria.nome)
            .join(Categoria)
            .where(Lancamento.data >= mes_selecionado.date(), Lancamento.data < proximo_mes.date())
            .order_by(Lancamento.tipo, Lancamento.descricao)
        ).all()

    planejamento = carregar_planejamento_mensal(Sessao, mes_selecionado)
    dados = pd.DataFrame(
        [
            {
                "Tipo": lancamento.tipo,
                "Descrição": lancamento.descricao,
                "Categoria": categoria,
                "Valor": float(lancamento.valor),
                "Data": lancamento.data,
                "Origem": lancamento.origem,
            }
            for lancamento, categoria in registros
        ],
        columns=["Tipo", "Descrição", "Categoria", "Valor", "Data", "Origem"],
    )
    despesas_planejadas = planejamento.rename(columns={"Conta": "Descrição", "Valor previsto": "Valor"})
    despesas_planejadas["Data"] = mes_selecionado.date()
    despesas_planejadas["Origem"] = "planejamento mensal"
    despesas_planejadas = despesas_planejadas[["Descrição", "Categoria", "Valor", "Data", "Origem", "Vencimento", "Status", "Observação"]]

    totais = dados.groupby("Tipo")["Valor"].sum().to_dict() if not dados.empty else {}
    col_receita, col_despesa, col_investimento = st.columns(3)
    col_receita.metric("Receitas", moeda(totais.get("receita", 0)))
    col_despesa.metric("Despesas", moeda(despesas_planejadas["Valor"].sum()))
    col_investimento.metric("Investimentos", moeda(totais.get("investimento", 0)))

    if dados.empty and despesas_planejadas.empty:
        st.info("Não há lançamentos neste mês.")
        return

    nomes = {"receita": "Receitas", "despesa": "Despesas", "investimento": "Investimentos"}
    abas = st.tabs(list(nomes.values()))
    for aba, (tipo, titulo) in zip(abas, nomes.items()):
        with aba:
            tabela = despesas_planejadas if tipo == "despesa" else dados[dados["Tipo"] == tipo].drop(columns="Tipo")
            if tabela.empty:
                st.caption(f"Nenhum lançamento de {titulo.lower()}.")
            else:
                st.dataframe(
                    tabela,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Valor": st.column_config.NumberColumn(format="R$ %.2f"),
                        "Data": st.column_config.DateColumn(format="DD/MM/YYYY"),
                    },
                )


def dashboard(Sessao) -> None:
    st.markdown('<p class="soso-title">Seu orçamento, sob controle.</p>', unsafe_allow_html=True)
    st.markdown('<p class="soso-subtitle">Acompanhe ganhos, gastos e investimentos mês a mês.</p>', unsafe_allow_html=True)

    resumo = carregar_resumo(Sessao)
    if resumo.empty:
        st.info("Ainda não há lançamentos. Registre o primeiro na aba **Novo lançamento** ou execute a migração.")
        return

    resumo = resumo.copy()
    resumo["ano"] = resumo["mes"].dt.year
    hoje = date.today()
    ano_atual = hoje.year
    mes_atual = pd.Timestamp(hoje).to_period("M").to_timestamp()
    anos = sorted(set(resumo["ano"].dropna().unique().tolist() + [ano_atual]), reverse=True)

    def selecionar_mes_do_ano() -> None:
        """Atualiza o mês para uma opção válida ao trocar de ano."""
        ano_selecionado = st.session_state["ano_selecionado"]
        st.session_state["mes_selecionado"] = (
            mes_atual if ano_selecionado == ano_atual else pd.Timestamp(f"{ano_selecionado}-12-01")
        )

    col_ano, col_mes = st.columns(2)
    with col_ano:
        ano = st.selectbox(
            "Ano", anos, index=anos.index(ano_atual), key="ano_selecionado", on_change=selecionar_mes_do_ano
        )
    with col_mes:
        dados_ano = resumo[resumo["ano"] == ano].copy()
        periodo_inicio = pd.Period(f"{ano}-01", freq="M")
        periodo_fim = pd.Period(hoje, freq="M") if ano == ano_atual else pd.Period(f"{ano}-12", freq="M")
        meses = pd.period_range(periodo_inicio, periodo_fim, freq="M").to_timestamp()
        meses = sorted(set(pd.Timestamp(m) for m in meses) | set(dados_ano["mes"].dropna().unique().tolist()))
        mes_padrao = mes_atual if ano == ano_atual else pd.Timestamp(f"{ano}-12-01")
        if st.session_state.get("mes_selecionado") not in meses:
            st.session_state["mes_selecionado"] = mes_padrao
        mes = st.selectbox(
            "Mês", meses, format_func=lambda x: pd.Timestamp(x).strftime("%m/%Y"), key="mes_selecionado"
        )

    dados_mes = dados_ano[dados_ano["mes"] == mes].set_index("tipo")["valor"].to_dict()
    receita = float(dados_mes.get("receita", 0) or 0)
    despesa = float(dados_mes.get("despesa", 0) or 0)
    investimento = float(dados_mes.get("investimento", 0) or 0)
    saldo = receita - despesa - investimento

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Receita", moeda(receita))
    col2.metric("Despesas", moeda(despesa))
    col3.metric("Investido", moeda(investimento))
    col4.metric("Saldo do mês", moeda(saldo))

    periodo_final = pd.Period(hoje, freq="M") if ano == ano_atual else pd.Period(f"{ano}-12", freq="M")
    meses_grafico = pd.period_range(f"{ano}-01", periodo_final, freq="M").to_timestamp()
    mensal = (
        dados_ano.pivot_table(index="mes", columns="tipo", values="valor", aggfunc="sum", fill_value=0)
        .reindex(meses_grafico, fill_value=0)
        .rename_axis("mes")
    )
    for tipo in ("receita", "despesa", "investimento"):
        if tipo not in mensal.columns:
            mensal[tipo] = 0.0

    painel_anual = st.container(border=True)
    painel_anual.markdown('<div class="panel-title">Receitas, despesas e fluxos</div>', unsafe_allow_html=True)

    for coluna, (tipo, titulo) in zip(
        painel_anual.columns(3),
        [("receita", "Receita total"), ("despesa", "Despesas totais"), ("investimento", "Total investido")],
    ):
        total = float(mensal[tipo].sum())
        media = float(mensal[tipo].mean())
        coluna.metric(titulo, moeda(total), delta=f"Média mensal: {moeda(media)}", delta_color="off")

    fig_anual = go.Figure()
    for tipo, nome, cor in [
        ("receita", "Receita", "#22c55e"),
        ("despesa", "Despesas", "#f87171"),
        ("investimento", "Investimento", "#60a5fa"),
    ]:
        fig_anual.add_trace(
            go.Bar(x=mensal.index, y=mensal[tipo].astype(float), name=nome, marker_color=cor, opacity=0.82)
        )
    fig_anual.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=20, b=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(color="#f8fafc"),
        ),
        barmode="group",
        xaxis=dict(title="Mês", showgrid=False, type="date", tickformat="%b"),
        yaxis=dict(title="Valor (R$)", showgrid=True, gridcolor="rgba(148,163,184,0.12)"),
        font={"color": "#e2e8f0"},
    )
    painel_anual.plotly_chart(fig_anual, use_container_width=True)

    painel_fixos = st.container(border=True)
    mes_nome = pd.Timestamp(mes).strftime("%m/%Y")
    painel_fixos.markdown(f'<div class="panel-title">Planilha de gastos — {mes_nome}</div>', unsafe_allow_html=True)
    painel_fixos.caption("A primeira versão deste mês é copiada do mês anterior. Salve suas alterações para usá-las como base no próximo mês.")
    tabela = carregar_planejamento_mensal(Sessao, pd.Timestamp(mes))
    editor = painel_fixos.data_editor(
        tabela,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        key=f"planejamento_{pd.Timestamp(mes).strftime('%Y_%m')}",
        column_config={
            "Valor previsto": st.column_config.NumberColumn(format="R$ %.2f"),
            "Status": st.column_config.SelectboxColumn(options=["Pago", "Pendente"]),
            "Vencimento": st.column_config.NumberColumn(min_value=1, max_value=31),
        },
    )
    if painel_fixos.button("Salvar planilha do mês", type="primary", key=f"salvar_planejamento_{pd.Timestamp(mes).strftime('%Y_%m')}"):
        try:
            salvar_planejamento_mensal(Sessao, pd.Timestamp(mes), editor)
        except ValueError as erro:
            painel_fixos.error(str(erro))
        else:
            painel_fixos.success("Planilha mensal salva.")
            st.rerun()


def novo_lancamento(Sessao) -> None:
    st.markdown('<div class="soso-title" style="font-size: 2rem;">Novo lançamento</div>', unsafe_allow_html=True)
    st.markdown('<p class="soso-subtitle">Registre uma receita, despesa ou investimento em poucos segundos.</p>', unsafe_allow_html=True)
    with Sessao() as sessao:
        categorias = sessao.scalars(select(Categoria).order_by(Categoria.nome)).all()
    tipos = {"Receita": "receita", "Despesa": "despesa", "Investimento": "investimento"}
    painel_lancamento = st.container(border=True)
    with painel_lancamento.form("novo_lancamento", clear_on_submit=True):
        tipo_exibido = st.segmented_control("Tipo do lançamento", list(tipos), default="Despesa", width="stretch")
        descricao = st.text_input("Descrição", placeholder="Ex.: Mercado")
        coluna_valor, coluna_data = st.columns(2)
        with coluna_valor:
            valor = st.number_input("Valor", min_value=0.01, step=1.0, format="%.2f")
        with coluna_data:
            data = st.date_input("Data", value=date.today())
        opcoes = [c.nome for c in categorias if c.tipo == tipos[tipo_exibido]]
        categoria_nome = st.selectbox("Categoria", ["Criar a partir da descrição"] + opcoes)
        enviar = st.form_submit_button("Salvar lançamento", type="primary", use_container_width=True)
    if enviar:
        if not descricao.strip():
            st.error("Informe uma descrição.")
            return
        tipo = tipos[tipo_exibido]
        nome_categoria = descricao.strip() if categoria_nome == "Criar a partir da descrição" else categoria_nome
        with Sessao.begin() as sessao:
            categoria = sessao.scalar(select(Categoria).where(Categoria.nome == nome_categoria))
            if categoria is None:
                categoria = Categoria(nome=nome_categoria, tipo=tipo)
                sessao.add(categoria)
                sessao.flush()
            sessao.add(Lancamento(categoria_id=categoria.id, tipo=tipo, descricao=descricao.strip(),
                                  valor=Decimal(str(valor)), data=data, origem="manual"))
        st.success("Lançamento salvo.")
        st.rerun()


def main() -> None:
    try:
        Sessao = sessao_factory()
    except RuntimeError as erro:
        st.error(str(erro))
        st.code("cp .env.example .env\n# edite DATABASE_URL\nstreamlit run app.py")
        st.stop()

    tab_dashboard, tab_detalhamento, tab_lancamento = st.tabs(["Dashboard", "Detalhamento do mês", "Novo lançamento"])

    with tab_dashboard:
        dashboard(Sessao)
    with tab_detalhamento:
        detalhamento_mes(Sessao)
    with tab_lancamento:
        novo_lancamento(Sessao)


if __name__ == "__main__":
    main()
