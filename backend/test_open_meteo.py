import requests
from datetime import datetime
from app.database import SessionLocal
from app.models import ClimaRegistro, NivelRiscoEnum
from app.bairros import BAIROS_RJ  # ← Adicione se tem
from app.services_clima import atualizar_clima  # ← Melhor usar serviço

def main():
    db = SessionLocal()
    try:
        for bairro, coords in BAIROS_RJ.items():
            print(f"\n=== Testando {bairro} ===")
            registro = atualizar_clima(bairro, db)  # Usa sua nova função
            print(f"✅ {bairro}: {registro.chuva_mm}mm | {registro.chuva_acum_3h_prox}mm(3h) | {registro.nivel_risco}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
