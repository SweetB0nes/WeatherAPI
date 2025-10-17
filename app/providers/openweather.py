import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

async def fetch_weather(
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> Dict[str, Any]:
    """ 
    Получает текущую погоду от OpenWeather по городу или координатам.
    Возвращает структурированные данные: местоположение, температуру, условия и провайдера.
    Требует указать либо city, либо оба параметра lat и lon.
    """
    params = {
        "appid": settings.openweather_api_key,
        "units": "metric", 
    }

    if lat is not None and lon is not None:
        params.update({"lat": lat, "lon": lon})
    elif city:
        params["q"] = city
    else:
        raise ValueError("Provide city or (lat, lon)")

    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        resp = await client.get(settings.openweather_base_url, params=params)
        resp.raise_for_status()

    data = resp.json()

    temp_c = float(data["main"]["temp"])                       
    lat_val = float(data["coord"]["lat"])
    lon_val = float(data["coord"]["lon"])
    conditions = data["weather"][0]["description"]
    city_name = data.get("name")

    return {
        "location": {"city": city_name, "lat": lat_val, "lon": lon_val},
        "temperature": {"value": round(temp_c, 1), "unit": "C"},
        "conditions": conditions,
        "provider": "openweather",
        
    }