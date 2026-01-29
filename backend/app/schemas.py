from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class NivelRiscoEnum(str, Enum):
    baixo = "baixo"
    medio = "medio"
    alto = "alto"


# Schema para criar (se tiver)
class ClimaRegistroCreate(BaseModel):
    bairro: str


# Schema para leitura (O que vai para o Frontend)
class ClimaRegistro(BaseModel):
    id: int
    bairro: str
    horario_registro: datetime
    chuva_mm: Optional[float] = 0.0
    precipitacao: Optional[float] = 0.0
    vento_velocidade: Optional[float] = 0.0

    # --- ADICIONE ESTES DOIS ---
    chuva_acum_3h_prox: Optional[float] = 0.0
    chuva_acum_6h_ant: Optional[float] = 0.0
    # ---------------------------

    nivel_risco: NivelRiscoEnum
    criado_em: datetime

    class Config:
        from_attributes = True