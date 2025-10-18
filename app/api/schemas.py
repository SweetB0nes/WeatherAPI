from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

class WeatherQuery(BaseModel):
    """
    Входные данные:
    - Либо city,
    - Либо оба lat и lon.
    Диапазоны широты/долготы ограничены.
    """
    city: Optional[str] = Field(default=None, description="Название города (например, Berlin)")
    lat: Optional[float] = Field(default=None, ge=-90, le=90, description="Широта (-90..90)")
    lon: Optional[float] = Field(default=None, ge=-180, le=180, description="Долгота (-180..180)")

    def is_empty(self) -> bool:
        return (self.city is None) and not (self.lat is not None and self.lon is not None)

class Location(BaseModel):
    city: Optional[str]
    lat: float
    lon: float

class Temperature(BaseModel):
    value: float
    unit: str = "C"

class WeatherResponse(BaseModel):
    location: Location
    temperature: Temperature
    conditions: str
    provider: str
    observed_at_utc: Optional[str] = Field(
        default=None, description="Время наблюдения"
    )