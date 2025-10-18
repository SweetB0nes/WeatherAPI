# Weather API

## Быстрый старт (Docker Compose)

1. В корне создайте .env:

        OPENWEATHER_API_KEY=<ваш_ключ_из_openweather>
   
        OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5/weather
   
        HTTP_TIMEOUT=5
   
        DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/weather

2. Поднимите окружение:

       docker compose up --build
3. Проверьте:

        curl "http://localhost:8000/healthz"
        curl "http://localhost:8000/api/v1/weather?city=Berlin"

   ## Примеры
       curl "http://localhost:8000/healthz"
       {"status":"ok"}

       curl "http://localhost:8000/api/v1/weather?city=Moscow"
       {"location":{"city":"Moscow","lat":55.7522,"lon":37.6156},"temperature":{"value":6.1,"unit":"C"},"conditions":"light rain","provider":"openweather","observed_at_utc":"2025-10-18T21:21:30+00:00"}

       curl "http://localhost:8000/api/v1/weather?lat=52.52&lon=13.405"
       {"location":{"city":"Mitte","lat":52.52,"lon":13.405},"temperature":{"value":6.1,"unit":"C"},"conditions":"clear sky","provider":"openweather","observed_at_utc":"2025-10-18T21:25:02+00:00"}

       curl "http://localhost:8000/api/v1/weather"
       {"detail":"Provide city or (lat, lon)"}
