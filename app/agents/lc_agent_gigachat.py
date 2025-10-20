import json
from typing import Dict, Any, Optional
from langchain_gigachat import GigaChat as ChatGigaChat
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from app.core.config import settings
from app.providers.openweather import fetch_weather  # тот же провайдер

@tool(
    "get_weather",
    description="Возвращает текущую погоду (OpenWeather). Укажите city или lat+lon."
)
async def get_weather_tool(city: Optional[str] = None,
                           lat: Optional[float] = None,
                           lon: Optional[float] = None) -> Dict[str, Any]:
    return await fetch_weather(city=city, lat=lat, lon=lon)

def build_agent() -> dict:
    llm = ChatGigaChat(
        credentials=settings.gigachat_credentials,
        scope=getattr(settings, "gigachat_scope", "GIGACHAT_API_PERS"),
        verify_ssl_certs=getattr(settings, "gigachat_verify_ssl", "false"),
        model=getattr(settings, "gigachat_model", "GigaChat"),
        temperature=0.2,
    )

    tools = [get_weather_tool]
    return {
        "llm": llm.bind_tools(tools),
        "tools": {t.name: t for t in tools},
        "system_prompt": (
            "Ты помощник-погодник. Для вопросов о погоде используй инструмент get_weather "
            "с параметрами (city ИЛИ lat+lon), затем кратко сформулируй ответ."
        ),
    }

async def run_with_result(agent_bundle: dict, user_input: str) -> Dict[str, Any]:
    llm = agent_bundle["llm"]
    tools = agent_bundle["tools"]
    sp = agent_bundle["system_prompt"]

    messages = [HumanMessage(content=f"{sp}\n\nПользователь: {user_input}")]
    ai: AIMessage = await llm.ainvoke(messages)

    while getattr(ai, "tool_calls", None):
        for call in ai.tool_calls:
            name = call["name"]
            args = call.get("args", {}) or {}
            result = await tools[name].ainvoke(args)
            messages.append(ai)
            messages.append(ToolMessage(
                content=json.dumps(result, ensure_ascii=False),
                tool_call_id=call["id"],
            ))
        ai = await llm.ainvoke(messages)

    return {"final_text": ai.content or ""}