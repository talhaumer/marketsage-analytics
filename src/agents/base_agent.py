"""
Base Agent Class
Provides shared functionality for all financial analysis agents
"""

from typing import Dict, Any, Optional, List
from langchain_core.messages import HumanMessage
from abc import ABC, abstractmethod
import time
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all financial analysis agents with shared functionality"""
    
    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        self.llm = None
        self.cache = {}
    
    def get_llm(self):
        """Lazy load LLM to avoid circular imports"""
        if self.llm is None:
            from tools.groq_llm import get_llm
            self.llm = get_llm()
        return self.llm
    
    @abstractmethod
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method - must be implemented by subclasses"""
        pass
    
    def format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with provided kwargs"""
        return template.format(**kwargs)
    
    def invoke_llm(self, prompt: str) -> str:
        """Invoke LLM with error handling"""
        try:
            llm = self.get_llm()
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Error invoking LLM: {str(e)}"
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            cached_data, timestamp = self.cache[key]
            # Cache valid for 5 minutes
            if time.time() - timestamp < 300:
                return cached_data
        return None
    
    def cache_set(self, key: str, value: Any):
        """Set value in cache with timestamp"""
        self.cache[key] = (value, time.time())
    
    def handle_error(self, state: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Consistent error handling across all agents"""
        error_msg = f"{self.name} error: {str(error)}"
        if 'error' in state:
            state['error'] = f"{state['error']}; {error_msg}"
        else:
            state['error'] = error_msg
        return state
    
    def log_analysis_start(self):
        """Log the start of analysis"""
        print(f"[{datetime.now().isoformat()}] {self.name}: Starting analysis...")
    
    def log_analysis_complete(self, duration: float):
        """Log completion of analysis"""
        print(f"[{datetime.now().isoformat()}] {self.name}: Completed in {duration:.2f}s")


class FinancialDataAgent(BaseAgent):
    """Base class specifically for agents that fetch financial/market data"""
    
    def __init__(self, name: str = "FinancialDataAgent"):
        super().__init__(name)
        self.data_cache = {}
    
    def fetch_with_cache(self, key: str, fetch_func, *args, **kwargs):
        """Fetch data with caching to avoid redundant API calls"""
        cached = self.cache_get(key)
        if cached is not None:
            print(f"[{self.name}] Using cached data for {key}")
            return cached
        
        print(f"[{self.name}] Fetching fresh data for {key}")
        data = fetch_func(*args, **kwargs)
        self.cache_set(key, data)
        return data
    
    def validate_symbols(self, symbols: List[str]) -> tuple[List[str], List[str]]:
        """Validate and categorize symbols (stocks vs crypto)"""
        from utils.crypto_symbols import split_symbols
        stocks, cryptos = split_symbols([s.upper() for s in symbols])
        return stocks, cryptos


class AnalysisAgent(BaseAgent):
    """Base class for agents that provide analysis based on data"""
    
    def __init__(self, name: str = "AnalysisAgent"):
        super().__init__(name)
    
    def create_analysis_prompt(
        self, 
        role: str,
        question: str,
        data: str,
        analysis_points: List[str],
        symbols: List[str],
        timeframe: str
    ) -> str:
        """Create a standardized analysis prompt"""
        points = "\n".join([f"{i+1}. **{point}**" for i, point in enumerate(analysis_points)])
        
        prompt = f"""
        As a {role}, analyze the following information:
        
        **Question:** {question}
        **Symbols:** {', '.join(symbols) if symbols else 'General market analysis'}
        **Timeframe:** {timeframe}
        
        **Data:**
        {data}
        
        Provide a comprehensive analysis including:
        {points}
        
        Format your response in clear, professional markdown with specific insights and actionable information.
        """
        
        return prompt

