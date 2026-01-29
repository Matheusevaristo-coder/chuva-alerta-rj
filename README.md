# ⛈️ ChuvaAlertaRJ - Monitoramento de Risco Meteorológico

> Sistema de monitoramento de chuvas em tempo real focado na Defesa Civil do Rio de Janeiro, com alertas automáticos e visualização de dados críticos.

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-blue)
![Python](https://img.shields.io/badge/Backend-FastAPI-green)
![React](https://img.shields.io/badge/Frontend-React_Vite-blue)

## 🎯 O Problema

O Rio de Janeiro sofre com enchentes repentinas (flash floods). A Defesa Civil e a população precisam de dados **centralizados** e **interpretados** (não apenas números brutos) para tomada de decisão rápida.

## 💡 A Solução

O **ChuvaAlertaRJ** agrega dados meteorológicos de APIs globais, processa o risco localmente com algoritmos personalizados e exibe em um Dashboard de alta performance ("Glassmorphism UI") para visualização em salas de situação.

### 🔥 Funcionalidades Principais

- **Monitoramento em Tempo Real:** Atualização minuto a minuto via OpenWeatherMap API.
- **Cálculo de Risco Inteligente:** Algoritmo próprio que cruza precipitação atual com saturação do solo.
- **Sistema de Alerta Ativo:** Disparo automático de notificações via **Telegram Bot** para riscos Médios e Altos.
- **Dashboard Interativo:** Mapa tático e gráficos de tendência usando *Leaflet* e *Recharts*.
- **Histórico Persistente:** Armazenamento em banco de dados SQL para auditoria.

---

## 🛠️ Tecnologias Utilizadas

### Backend (API & Worker)

- **Python 3.11+**
- **FastAPI:** Para alta performance assíncrona.
- **SQLAlchemy:** ORM para gestão do banco de dados SQLite.
- **Telegram API:** Para envio de alertas push.

### Frontend (Dashboard)

- **React.js + Vite:** SPA rápida e moderna.
- **Recharts:** Visualização de dados (Gráficos de Área).
- **React-Leaflet:** Mapas interativos.
- **CSS Modules:** Design Glassmorphism focado em UI/UX para ambientes dark mode.

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos

- Python 3.10+
- Node.js 18+
- Chave de API da [OpenWeatherMap](https://openweathermap.org/)

### 1. Configurando o Backend

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\Activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
# Configure sua API KEY no arquivo services_clima.py
uvicorn app.main:app --reload