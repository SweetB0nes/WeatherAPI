from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from .session import Base

class WeatherRequestRow(Base):
    __tablename__ = "weather_requests"

    id = Column(Integer, primary_key=True)
    requested_at_utc = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    query_city = Column(String, nullable=True)
    query_lat = Column(Float, nullable=True)
    query_lon = Column(Float, nullable=True)

    provider = Column(String, nullable=True)                 # 'openweather'
    result_temp_c = Column(Float, nullable=True)             # температура при успехе
    observed_at_utc = Column(String, nullable=True)          # ISO 8601 
    status = Column(String, nullable=False)                  # 'success' | 'provider_error' | 'validation_error'

    result_raw = Column(JSON, nullable=True)                 # часть ответа или ошибка