import requests
import os
from datetime import datetime
from sqlalchemy.orm import Session
from .models import ClimaRegistro, NivelRiscoEnum
from .bairros import BAIROS_RJ

# --- CONFIGURAÇÃO ---
#OPENWEATHERMAP
API_KEY = "a6416bde751b5b3f2a07a7d31c5b26f3"

# Configurações do Telegram
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def enviar_alerta_telegram(bairro, nivel, chuva_agora):
    """
    Envia alerta simplificado para o Telegram.
    """
    if not TOKEN or not TELEGRAM_CHAT_ID:
        return

    # Apenas envia se for risco Médio ou Alto
    if nivel not in ["alto", "medio"]:
        return

    emoji = "🚨" if nivel == "alto" else "⚠️"

    msg = (
        f"{emoji} *ALERTA EVARISTO SOLUTIONS* {emoji}\n\n"
        f"📍 *Bairro:* {bairro}\n"
        f"📢 *Risco:* {nivel.upper()}\n\n"
        f"💧 *Chuva (1h):* {chuva_agora:.1f} mm\n"
        f"💨 *Vento:* monitorado\n\n"
        f"🕒 {datetime.now().strftime('%H:%M')} - _Fonte: OpenWeather_"
    )

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}

    try:
        requests.post(url, data=data, timeout=5)
        print(f"📲 [Telegram] Alerta enviado para {bairro}")
    except Exception as e:
        print(f"❌ [Telegram] Erro: {e}")


def calcular_nivel_risco_owm(chuva_1h) -> NivelRiscoEnum:
    """
    Define o risco baseado na chuva da última hora (OpenWeatherMap).
    """
    chuva_1h = chuva_1h or 0.0

    # REGRA 1: Chuva Forte (> 15mm/h já é alerta forte em área urbana)
    if chuva_1h >= 15:
        return NivelRiscoEnum.alto

    # REGRA 2: Chuva Moderada/Atenção
    if chuva_1h >= 5:
        return NivelRiscoEnum.medio

    return NivelRiscoEnum.baixo


def atualizar_clima(bairro: str, db: Session) -> ClimaRegistro:
    coords = BAIROS_RJ.get(bairro)
    if not coords:
        print(f"Bairro {bairro} não encontrado.")
        return None

    # URL DA OPENWEATHERMAP (Plano Grátis / Current Weather)
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": coords["latitude"],
        "lon": coords["longitude"],
        "appid": API_KEY,
        "units": "metric",
        "lang": "pt_br"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"❌ Erro API OpenWeather ({bairro}): {e}")
        return None

    # --- EXTRAÇÃO DE DADOS (OpenWeatherMap) ---

    # 1. Chuva (Campo 'rain' -> '1h'). Se não estiver chovendo, o campo nem vem.
    chuva_obj = data.get("rain", {})
    chuva_atual = chuva_obj.get("1h", 0.0)

    # 2. Vento (Vem em m/s, convertemos para km/h)
    vento_ms = data.get("wind", {}).get("speed", 0.0)
    vento_kmh = vento_ms * 3.6

    # 3. Data/Hora
    horario_registro = datetime.now()

    # 4. Acumulados (Como a API Grátis não dá histórico, zeramos para não quebrar o banco)
    acum_passado_6h = 0.0
    acum_futuro_3h = 0.0

    # 5. Risco
    nivel_risco = calcular_nivel_risco_owm(chuva_atual)

    # Cria o registro no Banco
    registro = ClimaRegistro(
        bairro=bairro,
        horario_registro=horario_registro,
        chuva_mm=chuva_atual,
        precipitacao=chuva_atual,  # OWM usa o mesmo dado
        vento_velocidade=vento_kmh,
        chuva_acum_3h_prox=acum_futuro_3h,
        chuva_acum_6h_ant=acum_passado_6h,
        nivel_risco=nivel_risco,
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    print(f"✅ {bairro}: {chuva_atual}mm (Risco: {nivel_risco.value})")

    # Tenta enviar Telegram se for perigoso
    try:
        enviar_alerta_telegram(bairro, nivel_risco.value, chuva_atual)
    except Exception as e:
        print(f"Erro Telegram: {e}")

    return registro


def atualizar_clima_acari(db: Session) -> ClimaRegistro:
    # Função legada, apenas redireciona
    return atualizar_clima("Acari", db)