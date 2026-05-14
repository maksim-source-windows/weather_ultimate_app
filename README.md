# 🌦️ Weather App — Инструкция по запуску

## Требования
- Python 3.10 или выше

---

## 🚀 Быстрый старт

### 1. Создайте виртуальное окружение (рекомендуется)

```bash
python -m venv venv
```

Активация:
- **Windows:** `venv\Scripts\activate`
- **macOS / Linux:** `source venv/bin/activate`

---

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

---

### 3. Запустите приложение

```bash
streamlit run weather_app.py
```

Браузер откроется автоматически по адресу: **http://localhost:8501**

---

## 📦 Зависимости

| Библиотека   | Назначение                          |
|--------------|-------------------------------------|
| streamlit    | UI-фреймворк                        |
| requests     | HTTP-запросы к Open-Meteo API       |
| pandas       | Работа с табличными данными         |
| plotly       | Интерактивные графики               |
| numpy        | Математические вычисления           |

Внешние API (не требуют ключей):
- **Open-Meteo** — погода, CAPE, lightning_potential
- **Blitzortung.org** — карта молний (iframe)

---

## 🛠 Дополнительные параметры запуска

Изменить порт:
```bash
streamlit run weather_app.py --server.port 8080
```

Отключить автооткрытие браузера:
```bash
streamlit run weather_app.py --server.headless true
```

Развернуть на всех интерфейсах (например, в Docker):
```bash
streamlit run weather_app.py --server.address 0.0.0.0
```

---

## 🐳 Запуск через Docker (опционально)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY weather_app.py .
EXPOSE 8501
CMD ["streamlit", "run", "weather_app.py", "--server.address", "0.0.0.0"]
```

```bash
docker build -t weather-app .
docker run -p 8501:8501 weather-app
```

---

## ❗ Возможные проблемы

**`ModuleNotFoundError`** — не активировано виртуальное окружение или не установлены зависимости.
```bash
pip install -r requirements.txt
```

**Пустые графики / нет данных** — нет доступа к интернету или Open-Meteo временно недоступен. Подождите и обновите страницу.

**Радар не загружается** — Blitzortung.org может блокировать iframe в некоторых браузерах. Попробуйте Chrome или Firefox.
