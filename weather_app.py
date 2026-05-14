"""
🌦️ Weather App — Streamlit
Полнофункциональное погодное приложение с анимациями, грозопеленгацией и режимом астрономии.
Запуск: streamlit run weather_app.py
Зависимости: streamlit, pandas, plotly, requests, numpy
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import math

# ─────────────────────────────────────────────
# КОНФИГУРАЦИЯ ГОРОДОВ
# ─────────────────────────────────────────────
CITIES = {
    "Минск":      {"lat": 53.9045, "lon": 27.5615, "tz": "Europe/Minsk"},
    "Харьков":    {"lat": 49.9935, "lon": 36.2304, "tz": "Europe/Kiev"},
    "Ужгород":    {"lat": 48.6208, "lon": 22.2879, "tz": "Europe/Kiev"},
    "Москва":     {"lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow"},
    "Люберцы":    {"lat": 55.6778, "lon": 37.8927, "tz": "Europe/Moscow"},
    "Серпухов":   {"lat": 54.9167, "lon": 37.4167, "tz": "Europe/Moscow"},
    "Владимир":   {"lat": 56.1366, "lon": 40.3966, "tz": "Europe/Moscow"},
    "Гороховец":  {"lat": 56.2003, "lon": 42.6867, "tz": "Europe/Moscow"},
    "Пенза":      {"lat": 53.1959, "lon": 45.0183, "tz": "Europe/Moscow"},
    "Тамбов":     {"lat": 52.7212, "lon": 41.4522, "tz": "Europe/Moscow"},
    "Киев":       {"lat": 50.4501, "lon": 30.5234, "tz": "Europe/Kiev"},
    "Алма-Ата":   {"lat": 43.2220, "lon": 76.8512, "tz": "Asia/Almaty"},
    "Ташкент":    {"lat": 41.2995, "lon": 69.2401, "tz": "Asia/Tashkent"},
    "Баку":       {"lat": 40.4093, "lon": 49.8671, "tz": "Asia/Baku"},
    "Ереван":     {"lat": 40.1792, "lon": 44.4991, "tz": "Asia/Yerevan"},
    "Тбилиси":    {"lat": 41.6938, "lon": 44.8015, "tz": "Asia/Tbilisi"},
    "Кишинёв":    {"lat": 47.0105, "lon": 28.8638, "tz": "Europe/Chisinau"},
    "Рига":       {"lat": 56.9460, "lon": 24.1059, "tz": "Europe/Riga"},
    "Вильнюс":    {"lat": 54.6872, "lon": 25.2797, "tz": "Europe/Vilnius"},
    "Таллин":     {"lat": 59.4370, "lon": 24.7536, "tz": "Europe/Tallinn"},
}

# ─────────────────────────────────────────────
# ТЕМЫ ОФОРМЛЕНИЯ
# ─────────────────────────────────────────────
THEMES = {
    "Тёмная": {
        "bg": "#0d1117", "bg2": "#161b22", "card": "#1c2333",
        "text": "#e6edf3", "text2": "#8b949e", "accent": "#58a6ff",
        "accent2": "#3fb950", "border": "#30363d", "shadow": "rgba(0,0,0,0.5)",
    },
    "Светлая": {
        "bg": "#f0f4f8", "bg2": "#ffffff", "card": "#ffffff",
        "text": "#1a202c", "text2": "#718096", "accent": "#3182ce",
        "accent2": "#38a169", "border": "#e2e8f0", "shadow": "rgba(0,0,0,0.1)",
    },
    "Бежевая": {
        "bg": "#f5f0e8", "bg2": "#ede8dc", "card": "#faf7f2",
        "text": "#3d2b1f", "text2": "#7a6452", "accent": "#c17f3e",
        "accent2": "#6b8f52", "border": "#d4c9b8", "shadow": "rgba(60,40,20,0.15)",
    },
    "Амбиент": {
        "bg": "#1a1a2e", "bg2": "#16213e", "card": "#0f3460",
        "text": "#e0e0e0", "text2": "#a0a0b0", "accent": "#e94560",
        "accent2": "#53d8fb", "border": "#1a3a5c", "shadow": "rgba(0,0,0,0.6)",
    },
}

# ─────────────────────────────────────────────
# CSS АНИМАЦИИ ПОГОДЫ
# ─────────────────────────────────────────────
def get_weather_animation(wmo_code: int, t: dict) -> str:
    """Возвращает HTML+CSS анимацию в зависимости от WMO-кода погоды."""

    # Определяем тип погоды по WMO коду
    if wmo_code <= 1:
        weather_type = "sunny"
    elif wmo_code <= 3:
        weather_type = "cloudy"
    elif wmo_code in range(95, 100):
        weather_type = "storm"
    elif wmo_code in range(51, 82):
        weather_type = "rain"
    else:
        weather_type = "cloudy"

    card_bg = t["card"]
    accent  = t["accent"]

    if weather_type == "sunny":
        return f"""
<div class="weather-anim-box" style="background:linear-gradient(180deg,#1a3a5c 0%,#ff7043 40%,#ffb300 70%,{card_bg} 100%);">
  <style>
    @keyframes sunrise {{
      0%   {{ transform: translateY(60px) scale(0.7); opacity:0.3; }}
      100% {{ transform: translateY(0px) scale(1);   opacity:1; }}
    }}
    @keyframes ray-spin {{
      from {{ transform: rotate(0deg); }}
      to   {{ transform: rotate(360deg); }}
    }}
    @keyframes shimmer {{
      0%,100% {{ opacity:0.7; }} 50% {{ opacity:1; }}
    }}
    .sun-wrap {{ position:absolute; bottom:30px; left:50%; transform:translateX(-50%); animation:sunrise 2s ease-out forwards; }}
    .sun-core {{ width:70px; height:70px; background:radial-gradient(circle,#fff700,#ffb300); border-radius:50%; box-shadow:0 0 40px #ffb300,0 0 80px #ff8c00; }}
    .sun-rays {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); animation:ray-spin 8s linear infinite; }}
    .ray {{ position:absolute; width:4px; height:90px; background:linear-gradient(transparent,#ffb30088,transparent); border-radius:2px; top:-45px; left:-2px; }}
    .shimmer-overlay {{ position:absolute; inset:0; background:radial-gradient(ellipse at 50% 100%,#ffb30033 0%,transparent 70%); animation:shimmer 3s ease-in-out infinite; }}
  </style>
  <div class="shimmer-overlay"></div>
  <div class="sun-wrap">
    <div class="sun-rays">
      {''.join(f'<div class="ray" style="transform:rotate({i*30}deg)"></div>' for i in range(12))}
    </div>
    <div class="sun-core"></div>
  </div>
</div>"""

    elif weather_type == "cloudy":
        return f"""
<div class="weather-anim-box" style="background:linear-gradient(180deg,#2c3e50 0%,#4a5568 50%,{card_bg} 100%);">
  <style>
    @keyframes cloud-drift {{ 0%,100% {{ transform:translateX(0); }} 50% {{ transform:translateX(18px); }} }}
    @keyframes sun-peek    {{ 0%,100% {{ opacity:0.3; transform:translateX(-50%) translateY(10px); }} 50% {{ opacity:0.85; transform:translateX(-50%) translateY(0); }} }}
    .cloud-sun {{ position:absolute; bottom:25px; left:50%; transform:translateX(-50%); width:55px; height:55px; background:radial-gradient(#fff176,#fdd835); border-radius:50%; box-shadow:0 0 30px #fdd835; animation:sun-peek 5s ease-in-out infinite; }}
    .cloud {{ position:absolute; background:#b0bec5; border-radius:50px; opacity:0.9; }}
    .c1 {{ width:110px; height:45px; bottom:40px; left:20%; animation:cloud-drift 6s ease-in-out infinite; }}
    .c2 {{ width:140px; height:55px; bottom:55px; left:40%; animation:cloud-drift 8s ease-in-out infinite reverse; }}
    .c3 {{ width:90px;  height:38px; bottom:35px; right:15%; animation:cloud-drift 7s ease-in-out infinite; }}
    .c1::before {{ content:''; position:absolute; width:60px; height:60px; background:#b0bec5; border-radius:50%; top:-25px; left:15px; }}
    .c2::before {{ content:''; position:absolute; width:75px; height:70px; background:#b0bec5; border-radius:50%; top:-35px; left:25px; }}
    .c3::before {{ content:''; position:absolute; width:50px; height:50px; background:#b0bec5; border-radius:50%; top:-22px; left:12px; }}
  </style>
  <div class="cloud-sun"></div>
  <div class="cloud c1"></div>
  <div class="cloud c2"></div>
  <div class="cloud c3"></div>
</div>"""

    elif weather_type == "rain":
        drops = ''.join(
            f'<div class="drop" style="left:{np.random.randint(5,95)}%;'
            f'animation-delay:{np.random.random()*2:.2f}s;'
            f'animation-duration:{0.5+np.random.random()*0.5:.2f}s;'
            f'height:{np.random.randint(15,30)}px;opacity:{0.4+np.random.random()*0.5:.2f}"></div>'
            for _ in range(35)
        )
        return f"""
<div class="weather-anim-box" style="background:linear-gradient(180deg,#1a1a2e 0%,#2d3748 60%,{card_bg} 100%);overflow:hidden;">
  <style>
    @keyframes fall {{ 0% {{ transform:translateY(-20px); opacity:0; }} 80% {{ opacity:1; }} 100% {{ transform:translateY(130px); opacity:0; }} }}
    @keyframes cloud-sway {{ 0%,100% {{ transform:translateX(0); }} 50% {{ transform:translateX(10px); }} }}
    @keyframes puddle {{ 0%,100% {{ transform:scale(1); opacity:0.5; }} 50% {{ transform:scale(1.1); opacity:0.8; }} }}
    .drop {{ position:absolute; width:2px; background:linear-gradient(to bottom,transparent,#90caf9); border-radius:2px; top:0; animation:fall linear infinite; }}
    .rain-cloud {{ position:absolute; background:#455a64; border-radius:50px; }}
    .rc1 {{ width:120px; height:50px; top:5px;  left:15%; animation:cloud-sway 7s ease-in-out infinite; }}
    .rc2 {{ width:150px; height:60px; top:15px; left:40%; animation:cloud-sway 9s ease-in-out infinite reverse; }}
    .rc3 {{ width:100px; height:45px; top:8px;  right:12%; animation:cloud-sway 6s ease-in-out infinite; }}
    .rc1::before,.rc2::before,.rc3::before {{ content:''; position:absolute; background:#455a64; border-radius:50%; }}
    .rc1::before {{ width:65px; height:65px; top:-30px; left:20px; }}
    .rc2::before {{ width:80px; height:75px; top:-38px; left:30px; }}
    .rc3::before {{ width:55px; height:55px; top:-25px; left:18px; }}
    .puddle {{ position:absolute; bottom:6px; border-radius:50%; background:#4fc3f733; animation:puddle 2s ease-in-out infinite; }}
  </style>
  <div class="rain-cloud rc1"></div>
  <div class="rain-cloud rc2"></div>
  <div class="rain-cloud rc3"></div>
  {drops}
  <div class="puddle" style="width:60px;height:12px;left:20%;animation-delay:0.3s"></div>
  <div class="puddle" style="width:90px;height:16px;left:50%;animation-delay:0.8s"></div>
  <div class="puddle" style="width:50px;height:10px;right:20%;animation-delay:1.2s"></div>
</div>"""

    else:  # storm
        drops = ''.join(
            f'<div class="sdrop" style="left:{np.random.randint(5,95)}%;'
            f'animation-delay:{np.random.random()*1.5:.2f}s;'
            f'animation-duration:{0.3+np.random.random()*0.4:.2f}s;'
            f'height:{np.random.randint(20,40)}px"></div>'
            for _ in range(40)
        )
        return f"""
<div class="weather-anim-box" style="background:linear-gradient(180deg,#0d0d1a 0%,#1a1a2e 60%,{card_bg} 100%);overflow:hidden;">
  <style>
    @keyframes sfall    {{ 0% {{ transform:translateY(-20px) translateX(0); opacity:0; }} 100% {{ transform:translateY(140px) translateX(-10px); opacity:0.9; }} }}
    @keyframes flash    {{ 0%,90%,100% {{ opacity:0; }} 92%,96% {{ opacity:1; }} }}
    @keyframes bolt-anim {{ 0%,85%,100% {{ opacity:0; transform:scaleY(0); }} 87%,93% {{ opacity:1; transform:scaleY(1); }} }}
    @keyframes thunder-glow {{ 0%,89%,100% {{ background:#0d0d1a; }} 90%,95% {{ background:#1a2a4a; }} }}
    .storm-bg {{ position:absolute; inset:0; animation:thunder-glow 4s linear infinite; z-index:0; }}
    .sdrop {{ position:absolute; width:2px; background:linear-gradient(to bottom,transparent,#64b5f6); border-radius:2px; top:0; animation:sfall linear infinite; }}
    .storm-cloud {{ position:absolute; background:#263238; border-radius:50px; z-index:1; }}
    .sc1 {{ width:130px; height:55px; top:3px;  left:10%; }}
    .sc2 {{ width:160px; height:65px; top:10px; left:38%; }}
    .sc3 {{ width:110px; height:48px; top:5px;  right:10%; }}
    .sc1::before,.sc2::before,.sc3::before {{ content:''; position:absolute; background:#263238; border-radius:50%; }}
    .sc1::before {{ width:70px; height:70px; top:-32px; left:22px; }}
    .sc2::before {{ width:88px; height:82px; top:-42px; left:32px; }}
    .sc3::before {{ width:62px; height:60px; top:-28px; left:20px; }}
    .lightning-flash {{ position:absolute; inset:0; background:rgba(200,220,255,0.12); animation:flash 4s linear infinite; z-index:2; pointer-events:none; }}
    .bolt {{ position:absolute; z-index:3; font-size:40px; color:#fff176; text-shadow:0 0 20px #ffeb3b,0 0 40px #ff8f00; transform-origin:top center; }}
    .bolt1 {{ top:50px; left:35%; animation:bolt-anim 4s linear infinite; }}
    .bolt2 {{ top:45px; left:62%; animation:bolt-anim 4s linear infinite 2s; }}
  </style>
  <div class="storm-bg"></div>
  <div class="storm-cloud sc1"></div>
  <div class="storm-cloud sc2"></div>
  <div class="storm-cloud sc3"></div>
  {drops}
  <div class="lightning-flash"></div>
  <div class="bolt bolt1">⚡</div>
  <div class="bolt bolt2">⚡</div>
</div>"""


# ─────────────────────────────────────────────
# ЗАГРУЗКА ДАННЫХ
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def fetch_weather(lat: float, lon: float) -> dict | None:
    """Загружает данные о погоде из Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": (
            "temperature_2m,relativehumidity_2m,dewpoint_2m,"
            "apparent_temperature,precipitation_probability,precipitation,"
            "weathercode,surface_pressure,cloudcover,"
            "windspeed_10m,winddirection_10m,visibility,"
            "uv_index,cape,lightning_potential"
        ),
        "daily": (
            "weathercode,temperature_2m_max,temperature_2m_min,"
            "sunrise,sunset,uv_index_max,windspeed_10m_max,"
            "precipitation_probability_max,precipitation_sum"
        ),
        "wind_speed_unit": "ms",
        "timezone": "auto",
        "forecast_days": 7,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return None


# ─────────────────────────────────────────────
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ─────────────────────────────────────────────
def wind_direction_text(deg: float) -> str:
    directions = ["С","СВ","В","ЮВ","Ю","ЮЗ","З","СЗ"]
    idx = round(deg / 45) % 8
    return directions[idx]

def wmo_description(code: int) -> str:
    wmo = {
        0:"Ясно", 1:"Преимущественно ясно", 2:"Переменная облачность",
        3:"Облачно", 45:"Туман", 48:"Изморозь", 51:"Лёгкая морось",
        53:"Умеренная морось", 55:"Сильная морось", 61:"Лёгкий дождь",
        63:"Умеренный дождь", 65:"Сильный дождь", 71:"Лёгкий снег",
        73:"Умеренный снег", 75:"Сильный снег", 77:"Снежная крупа",
        80:"Ливень (слабый)", 81:"Ливень (умеренный)", 82:"Ливень (сильный)",
        85:"Снегопад (слабый)", 86:"Снегопад (сильный)",
        95:"Гроза", 96:"Гроза с градом", 99:"Гроза с сильным градом",
    }
    return wmo.get(int(code), f"Код {code}")

def storm_index(cape: float, lightning: float, humidity: float) -> dict:
    """Вычисляет грозовой индекс на основе CAPE, lightning_potential и влажности."""
    # CAPE: 0-500 слабый, 500-1500 умеренный, 1500-3000 сильный, >3000 экстремальный
    cape_score = min(cape / 3000, 1.0)
    # Lightning potential: 0-100
    lightning_score = min(lightning / 100, 1.0)
    # Влажность > 70% усиливает шанс грозы
    hum_factor = max(0, (humidity - 50) / 50)
    # Итоговый индекс
    score = cape_score * 0.5 + lightning_score * 0.35 + hum_factor * 0.15
    pct = round(score * 100)

    if score < 0.2:
        level, color, emoji = "Низкая",    "#43a047", "🟢"
    elif score < 0.45:
        level, color, emoji = "Средняя",   "#fb8c00", "🟡"
    elif score < 0.7:
        level, color, emoji = "Высокая",   "#e53935", "🔴"
    else:
        level, color, emoji = "Экстремальная", "#7b1fa2", "🟣"

    return {"level": level, "color": color, "emoji": emoji, "pct": pct, "score": score}

def sky_clarity(cloudcover: float, humidity: float) -> float:
    """Индекс чистоты неба 0-100%."""
    cloud_factor = (100 - cloudcover) / 100
    hum_factor   = max(0, (100 - humidity) / 100)
    return round((cloud_factor * 0.7 + hum_factor * 0.3) * 100)

def moon_phase_text(day_of_year: int) -> tuple[str, float]:
    """Упрощённая фаза луны (синодический цикл ~29.5 дней)."""
    phase_fraction = (day_of_year % 29.5) / 29.5
    if phase_fraction < 0.03 or phase_fraction > 0.97:
        return "🌑 Новолуние", phase_fraction
    elif phase_fraction < 0.22:
        return "🌒 Растущий серп", phase_fraction
    elif phase_fraction < 0.28:
        return "🌓 Первая четверть", phase_fraction
    elif phase_fraction < 0.47:
        return "🌔 Растущая луна", phase_fraction
    elif phase_fraction < 0.53:
        return "🌕 Полнолуние", phase_fraction
    elif phase_fraction < 0.72:
        return "🌖 Убывающая луна", phase_fraction
    elif phase_fraction < 0.78:
        return "🌗 Последняя четверть", phase_fraction
    else:
        return "🌘 Убывающий серп", phase_fraction

def visible_constellations(lat: float, month: int) -> list[str]:
    """Простая логика видимых созвездий по сезону и широте."""
    # Северное полушарие (lat > 20)
    seasonal = {
        (12,1,2): ["Орион 🌟","Телец 🐂","Близнецы ♊","Возничий 🐐","Эридан 🌊","Персей ⚔️"],
        (3,4,5):  ["Лев 🦁","Дева ♍","Рак 🦀","Гидра 🐉","Ворон 🐦","Чаша 🏆"],
        (6,7,8):  ["Скорпион 🦂","Стрелец 🏹","Орёл 🦅","Лебедь 🦢","Лира 🎵","Геркулес 💪"],
        (9,10,11):["Пегас 🐴","Андромеда ✨","Рыбы 🐠","Водолей 💧","Козерог 🐐","Кит 🐋"],
    }
    # Всесезонные (циркумполярные для широт > 45°)
    circumpolar = ["Большая Медведица 🐻","Малая Медведица ⭐","Кассиопея 👑","Дракон 🐲","Цефей 🔱"]
    result = list(circumpolar[:3])
    for months_tuple, consts in seasonal.items():
        if month in months_tuple:
            result.extend(consts[:4])
            break
    return result

def astro_conditions(clarity: float, phase_fraction: float, visibility_km: float) -> dict:
    """Оценивает условия для астрофото."""
    # Луна: около полнолуния (0.4-0.6) — плохо
    moon_interference = 1 - abs(phase_fraction - 0.5) * 2
    moon_penalty = moon_interference * 30

    score = clarity * 0.5 + min(visibility_km / 30, 1.0) * 30 - moon_penalty
    score = max(0, min(100, score))

    if score >= 65:
        verdict, color = "Отлично ✨", "#43a047"
    elif score >= 35:
        verdict, color = "Средне 🌤", "#fb8c00"
    else:
        verdict, color = "Плохо 🌧", "#e53935"

    return {"verdict": verdict, "color": color, "score": round(score)}


# ─────────────────────────────────────────────
# GRAFИКИ PLOTLY
# ─────────────────────────────────────────────
def make_forecast_charts(hourly: dict, t: dict) -> list:
    """Строит 4 графика прогноза на 5 дней."""
    times = pd.to_datetime(hourly["time"])
    mask  = times <= times[0] + pd.Timedelta(days=5)

    def base_layout(title):
        return dict(
            title=dict(text=title, font=dict(color=t["text"], size=14)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=t["text2"]),
            xaxis=dict(gridcolor=t["border"], showgrid=True),
            yaxis=dict(gridcolor=t["border"], showgrid=True),
            margin=dict(l=40, r=20, t=40, b=40),
            height=240,
        )

    charts = []

    # Температура
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=times[mask], y=np.array(hourly["temperature_2m"])[mask],
        fill="tozeroy", line=dict(color=t["accent"], width=2),
        fillcolor="rgba(88,166,255,0.2)", name="Температура °C"
    ))
    fig1.add_trace(go.Scatter(
        x=times[mask], y=np.array(hourly["apparent_temperature"])[mask],
        line=dict(color=t["accent2"], width=1.5, dash="dot"), name="Ощущается"
    ))
    fig1.update_layout(**base_layout("🌡 Температура (°C)"))
    charts.append(fig1)

    # Влажность
    fig2 = go.Figure(go.Bar(
        x=times[mask], y=np.array(hourly["relativehumidity_2m"])[mask],
        marker_color="rgba(63,185,80,0.75)", name="Влажность %"
    ))
    fig2.update_layout(**base_layout("💧 Влажность (%)"))
    charts.append(fig2)

    # Давление
    fig3 = go.Figure(go.Scatter(
        x=times[mask], y=np.array(hourly["surface_pressure"])[mask],
        line=dict(color="#ff7043", width=2), fill="tozeroy",
        fillcolor="rgba(255,112,67,0.2)", name="Давление гПа"
    ))
    fig3.update_layout(**base_layout("🌀 Давление (гПа)"))
    charts.append(fig3)

    # Скорость ветра
    fig4 = go.Figure(go.Scatter(
        x=times[mask], y=np.array(hourly["windspeed_10m"])[mask],
        line=dict(color="#ab47bc", width=2), fill="tozeroy",
        fillcolor="rgba(171,71,188,0.2)", name="Ветер м/с"
    ))
    fig4.update_layout(**base_layout("💨 Скорость ветра (м/с)"))
    charts.append(fig4)

    return charts


# ─────────────────────────────────────────────
# ПРИМЕНЕНИЕ ТЕМЫ
# ─────────────────────────────────────────────
def apply_theme(t: dict):
    st.markdown(f"""
<style>
  /* Основной фон */
  .stApp, [data-testid="stAppViewContainer"] {{
    background-color: {t['bg']} !important;
    color: {t['text']} !important;
  }}
  /* Сайдбар */
  [data-testid="stSidebar"] {{
    background-color: {t['bg2']} !important;
    border-right: 1px solid {t['border']};
  }}
  /* Карточки */
  .metric-card {{
    background: {t['card']};
    border: 1px solid {t['border']};
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 2px 12px {t['shadow']};
    margin-bottom: 12px;
    transition: transform 0.2s;
  }}
  .metric-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px {t['shadow']}; }}
  .metric-label {{ font-size: 0.72rem; color: {t['text2']}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }}
  .metric-value {{ font-size: 1.6rem; font-weight: 700; color: {t['text']}; line-height: 1.1; }}
  .metric-sub   {{ font-size: 0.82rem; color: {t['text2']}; margin-top: 2px; }}
  /* Анимационный блок */
  .weather-anim-box {{
    position: relative; width: 100%; height: 140px;
    border-radius: 16px; overflow: hidden;
    margin-bottom: 24px;
  }}
  /* Заголовок города */
  .city-header {{
    font-size: 2rem; font-weight: 800; color: {t['text']};
    margin: 0; line-height: 1.1;
  }}
  .city-sub {{
    font-size: 0.9rem; color: {t['text2']};
    margin-top: 4px;
  }}
  /* Секция */
  .section-title {{
    font-size: 1rem; font-weight: 700; color: {t['accent']};
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 22px 0 12px;
    border-left: 3px solid {t['accent']};
    padding-left: 10px;
  }}
  /* Storm bar */
  .storm-bar-outer {{
    background: {t['border']}; border-radius: 8px;
    height: 10px; width: 100%; margin-top: 8px;
  }}
  /* Selectbox, слайдеры — цвет текста */
  label, .stSelectbox label, [data-testid="stWidgetLabel"] {{
    color: {t['text2']} !important;
  }}
  /* Divider */
  hr {{ border-color: {t['border']}; }}
  /* Radio */
  [data-testid="stRadio"] label {{ color: {t['text']} !important; }}
  /* Кнопки */
  .stButton>button {{
    background: {t['accent']}22; border: 1px solid {t['accent']}66;
    color: {t['text']}; border-radius: 8px;
  }}
  .stButton>button:hover {{
    background: {t['accent']}44;
  }}
  /* Убираем лишние паддинги Streamlit */
  .block-container {{ padding-top: 1.5rem !important; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ОСНОВНОЕ ПРИЛОЖЕНИЕ
# ─────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="🌦 Погода",
        page_icon="🌦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── Сайдбар ──────────────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ Настройки")

        city_name = st.selectbox("🏙 Город", list(CITIES.keys()), index=0)
        city = CITIES[city_name]

        theme_name = st.radio("🎨 Тема", list(THEMES.keys()), index=0)
        t = THEMES[theme_name]

        astro_mode = st.toggle("🔭 Режим Астрономия", value=False)

        st.markdown("---")
        st.markdown(f"<span style='color:{t['text2']};font-size:0.8rem'>📍 {city['lat']:.4f}°N, {city['lon']:.4f}°E</span>", unsafe_allow_html=True)

    # Применяем тему
    apply_theme(t)

    # ── Загрузка данных ───────────────────────
    with st.spinner("Загружаю данные о погоде…"):
        data = fetch_weather(city["lat"], city["lon"])

    if not data:
        st.error("Не удалось загрузить данные. Проверьте соединение.")
        return

    cw = data["current_weather"]
    hourly = data["hourly"]
    daily  = data["daily"]

    # Текущий час в hourly
    now_str   = cw["time"]
    try:
        now_idx = hourly["time"].index(now_str)
    except ValueError:
        now_idx = 0

    def h(key):
        val = hourly.get(key, [None] * (now_idx + 1))
        return val[now_idx] if val else None

    # Текущие значения
    temp        = cw.get("temperature", h("temperature_2m"))
    feelslike   = h("apparent_temperature") or temp
    humidity    = h("relativehumidity_2m") or 0
    pressure    = h("surface_pressure") or 1013
    wind_speed  = cw.get("windspeed", h("windspeed_10m")) or 0
    wind_dir    = cw.get("winddirection", h("winddirection_10m")) or 0
    cloudcover  = h("cloudcover") or 0
    visibility  = (h("visibility") or 10000) / 1000  # метры → км
    uv_index    = h("uv_index") or 0
    precip_prob = h("precipitation_probability") or 0
    cape        = h("cape") or 0
    lightning   = h("lightning_potential") or 0
    wmo_code    = int(cw.get("weathercode", 0))

    storm = storm_index(cape, lightning, humidity)

    # Восход / закат
    sunrise_str = daily["sunrise"][0] if daily.get("sunrise") else None
    sunset_str  = daily["sunset"][0]  if daily.get("sunset")  else None

    def parse_dt(s):
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None

    sunrise_dt = parse_dt(sunrise_str)
    sunset_dt  = parse_dt(sunset_str)
    now_dt     = datetime.now()
    time_to_sunset = ""
    if sunset_dt:
        diff = sunset_dt - now_dt
        if diff.total_seconds() > 0:
            h_left = int(diff.total_seconds() // 3600)
            m_left = int((diff.total_seconds() % 3600) // 60)
            time_to_sunset = f"{h_left}ч {m_left}мин"

    # ── АНИМАЦИЯ ─────────────────────────────
    st.markdown(get_weather_animation(wmo_code, t), unsafe_allow_html=True)

    # ── ЗАГОЛОВОК ────────────────────────────
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"""
<div>
  <div class="city-header">{city_name}</div>
  <div class="city-sub">{wmo_description(wmo_code)} · Обновлено: {now_str[:16].replace('T',' ')}</div>
</div>""", unsafe_allow_html=True)
    with col_h2:
        st.markdown(f"""
<div style="text-align:right;padding-top:4px">
  <div style="font-size:3rem;font-weight:900;color:{t['text']};line-height:1">{temp:.1f}°C</div>
  <div style="color:{t['text2']};font-size:0.88rem">Ощущается {feelslike:.1f}°C</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ══════════════════════════════════════════
    # РЕЖИМ АСТРОНОМИЯ
    # ══════════════════════════════════════════
    if astro_mode:
        st.markdown("<div class='section-title'>🔭 Режим Астрономия</div>", unsafe_allow_html=True)

        doy   = now_dt.timetuple().tm_yday
        month = now_dt.month
        clarity = sky_clarity(cloudcover, humidity)
        moon_text, moon_frac = moon_phase_text(doy)
        astro = astro_conditions(clarity, moon_frac, visibility)
        constellations = visible_constellations(city["lat"], month)

        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            st.markdown(f"""
<div class="metric-card">
  <div class="metric-label">Чистота неба</div>
  <div class="metric-value" style="color:{t['accent']}">{clarity}%</div>
  <div class="metric-sub">Облачность {cloudcover:.0f}%, влажность {humidity:.0f}%</div>
</div>""", unsafe_allow_html=True)
        with ac2:
            st.markdown(f"""
<div class="metric-card">
  <div class="metric-label">Фаза луны</div>
  <div class="metric-value">{moon_text}</div>
  <div class="metric-sub">Индекс яркости {moon_frac*100:.0f}%</div>
</div>""", unsafe_allow_html=True)
        with ac3:
            st.markdown(f"""
<div class="metric-card">
  <div class="metric-label">Условия для астрофото</div>
  <div class="metric-value" style="color:{astro['color']}">{astro['verdict']}</div>
  <div class="metric-sub">Оценка {astro['score']}/100</div>
</div>""", unsafe_allow_html=True)

        # Созвездия
        st.markdown("<div class='section-title'>🌌 Видимые созвездия</div>", unsafe_allow_html=True)
        const_cols = st.columns(3)
        for i, c in enumerate(constellations[:6]):
            with const_cols[i % 3]:
                st.markdown(f"""
<div class="metric-card" style="padding:10px 14px">
  <div style="font-size:0.95rem;color:{t['text']}">{c}</div>
</div>""", unsafe_allow_html=True)

        # Лучшее время наблюдений
        if sunset_dt and sunrise_dt:
            next_sunrise = sunrise_dt + timedelta(days=1)
            best_start   = sunset_dt + timedelta(hours=1, minutes=30)
            best_end     = next_sunrise - timedelta(hours=1)
            st.markdown(f"""
<div class="metric-card" style="margin-top:12px">
  <div class="metric-label">⏰ Идеальное время наблюдений</div>
  <div class="metric-value" style="font-size:1.1rem;color:{t['accent']}">
    {best_start.strftime('%H:%M')} — {best_end.strftime('%H:%M')}
  </div>
  <div class="metric-sub">Через 1.5ч после заката до 1ч до рассвета</div>
</div>""", unsafe_allow_html=True)

        st.markdown("---")

    # ══════════════════════════════════════════
    # ОСНОВНЫЕ МЕТРИКИ
    # ══════════════════════════════════════════
    st.markdown("<div class='section-title'>📊 Текущие условия</div>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        (m1, "💧 Влажность",    f"{humidity:.0f}%",       ""),
        (m2, "🌀 Давление",     f"{pressure:.0f} гПа",    ""),
        (m3, "☀️ УФ-индекс",   f"{uv_index:.1f}",        ""),
        (m4, "👁 Видимость",    f"{visibility:.1f} км",   ""),
    ]
    for col, label, val, sub in metrics:
        with col:
            st.markdown(f"""
<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{val}</div>
  <div class="metric-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

    m5, m6, m7, m8 = st.columns(4)
    metrics2 = [
        (m5, "💨 Ветер",         f"{wind_speed:.1f} м/с",  f"{wind_direction_text(wind_dir)} ({wind_dir:.0f}°)"),
        (m6, "🌧 Вер. осадков",  f"{precip_prob:.0f}%",    ""),
        (m7, "🌅 Восход",        sunrise_dt.strftime('%H:%M') if sunrise_dt else "—", ""),
        (m8, "🌇 Закат",         f"{sunset_dt.strftime('%H:%M') if sunset_dt else '—'}", f"Через {time_to_sunset}" if time_to_sunset else ""),
    ]
    for col, label, val, sub in metrics2:
        with col:
            st.markdown(f"""
<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{val}</div>
  <div class="metric-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

    # ── Грозовой индекс ───────────────────────
    st.markdown("<div class='section-title'>⚡ Грозовой индекс</div>", unsafe_allow_html=True)
    gi1, gi2 = st.columns([2, 1])
    with gi1:
        st.markdown(f"""
<div class="metric-card">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
    <span style="font-size:2rem">{storm['emoji']}</span>
    <div>
      <div style="font-size:1.3rem;font-weight:700;color:{storm['color']}">{storm['level']}</div>
      <div style="color:{t['text2']};font-size:0.83rem">Шанс грозы: {storm['pct']}%</div>
    </div>
  </div>
  <div class="storm-bar-outer">
    <div style="height:10px;border-radius:8px;background:{storm['color']};width:{storm['pct']}%;transition:width 1s ease"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:0.77rem;color:{t['text2']}">
    <span>CAPE: {cape:.0f} Дж/кг</span>
    <span>Молнии: {lightning:.0f}%</span>
    <span>Влажность: {humidity:.0f}%</span>
  </div>
</div>""", unsafe_allow_html=True)
    with gi2:
        st.markdown(f"""
<div class="metric-card">
  <div class="metric-label">☁️ Облачность</div>
  <div class="metric-value">{cloudcover:.0f}%</div>
  <div class="metric-sub">{wmo_description(wmo_code)}</div>
</div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    # ГРАФИКИ ПРОГНОЗА
    # ══════════════════════════════════════════
    st.markdown("<div class='section-title'>📈 Прогноз на 5 дней</div>", unsafe_allow_html=True)
    charts = make_forecast_charts(hourly, t)
    ch_col1, ch_col2 = st.columns(2)
    with ch_col1:
        st.plotly_chart(charts[0], use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(charts[2], use_container_width=True, config={"displayModeBar": False})
    with ch_col2:
        st.plotly_chart(charts[1], use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(charts[3], use_container_width=True, config={"displayModeBar": False})

    # ── Суточный прогноз ──────────────────────
    st.markdown("<div class='section-title'>📅 Прогноз по дням</div>", unsafe_allow_html=True)
    day_cols = st.columns(7)
    for i in range(min(7, len(daily.get("time", [])))):
        with day_cols[i]:
            d_date  = daily["time"][i]
            d_wmo   = daily["weathercode"][i]
            d_max   = daily["temperature_2m_max"][i]
            d_min   = daily["temperature_2m_min"][i]
            d_rain  = daily["precipitation_probability_max"][i]
            day_label = "Сег." if i == 0 else ("Завт." if i == 1 else datetime.fromisoformat(d_date).strftime("%d.%m"))
            st.markdown(f"""
<div class="metric-card" style="text-align:center;padding:10px 6px">
  <div style="font-size:0.75rem;color:{t['text2']};font-weight:600">{day_label}</div>
  <div style="font-size:1.3rem;margin:4px 0">{'☀️' if d_wmo<=1 else ('⛅' if d_wmo<=3 else ('🌧' if 50<=d_wmo<=82 else ('⛈' if d_wmo>=95 else '🌥')))}</div>
  <div style="font-size:0.9rem;font-weight:700;color:{t['text']}">{d_max:.0f}°</div>
  <div style="font-size:0.8rem;color:{t['text2']}">{d_min:.0f}°</div>
  <div style="font-size:0.72rem;color:{t['accent']}">💧{d_rain:.0f}%</div>
</div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    # МОЛНИЕДЕТЕКТОР / РАДАР
    # ══════════════════════════════════════════
    st.markdown("<div class='section-title'>🗺 Радар и грозопеленгация</div>", unsafe_allow_html=True)

    # Кнопка обновления сохраняет ключ в session_state
    if "radar_key" not in st.session_state:
        st.session_state.radar_key = 0

    if st.button("🔄 Обновить радар"):
        st.session_state.radar_key += 1

    lat_r = city["lat"]
    lon_r = city["lon"]
    # Blitzortung iframe (молниедетектор)
    blitz_url = (
        f"https://www.blitzortung.org/en/live_lightning_maps.php"
        f"?map=11&lat={lat_r}&lon={lon_r}"
    )
    st.markdown(f"""
<iframe
  key="{st.session_state.radar_key}"
  src="{blitz_url}"
  width="100%" height="500"
  style="border:none;border-radius:12px;overflow:hidden"
  loading="lazy"
  title="Blitzortung Lightning Radar"
></iframe>
<p style="color:{t['text2']};font-size:0.75rem;margin-top:6px">
  🔴 Данные: blitzortung.org · Центр карты: {lat_r:.2f}°N, {lon_r:.2f}°E
</p>
""", unsafe_allow_html=True)

    # ── Футер ─────────────────────────────────
    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center;color:{t['text2']};font-size:0.75rem'>"
        f"Данные: <a href='https://open-meteo.com' style='color:{t['accent']}'>Open-Meteo</a> · "
        f"Молнии: <a href='https://blitzortung.org' style='color:{t['accent']}'>Blitzortung.org</a>"
        f"</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
