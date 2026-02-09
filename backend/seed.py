import random
from datetime import datetime
from app.database import SessionLocal
from app.models import ClimaRegistro, NivelRiscoEnum
from app.services_clima import enviar_alerta_telegram

# Lista dos bairros do seu sistema
BAIRROS = ["Acari", "Campo Grande", "Bonsucesso", "Botafogo", "Guadalupe"]


def simular_caos():
    db = SessionLocal()
    print("🚨 INICIANDO SIMULAÇÃO DE ESTADO CRÍTICO 🚨")
    print("-------------------------------------------")

    try:
        for bairro in BAIRROS:
            # Simula uma chuva torrencial (entre 60mm e 120mm)
            chuva_fake = random.uniform(60.0, 120.0)
            vento_fake = random.uniform(50.0, 90.0)  # Vento forte

            registro = ClimaRegistro(
                bairro=bairro,
                horario_registro=datetime.now(),
                chuva_mm=round(chuva_fake, 1),
                precipitacao=round(chuva_fake, 1),
                vento_velocidade=round(vento_fake, 1),
                chuva_acum_3h_prox=round(random.uniform(20, 40), 1),  # Previsão de mais chuva
                chuva_acum_6h_ant=round(random.uniform(30, 50), 1),  # Solo já encharcado
                nivel_risco=NivelRiscoEnum.alto  # FORÇA O RISCO ALTO
            )

            db.add(registro)
            db.commit()

            print(f"🔥 {bairro}: {registro.chuva_mm}mm | Vento: {registro.vento_velocidade}km/h | STATUS: CRÍTICO")

            # Tenta disparar o Telegram para testar o bot também
            try:
                enviar_alerta_telegram(bairro, "alto", chuva_fake)
            except Exception as e:
                print(f"   (Erro ao enviar Telegram: {e})")

        print("-------------------------------------------")
        print("✅ Simulação concluída! Olhe o painel agora.")

    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    simular_caos()