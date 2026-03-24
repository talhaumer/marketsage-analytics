"""
Pydantic Models for MarketSage Analytics API
This module contains all the data models used for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union, TypedDict, Annotated
from datetime import datetime
from enum import Enum
import operator


class AnalysisType(str, Enum):
    """Enumeration of supported analysis types"""
    COMPREHENSIVE = "comprehensive"
    QUICK = "quick"
    TECHNICAL = "technical"
    RISK = "risk"
    SENTIMENT = "sentiment"
    PORTFOLIO = "portfolio"


class RiskTolerance(str, Enum):
    """Enumeration of risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class Timeframe(str, Enum):
    """Enumeration of supported timeframes"""
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YEAR_TO_DATE = "ytd"
    MAX = "max"


class AnalysisRequest(BaseModel):
    """Request model for financial analysis"""
    question: str = Field(..., min_length=1, max_length=1000, description="The financial question to analyze")
    analysis_type: AnalysisType = Field(default=AnalysisType.COMPREHENSIVE, description="Type of analysis to perform")
    symbols: List[str] = Field(default=[], max_items=20, description="Stock symbols to analyze")
    timeframe: Timeframe = Field(default=Timeframe.ONE_YEAR, description="Time period for analysis")
    risk_tolerance: Optional[RiskTolerance] = Field(default=RiskTolerance.MODERATE, description="Risk tolerance level")

    @validator('symbols')
    def validate_symbols(cls, v):
        """Validate stock symbols format"""
        if not v:
            return v
        
        for symbol in v:
            if not symbol or not symbol.strip():
                raise ValueError("Symbols cannot be empty")
            if len(symbol.strip()) > 10:
                raise ValueError(f"Symbol {symbol} is too long (max 10 characters)")
            if not symbol.strip().isalpha():
                raise ValueError(f"Symbol {symbol} contains invalid characters")
        
        return [s.strip().upper() for s in v]

    @validator('question')
    def validate_question(cls, v):
        """Validate question content"""
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "question": "What's the market outlook for AI and technology stocks?",
                "analysis_type": "comprehensive",
                "symbols": ["AAPL", "MSFT", "GOOGL"],
                "timeframe": "1y",
                "risk_tolerance": "moderate"
            }
        }


class PortfolioRequest(BaseModel):
    """Request model for portfolio analysis"""
    symbols: List[str] = Field(..., min_items=1, max_items=50, description="Stock symbols in the portfolio")
    weights: Optional[List[float]] = Field(default=None, description="Portfolio weights for each symbol")
    risk_tolerance: Optional[RiskTolerance] = Field(default=RiskTolerance.MODERATE, description="Risk tolerance level")

    @validator('symbols')
    def validate_symbols(cls, v):
        """Validate stock symbols format"""
        if not v:
            raise ValueError("At least one symbol is required")
        
        for symbol in v:
            if not symbol or not symbol.strip():
                raise ValueError("Symbols cannot be empty")
            if len(symbol.strip()) > 10:
                raise ValueError(f"Symbol {symbol} is too long (max 10 characters)")
            if not symbol.strip().isalpha():
                raise ValueError(f"Symbol {symbol} contains invalid characters")
        
        return [s.strip().upper() for s in v]

    @validator('weights')
    def validate_weights(cls, v, values):
        """Validate portfolio weights"""
        if v is None:
            return v
        
        symbols = values.get('symbols', [])
        if len(v) != len(symbols):
            raise ValueError("Number of weights must match number of symbols")
        
        if not all(0 <= weight <= 1 for weight in v):
            raise ValueError("All weights must be between 0 and 1")
        
        total_weight = sum(v)
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError(f"Total weights must equal 1.0, got {total_weight}")
        
        return v

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"],
                "weights": [0.2, 0.2, 0.2, 0.2, 0.2],
                "risk_tolerance": "moderate"
            }
        }


class AnalysisMetadata(BaseModel):
    """Metadata for analysis results"""
    analysis_type: str = Field(..., description="Type of analysis performed")
    symbols: List[str] = Field(default=[], description="Symbols analyzed")
    timeframe: str = Field(..., description="Timeframe used for analysis")
    risk_tolerance: Optional[str] = Field(default=None, description="Risk tolerance level")
    timestamp: str = Field(..., description="Analysis timestamp")
    query_id: int = Field(..., description="Unique query identifier")
    framework: str = Field(default="LangGraph", description="Framework used")
    llm: str = Field(default="Gorq", description="LLM used")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")


class IndividualAnalyses(BaseModel):
    """Individual analysis results from different agents"""
    market_research: Optional[str] = Field(default=None, description="Market research analysis")
    financial_data: Optional[str] = Field(default=None, description="Financial data analysis")
    technical_analysis: Optional[str] = Field(default=None, description="Technical analysis")
    risk_assessment: Optional[str] = Field(default=None, description="Risk assessment")
    sentiment_analysis: Optional[str] = Field(default=None, description="Sentiment analysis")
    portfolio_analysis: Optional[str] = Field(default=None, description="Portfolio analysis")
    sector_analysis: Optional[str] = Field(default=None, description="Sector analysis")


class AnalysisData(BaseModel):
    """Data structure for analysis results"""
    final_analysis: str = Field(..., description="Final synthesized analysis")
    metadata: AnalysisMetadata = Field(..., description="Analysis metadata")
    individual_analyses: Optional[IndividualAnalyses] = Field(default=None, description="Individual agent analyses")


class AnalysisResponse(BaseModel):
    """Response model for financial analysis"""
    success: bool = Field(..., description="Whether the analysis was successful")
    data: Optional[AnalysisData] = Field(default=None, description="Analysis results data")
    error: Optional[str] = Field(default=None, description="Error message if analysis failed")
    processing_time: Optional[float] = Field(default=None, description="Total processing time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "final_analysis": "Based on comprehensive analysis...",
                    "metadata": {
                        "analysis_type": "comprehensive",
                        "symbols": ["AAPL", "MSFT"],
                        "timeframe": "1y",
                        "risk_tolerance": "moderate",
                        "timestamp": "2024-01-01T12:00:00",
                        "query_id": 1,
                        "framework": "LangGraph",
                        "llm": "Gorq",
                        "processing_time": 45.2
                    }
                },
                "processing_time": 45.2
            }
        }


class QueryRecord(BaseModel):
    """Record of a query for history tracking"""
    timestamp: str = Field(..., description="Query timestamp")
    question: str = Field(..., description="Original question")
    analysis_type: str = Field(..., description="Type of analysis performed")
    symbols: List[str] = Field(default=[], description="Symbols analyzed")
    processing_time: float = Field(..., description="Processing time in seconds")
    response_length: int = Field(..., description="Length of response in characters")


class HistoryResponse(BaseModel):
    """Response model for query history"""
    history: List[QueryRecord] = Field(..., description="List of recent queries")
    total_queries: int = Field(..., description="Total number of queries")


class AnalysisStats(BaseModel):
    """Analysis statistics model"""
    total_queries: int = Field(..., description="Total number of queries")
    average_processing_time: float = Field(..., description="Average processing time")
    analysis_types: Dict[str, int] = Field(..., description="Distribution of analysis types")
    most_analyzed_symbols: List[List[Union[str, int]]] = Field(..., description="Most analyzed symbols with counts")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Check timestamp")
    framework: str = Field(..., description="Framework name")
    llm: str = Field(..., description="LLM name")
    version: str = Field(..., description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00",
                "framework": "LangGraph",
                "llm": "Gorq",
                "version": "1.0.0"
            }
        }


class APIInfo(BaseModel):
    """API information model"""
    message: str = Field(..., description="API message")
    version: str = Field(..., description="API version")
    framework: str = Field(..., description="Framework name")
    endpoints: Dict[str, str] = Field(..., description="Available endpoints")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "LangGraph Financial Analyst API",
                "version": "1.0.0",
                "framework": "LangGraph + Gorq LLM",
                "endpoints": {
                    "/analyze": "Main financial analysis endpoint",
                    "/portfolio": "Portfolio analysis endpoint",
                    "/health": "Health check endpoint",
                    "/history": "Query history endpoint"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Analysis failed",
                "detail": "Invalid symbols provided",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


# Workflow State Models
class FinancialAnalysisState(TypedDict):
    """State for the financial analysis workflow"""
    # Input parameters
    question: str
    analysis_type: str
    symbols: List[str]
    timeframe: str
    risk_tolerance: Optional[str]
    
    # Agent outputs
    market_research: Optional[str]
    financial_data: Optional[Dict[str, Any]]
    technical_analysis: Optional[str]
    risk_assessment: Optional[str]
    sentiment_analysis: Optional[str]
    portfolio_analysis: Optional[str]
    sector_analysis: Optional[str]
    
    # Final output
    final_analysis: Optional[str]
    error: Optional[str]
    
    # Metadata
    timestamp: str
    processing_time: Optional[float]
