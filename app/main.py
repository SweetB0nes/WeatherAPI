import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
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
async def get_weather(
    city: Optional[str] = Query(default=None, description="Название города"),
    lat: Optional[float] = Query(default=None, description="Широта"),
    lon: Optional[float] = Query(default=None, description="Долгота"),
):
    """
    MVP-эндпоинт:
    - Если есть lat+lon — используем их.
    - Иначе, если есть city — используем город.
    - Иначе 400.
    """
    if lat is not None and lon is not None:
        return await fetch_weather(lat=lat, lon=lon)
    if city:
        return await fetch_weather(city=city)
    raise HTTPException(status_code=400, detail="Provide city or (lat, lon)")
