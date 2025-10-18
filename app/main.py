import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from app.api.schemas import WeatherQuery, WeatherResponse
from app.providers.openweather import fetch_weather

app = FastAPI(title="Weather API", version="0.1.0")

@app.exception_handler(httpx.RequestError)
async def httpx_request_error_handler(_, exc: httpx.RequestError):
    # Сетевые проблемы/таймауты до получения ответа
    return JSONResponse({"detail": "Upstream network error"}, status_code=502)

@app.exception_handler(httpx.HTTPStatusError)
async def httpx_status_error_handler(_, exc: httpx.HTTPStatusError):
    # Провайдер вернул 4xx/5xx
    code = exc.response.status_code if exc.response is not None else "unknown"
    return JSONResponse({"detail": f"Upstream HTTP {code}"}, status_code=502)

@app.get("healt")
async def healthz():
    return {"status": "ok"}

@app.get("/api/v1/weather")
async def get_weather(q: WeatherQuery = Depends()):
    """
    - 422: неверные типы/диапазоны.
    - 400: логическая ошибка запроса (не переданы ни city, ни обе координаты).
    - 502: проблемы провайдера.
    Приоритет: если есть координаты — используем их; иначе — город.
    """
    if q.is_empty():
        raise HTTPException(status_code=400, detail="Provide city or (lat, lon)")

    if q.lat is not None and q.lon is not None:
        data = await fetch_weather(lat=q.lat, lon=q.lon)
    else:
        data = await fetch_weather(city=q.city)

    return WeatherResponse(**data)