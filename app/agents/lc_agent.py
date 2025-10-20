from __future__ import annotations
from typing import Optional, Dict, Any

import json
import httpx

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool

from app.core.config import settings
from app.providers.openweather import fetch_weather

@tool 
async def get_weather(city: Optional[str] = None,
                lat: Optional[float] = None,
                lon: Optional[float] = None) -> Dict[str, Any]:
    """Get current weather by city (city) OR by coordinates (lat, lon). Returns JSON."""
    return await fetch_weather(city=city, lat=lat, lon=lon)


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


async def run_with_result(agent_bundle: dict, user_input: str) -> Dict[str, Any]:
    """
    Один «цикл» tool calling:
      1) user -> llm
      2) tool_calls
      3) llm формулирует финальный ответ
    """
    llm = agent_bundle["llm"]
    tools = agent_bundle["tools"]

    messages = [HumanMessage(content=user_input)]
    ai: AIMessage = await llm.ainvoke(messages)

    steps = []
    final_text: str

    if ai.tool_calls:
        for call in ai.tool_calls:
            name = call["name"]
            args = call.get("args", {})
            result = await tools[name].ainvoke(args)
            steps.append({"tool": name, "tool_input": args, "observation": result})
            messages.append(ai)
            messages.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    tool_call_id=call["id"],
                )
            )
        # Финальный ответ
        ai_final: AIMessage = await llm.ainvoke(messages)
        final_text = ai_final.content or ""
    else:
        final_text = ai.content or ""

    return {"final_text": final_text}