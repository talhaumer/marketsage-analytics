"""Groq LLM factory with MockLLM fallback for development without an API key."""
import os
from typing import Any, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class MockLLM(BaseChatModel):
    model_name: str = "mock-llm"

    @property
    def _llm_type(self) -> str:
        return "mock"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        last = messages[-1].content if messages else ""
        text = last.lower()

        if any(k in text for k in ("crypto", "bitcoin", "ethereum", "btc", "eth")):
            content = (
                "## Crypto Analysis (Mock)\n\n**Trend:** Bullish momentum.\n\n"
                "**Key Metrics:** Volume up 15%, RSI at 58.\n\n"
                "*Note: Mock data - set GROQ_API_KEY for real analysis.*"
            )
        elif any(k in text for k in ("risk", "volatility", "downside")):
            content = (
                "## Risk Assessment (Mock)\n\n**Risk Level:** Moderate\n\n"
                "**Volatility:** Within normal range.\n\n"
                "*Note: Mock data - set GROQ_API_KEY for real analysis.*"
            )
        elif any(k in text for k in ("technical", "rsi", "macd", "chart")):
            content = (
                "## Technical Analysis (Mock)\n\n**Signal:** Neutral.\n\n"
                "**Indicators:** RSI 52, MACD flat.\n\n"
                "*Note: Mock data - set GROQ_API_KEY for real analysis.*"
            )
        else:
            content = (
                "## Market Analysis (Mock)\n\n**Outlook:** Mixed signals.\n\n"
                "**Recommendation:** Monitor key levels.\n\n"
                "*Note: Mock data - set GROQ_API_KEY for real analysis.*"
            )

        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])


def get_llm(model: str = "llama-3.3-70b-versatile", temperature: float = 0.1) -> BaseChatModel:
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, temperature=temperature, api_key=api_key,
                        max_retries=3, timeout=30)
    return MockLLM()
