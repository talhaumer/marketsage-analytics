"""
LangGraph State Definition
This module defines the state schema for the financial analysis workflow
"""

from typing import List, Optional, Dict, Any, TypedDict, Annotated


def string_reducer(existing: Optional[str], new: Optional[str]) -> Optional[str]:
    """Reducer for string values - takes the latest non-None value"""
    return new if new is not None else existing


def dict_reducer(existing: Optional[Dict[str, Any]], new: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Reducer for dict values - takes the latest non-None value"""
    return new if new is not None else existing


def error_reducer(existing: Optional[str], new: Optional[str]) -> Optional[str]:
    """Reducer for error values - concatenates errors"""
    if existing and new:
        return f"{existing}; {new}"
    return new if new is not None else existing


class State(TypedDict):
    """State schema for LangGraph financial analysis workflow"""
    # Input parameters - using Annotated for proper parallel handling
    question: Annotated[str, string_reducer]
    analysis_type: Annotated[str, string_reducer]
    symbols: Annotated[List[str], string_reducer]
    timeframe: Annotated[str, string_reducer]
    risk_tolerance: Annotated[Optional[str], string_reducer]
    
    # Agent outputs - using Annotated for proper parallel handling
    market_research: Annotated[Optional[str], string_reducer]
    financial_data: Annotated[Optional[Dict[str, Any]], dict_reducer]
    technical_analysis: Annotated[Optional[str], string_reducer]
    risk_assessment: Annotated[Optional[str], string_reducer]
    sentiment_analysis: Annotated[Optional[str], string_reducer]
    portfolio_analysis: Annotated[Optional[str], string_reducer]
    sector_analysis: Annotated[Optional[str], string_reducer]
    crypto_analysis: Annotated[Optional[str], string_reducer]
    
    # Final output
    final_analysis: Annotated[Optional[str], string_reducer]
    error: Annotated[Optional[str], error_reducer]
    
    # Metadata
    timestamp: Annotated[str, string_reducer]
    processing_time: Annotated[Optional[float], string_reducer]
