"""Modelos e utilitários de acesso ao banco do SOSO."""
from __future__ import annotations

import os
from datetime import date, datetime, timezone
from decimal import Decimal

from dotenv import load_dotenv
from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    pass


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    tipo: Mapped[str] = mapped_column(String(20))  # receita, despesa ou investimento
    lancamentos: Mapped[list["Lancamento"]] = relationship(back_populates="categoria")


class GastoFixo(Base):
    __tablename__ = "gastos_fixos"

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    descricao: Mapped[str] = mapped_column(String(160))
    valor_previsto: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    dia_vencimento: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ativo: Mapped[bool] = mapped_column(default=True)
    categoria: Mapped[Categoria] = relationship()


class GastoPlanejado(Base):
    """Planejamento de despesas de um mês específico."""

    __tablename__ = "gastos_planejados"

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    descricao: Mapped[str] = mapped_column(String(160))
    valor_previsto: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    dia_vencimento: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Pendente")
    observacao: Mapped[str] = mapped_column(String(500), default="")
    mes_referencia: Mapped[date] = mapped_column(Date, index=True)
    categoria: Mapped[Categoria] = relationship()


class Lancamento(Base):
    __tablename__ = "lancamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    tipo: Mapped[str] = mapped_column(String(20), index=True)  # receita, despesa ou investimento
    descricao: Mapped[str] = mapped_column(String(160))
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    data: Mapped[date] = mapped_column(Date, index=True)
    gasto_fixo_id: Mapped[int | None] = mapped_column(ForeignKey("gastos_fixos.id"), nullable=True)
    origem: Mapped[str] = mapped_column(String(30), default="manual")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    categoria: Mapped[Categoria] = relationship(back_populates="lancamentos")
    gasto_fixo: Mapped[GastoFixo | None] = relationship()


def database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Defina DATABASE_URL no arquivo .env antes de conectar ao banco.")
    return url


def criar_engine(url: str | None = None):
    """Cria engine compatível com Supabase e SQLite (usado pelos testes)."""
    target = url or database_url()
    options: dict = {"future": True}
    if not target.startswith("sqlite"):
        options["pool_pre_ping"] = True
    return create_engine(target, **options)


def criar_tabelas(engine) -> None:
    Base.metadata.create_all(engine)


def criar_sessao(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
