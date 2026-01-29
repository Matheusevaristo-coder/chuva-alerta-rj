from app.database import SessionLocal
from app.services_clima import atualizar_clima

# Lista manual dos bairros (já que estão no services_clima.py)
LISTA_BAIRROS = ["Acari", "Campo Grande", "Bonsucesso", "Botafogo", "Guadalupe"]


def main():
    print("🚀 Iniciando atualização manual (OpenWeatherMap)...\n")

    db = SessionLocal()
    try:
        for bairro in LISTA_BAIRROS:
            print(f"🔄 Consultando {bairro}...")

            # Chama a função nova que usa sua API Key
            registro = atualizar_clima(bairro, db)

            if registro:
                print(f"   ✅ Sucesso! Chuva: {registro.chuva_mm}mm | Risco: {registro.nivel_risco.value.upper()}")
            else:
                print(f"   ❌ Falha ao obter dados.")

            print("-" * 30)

    except Exception as e:
        print(f"Erro geral: {e}")
    finally:
        db.close()
        print("\n🏁 Fim da atualização manual.")


if __name__ == "__main__":
    main()