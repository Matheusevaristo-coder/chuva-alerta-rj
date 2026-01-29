import requests
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import ClimaRegistro, NivelRiscoEnum
from .bairros import BAIROS_RJ

# --- CONFIGURAÇÃO ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def enviar_alerta_telegram(bairro, nivel, chuva_agora, acum_passado, acum_futuro):
    """
    Envia alerta detalhado com contexto de acumulados.
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
        f"💧 *Agora:* {chuva_agora:.1f} mm\n"
        f"⏪ *Acumulado (6h):* {acum_passado:.1f} mm\n"
        f"⏩ *Previsão (3h):* {acum_futuro:.1f} mm\n\n"
        f"🕒 {datetime.now().strftime('%H:%M')} - _Monitore via Painel_"
    )

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}

    try:
        requests.post(url, data=data, timeout=5)
        print(f"📲 [Telegram] Alerta enviado para {bairro}")
    except Exception as e:
        print(f"❌ [Telegram] Erro: {e}")


def calcular_nivel_risco(chuva_agora, acum_passado, acum_futuro) -> NivelRiscoEnum:
    """
    Define o risco baseado na chuva atual + saturação do solo (passado) + ameaça (futuro).
    """
    chuva_agora = chuva_agora or 0
    acum_passado = acum_passado or 0
    acum_futuro = acum_futuro or 0

    # REGRA 1: Tempestade Imediata (Chuva torrencial agora)
    if chuva_agora >= 15:
        return NivelRiscoEnum.alto

    # REGRA 2: Perigo de Deslizamento (Solo cheio + vai chover mais)
    # Ex: Já choveu 30mm e vem mais 10mm por aí
    total_risco = acum_passado + acum_futuro

    if total_risco >= 40:
        return NivelRiscoEnum.alto

    # REGRA 3: Atenção/Médio
    if chuva_agora >= 5 or total_risco >= 20:
        return NivelRiscoEnum.medio

    return NivelRiscoEnum.baixo


def atualizar_clima(bairro: str, db: Session) -> ClimaRegistro:
    coords = BAIROS_RJ.get(bairro)
    if not coords:
        raise ValueError(f"Bairro não cadastrado")

    # URL MODIFICADA: Adicionamos &past_days=1 para pegar as últimas horas
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={coords['latitude']}&longitude={coords['longitude']}"
        "&current=rain,precipitation,wind_speed_10m"
        "&hourly=rain"
        "&forecast_days=1"
        "&past_days=1"  # <--- IMPORTANTE: Pede dados do passado
        "&timezone=America%2FSao_Paulo"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Erro API: {e}")
        return None

    # 1. DADOS ATUAIS
    current = data.get("current", {})
    chuva_atual = current.get("rain", 0.0)

    hora_str = current.get("time")
    horario_registro = datetime.fromisoformat(hora_str) if hora_str else datetime.now()

    # 2. CALCULAR ACUMULADOS (Passado e Futuro) usando o array 'hourly'
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    rains = hourly.get("rain", [])

    # Descobre o índice da hora atual dentro do array gigante que a API devolveu
    hora_atual_iso = horario_registro.strftime("%Y-%m-%dT%H:00")

    try:
        idx_now = times.index(hora_atual_iso)
    except ValueError:
        # Fallback: usa 24h (meio do array) se não achar exato
        idx_now = 24

    # Soma as 6 horas ANTERIORES (Saturação)
    acum_passado_6h = 0
    start_past = max(0, idx_now - 6)
    for i in range(start_past, idx_now):
        acum_passado_6h += (rains[i] or 0)

    # Soma as 3 horas FUTURAS (Previsão)
    acum_futuro_3h = 0
    end_future = min(len(rains), idx_now + 1 + 3)
    for i in range(idx_now + 1, end_future):
        acum_futuro_3h += (rains[i] or 0)

    # 3. DEFINE RISCO
    nivel_risco = calcular_nivel_risco(chuva_atual, acum_passado_6h, acum_futuro_3h)

    # Cria o registro (COM A NOVA COLUNA INCLUÍDA)
    registro = ClimaRegistro(
        bairro=bairro,
        horario_registro=horario_registro,
        chuva_mm=chuva_atual,
        precipitacao=current.get("precipitation", 0.0),
        vento_velocidade=current.get("wind_speed_10m", 0.0),
        chuva_acum_3h_prox=acum_futuro_3h,
        chuva_acum_6h_ant=acum_passado_6h,  # <--- AQUI ESTÁ A NOVIDADE
        nivel_risco=nivel_risco,
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    try:
        enviar_alerta_telegram(bairro, nivel_risco.value, chuva_atual, acum_passado_6h, acum_futuro_3h)
    except Exception as e:
        print(f"Erro Telegram: {e}")

    return registro


def atualizar_clima_acari(db: Session) -> ClimaRegistro:
    return atualizar_clima("Acari", db)