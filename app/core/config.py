from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """ 
    Конфиг
    """
    openweather_api_key: str
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5/weather"
    http_timeout: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()