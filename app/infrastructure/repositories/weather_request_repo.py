from typing import Optional, Dict, Any
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models import WeatherRequestRow

class WeatherRequestRepository:
    def __init__(self, session_factory=SessionLocal):
        self._sf = session_factory

    def save_success(
        self,
        *,
        city: Optional[str],
        lat: Optional[float],
        lon: Optional[float],
        provider: str,
        temp_c: Optional[float],
        observed_at_utc: Optional[str],
        raw: Dict[str, Any],
    ) -> None:
        with self._sf() as s:
            s.add(WeatherRequestRow(
                query_city=city,
                query_lat=lat,
                query_lon=lon,
                provider=provider,
                result_temp_c=temp_c,
                observed_at_utc=observed_at_utc,
                status="success",
                result_raw=raw,
            ))
            s.commit()

    def save_provider_error(
        self,
        *,
        city: Optional[str],
        lat: Optional[float],
        lon: Optional[float],
        provider: str,
        error_detail: str,
    ) -> None:
        with self._sf() as s:
            s.add(WeatherRequestRow(
                query_city=city,
                query_lat=lat,
                query_lon=lon,
                provider=provider,
                status="provider_error",
                result_raw={"error": error_detail},
            ))
            s.commit()

    def save_validation_error(
        self,
        *,
        city: Optional[str],
        lat: Optional[float],
        lon: Optional[float],
        error_detail: str,
    ) -> None:
        with self._sf() as s:
            s.add(WeatherRequestRow(
                query_city=city,
                query_lat=lat,
                query_lon=lon,
                provider=None,
                status="validation_error",
                result_raw={"error": error_detail},
            ))
            s.commit()