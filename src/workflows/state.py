"""
LangGraph State Definition

Defines the State TypedDict and the reducer functions used by the financial
analysis workflow when nodes write to shared state in parallel.
"""

from typing import Annotated, Any, Dict, List, Optional, TypedDict


def string_reducer(existing: Any, new: Any) -> Any:
    """Reducer for scalar values - takes the latest non-None value."""
    return new if new is not None else existing


def list_reducer(existing: Optional[List], new: Optional[List]) -> List:
    """Reducer for list values - last write wins, falls back to empty list."""
    if new is not None:
        return new
    return existing if existing is not None else []


def dict_reducer(existing: Optional[Dict], new: Optional[Dict]) -> Dict:
    """Reducer for dict values - merges existing with new (new wins on conflict)."""
    if existing is None and new is None:
        return {}
    if existing is None:
        return new
    if new is None:
        return existing
    return {**existing, **new}


def error_reducer(existing: Optional[str], new: Optional[str]) -> Optional[str]:
    """Reducer for error values - concatenates non-empty errors."""
    if existing and new:
        return f"{existing}; {new}"
    return new if new is not None else existing


class State(TypedDict):
    """State schema for LangGraph financial analysis workflow."""

    # Input fields
    question: Annotated[str, string_reducer]
    analysis_type: Annotated[str, string_reducer]
    symbols: Annotated[List[str], list_reducer]
    timeframe: Annotated[str, string_reducer]
    risk_tolerance: Annotated[str, string_reducer]

    # Shared pre-fetched data
    shared_market_data: Annotated[Optional[Dict], dict_reducer]

    # Per-agent outputs
    market_research: Annotated[Optional[str], string_reducer]
    financial_data: Annotated[Optional[Dict], dict_reducer]
    technical_analysis: Annotated[Optional[str], string_reducer]
    risk_assessment: Annotated[Optional[str], string_reducer]
    sentiment_analysis: Annotated[Optional[str], string_reducer]
    portfolio_analysis: Annotated[Optional[str], string_reducer]
    sector_analysis: Annotated[Optional[str], string_reducer]
    crypto_analysis: Annotated[Optional[str], string_reducer]
    final_analysis: Annotated[Optional[str], string_reducer]

    # Metadata
    individual_analyses: Annotated[Optional[Dict], dict_reducer]
    processing_time: Annotated[Optional[float], string_reducer]
    agents_used: Annotated[List[str], list_reducer]
    detection_info: Annotated[Optional[Dict], dict_reducer]
    error: Annotated[Optional[str], error_reducer]
    timestamp: Annotated[Optional[str], string_reducer]
