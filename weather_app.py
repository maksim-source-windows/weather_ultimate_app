"""
🌦️ Weather App v2 — Streamlit
Запуск: streamlit run weather_app.py
Зависимости: streamlit, pandas, plotly, requests, numpy, ephem
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math

try:
    import ephem
    EPHEM_OK = True
except ImportError:
    EPHEM_OK = False

# ─────────────────────────────────────────────
# КОНФИГУРАЦИЯ ГОРОДОВ
# ─────────────────────────────────────────────
CITIES = {
    "Минск":      {"lat": 53.9045, "lon": 27.5615},
    "Харьков":    {"lat": 49.9935, "lon": 36.2304},
    "Ужгород":    {"lat": 48.6208, "lon": 22.2879},
    "Москва":     {"lat": 55.7558, "lon": 37.6173},
    "Люберцы":    {"lat": 55.6778, "lon": 37.8927},
    "Серпухов":   {"lat": 54.9167, "lon": 37.4167},
    "Владимир":   {"lat": 56.1366, "lon": 40.3966},
    "Гороховец":  {"lat": 56.2003, "lon": 42.6867},
    "Пенза":      {"lat": 53.1959, "lon": 45.0183},
    "Тамбов":     {"lat": 52.7212, "lon": 41.4522},
    "Киев":       {"lat": 50.4501, "lon": 30.5234},
    "Алма-Ата":   {"lat": 43.2220, "lon": 76.8512},
    "Ташкент":    {"lat": 41.2995, "lon": 69.2401},
    "Баку":       {"lat": 40.4093, "lon": 49.8671},
    "Ереван":     {"lat": 40.1792, "lon": 44.4991},
    "Тбилиси":    {"lat": 41.6938, "lon": 44.8015},
    "Кишинёв":    {"lat": 47.0105, "lon": 28.8638},
    "Рига":       {"lat": 56.9460, "lon": 24.1059},
    "Вильнюс":    {"lat": 54.6872, "lon": 25.2797},
    "Таллин":     {"lat": 59.4370, "lon": 24.7536},
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
# НОВОСТНЫЕ ССЫЛКИ
# ─────────────────────────────────────────────
METEO_NEWS = [
    {"title": "Gismeteo — новости погоды",  "url": "https://www.gismeteo.ru/news/",        "icon": "🌦"},
    {"title": "Meteoinfo.ru — прогнозы",    "url": "http://www.meteoinfo.ru/news",          "icon": "📡"},
    {"title": "Severe Weather EU",          "url": "https://www.severe-weather.eu/",        "icon": "⛈"},
    {"title": "Weather.com News",           "url": "https://weather.com/news/weather",      "icon": "🌍"},
    {"title": "WMO — World Met. Org.",      "url": "https://public.wmo.int/en/media/news",  "icon": "🏛"},
    {"title": "Погода Mail.ru новости",     "url": "https://pogoda.mail.ru/news/",          "icon": "☁️"},
]

ASTRO_NEWS = [
    {"title": "Астронет — новости",         "url": "http://www.astronet.ru/db/msg/",            "icon": "🔭"},
    {"title": "SpaceWeather.com",           "url": "https://spaceweather.com/",                 "icon": "☀️"},
    {"title": "Sky & Telescope",            "url": "https://skyandtelescope.org/astronomy-news/","icon": "🌠"},
    {"title": "Space.com — Astronomy",      "url": "https://www.space.com/astronomy",            "icon": "🚀"},
    {"title": "EarthSky",                   "url": "https://earthsky.org/",                     "icon": "🌌"},
    {"title": "NASA News",                  "url": "https://www.nasa.gov/news/",                "icon": "🛸"},
]

# ═══════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════

@st.cache_data(ttl=600)
def fetch_openmeteo(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
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
        "wind_speed_unit": "ms", "timezone": "auto", "forecast_days": 7,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Open-Meteo: {e}")
        return None


@st.cache_data(ttl=600)
def fetch_marine(lat: float, lon: float):
    url = "https://marine-api.open-meteo.com/v1/marine"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "wave_height,wave_direction,wave_period,sea_surface_temperature",
        "timezone": "auto", "forecast_days": 5,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=600)
def fetch_yr(lat: float, lon: float):
    url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    headers = {"User-Agent": "WeatherStreamlitApp/2.0 contact@demo.com"}
    try:
        r = requests.get(url, params={"lat": round(lat, 4), "lon": round(lon, 4)},
                         headers=headers, timeout=10)
        r.raise_for_status()
        ts = r.json().get("properties", {}).get("timeseries", [])
        result = {"times": [], "temp": [], "humidity": [], "pressure": [], "wind_speed": [], "wind_dir": []}
        for entry in ts[:120]:
            inst = entry.get("data", {}).get("instant", {}).get("details", {})
            result["times"].append(entry["time"])
            result["temp"].append(inst.get("air_temperature"))
            result["humidity"].append(inst.get("relative_humidity"))
            result["pressure"].append(inst.get("air_pressure_at_sea_level"))
            result["wind_speed"].append(inst.get("wind_speed"))
            result["wind_dir"].append(inst.get("wind_from_direction"))
        return result
    except Exception:
        return None


# ═══════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════

def hex_to_rgba(hex_color: str, alpha: float = 0.2) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def wind_direction_text(deg: float) -> str:
    dirs = ["С","СВ","В","ЮВ","Ю","ЮЗ","З","СЗ"]
    return dirs[round(float(deg) / 45) % 8]

def wmo_description(code: int) -> str:
    wmo = {
        0:"Ясно", 1:"Преимущественно ясно", 2:"Переменная облачность", 3:"Облачно",
        45:"Туман", 48:"Изморозь", 51:"Лёгкая морось", 53:"Умеренная морось",
        55:"Сильная морось", 61:"Лёгкий дождь", 63:"Умеренный дождь", 65:"Сильный дождь",
        71:"Лёгкий снег", 73:"Умеренный снег", 75:"Сильный снег", 77:"Снежная крупа",
        80:"Ливень (слабый)", 81:"Ливень (умеренный)", 82:"Ливень (сильный)",
        85:"Снегопад (слабый)", 86:"Снегопад (сильный)",
        95:"Гроза", 96:"Гроза с градом", 99:"Гроза с сильным градом",
    }
    return wmo.get(int(code), f"Код {code}")

def storm_index(cape: float, lightning: float, humidity: float) -> dict:
    score = min(cape/3000,1)*0.5 + min(lightning/100,1)*0.35 + max(0,(humidity-50)/50)*0.15
    pct = round(score * 100)
    if score < 0.2:   level, color, emoji = "Низкая",        "#43a047", "🟢"
    elif score < 0.45: level, color, emoji = "Средняя",       "#fb8c00", "🟡"
    elif score < 0.7:  level, color, emoji = "Высокая",       "#e53935", "🔴"
    else:              level, color, emoji = "Экстремальная", "#7b1fa2", "🟣"
    return {"level": level, "color": color, "emoji": emoji, "pct": pct}

def sky_clarity(cloudcover: float, humidity: float) -> float:
    return round(((100-cloudcover)/100*0.7 + max(0,(100-humidity)/100)*0.3)*100)

def moon_phase_text(doy: int):
    frac = (doy % 29.5) / 29.5
    if frac < 0.03 or frac > 0.97: return "🌑 Новолуние", frac
    elif frac < 0.22: return "🌒 Растущий серп", frac
    elif frac < 0.28: return "🌓 Первая четверть", frac
    elif frac < 0.47: return "🌔 Растущая луна", frac
    elif frac < 0.53: return "🌕 Полнолуние", frac
    elif frac < 0.72: return "🌖 Убывающая луна", frac
    elif frac < 0.78: return "🌗 Последняя четверть", frac
    else: return "🌘 Убывающий серп", frac

def visible_constellations(lat: float, month: int) -> list:
    seasonal = {
        (12,1,2): ["Орион 🌟","Телец 🐂","Близнецы ♊","Возничий 🐐","Эридан 🌊","Персей ⚔️"],
        (3,4,5):  ["Лев 🦁","Дева ♍","Рак 🦀","Гидра 🐉","Ворон 🐦","Чаша 🏆"],
        (6,7,8):  ["Скорпион 🦂","Стрелец 🏹","Орёл 🦅","Лебедь 🦢","Лира 🎵","Геркулес 💪"],
        (9,10,11):["Пегас 🐴","Андромеда ✨","Рыбы 🐠","Водолей 💧","Козерог 🐐","Кит 🐋"],
    }
    result = ["Большая Медведица 🐻","Малая Медведица ⭐","Кассиопея 👑"]
    for months_t, consts in seasonal.items():
        if month in months_t:
            result.extend(consts[:4]); break
    return result

def astro_conditions(clarity: float, moon_frac: float, visibility_km: float) -> dict:
    score = clarity*0.5 + min(visibility_km/30,1)*30 - (1-abs(moon_frac-0.5)*2)*30
    score = max(0, min(100, score))
    if score >= 65:   verdict, color = "Отлично ✨", "#43a047"
    elif score >= 35: verdict, color = "Средне 🌤",  "#fb8c00"
    else:             verdict, color = "Плохо 🌧",   "#e53935"
    return {"verdict": verdict, "color": color, "score": round(score)}


# ─────────────────────────────────────────────
# АСТРОНОМИЧЕСКИЕ СУМЕРКИ
# ─────────────────────────────────────────────
def calc_twilights(lat: float, lon: float, date: datetime) -> dict:
    if EPHEM_OK:
        obs = ephem.Observer()
        obs.lat = str(lat); obs.lon = str(lon)
        obs.date = date.strftime("%Y/%m/%d 12:00:00")
        obs.pressure = 0
        results = {}
        for name, horizon in [("civil","-6"),("nautical","-12"),("astronomical","-18")]:
            obs.horizon = horizon
            try:
                ev = ephem.localtime(obs.next_setting(ephem.Sun(), use_center=True)).strftime("%H:%M")
                mo = ephem.localtime(obs.next_rising(ephem.Sun(),  use_center=True)).strftime("%H:%M")
                results[name] = {"evening": ev, "morning": mo}
            except Exception:
                results[name] = {"evening": "—", "morning": "—"}
        return results
    else:
        doy   = date.timetuple().tm_yday
        decl  = 23.45 * math.sin(math.radians(360/365*(doy-81)))
        lat_r = math.radians(lat)
        decl_r= math.radians(decl)
        noon  = 12 - lon/15
        results = {}
        for name, dep in [("civil",6),("nautical",12),("astronomical",18)]:
            try:
                cos_h = (math.sin(math.radians(-dep)) - math.sin(lat_r)*math.sin(decl_r)) / \
                        (math.cos(lat_r)*math.cos(decl_r))
                if abs(cos_h) > 1:
                    results[name] = {"evening":"—","morning":"—"}; continue
                ha = math.degrees(math.acos(cos_h))
                ev = noon + ha/15; mo = noon - ha/15
                def fmt(x): h=int(x)%24; m=int((x%1)*60); return f"{h:02d}:{m:02d}"
                results[name] = {"evening": fmt(ev), "morning": fmt(mo)}
            except Exception:
                results[name] = {"evening":"—","morning":"—"}
        return results


# ─────────────────────────────────────────────
# ПЛАНЕТЫ (ephem)
# ─────────────────────────────────────────────
def get_planets(lat: float, lon: float) -> list:
    if not EPHEM_OK:
        return []
    obs = ephem.Observer()
    obs.lat = str(lat); obs.lon = str(lon)
    obs.date = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
    planets_def = [
        ("Меркурий ☿", ephem.Mercury()), ("Венера ♀",  ephem.Venus()),
        ("Марс ♂",     ephem.Mars()),    ("Юпитер ♃",  ephem.Jupiter()),
        ("Сатурн ♄",   ephem.Saturn()),  ("Уран ⛢",    ephem.Uranus()),
        ("Нептун ♆",   ephem.Neptune()),
    ]
    result = []
    for name, body in planets_def:
        body.compute(obs)
        alt = math.degrees(body.alt)
        result.append({
            "name": name, "alt": round(alt,1),
            "az": round(math.degrees(body.az),1),
            "ra": str(body.ra), "dec": str(body.dec),
            "mag": round(body.mag,1), "visible": alt > 0,
        })
    return result


# ─────────────────────────────────────────────
# ПОВСЕДНЕВНЫЕ СОВЕТЫ
# ─────────────────────────────────────────────
def daily_advice(temp, feelslike, wind_speed, humidity,
                 pressure, visibility, precip_prob, wmo_code, uv_index, cape) -> list:
    advice = []
    rain = precip_prob > 40 or wmo_code in range(51, 100)

    # Одежда
    if feelslike < -15:   c, cc = "🧥 Зимняя куртка, термобельё, шапка, варежки, тёплые сапоги", "#1565c0"
    elif feelslike < -5:  c, cc = "🧥 Тёплая куртка, свитер, шапка, перчатки", "#1976d2"
    elif feelslike < 5:   c, cc = "🧥 Куртка, кофта, шарф", "#0288d1"
    elif feelslike < 12:  c, cc = "🧦 Лёгкая куртка или плотная толстовка", "#0097a7"
    elif feelslike < 18:  c, cc = "👕 Толстовка или джемпер", "#00897b"
    elif feelslike < 24:  c, cc = "👕 Футболка, лёгкие брюки", "#43a047"
    else:                 c, cc = "🩳 Лёгкая одежда, шорты, сандали", "#f57f17"
    if rain: c += " + ☂️ зонт"
    if wind_speed > 10: c += " + ветровка"
    advice.append({"title": "👗 Одежда сегодня", "text": c, "color": cc})

    # Рыбалка
    fs = 0; fn = []
    if 990 < pressure < 1020: fs+=3; fn.append("давление стабильное ✅")
    elif pressure < 990:      fs+=1; fn.append("давление низкое ⚠️")
    else:                     fs+=2; fn.append("давление высокое")
    if wind_speed < 5:  fs+=2; fn.append("штиль ✅")
    elif wind_speed < 10: fs+=1; fn.append("слабый ветер")
    else: fn.append("сильный ветер ❌")
    if precip_prob < 20 and wmo_code < 51: fs+=2; fn.append("нет осадков ✅")
    else: fn.append("возможны осадки")
    if 8 <= temp <= 22: fs+=2; fn.append("хорошая температура ✅")
    if fs >= 7:   fv, fc = "Отличная рыбалка 🐟", "#43a047"
    elif fs >= 4: fv, fc = "Неплохо 🎣", "#fb8c00"
    else:         fv, fc = "Лучше остаться дома", "#e53935"
    advice.append({"title": "🎣 Рыбалка", "text": f"{fv} — {', '.join(fn[:3])}", "color": fc})

    # Походы
    if wmo_code >= 95: ht, hc = "Не рекомендуется — гроза ⛈", "#e53935"
    elif visibility < 1: ht, hc = "Опасно — туман, видимость < 1 км 🌫", "#e53935"
    elif visibility > 5 and wind_speed < 15 and precip_prob < 30 and cape < 500:
        if uv_index > 7: ht, hc = "Хорошо ⚠️ высокий УФ, берите SPF50+", "#fb8c00"
        else:            ht, hc = "Отличные условия для похода 🥾", "#43a047"
    else: ht, hc = "Условия неидеальны, будьте осторожны 🌦", "#fb8c00"
    advice.append({"title": "🥾 Походы", "text": ht, "color": hc})

    # Болезнь
    ss = (2 if humidity > 80 else 0) + (1 if wind_speed > 8 else 0) + \
         (2 if temp < 5 else 0) + (1 if temp > 28 else 0) + (1 if precip_prob > 50 else 0)
    if ss <= 1:   st2, sc = "Низкий риск 💪", "#43a047"
    elif ss <= 3: st2, sc = "Умеренный — одевайтесь теплее 🧣", "#fb8c00"
    else:         st2, sc = "Высокий риск — берегитесь простуды 🤧", "#e53935"
    advice.append({"title": "🤒 Риск заболеть", "text": st2, "color": sc})

    # Рейс
    df = []; ds = 0
    if visibility < 1:   ds+=4; df.append("туман (<1 км)")
    elif visibility < 3: ds+=2; df.append("плохая видимость")
    if wmo_code >= 95:         ds+=4; df.append("гроза")
    if wind_speed > 15:        ds+=3; df.append(f"сильный ветер {wind_speed:.0f}м/с")
    if wmo_code in range(71,78): ds+=2; df.append("снегопад")
    if ds == 0:   dv, dc = "Минимальный риск ✈️ полёты штатно", "#43a047"
    elif ds <= 2: dv, dc = f"Небольшой риск — {', '.join(df)}", "#fb8c00"
    elif ds <= 4: dv, dc = f"Возможны задержки: {', '.join(df)} 🕐", "#ff7043"
    else:         dv, dc = f"Высокий риск задержки/отмены: {', '.join(df)} ❌", "#e53935"
    advice.append({"title": "✈️ Риск задержки рейса", "text": dv, "color": dc})

    return advice


# ─────────────────────────────────────────────
# CSS АНИМАЦИИ ПОГОДЫ
# ─────────────────────────────────────────────
def get_weather_animation(wmo_code: int, t: dict) -> str:
    if wmo_code <= 1:   wt = "sunny"
    elif wmo_code <= 3: wt = "cloudy"
    elif wmo_code in range(95,100): wt = "storm"
    elif wmo_code in range(51,82):  wt = "rain"
    else: wt = "cloudy"
    bg = t["card"]

    if wt == "sunny":
        return f"""
<div class="weather-anim-box" style="background:linear-gradient(180deg,#1a3a5c 0%,#ff7043 40%,#ffb300 70%,{bg} 100%);">
  <style>
    @keyframes sunrise{{0%{{transform:translateY(60px) scale(0.7);opacity:.3}}100%{{transform:translateY(0) scale(1);opacity:1}}}}
    @keyframes ray-spin{{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}}
    @keyframes shimmer{{0%,100%{{opacity:.7}}50%{{opacity:1}}}}
    .sun-wrap{{position:absolute;bottom:30px;left:50%;transform:translateX(-50%);animation:sunrise 2s ease-out forwards}}
    .sun-core{{width:70px;height:70px;background:radial-gradient(circle,#fff700,#ffb300);border-radius:50%;box-shadow:0 0 40px #ffb300,0 0 80px #ff8c00}}
    .sun-rays{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);animation:ray-spin 8s linear infinite}}
    .ray{{position:absolute;width:4px;height:90px;background:linear-gradient(transparent,rgba(255,179,0,.5),transparent);border-radius:2px;top:-45px;left:-2px}}
    .shimmer-ov{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 100%,rgba(255,179,0,.2),transparent 70%);animation:shimmer 3s ease-in-out infinite}}
  </style>
  <div class="shimmer-ov"></div>
  <div class="sun-wrap"><div class="sun-rays">{''.join(f'<div class="ray" style="transform:rotate({i*30}deg)"></div>' for i in range(12))}</div><div class="sun-core"></div></div>
</div>"""

    elif wt == "cloudy":
        return f"""
<div class="weather-anim-box" style="background:linear-gradient(180deg,#2c3e50 0%,#4a5568 50%,{bg} 100%);">
  <style>
    @keyframes cdrift{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(18px)}}}}
    @keyframes speek{{0%,100%{{opacity:.3;transform:translateX(-50%) translateY(10px)}}50%{{opacity:.85;transform:translateX(-50%) translateY(0)}}}}
    .csun{{position:absolute;bottom:25px;left:50%;transform:translateX(-50%);width:55px;height:55px;background:radial-gradient(#fff176,#fdd835);border-radius:50%;box-shadow:0 0 30px #fdd835;animation:speek 5s ease-in-out infinite}}
    .cld{{position:absolute;background:#b0bec5;border-radius:50px;opacity:.9}}
    .cl1{{width:110px;height:45px;bottom:40px;left:20%;animation:cdrift 6s ease-in-out infinite}}
    .cl2{{width:140px;height:55px;bottom:55px;left:40%;animation:cdrift 8s ease-in-out infinite reverse}}
    .cl3{{width:90px;height:38px;bottom:35px;right:15%;animation:cdrift 7s ease-in-out infinite}}
    .cl1::before{{content:'';position:absolute;width:60px;height:60px;background:#b0bec5;border-radius:50%;top:-25px;left:15px}}
    .cl2::before{{content:'';position:absolute;width:75px;height:70px;background:#b0bec5;border-radius:50%;top:-35px;left:25px}}
    .cl3::before{{content:'';position:absolute;width:50px;height:50px;background:#b0bec5;border-radius:50%;top:-22px;left:12px}}
  </style>
  <div class="csun"></div><div class="cld cl1"></div><div class="cld cl2"></div><div class="cld cl3"></div>
</div>"""

    elif wt == "rain":
        rng = np.random.default_rng(42)
        drops = ''.join(
            f'<div style="position:absolute;width:2px;background:linear-gradient(to bottom,transparent,#90caf9);'
            f'border-radius:2px;top:0;left:{rng.integers(5,95)}%;height:{rng.integers(15,30)}px;'
            f'opacity:{0.4+rng.random()*0.5:.2f};animation:fall {0.5+rng.random()*0.5:.2f}s {rng.random()*2:.2f}s linear infinite"></div>'
            for _ in range(35))
        return f"""
<div class="weather-anim-box" style="background:linear-gradient(180deg,#1a1a2e,#2d3748 60%,{bg});overflow:hidden">
  <style>
    @keyframes fall{{0%{{transform:translateY(-20px);opacity:0}}80%{{opacity:1}}100%{{transform:translateY(130px);opacity:0}}}}
    @keyframes csway{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(10px)}}}}
    @keyframes puddle{{0%,100%{{transform:scale(1);opacity:.5}}50%{{transform:scale(1.1);opacity:.8}}}}
    .rcl{{position:absolute;background:#455a64;border-radius:50px}}
    .rrc1{{width:120px;height:50px;top:5px;left:15%;animation:csway 7s ease-in-out infinite}}
    .rrc2{{width:150px;height:60px;top:15px;left:40%;animation:csway 9s ease-in-out infinite reverse}}
    .rrc3{{width:100px;height:45px;top:8px;right:12%;animation:csway 6s ease-in-out infinite}}
    .rrc1::before{{content:'';position:absolute;width:65px;height:65px;background:#455a64;border-radius:50%;top:-30px;left:20px}}
    .rrc2::before{{content:'';position:absolute;width:80px;height:75px;background:#455a64;border-radius:50%;top:-38px;left:30px}}
    .rrc3::before{{content:'';position:absolute;width:55px;height:55px;background:#455a64;border-radius:50%;top:-25px;left:18px}}
    .pdl{{position:absolute;bottom:6px;border-radius:50%;background:rgba(79,195,247,.2);animation:puddle 2s ease-in-out infinite}}
  </style>
  <div class="rcl rrc1"></div><div class="rcl rrc2"></div><div class="rcl rrc3"></div>
  {drops}
  <div class="pdl" style="width:60px;height:12px;left:20%;animation-delay:.3s"></div>
  <div class="pdl" style="width:90px;height:16px;left:50%;animation-delay:.8s"></div>
  <div class="pdl" style="width:50px;height:10px;right:20%;animation-delay:1.2s"></div>
</div>"""

    else:  # storm
        rng = np.random.default_rng(7)
        drops = ''.join(
            f'<div style="position:absolute;width:2px;background:linear-gradient(to bottom,transparent,#64b5f6);'
            f'border-radius:2px;top:0;left:{rng.integers(5,95)}%;height:{rng.integers(20,40)}px;'
            f'animation:sfall {0.3+rng.random()*0.4:.2f}s {rng.random()*1.5:.2f}s linear infinite"></div>'
            for _ in range(40))
        return f"""
<div class="weather-anim-box" style="background:linear-gradient(180deg,#0d0d1a,#1a1a2e 60%,{bg});overflow:hidden">
  <style>
    @keyframes sfall{{0%{{transform:translateY(-20px) translateX(0);opacity:0}}100%{{transform:translateY(140px) translateX(-10px);opacity:.9}}}}
    @keyframes flash{{0%,90%,100%{{opacity:0}}92%,96%{{opacity:1}}}}
    @keyframes bolt-a{{0%,85%,100%{{opacity:0;transform:scaleY(0)}}87%,93%{{opacity:1;transform:scaleY(1)}}}}
    @keyframes tglow{{0%,89%,100%{{background:#0d0d1a}}90%,95%{{background:#1a2a4a}}}}
    .sbg{{position:absolute;inset:0;animation:tglow 4s linear infinite;z-index:0}}
    .scld{{position:absolute;background:#263238;border-radius:50px;z-index:1}}
    .sc1{{width:130px;height:55px;top:3px;left:10%}}.sc2{{width:160px;height:65px;top:10px;left:38%}}.sc3{{width:110px;height:48px;top:5px;right:10%}}
    .sc1::before{{content:'';position:absolute;width:70px;height:70px;background:#263238;border-radius:50%;top:-32px;left:22px}}
    .sc2::before{{content:'';position:absolute;width:88px;height:82px;background:#263238;border-radius:50%;top:-42px;left:32px}}
    .sc3::before{{content:'';position:absolute;width:62px;height:60px;background:#263238;border-radius:50%;top:-28px;left:20px}}
    .lflash{{position:absolute;inset:0;background:rgba(200,220,255,.12);animation:flash 4s linear infinite;z-index:2;pointer-events:none}}
    .bolt{{position:absolute;z-index:3;font-size:40px;color:#fff176;text-shadow:0 0 20px #ffeb3b,0 0 40px #ff8f00;transform-origin:top center}}
    .b1{{top:50px;left:35%;animation:bolt-a 4s linear infinite}}.b2{{top:45px;left:62%;animation:bolt-a 4s linear infinite 2s}}
  </style>
  <div class="sbg"></div><div class="scld sc1"></div><div class="scld sc2"></div><div class="scld sc3"></div>
  {drops}<div class="lflash"></div><div class="bolt b1">⚡</div><div class="bolt b2">⚡</div>
</div>"""


# ─────────────────────────────────────────────
# АНИМАЦИЯ ПЕРЕХОДА В АСТРОНОМИЮ
# ─────────────────────────────────────────────
def astro_banner() -> str:
    stars = ''.join(
        f'<div style="position:absolute;border-radius:50%;background:#fff;'
        f'width:{2+i%3}px;height:{2+i%3}px;top:{(i*37+11)%90}%;left:{(i*53+7)%95}%;'
        f'animation:twinkle {1.5+i%4*0.5:.1f}s {i%5*0.3:.1f}s ease-in-out infinite"></div>'
        for i in range(60))
    return f"""
<div style="position:relative;width:100%;height:160px;
  background:linear-gradient(180deg,#000005 0%,#0a0a2e 40%,#0d1b4a 100%);
  border-radius:16px;overflow:hidden;margin-bottom:20px">
  <style>
    @keyframes twinkle{{0%,100%{{opacity:.2;transform:scale(.8)}}50%{{opacity:1;transform:scale(1.2)}}}}
    @keyframes mway{{0%{{opacity:0;transform:translateX(-30px)}}100%{{opacity:.25;transform:translateX(0)}}}}
    @keyframes afade{{0%{{opacity:0;transform:translateY(20px)}}100%{{opacity:1;transform:translateY(0)}}}}
    @keyframes shoot{{0%{{transform:translateX(0) translateY(0);opacity:1}}100%{{transform:translateX(120px) translateY(60px);opacity:0}}}}
    .mw{{position:absolute;inset:0;background:linear-gradient(135deg,transparent 20%,rgba(180,160,255,.15) 50%,transparent 80%);animation:mway 2s ease-out forwards}}
    .atitle{{position:absolute;bottom:18px;left:50%;transform:translateX(-50%);color:#c8d8ff;font-size:1.4rem;font-weight:800;letter-spacing:.15em;text-shadow:0 0 20px #6699ff,0 0 40px #3366ff;animation:afade 1.5s ease-out forwards;white-space:nowrap}}
    .ss{{position:absolute;width:2px;height:2px;background:white;border-radius:50%;box-shadow:0 0 4px 1px white}}
    .ss1{{top:20%;left:10%;animation:shoot 2s ease-out infinite .5s}}.ss2{{top:35%;left:30%;animation:shoot 2.5s ease-out infinite 1.8s}}.ss3{{top:15%;left:60%;animation:shoot 1.8s ease-out infinite 3s}}
  </style>
  <div class="mw"></div>
  {stars}
  <div class="ss ss1"></div><div class="ss ss2"></div><div class="ss ss3"></div>
  <div class="atitle">🔭 РЕЖИМ АСТРОНОМИИ</div>
</div>"""


# ─────────────────────────────────────────────
# ГРАФИКИ PLOTLY
# ─────────────────────────────────────────────
def make_forecast_charts(hourly: dict, t: dict, yr_data=None) -> list:
    times = pd.to_datetime(hourly["time"])
    mask  = times <= times[0] + pd.Timedelta(days=5)

    def layout(title):
        return dict(
            title=dict(text=title, font=dict(color=t["text"], size=14)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=t["text2"]),
            xaxis=dict(gridcolor=t["border"], showgrid=True),
            yaxis=dict(gridcolor=t["border"], showgrid=True),
            margin=dict(l=40,r=20,t=40,b=40), height=240,
            legend=dict(font=dict(color=t["text2"]), bgcolor="rgba(0,0,0,0)"),
        )

    def yr_series(key):
        if not yr_data: return None, None
        yt = pd.to_datetime(yr_data["times"])
        ym = yt <= yt[0] + pd.Timedelta(days=5)
        ya = np.array([v if v is not None else np.nan for v in yr_data[key]])
        return yt[ym], ya[ym]

    charts = []

    # Температура
    f1 = go.Figure()
    f1.add_trace(go.Scatter(x=times[mask], y=np.array(hourly["temperature_2m"])[mask],
        fill="tozeroy", line=dict(color=t["accent"],width=2),
        fillcolor=hex_to_rgba(t["accent"],.15), name="Open-Meteo °C"))
    f1.add_trace(go.Scatter(x=times[mask], y=np.array(hourly["apparent_temperature"])[mask],
        line=dict(color=t["accent2"],width=1.5,dash="dot"), name="Ощущается"))
    yt, ya = yr_series("temp")
    if yt is not None:
        f1.add_trace(go.Scatter(x=yt, y=ya, line=dict(color="#ff7043",width=1.5,dash="dash"), name="Yr.no °C"))
    f1.update_layout(**layout("🌡 Температура (°C)"))
    charts.append(f1)

    # Влажность
    f2 = go.Figure(go.Bar(x=times[mask], y=np.array(hourly["relativehumidity_2m"])[mask],
        marker_color=hex_to_rgba(t["accent2"],.75), name="Open-Meteo %"))
    yt, ya = yr_series("humidity")
    if yt is not None:
        f2.add_trace(go.Scatter(x=yt, y=ya, line=dict(color="#ff7043",width=1.5,dash="dash"), name="Yr.no %"))
    f2.update_layout(**layout("💧 Влажность (%)"))
    charts.append(f2)

    # Давление
    f3 = go.Figure(go.Scatter(x=times[mask], y=np.array(hourly["surface_pressure"])[mask],
        line=dict(color="#ff7043",width=2), fill="tozeroy",
        fillcolor="rgba(255,112,67,.15)", name="Open-Meteo гПа"))
    yt, ya = yr_series("pressure")
    if yt is not None:
        f3.add_trace(go.Scatter(x=yt, y=ya, line=dict(color="#ab47bc",width=1.5,dash="dash"), name="Yr.no гПа"))
    f3.update_layout(**layout("🌀 Давление (гПа)"))
    charts.append(f3)

    # Ветер
    f4 = go.Figure(go.Scatter(x=times[mask], y=np.array(hourly["windspeed_10m"])[mask],
        line=dict(color="#ab47bc",width=2), fill="tozeroy",
        fillcolor="rgba(171,71,188,.15)", name="Open-Meteo м/с"))
    yt, ya = yr_series("wind_speed")
    if yt is not None:
        f4.add_trace(go.Scatter(x=yt, y=ya, line=dict(color="#ff7043",width=1.5,dash="dash"), name="Yr.no м/с"))
    f4.update_layout(**layout("💨 Скорость ветра (м/с)"))
    charts.append(f4)

    return charts


# ─────────────────────────────────────────────
# ТЕМА CSS
# ─────────────────────────────────────────────
def apply_theme(t: dict):
    st.markdown(f"""<style>
  .stApp,[data-testid="stAppViewContainer"]{{background-color:{t['bg']} !important;color:{t['text']} !important}}
  [data-testid="stSidebar"]{{background-color:{t['bg2']} !important;border-right:1px solid {t['border']}}}
  .metric-card{{background:{t['card']};border:1px solid {t['border']};border-radius:12px;padding:16px 18px;
    box-shadow:0 2px 12px {t['shadow']};margin-bottom:12px;transition:transform .2s}}
  .metric-card:hover{{transform:translateY(-2px);box-shadow:0 6px 20px {t['shadow']}}}
  .metric-label{{font-size:.72rem;color:{t['text2']};text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px}}
  .metric-value{{font-size:1.6rem;font-weight:700;color:{t['text']};line-height:1.1}}
  .metric-sub{{font-size:.82rem;color:{t['text2']};margin-top:2px}}
  .weather-anim-box{{position:relative;width:100%;height:140px;border-radius:16px;overflow:hidden;margin-bottom:24px}}
  .city-header{{font-size:2rem;font-weight:800;color:{t['text']};margin:0;line-height:1.1}}
  .city-sub{{font-size:.9rem;color:{t['text2']};margin-top:4px}}
  .section-title{{font-size:1rem;font-weight:700;color:{t['accent']};text-transform:uppercase;
    letter-spacing:.1em;margin:22px 0 12px;border-left:3px solid {t['accent']};padding-left:10px}}
  .storm-bar-outer{{background:{t['border']};border-radius:8px;height:10px;width:100%;margin-top:8px}}
  .news-card{{display:block;background:{t['card']};border:1px solid {t['border']};border-radius:10px;
    padding:12px 14px;margin-bottom:8px;text-decoration:none;color:{t['text']};transition:all .2s;
    box-shadow:0 1px 6px {t['shadow']}}}
  .news-card:hover{{transform:translateY(-2px);border-color:{t['accent']};box-shadow:0 4px 16px {t['shadow']}}}
  .news-card-title{{font-size:.9rem;font-weight:600;color:{t['text']}}}
  .news-card-sub{{font-size:.75rem;color:{t['text2']};margin-top:2px}}
  .advice-card{{background:{t['card']};border-radius:12px;padding:14px 16px;
    border-left:4px solid;margin-bottom:10px;box-shadow:0 2px 8px {t['shadow']}}}
  .yr-badge{{display:inline-block;background:#ff7043;color:white;font-size:.65rem;
    font-weight:700;padding:2px 6px;border-radius:4px;margin-left:6px;vertical-align:middle}}
  .planet-card{{background:{t['card']};border:1px solid {t['border']};border-radius:10px;
    padding:12px;text-align:center;margin-bottom:8px}}
  label,.stSelectbox label,[data-testid="stWidgetLabel"]{{color:{t['text2']} !important}}
  hr{{border-color:{t['border']}}}
  [data-testid="stRadio"] label{{color:{t['text']} !important}}
  .stButton>button{{background:{hex_to_rgba(t['accent'],.13)};border:1px solid {hex_to_rgba(t['accent'],.4)};
    color:{t['text']};border-radius:8px}}
  .stButton>button:hover{{background:{hex_to_rgba(t['accent'],.27)}}}
  .block-container{{padding-top:1.5rem !important}}
</style>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# РЕНДЕР НОВОСТЕЙ
# ─────────────────────────────────────────────
def render_news(news_list: list, t: dict, cols: int = 3):
    columns = st.columns(cols)
    for i, item in enumerate(news_list):
        with columns[i % cols]:
            st.markdown(f"""
<a href="{item['url']}" target="_blank" class="news-card">
  <div class="news-card-title">{item['icon']} {item['title']}</div>
  <div class="news-card-sub">{item['url'].split('/')[2]}</div>
</a>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════
def main():
    st.set_page_config(page_title="🌦 Погода v2", page_icon="🌦",
                       layout="wide", initial_sidebar_state="expanded")

    # ── Сайдбар ──────────────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ Настройки")
        city_name = st.selectbox("🏙 Город", list(CITIES.keys()), index=0)
        city = CITIES[city_name]
        theme_name = st.radio("🎨 Тема", list(THEMES.keys()), index=0)
        t = THEMES[theme_name]
        st.markdown("---")
        st.markdown("### 📡 Источники данных")
        use_yr = st.checkbox("🇳🇴 Сравнить с Yr.no (MET Norway)", value=False,
                             help="Добавляет прогноз Yr.no на графики пунктиром")
        st.markdown("---")
        astro_mode = st.toggle("🔭 Режим Астрономия", value=False)
        st.markdown("---")
        st.markdown(f"<span style='color:{t['text2']};font-size:.78rem'>📍 {city['lat']:.4f}°N {city['lon']:.4f}°E</span>",
                    unsafe_allow_html=True)
        if not EPHEM_OK:
            st.warning("Установите ephem для данных о планетах:\n```\npip install ephem\n```")

    apply_theme(t)

    # ── Загрузка ─────────────────────────────
    with st.spinner("Загружаю данные…"):
        data   = fetch_openmeteo(city["lat"], city["lon"])
        marine = fetch_marine(city["lat"], city["lon"])
        yr_data = fetch_yr(city["lat"], city["lon"]) if use_yr else None

    if not data:
        st.error("Нет данных от Open-Meteo. Проверьте соединение.")
        return

    cw = data["current_weather"]; hourly = data["hourly"]; daily = data["daily"]
    now_str = cw["time"]
    try:    ni = hourly["time"].index(now_str)
    except: ni = 0

    def h(key): v = hourly.get(key, [None]*(ni+1)); return v[ni] if v else None

    temp        = cw.get("temperature", h("temperature_2m")) or 0
    feelslike   = h("apparent_temperature") or temp
    humidity    = h("relativehumidity_2m") or 0
    pressure    = h("surface_pressure") or 1013
    wind_speed  = cw.get("windspeed", h("windspeed_10m")) or 0
    wind_dir    = cw.get("winddirection", h("winddirection_10m")) or 0
    cloudcover  = h("cloudcover") or 0
    visibility  = (h("visibility") or 10000) / 1000
    uv_index    = h("uv_index") or 0
    precip_prob = h("precipitation_probability") or 0
    cape        = h("cape") or 0
    lightning   = h("lightning_potential") or 0
    wmo_code    = int(cw.get("weathercode", 0))
    storm       = storm_index(cape, lightning, humidity)

    # Морские данные на текущий час
    marine_now = {}
    if marine and marine.get("hourly"):
        mh = marine["hourly"]
        try:    mi = mh["time"].index(now_str)
        except: mi = 0
        def mg(k): return (mh.get(k) or [None])[mi]
        marine_now = {"wave_height": mg("wave_height"), "wave_dir": mg("wave_direction"),
                      "wave_period": mg("wave_period"),  "sst": mg("sea_surface_temperature")}

    def parse_dt(s):
        try: return datetime.fromisoformat(s)
        except: return None
    sunrise_dt = parse_dt(daily["sunrise"][0] if daily.get("sunrise") else None)
    sunset_dt  = parse_dt(daily["sunset"][0]  if daily.get("sunset")  else None)
    now_dt     = datetime.now()
    time_to_sunset = ""
    if sunset_dt:
        diff = sunset_dt - now_dt
        if diff.total_seconds() > 0:
            time_to_sunset = f"{int(diff.total_seconds()//3600)}ч {int(diff.total_seconds()%3600//60)}мин"

    # ── АНИМАЦИЯ ─────────────────────────────
    if astro_mode:
        st.markdown(astro_banner(), unsafe_allow_html=True)
    else:
        st.markdown(get_weather_animation(wmo_code, t), unsafe_allow_html=True)

    # ── ЗАГОЛОВОК ────────────────────────────
    c1, c2 = st.columns([3,1])
    with c1:
        yr_b = '<span class="yr-badge">+ Yr.no</span>' if use_yr else ""
        mar_b= '<span class="yr-badge" style="background:#0288d1">+ Marine</span>' if marine else ""
        st.markdown(f"""<div>
  <div class="city-header">{city_name} {yr_b}{mar_b}</div>
  <div class="city-sub">{wmo_description(wmo_code)} · {now_str[:16].replace('T',' ')}</div>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style="text-align:right;padding-top:4px">
  <div style="font-size:3rem;font-weight:900;color:{t['text']};line-height:1">{temp:.1f}°C</div>
  <div style="color:{t['text2']};font-size:.88rem">Ощущается {feelslike:.1f}°C</div>
</div>""", unsafe_allow_html=True)

    # Yr.no панель сравнения
    if use_yr:
        if yr_data:
            yc_t = next((v for v in yr_data["temp"]      if v is not None), None)
            yc_w = next((v for v in yr_data["wind_speed"]if v is not None), None)
            yc_h = next((v for v in yr_data["humidity"]  if v is not None), None)
            yc_p = next((v for v in yr_data["pressure"]  if v is not None), None)
            if yc_t is not None:
                diff_t = yc_t - temp
                agree  = abs(diff_t) <= 2
                st.markdown(f"""
<div class="metric-card" style="border-left:3px solid #ff7043;margin-top:6px">
  <div class="metric-label">🇳🇴 Yr.no — независимый прогноз (MET Norway)</div>
  <div style="display:flex;gap:20px;flex-wrap:wrap;margin-top:6px">
    <span style="color:{t['text']}">🌡 <b>{yc_t:.1f}°C</b>
      <span style="color:{'#43a047' if agree else '#e53935'};font-size:.8rem">
        ({'+'if diff_t>=0 else ''}{diff_t:.1f}°)</span></span>
    {'<span style="color:'+t['text']+'">💧 <b>'+f"{yc_h:.0f}%</b></span>" if yc_h else ""}
    {'<span style="color:'+t['text']+'">💨 <b>'+f"{yc_w:.1f} м/с</b></span>" if yc_w else ""}
    {'<span style="color:'+t['text']+'">🌀 <b>'+f"{yc_p:.0f} гПа</b></span>" if yc_p else ""}
  </div>
  <div style="font-size:.72rem;color:{t['text2']};margin-top:4px">
    {'✅ Прогнозы совпадают' if agree else '⚠️ Расхождение температур: '+f"{abs(diff_t):.1f}°C"}
  </div>
</div>""", unsafe_allow_html=True)
        else:
            st.warning("Yr.no: API временно недоступен")

    st.markdown("---")

    # ══════════════════════════════════════════
    # АСТРОНОМИЯ
    # ══════════════════════════════════════════
    if astro_mode:
        doy    = now_dt.timetuple().tm_yday
        month  = now_dt.month
        clarity= sky_clarity(cloudcover, humidity)
        moon_text, moon_frac = moon_phase_text(doy)
        astro  = astro_conditions(clarity, moon_frac, visibility)
        consts = visible_constellations(city["lat"], month)
        twilights = calc_twilights(city["lat"], city["lon"], now_dt)

        # Метрики
        a1,a2,a3 = st.columns(3)
        with a1:
            st.markdown(f"""<div class="metric-card">
  <div class="metric-label">Чистота неба</div>
  <div class="metric-value" style="color:{t['accent']}">{clarity}%</div>
  <div class="metric-sub">Облачность {cloudcover:.0f}%, влажность {humidity:.0f}%</div>
</div>""", unsafe_allow_html=True)
        with a2:
            st.markdown(f"""<div class="metric-card">
  <div class="metric-label">Фаза луны</div>
  <div class="metric-value">{moon_text}</div>
  <div class="metric-sub">Яркость {moon_frac*100:.0f}%</div>
</div>""", unsafe_allow_html=True)
        with a3:
            st.markdown(f"""<div class="metric-card">
  <div class="metric-label">Условия для астрофото</div>
  <div class="metric-value" style="color:{astro['color']}">{astro['verdict']}</div>
  <div class="metric-sub">Оценка {astro['score']}/100</div>
</div>""", unsafe_allow_html=True)

        # Сумерки
        st.markdown("<div class='section-title'>🌅 Астрономические сумерки</div>", unsafe_allow_html=True)
        t1,t2,t3 = st.columns(3)
        for col, label, key, color in [
            (t1,"Гражданские (-6°)",    "civil",        "#fb8c00"),
            (t2,"Навигационные (-12°)", "nautical",     "#7b1fa2"),
            (t3,"Астрономические (-18°)","astronomical","#1565c0"),
        ]:
            tw = twilights.get(key, {})
            with col:
                st.markdown(f"""<div class="metric-card" style="border-left:3px solid {color}">
  <div class="metric-label">{label}</div>
  <div style="color:{t['text']};font-size:.95rem;margin-top:6px">
    🌆 Вечер: <b>{tw.get('evening','—')}</b><br>
    🌄 Утро: <b>{tw.get('morning','—')}</b>
  </div>
</div>""", unsafe_allow_html=True)

        # Лучшее время
        if sunset_dt and sunrise_dt:
            bs = sunset_dt + timedelta(hours=1, minutes=30)
            be = sunrise_dt + timedelta(days=1) - timedelta(hours=1)
            st.markdown(f"""<div class="metric-card">
  <div class="metric-label">⏰ Идеальное время наблюдений</div>
  <div class="metric-value" style="font-size:1.1rem;color:{t['accent']}">{bs.strftime('%H:%M')} — {be.strftime('%H:%M')}</div>
  <div class="metric-sub">После гражданских сумерек до рассвета</div>
</div>""", unsafe_allow_html=True)

        # Созвездия
        st.markdown("<div class='section-title'>🌌 Видимые созвездия</div>", unsafe_allow_html=True)
        cc = st.columns(3)
        for i, c in enumerate(consts[:6]):
            with cc[i%3]:
                st.markdown(f"""<div class="metric-card" style="padding:10px 14px">
  <div style="font-size:.95rem;color:{t['text']}">{c}</div>
</div>""", unsafe_allow_html=True)

        # Планеты
        st.markdown("<div class='section-title'>🪐 Планеты сегодня</div>", unsafe_allow_html=True)
        if EPHEM_OK:
            planets = get_planets(city["lat"], city["lon"])
            pcols = st.columns(4)
            for i, p in enumerate(planets):
                vc = "#43a047" if p["visible"] else t["border"]
                with pcols[i%4]:
                    st.markdown(f"""<div class="planet-card" style="border-color:{vc}">
  <div style="font-size:.95rem;font-weight:700;color:{t['text']}">{p['name']}</div>
  <div style="font-size:.72rem;color:{t['text2']};margin-top:5px;line-height:1.6">
    {'🟢 Видима' if p['visible'] else '🔴 Под горизонтом'}<br>
    Высота: <b>{p['alt']}°</b> · Азимут: <b>{p['az']}°</b><br>
    RA: {p['ra']} · Dec: {p['dec']}<br>
    Зв. величина: {p['mag']}
  </div>
</div>""", unsafe_allow_html=True)

            vis_planets = [p for p in planets if p["visible"]]
            if vis_planets:
                coord_text = "\n".join(
                    f"{p['name']}: RA={p['ra']}  Dec={p['dec']}  Alt={p['alt']}°  Az={p['az']}°  mag={p['mag']}"
                    for p in vis_planets)
                st.text_area("📋 Координаты видимых планет (для копирования)", coord_text, height=130)
        else:
            st.info("Для данных о планетах установите: `pip install ephem`")

        # Stellarium
        st.markdown("<div class='section-title'>🌠 Карта звёздного неба — Stellarium Web</div>", unsafe_allow_html=True)
        stell_url = f"https://stellarium-web.org/?lat={city['lat']}&lng={city['lon']}&date={now_dt.strftime('%Y-%m-%d')}"
        st.markdown(f"""<iframe src="{stell_url}" width="100%" height="560"
  style="border:none;border-radius:14px" loading="lazy" title="Stellarium Web"></iframe>
<p style="color:{t['text2']};font-size:.75rem;margin-top:5px">
  🔭 stellarium-web.org ·
  <a href="{stell_url}" target="_blank" style="color:{t['accent']}">Открыть полноэкранно</a>
</p>""", unsafe_allow_html=True)

        # Sky-Map
        st.markdown("<div class='section-title'>🗺 Интерактивная карта неба — Sky-Map.org</div>", unsafe_allow_html=True)
        sky_url = (f"https://www.sky-map.org/?ra={city['lon']/15:.2f}&de={city['lat']:.2f}"
                   "&zoom=3&show_grid=1&show_constellation_lines=1&show_constellation_names=1&show_planets=1")
        st.markdown(f"""<iframe src="{sky_url}" width="100%" height="500"
  style="border:none;border-radius:14px" loading="lazy" title="Sky-Map.org"></iframe>
<p style="color:{t['text2']};font-size:.75rem;margin-top:5px">
  🌌 sky-map.org ·
  <a href="https://www.sky-map.org" target="_blank" style="color:{t['accent']}">Открыть сайт</a>
</p>""", unsafe_allow_html=True)

        # Световое загрязнение
        st.markdown("<div class='section-title'>💡 Карта светового загрязнения</div>", unsafe_allow_html=True)
        lp_url = (f"https://www.lightpollutionmap.info/#zoom=8&lat={city['lat']}&lon={city['lon']}"
                  "&state=eyJiYXNlbWFwIjoiTGF5ZXJCaW5nUm9hZCIsIm92ZXJsYXkiOiJzYl8yMDI1Iiw"
                  "ib3ZlcmxheWNvbG9yIjpmYWxzZSwib3ZlcmxheW9wYWNpdHkiOiI2MCIsImZlYXR1cmVzb3"
                  "BhY2l0eSI6Ijg1In0=")
        st.markdown(f"""<iframe src="{lp_url}" width="100%" height="500"
  style="border:none;border-radius:14px" loading="lazy" title="Light Pollution Map"></iframe>
<p style="color:{t['text2']};font-size:.75rem;margin-top:5px">
  💡 lightpollutionmap.info — чем темнее, тем лучше для наблюдений ·
  <a href="{lp_url}" target="_blank" style="color:{t['accent']}">Открыть</a>
</p>""", unsafe_allow_html=True)

        # Астро новости
        st.markdown("<div class='section-title'>📰 Астро новости</div>", unsafe_allow_html=True)
        render_news(ASTRO_NEWS, t, cols=3)

        st.markdown("---")

    # ══════════════════════════════════════════
    # ТЕКУЩИЕ УСЛОВИЯ
    # ══════════════════════════════════════════
    st.markdown("<div class='section-title'>📊 Текущие условия</div>", unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    for col,label,val,sub in [
        (m1,"💧 Влажность",  f"{humidity:.0f}%",     ""),
        (m2,"🌀 Давление",   f"{pressure:.0f} гПа",  ""),
        (m3,"☀️ УФ-индекс", f"{uv_index:.1f}",      ""),
        (m4,"👁 Видимость",  f"{visibility:.1f} км", ""),
    ]:
        with col: st.markdown(f"""<div class="metric-card">
  <div class="metric-label">{label}</div><div class="metric-value">{val}</div><div class="metric-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

    m5,m6,m7,m8 = st.columns(4)
    for col,label,val,sub in [
        (m5,"💨 Ветер",        f"{wind_speed:.1f} м/с", f"{wind_direction_text(wind_dir)} ({wind_dir:.0f}°)"),
        (m6,"🌧 Вер. осадков", f"{precip_prob:.0f}%",   ""),
        (m7,"🌅 Восход",       sunrise_dt.strftime('%H:%M') if sunrise_dt else "—", ""),
        (m8,"🌇 Закат",        sunset_dt.strftime('%H:%M') if sunset_dt else "—",
                               f"Через {time_to_sunset}" if time_to_sunset else ""),
    ]:
        with col: st.markdown(f"""<div class="metric-card">
  <div class="metric-label">{label}</div><div class="metric-value">{val}</div><div class="metric-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

    # Морские данные
    if marine_now and any(v is not None for v in marine_now.values()):
        st.markdown("<div class='section-title'>🌊 Морские условия (Open-Meteo Marine)</div>", unsafe_allow_html=True)
        sc = st.columns(4)
        for col, label, key, fmt in [
            (sc[0],"🌊 Высота волн",   "wave_height",  lambda v: f"{v:.1f} м"),
            (sc[1],"🧭 Направ. волн",  "wave_dir",     lambda v: f"{v:.0f}° {wind_direction_text(v)}"),
            (sc[2],"⏱ Период волн",   "wave_period",  lambda v: f"{v:.1f} с"),
            (sc[3],"🌡 Темп. воды",    "sst",          lambda v: f"{v:.1f}°C"),
        ]:
            v = marine_now.get(key)
            with col: st.markdown(f"""<div class="metric-card" style="border-left:3px solid #0288d1">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{fmt(v) if v is not None else '—'}</div>
</div>""", unsafe_allow_html=True)

    # Грозовой индекс
    st.markdown("<div class='section-title'>⚡ Грозовой индекс</div>", unsafe_allow_html=True)
    gi1, gi2 = st.columns([2,1])
    with gi1:
        st.markdown(f"""<div class="metric-card">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
    <span style="font-size:2rem">{storm['emoji']}</span>
    <div>
      <div style="font-size:1.3rem;font-weight:700;color:{storm['color']}">{storm['level']}</div>
      <div style="color:{t['text2']};font-size:.83rem">Шанс грозы: {storm['pct']}%</div>
    </div>
  </div>
  <div class="storm-bar-outer">
    <div style="height:10px;border-radius:8px;background:{storm['color']};width:{storm['pct']}%;transition:width 1s ease"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:.77rem;color:{t['text2']}">
    <span>CAPE: {cape:.0f} Дж/кг</span><span>Молнии: {lightning:.0f}%</span><span>Влажность: {humidity:.0f}%</span>
  </div>
</div>""", unsafe_allow_html=True)
    with gi2:
        st.markdown(f"""<div class="metric-card">
  <div class="metric-label">☁️ Облачность</div>
  <div class="metric-value">{cloudcover:.0f}%</div>
  <div class="metric-sub">{wmo_description(wmo_code)}</div>
</div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    # ПОВСЕДНЕВНЫЕ СОВЕТЫ
    # ══════════════════════════════════════════
    st.markdown("<div class='section-title'>🗓 Повседневные советы</div>", unsafe_allow_html=True)
    advice = daily_advice(temp, feelslike, wind_speed, humidity,
                          pressure, visibility, precip_prob, wmo_code, uv_index, cape)
    ac1, ac2 = st.columns(2)
    for i, adv in enumerate(advice):
        with (ac1 if i%2==0 else ac2):
            st.markdown(f"""<div class="advice-card" style="border-left-color:{adv['color']}">
  <div style="font-size:.8rem;font-weight:700;color:{adv['color']};text-transform:uppercase;
              letter-spacing:.06em;margin-bottom:5px">{adv['title']}</div>
  <div style="font-size:.92rem;color:{t['text']}">{adv['text']}</div>
</div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    # ГРАФИКИ
    # ══════════════════════════════════════════
    st.markdown("<div class='section-title'>📈 Прогноз на 5 дней</div>", unsafe_allow_html=True)
    if use_yr and yr_data:
        st.caption("— Open-Meteo   ╌ Yr.no (пунктир)")
    charts = make_forecast_charts(hourly, t, yr_data if use_yr else None)
    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(charts[0], use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(charts[2], use_container_width=True, config={"displayModeBar": False})
    with ch2:
        st.plotly_chart(charts[1], use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(charts[3], use_container_width=True, config={"displayModeBar": False})

    # Суточный прогноз
    st.markdown("<div class='section-title'>📅 Прогноз по дням</div>", unsafe_allow_html=True)
    dcols = st.columns(7)
    for i in range(min(7, len(daily.get("time",[])))):
        with dcols[i]:
            dd = daily["time"][i]; dw = daily["weathercode"][i]
            dm = daily["temperature_2m_max"][i]; dn = daily["temperature_2m_min"][i]
            dr = daily["precipitation_probability_max"][i]
            lbl = "Сег." if i==0 else ("Завт." if i==1 else datetime.fromisoformat(dd).strftime("%d.%m"))
            ico = "☀️" if dw<=1 else ("⛅" if dw<=3 else ("🌧" if 50<=dw<=82 else ("⛈" if dw>=95 else "🌥")))
            st.markdown(f"""<div class="metric-card" style="text-align:center;padding:10px 6px">
  <div style="font-size:.75rem;color:{t['text2']};font-weight:600">{lbl}</div>
  <div style="font-size:1.3rem;margin:4px 0">{ico}</div>
  <div style="font-size:.9rem;font-weight:700;color:{t['text']}">{dm:.0f}°</div>
  <div style="font-size:.8rem;color:{t['text2']}">{dn:.0f}°</div>
  <div style="font-size:.72rem;color:{t['accent']}">💧{dr:.0f}%</div>
</div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    # МЕТЕО НОВОСТИ
    # ══════════════════════════════════════════
    st.markdown("<div class='section-title'>📰 Метео новости</div>", unsafe_allow_html=True)
    render_news(METEO_NEWS, t, cols=3)

    # ══════════════════════════════════════════
    # РАДАР
    # ══════════════════════════════════════════
    st.markdown("<div class='section-title'>🗺 Радар и грозопеленгация</div>", unsafe_allow_html=True)

    if "radar_key" not in st.session_state:
        st.session_state.radar_key = 0
    if st.button("🔄 Обновить радары"):
        st.session_state.radar_key += 1

    lat_r, lon_r = city["lat"], city["lon"]

    st.markdown(f"**⚡ Blitzortung — молниедетектор реального времени**")
    blitz = f"https://www.blitzortung.org/en/live_lightning_maps.php?map=11&lat={lat_r}&lon={lon_r}"
    st.markdown(f"""<iframe src="{blitz}" width="100%" height="500"
  style="border:none;border-radius:12px" loading="lazy"></iframe>
<p style="color:{t['text2']};font-size:.75rem;margin-top:4px">
  🔴 blitzortung.org · {lat_r:.2f}°N, {lon_r:.2f}°E
</p>""", unsafe_allow_html=True)

    st.markdown(f"**🌧 МетеоЛогикс — радар осадков**")
    mlogix = f"https://meteologix.com/ru/radar/europe-precipitation.html#{lat_r},{lon_r},7"
    st.markdown(f"""<iframe src="{mlogix}" width="100%" height="500"
  style="border:none;border-radius:12px" loading="lazy"></iframe>
<p style="color:{t['text2']};font-size:.75rem;margin-top:4px">
  🌧 meteologix.com ·
  <a href="https://meteologix.com/ru/radar/" target="_blank" style="color:{t['accent']}">Открыть в новой вкладке</a>
</p>""", unsafe_allow_html=True)

    # Футер
    st.markdown("---")
    yr_link = f' · <a href="https://api.met.no" style="color:{t["accent"]}">Yr.no</a>' if use_yr else ""
    st.markdown(
        f"<div style='text-align:center;color:{t['text2']};font-size:.75rem;line-height:2'>"
        f"Данные: "
        f"<a href='https://open-meteo.com' style='color:{t['accent']}'>Open-Meteo</a> · "
        f"<a href='https://marine-api.open-meteo.com' style='color:{t['accent']}'>Marine</a>"
        f"{yr_link} · "
        f"<a href='https://blitzortung.org' style='color:{t['accent']}'>Blitzortung</a> · "
        f"<a href='https://meteologix.com' style='color:{t['accent']}'>МетеоЛогикс</a>"
        f"</div>",
        unsafe_allow_html=True)


if __name__ == "__main__":
    main()
