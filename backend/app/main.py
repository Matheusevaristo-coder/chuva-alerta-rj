from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from .database import get_db, SessionLocal
from .models import ClimaRegistro
from .services_clima import atualizar_clima_acari, atualizar_clima
from .bairros import BAIRROS_RJ

# -------------------------------------------------------------------
# CONFIGURAÇÃO DO AGENDADOR (SCHEDULER)
# -------------------------------------------------------------------

scheduler = BackgroundScheduler()


def job_atualizar_todos_bairros():
    """Função que roda automaticamente para atualizar todos os bairros."""
    print("🔄 [JOB] Iniciando varredura de atualização...")
    db = SessionLocal()
    try:
        for bairro in BAIRROS_RJ.keys():
            try:
                atualizar_clima(bairro, db)
                print(f"   ✅ [JOB] {bairro} atualizado.")
            except Exception as e:
                print(f"   ❌ [JOB] Erro em {bairro}: {e}")
    finally:
        db.close()
    print("🏁 [JOB] Varredura finalizada.")


# -------------------------------------------------------------------
# LIFESPAN (CICLO DE VIDA DO APP)
# -------------------------------------------------------------------
# Isso garante que o agendador inicie junto com o servidor
# e faça uma atualização IMEDIATA ao ligar.

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- AO INICIAR O SERVIDOR ---
    print("🚀 Servidor iniciando... Atualizando dados agora!")

    # 1. Executa uma atualização imediata (para não esperar 1 min)
    job_atualizar_todos_bairros()

    # 2. Configura para rodar a cada 1 minuto (sincronizado com o React)
    scheduler.add_job(job_atualizar_todos_bairros, "interval", minutes=1)
    scheduler.start()

    yield  # O servidor roda aqui...

    # --- AO DESLIGAR O SERVIDOR ---
    print("🛑 Desligando agendador...")
    scheduler.shutdown()


# -------------------------------------------------------------------
# APP FASTAPI
# -------------------------------------------------------------------

app = FastAPI(
    title="ChuvaAlertaRJ API",
    version="0.1.0",
    lifespan=lifespan  # <--- Conectamos o ciclo de vida aqui
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# ENDPOINTS
# -------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


# NOVO: multi-bairros (O React consome este endpoint)
@app.get("/clima/atual")
def clima_atual(db: Session = Depends(get_db)):
    resultado = {}

    # Vamos percorrer a lista de bairros que tem coordenadas
    for bairro, coords in BAIRROS_RJ.items():
        # 1. Busca o clima no Banco de Dados
        ultimo = (
            db.query(ClimaRegistro)
            .filter(ClimaRegistro.bairro == bairro)
            .order_by(ClimaRegistro.horario_registro.desc())
            .first()
        )

        # 2. Monta o objeto base com as Coordenadas (Isso garante que o pino apareça no mapa)
        dados_bairro = {
            "lat": coords["latitude"],  # Pegando do arquivo bairros.py
            "lon": coords["longitude"]  # Pegando do arquivo bairros.py
        }

        # 3. Se tiver dados de clima, preenche o resto
        if ultimo:
            dados_bairro.update({
                "horario_registro": ultimo.horario_registro.isoformat(),
                "chuva_mm": float(ultimo.chuva_mm or 0),
                "chuva_acum_3h_prox": float(ultimo.chuva_acum_3h_prox or 0),
                "precipitacao": float(ultimo.precipitacao or 0),
                "vento_velocidade": float(ultimo.vento_velocidade or 0),
                "nivel_risco": ultimo.nivel_risco.value,
            })
        else:
            # Se não tiver clima, marca como erro mas MANTÉM as coordenadas
            dados_bairro.update({"erro": "Sem dados climáticos"})

        resultado[bairro] = dados_bairro

    return resultado

# --- Adicione isso no seu main.py ---

from typing import List
from pydantic import BaseModel


# Schema simples para a resposta do histórico (para o FastAPI documentar direito)
class HistoricoResponse(BaseModel):
    horario: str
    chuva: float
    nivel: str


@app.get("/clima/historico/{bairro}", response_model=List[HistoricoResponse])
def obter_historico(bairro: str, db: Session = Depends(get_db)):
    # Busca os últimos 24 registros (ex: últimas 24 horas se for de 1h em 1h, ou últimos 24 minutos se for min a min)
    registros = (
        db.query(ClimaRegistro)
        .filter(ClimaRegistro.bairro == bairro)
        .order_by(ClimaRegistro.horario_registro.desc())
        .limit(20)  # Pega os últimos 20 pontos
        .all()
    )

    # O banco traz do mais novo pro mais velho.
    # Para o gráfico, precisamos do contrário (esquerda p/ direita no tempo)
    registros = registros[::-1]

    resultado = []
    for reg in registros:
        resultado.append({
            "horario": reg.horario_registro.strftime("%H:%M"),  # Só a hora e minuto
            "chuva": float(reg.chuva_mm or 0),
            "nivel": reg.nivel_risco.value
        })

    return resultado

# --- ENDPOINTS MANUAIS (para testes) ---

@app.post("/internal/atualizar-clima/{bairro}")
def endpoint_atualizar_clima_multi(bairro: str, db: Session = Depends(get_db)):
    try:
        registro = atualizar_clima(bairro, db)
        return {"success": True, "bairro": bairro, "nivel_risco": registro.nivel_risco.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/internal/atualizar-clima")
def endpoint_atualizar_clima(db: Session = Depends(get_db)):
    registro = atualizar_clima_acari(db)
    return {"bairro": registro.bairro, "status": "ok"}