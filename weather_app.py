"""
Погода · Астрономия — Streamlit
Запуск:  streamlit run weather_app.py
Зависимости: см. requirements.txt (streamlit pandas numpy plotly requests ephem tzdata)

Необязательные ключи (st.secrets или переменные окружения):
  OWM_KEY      — OpenWeatherMap (доп. источник для сверки)
  WEATHERAPI_KEY — weatherapi.com (доп. источник для сверки)
  NASA_KEY     — api.nasa.gov (APOD; без ключа используется DEMO_KEY)
"""
import os, math, json
from datetime import datetime, timedelta, date, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

try:
    import ephem
    EPHEM_OK = True
except ImportError:
    EPHEM_OK = False

# ════════════════════════════════════════════════════════════════
# ГОРОДА  (название | широта | долгота)  — страны СНГ + Балтия + обсерватории
# ════════════════════════════════════════════════════════════════
_RAW = {
"Россия": """Москва|55.7558|37.6173
Санкт-Петербург|59.9343|30.3351
Новосибирск|55.0084|82.9357
Екатеринбург|56.8389|60.6057
Казань|55.7887|49.1221
Нижний Новгород|56.2965|43.9361
Челябинск|55.1644|61.4368
Самара|53.1959|50.1002
Омск|54.9885|73.3242
Ростов-на-Дону|47.2357|39.7015
Уфа|54.7388|55.9721
Красноярск|56.0153|92.8932
Воронеж|51.6720|39.1843
Пермь|58.0105|56.2502
Волгоград|48.7080|44.5133
Краснодар|45.0355|38.9753
Саратов|51.5336|46.0343
Тюмень|57.1522|65.5272
Тольятти|53.5078|49.4204
Ижевск|56.8527|53.2115
Барнаул|53.3548|83.7698
Ульяновск|54.3282|48.3866
Иркутск|52.2870|104.3050
Хабаровск|48.4802|135.0719
Ярославль|57.6261|39.8845
Владивосток|43.1155|131.8855
Махачкала|42.9849|47.5047
Томск|56.4846|84.9476
Оренбург|51.7682|55.0970
Кемерово|55.3547|86.0873
Новокузнецк|53.7596|87.1216
Рязань|54.6269|39.6916
Астрахань|46.3497|48.0408
Пенза|53.2007|45.0046
Липецк|52.6031|39.5708
Киров|58.6036|49.6680
Чебоксары|56.1322|47.2519
Тула|54.1961|37.6182
Калининград|54.7104|20.4522
Курск|51.7304|36.1926
Сочи|43.5855|39.7231
Ставрополь|45.0428|41.9734
Улан-Удэ|51.8335|107.5841
Тверь|56.8587|35.9176
Магнитогорск|53.4072|58.9792
Иваново|57.0004|40.9739
Брянск|53.2434|34.3640
Белгород|50.5997|36.5983
Сургут|61.2540|73.3962
Владимир|56.1290|40.4070
Чита|52.0340|113.4994
Архангельск|64.5401|40.5433
Мурманск|68.9585|33.0827
Калуга|54.5138|36.2612
Смоленск|54.7826|32.0453
Якутск|62.0355|129.6755
Петропавловск-Камчатский|53.0452|158.6483
Южно-Сахалинск|46.9591|142.7380
Петрозаводск|61.7849|34.3469
Сыктывкар|61.6688|50.8364
Вологда|59.2205|39.8915
Великий Новгород|58.5215|31.2755
Псков|57.8136|28.3496
Орёл|52.9703|36.0635
Тамбов|52.7212|41.4522
Кострома|57.7679|40.9269
Нальчик|43.4981|43.6189
Владикавказ|43.0241|44.6819
Грозный|43.3180|45.6949
Элиста|46.3078|44.2558
Йошкар-Ола|56.6344|47.8999
Саранск|54.1874|45.1839
Курган|55.4410|65.3411
Абакан|53.7156|91.4292
Горно-Алтайск|51.9581|85.9603
Норильск|69.3558|88.1893
Ханты-Мансийск|61.0042|69.0019
Салехард|66.5299|66.6019
Магадан|59.5638|150.8035
Благовещенск|50.2796|127.5405
Нижний Тагил|57.9101|59.9813
Подольск|55.4242|37.5547
Химки|55.8970|37.4297
Балашиха|55.7963|37.9382
Люберцы|55.6778|37.8927
Серпухов|54.9167|37.4167
Гороховец|56.2003|42.6867""",
"Беларусь": """Минск|53.9045|27.5615
Гомель|52.4345|30.9754
Могилёв|53.9007|30.3313
Витебск|55.1904|30.2049
Гродно|53.6694|23.8131
Брест|52.0976|23.7341
Бобруйск|53.1384|29.2214
Барановичи|53.1327|26.0139
Пинск|52.1229|26.0951
Орша|54.5081|30.4172
Мозырь|52.0495|29.2456
Новополоцк|55.5316|28.6564""",
"Украина": """Киев|50.4501|30.5234
Харьков|49.9935|36.2304
Одесса|46.4825|30.7233
Днепр|48.4647|35.0462
Львов|49.8397|24.0297
Запорожье|47.8388|35.1396
Винница|49.2331|28.4682
Полтава|49.5883|34.5514
Чернигов|51.4982|31.2893
Черкассы|49.4444|32.0598
Сумы|50.9077|34.7981
Житомир|50.2547|28.6587
Ровно|50.6199|26.2516
Ивано-Франковск|48.9226|24.7111
Тернополь|49.5535|25.5948
Луцк|50.7472|25.3254
Ужгород|48.6208|22.2879
Черновцы|48.2921|25.9358
Николаев|46.9750|31.9946
Херсон|46.6354|32.6169
Кропивницкий|48.5079|32.2623
Хмельницкий|49.4230|26.9871""",
"Казахстан": """Астана|51.1694|71.4491
Алматы|43.2220|76.8512
Шымкент|42.3417|69.5901
Караганда|49.8047|73.1094
Актобе|50.2839|57.1670
Тараз|42.9000|71.3667
Павлодар|52.2873|76.9674
Усть-Каменогорск|49.9483|82.6280
Семей|50.4233|80.2500
Атырау|47.1164|51.8830
Костанай|53.2144|63.6246
Кызылорда|44.8488|65.4823
Актау|43.6500|51.1500
Уральск|51.2278|51.3865
Петропавловск|54.8753|69.1628
Туркестан|43.2973|68.2517
Талдыкорган|45.0156|78.3739
Кокшетау|53.2833|69.4000
Экибастуз|51.7237|75.3229
Балхаш|46.8481|74.9950
Жезказган|47.7833|67.7667""",
"Узбекистан": """Ташкент|41.2995|69.2401
Самарканд|39.6542|66.9597
Бухара|39.7747|64.4286
Андижан|40.7821|72.3442
Наманган|40.9983|71.6726
Фергана|40.3842|71.7843
Нукус|42.4531|59.6103
Карши|38.8606|65.7891
Термез|37.2242|67.2783
Ургенч|41.5500|60.6333
Навои|40.0844|65.3792
Джизак|40.1158|67.8422
Коканд|40.5286|70.9425""",
"Кыргызстан": """Бишкек|42.8746|74.5698
Ош|40.5283|72.7985
Джалал-Абад|40.9333|72.9833
Каракол|42.4907|78.3936
Токмок|42.7625|75.3000
Нарын|41.4287|75.9911
Чолпон-Ата|42.6480|77.0828""",
"Таджикистан": """Душанбе|38.5598|68.7870
Худжанд|40.2826|69.6222
Бохтар|37.8364|68.7800
Куляб|37.9114|69.7828
Хорог|37.4894|71.5531""",
"Туркменистан": """Ашхабад|37.9601|58.3261
Туркменабат|39.0733|63.5786
Дашогуз|41.8363|59.9666
Мары|37.5942|61.8300
Туркменбаши|40.0230|52.9694
Балканабат|39.5100|54.3667""",
"Армения": """Ереван|40.1792|44.4991
Гюмри|40.7894|43.8475
Ванадзор|40.8128|44.4883
Севан|40.5486|44.9519
Горис|39.5114|46.3414""",
"Азербайджан": """Баку|40.4093|49.8671
Гянджа|40.6828|46.3606
Сумгаит|40.5855|49.6317
Мингечевир|40.7703|47.0496
Ленкорань|38.7529|48.8475
Шеки|41.1975|47.1706
Габала|40.9981|47.8458
Нахчыван|39.2089|45.4122""",
"Грузия": """Тбилиси|41.6938|44.8015
Батуми|41.6168|41.6367
Кутаиси|42.2679|42.7180
Рустави|41.5495|45.0050
Гори|41.9842|44.1128
Зугдиди|42.5088|41.8709
Телави|41.9198|45.4735
Степанцминда|42.6567|44.6422""",
"Молдова": """Кишинёв|47.0105|28.8638
Бельцы|47.7544|27.9184
Кагул|45.9040|28.1945
Орхей|47.3836|28.8239
Комрат|46.2955|28.6560""",
"Балтия": """Рига|56.9460|24.1059
Вильнюс|54.6872|25.2797
Таллин|59.4370|24.7536
Каунас|54.8985|23.9036
Тарту|58.3780|26.7290""",
"Обсерватории": """САО РАН (Архыз)|43.6469|41.4406
Терскол (Эльбрус)|43.2744|42.5008
Пулковская обсерватория|59.7667|30.3267
Бюраканская обсерватория|40.3347|44.2700
Майданакская обсерватория|38.6733|66.8967""",
}

def _build_cities():
    out = {}
    for country, block in _RAW.items():
        for line in block.strip().splitlines():
            n, la, lo = line.split("|")
            out[f"{n} · {country}"] = {"name": n, "country": country, "lat": float(la), "lon": float(lo)}
    return out

CITIES = _build_cities()
DEFAULT_CITY = "Москва · Россия"

# ════════════════════════════════════════════════════════════════
# СПРАВОЧНИКИ
# ════════════════════════════════════════════════════════════════
WMO_DESC = {
    0:"Ясно",1:"Малооблачно",2:"Переменная облачность",3:"Пасмурно",45:"Туман",48:"Изморозь",
    51:"Лёгкая морось",53:"Морось",55:"Сильная морось",56:"Ледяная морось",57:"Ледяная морось",
    61:"Небольшой дождь",63:"Дождь",65:"Сильный дождь",66:"Ледяной дождь",67:"Ледяной дождь",
    71:"Небольшой снег",73:"Снег",75:"Сильный снег",77:"Снежная крупа",
    80:"Кратковременный дождь",81:"Ливень",82:"Сильный ливень",85:"Снегопад",86:"Сильный снегопад",
    95:"Гроза",96:"Гроза с градом",99:"Гроза с крупным градом",
}

CONST_RU = {
"Andromeda":"Андромеда","Antlia":"Насос","Apus":"Райская Птица","Aquarius":"Водолей","Aquila":"Орёл","Ara":"Жертвенник",
"Aries":"Овен","Auriga":"Возничий","Bootes":"Волопас","Boötes":"Волопас","Caelum":"Резец","Camelopardalis":"Жираф",
"Cancer":"Рак","Canes Venatici":"Гончие Псы","Canis Major":"Большой Пёс","Canis Minor":"Малый Пёс",
"Capricornus":"Козерог","Carina":"Киль","Cassiopeia":"Кассиопея","Centaurus":"Центавр","Cepheus":"Цефей","Cetus":"Кит",
"Chamaeleon":"Хамелеон","Circinus":"Циркуль","Columba":"Голубь","Coma Berenices":"Волосы Вероники",
"Corona Australis":"Южная Корона","Corona Austrina":"Южная Корона","Corona Borealis":"Северная Корона","Corvus":"Ворон",
"Crater":"Чаша","Crux":"Южный Крест","Cygnus":"Лебедь","Delphinus":"Дельфин","Dorado":"Золотая Рыба","Draco":"Дракон",
"Equuleus":"Малый Конь","Eridanus":"Эридан","Fornax":"Печь","Gemini":"Близнецы","Grus":"Журавль","Hercules":"Геркулес",
"Horologium":"Часы","Hydra":"Гидра","Hydrus":"Южная Гидра","Indus":"Индеец","Lacerta":"Ящерица","Leo":"Лев",
"Leo Minor":"Малый Лев","Lepus":"Заяц","Libra":"Весы","Lupus":"Волк","Lynx":"Рысь","Lyra":"Лира","Mensa":"Столовая Гора",
"Microscopium":"Микроскоп","Monoceros":"Единорог","Musca":"Муха","Norma":"Наугольник","Octans":"Октант",
"Ophiuchus":"Змееносец","Orion":"Орион","Pavo":"Павлин","Pegasus":"Пегас","Perseus":"Персей","Phoenix":"Феникс",
"Pictor":"Живописец","Pisces":"Рыбы","Piscis Austrinus":"Южная Рыба","Puppis":"Корма","Pyxis":"Компас",
"Reticulum":"Сетка","Sagitta":"Стрела","Sagittarius":"Стрелец","Scorpius":"Скорпион","Sculptor":"Скульптор",
"Scutum":"Щит","Serpens":"Змея","Sextans":"Секстант","Taurus":"Телец","Telescopium":"Телескоп","Triangulum":"Треугольник",
"Triangulum Australe":"Южный Треугольник","Tucana":"Тукан","Ursa Major":"Большая Медведица","Ursa Minor":"Малая Медведица",
"Vela":"Паруса","Virgo":"Дева","Volans":"Летучая Рыба","Vulpecula":"Лисичка",
}

# Каталог ярких объектов глубокого космоса: id | название | тип | RA чч:мм.м | Dec ±гг:мм | блеск | размер, ′
_DSO_RAW = """M1|Крабовидная туманность|Остаток СН|05:34.5|+22:01|8.4|6×4
M2|M2|Шаровое скопление|21:33.5|-00:49|6.5|16
M3|M3|Шаровое скопление|13:42.2|+28:23|6.2|18
M4|M4|Шаровое скопление|16:23.6|-26:32|5.6|26
M5|M5|Шаровое скопление|15:18.6|+02:05|5.6|23
M6|Бабочка|Рассеянное скопление|17:40.1|-32:15|4.2|25
M7|Птолемей|Рассеянное скопление|17:53.9|-34:47|3.3|80
M8|Лагуна|Эмиссионная туманность|18:03.8|-24:23|6.0|90×40
M10|M10|Шаровое скопление|16:57.1|-04:06|6.6|20
M11|Дикая утка|Рассеянное скопление|18:51.1|-06:16|6.3|14
M12|M12|Шаровое скопление|16:47.2|-01:57|6.7|16
M13|Скопление Геркулеса|Шаровое скопление|16:41.7|+36:28|5.8|20
M15|M15|Шаровое скопление|21:30.0|+12:10|6.2|18
M16|Орёл|Эмиссионная туманность|18:18.8|-13:47|6.0|7
M17|Омега (Лебедь)|Эмиссионная туманность|18:20.8|-16:11|6.0|11
M20|Трёхраздельная|Эмиссионная туманность|18:02.6|-23:02|6.3|28
M22|M22|Шаровое скопление|18:36.4|-23:54|5.1|32
M27|Гантель|Планетарная туманность|19:59.6|+22:43|7.5|8×6
M29|M29|Рассеянное скопление|20:23.9|+38:32|6.6|7
M31|Туманность Андромеды|Галактика|00:42.7|+41:16|3.4|190×60
M32|M32|Галактика|00:42.7|+40:52|8.1|8×6
M33|Галактика Треугольника|Галактика|01:33.9|+30:39|5.7|70×42
M34|M34|Рассеянное скопление|02:42.0|+42:47|5.5|35
M35|M35|Рассеянное скопление|06:09.0|+24:21|5.3|28
M36|M36|Рассеянное скопление|05:36.1|+34:08|6.0|12
M37|M37|Рассеянное скопление|05:52.4|+32:33|5.6|24
M38|M38|Рассеянное скопление|05:28.7|+35:51|6.4|21
M39|M39|Рассеянное скопление|21:32.2|+48:26|4.6|32
M41|M41|Рассеянное скопление|06:46.0|-20:44|4.5|38
M42|Туманность Ориона|Эмиссионная туманность|05:35.4|-05:23|4.0|85×60
M44|Ясли (Praesepe)|Рассеянное скопление|08:40.4|+19:41|3.7|95
M45|Плеяды|Рассеянное скопление|03:47.0|+24:07|1.6|110
M46|M46|Рассеянное скопление|07:41.8|-14:49|6.1|27
M47|M47|Рассеянное скопление|07:36.6|-14:30|4.4|30
M51|Водоворот|Галактика|13:29.9|+47:12|8.4|11×7
M52|M52|Рассеянное скопление|23:24.2|+61:35|6.9|13
M56|M56|Шаровое скопление|19:16.6|+30:11|8.3|9
M57|Кольцо (Лира)|Планетарная туманность|18:53.6|+33:02|8.8|1.4×1
M63|Подсолнух|Галактика|13:15.8|+42:02|8.6|12×7
M64|Чёрный Глаз|Галактика|12:56.7|+21:41|8.5|10×5
M65|M65|Галактика|11:18.9|+13:05|9.3|10×3
M66|M66|Галактика|11:20.2|+12:59|8.9|9×4
M67|M67|Рассеянное скопление|08:51.4|+11:48|6.1|30
M71|M71|Шаровое скопление|19:53.8|+18:47|8.2|7
M74|M74|Галактика|01:36.7|+15:47|9.4|10
M78|M78|Отражательная туманность|05:46.7|+00:03|8.3|8×6
M79|M79|Шаровое скопление|05:24.5|-24:31|7.7|9
M81|Галактика Боде|Галактика|09:55.6|+69:04|6.9|27×14
M82|Сигара|Галактика|09:55.8|+69:41|8.4|11×4
M87|M87|Галактика|12:30.8|+12:24|8.6|7
M92|M92|Шаровое скопление|17:17.1|+43:08|6.4|14
M94|M94|Галактика|12:50.9|+41:07|8.2|11×9
M97|Сова|Планетарная туманность|11:14.8|+55:01|9.9|3
M101|Вертушка|Галактика|14:03.2|+54:21|7.9|29
M104|Сомбреро|Галактика|12:40.0|-11:37|8.0|9×4
M106|M106|Галактика|12:19.0|+47:18|8.4|19×8
M110|M110|Галактика|00:40.4|+41:41|8.5|20×10
NGC 869/884|Двойное скопление Персея|Рассеянное скопление|02:20.0|+57:08|3.7|60
NGC 457|Скопление Сова (ET)|Рассеянное скопление|01:19.1|+58:20|6.4|13
NGC 7000|Северная Америка|Эмиссионная туманность|20:58.8|+44:20|4.0|120×100
NGC 6992|Вуаль (Лебедь)|Остаток СН|20:56.8|+31:43|7.0|60
NGC 7293|Улитка (Хеликс)|Планетарная туманность|22:29.6|-20:50|7.6|16
NGC 2237|Розетта|Эмиссионная туманность|06:33.8|+04:59|9.0|80
NGC 891|NGC 891|Галактика|02:22.6|+42:21|10.0|13×3
NGC 7789|Роза Каролины|Рассеянное скопление|23:57.0|+56:44|6.7|16
Albireo|Альбирео|Двойная звезда|19:30.7|+27:58|3.1|0.6
Mizar|Мицар и Алькор|Двойная звезда|13:23.9|+54:56|2.2|0.2
"""

def _hm(s):  # "05:34.5" -> часы
    h, m = s.split(":"); return float(h) + float(m) / 60
def _dm(s):  # "+22:01" -> градусы
    sign = -1 if s.startswith("-") else 1
    d, m = s.lstrip("+-").split(":"); return sign * (float(d) + float(m) / 60)

DSO = []
for _l in _DSO_RAW.strip().splitlines():
    i, n, t, ra, de, mg, sz = _l.split("|")
    DSO.append({"id": i, "name": n, "type": t, "ra": _hm(ra), "dec": _dm(de), "mag": float(mg), "size": sz})

# Метеорные потоки: название | пик (мм-дд) | ZHR | скорость км/с | RA | Dec | родитель
_SHOWERS_RAW = """Квадрантиды|01-04|110|41|15:20|+49:30|2003 EH1
Лириды|04-22|18|49|18:04|+34:00|C/1861 G1 Thatcher
Эта-Аквариды|05-06|50|66|22:32|-01:00|1P/Галлея
Южные Дельта-Аквариды|07-30|25|41|22:36|-16:00|96P/Мачхольца
Персеиды|08-12|100|59|03:12|+58:00|109P/Свифта–Туттля
Дракониды|10-08|10|20|17:28|+54:00|21P/Джакобини–Циннера
Ориониды|10-21|20|66|06:20|+16:00|1P/Галлея
Южные Тауриды|11-05|5|27|03:28|+13:00|2P/Энке
Северные Тауриды|11-12|5|29|03:52|+22:00|2P/Энке
Леониды|11-17|15|71|10:12|+22:00|55P/Темпеля–Туттля
Геминиды|12-14|150|35|07:28|+33:00|3200 Фаэтон
Урсиды|12-22|10|33|14:28|+76:00|8P/Туттля"""
SHOWERS = []
for _l in _SHOWERS_RAW.splitlines():
    n, pk, z, v, ra, de, par = _l.split("|")
    SHOWERS.append({"name": n, "peak": pk, "zhr": int(z), "speed": int(v), "ra": _hm(ra), "dec": _dm(de), "parent": par})

# Затмения (справочно; точную видимость проверяйте на timeanddate.com / eclipse.gsfc.nasa.gov)
ECLIPSES = [
    ("2027-02-06", "Кольцеобразное солнечное", "Южная Америка, Атлантика, запад Африки"),
    ("2027-02-20", "Полутеневое лунное", "Америка, Европа, Африка"),
    ("2027-07-18", "Полутеневое лунное", "Азия, Австралия, Тихий океан"),
    ("2027-08-02", "Полное солнечное", "Испания, Северная Африка, Аравия; частное — в Европе"),
    ("2027-08-17", "Полутеневое лунное", "Америка, Африка"),
    ("2028-01-12", "Частное лунное", "Америка, Европа, Африка"),
    ("2028-01-26", "Кольцеобразное солнечное", "Эквадор, Перу, Бразилия, Испания, Португалия"),
    ("2028-07-06", "Частное лунное", "Европа, Африка, Азия, Австралия"),
    ("2028-07-22", "Полное солнечное", "Австралия, Новая Зеландия"),
    ("2028-12-31", "Полное лунное", "Европа, Африка, Азия, Австралия"),
]

# Линии созвездий по именам звёзд из каталога ephem (отсутствующие пары пропускаются)
CONST_LINES = {
 "Большая Медведица":[("Dubhe","Merak"),("Merak","Phecda"),("Phecda","Megrez"),("Megrez","Dubhe"),("Megrez","Alioth"),("Alioth","Mizar"),("Mizar","Alkaid")],
 "Орион":[("Betelgeuse","Bellatrix"),("Betelgeuse","Alnitak"),("Bellatrix","Mintaka"),("Mintaka","Alnilam"),("Alnilam","Alnitak"),("Alnitak","Saiph"),("Mintaka","Rigel")],
 "Кассиопея":[("Caph","Schedar"),("Schedar","Navi"),("Navi","Ruchbah"),("Ruchbah","Segin")],
 "Лебедь":[("Deneb","Sadr"),("Sadr","Albireo"),("Sadr","Gienah"),("Sadr","Delta Cygni")],
 "Лира":[("Vega","Sheliak"),("Sheliak","Sulafat"),("Vega","Sulafat")],
 "Лев":[("Regulus","Algieba"),("Algieba","Zosma"),("Zosma","Denebola"),("Zosma","Chertan")],
 "Скорпион":[("Antares","Dschubba"),("Antares","Shaula"),("Dschubba","Graffias")],
 "Пегас":[("Markab","Scheat"),("Scheat","Algenib"),("Algenib","Alpheratz"),("Alpheratz","Scheat"),("Algenib","Markab")],
 "Телец":[("Aldebaran","Elnath"),("Aldebaran","Alcyone")],
 "Близнецы":[("Castor","Pollux"),("Pollux","Alhena"),("Castor","Mebsuta")],
 "Летний треугольник":[("Vega","Deneb"),("Deneb","Altair"),("Altair","Vega")],
 "Малая Медведица":[("Polaris","Kochab"),("Kochab","Pherkad")],
 "Возничий":[("Capella","Menkalinan"),("Menkalinan","Elnath")],
 "Большой Пёс":[("Sirius","Mirzam"),("Sirius","Adara"),("Sirius","Wezen")],
}

def const_ru(name):
    return CONST_RU.get(name, name)

def wmo_desc(code):
    try: return WMO_DESC.get(int(code), "—")
    except Exception: return "—"

# ════════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ  (каждый источник — с таймаутом, повторами и безопасным откатом)
# ════════════════════════════════════════════════════════════════
UA = {"User-Agent": "WeatherAstro/4.0 (personal project)"}
_http = requests.Session()
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    _http.mount("https://", HTTPAdapter(max_retries=Retry(total=2, backoff_factor=0.6, status_forcelist=(429, 500, 502, 503, 504))))
except Exception:
    pass

def _get(url, params=None, timeout=12, headers=None):
    r = _http.get(url, params=params, timeout=timeout, headers={**UA, **(headers or {})})
    r.raise_for_status()
    return r

def secret(name, default=""):
    try:
        v = st.secrets.get(name)
    except Exception:
        v = None
    return v or os.environ.get(name, default)

# ── Open-Meteo: основной источник ─────────────────────────────
OM_HOURLY = ("temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,"
    "precipitation,weather_code,surface_pressure,pressure_msl,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,"
    "wind_speed_10m,wind_direction_10m,wind_gusts_10m,visibility,uv_index,cape,soil_temperature_0cm,soil_temperature_6cm,"
    "soil_moisture_0_to_1cm,temperature_850hPa,temperature_700hPa,temperature_500hPa,temperature_300hPa,"
    "relative_humidity_850hPa,relative_humidity_700hPa,relative_humidity_500hPa,relative_humidity_300hPa,"
    "wind_speed_850hPa,wind_speed_700hPa,wind_speed_500hPa,wind_speed_300hPa,"
    "wind_direction_850hPa,wind_direction_700hPa,wind_direction_500hPa,wind_direction_300hPa")
OM_DAILY = ("weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max,wind_speed_10m_max,"
    "wind_gusts_10m_max,precipitation_probability_max,precipitation_sum,snowfall_sum,et0_fao_evapotranspiration")
OM_CURRENT = ("temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,cloud_cover,"
    "surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m")

@st.cache_data(ttl=600, show_spinner=False)
def _om(lat, lon):
    return _get("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon, "current": OM_CURRENT, "hourly": OM_HOURLY, "daily": OM_DAILY,
        "wind_speed_unit": "ms", "timezone": "auto", "forecast_days": 7, "past_days": 1}).json()

def fetch_openmeteo(lat, lon):
    try:
        d = _om(round(lat, 4), round(lon, 4))
        d["_source"] = "Open-Meteo"
        return d
    except Exception:
        return None

@st.cache_data(ttl=900, show_spinner=False)
def _models(lat, lon):
    names = ["ecmwf_ifs025", "gfs_seamless", "icon_seamless"]
    j = _get("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon, "models": ",".join(names), "timezone": "auto", "forecast_days": 3,
        "hourly": "temperature_2m,cloud_cover,precipitation,wind_speed_10m", "wind_speed_unit": "ms"}).json()
    h = j["hourly"]; out = {}
    for m in names:
        if f"temperature_2m_{m}" in h:
            out[m] = {k: h.get(f"{k}_{m}") for k in ("temperature_2m", "cloud_cover", "precipitation", "wind_speed_10m")}
    return {"time": h["time"], "models": out}

def fetch_models(lat, lon):
    try: return _models(round(lat, 3), round(lon, 3))
    except Exception: return None

@st.cache_data(ttl=600, show_spinner=False)
def _marine(lat, lon):
    return _get("https://marine-api.open-meteo.com/v1/marine", {"latitude": lat, "longitude": lon,
        "hourly": "wave_height,wave_direction,wave_period,sea_surface_temperature", "timezone": "auto", "forecast_days": 3}).json()
def fetch_marine(lat, lon):
    try: return _marine(round(lat, 3), round(lon, 3))
    except Exception: return None

@st.cache_data(ttl=900, show_spinner=False)
def _aq(lat, lon):
    return _get("https://air-quality-api.open-meteo.com/v1/air-quality", {"latitude": lat, "longitude": lon,
        "hourly": "pm10,pm2_5,nitrogen_dioxide,ozone,european_aqi,birch_pollen,grass_pollen,alder_pollen,ragweed_pollen",
        "timezone": "auto", "forecast_days": 2}).json()
def fetch_airquality(lat, lon):
    try: return _aq(round(lat, 3), round(lon, 3))
    except Exception: return None

# ── MET Norway (Yr): независимый источник + резерв ────────────
@st.cache_data(ttl=900, show_spinner=False)
def _yr(lat, lon):
    return _get("https://api.met.no/weatherapi/locationforecast/2.0/complete", {"lat": lat, "lon": lon}).json()

def fetch_yr(lat, lon):
    """Возвращает таблицу по часам (UTC) или None."""
    try:
        ts = _yr(round(lat, 3), round(lon, 3))["properties"]["timeseries"]
    except Exception:
        return None
    rows = []
    for e in ts:
        d = e["data"]; i = d["instant"]["details"]
        n1 = d.get("next_1_hours") or {}
        rows.append({
            "time": pd.Timestamp(e["time"]).tz_convert("UTC"),
            "temp": i.get("air_temperature"), "dew": i.get("dew_point_temperature"),
            "rh": i.get("relative_humidity"), "pressure": i.get("air_pressure_at_sea_level"),
            "cloud": i.get("cloud_area_fraction"), "cloud_low": i.get("cloud_area_fraction_low"),
            "cloud_mid": i.get("cloud_area_fraction_medium"), "cloud_high": i.get("cloud_area_fraction_high"),
            "fog": i.get("fog_area_fraction"),
            "wind": i.get("wind_speed"), "wind_dir": i.get("wind_from_direction"), "gust": i.get("wind_speed_of_gust"),
            "precip": (n1.get("details") or {}).get("precipitation_amount"),
            "symbol": (n1.get("summary") or {}).get("symbol_code"),
        })
    return pd.DataFrame(rows) if rows else None

def _symbol_to_wmo(s):
    if not s: return 3
    s = s.split("_")[0]
    if "thunder" in s: return 95
    if "snow" in s: return 75 if "heavy" in s else (71 if "light" in s else 73)
    if "sleet" in s: return 67
    if "rain" in s: return 65 if "heavy" in s else (61 if "light" in s else 63)
    return {"clearsky": 0, "fair": 1, "partlycloudy": 2, "cloudy": 3, "fog": 45}.get(s, 3)

def openmeteo_from_yr(df, lat, lon):
    """Если Open-Meteo недоступен — собираем совместимую структуру из MET Norway."""
    if df is None or df.empty: return None
    off = int(round(lon / 15)); tzname = f"Etc/GMT{-off:+d}" if off else "UTC"
    tz = ZoneInfo(tzname)
    df = df.copy(); df["lt"] = df["time"].dt.tz_convert(tz).dt.tz_localize(None)
    df = df[df["lt"] >= df["lt"].iloc[0].floor("D")].head(48 * 2)
    df = df.drop_duplicates("lt").set_index("lt").resample("1h").first().interpolate(limit=6).reset_index()
    def col(c, f=lambda x: x): return [None if pd.isna(v) else f(v) for v in df[c]]
    n = len(df); z = [0] * n
    hourly = {
        "time": [t.strftime("%Y-%m-%dT%H:%M") for t in df["lt"]],
        "temperature_2m": col("temp"), "relative_humidity_2m": col("rh"), "dew_point_2m": col("dew"),
        "apparent_temperature": col("temp"), "precipitation_probability": [None] * n,
        "precipitation": [0 if v is None else v for v in col("precip")],
        "weather_code": [_symbol_to_wmo(s) for s in df["symbol"].ffill().fillna("cloudy")],
        "surface_pressure": col("pressure"), "pressure_msl": col("pressure"),
        "cloud_cover": col("cloud"), "cloud_cover_low": col("cloud_low"), "cloud_cover_mid": col("cloud_mid"),
        "cloud_cover_high": col("cloud_high"), "wind_speed_10m": col("wind"), "wind_direction_10m": col("wind_dir"),
        "wind_gusts_10m": col("gust"), "visibility": [None] * n, "uv_index": z, "cape": z,
    }
    d0 = df["lt"].dt.date; days = sorted(set(d0))[:7]; D = {k: [] for k in
        ("time", "weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "uv_index_max",
         "wind_speed_10m_max", "wind_gusts_10m_max", "precipitation_probability_max", "precipitation_sum", "snowfall_sum")}
    for d in days:
        m = (d0 == d).values
        t = df.loc[m, "temp"]; 
        D["time"].append(d.isoformat()); D["weather_code"].append(int(pd.Series([hourly["weather_code"][i] for i in np.where(m)[0]]).mode()[0]))
        D["temperature_2m_max"].append(float(t.max())); D["temperature_2m_min"].append(float(t.min()))
        D["sunrise"].append(None); D["sunset"].append(None); D["uv_index_max"].append(0)
        D["wind_speed_10m_max"].append(float(df.loc[m, "wind"].max())); D["wind_gusts_10m_max"].append(0)
        D["precipitation_probability_max"].append(0); D["precipitation_sum"].append(float(sum(hourly["precipitation"][i] for i in np.where(m)[0])))
        D["snowfall_sum"].append(0)
    now = datetime.now(tz).replace(tzinfo=None).strftime("%Y-%m-%dT%H:00")
    i = hourly["time"].index(now) if now in hourly["time"] else 0
    cur = {"time": hourly["time"][i], "is_day": 1}
    for k_cur, k_h in (("temperature_2m","temperature_2m"),("relative_humidity_2m","relative_humidity_2m"),
        ("apparent_temperature","apparent_temperature"),("weather_code","weather_code"),("cloud_cover","cloud_cover"),
        ("surface_pressure","surface_pressure"),("wind_speed_10m","wind_speed_10m"),("wind_direction_10m","wind_direction_10m"),
        ("wind_gusts_10m","wind_gusts_10m"),("precipitation","precipitation")):
        cur[k_cur] = hourly[k_h][i]
    return {"current": cur, "hourly": hourly, "daily": D, "timezone": tzname, "elevation": 0,
            "utc_offset_seconds": off * 3600, "_source": "MET Norway (резерв)"}

# ── Необязательные источники для сверки (нужны ключи) ─────────
@st.cache_data(ttl=900, show_spinner=False)
def _owm(lat, lon, key):
    return _get("https://api.openweathermap.org/data/2.5/weather", {"lat": lat, "lon": lon, "units": "metric", "appid": key}).json()
def fetch_owm(lat, lon):
    key = secret("OWM_KEY")
    if not key: return None
    try:
        j = _owm(round(lat, 3), round(lon, 3), key)
        return {"temp": j["main"]["temp"], "rh": j["main"]["humidity"], "pressure": j["main"]["pressure"],
                "wind": j["wind"]["speed"], "cloud": j["clouds"]["all"]}
    except Exception: return None

@st.cache_data(ttl=900, show_spinner=False)
def _wapi(lat, lon, key):
    return _get("https://api.weatherapi.com/v1/current.json", {"key": key, "q": f"{lat},{lon}"}).json()
def fetch_weatherapi(lat, lon):
    key = secret("WEATHERAPI_KEY")
    if not key: return None
    try:
        c = _wapi(round(lat, 3), round(lon, 3), key)["current"]
        return {"temp": c["temp_c"], "rh": c["humidity"], "pressure": c["pressure_mb"],
                "wind": c["wind_kph"] / 3.6, "cloud": c["cloud"]}
    except Exception: return None

# ── METAR / TAF: фактические наблюдения ближайшей станции ─────
@st.cache_data(ttl=600, show_spinner=False)
def _metar(lat, lon, box):
    r = _get("https://aviationweather.gov/api/data/metar",
             {"bbox": f"{lat-box},{lon-box*1.6},{lat+box},{lon+box*1.6}", "format": "json"}, timeout=10)
    return r.json() if r.text.strip() else []

def haversine(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))

def fetch_metar(lat, lon):
    """Ближайшая станция с наблюдением (не дальше ~150 км)."""
    for box in (0.7, 1.5, 2.5):
        try:
            obs = [o for o in _metar(round(lat, 2), round(lon, 2), box) if o.get("lat") is not None and o.get("temp") is not None]
        except Exception:
            return None
        if obs:
            o = min(obs, key=lambda x: haversine(lat, lon, x["lat"], x["lon"]))
            o["_dist"] = haversine(lat, lon, o["lat"], o["lon"])
            return o if o["_dist"] <= 150 else None
    return None

@st.cache_data(ttl=1800, show_spinner=False)
def _taf(icao):
    return _get("https://aviationweather.gov/api/data/taf", {"ids": icao, "format": "json"}, timeout=10).json()
def fetch_taf(icao):
    try:
        d = _taf(icao); return d[0] if d else None
    except Exception: return None

# ── Геокодинг (поиск любого города мира) ──────────────────────
@st.cache_data(ttl=86400, show_spinner=False)
def _geo(q):
    return _get("https://geocoding-api.open-meteo.com/v1/search", {"name": q, "count": 8, "language": "ru", "format": "json"}).json()
def geocode(q):
    try: return _geo(q.strip()).get("results") or []
    except Exception: return []

# ── Астро-источники ───────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def _7timer(lat, lon):
    return _get("http://www.7timer.info/bin/astro.php", {"lon": lon, "lat": lat, "ac": 0, "unit": "metric",
                "output": "json", "tzshift": 0}, timeout=12).json()

SEEING_ARCSEC = {1: "<0.5″", 2: "0.5–0.75″", 3: "0.75–1″", 4: "1–1.25″", 5: "1.25–1.5″", 6: "1.5–2″", 7: "2–2.5″", 8: ">2.5″"}
TRANSP_TXT = {1: "<0.3", 2: "0.3–0.4", 3: "0.4–0.5", 4: "0.5–0.6", 5: "0.6–0.7", 6: "0.7–0.85", 7: "0.85–1", 8: ">1"}

def fetch_7timer(lat, lon):
    """Seeing и прозрачность (модель 7Timer!, шаг 3 ч). Возвращает DataFrame с UTC-временем."""
    try:
        j = _7timer(round(lat, 2), round(lon, 2))
        init = datetime.strptime(str(j["init"]), "%Y%m%d%H").replace(tzinfo=timezone.utc)
        rows = [{"time": pd.Timestamp(init + timedelta(hours=int(p["timepoint"]))),
                 "cloud7": p["cloudcover"], "seeing": p["seeing"], "transp": p["transparency"],
                 "li": p.get("lifted_index")} for p in j["dataseries"]]
        return pd.DataFrame(rows)
    except Exception:
        return None

def _swpc(path):
    return _get("https://services.swpc.noaa.gov/" + path, timeout=12).json()

@st.cache_data(ttl=600, show_spinner=False)
def _kp(): return _swpc("products/noaa-planetary-k-index.json")
@st.cache_data(ttl=600, show_spinner=False)
def _kp_fc(): return _swpc("products/noaa-planetary-k-index-forecast.json")
@st.cache_data(ttl=300, show_spinner=False)
def _plasma(): return _swpc("products/solar-wind/plasma-1-day.json")
@st.cache_data(ttl=300, show_spinner=False)
def _mag(): return _swpc("products/solar-wind/mag-1-day.json")
@st.cache_data(ttl=300, show_spinner=False)
def _xray(): return _swpc("json/goes/primary/xrays-1-day.json")
@st.cache_data(ttl=3600, show_spinner=False)
def _f107(): return _swpc("products/summary/10cm-flux.json")
@st.cache_data(ttl=900, show_spinner=False)
def _ovation(): return _swpc("json/ovation_aurora_latest.json")

def _table(raw):
    """SWPC отдаёт списки списков: первая строка — заголовки."""
    return pd.DataFrame(raw[1:], columns=raw[0])

def fetch_space_weather():
    out = {}
    try:
        kp = _table(_kp()); kp["time_tag"] = pd.to_datetime(kp["time_tag"]); kp["Kp"] = pd.to_numeric(kp["Kp"]); out["kp"] = kp
    except Exception: out["kp"] = None
    try:
        f = _kp_fc(); fk = _table(f); fk["time_tag"] = pd.to_datetime(fk["time_tag"]); fk["kp"] = pd.to_numeric(fk["kp"]); out["kp_fc"] = fk
    except Exception: out["kp_fc"] = None
    try:
        p = _table(_plasma()); p["time_tag"] = pd.to_datetime(p["time_tag"])
        for c in ("density", "speed"): p[c] = pd.to_numeric(p[c], errors="coerce")
        out["plasma"] = p
    except Exception: out["plasma"] = None
    try:
        m = _table(_mag()); m["time_tag"] = pd.to_datetime(m["time_tag"])
        for c in ("bz_gsm", "bt"): m[c] = pd.to_numeric(m[c], errors="coerce")
        out["mag"] = m
    except Exception: out["mag"] = None
    try:
        x = pd.DataFrame(_xray()); x = x[x["energy"] == "0.1-0.8nm"].copy()
        x["time_tag"] = pd.to_datetime(x["time_tag"]); out["xray"] = x
    except Exception: out["xray"] = None
    try: out["f107"] = float(_f107()["Flux"])
    except Exception: out["f107"] = None
    return out

def aurora_probability(lat, lon):
    """Вероятность полярного сияния из модели OVATION (NOAA) для ближайшей точки сетки."""
    try:
        co = _ovation()["coordinates"]
        lon360 = lon % 360
        best = min((c for c in co if abs(c[1] - lat) <= 1.5 and min(abs(c[0] - lon360), 360 - abs(c[0] - lon360)) <= 1.5),
                   key=lambda c: (c[1] - lat) ** 2 + (c[0] - lon360) ** 2, default=None)
        return float(best[2]) if best else 0.0
    except Exception:
        return None

@st.cache_data(ttl=21600, show_spinner=False)
def _apod(key): return _get("https://api.nasa.gov/planetary/apod", {"api_key": key}, timeout=15).json()
def fetch_apod():
    try: return _apod(secret("NASA_KEY", "DEMO_KEY"))
    except Exception: return None

SATS = {"МКС (ISS)": 25544, "Китайская станция (CSS)": 48274, "Хаббл": 20580}

@st.cache_data(ttl=3600, show_spinner=False)
def _tle(cat):
    t = _get("https://celestrak.org/NORAD/elements/gp.php", {"CATNR": cat, "FORMAT": "tle"}, timeout=12).text.strip().splitlines()
    if len(t) < 3: raise ValueError("bad TLE")
    return [x.strip() for x in t[:3]]
def fetch_tle(cat):
    try: return _tle(cat)
    except Exception: return None

@st.cache_data(ttl=20, show_spinner=False)
def _iss_now(): return _get("https://api.wheretheiss.at/v1/satellites/25544", timeout=8).json()
def fetch_iss_now():
    try: return _iss_now()
    except Exception: return None

# ════════════════════════════════════════════════════════════════
# АСТРОНОМИЧЕСКИЕ РАСЧЁТЫ  (PyEphem; всё считается во времени выбранного города, а не сервера)
# ════════════════════════════════════════════════════════════════
BORTLE = {
    1: ("Эталонно тёмное", 7.8), 2: ("Очень тёмное", 7.3), 3: ("Сельское", 6.8), 4: ("Сельско-пригородное", 6.3),
    5: ("Пригород", 5.8), 6: ("Яркий пригород", 5.3), 7: ("Пригород и город", 4.8), 8: ("Город", 4.3), 9: ("Центр города", 3.8),
}
SYN = 29.530588  # синодический месяц, сут

def deg(x): return math.degrees(float(x))
def compass(az):
    return ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"][int(((az % 360) + 22.5) // 45) % 8]
def tzinfo(name):
    try: return ZoneInfo(name)
    except Exception: return timezone.utc
def to_utc_naive(dt): return dt.astimezone(timezone.utc).replace(tzinfo=None)
def d2l(d, tz):
    """ephem.Date -> aware datetime в часовом поясе города"""
    if d is None: return None
    return ephem.Date(d).datetime().replace(tzinfo=timezone.utc).astimezone(tz)
def hhmm(dt, fmt="%H:%M"): return dt.strftime(fmt) if dt is not None else "—"
def local_noon(date_iso, tzname):
    d = date.fromisoformat(date_iso); return datetime(d.year, d.month, d.day, 12, tzinfo=tzinfo(tzname))

def mk_obs(lat, lon, elev, when_naive_utc, pressure=None, horizon=None):
    o = ephem.Observer()
    o.lat, o.lon, o.elevation = str(lat), str(lon), float(elev or 0)
    if pressure is not None: o.pressure = pressure
    if horizon is not None: o.horizon = str(horizon)
    o.date = ephem.Date(when_naive_utc)
    return o

def _try(fn, *a, **k):
    try: return fn(*a, **k)
    except Exception: return None   # AlwaysUp / NeverUp / полярный день и ночь

# ── События Солнца и Луны для «ночи» с вечера даты D до утра D+1 ─────────
@st.cache_data(ttl=3600, show_spinner=False)
def sun_moon_events(lat, lon, elev, tzname, date_iso):
    tz = tzinfo(tzname); noon = to_utc_naive(local_noon(date_iso, tzname))
    mid = noon - timedelta(hours=12)
    sun, moon = ephem.Sun(), ephem.Moon()
    r = {}
    o = mk_obs(lat, lon, elev, mid)
    r["sunrise"] = d2l(_try(o.next_rising, sun), tz); r["sunset"] = d2l(_try(o.next_setting, sun), tz)
    o = mk_obs(lat, lon, elev, mid); r["noon"] = d2l(_try(o.next_transit, sun), tz)
    if r["noon"] is not None:
        o = mk_obs(lat, lon, elev, to_utc_naive(r["noon"])); sun.compute(o); r["noon_alt"] = deg(sun.alt)
    r["day_len"] = (r["sunset"] - r["sunrise"]) if r["sunrise"] and r["sunset"] else None
    o = mk_obs(lat, lon, elev, noon); r["sunrise_next"] = d2l(_try(o.next_rising, sun), tz)
    for key, h in (("civil", -6), ("naut", -12), ("astro", -18)):
        o = mk_obs(lat, lon, elev, noon, pressure=0, horizon=h)
        r[key + "_eve"] = d2l(_try(o.next_setting, sun, use_center=True), tz)
        o = mk_obs(lat, lon, elev, noon, pressure=0, horizon=h)
        r[key + "_morn"] = d2l(_try(o.next_rising, sun, use_center=True), tz)
    o = mk_obs(lat, lon, elev, noon); r["moonrise"] = d2l(_try(o.next_rising, moon), tz)
    o = mk_obs(lat, lon, elev, noon); r["moonset"] = d2l(_try(o.next_setting, moon), tz)
    if r["astro_eve"] and r["astro_morn"]: r["night_len"] = r["astro_morn"] - r["astro_eve"]
    else: r["night_len"] = None
    return r

@st.cache_data(ttl=3600, show_spinner=False)
def night_grid(lat, lon, elev, tzname, date_iso, step=10):
    """Положение Солнца и Луны каждые `step` минут с 12:00 дня D до 12:00 дня D+1 (геометрическая высота)."""
    t0 = to_utc_naive(local_noon(date_iso, tzname)); tz = tzinfo(tzname)
    o = mk_obs(lat, lon, elev, t0, pressure=0); sun, moon = ephem.Sun(), ephem.Moon(); rows = []
    for k in range(int(24 * 60 / step) + 1):
        tu = t0 + timedelta(minutes=k * step); o.date = ephem.Date(tu)
        sun.compute(o); moon.compute(o)
        rows.append((tu.replace(tzinfo=timezone.utc).astimezone(tz), deg(sun.alt), deg(sun.az), deg(moon.alt), deg(moon.az), float(moon.phase)))
    return pd.DataFrame(rows, columns=["t", "sun_alt", "sun_az", "moon_alt", "moon_az", "moon_ill"])

def dark_windows(grid, moon_free=False, sun_limit=-18):
    """Непрерывные интервалы тёмного неба (Солнце ниже sun_limit; опционально Луна под горизонтом)."""
    m = grid["sun_alt"] < sun_limit
    if moon_free: m &= grid["moon_alt"] < 0
    out, start = [], None
    for t, flag in zip(grid["t"], m):
        if flag and start is None: start = t
        if not flag and start is not None: out.append((start, prev)); start = None
        prev = t
    if start is not None: out.append((start, prev))
    return out

# ── Луна ────────────────────────────────────────────────────
def moon_phase_name(age):
    f = age / SYN
    if f < 0.03 or f > 0.97: return "Новолуние"
    if f < 0.22: return "Растущий серп"
    if f < 0.28: return "Первая четверть"
    if f < 0.47: return "Растущая Луна"
    if f < 0.53: return "Полнолуние"
    if f < 0.72: return "Убывающая Луна"
    if f < 0.78: return "Последняя четверть"
    return "Убывающий серп"

@st.cache_data(ttl=300, show_spinner=False)
def moon_info(lat, lon, elev, tzname, when_iso):
    tz = tzinfo(tzname); when = datetime.fromisoformat(when_iso)       # naive UTC
    o = mk_obs(lat, lon, elev, when); m = ephem.Moon(o); d0 = ephem.Date(when)
    age = float(d0 - ephem.previous_new_moon(d0))
    return {
        "illum": float(m.phase), "age": age, "waxing": age < SYN / 2, "name": moon_phase_name(age),
        "alt": deg(m.alt), "az": deg(m.az), "dist_km": float(m.earth_distance) * 149597870.7, "size": float(m.size),
        "const": ephem.constellation(m)[1], "colong": deg(m.colong), "lib_lat": deg(m.libration_lat), "lib_lon": deg(m.libration_long),
        "new": d2l(ephem.next_new_moon(d0), tz), "first": d2l(ephem.next_first_quarter_moon(d0), tz),
        "full": d2l(ephem.next_full_moon(d0), tz), "last": d2l(ephem.next_last_quarter_moon(d0), tz),
    }

@st.cache_data(ttl=3600, show_spinner=False)
def moon_month(tzname, date_iso, days=30):
    """Освещённость Луны на ближайшие дни (в 22:00 по местному времени)."""
    base = local_noon(date_iso, tzname).replace(hour=22); m = ephem.Moon(); out = []
    for k in range(days + 1):
        t = base + timedelta(days=k); m.compute(ephem.Date(to_utc_naive(t)))
        out.append((t.date(), float(m.phase)))
    return out

# ── Планеты ─────────────────────────────────────────────────
def planet_defs():
    return [("Меркурий", ephem.Mercury), ("Венера", ephem.Venus), ("Марс", ephem.Mars), ("Юпитер", ephem.Jupiter),
            ("Сатурн", ephem.Saturn), ("Уран", ephem.Uranus), ("Нептун", ephem.Neptune)]

@st.cache_data(ttl=900, show_spinner=False)
def planets_info(lat, lon, elev, tzname, date_iso, when_iso):
    tz = tzinfo(tzname); noon = to_utc_naive(local_noon(date_iso, tzname)); when = datetime.fromisoformat(when_iso)
    grid = night_grid(lat, lon, elev, tzname, date_iso)
    dark = (grid["sun_alt"] < -6).values
    oN = mk_obs(lat, lon, elev, when); rows = []; alts = {}
    og = mk_obs(lat, lon, elev, noon, pressure=0)
    for name, cls in planet_defs():
        b = cls(); b.compute(oN)
        o = mk_obs(lat, lon, elev, noon)
        rise, tr, st_ = (d2l(_try(o.next_rising, cls()), tz), d2l(_try(o.next_transit, cls()), tz), d2l(_try(o.next_setting, cls()), tz))
        a = []
        for t in grid["t"]:
            og.date = ephem.Date(to_utc_naive(t)); b2 = cls(); b2.compute(og); a.append(deg(b2.alt))
        a = np.array(a); alts[name] = a
        good = dark & (a > 8)
        if not good.any(): vis = "Не видна ночью"
        else:
            idx = np.where(good)[0]; mid = len(a) // 2   # середина окна ≈ местная полночь
            vis = "Всю ночь" if idx.min() < mid - 12 and idx.max() > mid + 12 else ("Вечером" if idx.mean() < mid else "Утром")
        el = deg(b.elong)
        rows.append({"name": name, "alt": deg(b.alt), "az": deg(b.az), "mag": float(b.mag), "elong": el, "phase": float(b.phase),
                     "dist": float(b.earth_distance), "size": float(b.size), "const": ephem.constellation(b)[1],
                     "rise": rise, "transit": tr, "set": st_, "vis": vis, "max_night_alt": float(a[dark].max()) if dark.any() else float("nan")})
    return rows, pd.DataFrame({"t": grid["t"], **alts})

@st.cache_data(ttl=3600, show_spinner=False)
def conjunctions(date_iso, tzname, days=45):
    """Сближения планет и Луны с планетами (геоцентрически), с шагом 3 часа."""
    t0 = to_utc_naive(local_noon(date_iso, tzname)); per = 8; n = days * per
    bodies = {name: cls() for name, cls in planet_defs()}; bodies["Луна"] = ephem.Moon(); sun = ephem.Sun()
    pos = {k: [] for k in bodies}; sp = {k: [] for k in bodies}
    for i in range(n):
        d = ephem.Date(t0 + timedelta(hours=24 / per * i)); sun.compute(d)
        for k, b in bodies.items():
            b.compute(d); pos[k].append((b.a_ra, b.a_dec)); sp[k].append(deg(ephem.separation((b.a_ra, b.a_dec), (sun.a_ra, sun.a_dec))))
    names = list(bodies); out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            thr = 5.0 if "Луна" in (a, b) else 4.0
            s = [deg(ephem.separation(pa, pb)) for pa, pb in zip(pos[a], pos[b])]
            for k in range(1, n - 1):
                if s[k] < thr and s[k] <= s[k - 1] and s[k] < s[k + 1]:
                    near_sun = min(sp[a][k], sp[b][k] if b != "Луна" else 99)
                    when = t0 + timedelta(hours=24 / per * k)
                    out.append({"when": when.replace(tzinfo=timezone.utc).astimezone(tzinfo(tzname)), "pair": f"{a} и {b}", "sep": s[k],
                                "note": "рядом с Солнцем, не наблюдается" if min(sp[a][k], sp[b][k]) < 15 else ""})
    return sorted(out, key=lambda x: x["when"])

# ── Звёзды, объекты глубокого космоса, созвездия ─────────────
@st.cache_data(show_spinner=False)
def star_catalog():
    """[(имя, RA рад, Dec рад, блеск)] из каталога PyEphem (~100 ярких звёзд)."""
    out = []
    try:
        import ephem.stars as _es
        names = list(_es.stars.keys())
    except Exception:
        names = ["Sirius", "Vega", "Arcturus", "Capella", "Rigel", "Procyon", "Betelgeuse", "Altair", "Aldebaran", "Spica", "Antares",
                 "Pollux", "Deneb", "Regulus", "Polaris", "Dubhe", "Castor"]
    for n in names:
        try:
            s = ephem.star(n); out.append((n, float(s._ra), float(s._dec), float(s.mag)))
        except Exception:
            pass
    return out

STAR_RU = {"Sirius": "Сириус", "Canopus": "Канопус", "Arcturus": "Арктур", "Vega": "Вега", "Capella": "Капелла", "Rigel": "Ригель",
           "Procyon": "Процион", "Betelgeuse": "Бетельгейзе", "Altair": "Альтаир", "Aldebaran": "Альдебаран", "Spica": "Спика",
           "Antares": "Антарес", "Pollux": "Поллукс", "Fomalhaut": "Фомальгаут", "Deneb": "Денеб", "Regulus": "Регул", "Castor": "Кастор",
           "Polaris": "Полярная", "Dubhe": "Дубхе", "Mirfak": "Мирфак", "Algol": "Алголь", "Alpheratz": "Альферац", "Bellatrix": "Беллатрикс",
           "Alnilam": "Альнилам", "Mizar": "Мицар", "Alioth": "Алиот", "Alkaid": "Бенетнаш", "Schedar": "Шедар", "Sadr": "Садр",
           "Albireo": "Альбирео", "Markab": "Маркаб", "Hamal": "Хамаль", "Kochab": "Кохаб", "Elnath": "Эльнат", "Alhena": "Альхена"}

def fixed(ra, dec):
    f = ephem.FixedBody(); f._ra = ra; f._dec = dec; f._epoch = ephem.J2000; return f

def galactic_to_equatorial(l_deg, b_deg=0.0):
    """Галактические -> экваториальные (J2000), рад."""
    a_g, d_g, l_n = math.radians(192.85948), math.radians(27.12825), math.radians(122.93192)
    l, b = math.radians(l_deg), math.radians(b_deg)
    sd = math.sin(d_g) * math.sin(b) + math.cos(d_g) * math.cos(b) * math.cos(l_n - l)
    dec = math.asin(sd)
    y = math.cos(b) * math.sin(l_n - l); x = math.sin(b) * math.cos(d_g) - math.cos(b) * math.sin(d_g) * math.cos(l_n - l)
    return (a_g + math.atan2(y, x)) % (2 * math.pi), dec

@st.cache_data(ttl=900, show_spinner=False)
def sky_snapshot(lat, lon, elev, when_iso, mag_lim=4.5, with_dso=True):
    """Положение звёзд, планет, Луны, Солнца, DSO, галактической плоскости для карты неба."""
    when = datetime.fromisoformat(when_iso); o = mk_obs(lat, lon, elev, when)
    stars = []
    for n, ra, dec, mg in star_catalog():
        if mg <= mag_lim:
            f = fixed(ra, dec); f.compute(o); stars.append({"name": n, "alt": deg(f.alt), "az": deg(f.az), "mag": mg})
    pl = []
    for name, cls in planet_defs():
        b = cls(); b.compute(o); pl.append({"name": name, "alt": deg(b.alt), "az": deg(b.az), "mag": float(b.mag)})
    sun, moon = ephem.Sun(o), ephem.Moon(o)
    d = []
    if with_dso:
        for x in DSO:
            f = fixed(math.radians(x["ra"] * 15), math.radians(x["dec"])); f.compute(o)
            d.append({"id": x["id"], "name": x["name"], "alt": deg(f.alt), "az": deg(f.az), "mag": x["mag"]})
    mw = []
    for l in range(0, 361, 6):
        f = fixed(*galactic_to_equatorial(l)); f.compute(o); mw.append((deg(f.alt), deg(f.az)))
    return {"stars": stars, "planets": pl, "sun": (deg(sun.alt), deg(sun.az)), "moon": (deg(moon.alt), deg(moon.az), float(moon.phase)),
            "dso": d, "mw": mw}

@st.cache_data(ttl=900, show_spinner=False)
def constellations_overhead(lat, lon, elev, when_iso):
    """Какие созвездия сейчас над горизонтом (выборка по сетке alt/az, вес ~ площадь на небе)."""
    when = datetime.fromisoformat(when_iso); o = mk_obs(lat, lon, elev, when); w = {}
    for alt in range(10, 90, 8):
        for az in range(0, 360, 10):
            try:
                ra, dec = o.radec_of(math.radians(az), math.radians(alt))
                c = ephem.constellation((ra, dec), epoch=o.date)[1]
            except Exception:
                continue
            w[c] = w.get(c, 0) + math.cos(math.radians(alt))
    tot = sum(w.values()) or 1
    return sorted(((const_ru(k), v / tot * 100) for k, v in w.items()), key=lambda x: -x[1])

# ── Планировщик объектов глубокого космоса ───────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def dso_night(lat, lon, elev, tzname, date_iso):
    """Для каждого объекта: максимальная высота в тёмное время, время кульминации, часы выше 30°, расстояние до Луны."""
    grid = night_grid(lat, lon, elev, tzname, date_iso, step=20)
    dark = (grid["sun_alt"] < -12).values
    t0 = to_utc_naive(local_noon(date_iso, tzname)); o = mk_obs(lat, lon, elev, t0, pressure=0)
    objs = [(x, fixed(math.radians(x["ra"] * 15), math.radians(x["dec"]))) for x in DSO]
    alt = {x["id"]: [] for x, _ in objs}; sep = {x["id"]: [] for x, _ in objs}; moon = ephem.Moon()
    for t in grid["t"]:
        o.date = ephem.Date(to_utc_naive(t)); moon.compute(o)
        for x, f in objs:
            f.compute(o); alt[x["id"]].append(deg(f.alt)); sep[x["id"]].append(deg(ephem.separation(f, moon)))
    rows = []
    for x, _ in objs:
        a = np.array(alt[x["id"]]); s = np.array(sep[x["id"]])
        if dark.any():
            ad = np.where(dark, a, -90); k = int(ad.argmax())
            rows.append({**x, "max_alt": float(ad[k]), "best_t": grid["t"].iloc[k], "hours30": float(((ad > 30).sum()) * 20 / 60),
                         "moon_sep": float(s[k])})
        else:
            rows.append({**x, "max_alt": float(a.max()), "best_t": grid["t"].iloc[int(a.argmax())], "hours30": 0.0, "moon_sep": float(s[int(a.argmax())])})
    return rows, pd.DataFrame({"t": grid["t"], **{k: v for k, v in alt.items()}})

def limiting_mag(bortle, moon_illum, moon_alt):
    nelm = BORTLE[bortle][1]
    k = 1.8 * (1 - (bortle - 1) / 9 * 0.8)
    pen = k * (moon_illum / 100) * max(0.0, math.sin(math.radians(moon_alt)))
    return max(2.5, nelm - pen)

def dso_visibility(obj, nelm_eff, aperture_mm):
    """Грубая оценка доступности: сравнение блеска (с поправкой на протяжённость) с предельной величиной."""
    lim = nelm_eff + 5 * math.log10(max(aperture_mm, 7) / 7) - 0.3
    t = obj["type"]; pen = 0.0 if t in ("Шаровое скопление", "Рассеянное скопление", "Двойная звезда") else (0.6 if t == "Планетарная туманность" else 1.2)
    margin = lim - (obj["mag"] + pen)
    if margin > 2.5: return "Легко", margin
    if margin > 0.8: return "Хорошо", margin
    if margin > 0: return "На пределе", margin
    return "Не по силам", margin

# ── Метеорные потоки ─────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def meteor_outlook(lat, lon, elev, tzname, date_iso):
    tz = tzinfo(tzname); today = date.fromisoformat(date_iso); out = []
    for s in SHOWERS:
        mm, dd = map(int, s["peak"].split("-")); pk = date(today.year, mm, dd)
        if pk < today: pk = date(today.year + 1, mm, dd)
        t = datetime(pk.year, pk.month, pk.day, 3, tzinfo=tz)         # 03:00 местного — типичный максимум для наблюдателя
        o = mk_obs(lat, lon, elev, to_utc_naive(t)); m = ephem.Moon(o); r = fixed(math.radians(s["ra"] * 15), math.radians(s["dec"])); r.compute(o)
        out.append({**s, "date": pk, "days": (pk - today).days, "moon": float(m.phase), "rad_alt": deg(r.alt),
                    "rad_max": 90 - abs(lat - s["dec"]) if abs(lat - s["dec"]) <= 90 else 0})
    return sorted(out, key=lambda x: x["days"])

# ── Спутники ────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def sat_passes(lat, lon, elev, tzname, tle, start_iso, days=7):
    tz = tzinfo(tzname); start = datetime.fromisoformat(start_iso); end = ephem.Date(start + timedelta(days=days))
    try: sat = ephem.readtle(*tle)
    except Exception: return []
    o = mk_obs(lat, lon, elev, start); out = []
    for _ in range(60):
        try: rt, raz, mt, malt, st_, saz = o.next_pass(sat)
        except Exception: break
        if st_ is None: break
        if rt is None or mt is None:
            o.date = st_ + 5 * ephem.minute; continue
        if rt > end: break
        o2 = mk_obs(lat, lon, elev, ephem.Date(mt).datetime(), pressure=0); sat.compute(o2); sun = ephem.Sun(o2)
        sunlit = not sat.eclipsed; sa = deg(sun.alt)
        if deg(malt) >= 10:
            out.append({"rise": d2l(rt, tz), "max": d2l(mt, tz), "set": d2l(st_, tz), "max_alt": deg(malt), "rise_az": deg(raz),
                        "set_az": deg(saz), "visible": bool(sunlit and sa < -6), "sunlit": bool(sunlit), "sun_alt": sa})
        o.date = st_ + 5 * ephem.minute
    return out

@st.cache_data(ttl=300, show_spinner=False)
def sat_track(tle, start_iso, minutes=95):
    """Подспутниковая трасса на ближайшие `minutes` минут."""
    try: sat = ephem.readtle(*tle)
    except Exception: return []
    start = datetime.fromisoformat(start_iso); pts = []
    for k in range(0, minutes + 1, 1):
        sat.compute(ephem.Date(start + timedelta(minutes=k))); pts.append((deg(sat.sublat), deg(sat.sublong)))
    return pts

# ════════════════════════════════════════════════════════════════
# ОФОРМЛЕНИЕ
# ════════════════════════════════════════════════════════════════
import html as _html
esc = _html.escape

THEMES = {
    "Графит": dict(dark=True, bg="#0E1013", surface="#16191E", sunk="#1C2026", line="#2A2F37", grid="#23272E", text="#E9ECF0", muted="#9BA5B1",
                   accent="#8CC8F0", ink="#8CC8F0", tint="#182733", good="#62B894", warn="#D8A84F", bad="#E37F76", moon_lit="#D7E6F2", moon_dark="#2A3039",
                   colors=["#8CC8F0", "#5B8DB3", "#9BA5B1", "#62B894", "#D8A84F"]),
    "Полночь": dict(dark=True, bg="#080D1A", surface="#0F1730", sunk="#152040", line="#243055", grid="#1B2647", text="#E6ECFA", muted="#98A6C8",
                    accent="#7FB0FF", ink="#8DBBFF", tint="#14224A", good="#63C0A0", warn="#E0B058", bad="#EA8579", moon_lit="#DCE6FA", moon_dark="#1E2848",
                    colors=["#8DBBFF", "#5A82CC", "#98A6C8", "#63C0A0", "#E0B058"]),
    "Аврора": dict(dark=True, bg="#07110F", surface="#0D1B18", sunk="#122622", line="#1F3A34", grid="#17302B", text="#E4F2EE", muted="#8FB0A7",
                   accent="#7ADBC0", ink="#7ADBC0", tint="#10302A", good="#6FD6A8", warn="#D9B35B", bad="#E58A7E", moon_lit="#D6F0E8", moon_dark="#1C312C",
                   colors=["#7ADBC0", "#4E9C88", "#8FB0A7", "#B6A0E6", "#D9B35B"]),
    "Светлая": dict(dark=False, bg="#EDEFF2", surface="#FFFFFF", sunk="#F4F5F7", line="#DDE1E7", grid="#E8EAEE", text="#161C24", muted="#566273",
                    accent="#A8D5F2", ink="#1F6A9B", tint="#E7F3FC", good="#2F7D5C", warn="#9A6B17", bad="#B0453D", moon_lit="#9CCBEA", moon_dark="#DDE1E7",
                    colors=["#1F6A9B", "#A8D5F2", "#566273", "#2F7D5C", "#9A6B17"]),
    "Красная ночь": dict(dark=True, red=True, bg="#0A0303", surface="#140606", sunk="#1C0909", line="#3A1414", grid="#2A0E0E", text="#F06A5E", muted="#CC6258",
                         accent="#B3302A", ink="#FF6B5F", tint="#240A0A", good="#E0675C", warn="#CF4C42", bad="#FF6B5F", moon_lit="#B3302A", moon_dark="#2A0E0E",
                         colors=["#FF6B5F", "#B3302A", "#8A2A25", "#D6584E", "#6B1F1B"]),
}
DEFAULT_THEME = "Графит"

_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html{scroll-behavior:smooth}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important;color:var(--text)!important;
 font-family:'Inter',-apple-system,'Segoe UI',Roboto,sans-serif;font-size:15px;-webkit-font-smoothing:antialiased}
[data-testid="stHeader"]{background:transparent!important;height:0!important}
[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important}
.block-container{max-width:1160px;padding:1.4rem 1rem 4rem!important}
/* — текст: жёстко задаём цвета, чтобы тема Streamlit/браузера не «съедала» контраст — */
.stApp p,.stApp li,.stApp label,.stApp summary,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stWidgetLabel"] *,.stApp [data-testid="stCheckbox"] *,.stApp [data-testid="stToggle"] *{color:var(--text)!important}
.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] *,.stApp small{color:var(--muted)!important}
.stApp [data-testid="stWidgetLabel"] p,.stApp [data-testid="stWidgetLabel"] label{color:var(--muted)!important;font-size:13px!important}
.stApp a{color:var(--ink)!important;text-decoration:none}.stApp a:hover{text-decoration:underline}
.stApp [data-baseweb="select"] *,.stApp input,.stApp textarea{color:var(--text)!important;-webkit-text-fill-color:var(--text)!important}
.stApp input::placeholder,.stApp textarea::placeholder{color:var(--muted)!important;-webkit-text-fill-color:var(--muted)!important;opacity:1}
.stApp [data-baseweb="select"] svg,.stApp [data-testid="stExpander"] svg{fill:var(--muted)!important;color:var(--muted)!important}
[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="base-input"],.stTextInput input,.stNumberInput input,.stDateInput input,.stTimeInput input{
 background:var(--surface)!important;border-color:var(--line)!important;border-radius:10px!important}
[data-baseweb="select"]>div:focus-within,[data-baseweb="input"]:focus-within{border-color:var(--accent)!important}
[data-baseweb="popover"],[data-baseweb="popover"]>div,[data-baseweb="menu"],[data-baseweb="menu"] ul{background:var(--surface)!important;border:1px solid var(--line);border-radius:12px!important}
[data-baseweb="popover"] li,[data-baseweb="menu"] li{background:transparent!important;color:var(--text)!important}
[data-baseweb="popover"] li:hover,[data-baseweb="popover"] li[aria-selected="true"]{background:var(--sunk)!important}
[data-baseweb="popover"] *{color:var(--text)}
[data-baseweb="calendar"],[data-baseweb="calendar"] *{background:var(--surface)!important;color:var(--text)!important}
[data-testid="stNumberInput"] button{background:var(--sunk)!important;color:var(--text)!important;border-color:var(--line)!important}
.stButton>button,.stLinkButton a,[data-testid="stBaseLinkButton-secondary"]{background:var(--surface)!important;border:1px solid var(--line)!important;border-radius:10px!important;font-weight:500;box-shadow:none!important;transition:border-color .2s,transform .2s}
.stButton>button *,.stLinkButton a *{color:var(--text)!important}
.stButton>button:hover,.stLinkButton a:hover{border-color:var(--accent)!important;transform:translateY(-1px)}
[data-testid="stAlert"]{background:var(--surface)!important;border:1px solid var(--line)!important;border-radius:12px!important}
[data-testid="stAlert"] *{color:var(--text)!important}
[data-testid="stSpinner"] *{color:var(--muted)!important}
[data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--line)!important;border-radius:14px!important}
[data-testid="stExpander"] summary p{font-size:14px;font-weight:500}
[data-testid="stSlider"] [role="slider"]{background:var(--ink)!important;border-color:var(--ink)!important}
[data-testid="stSliderThumbValue"]{color:var(--text)!important}
[data-testid="stTickBarMin"],[data-testid="stTickBarMax"]{color:var(--muted)!important}
[data-baseweb="checkbox"]>div:first-child{border-color:var(--line)!important}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;background:transparent!important}.stTabs [aria-selected="true"]{color:var(--text)!important}
.stTabs [data-baseweb="tab-highlight"]{background:var(--ink)!important}.stTabs [data-baseweb="tab-border"]{background:var(--line)!important}
iframe{border:1px solid var(--line)!important;border-radius:14px}
.js-plotly-plot .plotly .modebar{display:none!important}
hr{border-color:var(--line)}
/* — переносы: колонки не сжимаются в «столбик из букв», а переносятся на новую строку — */
[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.75rem!important}
[data-testid="stColumn"],[data-testid="column"]{min-width:min(100%,220px)!important;flex:1 1 220px!important;width:auto!important}
.stApp,.stApp *{word-break:normal!important;overflow-wrap:break-word!important;hyphens:none!important}
.stApp [data-testid="stWidgetLabel"] *,.stApp [data-testid="stCheckbox"] *,.stApp [role="radiogroup"] *,.stApp button *{overflow-wrap:normal!important;word-break:keep-all!important}
/* — типографика и карточки — */
.brand{font-size:15px;font-weight:600;letter-spacing:-.01em}
.stApp .muted,.stApp .note,.stApp .h-sub,.stApp .stat .k,.stApp .stat .s,.stApp .tbl th,.stApp .strip .h .a,.stApp .kv span:first-child{color:var(--muted)!important}
.stApp .kv span.tx{color:var(--text)!important}
.stApp .tw,.stApp .card{color:var(--text)}
.h-sec{font-size:17px;font-weight:600;letter-spacing:-.01em;margin:30px 0 4px}
.h-sub{font-size:13.5px;margin:0 0 12px;line-height:1.5}
.num{font-variant-numeric:tabular-nums}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px 18px;transition:border-color .25s,transform .25s}
.card:hover{border-color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,var(--min,160px)),1fr));gap:10px;margin:0 0 10px}
.stat .k{font-size:12.5px;margin-bottom:6px}.stat .v{font-size:24px;font-weight:500;letter-spacing:-.02em;line-height:1.15;font-variant-numeric:tabular-nums}
.stat .s{font-size:12.5px;margin-top:5px;line-height:1.4}
.hero{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;padding:6px 2px 18px}
.hero .city{font-size:clamp(26px,4vw,38px);font-weight:600;letter-spacing:-.03em;line-height:1.1}
.hero .temp{font-size:clamp(52px,9vw,84px);font-weight:300;letter-spacing:-.05em;line-height:1;font-variant-numeric:tabular-nums}
.verdict{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.verdict .big{font-size:clamp(44px,8vw,64px);font-weight:300;letter-spacing:-.04em;line-height:1;font-variant-numeric:tabular-nums}
.verdict .t{font-size:18px;font-weight:600;letter-spacing:-.01em}
.bar{height:4px;background:var(--line);border-radius:4px;overflow:hidden;margin-top:10px}
.bar>i{display:block;height:100%;background:var(--accent);border-radius:4px;transform-origin:left;animation:grow .9s cubic-bezier(.2,.7,.2,1) .15s both}
.chip{display:inline-flex;align-items:center;gap:7px;padding:3px 11px;border-radius:999px;background:var(--sunk);border:1px solid var(--line);font-size:12.5px;white-space:nowrap}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block}
.note{font-size:12.5px;line-height:1.55;margin-top:8px}
.sep{height:1px;background:var(--line);margin:14px 0}
.kv{display:flex;flex-wrap:wrap;justify-content:space-between;gap:4px 14px;padding:9px 0;border-bottom:1px solid var(--line);font-size:14px}
.kv:last-child{border-bottom:0}.kv span:last-child{font-variant-numeric:tabular-nums;text-align:right;margin-left:auto}
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch;background:var(--surface);border:1px solid var(--line);border-radius:14px}
table.tbl{width:100%;border-collapse:collapse;font-size:13.5px;min-width:560px}
.tbl th{text-align:left;font-weight:500;font-size:12.5px;padding:11px 14px;border-bottom:1px solid var(--line);white-space:nowrap}
.tbl td{padding:11px 14px;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums;white-space:nowrap;transition:background .2s}
.tbl tr:hover td{background:var(--sunk)}.tbl tr:last-child td{border-bottom:0}.tbl td.r,.tbl th.r{text-align:right}
.tbl td.wrap{white-space:normal;min-width:240px;line-height:1.5}
.strip{display:flex;gap:8px;overflow-x:auto;padding-bottom:6px;-webkit-overflow-scrolling:touch}
.strip .h{flex:0 0 auto;min-width:64px;text-align:center;padding:12px 8px;background:var(--surface);border:1px solid var(--line);border-radius:12px;transition:transform .2s,border-color .2s}
.strip .h:hover{transform:translateY(-3px);border-color:var(--accent)}
.strip .h .a{font-size:12.5px}.strip .h .b{font-size:16px;font-weight:500;margin-top:6px}.strip .h .c{font-size:12px;color:var(--ink);margin-top:3px}
.day{display:grid;grid-template-columns:78px 28px minmax(0,1fr) 150px 48px;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid var(--line);font-size:14px}
.day:last-child{border-bottom:0}.day .rng{position:relative;height:4px;background:var(--line);border-radius:4px}
.day .rng i{position:absolute;top:0;bottom:0;background:var(--accent);border-radius:4px}
@media(max-width:600px){.day{grid-template-columns:64px 26px minmax(0,1fr) 44px}.day>span:nth-child(3){display:none}.day .rng{display:none}.block-container{padding:1rem .75rem 3rem!important}}
.ico{width:24px;height:24px;stroke:var(--ink);fill:none;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.step{font-size:34px;font-weight:300;color:var(--ink);letter-spacing:-.03em;line-height:1}
.gl b{display:block;font-weight:600;margin-bottom:6px}
/* — навигация — */
.st-key-mode [role="radiogroup"],.st-key-sub [role="radiogroup"]{flex-wrap:nowrap!important;overflow-x:auto;gap:4px!important;scrollbar-width:none;padding-bottom:2px}
.st-key-mode [role="radiogroup"]::-webkit-scrollbar,.st-key-sub [role="radiogroup"]::-webkit-scrollbar{display:none}
.st-key-mode label[data-baseweb="radio"]>div:first-child,.st-key-sub label[data-baseweb="radio"]>div:first-child,[class*="st-key-chart"] label[data-baseweb="radio"]>div:first-child{display:none!important}
.st-key-mode label[data-baseweb="radio"],[class*="st-key-chart"] label[data-baseweb="radio"]{flex:0 0 auto;padding:7px 15px!important;border-radius:999px;border:1px solid transparent;margin:0!important;white-space:nowrap;cursor:pointer;transition:background .25s,border-color .25s,transform .2s}
.st-key-mode label[data-baseweb="radio"]:hover,[class*="st-key-chart"] label[data-baseweb="radio"]:hover{background:var(--sunk)}
.st-key-mode label[data-baseweb="radio"]:has(input:checked),[class*="st-key-chart"] label[data-baseweb="radio"]:has(input:checked){background:var(--surface);border-color:var(--accent)}
.st-key-sub label[data-baseweb="radio"]{flex:0 0 auto;padding:8px 4px!important;margin:0 14px 0 0!important;border-bottom:2px solid transparent;border-radius:0;white-space:nowrap;cursor:pointer;transition:border-color .25s}
.st-key-sub label[data-baseweb="radio"]:has(input:checked){border-bottom-color:var(--ink)}
.st-key-sub{border-bottom:1px solid var(--line);margin-bottom:6px}
.st-key-mode p,.st-key-sub p,[class*="st-key-chart"] p{font-size:14px!important;white-space:nowrap!important}
/* — анимации — */
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.block-container [data-testid="stElementContainer"],.block-container .element-container{animation:fadeUp .55s cubic-bezier(.2,.7,.2,1) both}
.block-container [data-testid="stElementContainer"]:nth-child(2){animation-delay:.04s}.block-container [data-testid="stElementContainer"]:nth-child(3){animation-delay:.08s}
.block-container [data-testid="stElementContainer"]:nth-child(4){animation-delay:.12s}.block-container [data-testid="stElementContainer"]:nth-child(5){animation-delay:.16s}
.block-container [data-testid="stElementContainer"]:nth-child(6){animation-delay:.2s}.block-container [data-testid="stElementContainer"]:nth-child(7){animation-delay:.24s}
.block-container [data-testid="stElementContainer"]:nth-child(n+8){animation-delay:.28s}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""

def apply_css(t):
    st.markdown(f"""<style>:root{{color-scheme:{'dark' if t['dark'] else 'light'};--bg:{t['bg']};--surface:{t['surface']};--sunk:{t['sunk']};--line:{t['line']};--text:{t['text']};
--muted:{t['muted']};--accent:{t['accent']};--ink:{t['ink']};--tint:{t['tint']};--good:{t['good']};--warn:{t['warn']};--bad:{t['bad']}}}{_CSS}</style>""", unsafe_allow_html=True)

def section(title, sub=""):
    st.markdown(f"<div class='h-sec'>{esc(title)}</div>" + (f"<div class='h-sub'>{sub}</div>" if sub else "<div style='height:8px'></div>"), unsafe_allow_html=True)

def stat(label, value, sub="", color=None):
    c = f" style='color:{color}'" if color else ""
    return f"<div class='card stat'><div class='k'>{label}</div><div class='v'{c}>{value}</div><div class='s'>{sub}</div></div>"

def grid(items, minw=160):
    st.markdown(f"<div class='grid' style='--min:{minw}px'>{''.join(items)}</div>", unsafe_allow_html=True)

def card(html_inner, extra=""):
    st.markdown(f"<div class='card' {extra}>{html_inner}</div>", unsafe_allow_html=True)

def kv_rows(rows):
    return "".join(f"<div class='kv'><span>{k}</span><span>{v}</span></div>" for k, v in rows)

def chip(text, color):
    return f"<span class='chip'><span class='dot' style='background:{color}'></span>{text}</span>"

def table(headers, rows, right=()):
    h = "".join(f"<th class='{'r' if i in right else ''}'>{x}</th>" for i, x in enumerate(headers))
    b = "".join("<tr>" + "".join(f"<td class='{'r' if i in right else ''}'>{c}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    st.markdown(f"<div class='tw'><table class='tbl'><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>", unsafe_allow_html=True)

def note(text): st.markdown(f"<div class='note'>{text}</div>", unsafe_allow_html=True)

def tone(score, t):
    """Цвет по оценке 0–100: приглушённая палитра."""
    return t["good"] if score >= 65 else (t["warn"] if score >= 35 else t["bad"])

def verdict_card(score, title, sub, t, extra=""):
    st.markdown(f"""<div class='card'><div class='verdict'><div class='big'>{score:.0f}</div>
<div><div class='t'>{title}</div><div class='muted' style='font-size:13.5px;margin-top:3px'>{sub}</div></div></div>
<div class='bar'><i style='width:{max(0, min(100, score)):.0f}%;background:{tone(score, t)}'></i></div>{extra}</div>""", unsafe_allow_html=True)

# ── Линейные иконки погоды (SVG, без эмодзи) ───────────────────
_CLOUD = "<path d='M7 18h9.5a4 4 0 0 0 .6-7.95A5.5 5.5 0 0 0 6.5 11.2 3.4 3.4 0 0 0 7 18z'/>"
def wx_icon(code, day=True):
    c = int(code if code is not None else 3)
    if c == 0: body = "<circle cx='12' cy='12' r='4'/>" + "".join(f"<path d='M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4 7 17M17 7l1.4-1.4' />" for _ in range(1)) if day else "<path d='M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z'/>"
    elif c in (1, 2): body = "<circle cx='8' cy='8' r='2.6'/><path d='M8 2.5v1M2.5 8h1M4.1 4.1l.7.7M11.9 4.1l-.7.7'/><g transform='translate(1.5 2)'>" + _CLOUD + "</g>"
    elif c in (45, 48): body = "<path d='M4 8h16M3 12h18M6 16h12M9 20h6'/>"
    elif c in range(51, 68) or c in range(80, 83): body = _CLOUD + "<path d='M8 20l-1 2M12 20l-1 2M16 20l-1 2'/>"
    elif c in range(71, 78) or c in (85, 86): body = _CLOUD + "<path d='M8 21h.01M12 21h.01M16 21h.01M10 23h.01M14 23h.01'/>"
    elif c >= 95: body = _CLOUD + "<path d='M12 14l-2.5 4h3.5l-2 4'/>"
    else: body = _CLOUD
    return f"<svg class='ico' viewBox='0 0 24 24'>{body}</svg>"

# ── Луна: SVG с реальным терминатором ──────────────────────────
def moon_svg(illum, waxing, size=132, north=True, t=None):
    t = t or THEMES[DEFAULT_THEME]
    r = 50; k = max(0.0, min(1.0, illum / 100)); rx = abs(1 - 2 * k) * r
    sweep = 0 if k < 0.5 else 1
    lit = f"M50 0 A{r} {r} 0 0 1 50 100 A{rx:.2f} {r} 0 0 {sweep} 50 0 Z"
    flip = (not waxing) if north else waxing
    tr = "translate(100 0) scale(-1 1)" if flip else ""
    return (f"<svg viewBox='-4 -4 108 108' width='{size}' height='{size}'><circle cx='50' cy='50' r='{r}' fill='{t['moon_dark']}'/>"
            f"<path d='{lit}' fill='{t['moon_lit']}' transform='{tr}'/><circle cx='50' cy='50' r='{r}' fill='none' stroke='{t['line']}' stroke-width='1'/></svg>")

# ── Plotly: единый стиль ───────────────────────────────────────
def style_fig(fig, t, h=280, legend=True, title=None):
    fig.update_layout(
        height=h, margin=dict(l=44, r=14, t=34 if (title or legend) else 14, b=34), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=t["muted"], size=12), hovermode="x unified", colorway=t["colors"],
        title=dict(text=title, x=0, font=dict(size=14, color=t["text"])) if title else None,
        legend=dict(orientation="h", y=1.14, x=0, bgcolor="rgba(0,0,0,0)", font=dict(size=12)) if legend else dict(visible=False),
        hoverlabel=dict(bgcolor=t["surface"], bordercolor=t["line"], font=dict(color=t["text"])))
    fig.update_xaxes(gridcolor=t["grid"], zeroline=False, linecolor=t["line"], showgrid=False)
    fig.update_yaxes(gridcolor=t["grid"], zeroline=False, linecolor="rgba(0,0,0,0)")
    return fig

def show(fig, key=None):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True}, key=key)

# ── Единицы ────────────────────────────────────────────────────
def fp(hpa):
    if hpa is None: return "—"
    return f"{hpa * 0.750062:.0f} мм" if st.session_state.get("unit_p", "мм рт. ст.") == "мм рт. ст." else f"{hpa:.0f} гПа"
def fw(ms):
    if ms is None: return "—"
    return f"{ms * 3.6:.0f} км/ч" if st.session_state.get("unit_w", "м/с") == "км/ч" else f"{ms:.1f} м/с"
def f1(v, unit="", nd=0):
    return "—" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.{nd}f}{unit}"
def wind_txt(deg_):
    return "—" if deg_ is None else f"{compass(deg_ + 0)}"

# ════════════════════════════════════════════════════════════════
# ИНДЕКСЫ И ОЦЕНКИ
# ════════════════════════════════════════════════════════════════
def dewpoint(T, RH):
    if T is None or RH is None or RH <= 0: return None
    a, b = 17.62, 243.12; g = math.log(RH / 100) + a * T / (b + T); return b * g / (a - g)

def storm_index(cape, rh, wmo):
    s = min((cape or 0) / 2500, 1) * 0.65 + max(0, ((rh or 0) - 55) / 45) * 0.15 + (0.2 if (wmo or 0) >= 95 else 0)
    pct = round(s * 100)
    return pct, ("Низкая" if pct < 20 else "Умеренная" if pct < 45 else "Высокая" if pct < 70 else "Очень высокая")

def walk_comfort(feels, wind, precip_prob, wmo, rh):
    s = 100
    if feels is not None:
        s -= 45 if (feels < -15 or feels > 35) else 25 if (feels < -5 or feels > 30) else 10 if (feels < 5 or feels > 27) else 0
    if wind is not None: s -= 30 if wind > 14 else 15 if wind > 9 else 5 if wind > 6 else 0
    if (precip_prob or 0) > 70 or (wmo or 0) in range(60, 100): s -= 35
    elif (precip_prob or 0) > 40: s -= 15
    if (rh or 0) > 92: s -= 8
    s = max(0, min(100, s))
    return s, ("Отлично" if s >= 80 else "Хорошо" if s >= 60 else "Терпимо" if s >= 40 else "Неуютно" if s >= 20 else "Лучше остаться дома")

def clothing(feels, wind, rain):
    if feels is None: return "—"
    s = ("Зимний пуховик, термобельё, шапка, перчатки" if feels < -15 else "Тёплая куртка, свитер, шапка, перчатки" if feels < -5 else
         "Куртка, тёплая кофта, шарф" if feels < 5 else "Лёгкая куртка или плотная толстовка" if feels < 12 else
         "Толстовка или джемпер" if feels < 18 else "Футболка, лёгкие брюки" if feels < 25 else "Лёгкая одежда, головной убор")
    if rain: s += "; зонт или дождевик"
    elif (wind or 0) > 10: s += "; ветровка"
    return s

def uv_text(uv):
    uv = uv or 0
    return "Низкий" if uv < 3 else "Умеренный" if uv < 6 else "Высокий" if uv < 8 else "Очень высокий" if uv < 11 else "Экстремальный"

def aqi_text(v):
    if v is None: return "—", "#999"
    for lim, txt in ((20, "Отличное"), (40, "Хорошее"), (60, "Умеренное"), (80, "Плохое"), (100, "Очень плохое")):
        if v <= lim: return txt, None
    return "Опасное", None

def drone_score(wind, gust, vis_km, pprob, wmo, temp, kp=None, wind120=None):
    s, issues = 100, []
    w = max(wind or 0, wind120 or 0)
    if w > 10: s -= 45; issues.append(f"Сильный ветер {w:.0f} м/с")
    elif w > 7: s -= 22; issues.append(f"Заметный ветер {w:.0f} м/с")
    if (gust or 0) > 12: s -= 20; issues.append(f"Порывы до {gust:.0f} м/с")
    elif (gust or 0) > 9: s -= 8
    if vis_km is not None and vis_km < 1: s -= 50; issues.append("Туман, видимость менее 1 км")
    elif vis_km is not None and vis_km < 3: s -= 20; issues.append("Ограниченная видимость")
    if (wmo or 0) >= 95: s -= 60; issues.append("Гроза")
    elif (wmo or 0) in range(51, 100) or (pprob or 0) > 60: s -= 28; issues.append("Осадки")
    if temp is not None and temp < -10: s -= 22; issues.append("Сильный мороз: аккумулятор быстро теряет ёмкость")
    elif temp is not None and temp < 5: s -= 8; issues.append("Холод: ёмкость батареи ниже номинала")
    if kp is not None and kp >= 5: s -= 20; issues.append(f"Геомагнитная буря (Kp {kp:.0f}): возможны сбои GNSS")
    return max(0, min(100, s)), issues

# ════════════════════════════════════════════════════════════════
# РЕЖИМ «АСТРОНОМИЯ»
# ════════════════════════════════════════════════════════════════
def utcnow(): return datetime.now(timezone.utc).replace(tzinfo=None)

def astro_hourly(ctx, seven, hours=72):
    """Почасовая оценка условий наблюдений: облака по ярусам, прозрачность, seeing, Луна, ветер, роса."""
    H, ni, tz = ctx["hourly"], ctx["ni"], ctx["tz"]; lat, lon, elev, _ = ctx["S"]
    n = len(H["time"]); idx = range(ni, min(ni + hours, n))
    def g(k, i):
        v = H.get(k); return v[i] if v and v[i] is not None else None
    o = mk_obs(lat, lon, elev, utcnow(), pressure=0); sun, moon = ephem.Sun(), ephem.Moon(); rows = []
    s7 = seven if (seven is not None and len(seven)) else None
    for i in idx:
        tl = datetime.fromisoformat(H["time"][i]).replace(tzinfo=tz); tu = to_utc_naive(tl)
        o.date = ephem.Date(tu); sun.compute(o); moon.compute(o)
        low, mid, high, tot = g("cloud_cover_low", i), g("cloud_cover_mid", i), g("cloud_cover_high", i), g("cloud_cover", i)
        if None in (low, mid, high): eff = tot if tot is not None else 50
        else: eff = 100 * (1 - (1 - low / 100) * (1 - mid / 100) * (1 - 0.55 * high / 100))
        T, RH, Td = g("temperature_2m", i), g("relative_humidity_2m", i), g("dew_point_2m", i)
        spread = (T - Td) if (T is not None and Td is not None) else None
        seeing = transp = None
        if s7 is not None:
            d = (s7["time"] - pd.Timestamp(tu, tz="UTC")).abs(); j = int(d.values.argmin())
            if d.iloc[j] <= pd.Timedelta(hours=2): seeing, transp = int(s7["seeing"].iloc[j]), int(s7["transp"].iloc[j])
        clear = 100 - eff
        tr_c = (8 - transp) / 7 * 100 if transp else max(0, 100 - max(0, (RH or 60) - 40) * 1.4)
        se_c = (8 - seeing) / 7 * 100 if seeing else 60
        malt = deg(moon.alt); ill = float(moon.phase)
        moon_c = 100 * (1 - ill / 100 * max(0.0, math.sin(math.radians(malt)))) if malt > 0 else 100
        w = g("wind_speed_10m", i) or 0; wind_c = 100 if w < 4 else max(0, 100 - (w - 4) * 10)
        score = (0.55 * clear + 0.15 * tr_c + 0.12 * se_c + 0.12 * moon_c + 0.06 * wind_c) * min(1, clear / 50)
        rows.append({"t": tl, "sun_alt": deg(sun.alt), "moon_alt": malt, "moon_ill": ill, "cloud": eff, "clear": clear, "rh": RH, "temp": T,
                     "spread": spread, "wind": w, "seeing": seeing, "transp": transp, "tr_c": tr_c, "se_c": se_c, "moon_c": moon_c,
                     "wind_c": wind_c, "score": score})
    return pd.DataFrame(rows)

def verdict_for(score):
    return "Отличные условия" if score >= 75 else "Хорошие условия" if score >= 55 else "Средние условия" if score >= 35 else "Плохие условия"

def body_az_at(ctx, when_local, cls):
    if when_local is None: return None
    lat, lon, elev, _ = ctx["S"]; o = mk_obs(lat, lon, elev, to_utc_naive(when_local)); b = cls(o); return deg(b.az)

def astro_night(ctx):
    """Ночь, к которой относятся расчёты: с 12:00 даты D до 12:00 D+1."""
    now = ctx["now"]; d = now.date() if now.hour >= 12 else now.date() - timedelta(days=1)
    return d.isoformat()

# ── Раздел 1: Сегодня ночью ──────────────────────────────────
def astro_tonight(ctx, th):
    S = ctx["S"]; tz = ctx["tz"]; nd = astro_night(ctx)
    seven = fetch_7timer(S[0], S[1]); df = astro_hourly(ctx, seven)
    ev = sun_moon_events(*S, nd); grid = night_grid(*S, nd)
    lim = -12 if (grid["sun_alt"] < -12).any() else -6
    dk = df[df["sun_alt"] < lim].copy()
    if dk.empty:
        st.info("В ближайшие часы Солнце не опускается достаточно низко (белые ночи или полярный день). Доступны Луна, планеты и яркие звёзды."); return
    dk["night"] = (dk["t"] - timedelta(hours=12)).dt.date
    first = dk["night"].min(); tn = dk[dk["night"] == first]
    roll = tn["score"].rolling(3, min_periods=1).mean(); k = int(roll.values.argmax())
    w0, w1 = tn["t"].iloc[max(0, k - 2)], tn["t"].iloc[k]; best = float(roll.iloc[k]); mean = float(tn["score"].mean())
    sc = best
    moon_i = moon_info(*S, utcnow().replace(microsecond=0).isoformat())
    verdict_card(sc, verdict_for(sc), f"Лучшее окно: {hhmm(w0)}–{hhmm(w1 + timedelta(hours=1))} · в среднем за ночь {mean:.0f} из 100", th)
    b = ctx["bortle"]; nelm = limiting_mag(b, tn["moon_ill"].mean(), float(tn["moon_alt"].clip(lower=0).mean()))
    seeing_v = tn["seeing"].dropna(); tr_v = tn["transp"].dropna()
    items = [stat("Ясность неба", f"{tn['clear'].mean():.0f}%", f"облачность {tn['cloud'].mean():.0f}% (учтены ярусы)"),
             stat("Луна", f"{tn['moon_ill'].mean():.0f}%", "освещённость в среднем за ночь"),
             stat("Предельная звёздная величина", f"{nelm:.1f}", f"Bortle {b}, оценка для невооружённого глаза"),
             stat("Seeing", f"{SEEING_ARCSEC.get(int(round(seeing_v.mean())), '—')}" if len(seeing_v) else "—", "размер звёздного диска (7Timer!)"),
             stat("Прозрачность", f"{TRANSP_TXT.get(int(round(tr_v.mean())), '—')}" if len(tr_v) else f"{tn['tr_c'].mean():.0f}/100", "потеря блеска, зв. вел./воздушная масса" if len(tr_v) else "оценка по влажности")]
    st.markdown(f"<div class='grid' style='--min:180px'>{''.join(items)}</div>", unsafe_allow_html=True)

    section("Ближайшие ночи")
    cards = []
    for nid, g_ in dk.groupby("night"):
        if len(g_) < 3: continue
        r = g_["score"].rolling(3, min_periods=1).mean(); kk = int(r.values.argmax())
        cards.append(stat(["пн","вт","ср","чт","пт","сб","вс"][nid.weekday()] + nid.strftime(" %d.%m"),
                          f"{r.iloc[kk]:.0f}", f"окно {hhmm(g_['t'].iloc[max(0, kk - 2)])}–{hhmm(g_['t'].iloc[kk] + timedelta(hours=1))} · ясно {g_['clear'].mean():.0f}% · Луна {g_['moon_ill'].mean():.0f}%",
                          tone(r.iloc[kk], th)))
    st.markdown(f"<div class='grid' style='--min:200px'>{''.join(cards[:4])}</div>", unsafe_allow_html=True)

    section("Часы ночи", "Чем насыщеннее цвет, тем лучше. Пустые ячейки — день или сумерки.")
    rows = [("Итог", "score"), ("Ясность", "clear"), ("Прозрачность", "tr_c"), ("Seeing", "se_c"), ("Луна (помеха)", "moon_c"), ("Ветер", "wind_c")]
    d3 = df[df["t"] >= ctx["now"] - timedelta(hours=1)].head(60).copy(); night = d3["sun_alt"] < lim
    z = [[(v if nt else None) for v, nt in zip(d3[c], night)] for _, c in rows]
    hov = [[f"{lbl}: {v:.0f}" if nt else "" for v, nt in zip(d3[c], night)] for lbl, c in rows]
    fig = go.Figure(go.Heatmap(z=z, x=[t.strftime("%d.%m %H:%M") for t in d3["t"]], y=[r[0] for r in rows], zmin=0, zmax=100, xgap=2, ygap=2,
                               colorscale=[[0, th["sunk"]], [1, th["ink"]]], showscale=False, text=hov, hoverinfo="text"))
    style_fig(fig, th, 260, legend=False); fig.update_yaxes(autorange="reversed"); fig.update_xaxes(showgrid=False, tickangle=-60, nticks=14)
    show(fig, "heat")

    section("Ключевые времена")
    c1, c2 = st.columns(2)
    with c1:
        card(kv_rows([("Закат", hhmm(ev["sunset"])), ("Конец гражданских сумерек", hhmm(ev["civil_eve"])), ("Конец навигационных сумерек", hhmm(ev["naut_eve"])),
                      ("Начало астрономической ночи", hhmm(ev["astro_eve"]) if ev["astro_eve"] else "нет"),
                      ("Конец астрономической ночи", hhmm(ev["astro_morn"]) if ev["astro_morn"] else "нет"),
                      ("Восход", hhmm(ev["sunrise_next"]))]))
    with c2:
        win = dark_windows(grid, moon_free=True)
        longest = max(win, key=lambda w: (w[1] - w[0]).total_seconds()) if win else None
        nl = ev["night_len"]
        card(kv_rows([("Восход Луны", hhmm(ev["moonrise"])), ("Заход Луны", hhmm(ev["moonset"])),
                      ("Фаза", f"{moon_i['name']}, {moon_i['illum']:.0f}%"),
                      ("Длина астрономической ночи", f"{int(nl.total_seconds() // 3600)} ч {int(nl.total_seconds() % 3600 // 60)} мин" if nl else "нет"),
                      ("Тёмное небо без Луны", f"{hhmm(longest[0])}–{hhmm(longest[1])}" if longest else "нет"),
                      ("Часовой пояс", ctx["tzname"])]))

    section("Практические замечания")
    tips = []
    sp = tn["spread"].dropna()
    if len(sp) and sp.min() < 2.5: tips.append("Высокий риск росы (температура близка к точке росы): подготовьте обогреватель оптики и бленды.")
    if tn["wind"].max() > 7: tips.append(f"Порывистый ветер до {tn['wind'].max():.0f} м/с: возможна тряска монтировки, берите защиту и низкую кратность.")
    if tn["moon_ill"].mean() > 60 and tn["moon_alt"].max() > 10: tips.append(f"Яркая Луна ({tn['moon_ill'].mean():.0f}%): объекты глубокого космоса лучше после захода Луны ({hhmm(ev['moonset'])}); в это время хороши Луна, планеты, двойные звёзды.")
    if len(seeing_v) and seeing_v.mean() <= 3: tips.append("Хороший seeing: удобная ночь для планет и тесных двойных.")
    if tn["temp"].min() is not None and tn["temp"].min() < -15: tips.append("Сильный мороз: держите аккумуляторы в тепле, избегайте резких перепадов температуры оптики.")
    if tn["clear"].mean() < 40: tips.append("Преобладает облачность. Смотрите соседние ночи или карту облаков ниже.")
    if not tips: tips.append("Серьёзных ограничений не видно. Дайте оптике остыть 30–40 минут до начала наблюдений.")
    card("".join(f"<div class='kv'><span class='tx'>{x}</span></div>" for x in tips))
    note("Модель — композиция Open-Meteo (облака по ярусам, влажность, ветер) и 7Timer! (seeing, прозрачность; шаг 3 часа). Это прогноз, он ошибается на 20–30% по времени прояснений.")

    with st.expander("Спутниковая карта облаков (Windy)"):
        components.iframe(f"https://embed.windy.com/embed2.html?lat={S[0]:.3f}&lon={S[1]:.3f}&detailLat={S[0]:.3f}&detailLon={S[1]:.3f}&zoom=6&level=surface&overlay=clouds&product=ecmwf&menu=&message=true&marker=true&calendar=now&type=map&location=coordinates&metricWind=m%2Fs&metricTemp=%C2%B0C", height=420)

# ── Раздел 2: Карта неба ────────────────────────────────────
def sky_figure(snap, th, show_names, show_lines, show_dso, show_mw):
    fig = go.Figure(); bright = th["text"]
    if show_mw:
        xs, ys, seg = [], [], []
        for alt, az in snap["mw"]:
            if alt > 0: xs.append(az); ys.append(90 - alt)
            elif xs: xs.append(None); ys.append(None)
        fig.add_trace(go.Scatterpolar(theta=xs, r=ys, mode="lines", line=dict(color=th["accent"], width=18), opacity=.28, hoverinfo="skip", name="Млечный Путь", connectgaps=False))
    pos = {s["name"]: s for s in snap["stars"]}
    if show_lines:
        tx, rr = [], []
        for pairs in CONST_LINES.values():
            for a, b in pairs:
                if a in pos and b in pos and pos[a]["alt"] > 0 and pos[b]["alt"] > 0:
                    tx += [pos[a]["az"], pos[b]["az"], None]; rr += [90 - pos[a]["alt"], 90 - pos[b]["alt"], None]
        fig.add_trace(go.Scatterpolar(theta=tx, r=rr, mode="lines", line=dict(color=th["muted"], width=1), opacity=.55, hoverinfo="skip", name="Созвездия"))
    st_ = [s for s in snap["stars"] if s["alt"] > 0]
    fig.add_trace(go.Scatterpolar(theta=[s["az"] for s in st_], r=[90 - s["alt"] for s in st_], mode="markers",
        marker=dict(size=[max(2.5, 9 - 1.6 * s["mag"]) for s in st_], color=bright, opacity=.9), name="Звёзды",
        text=[f"{STAR_RU.get(s['name'], s['name'])} · {s['mag']:.1f}ᵐ · выс. {s['alt']:.0f}°" for s in st_], hoverinfo="text"))
    if show_names:
        nm = [s for s in st_ if s["mag"] < 1.6]
        fig.add_trace(go.Scatterpolar(theta=[s["az"] for s in nm], r=[90 - s["alt"] for s in nm], mode="text", text=[STAR_RU.get(s["name"], s["name"]) for s in nm],
                                      textposition="top right", textfont=dict(size=11, color=th["muted"]), hoverinfo="skip", showlegend=False))
    if show_dso:
        dd = [d for d in snap["dso"] if d["alt"] > 0 and d["mag"] < 7.5]
        fig.add_trace(go.Scatterpolar(theta=[d["az"] for d in dd], r=[90 - d["alt"] for d in dd], mode="markers+text", text=[d["id"] if d["id"].startswith("M") else "" for d in dd],
            textposition="bottom center", textfont=dict(size=10, color=th["ink"]), marker=dict(symbol="diamond-open", size=8, color=th["ink"]), name="Объекты Мессье / NGC",
            hovertext=[f"{d['id']} {d['name']} · {d['mag']:.1f}ᵐ" for d in dd], hoverinfo="text"))
    pl = [p for p in snap["planets"] if p["alt"] > 0]
    if pl: fig.add_trace(go.Scatterpolar(theta=[p["az"] for p in pl], r=[90 - p["alt"] for p in pl], mode="markers+text", text=[p["name"] for p in pl],
        textposition="top center", textfont=dict(size=11, color=th["ink"]), marker=dict(size=11, color=th["ink"], line=dict(color=th["surface"], width=1.5)), name="Планеты",
        hovertext=[f"{p['name']} · {p['mag']:.1f}ᵐ · выс. {p['alt']:.0f}°" for p in pl], hoverinfo="text"))
    ma, mz, mi = snap["moon"]
    if ma > 0: fig.add_trace(go.Scatterpolar(theta=[mz], r=[90 - ma], mode="markers+text", text=["Луна"], textposition="top center", textfont=dict(size=11, color=th["text"]),
        marker=dict(size=20, color=th["surface"], line=dict(color=th["ink"], width=2)), name="Луна", hovertext=[f"Луна · {mi:.0f}% · выс. {ma:.0f}°"], hoverinfo="text"))
    sa, sz = snap["sun"]
    if sa > 0: fig.add_trace(go.Scatterpolar(theta=[sz], r=[90 - sa], mode="markers+text", text=["Солнце"], textposition="top center", textfont=dict(size=11, color=th["warn"]),
        marker=dict(size=20, color=th["warn"]), name="Солнце", hoverinfo="skip"))
    fig.update_layout(height=560, margin=dict(l=24, r=24, t=14, b=14), paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color=th["muted"], size=12), showlegend=False,
        polar=dict(bgcolor=th["surface"], radialaxis=dict(range=[0, 90], tickvals=[0, 30, 60, 90], ticktext=["горизонт", "30°", "60°", "зенит"], gridcolor=th["line"], linecolor=th["line"], angle=90, tickfont=dict(size=10)),
                   angularaxis=dict(rotation=90, direction="counterclockwise", tickvals=[0, 90, 180, 270], ticktext=["С", "В", "Ю", "З"], gridcolor=th["line"], linecolor=th["line"], tickfont=dict(size=13, color=th["text"]))))
    return fig

def astro_sky(ctx, th):
    S = ctx["S"]; tz = ctx["tz"]; now = ctx["now"]
    c1, c2 = st.columns(2)
    with c1: d = st.date_input("Дата", value=now.date(), key="sky_d")
    with c2:
        opts = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
        cur = f"{now.hour:02d}:{30 if now.minute >= 30 else 0:02d}"; tm = st.selectbox("Время", opts, index=opts.index(cur), key="sky_t")
    layers = st.multiselect("Слои на карте", ["Имена звёзд", "Линии созвездий", "Объекты Мессье", "Млечный Путь"], default=["Имена звёзд", "Линии созвездий", "Объекты Мессье", "Млечный Путь"], key="sky_layers")
    sn, sl, sd, sm = ("Имена звёзд" in layers, "Линии созвездий" in layers, "Объекты Мессье" in layers, "Млечный Путь" in layers)
    hh, mm = map(int, tm.split(":")); when = datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz)
    snap = sky_snapshot(S[0], S[1], S[2], to_utc_naive(when).isoformat(), 5.0, True)
    if not EPHEM_OK: return
    show(sky_figure(snap, th, sn, sl, sd, sm), "skyfig")
    note(f"Вид вверх: север сверху, восток слева (как на небе). Центр — зенит, край — горизонт. Время {when.strftime('%d.%m.%Y %H:%M')} ({ctx['tzname']}).")
    section("Созвездия над горизонтом", "Доля видимого неба, которую занимает созвездие")
    cons = constellations_overhead(S[0], S[1], S[2], to_utc_naive(when).isoformat())[:12]
    rows = "".join(f"<div class='kv'><span class='tx'>{n}</span><span>{p:.0f}%<div class='bar' style='width:90px;margin:5px 0 0 auto'><i style='width:{min(100, p * 4):.0f}%'></i></div></span></div>" for n, p in cons)
    c1, c2 = st.columns(2)
    half = (len(cons) + 1) // 2
    for col, part in ((c1, cons[:half]), (c2, cons[half:])):
        with col:
            card("".join(f"<div class='kv'><span class='tx'>{n}</span><span class='muted'>{p:.0f}%</span></div>" for n, p in part))
    with st.expander("Интерактивная карта Stellarium Web"):
        components.iframe(f"https://stellarium-web.org/?lat={S[0]:.4f}&lng={S[1]:.4f}&elev={S[2]:.0f}&date={to_utc_naive(when).strftime('%Y-%m-%dT%H:%M:%SZ')}", height=520)
        note("Если карта не загрузилась, сервис мог запретить встраивание — откройте stellarium-web.org в отдельной вкладке.")

# ── Раздел 3: Солнце и Луна ─────────────────────────────────
def astro_sun_moon(ctx, th):
    S = ctx["S"]; tz = ctx["tz"]; nd = astro_night(ctx)
    ev = sun_moon_events(*S, nd); grid = night_grid(*S, nd)
    mi = moon_info(*S, utcnow().replace(microsecond=0).isoformat())
    c1, c2 = st.columns([1, 1.6])
    with c1:
        st.markdown(f"<div class='card' style='text-align:center'>{moon_svg(mi['illum'], mi['waxing'], 150, ctx['lat'] >= 0, th)}"
                    f"<div class='v' style='font-size:22px;font-weight:500;margin-top:8px'>{mi['name']}</div>"
                    f"<div class='muted'>освещено {mi['illum']:.0f}% · возраст {mi['age']:.1f} сут</div></div>", unsafe_allow_html=True)
    with c2:
        card(kv_rows([("Сейчас", f"высота {mi['alt']:.0f}°, азимут {mi['az']:.0f}° ({compass(mi['az'])})"), ("Созвездие", const_ru(mi["const"])),
                      ("Расстояние", f"{mi['dist_km']:,.0f} км".replace(",", " ")), ("Угловой диаметр", f"{mi['size'] / 60:.1f}′"),
                      ("Колонгитуда", f"{mi['colong']:.1f}° (положение терминатора)"), ("Либрация", f"широта {mi['lib_lat']:+.1f}°, долгота {mi['lib_lon']:+.1f}°"),
                      ("Восход / заход", f"{hhmm(ev['moonrise'])} / {hhmm(ev['moonset'])}")]))
    section("Ближайшие фазы")
    grid_items = [stat("Новолуние", hhmm(mi["new"], "%d.%m %H:%M")), stat("Первая четверть", hhmm(mi["first"], "%d.%m %H:%M")),
                  stat("Полнолуние", hhmm(mi["full"], "%d.%m %H:%M")), stat("Последняя четверть", hhmm(mi["last"], "%d.%m %H:%M"))]
    st.markdown(f"<div class='grid' style='--min:150px'>{''.join(grid_items)}</div>", unsafe_allow_html=True)
    note("Супер-Луна: расстояние в перигее около 357 000 км, в апогее около 406 000 км. Сравните с текущим значением выше.")

    mm_ = moon_month(ctx["tzname"], nd)
    fig = go.Figure(go.Bar(x=[d for d, _ in mm_], y=[v for _, v in mm_], marker_color=th["accent"], hovertemplate="%{x|%d.%m}: %{y:.0f}%<extra></extra>"))
    style_fig(fig, th, 200, legend=False, title="Освещённость Луны на месяц вперёд, %"); fig.update_yaxes(range=[0, 100]); show(fig, "moonm")

    section("Солнце", "Данные для вечера выбранной даты")
    az_r = body_az_at(ctx, ev["sunrise"], ephem.Sun); az_s = body_az_at(ctx, ev["sunset"], ephem.Sun)
    dl = ev["day_len"]
    items = [stat("Восход", hhmm(ev["sunrise"]), f"азимут {az_r:.0f}° ({compass(az_r)})" if az_r is not None else ""),
             stat("Полдень", hhmm(ev["noon"]), f"высота {ev['noon_alt']:.0f}°" if ev.get("noon_alt") is not None else ""),
             stat("Закат", hhmm(ev["sunset"]), f"азимут {az_s:.0f}° ({compass(az_s)})" if az_s is not None else ""),
             stat("Длина дня", f"{int(dl.total_seconds() // 3600)} ч {int(dl.total_seconds() % 3600 // 60)} мин" if dl else "—", "")]
    st.markdown(f"<div class='grid' style='--min:160px'>{''.join(items)}</div>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grid["t"], y=grid["sun_alt"], name="Солнце", line=dict(color=th["warn"], width=2)))
    fig.add_trace(go.Scatter(x=grid["t"], y=grid["moon_alt"], name="Луна", line=dict(color=th["ink"], width=2)))
    for y_, lbl in ((-6, "гражданские"), (-12, "навигационные"), (-18, "астрономические")):
        fig.add_hline(y=y_, line=dict(color=th["line"], width=1, dash="dot"), annotation_text=lbl, annotation_font_size=10, annotation_position="bottom left")
    fig.add_hline(y=0, line=dict(color=th["muted"], width=1))
    style_fig(fig, th, 300, title="Высота над горизонтом, °  (с полудня до полудня)"); show(fig, "sunmoon")

# ── Раздел 4: Планеты ───────────────────────────────────────
def astro_planets(ctx, th):
    S = ctx["S"]; nd = astro_night(ctx); tz = ctx["tz"]
    rows, alts = planets_info(*S, nd, utcnow().replace(minute=0, second=0, microsecond=0).isoformat())
    section("Планеты сейчас", "Высота и азимут — на текущий момент; видимость — для ночи, начинающейся вечером этой даты")
    tr = []
    for r in rows:
        el = r["elong"]; side = "восточнее" if el > 0 else "западнее"
        hint = "противостояние" if abs(el) > 172 else ("у Солнца" if abs(el) < 15 else "")
        tr.append([f"<b>{r['name']}</b>", const_ru(r["const"]), f"{r['mag']:+.1f}ᵐ", f"{abs(el):.0f}° {side}" + (f" · {hint}" if hint else ""),
                   f"{r['phase']:.0f}%", f"{r['dist']:.2f} а.е.", f"{r['size']:.1f}″", f"{hhmm(r['rise'])} / {hhmm(r['transit'])} / {hhmm(r['set'])}",
                   f"{r['alt']:.0f}° / {r['az']:.0f}° {compass(r['az'])}", r["vis"]])
    table(["Планета", "Созвездие", "Блеск", "Элонгация", "Фаза", "Расстояние", "Диаметр", "Восход / кульм. / заход", "Сейчас: выс. / аз.", "Видимость"], tr)
    fig = go.Figure()
    cols = th["colors"] + ["#8A94A3", "#C9B27A", "#7AA6C9"]
    for i, (name, _) in enumerate(planet_defs()):
        fig.add_trace(go.Scatter(x=alts["t"], y=alts[name], name=name, mode="lines", line=dict(width=2, color=cols[i % len(cols)])))
    fig.add_hline(y=0, line=dict(color=th["muted"], width=1)); style_fig(fig, th, 320, title="Высота планет за ночь, °")
    fig.update_yaxes(range=[-10, 90]); show(fig, "planalt")
    note("Элонгация — угловое расстояние от Солнца. Меркурий и Венера лучше видны при большой элонгации; внешние планеты ярче всего в противостоянии (≈180°).")

# ── Раздел 5: Глубокий космос ───────────────────────────────
def astro_dso(ctx, th):
    S = ctx["S"]; nd = astro_night(ctx); tz = ctx["tz"]
    rows, alts = dso_night(*S, nd)
    mi = moon_info(*S, utcnow().replace(microsecond=0).isoformat())
    c1, c2, c3, c4 = st.columns(4)
    ap = c1.number_input("Апертура, мм", 30, 600, int(ctx["aperture"]), 10, key="ap_dso")
    minalt = c2.slider("Мин. высота, °", 10, 60, 30, key="dso_minalt")
    types = sorted({r["type"] for r in rows}); sel_t = c3.multiselect("Тип", types, default=[], placeholder="Все типы", key="dso_types")
    only_vis = c4.toggle("Только доступные", True, key="dso_vis")
    nelm = limiting_mag(ctx["bortle"], mi["illum"], max(mi["alt"], 0))
    out = []
    for r in rows:
        if sel_t and r["type"] not in sel_t: continue
        if r["max_alt"] < minalt: continue
        vis, margin = dso_visibility(r, nelm, ap)
        if only_vis and vis == "Не по силам": continue
        penalty = 0 if r["moon_sep"] > 40 else (40 - r["moon_sep"]) / 2
        r2 = {**r, "vis": vis, "margin": margin, "rank": margin * 10 + r["max_alt"] * 0.4 - penalty}; out.append(r2)
    out.sort(key=lambda x: -x["rank"])
    section("Что смотреть сегодня ночью", f"Сортировка по доступности, высоте и расстоянию от Луны · предельная величина глаза {nelm:.1f}ᵐ (Bortle {ctx['bortle']}) · апертура {ap} мм")
    if not out: st.info("Под эти условия ничего не подходит — уменьшите минимальную высоту или снимите фильтры."); return
    tr = [[f"<b>{r['id']}</b>", r["name"], r["type"], f"{r['mag']:.1f}ᵐ", r["size"] + "′", f"{r['max_alt']:.0f}° в {hhmm(r['best_t'])}", f"{r['hours30']:.1f} ч", f"{r['moon_sep']:.0f}°", r["vis"]] for r in out[:40]]
    table(["Объект", "Название", "Тип", "Блеск", "Размер", "Макс. высота", "Выше 30°", "От Луны", "Доступность"], tr)
    pick = st.multiselect("График высоты", [f"{r['id']} · {r['name']}" for r in out], default=[f"{r['id']} · {r['name']}" for r in out[:4]], key="dso_pick")
    if pick:
        fig = go.Figure(); dark = night_grid(*S, nd)
        for p in pick:
            oid = p.split(" · ")[0]
            if oid in alts: fig.add_trace(go.Scatter(x=alts["t"], y=alts[oid], name=oid, mode="lines", line=dict(width=2)))
        fig.add_trace(go.Scatter(x=dark["t"], y=dark["moon_alt"], name="Луна", line=dict(color=th["muted"], width=1.5, dash="dot")))
        for a, b in dark_windows(dark, False, -18): fig.add_vrect(x0=a, x1=b, fillcolor=th["tint"], opacity=.7, line_width=0, layer="below")
        fig.add_hline(y=30, line=dict(color=th["line"], dash="dot")); style_fig(fig, th, 320, title="Высота над горизонтом, °  (заливка — астрономическая ночь)"); fig.update_yaxes(range=[0, 90]); show(fig, "dsoalt")
    note("Оценка доступности приблизительна: она сравнивает блеск объекта (с поправкой на протяжённость) с предельной величиной. Для слабых протяжённых галактик важнее тёмное небо, чем апертура.")

# ── Раздел 6: Спутники ──────────────────────────────────────
def astro_sats(ctx, th):
    S = ctx["S"]; tz = ctx["tz"]
    name = st.radio("Объект", list(SATS), horizontal=True, label_visibility="collapsed", key="sat_sel")
    tle = fetch_tle(SATS[name])
    if not tle: st.warning("Не удалось получить орбитальные элементы (CelesTrak). Попробуйте позже."); return
    now_iso = utcnow().replace(microsecond=0).isoformat()
    ps = sat_passes(*S, tuple(tle), now_iso, 7)
    section("Ближайшие пролёты (7 дней)", "Высота максимума не ниже 10°. «Виден» — объект освещён Солнцем, а небо тёмное (Солнце ниже −6°).")
    if not ps: st.info("Пролётов с высотой более 10° в ближайшие 7 дней нет.")
    else:
        tr = []
        for p in ps[:15]:
            dur = (p["set"] - p["rise"]).total_seconds() / 60
            tr.append([p["rise"].strftime("%d.%m"), f"{hhmm(p['rise'])}", f"{hhmm(p['max'])}", f"{hhmm(p['set'])}", f"{p['max_alt']:.0f}°",
                       f"{compass(p['rise_az'])} → {compass(p['set_az'])}", f"{dur:.0f} мин", "Виден" if p["visible"] else ("В тени Земли" if not p["sunlit"] else "Светлое небо")])
        table(["Дата", "Начало", "Максимум", "Конец", "Макс. высота", "Направление", "Длительность", "Видимость"], tr)
    section("Где сейчас")
    track = sat_track(tuple(tle), now_iso, 95)
    if track:
        fig = go.Figure()
        la = [p[0] for p in track]; lo = [p[1] for p in track]
        for i in range(1, len(lo)):
            if abs(lo[i] - lo[i - 1]) > 180: lo[i - 1] = None; la[i - 1] = None
        fig.add_trace(go.Scattergeo(lat=la, lon=lo, mode="lines", line=dict(width=2, color=th["ink"]), name="Трасса 95 мин", hoverinfo="skip"))
        fig.add_trace(go.Scattergeo(lat=[track[0][0]], lon=[track[0][1]], mode="markers", marker=dict(size=11, color=th["ink"]), name=name))
        fig.add_trace(go.Scattergeo(lat=[S[0]], lon=[S[1]], mode="markers", marker=dict(size=9, color=th["warn"], symbol="diamond"), name="Вы"))
        fig.update_layout(height=380, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", showlegend=True, legend=dict(orientation="h", y=0.02, x=0.01, bgcolor="rgba(0,0,0,0)"),
            geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor=th["sunk"], showocean=True, oceancolor=th["surface"], showcountries=True, countrycolor=th["line"], coastlinecolor=th["line"],
                     projection_type="natural earth", lataxis=dict(showgrid=True, gridcolor=th["grid"]), lonaxis=dict(showgrid=True, gridcolor=th["grid"])))
        show(fig, "satmap")
    if SATS[name] == 25544:
        iss = fetch_iss_now()
        if iss:
            grid([stat("Высота орбиты", f"{iss['altitude']:.0f} км"), stat("Скорость", f"{iss['velocity']:,.0f} км/ч".replace(",", " ")),
                  stat("Над точкой", f"{iss['latitude']:.1f}°, {iss['longitude']:.1f}°"), stat("Освещение", {"daylight": "день", "eclipsed": "в тени", "visible": "освещена"}.get(iss["visibility"], iss["visibility"]))], 170)
    note("Орбитальные элементы — CelesTrak (обновляются несколько раз в сутки); расчёт — PyEphem. Точность времени пролёта — единицы секунд на ближайшие дни.")

# ── Раздел 7: События ───────────────────────────────────────
def astro_events(ctx, th):
    S = ctx["S"]; nd = astro_night(ctx)
    section("Метеорные потоки", "Лунная помеха и высота радианта оценены на 03:00 по местному времени в день максимума")
    tr = []
    for m in meteor_outlook(*S, nd)[:6]:
        good = m["moon"] < 35 and m["rad_alt"] > 20
        q, col = ("Хорошие условия", th["good"]) if good else (("Мешает Луна", th["warn"]) if m["moon"] >= 35 else ("Радиант низко", th["warn"]))
        when = "сегодня" if m["days"] == 0 else f"через {m['days']} дн."
        tr.append([f"<b>{m['name']}</b>", m["date"].strftime("%d.%m"), when, f"{m['zhr']}", f"{m['speed']} км/с", f"{m['moon']:.0f}%", f"{m['rad_alt']:.0f}° (макс. {m['rad_max']:.0f}°)", chip(q, col), m["parent"]])
    table(["Поток", "Максимум", "Когда", "ZHR", "Скорость", "Луна в максимуме", "Радиант в 03:00", "Оценка", "Родитель"], tr)
    note("ZHR — идеальная часовая частота при тёмном небе и радианте в зените; реально видно в 3–10 раз меньше. Даты максимумов указаны с точностью ±1 сутки.")
    section("Сближения", "Ближайшие 45 дней, геоцентрические угловые расстояния")
    cj = conjunctions(nd, ctx["tzname"])
    if cj: table(["Дата и время", "Пара", "Расстояние", "Примечание"], [[c["when"].strftime("%d.%m %H:%M"), c["pair"], f"{c['sep']:.1f}°", c["note"]] for c in cj[:14]])
    else: st.info("Тесных сближений на ближайшие 45 дней не найдено.")
    section("Затмения", "Справочный список; точную видимость для вашего места проверяйте по NASA или timeanddate.com")
    today = ctx["now"].date().isoformat()
    ec = [e for e in ECLIPSES if e[0] >= today][:6]
    table(["Дата", "Тип", "Где видно"], [[datetime.fromisoformat(d).strftime("%d.%m.%Y"), t_, r] for d, t_, r in ec])
    c1, c2 = st.columns(2)
    c1.link_button("NASA: затмения", "https://eclipse.gsfc.nasa.gov/", use_container_width=True)
    c2.link_button("timeanddate: астрономия", "https://www.timeanddate.com/astronomy/", use_container_width=True)

# ── Раздел 8: Космическая погода ────────────────────────────
def xray_class(f):
    if f is None or f <= 0: return "—"
    for lim, ch in ((1e-4, "X"), (1e-5, "M"), (1e-6, "C"), (1e-7, "B"), (0, "A")):
        if f >= lim or ch == "A":
            base = {"X": 1e-4, "M": 1e-5, "C": 1e-6, "B": 1e-7, "A": 1e-8}[ch]; return f"{ch}{f / base:.1f}"

def geomag_lat(lat, lon):
    plat, plon = math.radians(80.65), math.radians(-72.68); la, lo = math.radians(lat), math.radians(lon)
    return math.degrees(math.asin(math.sin(la) * math.sin(plat) + math.cos(la) * math.cos(plat) * math.cos(lo - plon)))

def astro_space(ctx, th):
    S = ctx["S"]; sw = fetch_space_weather()
    if not any(v is not None for v in sw.values()): st.warning("NOAA SWPC сейчас недоступен."); return
    kp = sw["kp"]; kp_now = float(kp["Kp"].iloc[-1]) if kp is not None and len(kp) else None
    gscale = "—" if kp_now is None else ("G0" if kp_now < 5 else f"G{min(5, int(kp_now) - 4)}")
    sp = sw["plasma"]; speed = float(sp["speed"].dropna().iloc[-1]) if sp is not None and sp["speed"].notna().any() else None
    dens = float(sp["density"].dropna().iloc[-1]) if sp is not None and sp["density"].notna().any() else None
    mg = sw["mag"]; bz = float(mg["bz_gsm"].dropna().iloc[-1]) if mg is not None and mg["bz_gsm"].notna().any() else None
    xr = sw["xray"]; xf = float(xr["flux"].iloc[-1]) if xr is not None and len(xr) else None
    gm = geomag_lat(S[0], S[1]); prob = aurora_probability(S[0], S[1])
    kreq = max(0.0, (66.5 - gm) / 2.1)
    section("Космическая погода", "NOAA SWPC · обновление каждые 5–10 минут")
    grid([stat("Индекс Kp", f"{kp_now:.1f}" if kp_now is not None else "—", f"геомагнитная шкала {gscale}"),
          stat("Скорость солнечного ветра", f"{speed:.0f} км/с" if speed else "—", "обычно 300–450; выше 600 — возмущение"),
          stat("Bz (поле IMF)", f"{bz:+.1f} нТл" if bz is not None else "—", "южное направление (минус) усиливает бури"),
          stat("Плотность ветра", f"{dens:.1f} см⁻³" if dens else "—", ""),
          stat("Рентген Солнца", xray_class(xf), "класс вспышки GOES (0.1–0.8 нм)"),
          stat("Радиоиндекс F10.7", f"{sw['f107']:.0f}" if sw.get("f107") else "—", "индикатор солнечной активности")], 170)
    section("Полярное сияние в вашей точке")
    grid([stat("Вероятность (OVATION)", f"{prob:.0f}%" if prob is not None else "—", "по модели NOAA на ближайший час"),
          stat("Геомагнитная широта", f"{gm:.1f}°", "для вашей точки"),
          stat("Нужный Kp (оценка)", f"≈ {kreq:.0f}" if kreq > 0 else "любой", "для сияния у горизонта при ясном небе")], 200)
    if kp is not None and len(kp) > 0:
        k = kp.tail(56)
        fig = go.Figure(go.Bar(x=k["time_tag"], y=k["Kp"], marker_color=[th["ink"] if v >= 5 else th["accent"] for v in k["Kp"]], hovertemplate="%{x|%d.%m %H:%M} UTC: Kp %{y:.1f}<extra></extra>"))
        fc = sw.get("kp_fc")
        if fc is not None and len(fc): 
            fut = fc[fc["time_tag"] > k["time_tag"].max()]
            fig.add_trace(go.Bar(x=fut["time_tag"], y=fut["kp"], marker_color=th["line"], name="Прогноз", hovertemplate="%{x|%d.%m %H:%M} UTC: Kp %{y:.1f} (прогноз)<extra></extra>"))
        fig.add_hline(y=5, line=dict(color=th["warn"], dash="dot"), annotation_text="буря G1", annotation_font_size=10)
        style_fig(fig, th, 240, legend=False, title="Kp: последние 7 суток и прогноз (UTC)"); fig.update_yaxes(range=[0, 9]); show(fig, "kp")
    if sp is not None and len(sp):
        s2 = sp.dropna(subset=["speed"]).iloc[::5]
        fig = go.Figure(go.Scatter(x=s2["time_tag"], y=s2["speed"], line=dict(color=th["ink"], width=1.8), name="км/с"))
        style_fig(fig, th, 220, legend=False, title="Скорость солнечного ветра за сутки, км/с (UTC)"); show(fig, "sw")
    c1, c2 = st.columns(2)
    c1.link_button("SpaceWeatherLive", "https://www.spaceweatherlive.com/", use_container_width=True)
    c2.link_button("NOAA SWPC", "https://www.swpc.noaa.gov/", use_container_width=True)

# ── Раздел 9: Инструменты ───────────────────────────────────
def astro_tools(ctx, th):
    S = ctx["S"]; tz = ctx["tz"]; now_u = utcnow()
    o = mk_obs(S[0], S[1], S[2], now_u); lst = str(o.sidereal_time()).split(".")[0]
    section("Время")
    grid([stat("Местное время", ctx["now"].strftime("%H:%M:%S"), ctx["tzname"]), stat("UTC", now_u.strftime("%H:%M:%S"), now_u.strftime("%d.%m.%Y")),
          stat("Юлианская дата", f"{float(ephem.julian_date(now_u)):.4f}", "JD"), stat("Местное звёздное время", lst, "часы:минуты:секунды")], 170)
    section("Астрофото: выдержка без трекера", "Правило NPF точнее старого «правила 500»")
    c1, c2, c3, c4 = st.columns(4)
    fl = c1.number_input("Фокусное, мм", 8, 800, 24, key="t_fl"); fn = c2.number_input("Диафрагма f/", 0.95, 22.0, 2.8, 0.1, key="t_fn")
    px = c3.number_input("Пиксель, мкм", 1.0, 10.0, 4.3, 0.1, key="t_px"); crop = c4.number_input("Кроп-фактор", 1.0, 3.0, 1.0, 0.1, key="t_crop")
    npf = (35 * fn + 30 * px) / fl
    grid([stat("Выдержка NPF", f"{npf:.1f} с", "звёзды без заметного следа у экватора"), stat("Правило 500", f"{500 / (fl * crop):.1f} с", "для сравнения, завышает"),
          stat("Масштаб кадра", f"{206.265 * px / fl:.2f}″/px", "угловой размер пикселя")], 190)
    section("Поле зрения камеры")
    sens = {"Полный кадр 36×24": (36, 24), "APS-C 23.5×15.6": (23.5, 15.6), "APS-C Canon 22.3×14.9": (22.3, 14.9), "Micro 4/3 17.3×13": (17.3, 13), "1″ 13.2×8.8": (13.2, 8.8)}
    c1, c2 = st.columns(2); sn = c1.selectbox("Матрица", list(sens), key="t_sens"); fl2 = c2.number_input("Фокусное, мм ", 8, 4000, 200, key="t_fl2")
    w, h = sens[sn]; fw_, fh_ = math.degrees(2 * math.atan(w / 2 / fl2)), math.degrees(2 * math.atan(h / 2 / fl2))
    grid([stat("Поле зрения", f"{fw_:.2f}° × {fh_:.2f}°", ""), stat("Для сравнения", "Луна 0.5°, M31 3°×1°", "Плеяды 2°, туманность Ориона 1°")], 220)
    section("Телескоп")
    c1, c2, c3, c4 = st.columns(4)
    D = c1.number_input("Апертура, мм", 30, 1000, int(ctx["aperture"]), 10, key="t_D"); F = c2.number_input("Фокусное, мм  ", 100, 5000, 600, 50, key="t_F")
    ep = c3.number_input("Окуляр, мм", 2.0, 50.0, 10.0, 0.5, key="t_ep"); afov = c4.number_input("Поле окуляра, °", 40, 100, 52, key="t_afov")
    M = F / ep
    grid([stat("Светосила", f"f/{F / D:.1f}", ""), stat("Предел разрешения", f"{116 / D:.2f}″", "по Доусу"), stat("Предельная звёздная величина", f"{2.7 + 5 * math.log10(D):.1f}ᵐ", "оценка для звёзд"),
          stat("Собирает света", f"{(D / 7) ** 2:,.0f}×".replace(",", " "), "относительно глаза"), stat("Увеличение", f"{M:.0f}×", f"макс. полезное ≈ {2 * D}×, мин. ≈ {D / 7:.0f}×"),
          stat("Поле зрения", f"{afov / M:.2f}°", ""), stat("Выходной зрачок", f"{D / M:.1f} мм", "оптимум 2–5 мм")], 180)
    section("Млечный Путь")
    nd = astro_night(ctx); grid_ = night_grid(*S, nd, 20); o2 = mk_obs(S[0], S[1], S[2], to_utc_naive(grid_["t"].iloc[0]), pressure=0)
    gc = fixed(math.radians(17.7611 * 15), math.radians(-29.0078)); al = []
    for t_ in grid_["t"]: o2.date = ephem.Date(to_utc_naive(t_)); gc.compute(o2); al.append(deg(gc.alt))
    al = np.array(al); dk = (grid_["sun_alt"] < -18).values
    mx = float(al[dk].max()) if dk.any() else float(al.max()); culm = 90 - abs(S[0] + 29.0)
    grid([stat("Центр Галактики", f"до {mx:.0f}° сегодня ночью", f"максимальная высота в год — {max(culm, 0):.0f}°"),
          stat("Лучший сезон ядра", "июнь — август" if S[0] > 0 else "апрель — сентябрь", "ядро в Стрельце; чем южнее, тем выше")], 240)
    if culm < 15: note("На вашей широте центр Галактики поднимается очень низко. Для съёмки ядра лучше южнее; летом хороши лебединая и кассиопейная части Млечного Пути.")
    section("Тёмное небо и атмосфера")
    c1, c2, c3 = st.columns(3)
    c1.link_button("Карта световых загрязнений", f"https://www.lightpollutionmap.info/#zoom=9&lat={S[0]:.4f}&lon={S[1]:.4f}", use_container_width=True)
    c2.link_button("Clear Outside", f"https://clearoutside.com/forecast/{S[0]:.2f}/{S[1]:.2f}", use_container_width=True)
    c3.link_button("Astrospheric", "https://www.astrospheric.com/", use_container_width=True)
    ap = fetch_apod()
    if ap and ap.get("url"):
        section("Снимок дня NASA (APOD)")
        c1, c2 = st.columns([1.4, 1])
        with c1:
            if ap.get("media_type") == "image": st.image(ap["url"], use_container_width=True)
            else: st.link_button("Открыть видео", ap["url"])
        with c2:
            card(f"<div class='v' style='font-size:18px'>{esc(ap.get('title', ''))}</div><div class='muted' style='margin-top:6px'>{esc(ap.get('date', ''))}"
                 f"{' · © ' + esc(ap['copyright'].strip()) if ap.get('copyright') else ''}</div><div class='note'>Описание на английском — на странице NASA.</div>")
            st.link_button("Страница APOD", "https://apod.nasa.gov/apod/astropix.html", use_container_width=True)

ASTRO_SECTIONS = {"Сегодня ночью": astro_tonight, "Карта неба": astro_sky, "Солнце и Луна": astro_sun_moon, "Планеты": astro_planets,
                  "Глубокий космос": astro_dso, "Спутники": astro_sats, "События": astro_events, "Космос и Солнце": astro_space, "Инструменты": astro_tools}

def mode_astro(ctx, th):
    if not EPHEM_OK:
        st.error("Для астрономии нужна библиотека ephem: pip install ephem"); return
    sub = st.radio("Раздел", list(ASTRO_SECTIONS), horizontal=True, label_visibility="collapsed", key="sub")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    with st.container(key=f"s{list(ASTRO_SECTIONS).index(sub)}"):
        ASTRO_SECTIONS[sub](ctx, th)

# ════════════════════════════════════════════════════════════════
# ПОДГОТОВКА ПРОГНОЗА
# ════════════════════════════════════════════════════════════════
def prepare(data):
    """Нарезка прогноза с начала сегодняшних суток; индекс текущего часа; тренд давления."""
    H, D, cur = data["hourly"], data["daily"], data["current"]
    times = H["time"]; today = cur["time"][:10]; hk = cur["time"][:13] + ":00"
    full_ni = times.index(hk) if hk in times else 0
    start = next((i for i, t in enumerate(times) if t.startswith(today)), 0)
    hourly = {k: v[start:] for k, v in H.items()}
    d0 = next((i for i, t in enumerate(D["time"]) if t == today), 0)
    daily = {k: v[d0:] for k, v in D.items()}
    p = H.get("surface_pressure") or []
    trend = (p[full_ni] - p[full_ni - 3]) if (len(p) > full_ni and full_ni >= 3 and p[full_ni] is not None and p[full_ni - 3] is not None) else None
    return hourly, daily, full_ni - start, trend

def hv(ctx, key, off=0):
    v = ctx["hourly"].get(key); i = ctx["ni"] + off
    return v[i] if v and 0 <= i < len(v) else None

def local_now(tzname): return datetime.now(tzinfo(tzname))

# ════════════════════════════════════════════════════════════════
# РЕЖИМ «ОБЗОР»
# ════════════════════════════════════════════════════════════════
def day_label(i, iso):
    d = date.fromisoformat(iso); return "Сегодня" if i == 0 else "Завтра" if i == 1 else ["пн", "вт", "ср", "чт", "пт", "сб", "вс"][d.weekday()] + d.strftime(" %d.%m")

def mode_overview(ctx, th, extra):
    cur, daily, H, ni = ctx["cur"], ctx["daily"], ctx["hourly"], ctx["ni"]
    T, FL, RH = cur.get("temperature_2m"), cur.get("apparent_temperature"), cur.get("relative_humidity_2m")
    wmo = cur.get("weather_code", 0); wind = cur.get("wind_speed_10m"); gust = cur.get("wind_gusts_10m"); wd = cur.get("wind_direction_10m")
    P = cur.get("surface_pressure"); cloud = cur.get("cloud_cover"); pp = hv(ctx, "precipitation_probability"); uv = hv(ctx, "uv_index"); vis = hv(ctx, "visibility")
    dew = hv(ctx, "dew_point_2m"); cape = hv(ctx, "cape") or 0; trend = ctx["trend"]
    sr = daily["sunrise"][0] if daily.get("sunrise") else None; ss = daily["sunset"][0] if daily.get("sunset") else None
    st.markdown(f"""<div class='hero'><div><div class='city'>{esc(ctx['name'])}</div>
<div class='muted' style='margin-top:6px'>{wmo_desc(wmo)} · {ctx['now'].strftime('%d.%m, %H:%M')} · {esc(ctx['sub'])}</div></div>
<div style='display:flex;align-items:center;gap:14px'><span style='transform:scale(1.8);display:inline-block;margin-right:10px'>{wx_icon(wmo, bool(cur.get('is_day', 1)))}</span>
<div style='text-align:right'><div class='temp'>{f1(T, '°')}</div><div class='muted'>ощущается как {f1(FL, '°')}</div></div></div></div>""", unsafe_allow_html=True)
    tr_txt = "—" if trend is None else ("растёт" if trend > 1 else "падает" if trend < -1 else "стабильно")
    grid([stat("Ветер", fw(wind), f"{compass(wd)}, порывы {fw(gust)}" if wd is not None else ""),
          stat("Давление", fp(P), f"тенденция за 3 ч: {tr_txt}"),
          stat("Влажность", f1(RH, "%"), f"точка росы {f1(dew, '°')}"),
          stat("Осадки", f1(pp, "%"), "вероятность в этот час"),
          stat("Облачность", f1(cloud, "%"), ""),
          stat("Видимость", "—" if vis is None else f"{vis / 1000:.1f} км", ""),
          stat("УФ-индекс", f1(uv, "", 1), uv_text(uv)),
          stat("Солнце", f"{sr[11:16] if sr else '—'} — {ss[11:16] if ss else '—'}", "восход — закат")], 150)

    section("Ближайшие часы")
    cells = []
    for k in range(0, 24):
        i = ni + k
        if i >= len(H["time"]): break
        t_ = H["time"][i]
        cells.append(f"<div class='h'><div class='a'>{t_[11:16]}</div>{wx_icon(H['weather_code'][i])}<div class='b'>{f1(H['temperature_2m'][i], '°')}</div><div class='c'>{f1(H['precipitation_probability'][i], '%')}</div></div>")
    st.markdown(f"<div class='strip'>{''.join(cells)}</div>", unsafe_allow_html=True)

    section("Прогноз на 7 дней")
    lo_all = min(daily["temperature_2m_min"]); hi_all = max(daily["temperature_2m_max"]); span = max(hi_all - lo_all, 1); rows = []
    for i, iso in enumerate(daily["time"][:7]):
        lo, hi = daily["temperature_2m_min"][i], daily["temperature_2m_max"][i]; pr = daily["precipitation_probability_max"][i]
        rows.append(f"<div class='day'><span>{day_label(i, iso)}</span>{wx_icon(daily['weather_code'][i])}<span class='muted'>{wmo_desc(daily['weather_code'][i])}</span>"
                    f"<span class='num' style='display:flex;gap:8px;align-items:center'><span class='muted'>{lo:.0f}°</span><span class='rng' style='flex:1'><i style='left:{(lo - lo_all) / span * 100:.0f}%;right:{100 - (hi - lo_all) / span * 100:.0f}%'></i></span><span>{hi:.0f}°</span></span>"
                    f"<span class='num' style='color:var(--ink);text-align:right'>{f1(pr, '%')}</span></div>")
    card("".join(rows))

    section("Графики")
    kind = st.radio("График", ["Температура", "Осадки", "Ветер", "Давление", "Облачность", "Влажность"], horizontal=True, label_visibility="collapsed", key="chart")
    show(chart_forecast(ctx, th, kind, extra), "fc")

    section("Оценки и советы")
    s, w = walk_comfort(FL, wind, pp, wmo, RH); sp, sl = storm_index(cape, RH, wmo)
    c1, c2 = st.columns(2)
    with c1: verdict_card(s, w, "Комфорт прогулки", th)
    with c2: verdict_card(100 - sp, f"Грозовой риск: {sl.lower()}", f"CAPE {cape:.0f} Дж/кг, оценка {sp}%", th)
    rain = (pp or 0) > 40 or wmo in range(51, 100)
    card(kv_rows([("Одежда", clothing(FL, wind, rain)),
                  ("Прогулка", "Подходящая погода" if s >= 60 else "Лучше короткая"),
                  ("Риск простуды", "Повышенный: влажно и ветрено" if ((RH or 0) > 80 and (wind or 0) > 8) or (T is not None and T < 3) else "Невысокий"),
                  ("Давление", "Резкие перепады могут сказываться на метеозависимых" if trend is not None and abs(trend) > 3 else "Перепадов нет")]))
    aq = extra.get("aq")
    if aq and aq.get("hourly"):
        try:
            ai = aq["hourly"]["time"].index(cur["time"][:13] + ":00"); v = aq["hourly"]["european_aqi"][ai]
            txt, _ = aqi_text(v); pm = aq["hourly"]["pm2_5"][ai]
            section("Качество воздуха")
            grid([stat("Европейский AQI", f"{v:.0f}" if v is not None else "—", txt), stat("PM2.5", f"{pm:.0f} мкг/м³" if pm is not None else "—", "ориентир ВОЗ: 15 за 24 ч"),
                  stat("Пыльца берёзы", f1(aq["hourly"].get("birch_pollen", [None] * 99)[ai], "", 0), "зёрен/м³"), stat("Пыльца злаков", f1(aq["hourly"].get("grass_pollen", [None] * 99)[ai], "", 0), "зёрен/м³")], 160)
        except Exception: pass
    mar = extra.get("marine")
    if mar and mar.get("hourly") and mar["hourly"].get("wave_height") and any(v is not None for v in mar["hourly"]["wave_height"][:24]):
        try:
            mi = mar["hourly"]["time"].index(cur["time"][:13] + ":00"); mh = mar["hourly"]
            section("Море")
            grid([stat("Волны", f1(mh["wave_height"][mi], " м", 1), f"период {f1(mh['wave_period'][mi], ' с', 1)}"), stat("Температура воды", f1(mh["sea_surface_temperature"][mi], "°", 1), "")], 170)
        except Exception: pass
    best = best_days(daily, H)
    if best:
        section("Лучший день недели для...")
        grid([stat(k, v["label"], f"оценка {v['score']}") for k, v in best.items()], 140)

def best_days(daily, hourly):
    times = pd.to_datetime(hourly["time"]); out = {}
    fns = {"Прогулок": lambda d: (100 - d["pp"]) * .5 + max(0, 1 - d["w"] / 14) * 30 + (100 - d["cl"]) * .2,
           "Рыбалки": lambda d: (1 if 990 < d["p"] < 1020 else .5) * 30 + max(0, 1 - d["w"] / 9) * 40 + (100 - d["pp"]) * .3,
           "Астрономии": lambda d: (100 - d["cl"]) * .75 + max(0, 100 - d["rh"]) * .25,
           "Фотографии": lambda d: min(d["cl"], 70) * .5 + max(0, 1 - d["w"] / 18) * 30 + (100 - d["pp"]) * .2 + 20,
           "Работы на участке": lambda d: (100 - d["pp"]) * .5 + max(0, 1 - d["w"] / 14) * 25 + (25 if 8 < d["t"] < 27 else 8)}
    days = []
    for i, iso in enumerate(daily["time"][:7]):
        idx = np.where(times.date == date.fromisoformat(iso))[0]
        if not len(idx): continue
        def av(k, dflt=0):
            v = [hourly[k][j] for j in idx if hourly.get(k) and hourly[k][j] is not None]; return float(np.mean(v)) if v else dflt
        days.append({"i": i, "iso": iso, "cl": av("cloud_cover", 50), "w": av("wind_speed_10m"), "pp": av("precipitation_probability", 30), "rh": av("relative_humidity_2m", 60), "p": av("surface_pressure", 1010), "t": av("temperature_2m", 10)})
    for k, f in fns.items():
        if days:
            b = max(days, key=f); out[k] = {"label": day_label(b["i"], b["iso"]), "score": round(f(b))}
    return out

def chart_forecast(ctx, th, kind, extra):
    H = ctx["hourly"]; ni = ctx["ni"]; t = pd.to_datetime(H["time"]); m = (t >= t[ni] - pd.Timedelta(hours=3)) & (t <= t[ni] + pd.Timedelta(days=5)); x = t[m]
    arr = lambda k: np.array([np.nan if v is None else v for v in H[k]], dtype=float)[m]
    yr = extra.get("yr"); fig = go.Figure(); tz = ctx["tz"]
    def yr_series(col):
        if yr is None: return None
        ts = yr["time"].dt.tz_convert(tz).dt.tz_localize(None); mk = (ts >= x.min()) & (ts <= x.max()); return ts[mk], yr.loc[mk, col]
    if kind == "Температура":
        fig.add_trace(go.Scatter(x=x, y=arr("temperature_2m"), name="Open-Meteo", line=dict(color=th["ink"], width=2.2)))
        fig.add_trace(go.Scatter(x=x, y=arr("apparent_temperature"), name="Ощущается", line=dict(color=th["muted"], width=1.4, dash="dot")))
        mod = extra.get("models")
        if mod:
            mt = pd.to_datetime(mod["time"])
            for nm, d in mod["models"].items():
                fig.add_trace(go.Scatter(x=mt, y=d["temperature_2m"], name={"ecmwf_ifs025": "ECMWF", "gfs_seamless": "GFS", "icon_seamless": "ICON"}.get(nm, nm), line=dict(width=1, dash="dash"), opacity=.7))
        ys = yr_series("temp")
        if ys: fig.add_trace(go.Scatter(x=ys[0], y=ys[1], name="MET Norway", line=dict(color=th["warn"], width=1.4, dash="dash")))
        title = "Температура, °C"
    elif kind == "Осадки":
        fig.add_trace(go.Bar(x=x, y=arr("precipitation"), name="Осадки, мм", marker_color=th["accent"]))
        fig.add_trace(go.Scatter(x=x, y=arr("precipitation_probability"), name="Вероятность, %", yaxis="y2", line=dict(color=th["ink"], width=1.8)))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 100], showgrid=False)); title = "Осадки"
    elif kind == "Ветер":
        mult = 3.6 if st.session_state.get("unit_w") == "км/ч" else 1
        fig.add_trace(go.Scatter(x=x, y=arr("wind_speed_10m") * mult, name="Ветер", line=dict(color=th["ink"], width=2), fill="tozeroy", fillcolor=th["tint"]))
        fig.add_trace(go.Scatter(x=x, y=arr("wind_gusts_10m") * mult, name="Порывы", line=dict(color=th["muted"], width=1.2, dash="dot")))
        title = "Ветер, км/ч" if mult > 1 else "Ветер, м/с"
    elif kind == "Давление":
        mult = 0.750062 if st.session_state.get("unit_p", "мм рт. ст.") == "мм рт. ст." else 1
        fig.add_trace(go.Scatter(x=x, y=arr("surface_pressure") * mult, name="Open-Meteo", line=dict(color=th["ink"], width=2)))
        ys = yr_series("pressure")
        if ys: fig.add_trace(go.Scatter(x=ys[0], y=ys[1] * mult, name="MET Norway (на уровне моря)", line=dict(color=th["warn"], width=1.2, dash="dash")))
        title = "Давление на станции, мм рт. ст." if mult < 1 else "Давление на станции, гПа"
    elif kind == "Облачность":
        for k, nm, c in (("cloud_cover_high", "Верхний ярус", th["accent"]), ("cloud_cover_mid", "Средний ярус", th["muted"]), ("cloud_cover_low", "Нижний ярус", th["ink"])):
            if H.get(k): fig.add_trace(go.Scatter(x=x, y=arr(k), name=nm, line=dict(width=1.6, color=c)))
        fig.add_trace(go.Scatter(x=x, y=arr("cloud_cover"), name="Общая", line=dict(color=th["text"], width=2))); fig.update_yaxes(range=[0, 100]); title = "Облачность, %"
    else:
        fig.add_trace(go.Scatter(x=x, y=arr("relative_humidity_2m"), name="Влажность", line=dict(color=th["ink"], width=2)))
        fig.add_trace(go.Scatter(x=x, y=arr("dew_point_2m"), name="Точка росы, °C", yaxis="y2", line=dict(color=th["muted"], width=1.4, dash="dot")))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False)); title = "Влажность, %"
    style_fig(fig, th, 320, title=title)
    fig.add_vline(x=pd.Timestamp(ctx["cur"]["time"]), line=dict(color=th["line"], width=1))
    return fig

# ════════════════════════════════════════════════════════════════
# РЕЖИМ «ОГОРОДНИК»
# ════════════════════════════════════════════════════════════════
CROPS = [("Горох, редис, шпинат", 4), ("Морковь, свёкла, лук-севок", 7), ("Картофель (посадка)", 8), ("Кукуруза, фасоль", 12),
         ("Томаты, перец (рассада)", 12), ("Огурцы, кабачки, тыква", 14), ("Базилик, баклажаны", 16)]

def mode_garden(ctx, th, extra):
    H, D, ni = ctx["hourly"], ctx["daily"], ctx["ni"]
    st0 = hv(ctx, "soil_temperature_6cm"); st00 = hv(ctx, "soil_temperature_0cm"); sm = hv(ctx, "soil_moisture_0_to_1cm")
    n = min(7, len(D["time"])); tmin = D["temperature_2m_min"][:n]; tmax = D["temperature_2m_max"][:n]; prec = [(v or 0) for v in D["precipitation_sum"][:n]]
    et0 = [(v or 0) for v in (D.get("et0_fao_evapotranspiration") or [0] * n)[:n]]
    frost_days = [(i, v) for i, v in enumerate(tmin) if v <= 0]
    gdd = sum(max(0, (a + b) / 2 - 5) for a, b in zip(tmin, tmax)); balance = sum(prec) - sum(et0)
    first_frost = f"{day_label(frost_days[0][0], D['time'][frost_days[0][0]])}, до {frost_days[0][1]:.0f}°" if frost_days else "не ожидаются"
    section("Сводка на неделю")
    grid([stat("Заморозки", first_frost, "минимум ≤ 0 °C"), stat("Температура почвы", f1(st0, "°", 1), "на глубине 6 см сейчас"),
          stat("Сумма активных температур", f"{gdd:.0f}", "выше +5 °C за 7 дней"),
          stat("Водный баланс", f"{balance:+.0f} мм", "осадки минус испарение за 7 дней" if any(et0) else "осадки за 7 дней"),
          stat("Влажность почвы", f"{sm * 100:.0f}%" if sm is not None else "—", "верхний слой, объёмная")], 170)
    section("По дням")
    rows = []
    for i in range(n):
        wmo = D["weather_code"][i]; frost = tmin[i] <= 0; chill = 0 < tmin[i] <= 3
        water = (et0[i] - prec[i] > 2.5) if any(et0) else (prec[i] < 2 and tmax[i] > 20)
        work = (not frost) and tmax[i] > 8 and (D["precipitation_probability_max"][i] or 0) < 50 and wmo not in range(60, 100)
        spray = (D["wind_speed_10m_max"][i] or 0) < 4.5 and prec[i] < 0.5
        rows.append([day_label(i, D["time"][i]), f"{tmin[i]:.0f}° … {tmax[i]:.0f}°", f"{prec[i]:.1f} мм", f"{et0[i]:.1f} мм" if any(et0) else "—",
                     chip("Заморозок", th["bad"]) if frost else (chip("Возможен", th["warn"]) if chill else chip("Нет", th["good"])),
                     "Нужен" if water else "Не нужен", chip("Можно", th["good"]) if work else chip("Нет", th["bad"]), "Подходит" if spray else "Ветрено/дождь"])
    table(["День", "Темп.", "Осадки", "Испарение", "Заморозок", "Полив", "Работы", "Опрыскивание"], rows)
    note("Заморозок приземного слоя бывает на 2–4 градуса холоднее, чем показывает метеобудка (2 м): при минимуме +2…+3 °C в ясную безветренную ночь укрывайте рассаду.")

    section("Что сеять при текущей температуре почвы")
    tr = []
    for crop, tmin_s in CROPS:
        ok = st0 is not None and st0 >= tmin_s
        tr.append([crop, f"от {tmin_s}°", chip("Можно", th["good"]) if ok else chip("Рано", th["warn"])])
    table(["Культура", "Мин. температура почвы", "Статус"], tr)
    note("Ориентировочные пороги прорастания; сроки зависят от сорта и региона. Для ночных заморозков учитывайте минимумы выше.")

    # Риск фитофтороза (упрощённый критерий Хаттона: ≥11 ч подряд с T ≥ 10 и RH ≥ 90 %)
    T, RH = H["temperature_2m"], H["relative_humidity_2m"]; run = best = 0
    for i in range(ni, min(ni + 48, len(T))):
        if T[i] is not None and RH[i] is not None and T[i] >= 10 and RH[i] >= 90: run += 1; best = max(best, run)
        else: run = 0
    section("Болезни и вредители")
    risk = ("Высокий", th["bad"]) if best >= 11 else (("Умеренный", th["warn"]) if best >= 6 else ("Низкий", th["good"]))
    card(kv_rows([("Риск фитофтороза и мильдью на 48 ч", chip(risk[0], risk[1])), ("Самая долгая влажная и тёплая серия", f"{best} ч подряд (T ≥ 10 °C, RH ≥ 90%)"),
                  ("Жара", "Возможен тепловой стресс: тень и утренний полив" if max(tmax) > 30 else "Нет"), ("Град", "Укройте теплицы и рассаду" if any(c in (96, 99) for c in D["weather_code"][:n]) else "Не ожидается")]))
    sc = pd.DataFrame({"t": pd.to_datetime(H["time"]), "s0": [np.nan if v is None else v for v in H.get("soil_temperature_0cm", [None] * len(H["time"]))],
                       "s6": [np.nan if v is None else v for v in H.get("soil_temperature_6cm", [None] * len(H["time"]))], "air": [np.nan if v is None else v for v in H["temperature_2m"]]})
    sc = sc[sc["t"] <= sc["t"].iloc[ni] + pd.Timedelta(days=5)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sc["t"], y=sc["air"], name="Воздух 2 м", line=dict(color=th["muted"], width=1.4)))
    fig.add_trace(go.Scatter(x=sc["t"], y=sc["s0"], name="Поверхность почвы", line=dict(color=th["ink"], width=1.6)))
    fig.add_trace(go.Scatter(x=sc["t"], y=sc["s6"], name="Почва 6 см", line=dict(color=th["good"], width=2)))
    fig.add_hline(y=0, line=dict(color=th["bad"], width=1, dash="dot")); style_fig(fig, th, 300, title="Температура воздуха и почвы, °C"); show(fig, "soil")

# ════════════════════════════════════════════════════════════════
# РЕЖИМ «ДРОНЫ»
# ════════════════════════════════════════════════════════════════
def mode_drone(ctx, th, extra):
    H, ni = ctx["hourly"], ctx["ni"]; cur = ctx["cur"]
    sw = fetch_space_weather(); kp = float(sw["kp"]["Kp"].iloc[-1]) if sw.get("kp") is not None and len(sw["kp"]) else None
    # ветер на высотах: у поверхности и на уровнях 850/700 гПа (≈1.5 и 3 км) из Open-Meteo
    w10 = hv(ctx, "wind_speed_10m"); w850 = hv(ctx, "wind_speed_850hPa"); gust = hv(ctx, "wind_gusts_10m")
    vis = (hv(ctx, "visibility") or 10000) / 1000
    score, issues = drone_score(w10, gust, vis, hv(ctx, "precipitation_probability"), cur.get("weather_code"), cur.get("temperature_2m"), kp, None)
    verdict = "Полёты возможны" if score >= 70 else "С осторожностью" if score >= 40 else "Лучше не летать"
    verdict_card(score, verdict, "Оценка по ветру, порывам, видимости, осадкам, температуре и геомагнитной обстановке", th,
                 ("<div class='sep'></div>" + "".join(f"<div class='kv'><span class='tx'>{x}</span></div>" for x in issues)) if issues else "")
    grid([stat("Ветер у земли", fw(w10), f"порывы {fw(gust)}"), stat("Ветер на высоте ≈1.5 км", fw(w850), "уровень 850 гПа; на 120 м он обычно сильнее, чем у земли"),
          stat("Видимость", f"{vis:.1f} км", ""), stat("Температура", f1(cur.get("temperature_2m"), "°"), "ниже +5 °C батарея теряет ёмкость"),
          stat("Kp (GNSS)", f"{kp:.1f}" if kp is not None else "—", "при Kp ≥ 5 возможна потеря точности GPS")], 170)
    # почасовое окно полётов
    t = pd.to_datetime(H["time"]); idx = [i for i in range(ni, min(ni + 48, len(t)))]; sc = []
    for i in idx:
        g = lambda k: (H.get(k) or [None] * len(t))[i]
        s, _ = drone_score(g("wind_speed_10m"), g("wind_gusts_10m"), (g("visibility") or 10000) / 1000, g("precipitation_probability"), g("weather_code"), g("temperature_2m"), kp, None); sc.append(s)
    section("Окно полётов на 48 часов")
    fig = go.Figure(go.Bar(x=[t[i] for i in idx], y=sc, marker_color=[th["good"] if s >= 70 else th["warn"] if s >= 40 else th["bad"] for s in sc], hovertemplate="%{x|%d.%m %H:%M}: %{y:.0f}<extra></extra>"))
    style_fig(fig, th, 240, legend=False, title="Пригодность для полёта, 0–100"); fig.update_yaxes(range=[0, 100]); show(fig, "drone48")
    ev = sun_moon_events(*ctx["S"], ctx["now"].date().isoformat()) if EPHEM_OK else {}
    if ev: card(kv_rows([("Светлое время", f"{hhmm(ev.get('civil_morn_today') or ev.get('sunrise'))} — {hhmm(ev.get('sunset'))}"), ("Гражданские сумерки заканчиваются", hhmm(ev.get("civil_eve")))]))
    m = extra.get("metar")
    if m: card(kv_rows([("Ближайший аэродром", f"{esc(str(m.get('name', m.get('icaoId', ''))))} ({m.get('icaoId', '')})"), ("Расстояние", f"{m['_dist']:.0f} км"),
                        ("Что делать", "Проверьте воздушное пространство и ограничения для вашего района до полёта")]))
    note("Оценка — только метеоусловия. Правила, зоны ограничений и регистрация дронов зависят от страны и района — это ваша ответственность. Высота полёта по большинству правил не выше 120 м над землёй.")

# ════════════════════════════════════════════════════════════════
# РЕЖИМ «ФОТОГРАФ»
# ════════════════════════════════════════════════════════════════
def light_windows(grid):
    """Золотой час: Солнце от −4° до +6°; синий: от −8° до −4°."""
    out = {"golden": [], "blue": []}
    for name, lo, hi in (("golden", -4, 6), ("blue", -8, -4)):
        m = (grid["sun_alt"] > lo) & (grid["sun_alt"] <= hi); start = None; prev = None
        for t, f in zip(grid["t"], m):
            if f and start is None: start = t
            if not f and start is not None: out[name].append((start, prev)); start = None
            prev = t
        if start is not None: out[name].append((start, prev))
    return out

def mode_photo(ctx, th, extra):
    if not EPHEM_OK: st.error("Нужна библиотека ephem: pip install ephem"); return
    S = ctx["S"]; nd = astro_night(ctx); ev = sun_moon_events(*S, nd); grid_ = night_grid(*S, nd, 5); win = light_windows(grid_)
    cur = ctx["cur"]; H, ni = ctx["hourly"], ctx["ni"]
    # прогноз «красочного» неба: высокие/средние облака 30–70% при открытом горизонте
    hi, mid, low = hv(ctx, "cloud_cover_high"), hv(ctx, "cloud_cover_mid"), hv(ctx, "cloud_cover_low")
    vis = (hv(ctx, "visibility") or 10000) / 1000
    if None not in (hi, mid, low):
        up = (hi + mid) / 2
        sky = ("Благоприятно для эффектного заката/рассвета", 85) if (25 <= up <= 75 and low < 25 and vis > 8) else (("Ясно: чистый градиент без облаков", 60) if (up < 15 and low < 15) else (("Низкая облачность закроет горизонт", 25) if low > 60 else ("Умеренно", 45)))
    else: sky = ("Недостаточно данных по ярусам облаков", 45)
    verdict_card(sky[1], sky[0], f"верхний ярус {f1(hi, '%')}, средний {f1(mid, '%')}, нижний {f1(low, '%')}, видимость {vis:.0f} км", th)
    section("Золотой и синий час", "Золотой — Солнце от −4° до +6°; синий — от −8° до −4°")
    def span(ws, i): return f"{hhmm(ws[i][0])} — {hhmm(ws[i][1])}" if len(ws) > i else "—"
    gw = sorted(win["golden"], key=lambda w: w[0]); bw = sorted(win["blue"], key=lambda w: w[0])
    az_r = body_az_at(ctx, ev["sunrise_next"], ephem.Sun); az_s = body_az_at(ctx, ev["sunset"], ephem.Sun)
    grid([stat("Золотой час, вечер", span(gw, 0), f"закат в {hhmm(ev['sunset'])}, азимут {az_s:.0f}° {compass(az_s)}" if az_s is not None else ""),
          stat("Синий час, вечер", span(bw, 0), "после заката"), stat("Синий час, утро", span(bw, 1), "перед рассветом"),
          stat("Золотой час, утро", span(gw, 1), f"восход в {hhmm(ev['sunrise_next'])}, азимут {az_r:.0f}° {compass(az_r)}" if az_r is not None else "")], 200)
    # таймлайн
    fig = go.Figure(); X0 = grid_["t"].iloc[0]
    def bar(a, b, name, color): fig.add_trace(go.Bar(x=[(b - a).total_seconds() / 3600 + 5 / 60], y=[""], base=[(a - X0).total_seconds() / 3600], orientation="h", marker_color=color, name=name, hovertemplate=f"{name}: {hhmm(a)}–{hhmm(b)}<extra></extra>"))
    for a, b in gw: bar(a, b, "Золотой час", th["warn"])
    for a, b in bw: bar(a, b, "Синий час", th["ink"])
    for a, b in dark_windows(grid_, False, -18): bar(a, b, "Астрономическая ночь", th["muted"])
    ticks = list(range(0, 25, 3)); fig.update_layout(barmode="overlay"); style_fig(fig, th, 130, title="Световые окна суток")
    fig.update_xaxes(tickvals=ticks, ticktext=[(X0 + timedelta(hours=h)).strftime("%H:%M") for h in ticks], range=[0, 24]); show(fig, "photo_tl")
    section("Луна и условия")
    mi = moon_info(*S, utcnow().replace(microsecond=0).isoformat()); items = []
    if ev["moonrise"] and ev["sunset"] and mi["illum"] > 88 and abs((ev["moonrise"] - ev["sunset"]).total_seconds()) < 5400:
        items.append("Восход почти полной Луны близко к закату: хороший момент для кадра с Луной над горизонтом.")
    fog = (hv(ctx, "relative_humidity_2m") or 0) > 94 and (hv(ctx, "wind_speed_10m") or 9) < 2.5
    if fog: items.append("Высокий шанс тумана на рассвете: подходит для атмосферных пейзажей.")
    if (hv(ctx, "wind_speed_10m") or 0) > 8: items.append("Сильный ветер: штатив с утяжелением, короткие выдержки.")
    if not items: items.append("Особых событий не ожидается. Смотрите окно света выше.")
    card(kv_rows([("Луна", f"{mi['name']}, {mi['illum']:.0f}%; восход {hhmm(ev['moonrise'])}, заход {hhmm(ev['moonset'])}")]) + "".join(f"<div class='kv'><span class='tx'>{x}</span></div>" for x in items))
    # риск для техники
    T, RH, wmo, w = cur.get("temperature_2m"), cur.get("relative_humidity_2m"), cur.get("weather_code") or 0, cur.get("wind_speed_10m") or 0
    risks = []
    if (RH or 0) > 90: risks.append("Конденсат на линзах (влажность выше 90%): держите оптику в сумке при переходе из тепла")
    if wmo in range(51, 83): risks.append("Осадки: нужен дождевик для камеры")
    if wmo >= 95: risks.append("Гроза: не работайте на открытом месте со штативом")
    if T is not None and T < -10: risks.append("Мороз: аккумуляторы разряжаются быстро, держите запасные в тёплом кармане")
    if T is not None and hv(ctx, "dew_point_2m") is not None and T - hv(ctx, "dew_point_2m") < 2: risks.append("Роса: возможно запотевание объектива")
    section("Риски для техники"); card("".join(f"<div class='kv'><span class='tx'>{r}</span></div>" for r in risks) if risks else "<div class='kv'><span>Условия безопасны для техники</span></div>")
    section("Экспозиция при дневном свете", "Правило «солнечной шестнадцатой» для ISO 100")
    cl = hv(ctx, "cloud_cover") or 0
    ap, sh = ("f/16", "1/ISO") if cl < 20 else ("f/11", "1/ISO") if cl < 50 else ("f/8", "1/ISO") if cl < 80 else ("f/5.6", "1/ISO")
    card(kv_rows([("Диафрагма", ap), ("Выдержка", "1/100 с при ISO 100" if cl < 20 else "1/100 с при ISO 100 (диафрагма из таблицы)"), ("Состояние неба", f"облачность {cl:.0f}%")]))
    note("Правило даёт отправную точку: проверьте гистограмму. Для ночной съёмки и астрофото см. раздел «Инструменты» в режиме «Астрономия».")
    fig = go.Figure(); s5 = grid_
    fig.add_trace(go.Scatter(x=s5["t"], y=s5["sun_alt"], name="Солнце", line=dict(color=th["warn"], width=2)))
    fig.add_trace(go.Scatter(x=s5["t"], y=s5["moon_alt"], name="Луна", line=dict(color=th["ink"], width=1.6)))
    fig.add_hline(y=0, line=dict(color=th["muted"], width=1)); style_fig(fig, th, 260, title="Высота Солнца и Луны, °"); show(fig, "photo_sun")

# ════════════════════════════════════════════════════════════════
# РЕЖИМ «ДАННЫЕ И ИСТОЧНИКИ»
# ════════════════════════════════════════════════════════════════
def nearest_hour(df, tz, key, now_local):
    if df is None or df.empty: return None
    ts = df["time"].dt.tz_convert(tz); d = (ts - pd.Timestamp(now_local)).abs(); j = int(d.values.argmin())
    v = df[key].iloc[j]; return None if pd.isna(v) else float(v)

def mode_data(ctx, th, extra):
    S = ctx["S"]; cur = ctx["cur"]; tz = ctx["tz"]; now = ctx["now"]; yr = extra.get("yr"); metar = extra.get("metar"); mod = extra.get("models")
    rows = [("Open-Meteo", cur.get("temperature_2m"), cur.get("wind_speed_10m"), cur.get("cloud_cover"), cur.get("surface_pressure") and cur["surface_pressure"], cur.get("relative_humidity_2m"))]
    if yr is not None: rows.append(("MET Norway (Yr)", nearest_hour(yr, tz, "temp", now), nearest_hour(yr, tz, "wind", now), nearest_hour(yr, tz, "cloud", now), nearest_hour(yr, tz, "pressure", now), nearest_hour(yr, tz, "rh", now)))
    if metar:
        kt = 0.514444; rows.append((f"METAR {metar.get('icaoId', '')} ({metar['_dist']:.0f} км)", metar.get("temp"), (metar.get("wspd") or 0) * kt if metar.get("wspd") is not None else None, None, metar.get("altim"), None))
    if mod:
        mt = pd.to_datetime(mod["time"]); j = int((mt - pd.Timestamp(cur["time"])).to_series().abs().values.argmin()) if len(mt) else 0
        for nm, d in mod["models"].items(): rows.append(({"ecmwf_ifs025": "ECMWF IFS", "gfs_seamless": "NOAA GFS", "icon_seamless": "DWD ICON"}.get(nm, nm), d["temperature_2m"][j], d["wind_speed_10m"][j], d["cloud_cover"][j], None, None))
    for nm, fn in (("OpenWeatherMap", fetch_owm), ("WeatherAPI", fetch_weatherapi)):
        r = fn(S[0], S[1])
        if r: rows.append((nm, r["temp"], r["wind"], r["cloud"], r["pressure"], r["rh"]))
    temps = [r[1] for r in rows if r[1] is not None]
    if len(temps) >= 2:
        spread = max(temps) - min(temps); lvl, col = ("Высокая", th["good"]) if spread <= 1.5 else (("Средняя", th["warn"]) if spread <= 3.5 else ("Низкая", th["bad"]))
        verdict_card(max(0, 100 - spread * 18), f"Согласованность источников: {lvl.lower()}", f"разброс температур {spread:.1f} °C между {len(temps)} источниками", th)
    else: st.info("Для сверки нужно минимум два источника. Включите их в настройках.")
    section("Сейчас по источникам")
    f = lambda v, u="", nd=1: "—" if v is None else f"{v:.{nd}f}{u}"
    table(["Источник", "Температура", "Ветер, м/с", "Облачность", "Давление, гПа", "Влажность"],
          [[r[0], f(r[1], "°"), f(r[2]), f(r[3], "%", 0), f(r[4], "", 0), f(r[5], "%", 0)] for r in rows], right=(1, 2, 3, 4, 5))
    note("Open-Meteo — основной источник. Остальные — независимые проверки: MET Norway (Норвежский метеоинститут), METAR — реальное наблюдение аэродрома, ECMWF/GFS/ICON — разные глобальные модели. "
         "Давление METAR приведено к уровню моря, у остальных — на станции. Дополнительные источники (OpenWeatherMap, WeatherAPI) включаются ключами OWM_KEY и WEATHERAPI_KEY.")
    if metar:
        section("Авиационные сводки")
        card(f"<div class='kv'><span>METAR</span><span style='font-family:ui-monospace,monospace;font-size:12.5px;text-align:left'>{esc(metar.get('rawOb', '—'))}</span></div>")
        taf = fetch_taf(metar.get("icaoId", ""))
        if taf: card(f"<div class='kv'><span>TAF</span><span style='font-family:ui-monospace,monospace;font-size:12.5px;text-align:left'>{esc((taf.get('rawTAF') or taf.get('rawTaf') or '—')[:600])}</span></div>")
    section("Атмосфера")
    c1, c2 = st.columns(2)
    with c1: show(chart_skewt(ctx, th), "skewt")
    with c2: show(chart_windrose(ctx, th), "rose")
    section("Радар и карты")
    ov = st.radio("Слой", ["radar", "clouds", "wind", "temp", "pressure"], format_func={"radar": "Радар осадков", "clouds": "Облака", "wind": "Ветер", "temp": "Температура", "pressure": "Давление"}.get, horizontal=True, key="chart_l", label_visibility="collapsed")
    components.iframe(f"https://embed.windy.com/embed2.html?lat={S[0]:.3f}&lon={S[1]:.3f}&detailLat={S[0]:.3f}&detailLon={S[1]:.3f}&zoom=7&level=surface&overlay={ov}&menu=&message=true&marker=true&calendar=now&type=map&location=coordinates&metricWind=m%2Fs&metricTemp=%C2%B0C", height=460)
    c1, c2, c3 = st.columns(3)
    c1.link_button("Молнии: Blitzortung", f"https://www.blitzortung.org/en/live_lightning_maps.php?map=11&lat={S[0]:.2f}&lon={S[1]:.2f}", use_container_width=True)
    c2.link_button("Радары: Meteologix", "https://meteologix.com/ru/radar/", use_container_width=True)
    c3.link_button("Новости: Gismeteo", "https://www.gismeteo.ru/news/", use_container_width=True)

def chart_skewt(ctx, th):
    H, ni = ctx["hourly"], ctx["ni"]; lv = [850, 700, 500, 300]; T, Td = [], []
    for l in lv:
        t_ = (H.get(f"temperature_{l}hPa") or [None] * 999)[ni]; r = (H.get(f"relative_humidity_{l}hPa") or [None] * 999)[ni]
        T.append(t_); Td.append(dewpoint(t_, r) if t_ is not None and r else None)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=T, y=lv, mode="lines+markers", name="Температура", line=dict(color=th["ink"], width=2)))
    fig.add_trace(go.Scatter(x=Td, y=lv, mode="lines+markers", name="Точка росы", line=dict(color=th["muted"], width=2, dash="dash")))
    style_fig(fig, th, 320, title="Температура и точка росы по высотам"); fig.update_yaxes(autorange="reversed", title="гПа"); fig.update_xaxes(title="°C"); fig.update_layout(hovermode="closest"); return fig

def chart_windrose(ctx, th):
    H = ctx["hourly"]; ni = ctx["ni"]; d = H["wind_direction_10m"][ni:ni + 120]; s = H["wind_speed_10m"][ni:ni + 120]
    fr = [0] * 8; sp = [0.0] * 8
    for a, b in zip(d, s):
        if a is None or b is None: continue
        k = int(((a + 22.5) % 360) // 45); fr[k] += 1; sp[k] += b
    tot = max(sum(fr), 1)
    fig = go.Figure(go.Barpolar(r=[f / tot * 100 for f in fr], theta=["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"], marker_color=th["accent"], marker_line_color=th["ink"], marker_line_width=1, hovertemplate="%{theta}: %{r:.0f}%<extra></extra>"))
    fig.update_layout(height=320, margin=dict(l=30, r=30, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color=th["muted"]), title=dict(text="Роза ветров на 5 суток, %", x=0, font=dict(size=14, color=th["text"])),
                      polar=dict(bgcolor="rgba(0,0,0,0)", angularaxis=dict(rotation=90, direction="clockwise", gridcolor=th["line"]), radialaxis=dict(gridcolor=th["line"], tickfont=dict(size=10))))
    return fig

# ════════════════════════════════════════════════════════════════
# ТУТОРИАЛ
# ════════════════════════════════════════════════════════════════
def go_to(mode):
    st.session_state["pending_mode"] = mode

def mode_tutorial(th):
    st.markdown("<div class='hero'><div><div class='city'>Как пользоваться</div><div class='muted' style='margin-top:6px'>Короткое руководство: где что находится и как читать цифры</div></div></div>", unsafe_allow_html=True)
    section("Быстрый старт", "Четыре шага — и вы в курсе")
    steps = [("1", "Выберите город", "Верхний список: начните печатать название. Нет вашего города — раскройте «Поиск, свой город, настройки»."),
             ("2", "Выберите режим", "Полоса с названиями под городом: Обзор, Астрономия, Огородник, Дроны, Фотограф, Данные."),
             ("3", "Смотрите оценку", "В каждом режиме сверху есть число от 0 до 100 — насколько подходят условия. Ниже — подробности."),
             ("4", "Настройте под себя", "Тема оформления — справа вверху. Единицы, класс тёмного неба и размер телескопа — в настройках.")]
    st.markdown("<div class='grid' style='--min:230px'>" + "".join(f"<div class='card'><div class='step'>{n}</div><div style='font-weight:600;margin:10px 0 6px'>{t}</div><div class='note' style='margin:0'>{d}</div></div>" for n, t, d in steps) + "</div>", unsafe_allow_html=True)

    section("Карта приложения")
    modes = [("Обзор", "Каждый день", "Температура, ветер, давление, почасовой прогноз, 7 дней, графики, качество воздуха, советы по одежде"),
             ("Астрономия", "Наблюдатели неба", "Оценка ночи, карта неба, Луна, планеты, глубокий космос, МКС, метеоры, космическая погода, калькуляторы"),
             ("Огородник", "Дача и сад", "Заморозки, температура почвы, что сеять, полив, риск фитофтороза, работы по дням"),
             ("Дроны", "Пилоты", "Пригодность для полёта, ветер, видимость, Kp для GPS, окно полётов на 48 часов"),
             ("Фотограф", "Съёмка", "Золотой и синий час, прогноз красочного неба, Луна, риски для техники, экспозиция"),
             ("Данные", "Проверка", "Сверка нескольких источников, METAR, модели, радар, ветер по высотам")]
    st.markdown("<div class='tw'><table class='tbl'><thead><tr><th>Режим</th><th>Для кого</th><th>Что внутри</th></tr></thead><tbody>" +
                "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td class='wrap'>{c}</td></tr>" for a, b, c in modes) + "</tbody></table></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, (m, _, _) in enumerate(modes):
        cols[i % 3].button(f"Открыть: {m}", key=f"tut_{m}", on_click=go_to, args=(m,), use_container_width=True)

    section("Астрономия по разделам", "Внутри режима «Астрономия» есть подменю — переключайте разделы, они грузятся по одному")
    sec = [("Сегодня ночью", "Оценка ночи, лучшее окно, ближайшие 4 ночи, тепловая карта часов, сумерки, Луна, замечания"),
           ("Карта неба", "Вид на небо в любое время: звёзды, планеты, Луна, Млечный Путь, список созвездий"),
           ("Солнце и Луна", "Фаза, возраст, расстояние, ближайшие новолуния и полнолуния, графики высоты"),
           ("Планеты", "Где каждая планета, яркость, элонгация, время восхода и захода"),
           ("Глубокий космос", "Галактики, туманности, скопления: что подходит под ваш телескоп и небо"),
           ("Спутники", "Пролёты МКС, китайской станции и Хаббла над вашим городом"),
           ("События", "Метеорные потоки, сближения планет, затмения"),
           ("Космос и Солнце", "Геомагнитная обстановка, солнечный ветер, вспышки, шанс полярного сияния"),
           ("Инструменты", "Выдержка для астрофото, поле зрения, параметры телескопа, Млечный Путь, снимок дня NASA")]
    st.markdown("<div class='tw'><table class='tbl'><thead><tr><th>Раздел</th><th>Что показывает</th></tr></thead><tbody>" + "".join(f"<tr><td><b>{a}</b></td><td class='wrap'>{b}</td></tr>" for a, b in sec) + "</tbody></table></div>", unsafe_allow_html=True)
    st.button("Открыть «Астрономию»", key="tut_astro2", on_click=go_to, args=("Астрономия",))

    section("Как читать оценки")
    st.markdown("<div class='grid' style='--min:200px'>" + "".join(f"<div class='card'>{chip(l, c)}<div class='note'>{d}</div></div>" for l, c, d in [
        ("75–100 · Отлично", th["good"], "Условия почти идеальные, можно планировать без оговорок."),
        ("55–74 · Хорошо", th["good"], "Подходит, но есть небольшие помехи — смотрите замечания."),
        ("35–54 · Средне", th["warn"], "Возможно, но результат будет компромиссным."),
        ("0–34 · Плохо", th["bad"], "Лучше выбрать другое время. Смотрите ближайшие дни.")]) + "</div>", unsafe_allow_html=True)

    section("Свой город")
    card(kv_rows([("Поиск", "«Поиск, свой город, настройки» → «Найти город» → введите название → нажмите на найденный вариант"),
                  ("По координатам", "Вкладка «По координатам»: название, широта, долгота (десятичные градусы) → «Добавить и выбрать»"),
                  ("Поделиться", "Ссылка в адресной строке запоминает город и тему — просто скопируйте её")]))
    note("Для астрономии лучше всего указывать точку наблюдений за городом, а в настройках выбрать класс тёмного неба (Bortle).")

    section("Словарь терминов")
    gl = [("Seeing", "Спокойствие атмосферы: насколько «дрожит» изображение. Чем меньше угловой размер звёздного диска в секундах, тем лучше для планет."),
          ("Прозрачность", "Насколько воздух пропускает свет звёзд. Падает при дымке, влажности, пыли."),
          ("Класс Бортля", "Шкала от 1 (идеально тёмное небо) до 9 (центр города). Определяет, какие звёзды видно."),
          ("Предельная звёздная величина", "Самая слабая звезда, которую видно глазом. Чем число больше, тем темнее небо."),
          ("Астрономическая ночь", "Время, когда Солнце ниже −18° и небо полностью тёмное. Летом на севере её может не быть."),
          ("Высота и азимут", "Высота — угол над горизонтом (90° — зенит). Азимут — направление: 0° север, 90° восток, 180° юг, 270° запад."),
          ("Элонгация", "Угол между планетой и Солнцем. Чем больше, тем лучше планета видна на тёмном небе."),
          ("Терминатор", "Граница света и тени на Луне. Вдоль неё рельеф виден лучше всего."),
          ("Kp-индекс", "Мера геомагнитной возмущённости от 0 до 9. Kp ≥ 5 — магнитная буря: возможны сияния и сбои GPS."),
          ("ZHR", "Теоретическая часовая частота метеоров при идеальных условиях. Реально видно заметно меньше."),
          ("Точка росы", "Температура, при которой выпадает роса. Если воздух к ней близок — оптика запотевает."),
          ("CAPE", "Энергия неустойчивости атмосферы: чем выше, тем сильнее потенциальные грозы.")]
    st.markdown("<div class='grid' style='--min:280px'>" + "".join(f"<div class='card gl'><b>{t}</b><div class='note' style='margin:0'>{d}</div></div>" for t, d in gl) + "</div>", unsafe_allow_html=True)

    section("Откуда данные и насколько им верить")
    card(kv_rows([("Прогноз", "Open-Meteo; резерв — MET Norway. Если основной источник недоступен, приложение переключится само"),
                  ("Проверка", "Режим «Данные»: сравнение с несколькими моделями и реальным наблюдением ближайшего аэродрома"),
                  ("Астрономия", "Положения Солнца, Луны, планет, звёзд и спутников считаются локально (PyEphem) для часового пояса вашего города"),
                  ("Seeing и прозрачность", "Модель 7Timer!, шаг 3 часа: это прогноз, он ошибается чаще, чем температура"),
                  ("Космическая погода", "NOAA SWPC, обновление несколько минут")]))
    section("Частые вопросы")
    for q, a in [("Почему цифры отличаются от другого сайта?", "У разных сервисов разные модели и время обновления. Загляните в «Данные»: там видно разброс между источниками."),
                 ("Почему время не моё?", "Везде используется часовой пояс выбранного города, а не вашего устройства."),
                 ("Ничего не загружается", "Проверьте интернет и повторите. Если «Open-Meteo» недоступен, появится предупреждение и данные из резервного источника."),
                 ("Как включить красную подсветку для наблюдений?", "Тема «Красная ночь» справа вверху: она сохраняет темновую адаптацию глаз.")]:
        with st.expander(q): st.markdown(a)

# ════════════════════════════════════════════════════════════════
# ГЛАВНЫЙ ЭКРАН
# ════════════════════════════════════════════════════════════════
MODES = ["Обзор", "Астрономия", "Огородник", "Дроны", "Фотограф", "Данные", "Туториал"]

def parse_custom(s):
    try:
        n, la, lo = s.split("|"); return {"name": n, "country": "Своё место", "lat": float(la), "lon": float(lo)}
    except Exception: return None

def main():
    st.set_page_config(page_title="Погода и астрономия", page_icon="◐", layout="wide", initial_sidebar_state="collapsed")
    ss = st.session_state; qp = st.query_params
    if "init" not in ss:
        ss["custom"] = {}; ss["theme"] = qp.get("theme", DEFAULT_THEME) if qp.get("theme") in THEMES else DEFAULT_THEME
        ss.update(bortle=6, aperture=100, unit_p="мм рт. ст.", unit_w="м/с", use_yr=True, use_models=True, use_metar=True, mode="Обзор")
        if "c" in qp:
            c = parse_custom(qp["c"])
            if c: ss["custom"][f"{c['name']} · Своё место"] = c; ss["city"] = f"{c['name']} · Своё место"
        elif qp.get("city") in CITIES: ss["city"] = qp["city"]
        ss["init"] = True
    if "pending_city" in ss: ss["city"] = ss.pop("pending_city")
    if "pending_mode" in ss: ss["mode"] = ss.pop("pending_mode")
    th = THEMES[ss["theme"]]; apply_css(th)

    # ── шапка ──
    h1, h2 = st.columns([4, 1])
    with h1: st.markdown("<div class='brand' style='padding-top:8px'>Погода и астрономия</div>", unsafe_allow_html=True)
    with h2: st.selectbox("Тема", list(THEMES), key="theme", label_visibility="collapsed")
    ALL = {**CITIES, **ss["custom"]}; keys = list(ALL)
    if ss.get("city") not in ALL: ss["city"] = DEFAULT_CITY
    sel = st.selectbox("Город", keys, key="city", format_func=lambda k: f"{ALL[k]['name']}  ·  {ALL[k]['country']}", label_visibility="collapsed", placeholder="Начните вводить название города")
    place = ALL[sel]

    with st.expander("Поиск, свой город, настройки"):
        t1, t2, t3 = st.tabs(["Найти город", "По координатам", "Настройки"])
        with t1:
            q = st.text_input("Название города", placeholder="например, Бишкек, Пятигорск, Tashkent", key="q")
            if q and len(q.strip()) >= 2:
                res = geocode(q)
                if not res: st.caption("Ничего не найдено.")
                for i, r in enumerate(res):
                    label = f"{r['name']} · {r.get('admin1', '')} · {r.get('country', '')}".replace(" ·  ·", " ·")
                    if st.button(label, key=f"g{i}", use_container_width=True):
                        k = f"{r['name']} · Своё место"; ss["custom"][k] = {"name": r["name"], "country": r.get("country", "Своё место"), "lat": r["latitude"], "lon": r["longitude"], "elev": r.get("elevation")}
                        ss["pending_city"] = k; st.rerun()
        with t2:
            a, b, c = st.columns(3)
            nm = a.text_input("Название", "Моё место", key="c_name"); la = b.number_input("Широта", -90.0, 90.0, 55.0, 0.0001, format="%.4f", key="c_lat"); lo = c.number_input("Долгота", -180.0, 180.0, 37.0, 0.0001, format="%.4f", key="c_lon")
            if st.button("Добавить и выбрать", use_container_width=True):
                k = f"{nm.strip() or 'Моё место'} · Своё место"; ss["custom"][k] = {"name": nm.strip() or "Моё место", "country": "Своё место", "lat": la, "lon": lo}; ss["pending_city"] = k; st.rerun()
            st.caption("Координаты в десятичных градусах (например, 43.2220 и 76.8512).")
        with t3:
            a, b = st.columns(2)
            b.selectbox("Давление", ["мм рт. ст.", "гПа"], key="unit_p"); a.selectbox("Ветер", ["м/с", "км/ч"], key="unit_w")
            b.selectbox("Тёмное небо: класс Бортля", list(BORTLE), key="bortle", format_func=lambda k: f"{k} — {BORTLE[k][0]}")
            a.number_input("Апертура телескопа, мм", 30, 600, key="aperture", step=10)
            st.markdown("**Источники для сверки**")
            a.toggle("MET Norway (Yr)", key="use_yr"); b.toggle("Модели ECMWF, GFS, ICON", key="use_models"); a.toggle("METAR аэродрома", key="use_metar")

    mode = st.radio("Режим", MODES, horizontal=True, label_visibility="collapsed", key="mode")
    try:
        st.query_params["theme"] = ss["theme"]
        st.query_params["city"] = sel if sel in CITIES else ""
        if sel not in CITIES: st.query_params["c"] = f"{place['name']}|{place['lat']:.4f}|{place['lon']:.4f}"
    except Exception: pass
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if mode == "Туториал":
        with st.container(key="v6"): mode_tutorial(th)
        return
    if not ss.get("hide_tip"):
        card("<div style='font-weight:600'>Впервые здесь?</div><div class='note' style='margin-top:4px'>В туториале — где что находится, как читать оценки и словарь терминов.</div>")
        b1, b2 = st.columns(2)
        b1.button("Открыть туториал", key="tip_open", on_click=lambda: (go_to("Туториал"), ss.update(hide_tip=True)), use_container_width=True)
        b2.button("Скрыть", key="tip_hide", on_click=lambda: ss.update(hide_tip=True), use_container_width=True)

    # ── данные ──
    lat, lon = float(place["lat"]), float(place["lon"])
    with st.spinner("Загружаю данные"):
        data = fetch_openmeteo(lat, lon); yr = fetch_yr(lat, lon) if (ss["use_yr"] or data is None) else None
        if data is None:
            data = openmeteo_from_yr(yr, lat, lon)
            if data is None: st.error("Ни один источник прогноза не отвечает. Проверьте соединение и попробуйте позже."); return
            st.warning("Open-Meteo недоступен — показаны данные резервного источника MET Norway. Часть показателей (УФ, CAPE, почва, ярусы облаков) может отсутствовать.")
        models = fetch_models(lat, lon) if ss["use_models"] else None
        metar = fetch_metar(lat, lon) if ss["use_metar"] else None
        extra = {"yr": yr, "models": models, "metar": metar, "aq": fetch_airquality(lat, lon), "marine": fetch_marine(lat, lon)}
    tzname = data.get("timezone", "UTC"); tz = tzinfo(tzname); elev = place.get("elev") or data.get("elevation") or 0
    hourly, daily, ni, trend = prepare(data); now = datetime.now(tz)
    ctx = dict(lat=lat, lon=lon, elev=elev, tzname=tzname, tz=tz, S=(round(lat, 4), round(lon, 4), round(float(elev)), tzname), name=place["name"],
               sub=f"{lat:.2f}°, {lon:.2f}° · {elev:.0f} м", now=now, hourly=hourly, daily=daily, ni=max(ni, 0), cur=data["current"], trend=trend,
               bortle=ss["bortle"], aperture=ss["aperture"])
    fn = {"Обзор": mode_overview, "Астрономия": lambda c, t, e: mode_astro(c, t), "Огородник": mode_garden, "Дроны": mode_drone, "Фотограф": mode_photo, "Данные": mode_data}[mode]
    with st.container(key=f"v{MODES.index(mode)}"): fn(ctx, th, extra)

    st.markdown(f"<div class='note' style='margin-top:36px'>Данные: {esc(data.get('_source', 'Open-Meteo'))}, MET Norway, NOAA (METAR, SWPC), 7Timer!, CelesTrak, NASA. Астрономические расчёты — PyEphem. "
                f"Время указано в поясе места ({esc(tzname)}).</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
