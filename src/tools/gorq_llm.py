"""
Groq LLM Integration Module
This module provides integration with Groq LLM for the financial analysis system.
"""

from typing import List, Dict, Any, Optional
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

# Removed old GorqLLM class - now using ChatGroq directly

def create_gorq_llm(
    api_key: Optional[str] = None,
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.1,
    max_tokens: int = 2048
) -> ChatGroq:
    """
    Create a Groq LLM instance
    
    Args:
        api_key: Groq API key (if None, will try to get from environment)
        model: Groq model name
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
    
    Returns:
        ChatGroq instance
    """
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        model_name=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

def get_llm() -> BaseLanguageModel:
    """
    Get Groq LLM with automatic fallback to mock LLM
    """
    try:
        # Try to create Groq LLM
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            print("No GROQ_API_KEY found in environment, using mock LLM...")
            return create_mock_llm()
        
        return create_gorq_llm(api_key=api_key)
    except Exception as e:
        print(f"Groq LLM not available: {e}")
        print("Creating a mock LLM for testing purposes...")
        return create_mock_llm()

def create_mock_llm() -> BaseLanguageModel:
    """Create a mock LLM for testing when no real LLM is available"""
    from langchain_core.language_models.base import BaseLanguageModel
    from langchain_core.messages import BaseMessage, AIMessage
    from typing import List, Optional, Any, Dict
    
    class MockLLM(BaseLanguageModel):
        def _call(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any) -> str:
            # Extract the last message content
            if messages:
                last_message = messages[-1].content
                # Generate a simple response based on the content
                if "market research" in last_message.lower():
                    return "**Market Research Analysis**\n\nBased on current market conditions, I've analyzed the provided information. The market shows mixed signals with some sectors performing well while others face challenges. Recent news indicates moderate volatility, and investors should remain cautious but optimistic about long-term prospects."
                elif "financial data" in last_message.lower():
                    return "**Financial Data Analysis**\n\nI've processed the financial data for the requested symbols. The analysis shows varying performance across different metrics. Key indicators suggest moderate growth potential with some areas of concern that warrant further monitoring."
                elif "technical analysis" in last_message.lower():
                    return "**Technical Analysis**\n\nTechnical indicators show mixed signals. Some stocks are in oversold territory while others appear overbought. Moving averages suggest a neutral to slightly bullish trend, but momentum indicators are inconclusive."
                elif "risk assessment" in last_message.lower():
                    return "**Risk Assessment**\n\nOverall risk level is moderate. The portfolio shows good diversification, but there are some concentration risks in certain sectors. Volatility levels are within acceptable ranges, and downside protection measures should be considered."
                elif "sentiment analysis" in last_message.lower():
                    return "**Sentiment Analysis**\n\nMarket sentiment appears neutral to slightly positive. News sentiment shows mixed signals with some positive developments offset by concerns about market volatility. Social media sentiment is cautiously optimistic."
                elif "portfolio analysis" in last_message.lower():
                    return "**Portfolio Analysis**\n\nThe portfolio shows good diversification across sectors. Performance metrics indicate moderate returns with acceptable risk levels. Some rebalancing may be beneficial to optimize the risk-return profile."
                elif "sector analysis" in last_message.lower():
                    return "**Sector Analysis**\n\nTechnology and healthcare sectors show strong performance, while energy and utilities face headwinds. Consumer discretionary sectors are mixed, reflecting broader economic uncertainty."
                else:
                    return "**Analysis Summary**\n\nI've completed a comprehensive analysis of the requested information. The data shows mixed signals across different metrics, suggesting a cautious but not pessimistic outlook. Further monitoring and regular updates are recommended."
            return "**Analysis Complete**\n\nI've processed your request and provided a comprehensive analysis based on the available information."
        
        @property
        def _llm_type(self) -> str:
            return "mock"
        
        def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any) -> str:
            return self._call(messages, stop, run_manager, **kwargs)
        
        def invoke(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> str:
            return self._call(messages, stop, **kwargs)
        
        def predict(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> str:
            return self._call(messages, stop, **kwargs)
        
        def predict_messages(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> List[BaseMessage]:
            response = self._call(messages, stop, **kwargs)
            return [AIMessage(content=response)]
        
        def generate_prompt(self, prompts: List[Dict[str, Any]], stop: Optional[List[str]] = None, **kwargs: Any) -> List[BaseMessage]:
            return [AIMessage(content=self._call([HumanMessage(content=str(prompt))], stop, **kwargs)) for prompt in prompts]
        
        async def agenerate_prompt(self, prompts: List[Dict[str, Any]], stop: Optional[List[str]] = None, **kwargs: Any) -> List[BaseMessage]:
            return self.generate_prompt(prompts, stop, **kwargs)
        
        async def apredict(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> str:
            return self._call(messages, stop, **kwargs)
        
        async def apredict_messages(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> List[BaseMessage]:
            return self.predict_messages(messages, stop, **kwargs)
    
    return MockLLM()
