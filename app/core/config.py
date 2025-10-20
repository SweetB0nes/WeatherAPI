from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """ 
    Конфиг
    """
    openweather_api_key: str
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5/weather"
    http_timeout: int = 5
    
    database_url: str | None = None

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None

    gigachat_credentials: str | None = None
    gigachat_scope: str = "GIGACHAT_API_PERS"   # или GIGACHAT_API_CORP
    gigachat_verify_ssl: bool = False
    gigachat_model: str = "GigaChat"            # или "GigaChat-Pro"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()