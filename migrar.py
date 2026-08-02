"""Importa a planilha histórica para o banco de dados do SOSO.

Uso: python migrar.py --arquivo financas.xlsx
O script pode ser executado mais de uma vez: registros previamente importados
não são inseridos novamente.
"""
from __future__ import annotations

import argparse
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

import openpyxl
from sqlalchemy import select

from database import Categoria, GastoFixo, Lancamento, criar_engine, criar_sessao, criar_tabelas

MESES = {nome: numero for numero, nome in enumerate(
    ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"), 1
)}
IGNORAR = {"pessoal", "contas", "total", "valor", "mês", "ganho total", "valor total"}
ROTULOS_RECEITA = {"ganho", "receita", "salário", "salario"}
ROTULOS_INVESTIMENTO = {"investido", "investimento", "investimentos"}


def texto(valor: object) -> str:
    return str(valor or "").strip()


def normalizar(valor: object) -> str:
    return re.sub(r"\s+", " ", texto(valor).lower())


def para_decimal(valor: object) -> Decimal | None:
    """Converte números e textos como 'R$ 2.504,08' sem aceitar lixo."""
    if valor is None or isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float, Decimal)):
        return Decimal(str(valor)).quantize(Decimal("0.01"))
    bruto = texto(valor).replace("R$", "").replace(" ", "")
    if not bruto:
        return None
    if "," in bruto:
        bruto = bruto.replace(".", "").replace(",", ".")
    try:
        return Decimal(bruto).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def tipo_do_rotulo(rotulo: str) -> str:
    chave = normalizar(rotulo)
    if chave in ROTULOS_RECEITA:
        return "receita"
    if chave in ROTULOS_INVESTIMENTO:
        return "investimento"
    return "despesa"


def abas_anuais(workbook) -> list[tuple[int, object]]:
    resultado = []
    for aba in workbook.worksheets:
        try:
            ano = int(aba.title)
        except ValueError:
            continue
        if 2000 <= ano <= 2100:
            resultado.append((ano, aba))
    return resultado


def extrair_lancamentos(arquivo: str | Path):
    """Lê os blocos mensais da planilha e devolve tuplas prontas para importar."""
    # A planilha original não declara a dimensão usada em todas as abas; por
    # isso, o modo read_only não consegue informar max_row com confiabilidade.
    wb = openpyxl.load_workbook(arquivo, data_only=True, read_only=False)
    registros = []
    for ano, aba in abas_anuais(wb):
        # Na planilha, cada bloco começa em E, I, M... e contém descrição/valor.
        for mes in range(1, 13):
            coluna_descricao = 5 + (mes - 1) * 4
            # Abas vazias no Excel podem não informar ``max_row`` em modo leitura.
            for linha in range(4, (aba.max_row or 0) + 1):
                descricao = texto(aba.cell(linha, coluna_descricao).value)
                valor = para_decimal(aba.cell(linha, coluna_descricao + 1).value)
                chave = normalizar(descricao)
                if not descricao or valor is None or valor <= 0 or chave in IGNORAR:
                    continue
                if chave in MESES:  # cabeçalhos do segundo semestre
                    continue
                tipo = tipo_do_rotulo(descricao)
                registros.append((ano, mes, descricao, valor, tipo))
    wb.close()
    return registros


def obter_categoria(sessao, nome: str, tipo: str) -> Categoria:
    categoria = sessao.scalar(select(Categoria).where(Categoria.nome == nome))
    if categoria is None:
        categoria = Categoria(nome=nome, tipo=tipo)
        sessao.add(categoria)
        sessao.flush()
    return categoria


def importar(arquivo: str | Path, url: str | None = None) -> int:
    engine = criar_engine(url)
    criar_tabelas(engine)
    Sessao = criar_sessao(engine)
    inseridos = 0
    with Sessao.begin() as sessao:
        for ano, mes, descricao, valor, tipo in extrair_lancamentos(arquivo):
            categoria = obter_categoria(sessao, descricao, tipo)
            data_lancamento = date(ano, mes, 1)
            existente = sessao.scalar(select(Lancamento.id).where(
                Lancamento.descricao == descricao,
                Lancamento.tipo == tipo,
                Lancamento.valor == valor,
                Lancamento.data == data_lancamento,
                Lancamento.origem == "excel",
            ))
            if existente:
                continue
            gasto_fixo_id = None
            if tipo == "despesa":
                fixo = sessao.scalar(select(GastoFixo).where(GastoFixo.descricao == descricao))
                if fixo is None:
                    fixo = GastoFixo(categoria_id=categoria.id, descricao=descricao, valor_previsto=valor, dia_vencimento=10)
                    sessao.add(fixo)
                    sessao.flush()
                gasto_fixo_id = fixo.id
            sessao.add(Lancamento(categoria_id=categoria.id, tipo=tipo, descricao=descricao,
                                  valor=valor, data=data_lancamento, gasto_fixo_id=gasto_fixo_id,
                                  origem="excel"))
            inseridos += 1
    return inseridos


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa financas.xlsx para o Supabase.")
    parser.add_argument("--arquivo", default="financas.xlsx", help="Caminho da planilha de origem")
    args = parser.parse_args()
    if not Path(args.arquivo).exists():
        parser.error(f"Arquivo não encontrado: {args.arquivo}")
    total = importar(args.arquivo)
    print(f"Importação concluída: {total} lançamento(s) novos.")


if __name__ == "__main__":
    main()
