import httpx

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import ORJSONResponse

from app.api.schemas import WeatherQuery, WeatherResponse, AgentQueryRequest, AgentQueryResponse
from app.providers.openweather import fetch_weather  
from app.infrastructure.repositories.weather_request_repo import WeatherRequestRepository
from app.infrastructure.repositories.agent_request_repo import AgentRequestRepository

from app.agents.lc_agent import build_agent, run_with_result
from app.agents.lc_agent_gigachat import build_agent as build_gigachat_agent
from app.agents.lc_agent_gigachat import run_with_result as run_gigachat

weather_repo = WeatherRequestRepository()
agent_repo = AgentRequestRepository()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent_bundle = build_agent()

    try:
        app.state.gigachat_bundle = build_gigachat_agent()
    except Exception:
        app.state.gigachat_bundle = None

    yield

app = FastAPI(
    title="Weather API",
    version="0.4.0",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,  
)

# ------------------------------
# 1) Старый REST-эндпоинт погоды
# ------------------------------
@app.get("/healthz")
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
        weather_repo.save_validation_error(
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
        weather_repo.save_success(
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
        weather_repo.save_provider_error(
            city=q.city,
            lat=q.lat,
            lon=q.lon,
            provider="openweather",
            error_detail=str(e),
        )
        raise HTTPException(status_code=502, detail="Upstream provider error") from e


# -----------------------------------------
# 2) Новый эндпоинт: агент + лог в БД (текст)
# -----------------------------------------
@app.post("/api/v1/agent-query", response_model=AgentQueryResponse, summary="Ask GPT (agent) about weather")
async def agent_query(req: AgentQueryRequest, request: Request):
    try:
        bundle = request.app.state.agent_bundle
        result = await run_with_result(bundle, req.query) # {"final_text": "..."}
        answer_text = result.get("final_text") or ""

        row_id = agent_repo.save_success(query_text=req.query, response={"final_text": answer_text})
        return AgentQueryResponse(id=row_id, status="success", answer=answer_text)

    except Exception as e:
        if hasattr(agent_repo, "save_error"):
            agent_repo.save_error(query_text=req.query, error_detail=str(e))
        return AgentQueryResponse(id=0, status="error", answer="", error=str(e))

@app.post("/api/v1/agent-query-gigachat", response_model=AgentQueryResponse, summary="Ask GigaChat (agent) about weather")
async def agent_query_gigachat(req: AgentQueryRequest, request: Request):
    try:
        bundle = getattr(request.app.state, "gigachat_bundle", None)
        if bundle is None:
            raise HTTPException(status_code=503, detail="GigaChat agent is not configured")

        result = await run_gigachat(bundle, req.query)
        answer_text = result.get("final_text") or ""

        row_id = agent_repo.save_success(query_text=req.query, response={"final_text": answer_text})
        return AgentQueryResponse(id=row_id, status="success", answer=answer_text)

    except Exception as e:
        if hasattr(agent_repo, "save_error"):
            agent_repo.save_error(query_text=req.query, error_detail=str(e))
        return AgentQueryResponse(id=0, status="error", answer="", error=str(e))