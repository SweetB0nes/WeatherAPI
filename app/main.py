import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.api.schemas import WeatherQuery, WeatherResponse
from app.providers.openweather import fetch_weather
from app.infrastructure.repositories.weather_request_repo import WeatherRequestRepository

app = FastAPI(title="Weather API", version="0.3.0")
repo = WeatherRequestRepository()

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
        repo.save_validation_error(
            city=q.city, lat=q.lat, lon=q.lon,
            error_detail="Provide city or (lat, lon)",
        )
        raise HTTPException(status_code=400, detail="Provide city or (lat, lon)")

    try:
        if q.lat is not None and q.lon is not None:
            data = await fetch_weather(lat=q.lat, lon=q.lon)
            city = data["location"].get("city")
        else:
            data = await fetch_weather(city=q.city)
            city = q.city

        # Успешный ответ -> пишем success
        repo.save_success(
            city=city,
            lat=data["location"]["lat"],
            lon=data["location"]["lon"],
            provider=data["provider"],
            temp_c=data["temperature"]["value"],
            observed_at_utc=data.get("observed_at_utc"),
            raw=data,
        )
        return WeatherResponse(**data)

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        # Ошибка провайдера -> запись + 502
        repo.save_provider_error(
            city=q.city,
            lat=q.lat,
            lon=q.lon,
            provider="openweather",
            error_detail=str(e),
        )
        raise HTTPException(status_code=502, detail="Upstream provider error") from e
