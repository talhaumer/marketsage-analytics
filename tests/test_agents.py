"""Integration tests for agent functions using MockLLM."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

import os
os.environ.pop("GROQ_API_KEY", None)  # force MockLLM

import pytest


def _base_state(**kwargs):
    defaults = dict(
        question="What is the outlook for AAPL?",
        analysis_type="quick",
        symbols=["AAPL"],
        timeframe="1mo",
        risk_tolerance="moderate",
        shared_market_data={},
        market_research=None,
        financial_data=None,
        technical_analysis=None,
        risk_assessment=None,
        sentiment_analysis=None,
        portfolio_analysis=None,
        sector_analysis=None,
        crypto_analysis=None,
        final_analysis=None,
        individual_analyses=None,
        processing_time=None,
        agents_used=[],
        detection_info=None,
        error=None,
        timestamp=None,
    )
    defaults.update(kwargs)
    return defaults


def test_market_research_agent_sets_output():
    from agents.market_research_agent import market_research_agent
    result = market_research_agent(_base_state())
    assert "market_research" in result
    assert isinstance(result["market_research"], str)
    assert result["market_research"]


def test_financial_data_agent_sets_output():
    from agents.financial_data_agent import financial_data_agent
    result = financial_data_agent(_base_state())
    assert "financial_data" in result


def test_sentiment_analysis_agent_sets_output():
    from agents.sentiment_analysis_agent import sentiment_analysis_agent
    result = sentiment_analysis_agent(_base_state())
    assert "sentiment_analysis" in result
    assert isinstance(result.get("sentiment_analysis"), str)


def test_crypto_agent_sets_output_for_crypto_symbols():
    from agents.crypto_agent import crypto_agent
    result = crypto_agent(_base_state(symbols=["BTC", "ETH"], analysis_type="crypto"))
    assert "crypto_analysis" in result


def test_final_synthesis_agent_produces_final_analysis():
    from agents.final_synthesis_agent import final_synthesis_agent
    result = final_synthesis_agent(_base_state(
        market_research="Market looks positive.",
        financial_data={"analysis": "Revenue growing."},
        technical_analysis="RSI at 55, MACD bullish.",
        risk_assessment="Moderate risk.",
        sentiment_analysis="Positive sentiment.",
        portfolio_analysis="Well diversified.",
        sector_analysis="Tech sector outperforming.",
        crypto_analysis="N/A for stocks.",
    ))
    assert "final_analysis" in result
    assert result["final_analysis"]


def test_sector_agent_handles_empty_symbols():
    from agents.sector_analysis_agent import sector_analysis_agent
    result = sector_analysis_agent(_base_state(symbols=[]))
    assert "sector_analysis" in result
