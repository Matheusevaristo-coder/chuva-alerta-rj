import random
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import ClimaRegistro, NivelRiscoEnum

# Cria as tabelas se não existirem
Base.metadata.create_all(bind=engine)

db = SessionLocal()

print("🌱 Plantando dados falsos para teste...")

bairro_teste = "Guadalupe"
agora = datetime.now()

# Gera 1 dado a cada 10 minutos nas últimas 6 horas
for i in range(36):
    tempo_atras = agora - timedelta(minutes=i * 10)

    # Simula uma chuva que aumenta e diminui
    chuva_fake = max(0, 15 - abs(18 - i)) + random.uniform(0, 2)

    nivel = "baixo"
    if chuva_fake > 10: nivel = "medio"
    if chuva_fake > 20: nivel = "alto"

    registro = ClimaRegistro(
        bairro=bairro_teste,
        horario_registro=tempo_atras,
        chuva_mm=round(chuva_fake, 1),
        precipitacao=round(chuva_fake, 1),
        vento_velocidade=random.uniform(5, 15),
        chuva_acum_3h_prox=0,
        chuva_acum_6h_ant=0,
        nivel_risco=NivelRiscoEnum(nivel)
    )
    db.add(registro)

db.commit()
print(f"✅ Sucesso! 36 registros falsos criados para {bairro_teste}.")
print("🔄 Atualize o site e clique em 'Ver Tendência' em Guadalupe.")