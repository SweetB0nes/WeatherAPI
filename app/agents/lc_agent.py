from __future__ import annotations
from typing import Optional, Dict, Any

import json
import httpx

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool

from app.core.config import settings


def _fetch_weather(city: Optional[str] = None,
                   lat: Optional[float] = None,
                   lon: Optional[float] = None) -> Dict[str, Any]:
    """Синхронный вызов OpenWeather на httpx"""
    if (lat is not None and lon is not None):
        params = {"lat": lat, "lon": lon}
    elif city:
        params = {"q": city}
    else:
        raise ValueError("Provide city or (lat, lon)")

    params.update({
        "appid": settings.openweather_api_key,
        "units": "metric",
    })

    with httpx.Client(timeout=settings.http_timeout) as client:
        r = client.get(settings.openweather_base_url, params=params)
        r.raise_for_status()
        data = r.json()

    return {
        "location": {
            "city": data.get("name"),
            "lat": float(data["coord"]["lat"]),
            "lon": float(data["coord"]["lon"]),
        },
        "temperature": {"value": round(float(data["main"]["temp"]), 1), "unit": "C"},
        "conditions": data["weather"][0]["description"],
        "provider": "openweather",
        "observed_at_utc": data.get("dt"),
    }


@tool 
def get_weather(city: Optional[str] = None,
                lat: Optional[float] = None,
                lon: Optional[float] = None) -> Dict[str, Any]:
    """Get current weather by city (city) OR by coordinates (lat, lon). Returns JSON."""
    return _fetch_weather(city=city, lat=lat, lon=lon)


def build_agent() -> dict:
    """
    Возвращаем «bundle»:
      - llm_with_tools: ChatOpenAI
      - tool_map: словарь вызова инструмента по имени
    """
    llm_kwargs = {
        "api_key": settings.openai_api_key,
        "model": settings.openai_model,
        "temperature": 0,
    }
    
    if settings.openai_base_url:
        llm_kwargs["base_url"] = settings.openai_base_url

    llm = ChatOpenAI(**llm_kwargs)
    llm_with_tools = llm.bind_tools([get_weather])
    return {"llm": llm_with_tools, "tools": {"get_weather": get_weather}}


def run_with_result(agent_bundle: dict, user_input: str) -> Dict[str, Any]:
    """
    Один «цикл» tool calling:
      1) user -> llm
      2) tool_calls
      3) llm формулирует финальный ответ
    """
    llm = agent_bundle["llm"]
    tools = agent_bundle["tools"]

    messages = [HumanMessage(user_input)]
    ai: AIMessage = llm.invoke(messages)

    steps = []
    final_text: str

    if ai.tool_calls:
        for call in ai.tool_calls:
            name = call["name"]
            args = call.get("args", {})
            result = tools[name].invoke(args)
            steps.append({"tool": name, "tool_input": args, "observation": result})
            messages.append(ai)
            messages.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    tool_call_id=call["id"],
                )
            )
        # Финальный ответ 
        ai_final: AIMessage = llm.invoke(messages)
        final_text = ai_final.content or ""
    else:
        final_text = ai.content or ""

    return {"final_text": final_text}