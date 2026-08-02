from database import Categoria, criar_engine, criar_sessao, criar_tabelas


def test_cria_tabelas_e_relacionamento(tmp_path):
    engine = criar_engine(f"sqlite:///{tmp_path / 'dados.db'}")
    criar_tabelas(engine)
    Sessao = criar_sessao(engine)
    with Sessao.begin() as sessao:
        sessao.add(Categoria(nome="Mercado", tipo="despesa"))
    with Sessao() as sessao:
        assert sessao.query(Categoria).filter_by(nome="Mercado").one().tipo == "despesa"
