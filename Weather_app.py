"""
╔══════════════════════════════════════════════════════════════╗
║  🌦️  WEATHER APP v3  —  Streamlit                           ║
║  Полнофункциональное метео-приложение                        ║
║  Запуск: streamlit run weather_app.py                        ║
║  Зависимости: streamlit pandas plotly requests numpy ephem   ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import math
import json

try:
    import ephem
    EPHEM_OK = True
except ImportError:
    EPHEM_OK = False

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ ГОРОДОВ  (lat, lon, METAR-станция, WMO-зонд)
# ═══════════════════════════════════════════════════════════════
CITIES = {
    "Минск":     {"lat":53.9045,"lon":27.5615,"metar":"UMMS","sounding":"33345"},
    "Харьков":   {"lat":49.9935,"lon":36.2304,"metar":"UKHH","sounding":"34300"},
    "Ужгород":   {"lat":48.6208,"lon":22.2879,"metar":"UKLU","sounding":"33393"},
    "Москва":    {"lat":55.7558,"lon":37.6173,"metar":"UUWW","sounding":"27612"},
    "Люберцы":   {"lat":55.6778,"lon":37.8927,"metar":"UUWW","sounding":"27612"},
    "Серпухов":  {"lat":54.9167,"lon":37.4167,"metar":"UUWW","sounding":"27612"},
    "Владимир":  {"lat":56.1366,"lon":40.3966,"metar":"UUEE","sounding":"27459"},
    "Гороховец": {"lat":56.2003,"lon":42.6867,"metar":"UUEE","sounding":"27459"},
    "Пенза":     {"lat":53.1959,"lon":45.0183,"metar":"UWPP","sounding":"28698"},
    "Тамбов":    {"lat":52.7212,"lon":41.4522,"metar":"UUOB","sounding":"27786"},
    "Киев":      {"lat":50.4501,"lon":30.5234,"metar":"UKBB","sounding":"33345"},
    "Алма-Ата":  {"lat":43.2220,"lon":76.8512,"metar":"UAAA","sounding":"38457"},
    "Ташкент":   {"lat":41.2995,"lon":69.2401,"metar":"UTTT","sounding":"38353"},
    "Баку":      {"lat":40.4093,"lon":49.8671,"metar":"UBBB","sounding":"37849"},
    "Ереван":    {"lat":40.1792,"lon":44.4991,"metar":"UDYZ","sounding":"37716"},
    "Тбилиси":   {"lat":41.6938,"lon":44.8015,"metar":"UGTB","sounding":"37789"},
    "Кишинёв":   {"lat":47.0105,"lon":28.8638,"metar":"LUKK","sounding":"33902"},
    "Рига":      {"lat":56.9460,"lon":24.1059,"metar":"EVRA","sounding":"26422"},
    "Вильнюс":   {"lat":54.6872,"lon":25.2797,"metar":"EYVI","sounding":"26629"},
    "Таллин":    {"lat":59.4370,"lon":24.7536,"metar":"EETN","sounding":"26038"},
}

# ═══════════════════════════════════════════════════════════════
# ТЕМЫ
# ═══════════════════════════════════════════════════════════════
THEMES = {
    "Тёмная":  {"bg":"#0d1117","bg2":"#161b22","card":"#1c2333","text":"#e6edf3",
                "text2":"#8b949e","accent":"#58a6ff","accent2":"#3fb950",
                "border":"#30363d","shadow":"rgba(0,0,0,0.5)"},
    "Светлая": {"bg":"#f0f4f8","bg2":"#ffffff","card":"#ffffff","text":"#1a202c",
                "text2":"#718096","accent":"#3182ce","accent2":"#38a169",
                "border":"#e2e8f0","shadow":"rgba(0,0,0,0.1)"},
    "Бежевая": {"bg":"#f5f0e8","bg2":"#ede8dc","card":"#faf7f2","text":"#3d2b1f",
                "text2":"#7a6452","accent":"#c17f3e","accent2":"#6b8f52",
                "border":"#d4c9b8","shadow":"rgba(60,40,20,0.15)"},
    "Амбиент": {"bg":"#1a1a2e","bg2":"#16213e","card":"#0f3460","text":"#e0e0e0",
                "text2":"#a0a0b0","accent":"#e94560","accent2":"#53d8fb",
                "border":"#1a3a5c","shadow":"rgba(0,0,0,0.6)"},
}

# ═══════════════════════════════════════════════════════════════
# НОВОСТНЫЕ ССЫЛКИ
# ═══════════════════════════════════════════════════════════════
METEO_NEWS = [
    {"title":"Gismeteo — новости",    "url":"https://www.gismeteo.ru/news/",           "icon":"🌦"},
    {"title":"Meteoinfo.ru",          "url":"http://www.meteoinfo.ru/news",             "icon":"📡"},
    {"title":"Severe Weather EU",     "url":"https://www.severe-weather.eu/",           "icon":"⛈"},
    {"title":"Weather.com News",      "url":"https://weather.com/news/weather",         "icon":"🌍"},
    {"title":"WMO — World Met. Org.", "url":"https://public.wmo.int/en/media/news",     "icon":"🏛"},
    {"title":"Погода Mail.ru",        "url":"https://pogoda.mail.ru/news/",             "icon":"☁️"},
]
ASTRO_NEWS = [
    {"title":"Астронет",              "url":"http://www.astronet.ru/db/msg/",           "icon":"🔭"},
    {"title":"SpaceWeather.com",      "url":"https://spaceweather.com/",                "icon":"☀️"},
    {"title":"Sky & Telescope",       "url":"https://skyandtelescope.org/astronomy-news/","icon":"🌠"},
    {"title":"Space.com",             "url":"https://www.space.com/astronomy",          "icon":"🚀"},
    {"title":"EarthSky",              "url":"https://earthsky.org/",                    "icon":"🌌"},
    {"title":"NASA News",             "url":"https://www.nasa.gov/news/",               "icon":"🛸"},
]

# WMO-коды → описание
WMO_DESC = {
    0:"Ясно",1:"Преимущественно ясно",2:"Переменная облачность",3:"Облачно",
    45:"Туман",48:"Изморозь",51:"Лёгкая морось",53:"Умеренная морось",
    55:"Сильная морось",61:"Лёгкий дождь",63:"Умеренный дождь",65:"Сильный дождь",
    71:"Лёгкий снег",73:"Умеренный снег",75:"Сильный снег",77:"Снежная крупа",
    80:"Ливень (слабый)",81:"Ливень (умеренный)",82:"Ливень (сильный)",
    85:"Снегопад (слабый)",86:"Снегопад (сильный)",
    95:"Гроза",96:"Гроза с градом",99:"Гроза с сильным градом",
}

# ═══════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def fetch_openmeteo(lat, lon):
    """Основной прогноз Open-Meteo."""
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude":lat,"longitude":lon,"current_weather":True,
            "hourly":(
                "temperature_2m,relativehumidity_2m,dewpoint_2m,apparent_temperature,"
                "precipitation_probability,precipitation,weathercode,surface_pressure,"
                "cloudcover,windspeed_10m,winddirection_10m,windgusts_10m,visibility,"
                "uv_index,cape,lightning_potential,soil_temperature_0cm,soil_temperature_6cm,"
                "soil_moisture_0_1cm,temperature_850hPa,temperature_700hPa,temperature_500hPa,"
                "temperature_300hPa,dewpoint_850hPa,dewpoint_700hPa,dewpoint_500hPa,"
                "windspeed_850hPa,windspeed_700hPa,windspeed_500hPa,"
                "winddirection_850hPa,winddirection_700hPa,winddirection_500hPa"
            ),
            "daily":(
                "weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset,"
                "uv_index_max,windspeed_10m_max,windgusts_10m_max,"
                "precipitation_probability_max,precipitation_sum,snowfall_sum"
            ),
            "wind_speed_unit":"ms","timezone":"auto","forecast_days":7,
        }, timeout=12)
        r.raise_for_status(); return r.json()
    except Exception as e:
        st.error(f"Open-Meteo: {e}"); return None


@st.cache_data(ttl=600)
def fetch_marine(lat, lon):
    """Open-Meteo Marine — волны и температура воды."""
    try:
        r = requests.get("https://marine-api.open-meteo.com/v1/marine", params={
            "latitude":lat,"longitude":lon,
            "hourly":"wave_height,wave_direction,wave_period,sea_surface_temperature",
            "timezone":"auto","forecast_days":5,
        }, timeout=10)
        r.raise_for_status(); return r.json()
    except Exception:
        return None


@st.cache_data(ttl=600)
def fetch_airquality(lat, lon):
    """Open-Meteo Air Quality — AQI, пыльца, PM2.5."""
    try:
        r = requests.get("https://air-quality-api.open-meteo.com/v1/air-quality", params={
            "latitude":lat,"longitude":lon,
            "hourly":(
                "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,"
                "european_aqi,birch_pollen,grass_pollen,mugwort_pollen"
            ),
            "timezone":"auto","forecast_days":3,
        }, timeout=10)
        r.raise_for_status(); return r.json()
    except Exception:
        return None


@st.cache_data(ttl=3600)
def fetch_climate_norm(lat, lon):
    """Open-Meteo Archive — климатическая норма за последние 10 лет."""
    try:
        today = date.today()
        start = date(today.year - 10, today.month, today.day)
        end   = date(today.year - 1,  today.month, today.day)
        r = requests.get("https://archive-api.open-meteo.com/v1/archive", params={
            "latitude":lat,"longitude":lon,
            "start_date":start.isoformat(),"end_date":end.isoformat(),
            "daily":"temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone":"auto",
        }, timeout=15)
        r.raise_for_status()
        d = r.json().get("daily", {})
        tmax = [v for v in (d.get("temperature_2m_max") or []) if v is not None]
        tmin = [v for v in (d.get("temperature_2m_min") or []) if v is not None]
        prec = [v for v in (d.get("precipitation_sum") or []) if v is not None]
        return {
            "norm_tmax": round(np.mean(tmax),1) if tmax else None,
            "norm_tmin": round(np.mean(tmin),1) if tmin else None,
            "norm_prec": round(np.mean(prec),1) if prec else None,
        }
    except Exception:
        return None


@st.cache_data(ttl=600)
def fetch_yr(lat, lon):
    """Yr.no — независимый норвежский прогноз."""
    try:
        r = requests.get(
            "https://api.met.no/weatherapi/locationforecast/2.0/compact",
            params={"lat":round(lat,4),"lon":round(lon,4)},
            headers={"User-Agent":"WeatherAppV3/1.0 contact@demo.com"},
            timeout=10)
        r.raise_for_status()
        ts = r.json().get("properties",{}).get("timeseries",[])
        res = {"times":[],"temp":[],"humidity":[],"pressure":[],"wind_speed":[],"wind_dir":[]}
        for e in ts[:120]:
            inst = e.get("data",{}).get("instant",{}).get("details",{})
            res["times"].append(e["time"])
            res["temp"].append(inst.get("air_temperature"))
            res["humidity"].append(inst.get("relative_humidity"))
            res["pressure"].append(inst.get("air_pressure_at_sea_level"))
            res["wind_speed"].append(inst.get("wind_speed"))
            res["wind_dir"].append(inst.get("wind_from_direction"))
        return res
    except Exception:
        return None


@st.cache_data(ttl=900)
def fetch_metar(station_code):
    """METAR — авиационная метеосводка."""
    try:
        url = f"https://aviationweather.gov/api/data/metar?ids={station_code}&format=json"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        return data[0] if data else None
    except Exception:
        return None


@st.cache_data(ttl=900)
def fetch_taf(station_code):
    """TAF — авиационный прогноз погоды."""
    try:
        url = f"https://aviationweather.gov/api/data/taf?ids={station_code}&format=json"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        return data[0] if data else None
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def hex_to_rgba(hx, a=0.2):
    h=hx.lstrip("#"); return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"

def wind_dir_text(deg):
    return ["С","СВ","В","ЮВ","Ю","ЮЗ","З","СЗ"][round(float(deg)/45)%8]

def wmo_desc(code):
    return WMO_DESC.get(int(code), f"Код {code}")

def wmo_icon(code):
    c=int(code)
    if c<=1: return "☀️"
    elif c<=3: return "⛅"
    elif c in(45,48): return "🌫"
    elif c in range(51,68): return "🌧"
    elif c in range(71,78): return "❄️"
    elif c in range(80,83): return "🌧"
    elif c in range(85,87): return "🌨"
    elif c>=95: return "⛈"
    return "🌥"


def storm_index(cape, lightning, humidity):
    score = min(cape/3000,1)*0.5 + min(lightning/100,1)*0.35 + max(0,(humidity-50)/50)*0.15
    pct   = round(score*100)
    if score<0.2:   lv,co,em = "Низкая","#43a047","🟢"
    elif score<0.45: lv,co,em = "Средняя","#fb8c00","🟡"
    elif score<0.7:  lv,co,em = "Высокая","#e53935","🔴"
    else:            lv,co,em = "Экстремальная","#7b1fa2","🟣"
    return {"level":lv,"color":co,"emoji":em,"pct":pct}


def sky_clarity(cloudcover, humidity):
    return round(((100-cloudcover)/100*0.7+max(0,(100-humidity)/100)*0.3)*100)


def moon_phase(doy):
    f=(doy%29.5)/29.5
    if f<0.03 or f>0.97: return "🌑 Новолуние",f
    elif f<0.22: return "🌒 Растущий серп",f
    elif f<0.28: return "🌓 Первая четверть",f
    elif f<0.47: return "🌔 Растущая луна",f
    elif f<0.53: return "🌕 Полнолуние",f
    elif f<0.72: return "🌖 Убывающая луна",f
    elif f<0.78: return "🌗 Последняя четверть",f
    else:        return "🌘 Убывающий серп",f


def visible_constellations(lat, month):
    seasonal = {
        (12,1,2): ["Орион 🌟","Телец 🐂","Близнецы ♊","Возничий 🐐","Эридан 🌊","Персей ⚔️"],
        (3,4,5):  ["Лев 🦁","Дева ♍","Рак 🦀","Гидра 🐉","Ворон 🐦","Чаша 🏆"],
        (6,7,8):  ["Скорпион 🦂","Стрелец 🏹","Орёл 🦅","Лебедь 🦢","Лира 🎵","Геркулес 💪"],
        (9,10,11):["Пегас 🐴","Андромеда ✨","Рыбы 🐠","Водолей 💧","Козерог 🐐","Кит 🐋"],
    }
    result=["Большая Медведица 🐻","Малая Медведица ⭐","Кассиопея 👑"]
    for mt,cs in seasonal.items():
        if month in mt: result.extend(cs[:4]); break
    return result


def astro_score(clarity, moon_frac, visibility_km):
    score = clarity*0.5 + min(visibility_km/30,1)*30 - (1-abs(moon_frac-0.5)*2)*30
    score = max(0,min(100,score))
    if score>=65:   v,c="Отлично ✨","#43a047"
    elif score>=35: v,c="Средне 🌤","#fb8c00"
    else:           v,c="Плохо 🌧","#e53935"
    return {"verdict":v,"color":c,"score":round(score)}


# ─── Астрономические сумерки ───────────────────────────────────
def calc_twilights(lat, lon, dt):
    if EPHEM_OK:
        obs=ephem.Observer(); obs.lat=str(lat); obs.lon=str(lon)
        obs.date=dt.strftime("%Y/%m/%d 12:00:00"); obs.pressure=0
        res={}
        for name,hor in[("civil","-6"),("nautical","-12"),("astronomical","-18")]:
            obs.horizon=hor
            try:
                ev=ephem.localtime(obs.next_setting(ephem.Sun(),use_center=True)).strftime("%H:%M")
                mo=ephem.localtime(obs.next_rising(ephem.Sun(), use_center=True)).strftime("%H:%M")
                res[name]={"evening":ev,"morning":mo}
            except: res[name]={"evening":"—","morning":"—"}
        return res
    # Fallback без ephem
    doy=dt.timetuple().tm_yday
    decl=23.45*math.sin(math.radians(360/365*(doy-81)))
    lr=math.radians(lat); dr=math.radians(decl); noon=12-lon/15
    res={}
    for name,dep in[("civil",6),("nautical",12),("astronomical",18)]:
        try:
            ch=(math.sin(math.radians(-dep))-math.sin(lr)*math.sin(dr))/(math.cos(lr)*math.cos(dr))
            if abs(ch)>1: res[name]={"evening":"—","morning":"—"}; continue
            ha=math.degrees(math.acos(ch))
            def fmt(x): return f"{int(x)%24:02d}:{int((x%1)*60):02d}"
            res[name]={"evening":fmt(noon+ha/15),"morning":fmt(noon-ha/15)}
        except: res[name]={"evening":"—","morning":"—"}
    return res


# ─── Золотой / синий час ──────────────────────────────────────
def calc_golden_blue(lat, lon, dt):
    """Возвращает точные временные окна золотого и синего часа."""
    if not EPHEM_OK:
        return None
    obs=ephem.Observer(); obs.lat=str(lat); obs.lon=str(lon)
    obs.date=dt.strftime("%Y/%m/%d 12:00:00"); obs.pressure=0
    windows={}
    try:
        # Закатный золотой час: солнце между 0° и 6°
        obs.horizon="0"
        sunset=ephem.localtime(obs.next_setting(ephem.Sun(),use_center=True))
        obs.horizon="6"
        golden_eve_start=ephem.localtime(obs.next_setting(ephem.Sun(),use_center=True))
        windows["golden_evening"]={"start":golden_eve_start.strftime("%H:%M"),"end":sunset.strftime("%H:%M")}

        # Рассветный золотой час
        obs.date=dt.strftime("%Y/%m/%d 00:00:00")
        obs.horizon="0"
        sunrise=ephem.localtime(obs.next_rising(ephem.Sun(),use_center=True))
        obs.horizon="6"
        golden_mor_end=ephem.localtime(obs.next_rising(ephem.Sun(),use_center=True))
        windows["golden_morning"]={"start":sunrise.strftime("%H:%M"),"end":golden_mor_end.strftime("%H:%M")}

        # Синий час вечером: -6° до 0°
        obs.date=dt.strftime("%Y/%m/%d 12:00:00")
        obs.horizon="-6"
        blue_eve_end=ephem.localtime(obs.next_setting(ephem.Sun(),use_center=True))
        windows["blue_evening"]={"start":sunset.strftime("%H:%M"),"end":blue_eve_end.strftime("%H:%M")}

        # Синий час утром
        obs.date=dt.strftime("%Y/%m/%d 00:00:00")
        obs.horizon="-6"
        blue_mor_start=ephem.localtime(obs.next_rising(ephem.Sun(),use_center=True))
        windows["blue_morning"]={"start":blue_mor_start.strftime("%H:%M"),"end":sunrise.strftime("%H:%M")}

        windows["sunrise"]=sunrise.strftime("%H:%M")
        windows["sunset"]=sunset.strftime("%H:%M")
    except Exception:
        pass
    return windows


# ─── Дуга солнца ──────────────────────────────────────────────
def calc_sun_arc(lat, lon, dt):
    """Возвращает азимут и высоту солнца по часам."""
    if not EPHEM_OK:
        return None
    obs=ephem.Observer(); obs.lat=str(lat); obs.lon=str(lon); obs.pressure=0
    times,alts,azs=[],[],[]
    base=dt.replace(hour=0,minute=0,second=0,microsecond=0)
    for h in range(0,24*4):  # каждые 15 минут
        t=base+timedelta(minutes=h*15)
        obs.date=t.strftime("%Y/%m/%d %H:%M:%S")
        sun=ephem.Sun(obs)
        alts.append(round(math.degrees(sun.alt),2))
        azs.append(round(math.degrees(sun.az),2))
        times.append(t.strftime("%H:%M"))
    return {"times":times,"alt":alts,"az":azs}


# ─── Планеты ──────────────────────────────────────────────────
def get_planets(lat, lon):
    if not EPHEM_OK: return []
    obs=ephem.Observer(); obs.lat=str(lat); obs.lon=str(lon)
    obs.date=datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
    defs=[("Меркурий ☿",ephem.Mercury()),("Венера ♀",ephem.Venus()),
          ("Марс ♂",ephem.Mars()),("Юпитер ♃",ephem.Jupiter()),
          ("Сатурн ♄",ephem.Saturn()),("Уран ⛢",ephem.Uranus()),("Нептун ♆",ephem.Neptune())]
    res=[]
    for name,body in defs:
        body.compute(obs)
        alt=math.degrees(body.alt)
        res.append({"name":name,"alt":round(alt,1),"az":round(math.degrees(body.az),1),
                    "ra":str(body.ra),"dec":str(body.dec),"mag":round(body.mag,1),"visible":alt>0})
    return res


# ─── AQI описание ─────────────────────────────────────────────
def aqi_level(val):
    if val is None: return "—","#888"
    if val<=20:   return "Отличное 🟢",    "#43a047"
    elif val<=40: return "Хорошее 🟡",     "#c6c000"
    elif val<=60: return "Умеренное 🟠",   "#fb8c00"
    elif val<=80: return "Плохое 🔴",      "#e53935"
    elif val<=100:return "Очень плохое 🟣","#7b1fa2"
    else:         return "Опасное ⚫",      "#212121"


# ─── Повседневные советы ──────────────────────────────────────
def daily_advice(temp,feelslike,wind,humidity,pressure,visibility,precip_prob,wmo,uv,cape):
    adv=[]
    rain=precip_prob>40 or wmo in range(51,100)
    # Одежда
    if feelslike<-15:  c,cc="🧥 Зимняя куртка, термобельё, шапка, варежки","#1565c0"
    elif feelslike<-5: c,cc="🧥 Тёплая куртка, свитер, шапка, перчатки","#1976d2"
    elif feelslike<5:  c,cc="🧥 Куртка, кофта, шарф","#0288d1"
    elif feelslike<12: c,cc="🧦 Лёгкая куртка или плотная толстовка","#0097a7"
    elif feelslike<18: c,cc="👕 Толстовка или джемпер","#00897b"
    elif feelslike<24: c,cc="👕 Футболка, лёгкие брюки","#43a047"
    else:              c,cc="🩳 Лёгкая одежда, шорты","#f57f17"
    if rain: c+=" + ☂️ зонт"
    if wind>10: c+=" + ветровка"
    adv.append({"title":"👗 Одежда","text":c,"color":cc})

    # Рыбалка
    fs=0; fn=[]
    if 990<pressure<1020: fs+=3;fn.append("стабильное давление ✅")
    elif pressure<990:    fs+=1;fn.append("низкое давление ⚠️")
    else:                 fs+=2;fn.append("высокое давление")
    if wind<5:     fs+=2;fn.append("штиль ✅")
    elif wind<10:  fs+=1;fn.append("слабый ветер")
    else:          fn.append("сильный ветер ❌")
    if precip_prob<20 and wmo<51: fs+=2;fn.append("без осадков ✅")
    else: fn.append("осадки возможны")
    if 8<=temp<=22: fs+=2;fn.append("хорошая температура ✅")
    if fs>=7: fv,fc="Отличная рыбалка 🐟","#43a047"
    elif fs>=4: fv,fc="Неплохо 🎣","#fb8c00"
    else: fv,fc="Лучше дома","#e53935"
    adv.append({"title":"🎣 Рыбалка","text":f"{fv} — {', '.join(fn[:3])}","color":fc})

    # Походы
    if wmo>=95: ht,hc="Не рекомендуется — гроза ⛈","#e53935"
    elif visibility<1: ht,hc="Опасно — туман <1 км 🌫","#e53935"
    elif visibility>5 and wind<15 and precip_prob<30 and cape<500:
        if uv>7: ht,hc="Хорошо ⚠️ высокий УФ, SPF50+","#fb8c00"
        else: ht,hc="Отличные условия 🥾","#43a047"
    else: ht,hc="Условия неидеальны 🌦","#fb8c00"
    adv.append({"title":"🥾 Походы","text":ht,"color":hc})

    # Болезнь
    ss=(2 if humidity>80 else 0)+(1 if wind>8 else 0)+(2 if temp<5 else 0)+(1 if temp>28 else 0)+(1 if precip_prob>50 else 0)
    if ss<=1: st2,sc="Низкий риск 💪","#43a047"
    elif ss<=3: st2,sc="Умеренный — одевайтесь теплее 🧣","#fb8c00"
    else: st2,sc="Высокий риск 🤧","#e53935"
    adv.append({"title":"🤒 Риск заболеть","text":st2,"color":sc})

    # Рейс
    df=[]; ds=0
    if visibility<1:   ds+=4;df.append("туман")
    elif visibility<3: ds+=2;df.append("плохая видимость")
    if wmo>=95:        ds+=4;df.append("гроза")
    if wind>15:        ds+=3;df.append(f"ветер {wind:.0f}м/с")
    if wmo in range(71,78): ds+=2;df.append("снегопад")
    if ds==0:    dv,dc="Минимальный риск ✈️","#43a047"
    elif ds<=2:  dv,dc=f"Небольшой — {', '.join(df)}","#fb8c00"
    elif ds<=4:  dv,dc=f"Возможны задержки: {', '.join(df)} 🕐","#ff7043"
    else:        dv,dc=f"Высокий риск отмены: {', '.join(df)} ❌","#e53935"
    adv.append({"title":"✈️ Риск задержки рейса","text":dv,"color":dc})
    return adv


# ─── Лучший день недели ───────────────────────────────────────
def best_days(daily, hourly):
    """Анализирует прогноз и находит лучший день для каждой активности."""
    times=pd.to_datetime(hourly.get("time",[]))
    results={}
    categories={
        "🥾 Поход":    lambda d: (100-d["cloud"])*0.4 + max(0,1-d["wind"]/15)*30 + (100-d["precip"])*0.3,
        "🎣 Рыбалка":  lambda d: (1 if 990<d["press"]<1020 else 0.5)*30 + max(0,1-d["wind"]/10)*40 + (100-d["precip"])*0.3,
        "🔭 Астро":    lambda d: (100-d["cloud"])*0.7 + (100-d["humid"])*0.3,
        "📷 Фото":     lambda d: min(d["cloud"],70)*0.5 + max(0,1-d["wind"]/20)*30 + (100-d["precip"])*0.2 + 20,
        "🌱 Дача":     lambda d: (100-d["precip"])*0.5 + max(0,1-d["wind"]/15)*25 + (1 if 10<d["temp"]<28 else 0.3)*25,
    }
    days=[]
    for i in range(min(7,len(daily.get("time",[])))):
        dt_str=daily["time"][i]
        mask=pd.to_datetime(times).date==date.fromisoformat(dt_str)
        idxs=[j for j,b in enumerate(mask) if b]
        if not idxs: continue
        def havg(key):
            vals=[hourly.get(key,[None]*200)[j] for j in idxs if hourly.get(key,[None]*200)[j] is not None]
            return np.mean(vals) if vals else 0
        d={
            "date":dt_str,"idx":i,
            "cloud":havg("cloudcover"),"wind":havg("windspeed_10m"),
            "precip":havg("precipitation_probability"),"humid":havg("relativehumidity_2m"),
            "press":havg("surface_pressure"),"temp":havg("temperature_2m"),
        }
        days.append(d)
    for cat,fn in categories.items():
        if not days: continue
        scored=[(fn(d),d) for d in days]
        best=max(scored,key=lambda x:x[0])
        dt=date.fromisoformat(best[1]["date"])
        label="Сег." if best[1]["idx"]==0 else ("Завт." if best[1]["idx"]==1 else dt.strftime("%d.%m"))
        results[cat]={"label":label,"score":round(best[0])}
    return results


# ─── Индекс комфорта прогулки ─────────────────────────────────
def walk_comfort(temp, feelslike, wind, humidity, precip_prob, wmo):
    score=100
    if feelslike<-10 or feelslike>35: score-=40
    elif feelslike<0 or feelslike>30: score-=20
    elif feelslike<5 or feelslike>28: score-=10
    if wind>15: score-=30
    elif wind>10: score-=15
    elif wind>7:  score-=5
    if precip_prob>70 or wmo in range(60,100): score-=35
    elif precip_prob>40: score-=15
    if humidity>90: score-=10
    score=max(0,min(100,score))
    if score>=75:   return "Идеально 🌟",score,"#43a047"
    elif score>=55: return "Хорошо 😊",score,"#8bc34a"
    elif score>=35: return "Терпимо 😐",score,"#fb8c00"
    elif score>=15: return "Плохо 😕",score,"#e53935"
    else:           return "Сидите дома 🏠",score,"#7b1fa2"


# ─── Риск для фотооборудования ────────────────────────────────
def photo_gear_risk(temp, humidity, precip_prob, wmo, wind, feelslike):
    risks=[]; total=0
    if humidity>90: risks.append("💧 Конденсат на линзе (влажность >90%)"); total+=3
    elif humidity>80: risks.append("💧 Риск конденсата (влажность >80%)"); total+=1
    if wmo in range(61,83): risks.append("🌧 Риск попадания воды — нужна защита IP"); total+=4
    if wmo in(96,99): risks.append("🌨 КРИТИЧНО: Град — немедленно укройте оборудование!"); total+=8
    if wmo>=95: risks.append("⚡ Гроза — риск статического разряда на сенсоре"); total+=3
    if temp<-10: risks.append("🪫 Аккумулятор разряжается быстро (<-10°C)"); total+=2
    elif temp<0: risks.append("🪫 Следите за зарядом аккумулятора (<0°C)"); total+=1
    if abs(feelslike-temp)>8: risks.append("🌡 Резкий перепад температур — риск конденсата внутри объектива"); total+=2
    if wind>12: risks.append("💨 Сильный ветер — штатив обязателен, риск падения"); total+=2
    if total==0: return "✅ Условия безопасны для оборудования","#43a047",[]
    elif total<=3: return "⚠️ Умеренный риск","#fb8c00",risks
    elif total<=6: return "🔴 Высокий риск — используйте защиту","#e53935",risks
    else:          return "🆘 КРИТИЧЕСКИЙ РИСК","#7b1fa2",risks


# ─── Условия для фотосъёмки ──────────────────────────────────
def photo_conditions(cloudcover, humidity, wmo, visibility):
    # Частичная облачность на закате = драматичное небо
    if 20<=cloudcover<=70 and wmo<51 and visibility>5:
        sky,sc="🌅 Драматичное небо! Отличные условия","#43a047"
    elif cloudcover<20 and visibility>10:
        sky,sc="☀️ Чистое небо — хорошо для пейзажа","#8bc34a"
    elif humidity>80 and cloudcover<30:
        sky,sc="🌫 Туманная дымка — подходит для мистики","#fb8c00"
    elif wmo in(61,63,80,81):
        sky,sc="🌧 Дождь — интересные рефлексии","#0288d1"
    elif cloudcover>85:
        sky,sc="☁️ Сплошная облачность — плоский свет","#78909c"
    else:
        sky,sc="🌤 Переменная облачность — неплохо","#fb8c00"
    return sky,sc


# ─── Режим Огородник ─────────────────────────────────────────
def garden_forecast(daily, hourly):
    """Анализ условий для дачи на 7 дней."""
    result=[]
    for i in range(min(7,len(daily.get("time",[])))):
        tmin=daily["temperature_2m_min"][i]
        tmax=daily["temperature_2m_max"][i]
        prec=daily["precipitation_sum"][i] or 0
        prob=daily["precipitation_probability_max"][i] or 0
        wmo_d=daily["weathercode"][i]

        # Агрозаморозок
        frost=tmin<2
        # Нужен полив
        watering=prec<2 and tmax>18 and prob<30
        # Можно работать
        workable=not frost and tmax>8 and prob<50 and wmo_d not in range(60,100)

        dt=date.fromisoformat(daily["time"][i])
        lbl="Сег." if i==0 else ("Завт." if i==1 else dt.strftime("%d.%m"))
        result.append({
            "label":lbl,"tmin":tmin,"tmax":tmax,"prec":prec,"prob":prob,
            "frost":frost,"watering":watering,"workable":workable,"wmo":wmo_d
        })
    return result


# ─── Режим Дрон ───────────────────────────────────────────────
def drone_conditions(wind, gusts, visibility, precip_prob, wmo, temp):
    score=100; issues=[]
    if wind>10:  score-=40;issues.append(f"Ветер {wind:.1f}м/с >10 ❌")
    elif wind>7: score-=20;issues.append(f"Ветер {wind:.1f}м/с — осторожно")
    if gusts and gusts>12: score-=20;issues.append(f"Порывы {gusts:.1f}м/с ❌")
    if visibility<1: score-=50;issues.append("Туман — видимость <1км ❌")
    elif visibility<3: score-=20;issues.append("Плохая видимость")
    if wmo>=95: score-=60;issues.append("Гроза — ЗАПРЕЩЕНО ❌")
    elif wmo in range(60,100): score-=30;issues.append("Осадки — не рекомендуется")
    if temp<-10: score-=20;issues.append("Мороз — аккумулятор разряжается быстро")
    score=max(0,min(100,score))
    if score>=70:   v,c="✅ Безопасно","#43a047"
    elif score>=40: v,c="⚠️ Осторожно","#fb8c00"
    else:           v,c="🚫 Не летать","#e53935"
    return {"verdict":v,"color":c,"score":score,"issues":issues}


# ─── Упрощённый Skew-T ────────────────────────────────────────
def build_skewt(hourly, now_idx):
    """Строит упрощённую диаграмму T/Td по стандартным уровням давления."""
    levels  =[850,700,500,300]
    temps   =[hourly.get(f"temperature_{l}hPa",[None]*300)[now_idx] for l in levels]
    dewpts  =[hourly.get(f"dewpoint_{l}hPa",   [None]*300)[now_idx] for l in levels]
    wspeeds =[hourly.get(f"windspeed_{l}hPa",  [None]*300)[now_idx] for l in levels]
    wdirs   =[hourly.get(f"winddirection_{l}hPa",[None]*300)[now_idx] for l in levels]

    temps  =[v if v is not None else np.nan for v in temps]
    dewpts =[v if v is not None else np.nan for v in dewpts]
    wspeeds=[v if v is not None else np.nan for v in wspeeds]
    wdirs  =[v if v is not None else np.nan for v in wdirs]

    return {"levels":levels,"temps":temps,"dewpts":dewpts,"wspeeds":wspeeds,"wdirs":wdirs}


# ═══════════════════════════════════════════════════════════════
# CSS АНИМАЦИИ
# ═══════════════════════════════════════════════════════════════

def get_weather_animation(wmo_code, t):
    bg=t["card"]
    if wmo_code<=1:   wt="sunny"
    elif wmo_code<=3: wt="cloudy"
    elif wmo_code in range(95,100): wt="storm"
    elif wmo_code in range(51,82):  wt="rain"
    else: wt="cloudy"

    if wt=="sunny":
        return f"""<div class="weather-anim-box" style="background:linear-gradient(180deg,#1a3a5c,#ff7043 40%,#ffb300 70%,{bg});">
  <style>
    @keyframes sunrise{{0%{{transform:translateY(60px) scale(.7);opacity:.3}}100%{{transform:translateY(0) scale(1);opacity:1}}}}
    @keyframes rayspin{{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}}
    @keyframes shim{{0%,100%{{opacity:.7}}50%{{opacity:1}}}}
    .sw{{position:absolute;bottom:30px;left:50%;transform:translateX(-50%);animation:sunrise 2s ease-out forwards}}
    .sc{{width:70px;height:70px;background:radial-gradient(circle,#fff700,#ffb300);border-radius:50%;box-shadow:0 0 40px #ffb300,0 0 80px #ff8c00}}
    .sr{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);animation:rayspin 8s linear infinite}}
    .ry{{position:absolute;width:4px;height:90px;background:linear-gradient(transparent,rgba(255,179,0,.5),transparent);border-radius:2px;top:-45px;left:-2px}}
    .sov{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 100%,rgba(255,179,0,.2),transparent 70%);animation:shim 3s ease-in-out infinite}}
  </style>
  <div class="sov"></div>
  <div class="sw"><div class="sr">{''.join(f'<div class="ry" style="transform:rotate({i*30}deg)"></div>' for i in range(12))}</div><div class="sc"></div></div>
</div>"""

    elif wt=="cloudy":
        return f"""<div class="weather-anim-box" style="background:linear-gradient(180deg,#2c3e50,#4a5568 50%,{bg});">
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

    elif wt=="rain":
        rng=np.random.default_rng(42)
        dr=''.join(f'<div style="position:absolute;width:2px;background:linear-gradient(to bottom,transparent,#90caf9);border-radius:2px;top:0;left:{rng.integers(5,95)}%;height:{rng.integers(15,30)}px;opacity:{0.4+rng.random()*0.5:.2f};animation:fall {0.5+rng.random()*0.5:.2f}s {rng.random()*2:.2f}s linear infinite"></div>' for _ in range(35))
        return f"""<div class="weather-anim-box" style="background:linear-gradient(180deg,#1a1a2e,#2d3748 60%,{bg});overflow:hidden">
  <style>
    @keyframes fall{{0%{{transform:translateY(-20px);opacity:0}}80%{{opacity:1}}100%{{transform:translateY(130px);opacity:0}}}}
    @keyframes csway{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(10px)}}}}
    .rcl{{position:absolute;background:#455a64;border-radius:50px}}
    .rr1{{width:120px;height:50px;top:5px;left:15%;animation:csway 7s ease-in-out infinite}}
    .rr2{{width:150px;height:60px;top:15px;left:40%;animation:csway 9s ease-in-out infinite reverse}}
    .rr3{{width:100px;height:45px;top:8px;right:12%;animation:csway 6s ease-in-out infinite}}
    .rr1::before{{content:'';position:absolute;width:65px;height:65px;background:#455a64;border-radius:50%;top:-30px;left:20px}}
    .rr2::before{{content:'';position:absolute;width:80px;height:75px;background:#455a64;border-radius:50%;top:-38px;left:30px}}
    .rr3::before{{content:'';position:absolute;width:55px;height:55px;background:#455a64;border-radius:50%;top:-25px;left:18px}}
    .pdl{{position:absolute;bottom:6px;border-radius:50%;background:rgba(79,195,247,.2);animation:puddle 2s ease-in-out infinite}}
    @keyframes puddle{{0%,100%{{transform:scale(1);opacity:.5}}50%{{transform:scale(1.1);opacity:.8}}}}
  </style>
  <div class="rcl rr1"></div><div class="rcl rr2"></div><div class="rcl rr3"></div>{dr}
  <div class="pdl" style="width:60px;height:12px;left:20%;animation-delay:.3s"></div>
  <div class="pdl" style="width:90px;height:16px;left:50%;animation-delay:.8s"></div>
</div>"""

    else:  # storm
        rng=np.random.default_rng(7)
        dr=''.join(f'<div style="position:absolute;width:2px;background:linear-gradient(to bottom,transparent,#64b5f6);border-radius:2px;top:0;left:{rng.integers(5,95)}%;height:{rng.integers(20,40)}px;animation:sfall {0.3+rng.random()*0.4:.2f}s {rng.random()*1.5:.2f}s linear infinite"></div>' for _ in range(40))
        return f"""<div class="weather-anim-box" style="background:linear-gradient(180deg,#0d0d1a,#1a1a2e 60%,{bg});overflow:hidden">
  <style>
    @keyframes sfall{{0%{{transform:translateY(-20px) translateX(0);opacity:0}}100%{{transform:translateY(140px) translateX(-10px);opacity:.9}}}}
    @keyframes flash{{0%,90%,100%{{opacity:0}}92%,96%{{opacity:1}}}}
    @keyframes bolta{{0%,85%,100%{{opacity:0;transform:scaleY(0)}}87%,93%{{opacity:1;transform:scaleY(1)}}}}
    @keyframes tglow{{0%,89%,100%{{background:#0d0d1a}}90%,95%{{background:#1a2a4a}}}}
    .sbg{{position:absolute;inset:0;animation:tglow 4s linear infinite;z-index:0}}
    .scl{{position:absolute;background:#263238;border-radius:50px;z-index:1}}
    .sc1{{width:130px;height:55px;top:3px;left:10%}}.sc2{{width:160px;height:65px;top:10px;left:38%}}.sc3{{width:110px;height:48px;top:5px;right:10%}}
    .sc1::before{{content:'';position:absolute;width:70px;height:70px;background:#263238;border-radius:50%;top:-32px;left:22px}}
    .sc2::before{{content:'';position:absolute;width:88px;height:82px;background:#263238;border-radius:50%;top:-42px;left:32px}}
    .sc3::before{{content:'';position:absolute;width:62px;height:60px;background:#263238;border-radius:50%;top:-28px;left:20px}}
    .lfl{{position:absolute;inset:0;background:rgba(200,220,255,.12);animation:flash 4s linear infinite;z-index:2;pointer-events:none}}
    .blt{{position:absolute;z-index:3;font-size:40px;color:#fff176;text-shadow:0 0 20px #ffeb3b,0 0 40px #ff8f00;transform-origin:top center}}
    .b1{{top:50px;left:35%;animation:bolta 4s linear infinite}}.b2{{top:45px;left:62%;animation:bolta 4s linear infinite 2s}}
  </style>
  <div class="sbg"></div><div class="scl sc1"></div><div class="scl sc2"></div><div class="scl sc3"></div>
  {dr}<div class="lfl"></div><div class="blt b1">⚡</div><div class="blt b2">⚡</div>
</div>"""


def astro_banner():
    stars=''.join(f'<div style="position:absolute;border-radius:50%;background:#fff;width:{2+i%3}px;height:{2+i%3}px;top:{(i*37+11)%90}%;left:{(i*53+7)%95}%;animation:twinkle {1.5+i%4*0.5:.1f}s {i%5*0.3:.1f}s ease-in-out infinite"></div>' for i in range(60))
    return f"""<div style="position:relative;width:100%;height:160px;background:linear-gradient(180deg,#000005,#0a0a2e 40%,#0d1b4a);border-radius:16px;overflow:hidden;margin-bottom:20px">
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
  <div class="mw"></div>{stars}
  <div class="ss ss1"></div><div class="ss ss2"></div><div class="ss ss3"></div>
  <div class="atitle">🔭 РЕЖИМ АСТРОНОМИИ</div>
</div>"""


def photo_banner():
    return """<div style="position:relative;width:100%;height:160px;background:linear-gradient(180deg,#0d1b2a 0%,#1a237e 30%,#e65100 65%,#ff8f00 85%,#ffd54f 100%);border-radius:16px;overflow:hidden;margin-bottom:20px">
  <style>
    @keyframes sunrise2{{0%{{transform:translateY(80px);opacity:0}}100%{{transform:translateY(0);opacity:1}}}}
    @keyframes glow2{{0%,100%{{opacity:.6}}50%{{opacity:1}}}}
    @keyframes cfloat{{0%,100%{{transform:translateX(0) translateY(0)}}50%{{transform:translateX(15px) translateY(-5px)}}}}
    .psun{{position:absolute;bottom:20px;left:50%;transform:translateX(-50%);width:60px;height:60px;background:radial-gradient(#fff9c4,#ff8f00);border-radius:50%;box-shadow:0 0 50px #ff8f00,0 0 100px rgba(255,143,0,.4);animation:sunrise2 2s ease-out forwards,glow2 4s ease-in-out infinite 2s}}
    .pcl{{position:absolute;background:rgba(255,183,77,.6);border-radius:50px}}
    .pc1{{width:130px;height:40px;bottom:55px;left:15%;animation:cfloat 7s ease-in-out infinite}}
    .pc2{{width:100px;height:35px;bottom:70px;right:20%;animation:cfloat 9s ease-in-out infinite reverse}}
    .pc1::before{{content:'';position:absolute;width:60px;height:55px;background:rgba(255,183,77,.6);border-radius:50%;top:-25px;left:20px}}
    .pc2::before{{content:'';position:absolute;width:50px;height:45px;background:rgba(255,183,77,.6);border-radius:50%;top:-20px;left:15px}}
    .ptitle{{position:absolute;bottom:15px;left:50%;transform:translateX(-50%);color:#fff9c4;font-size:1.4rem;font-weight:800;letter-spacing:.12em;text-shadow:0 0 15px #ff8f00,0 0 30px rgba(255,143,0,.6);white-space:nowrap}}
  </style>
  <div class="psun"></div><div class="pcl pc1"></div><div class="pcl pc2"></div>
  <div class="ptitle">📷 РЕЖИМ ФОТОГРАФА</div>
</div>"""


def drone_banner():
    return """<div style="position:relative;width:100%;height:130px;background:linear-gradient(180deg,#0277bd,#29b6f6 50%,#e1f5fe);border-radius:16px;overflow:hidden;margin-bottom:20px">
  <style>
    @keyframes dfloat{{0%,100%{{transform:translateX(0) translateY(0) rotate(0deg)}}25%{{transform:translateX(20px) translateY(-8px) rotate(2deg)}}75%{{transform:translateX(-15px) translateY(5px) rotate(-2deg)}}}}
    @keyframes propel{{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}}
    .drone-body{{position:absolute;top:35px;left:50%;transform:translateX(-50%);font-size:3rem;animation:dfloat 3s ease-in-out infinite}}
    .dtitle{{position:absolute;bottom:12px;left:50%;transform:translateX(-50%);color:#0d47a1;font-size:1.3rem;font-weight:800;letter-spacing:.12em;white-space:nowrap}}
  </style>
  <div class="drone-body">🚁</div>
  <div class="dtitle">🚁 РЕЖИМ ДРОН / FPV</div>
</div>"""


def garden_banner():
    return """<div style="position:relative;width:100%;height:130px;background:linear-gradient(180deg,#1b5e20,#388e3c 50%,#a5d6a7);border-radius:16px;overflow:hidden;margin-bottom:20px">
  <style>
    @keyframes sway{{0%,100%{{transform:rotate(-3deg)}}50%{{transform:rotate(3deg)}}}}
    .gplant{{position:absolute;font-size:2.5rem;bottom:15px;animation:sway 2s ease-in-out infinite}}
    .gp1{{left:15%}}.gp2{{left:35%;animation-delay:.4s}}.gp3{{left:55%;animation-delay:.8s}}.gp4{{right:10%;animation-delay:1.2s}}
    .gtitle{{position:absolute;top:20px;left:50%;transform:translateX(-50%);color:#f1f8e9;font-size:1.3rem;font-weight:800;letter-spacing:.1em;white-space:nowrap;text-shadow:0 2px 4px rgba(0,0,0,.3)}}
  </style>
  <div class="gplant gp1">🌱</div><div class="gplant gp2">🌿</div><div class="gplant gp3">🌻</div><div class="gplant gp4">🌾</div>
  <div class="gtitle">🌱 РЕЖИМ ОГОРОДНИКА</div>
</div>"""


# ═══════════════════════════════════════════════════════════════
# ГРАФИКИ PLOTLY
# ═══════════════════════════════════════════════════════════════

def base_layout(title, t, h=240):
    return dict(
        title=dict(text=title,font=dict(color=t["text"],size=14)),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=t["text2"]),
        xaxis=dict(gridcolor=t["border"],showgrid=True),
        yaxis=dict(gridcolor=t["border"],showgrid=True),
        margin=dict(l=40,r=20,t=40,b=40),height=h,
        legend=dict(font=dict(color=t["text2"]),bgcolor="rgba(0,0,0,0)"),
    )


def chart_temperature(hourly, t, yr_data=None):
    times=pd.to_datetime(hourly["time"]); mask=times<=times[0]+pd.Timedelta(days=5)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=times[mask],y=np.array(hourly["temperature_2m"])[mask],
        fill="tozeroy",line=dict(color=t["accent"],width=2),fillcolor=hex_to_rgba(t["accent"],.15),name="Темп. °C"))
    fig.add_trace(go.Scatter(x=times[mask],y=np.array(hourly["apparent_temperature"])[mask],
        line=dict(color=t["accent2"],width=1.5,dash="dot"),name="Ощущается"))
    if yr_data:
        yt=pd.to_datetime(yr_data["times"]); ym=yt<=yt[0]+pd.Timedelta(days=5)
        ya=np.array([v if v is not None else np.nan for v in yr_data["temp"]])
        fig.add_trace(go.Scatter(x=yt[ym],y=ya[ym],line=dict(color="#ff7043",width=1.5,dash="dash"),name="Yr.no °C"))
    fig.update_layout(**base_layout("🌡 Температура (°C)",t)); return fig


def chart_humidity(hourly, t, yr_data=None):
    times=pd.to_datetime(hourly["time"]); mask=times<=times[0]+pd.Timedelta(days=5)
    fig=go.Figure(go.Bar(x=times[mask],y=np.array(hourly["relativehumidity_2m"])[mask],
        marker_color=hex_to_rgba(t["accent2"],.75),name="Влажность %"))
    if yr_data:
        yt=pd.to_datetime(yr_data["times"]); ym=yt<=yt[0]+pd.Timedelta(days=5)
        ya=np.array([v if v is not None else np.nan for v in yr_data["humidity"]])
        fig.add_trace(go.Scatter(x=yt[ym],y=ya[ym],line=dict(color="#ff7043",width=1.5,dash="dash"),name="Yr.no %"))
    fig.update_layout(**base_layout("💧 Влажность (%)",t)); return fig


def chart_pressure(hourly, t, yr_data=None):
    times=pd.to_datetime(hourly["time"]); mask=times<=times[0]+pd.Timedelta(days=5)
    fig=go.Figure(go.Scatter(x=times[mask],y=np.array(hourly["surface_pressure"])[mask],
        line=dict(color="#ff7043",width=2),fill="tozeroy",fillcolor="rgba(255,112,67,.15)",name="гПа"))
    if yr_data:
        yt=pd.to_datetime(yr_data["times"]); ym=yt<=yt[0]+pd.Timedelta(days=5)
        ya=np.array([v if v is not None else np.nan for v in yr_data["pressure"]])
        fig.add_trace(go.Scatter(x=yt[ym],y=ya[ym],line=dict(color="#ab47bc",width=1.5,dash="dash"),name="Yr.no гПа"))
    fig.update_layout(**base_layout("🌀 Давление (гПа)",t)); return fig


def chart_wind(hourly, t, yr_data=None):
    times=pd.to_datetime(hourly["time"]); mask=times<=times[0]+pd.Timedelta(days=5)
    fig=go.Figure(go.Scatter(x=times[mask],y=np.array(hourly["windspeed_10m"])[mask],
        line=dict(color="#ab47bc",width=2),fill="tozeroy",fillcolor="rgba(171,71,188,.15)",name="м/с"))
    gusts=hourly.get("windgusts_10m")
    if gusts:
        fig.add_trace(go.Scatter(x=times[mask],y=np.array(gusts)[mask],
            line=dict(color="#e53935",width=1,dash="dot"),name="Порывы м/с"))
    if yr_data:
        yt=pd.to_datetime(yr_data["times"]); ym=yt<=yt[0]+pd.Timedelta(days=5)
        ya=np.array([v if v is not None else np.nan for v in yr_data["wind_speed"]])
        fig.add_trace(go.Scatter(x=yt[ym],y=ya[ym],line=dict(color="#ff7043",width=1.5,dash="dash"),name="Yr.no м/с"))
    fig.update_layout(**base_layout("💨 Ветер (м/с)",t)); return fig


def chart_precipitation(hourly, t):
    times=pd.to_datetime(hourly["time"]); mask=times<=times[0]+pd.Timedelta(days=5)
    fig=go.Figure()
    prec=np.array(hourly.get("precipitation",[0]*300))[mask]
    prob=np.array(hourly.get("precipitation_probability",[0]*300))[mask]
    fig.add_trace(go.Bar(x=times[mask],y=prec,name="Осадки мм",marker_color="rgba(33,150,243,.7)"))
    fig.add_trace(go.Scatter(x=times[mask],y=prob,name="Вероятность %",
        line=dict(color="#ff7043",width=2),yaxis="y2"))
    lo=base_layout("🌧 Осадки (мм) / Вероятность (%)",t)
    lo["yaxis2"]=dict(overlaying="y",side="right",gridcolor=t["border"],showgrid=False,
                      title="Вероятность %",range=[0,100],tickfont=dict(color=t["text2"]))
    fig.update_layout(**lo); return fig


def chart_heatmap(hourly, t):
    times=pd.to_datetime(hourly["time"])
    mask=times<times[0]+pd.Timedelta(days=7)
    df=pd.DataFrame({"dt":times[mask],"temp":np.array(hourly["temperature_2m"])[mask]})
    df["day"]=df["dt"].dt.strftime("%d.%m")
    df["hour"]=df["dt"].dt.hour
    pivot=df.pivot_table(index="hour",columns="day",values="temp",aggfunc="mean")
    fig=go.Figure(go.Heatmap(z=pivot.values,x=pivot.columns,y=pivot.index,
        colorscale="RdYlBu_r",reversescale=False,
        colorbar=dict(title="°C",tickfont=dict(color=t["text2"]))))
    lo=base_layout("🌡 Тепловая карта температур (°C)",t,280)
    lo["yaxis"]["title"]="Час"; lo["xaxis"]["title"]="Дата"
    fig.update_layout(**lo); return fig


def chart_wind_rose(hourly, t):
    mask=pd.to_datetime(hourly["time"])<=pd.to_datetime(hourly["time"])[0]+pd.Timedelta(days=5)
    dirs=np.array(hourly.get("winddirection_10m",[]))[mask]
    spds=np.array(hourly.get("windspeed_10m",[]))[mask]
    dirs=[d for d in dirs if d is not None]
    spds=[s for s in spds if s is not None]
    bins=np.arange(-22.5,360+22.5,45)
    dnames=["С","СВ","В","ЮВ","Ю","ЮЗ","З","СЗ"]
    freq=[0.0]*8; wspeed=[0.0]*8
    for d,s in zip(dirs,spds):
        idx=int((d+22.5)%360//45)%8
        freq[idx]+=1; wspeed[idx]+=s
    total=max(sum(freq),1)
    freq_pct=[f/total*100 for f in freq]
    avg_spd=[wspeed[i]/max(freq[i],1) for i in range(8)]
    fig=go.Figure(go.Barpolar(
        r=freq_pct, theta=dnames,
        marker_color=avg_spd, marker_colorscale="Blues",
        marker_showscale=True,
        marker_colorbar=dict(title="м/с",tickfont=dict(color=t["text2"])),
        opacity=0.85, name="Частота %"
    ))
    fig.update_layout(
        title=dict(text="🌬 Роза ветров",font=dict(color=t["text"],size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(tickfont=dict(color=t["text2"]),gridcolor=t["border"]),
            angularaxis=dict(tickfont=dict(color=t["text2"]),gridcolor=t["border"])),
        margin=dict(l=40,r=40,t=50,b=40),height=300,
    ); return fig


def chart_sun_arc(sun_data, t):
    if not sun_data: return None
    alts=sun_data["alt"]; times=sun_data["times"]
    above=[a if a>=0 else 0 for a in alts]
    below=[a if a<0 else 0 for a in alts]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=times,y=above,fill="tozeroy",
        line=dict(color="#ffb300",width=2),fillcolor="rgba(255,179,0,.2)",name="Над горизонтом"))
    fig.add_trace(go.Scatter(x=times,y=below,fill="tozeroy",
        line=dict(color="#1565c0",width=1,dash="dot"),fillcolor="rgba(21,101,192,.1)",name="Под горизонтом"))
    fig.add_hline(y=0,line=dict(color=t["border"],width=1,dash="dash"))
    lo=base_layout("☀️ Дуга солнца — высота над горизонтом (°)",t,260)
    lo["xaxis"]["tickmode"]="array"
    lo["xaxis"]["tickvals"]=[times[i*4*3] for i in range(8)]
    lo["xaxis"]["ticktext"]=[times[i*4*3] for i in range(8)]
    fig.update_layout(**lo); return fig


def chart_skewt(skewt_data, t):
    levels=skewt_data["levels"]; temps=skewt_data["temps"]; dewpts=skewt_data["dewpts"]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=temps,y=levels,mode="lines+markers",
        line=dict(color="#e53935",width=2),name="Температура °C",
        marker=dict(size=8,color="#e53935")))
    fig.add_trace(go.Scatter(x=dewpts,y=levels,mode="lines+markers",
        line=dict(color="#1976d2",width=2,dash="dash"),name="Точка росы °C",
        marker=dict(size=8,color="#1976d2")))
    fig.add_trace(go.Scatter(
        x=temps+dewpts[::-1],
        y=levels+levels[::-1],
        fill="toself",fillcolor="rgba(255,152,0,.15)",
        line=dict(color="rgba(0,0,0,0)"),name="T–Td разрыв",showlegend=True))
    lo=base_layout("📡 Упрощённый Skew-T (T и Td по уровням давления)",t,320)
    lo["yaxis"]["autorange"]="reversed"; lo["yaxis"]["title"]="Давление (гПа)"
    lo["xaxis"]["title"]="Температура (°C)"
    fig.update_layout(**lo); return fig


def chart_hodograph(skewt_data, t):
    wspd=skewt_data["wspeeds"]; wdir=skewt_data["wdirs"]; levels=skewt_data["levels"]
    u=[-(s or 0)*math.sin(math.radians(d or 0)) for s,d in zip(wspd,wdir)]
    v=[-(s or 0)*math.cos(math.radians(d or 0)) for s,d in zip(wspd,wdir)]
    colors=["#e53935","#fb8c00","#43a047","#1976d2"]
    fig=go.Figure()
    for i in range(len(levels)-1):
        fig.add_trace(go.Scatter(x=u[i:i+2],y=v[i:i+2],mode="lines+markers",
            line=dict(color=colors[i],width=3),marker=dict(size=10,color=colors[i]),
            name=f"{levels[i]} гПа",showlegend=True))
    fig.add_hline(y=0,line=dict(color=t["border"],width=1))
    fig.add_vline(x=0,line=dict(color=t["border"],width=1))
    lo=base_layout("🌀 Hodograph — сдвиг ветра по высотам",t,300)
    lo["xaxis"]["title"]="U (м/с)"; lo["yaxis"]["title"]="V (м/с)"
    lo["xaxis"]["zeroline"]=False; lo["yaxis"]["zeroline"]=False
    fig.update_layout(**lo); return fig


def chart_pressure_temp_combo(hourly, t):
    times=pd.to_datetime(hourly["time"]); mask=times<=times[0]+pd.Timedelta(days=5)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=times[mask],y=np.array(hourly["surface_pressure"])[mask],
        line=dict(color="#ff7043",width=2),name="Давление гПа",yaxis="y1"))
    fig.add_trace(go.Scatter(x=times[mask],y=np.array(hourly["temperature_2m"])[mask],
        line=dict(color=t["accent"],width=2,dash="dash"),name="Температура °C",yaxis="y2"))
    lo=base_layout("📊 Давление (гПа) + Температура (°C)",t)
    lo["yaxis2"]=dict(overlaying="y",side="right",gridcolor=t["border"],showgrid=False,
                      tickfont=dict(color=t["text2"]),title="Температура °C")
    fig.update_layout(**lo); return fig


def chart_isotherms(t):
    lats=[v["lat"] for v in CITIES.values()]
    lons=[v["lon"] for v in CITIES.values()]
    names=list(CITIES.keys())
    fig=go.Figure(go.Scattergeo(
        lat=lats,lon=lons,text=names,mode="markers+text",
        marker=dict(size=12,color="rgba(88,166,255,.8)",
                    line=dict(color=t["border"],width=1)),
        textposition="top center",
        textfont=dict(color=t["text"],size=11),
    ))
    fig.update_layout(
        title=dict(text="🗺 Карта городов",font=dict(color=t["text"],size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)",
            showland=True,landcolor=t["card"],
            showocean=True,oceancolor=t["bg"],
            showcountries=True,countrycolor=t["border"],
            showcoastlines=True,coastlinecolor=t["border"],
            projection_type="natural earth",
            center=dict(lat=52,lon=40),projection_scale=3),
        margin=dict(l=0,r=0,t=40,b=0),height=380,
        font=dict(color=t["text2"]),
    ); return fig


def chart_photo_timeline(golden, t):
    if not golden: return None
    windows=[
        ("Ночь",        "00:00", golden.get("blue_morning",{}).get("start","05:00"),  "#1a237e"),
        ("Синий час 🔵", golden.get("blue_morning",{}).get("start","05:00"), golden.get("golden_morning",{}).get("start","06:00"), "#283593"),
        ("Золотой час 🌅", golden.get("golden_morning",{}).get("start","06:00"), golden.get("golden_morning",{}).get("end","07:00"), "#e65100"),
        ("День",         golden.get("golden_morning",{}).get("end","07:00"), golden.get("golden_evening",{}).get("start","19:00"), "#0277bd"),
        ("Золотой час 🌇", golden.get("golden_evening",{}).get("start","19:00"), golden.get("golden_evening",{}).get("end","20:00"), "#bf360c"),
        ("Синий час 🌃", golden.get("golden_evening",{}).get("end","20:00"), golden.get("blue_evening",{}).get("end","21:00"), "#1a237e"),
        ("Ночь",         golden.get("blue_evening",{}).get("end","21:00"), "24:00",    "#0d0d2e"),
    ]
    def to_min(s):
        try:
            h,m=map(int,s.split(":")); return h*60+m
        except: return 0

    fig=go.Figure()
    for name,start,end,color in windows:
        s=to_min(start); e=to_min(end)
        if e<=s: e=s+1
        fig.add_trace(go.Bar(x=[e-s],y=["День"],base=s,orientation="h",
            marker_color=color,name=name,
            hovertemplate=f"{name}: {start}–{end}<extra></extra>"))
    lo=base_layout("⏰ Фотографическое окно дня",t,130)
    lo["xaxis"]["range"]=[0,1440]; lo["xaxis"]["tickmode"]="array"
    lo["xaxis"]["tickvals"]=[i*60 for i in range(0,25,3)]
    lo["xaxis"]["ticktext"]=[f"{i:02d}:00" for i in range(0,25,3)]
    lo["barmode"]="stack"; lo["showlegend"]=True
    lo["legend"]=dict(orientation="h",y=-0.5,font=dict(color=t["text2"],size=10),bgcolor="rgba(0,0,0,0)")
    fig.update_layout(**lo); return fig


# ═══════════════════════════════════════════════════════════════
# ТЕМА CSS
# ═══════════════════════════════════════════════════════════════

def apply_theme(t):
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
  .best-day-card{{background:{t['card']};border:1px solid {t['border']};border-radius:10px;
    padding:14px;margin-bottom:8px;text-align:center}}
  .comfort-big{{font-size:1.8rem;font-weight:800;text-align:center;padding:18px;
    border-radius:14px;margin-bottom:16px}}
  label,.stSelectbox label,[data-testid="stWidgetLabel"]{{color:{t['text2']} !important}}
  hr{{border-color:{t['border']}}}
  [data-testid="stRadio"] label{{color:{t['text']} !important}}
  .stButton>button{{background:{hex_to_rgba(t['accent'],.13)};border:1px solid {hex_to_rgba(t['accent'],.4)};
    color:{t['text']};border-radius:8px}}
  .stButton>button:hover{{background:{hex_to_rgba(t['accent'],.27)}}}
  .block-container{{padding-top:1.5rem !important}}
  .stTextArea textarea{{background:{t['card']};color:{t['text']};border-color:{t['border']}}}
  .stExpander{{background:{t['card']};border-color:{t['border']}}}
</style>""", unsafe_allow_html=True)


# ─── UI-хелперы ───────────────────────────────────────────────

def mc(label, value, sub="", color=None):
    val_style = f"color:{color}" if color else ""
    return f"""<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value" style="{val_style}">{value}</div>
  <div class="metric-sub">{sub}</div>
</div>"""


def mc_accent(label, value, sub="", accent_color="#58a6ff", border=True):
    border_style = f"border-left:3px solid {accent_color}" if border else ""
    return f"""<div class="metric-card" style="{border_style}">
  <div class="metric-label">{label}</div>
  <div class="metric-value" style="color:{accent_color}">{value}</div>
  <div class="metric-sub">{sub}</div>
</div>"""


def render_news(news_list, t, cols=3):
    columns=st.columns(cols)
    for i,item in enumerate(news_list):
        with columns[i%cols]:
            st.markdown(f"""<a href="{item['url']}" target="_blank" class="news-card">
  <div class="news-card-title">{item['icon']} {item['title']}</div>
  <div class="news-card-sub">{item['url'].split('/')[2]}</div>
</a>""", unsafe_allow_html=True)


def section(title):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# MAIN — ОСНОВНАЯ ФУНКЦИЯ ПРИЛОЖЕНИЯ
# ═══════════════════════════════════════════════════════════════

def main():
    st.set_page_config(page_title="🌦 Погода v3", page_icon="🌦", layout="wide", initial_sidebar_state="expanded")

    # ── Сайдбар ──────────────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ Настройки")
        city_name = st.selectbox("🏙 Город", list(CITIES.keys()), index=0)
        city = CITIES[city_name]
        theme_name = st.radio("🎨 Тема", list(THEMES.keys()), index=0)
        t = THEMES[theme_name]
        st.markdown("---")
        st.markdown("### 📡 Источники данных")
        use_yr = st.checkbox("🇳🇴 Сравнить с Yr.no (MET Norway)", value=False)
        use_metar = st.checkbox("🛩 METAR/TAF (авиация)", value=False)
        st.markdown("---")
        st.markdown("### 🧭 Режимы")
        astro_mode = st.toggle("🔭 Астрономия", value=False)
        garden_mode = st.toggle("🌱 Огородник", value=False)
        drone_mode = st.toggle("🚁 Дрон / FPV", value=False)
        photo_mode = st.toggle("📷 Фотограф", value=False)
        st.markdown("---")
        st.markdown(f"<span style='color:{t['text2']};font-size:.78rem'>📍 {city['lat']:.4f}°N {city['lon']:.4f}°E</span>", unsafe_allow_html=True)
        if not EPHEM_OK:
            st.warning("Установите ephem для планет и сумерек:\npip install ephem")

    apply_theme(t)

    # ── Загрузка данных ─────────────────────────────
    with st.spinner("Загружаю данные..."):
        data = fetch_openmeteo(city["lat"], city["lon"])
        marine = fetch_marine(city["lat"], city["lon"])
        airquality = fetch_airquality(city["lat"], city["lon"])
        climate_norm = fetch_climate_norm(city["lat"], city["lon"])
        yr_data = fetch_yr(city["lat"], city["lon"]) if use_yr else None
        metar = fetch_metar(city["metar"]) if use_metar and city.get("metar") else None
        taf = fetch_taf(city["metar"]) if use_metar and city.get("metar") else None

    if not data:
        st.error("Нет данных от Open-Meteo. Проверьте соединение.")
        return

    cw = data["current_weather"]
    hourly = data["hourly"]
    daily = data["daily"]

    now_str = cw["time"]
    try:
        ni = hourly["time"].index(now_str)
    except ValueError:
        ni = 0

    def h(key):
        v = hourly.get(key, [None] * (ni + 1))
        return v[ni] if v else None

    temp = cw.get("temperature", h("temperature_2m")) or 0
    feelslike = h("apparent_temperature") or temp
    humidity = h("relativehumidity_2m") or 0
    pressure = h("surface_pressure") or 1013
    wind_speed = cw.get("windspeed", h("windspeed_10m")) or 0
    wind_gusts = h("windgusts_10m") or 0
    wind_dir = cw.get("winddirection", h("winddirection_10m")) or 0
    cloudcover = h("cloudcover") or 0
    visibility = (h("visibility") or 10000) / 1000
    uv_index = h("uv_index") or 0
    precip_prob = h("precipitation_probability") or 0
    cape = h("cape") or 0
    lightning = h("lightning_potential") or 0
    wmo_code = int(cw.get("weathercode", 0))

    # Морские данные
    marine_now = {}
    if marine and marine.get("hourly"):
        mh = marine["hourly"]
        try:
            mi = mh["time"].index(now_str)
        except ValueError:
            mi = 0
        def mg(k): return (mh.get(k) or [None])[mi]
        marine_now = {
            "wave_height": mg("wave_height"),
            "wave_dir": mg("wave_direction"),
            "wave_period": mg("wave_period"),
            "sst": mg("sea_surface_temperature")
        }

    # Air Quality
    aqi_now = None
    if airquality and airquality.get("hourly"):
        aqh = airquality["hourly"]
        try:
            ai = aqh["time"].index(now_str)
            aqi_now = aqh.get("european_aqi", [None])[ai]
        except:
            pass

    # Skew-T
    skewt_data = build_skewt(hourly, ni)

    # Солнечная дуга
    sun_arc = calc_sun_arc(city["lat"], city["lon"], datetime.now()) if EPHEM_OK else None

    # Золотой/синий час
    golden_blue = calc_golden_blue(city["lat"], city["lon"], datetime.now()) if EPHEM_OK else None

    # Индексы
    storm = storm_index(cape, lightning, humidity)
    walk_score, walk_verdict, walk_color = walk_comfort(temp, feelslike, wind_speed, humidity, precip_prob, wmo_code)
    best = best_days(daily, hourly) if daily else {}

    # Восход/закат
    def parse_dt(s):
        try:
            return datetime.fromisoformat(s)
        except:
            return None
    sunrise_dt = parse_dt(daily.get("sunrise", [None])[0])
    sunset_dt = parse_dt(daily.get("sunset", [None])[0])
    now_dt = datetime.now()
    time_to_sunset = ""
    if sunset_dt:
        diff = sunset_dt - now_dt
        if diff.total_seconds() > 0:
            time_to_sunset = f"{int(diff.total_seconds()//3600)}ч {int(diff.total_seconds()%3600//60)}мин"

    # ── АНИМАЦИЯ ─────────────────────────────
    if astro_mode:
        st.markdown(astro_banner(), unsafe_allow_html=True)
    elif photo_mode:
        st.markdown(photo_banner(), unsafe_allow_html=True)
    elif drone_mode:
        st.markdown(drone_banner(), unsafe_allow_html=True)
    elif garden_mode:
        st.markdown(garden_banner(), unsafe_allow_html=True)
    else:
        st.markdown(get_weather_animation(wmo_code, t), unsafe_allow_html=True)

    # ── ЗАГОЛОВОК ────────────────────────────
    c1, c2 = st.columns([3, 1])
    with c1:
        yr_b = '<span class="yr-badge">+ Yr.no</span>' if use_yr else ""
        metar_b = '<span class="yr-badge" style="background:#0288d1">+ METAR</span>' if use_metar else ""
        st.markdown(f"""
        <div>
            <div class="city-header">{city_name} {yr_b}{metar_b}</div>
            <div class="city-sub">{wmo_desc(wmo_code)} · {now_str[:16].replace('T', ' ')}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="text-align:right;padding-top:4px">
            <div style="font-size:3rem;font-weight:900;color:{t['text']};line-height:1">{temp:.1f}°C</div>
            <div style="color:{t['text2']};font-size:.88rem">Ощущается {feelslike:.1f}°C</div>
        </div>
        """, unsafe_allow_html=True)

    # Yr.no сравнение
    if use_yr and yr_data:
        yc_t = next((v for v in yr_data["temp"] if v is not None), None)
        if yc_t is not None:
            diff_t = yc_t - temp
            agree = abs(diff_t) <= 2
            st.markdown(f"""
            <div class="metric-card" style="border-left:3px solid #ff7043;margin-top:6px">
                <div class="metric-label">🇳🇴 Yr.no — независимый прогноз (MET Norway)</div>
                <div style="display:flex;gap:20px;flex-wrap:wrap;margin-top:6px">
                    <span style="color:{t['text']}">🌡 <b>{yc_t:.1f}°C</b>
                        <span style="color:{'#43a047' if agree else '#e53935'};font-size:.8rem">
                            ({'+' if diff_t >= 0 else ''}{diff_t:.1f}°)
                        </span>
                    </span>
                </div>
                <div style="font-size:.72rem;color:{t['text2']};margin-top:4px">
                    {'✅ Прогнозы совпадают' if agree else '⚠️ Расхождение температур: ' + f"{abs(diff_t):.1f}°C"}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── РЕЖИМ АСТРОНОМИЯ ─────────────────────────────
    if astro_mode:
        section("🔭 Режим Астрономия")
        doy = now_dt.timetuple().tm_yday
        month = now_dt.month
        clarity = sky_clarity(cloudcover, humidity)
        moon_text, moon_frac = moon_phase(doy)
        astro = astro_score(clarity, moon_frac, visibility)
        consts = visible_constellations(city["lat"], month)
        twilights = calc_twilights(city["lat"], city["lon"], now_dt)

        a1, a2, a3 = st.columns(3)
        with a1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Чистота неба</div>
                <div class="metric-value" style="color:{t['accent']}">{clarity}%</div>
                <div class="metric-sub">Облачность {cloudcover:.0f}%, влажность {humidity:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with a2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Фаза луны</div>
                <div class="metric-value">{moon_text}</div>
                <div class="metric-sub">Яркость {moon_frac * 100:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with a3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Условия для астрофото</div>
                <div class="metric-value" style="color:{astro['color']}">{astro['verdict']}</div>
                <div class="metric-sub">Оценка {astro['score']}/100</div>
            </div>
            """, unsafe_allow_html=True)

        # Сумерки
        section("🌅 Астрономические сумерки")
        t1, t2, t3 = st.columns(3)
        for col, label, key, color in [
            (t1, "Гражданские (-6°)", "civil", "#fb8c00"),
            (t2, "Навигационные (-12°)", "nautical", "#7b1fa2"),
            (t3, "Астрономические (-18°)", "astronomical", "#1565c0"),
        ]:
            tw = twilights.get(key, {})
            with col:
                st.markdown(f"""
                <div class="metric-card" style="border-left:3px solid {color}">
                    <div class="metric-label">{label}</div>
                    <div style="color:{t['text']};font-size:.95rem;margin-top:6px">
                        🌆 Вечер: <b>{tw.get('evening', '—')}</b><br>
                        🌄 Утро: <b>{tw.get('morning', '—')}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Лучшее время
        if sunset_dt and sunrise_dt:
            bs = sunset_dt + timedelta(hours=1, minutes=30)
            be = sunrise_dt + timedelta(days=1) - timedelta(hours=1)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⏰ Идеальное время наблюдений</div>
                <div class="metric-value" style="font-size:1.1rem;color:{t['accent']}">{bs.strftime('%H:%M')} — {be.strftime('%H:%M')}</div>
                <div class="metric-sub">После гражданских сумерек до рассвета</div>
            </div>
            """, unsafe_allow_html=True)

        # Созвездия
        section("🌌 Видимые созвездия")
        cc = st.columns(3)
        for i, c in enumerate(consts[:6]):
            with cc[i % 3]:
                st.markdown(f"""
                <div class="metric-card" style="padding:10px 14px">
                    <div style="font-size:.95rem;color:{t['text']}">{c}</div>
                </div>
                """, unsafe_allow_html=True)

        # Планеты
        if EPHEM_OK:
            section("🪐 Планеты сегодня")
            planets = get_planets(city["lat"], city["lon"])
            pcols = st.columns(4)
            for i, p in enumerate(planets):
                vc = "#43a047" if p["visible"] else t["border"]
                with pcols[i % 4]:
                    st.markdown(f"""
                    <div class="planet-card" style="border-color:{vc}">
                        <div style="font-size:.95rem;font-weight:700;color:{t['text']}">{p['name']}</div>
                        <div style="font-size:.72rem;color:{t['text2']};margin-top:5px;line-height:1.6">
                            {'🟢 Видима' if p['visible'] else '🔴 Под горизонтом'}<br>
                            Высота: <b>{p['alt']}°</b> · Азимут: <b>{p['az']}°</b><br>
                            RA: {p['ra']} · Dec: {p['dec']}<br>
                            Зв. величина: {p['mag']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Stellarium
        section("🌠 Карта звёздного неба — Stellarium Web")
        stell_url = f"https://stellarium-web.org/?lat={city['lat']}&lng={city['lon']}&date={now_dt.strftime('%Y-%m-%d')}"
        st.markdown(f"""
        <iframe src="{stell_url}" width="100%" height="560" style="border:none;border-radius:14px" loading="lazy"></iframe>
        <p style="color:{t['text2']};font-size:.75rem;margin-top:5px">
            🔭 stellarium-web.org · <a href="{stell_url}" target="_blank" style="color:{t['accent']}">Открыть полноэкранно</a>
        </p>
        """, unsafe_allow_html=True)

        # Новости астро
        section("📰 Астро новости")
        render_news(ASTRO_NEWS, t, cols=3)

        st.markdown("---")

    # ── РЕЖИМ ОГОРОДНИК ─────────────────────────────
    if garden_mode:
        section("🌱 Режим Огородника")
        garden = garden_forecast(daily, hourly)
        cols = st.columns(7)
        for i, g in enumerate(garden[:7]):
            with cols[i]:
                frost_icon = "❄️" if g["frost"] else "✅"
                water_icon = "💧" if g["watering"] else "☀️"
                work_icon = "🟢" if g["workable"] else "🔴"
                st.markdown(f"""
                <div class="metric-card" style="text-align:center;padding:10px 6px">
                    <div style="font-weight:700">{g['label']}</div>
                    <div>{frost_icon} {water_icon} {work_icon}</div>
                    <div style="font-size:.8rem">{g['tmin']:.0f}°…{g['tmax']:.0f}°</div>
                    <div style="font-size:.7rem">💧{g['prec']:.1f}мм</div>
                    <div style="font-size:.7rem">{'❄️ Заморозки!' if g['frost'] else '🌱 Можно работать' if g['workable'] else '⛔ Не работать'}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── РЕЖИМ ДРОН ─────────────────────────────
    if drone_mode:
        section("🚁 Режим Дрон / FPV")
        drone = drone_conditions(wind_speed, wind_gusts, visibility, precip_prob, wmo_code, temp)
        st.markdown(f"""
        <div class="comfort-big" style="background:{drone['color']}20;border:1px solid {drone['color']}">
            <span style="font-size:2rem">{drone['verdict']}</span><br>
            <span style="font-size:1.2rem">Безопасность полётов: {drone['score']}%</span>
        </div>
        """, unsafe_allow_html=True)
        if drone['issues']:
            st.warning("\n".join(drone['issues']))

    # ── РЕЖИМ ФОТОГРАФ ─────────────────────────────
    if photo_mode:
        section("📷 Режим Фотографа")
        # Золотой/синий час
        if golden_blue:
            st.markdown("### 🌅 Золотой и синий час")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🌅 Утренний золотой час: {golden_blue.get('golden_morning', {}).get('start', '—')} — {golden_blue.get('golden_morning', {}).get('end', '—')}")
                st.info(f"🌃 Утренний синий час: {golden_blue.get('blue_morning', {}).get('start', '—')} — {golden_blue.get('blue_morning', {}).get('end', '—')}")
            with col2:
                st.info(f"🌇 Вечерний золотой час: {golden_blue.get('golden_evening', {}).get('start', '—')} — {golden_blue.get('golden_evening', {}).get('end', '—')}")
                st.info(f"🌌 Вечерний синий час: {golden_blue.get('blue_evening', {}).get('start', '—')} — {golden_blue.get('blue_evening', {}).get('end', '—')}")

        # Таймлайн
        tl = chart_photo_timeline(golden_blue, t)
        if tl:
            st.plotly_chart(tl, use_container_width=True, config={"displayModeBar": False})

        # Условия съёмки
        photo_sky, photo_color = photo_conditions(cloudcover, humidity, wmo_code, visibility)
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid {photo_color}">
            <div class="metric-label">📸 Условия для съёмки</div>
            <div class="metric-value" style="font-size:1.2rem;color:{photo_color}">{photo_sky}</div>
        </div>
        """, unsafe_allow_html=True)

        # Риск для оборудования
        gear_risk, gear_color, gear_issues = photo_gear_risk(temp, humidity, precip_prob, wmo_code, wind_speed, feelslike)
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid {gear_color}">
            <div class="metric-label">🛡 Риск для оборудования</div>
            <div class="metric-value" style="font-size:1.1rem;color:{gear_color}">{gear_risk}</div>
        </div>
        """, unsafe_allow_html=True)
        if gear_issues:
            for issue in gear_issues[:3]:
                st.caption(issue)

        # Дуга солнца
        if sun_arc:
            section("☀️ Дуга солнца сегодня")
            fig_sun = chart_sun_arc(sun_arc, t)
            if fig_sun:
                st.plotly_chart(fig_sun, use_container_width=True, config={"displayModeBar": False})

    # ── ТЕКУЩИЕ УСЛОВИЯ ─────────────────────────────
    section("📊 Текущие условия")

    m1, m2, m3, m4 = st.columns(4)
    for col, label, val, sub in [
        (m1, "💧 Влажность", f"{humidity:.0f}%", ""),
        (m2, "🌀 Давление", f"{pressure:.0f} гПа", ""),
        (m3, "☀️ УФ-индекс", f"{uv_index:.1f}", ""),
        (m4, "👁 Видимость", f"{visibility:.1f} км", ""),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    m5, m6, m7, m8 = st.columns(4)
    for col, label, val, sub in [
        (m5, "💨 Ветер", f"{wind_speed:.1f} м/с", f"{wind_dir_text(wind_dir)} ({wind_dir:.0f}°)"),
        (m6, "🌧 Вер. осадков", f"{precip_prob:.0f}%", ""),
        (m7, "🌅 Восход", sunrise_dt.strftime('%H:%M') if sunrise_dt else "—", ""),
        (m8, "🌇 Закат", sunset_dt.strftime('%H:%M') if sunset_dt else "—", f"Через {time_to_sunset}" if time_to_sunset else ""),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    # Морские данные
    if marine_now and any(v is not None for v in marine_now.values()):
        section("🌊 Морские условия (Open-Meteo Marine)")
        sc = st.columns(4)
        for col, label, key, fmt in [
            (sc[0], "🌊 Высота волн", "wave_height", lambda v: f"{v:.1f} м"),
            (sc[1], "🧭 Направ. волн", "wave_dir", lambda v: f"{v:.0f}° {wind_dir_text(v)}"),
            (sc[2], "⏱ Период волн", "wave_period", lambda v: f"{v:.1f} с"),
            (sc[3], "🌡 Темп. воды", "sst", lambda v: f"{v:.1f}°C"),
        ]:
            v = marine_now.get(key)
            with col:
                st.markdown(f"""
                <div class="metric-card" style="border-left:3px solid #0288d1">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{fmt(v) if v is not None else '—'}</div>
                </div>
                """, unsafe_allow_html=True)

    # Качество воздуха
    if aqi_now is not None:
        aqi_text, aqi_color = aqi_level(aqi_now)
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid {aqi_color}">
            <div class="metric-label">🌫 Качество воздуха (AQI)</div>
            <div class="metric-value" style="color:{aqi_color}">{aqi_text}</div>
            <div class="metric-sub">Индекс: {aqi_now}</div>
        </div>
        """, unsafe_allow_html=True)

    # Грозовой индекс
    section("⚡ Грозовой индекс")
    gi1, gi2 = st.columns([2, 1])
    with gi1:
        st.markdown(f"""
        <div class="metric-card">
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
        </div>
        """, unsafe_allow_html=True)
    with gi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">☁️ Облачность</div>
            <div class="metric-value">{cloudcover:.0f}%</div>
            <div class="metric-sub">{wmo_desc(wmo_code)}</div>
        </div>
        """, unsafe_allow_html=True)

    # Индекс комфорта прогулки
    section("🚶 Индекс комфорта прогулки")
    st.markdown(f"""
    <div class="comfort-big" style="background:{walk_color}20;border:1px solid {walk_color}">
        <span style="font-size:2rem">{walk_verdict}</span><br>
        <span style="font-size:1.2rem">Комфортность: {walk_score}%</span>
    </div>
    """, unsafe_allow_html=True)

    # Повседневные советы
    section("🗓 Повседневные советы")
    advice = daily_advice(temp, feelslike, wind_speed, humidity, pressure, visibility, precip_prob, wmo_code, uv_index, cape)
    ac1, ac2 = st.columns(2)
    for i, adv in enumerate(advice):
        with (ac1 if i % 2 == 0 else ac2):
            st.markdown(f"""
            <div class="advice-card" style="border-left-color:{adv['color']}">
                <div style="font-size:.8rem;font-weight:700;color:{adv['color']};text-transform:uppercase;letter-spacing:.06em;margin-bottom:5px">{adv['title']}</div>
                <div style="font-size:.92rem;color:{t['text']}">{adv['text']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Лучший день в неделе
    if best:
        section("📅 Лучший день для...")
        bcols = st.columns(5)
        for i, (cat, val) in enumerate(best.items()):
            with bcols[i % 5]:
                st.markdown(f"""
                <div class="best-day-card">
                    <div style="font-size:1.2rem">{cat}</div>
                    <div style="font-size:1.5rem;font-weight:700;color:{t['accent']}">{val['label']}</div>
                    <div style="font-size:.7rem">оценка {val['score']}</div>
                </div>
                """, unsafe_allow_html=True)

    # METAR/TAF
    if use_metar and metar:
        section("🛩 Авиационная метеосводка (METAR)")
        st.info(f"**{metar.get('stationId', city.get('metar', ''))}** {metar.get('rawOb', 'Нет данных')}")
    if use_metar and taf:
        section("📡 Авиационный прогноз (TAF)")
        st.info(f"**{taf.get('stationId', city.get('metar', ''))}** {taf.get('rawTaf', 'Нет данных')[:500]}")

    # ── ГРАФИКИ ─────────────────────────────
    section("📈 Прогноз на 5 дней")
    if use_yr and yr_data:
        st.caption("— Open-Meteo   ╌ Yr.no (пунктир)")

    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(chart_temperature(hourly, t, yr_data if use_yr else None), use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(chart_pressure(hourly, t, yr_data if use_yr else None), use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(chart_precipitation(hourly, t), use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(chart_heatmap(hourly, t), use_container_width=True, config={"displayModeBar": False})
        if not photo_mode:
            st.plotly_chart(chart_wind_rose(hourly, t), use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(chart_skewt(skewt_data, t), use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(chart_hodograph(skewt_data, t), use_container_width=True, config={"displayModeBar": False})
    with ch2:
        st.plotly_chart(chart_humidity(hourly, t, yr_data if use_yr else None), use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(chart_wind(hourly, t, yr_data if use_yr else None), use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(chart_pressure_temp_combo(hourly, t), use_container_width=True, config={"displayModeBar": False})
        if not photo_mode and sun_arc:
            st.plotly_chart(chart_sun_arc(sun_arc, t), use_container_width=True, config={"displayModeBar": False})

    # Суточный прогноз
    section("📅 Прогноз по дням")
    dcols = st.columns(7)
    for i in range(min(7, len(daily.get("time", [])))):
        with dcols[i]:
            dd = daily["time"][i]
            dw = daily["weathercode"][i]
            dm = daily["temperature_2m_max"][i]
            dn = daily["temperature_2m_min"][i]
            dr = daily["precipitation_probability_max"][i]
            lbl = "Сег." if i == 0 else ("Завт." if i == 1 else datetime.fromisoformat(dd).strftime("%d.%m"))
            ico = wmo_icon(dw)
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;padding:10px 6px">
                <div style="font-size:.75rem;color:{t['text2']};font-weight:600">{lbl}</div>
                <div style="font-size:1.3rem;margin:4px 0">{ico}</div>
                <div style="font-size:.9rem;font-weight:700;color:{t['text']}">{dm:.0f}°</div>
                <div style="font-size:.8rem;color:{t['text2']}">{dn:.0f}°</div>
                <div style="font-size:.72rem;color:{t['accent']}">💧{dr:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

    # Метео новости
    section("📰 Метео новости")
    render_news(METEO_NEWS, t, cols=3)

    # ── РАДАРЫ ─────────────────────────────
    section("🗺 Радар и грозопеленгация")
    if "radar_key" not in st.session_state:
        st.session_state.radar_key = 0
    if st.button("🔄 Обновить радары"):
        st.session_state.radar_key += 1

    lat_r, lon_r = city["lat"], city["lon"]

    st.markdown("**⚡ Blitzortung — молниедетектор реального времени**")
    blitz = f"https://www.blitzortung.org/en/live_lightning_maps.php?map=11&lat={lat_r}&lon={lon_r}"
    st.markdown(f"""
    <iframe src="{blitz}" width="100%" height="500" style="border:none;border-radius:12px" loading="lazy"></iframe>
    <p style="color:{t['text2']};font-size:.75rem;margin-top:4px">🔴 blitzortung.org · {lat_r:.2f}°N, {lon_r:.2f}°E</p>
    """, unsafe_allow_html=True)

    st.markdown("**🌧 МетеоЛогикс — радар осадков**")
    mlogix = f"https://meteologix.com/ru/radar/europe-precipitation.html#{lat_r},{lon_r},7"
    st.markdown(f"""
    <iframe src="{mlogix}" width="100%" height="500" style="border:none;border-radius:12px" loading="lazy"></iframe>
    <p style="color:{t['text2']};font-size:.75rem;margin-top:4px">
        🌧 meteologix.com · <a href="https://meteologix.com/ru/radar/" target="_blank" style="color:{t['accent']}">Открыть в новой вкладке</a>
    </p>
    """, unsafe_allow_html=True)

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
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()