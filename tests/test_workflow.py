"""
Tests for the financial analysis workflow.
"""

import pytest
from src.workflows.financial_analysis_workflow import create_financial_analysis_workflow, FinancialAnalysisState


def test_workflow_creation():
    """Test that the workflow can be created successfully."""
    workflow = create_financial_analysis_workflow()
    assert workflow is not None


def test_financial_analysis_state():
    """Test the FinancialAnalysisState structure."""
    state = FinancialAnalysisState(
        question="Test question",
        analysis_type="comprehensive",
        symbols=["AAPL"],
        timeframe="1y",
        timestamp="2024-01-01T00:00:00Z"
    )
    assert state["question"] == "Test question"
    assert state["analysis_type"] == "comprehensive"
    assert state["symbols"] == ["AAPL"]
    assert state["timeframe"] == "1y"


if __name__ == "__main__":
    pytest.main([__file__])
