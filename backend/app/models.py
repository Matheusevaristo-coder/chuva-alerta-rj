from sqlalchemy import Column, Integer, String, DECIMAL, Enum, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum


class NivelRiscoEnum(str, enum.Enum):
    baixo = "baixo"
    medio = "medio"
    alto = "alto"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    bairro = Column(String(100), nullable=False)
    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    alertas = relationship("Alerta", back_populates="usuario")


class ClimaRegistro(Base):
    __tablename__ = "clima_registros"

    id = Column(Integer, primary_key=True, index=True)
    bairro = Column(String(100), nullable=False)
    horario_registro = Column(DateTime, nullable=False)
    chuva_mm = Column(DECIMAL(5, 2))
    precipitacao = Column(DECIMAL(5, 2))
    vento_velocidade = Column(DECIMAL(5, 2))
    chuva_acum_3h_prox = Column(DECIMAL(5, 2))

    # --- NOVA COLUNA DE ACUMULADO ---
    chuva_acum_6h_ant = Column(DECIMAL(5, 2), default=0.0)
    # --------------------------------

    nivel_risco = Column(Enum(NivelRiscoEnum), nullable=False)

    # CORREÇÃO AQUI: Mudamos de TIMESTAMP (que dava erro) para DateTime (igual aos outros)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    bairro = Column(String(100), nullable=False)
    horario_alerta = Column(DateTime, nullable=False)
    mensagem = Column(Text, nullable=False)
    tipo_alerta = Column(String(50), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="alertas")