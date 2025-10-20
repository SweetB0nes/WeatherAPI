# Weather API (main)

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

# Weather API (feat/agent-openweather)

## Быстрый старт (Docker Compose)

1. В корне создайте .env:

        OPENWEATHER_API_KEY=<ваш_ключ_из_openweather>
   
        OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5/weather
   
        HTTP_TIMEOUT=5
   
        DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/weather

        OPENAI_API_KEY=<ваш_ключ_из_gpt>
        OPENAI_MODEL=gpt-4o-mini

   Если используется проки сервис (например proxyAPI)
   
        OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1

   GigaChat

        GIGACHAT_CREDENTIALS=<ваш_ключ_из_GigaChat-API>
        GIGACHAT_SCOPE=GIGACHAT_API_PERS
        GIGACHAT_VERIFY_SSL=false
        GIGACHAT_MODEL=GigaChat-Pro

3. Поднимите окружение:

       docker compose up --build
4. Проверьте:

        curl "http://localhost:8000/healthz"

   ## Примеры
       curl "http://localhost:8000/healthz"
       {"status":"ok"}

       curl "http://localhost:8000/api/v1/weather?city=Moscow"
       {"location":{"city":"Moscow","lat":55.7522,"lon":37.6156},"temperature":{"value":6.1,"unit":"C"},"conditions":"light rain","provider":"openweather","observed_at_utc":"2025-10-18T21:21:30+00:00"}

       curl -X POST "http://localhost:8000/api/v1/agent-query" ^
          -H "Content-Type: application/json" ^
          -d "{\"query\":\"Какая погода в Москве сейчас?\"}"
        {"id":1,"status":"success","answer":"Сейчас в Москве температура составляет 5.9°C, погода облачная.","error":null}
   
       curl -X POST "http://localhost:8000/api/v1/agent-query" ^
          -H "Content-Type: application/json" ^
          -d "{\"query\":\"Погода для широты 43.60 и долготы 39.73\"}"
       {"id":2,"status":"success","answer":"В Сочи (широта 43.60, долгота 39.73) сейчас температура составляет 16.1°C, и наблюдаются сильные дожди.","error":null}

       curl -X POST "http://localhost:8000/api/v1/agent-query-gigachat" ^
          -H "Content-Type: application/json" ^
          -d "{\"query\":\"Какая погода в Москве сейчас?\"}"
       {"id":3,"status":"success","answer":"Сейчас в Москве облачно, температура воздуха около 5°C.","error":null}
   
       curl -X POST "http://localhost:8000/api/v1/agent-query-gigachat" ^
          -H "Content-Type: application/json" ^
          -d "{\"query\":\"Погода для широты 43.60 и долготы 39.73\"}"
       {"id":2,"status":"success","answer":"На указанных координатах сейчас облачно, температура воздуха +14°C. Город — Сочи.","error":null}
