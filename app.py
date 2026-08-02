"""SOSO — Sistema Operacional que Salva o Orçamento."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import select

from database import Categoria, GastoFixo, Lancamento, criar_engine, criar_sessao, criar_tabelas

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
        background: rgba(15, 23, 42, 0.9);
        border-color: rgba(96, 165, 250, 0.55);
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
    dados = pd.DataFrame(linhas, columns=["data", "tipo", "valor"])
    if dados.empty:
        return pd.DataFrame(columns=["mes", "tipo", "valor"])
    dados["mes"] = pd.to_datetime(dados["data"]).dt.to_period("M").dt.to_timestamp()
    return dados.groupby(["mes", "tipo"], as_index=False)["valor"].sum()


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
    painel_fixos.markdown('<div class="panel-title">Planilha de gastos fixos</div>', unsafe_allow_html=True)
    with Sessao() as sessao:
        fixos = sessao.execute(select(GastoFixo, Categoria.nome).join(Categoria).order_by(GastoFixo.descricao)).all()
    tabela = pd.DataFrame(
        [{
            "Conta": gasto.descricao,
            "Categoria": categoria,
            "Valor previsto": float(gasto.valor_previsto),
            "Vencimento": gasto.dia_vencimento,
            "Status": "Pago" if gasto.ativo else "Pendente",
            "Observação": "",
        } for gasto, categoria in fixos]
    )
    if tabela.empty:
        tabela = pd.DataFrame(columns=["Conta", "Categoria", "Valor previsto", "Vencimento", "Status", "Observação"])
    editor = painel_fixos.data_editor(
        tabela,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "Valor previsto": st.column_config.NumberColumn(format="R$ %.2f"),
            "Status": st.column_config.SelectboxColumn(options=["Pago", "Pendente"]),
            "Vencimento": st.column_config.NumberColumn(min_value=1, max_value=31),
        },
        disabled=["Conta", "Categoria"],
    )


def novo_lancamento(Sessao) -> None:
    st.header("Novo lançamento")
    st.caption("Registre uma movimentação em poucos segundos.")
    with Sessao() as sessao:
        categorias = sessao.scalars(select(Categoria).order_by(Categoria.nome)).all()
    tipos = {"Receita": "receita", "Despesa": "despesa", "Investimento": "investimento"}
    with st.form("novo_lancamento", clear_on_submit=True):
        tipo_exibido = st.segmented_control("Tipo", list(tipos), default="Despesa")
        descricao = st.text_input("Descrição", placeholder="Ex.: Mercado")
        valor = st.number_input("Valor", min_value=0.01, step=1.0, format="%.2f")
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


def gastos_fixos(Sessao) -> None:
    st.header("Gastos fixos")
    with Sessao() as sessao:
        fixos = sessao.execute(select(GastoFixo, Categoria.nome).join(Categoria).order_by(GastoFixo.descricao)).all()
    if fixos:
        tabela = pd.DataFrame([{"Descrição": f.descricao, "Categoria": categoria, "Valor previsto": float(f.valor_previsto),
                                "Vencimento": f.dia_vencimento, "Ativo": f.ativo} for f, categoria in fixos])
        st.dataframe(tabela, use_container_width=True, hide_index=True,
                     column_config={"Valor previsto": st.column_config.NumberColumn(format="R$ %.2f")})
    else:
        st.info("Nenhum gasto fixo cadastrado.")
    with st.expander("Adicionar gasto fixo"):
        with st.form("novo_fixo", clear_on_submit=True):
            descricao = st.text_input("Conta")
            valor = st.number_input("Valor previsto", min_value=0.01, step=1.0, format="%.2f")
            vencimento = st.number_input("Dia de vencimento", min_value=1, max_value=31, value=10)
            salvar = st.form_submit_button("Adicionar", type="primary")
        if salvar:
            if not descricao.strip():
                st.error("Informe a conta.")
            else:
                with Sessao.begin() as sessao:
                    categoria = sessao.scalar(select(Categoria).where(Categoria.nome == descricao.strip()))
                    if categoria is None:
                        categoria = Categoria(nome=descricao.strip(), tipo="despesa")
                        sessao.add(categoria)
                        sessao.flush()
                    sessao.add(GastoFixo(categoria_id=categoria.id, descricao=descricao.strip(),
                                         valor_previsto=Decimal(str(valor)), dia_vencimento=int(vencimento)))
                st.success("Gasto fixo adicionado.")
                st.rerun()


def main() -> None:
    try:
        Sessao = sessao_factory()
    except RuntimeError as erro:
        st.error(str(erro))
        st.code("cp .env.example .env\n# edite DATABASE_URL\nstreamlit run app.py")
        st.stop()

    tab_dashboard, tab_lancamento, tab_fixos = st.tabs(["Dashboard", "Novo lançamento", "Gastos fixos"])

    with tab_dashboard:
        dashboard(Sessao)
    with tab_lancamento:
        novo_lancamento(Sessao)
    with tab_fixos:
        gastos_fixos(Sessao)


if __name__ == "__main__":
    main()
