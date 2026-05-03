import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

import pytest
from api.models import AnalysisRequest, IndividualAnalyses


def test_symbol_with_dot_is_valid():
    req = AnalysisRequest(
        question="Analyze Berkshire",
        symbols=["BRK.B"],
        analysis_type="quick",
    )
    assert "BRK.B" in req.symbols


def test_symbol_with_number_is_valid():
    req = AnalysisRequest(
        question="Analyze 1INCH",
        symbols=["1INCH"],
        analysis_type="quick",
    )
    assert "1INCH" in req.symbols


def test_individual_analyses_has_crypto_field():
    ia = IndividualAnalyses(
        market_research="x",
        financial_data="x",
        technical_analysis="x",
        risk_assessment="x",
        sentiment_analysis="x",
        portfolio_analysis="x",
        sector_analysis="x",
        crypto_analysis="x",
    )
    assert ia.crypto_analysis == "x"


def test_question_too_long_raises():
    with pytest.raises(Exception):
        AnalysisRequest(
            question="x" * 1001,
            symbols=["AAPL"],
            analysis_type="quick",
        )
