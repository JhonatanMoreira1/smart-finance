from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

db = SQLAlchemy()

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    preco_venda = Column(Float, nullable=False)
    custo = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)

class Entrada(db.Model):
    __tablename__ = 'entradas'
    id = Column(Integer, primary_key=True)
    data = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)
    produto = relationship('Produto')
    quantidade = Column(Integer, nullable=False)
    custo_unitario = Column(Float, nullable=False)
    total_custo = Column(Float, nullable=False)

class Saida(db.Model):
    __tablename__ = 'saidas'
    id = Column(Integer, primary_key=True)
    data = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)
    produto = relationship('Produto')
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    total_venda = Column(Float, nullable=False)
    forma_pagamento = Column(String(50))
    cliente = Column(String(100))

class Servico(db.Model):
    __tablename__ = 'servicos'
    id = Column(Integer, primary_key=True)
    data_hora = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    servico_descricao = Column(String(255), nullable=False)
    aparelho = Column(String(100))
    tipo = Column(String(50), nullable=False)
    custo_pecas = Column(Float, default=0.0)
    mao_de_obra = Column(Float, default=0.0)
    preco_aparelho = Column(Float, default=0.0)
    status = Column(String(50), default='Iniciado')
    forma_pagamento = Column(String(100))
    cliente = Column(String(100))