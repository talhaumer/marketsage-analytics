"""
LangGraph Financial Analysis Workflow
This module defines the main workflow for financial analysis using LangGraph and Gorq LLM
"""

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Optional, Dict, Any, TypedDict
import json
from datetime import datetime

from api.models import FinancialAnalysisState
from tools.gorq_llm import get_llm
from workflows.state import State
from tools.financial_tools import (
    get_stock_data,
    search_financial_news,
    calculate_portfolio_metrics,
    analyze_sector_performance,
    get_market_sentiment
)
from agents import (
    market_research_agent,
    financial_data_agent,
    technical_analysis_agent,
    risk_assessment_agent,
    sentiment_analysis_agent,
    portfolio_analysis_agent,
    sector_analysis_agent,
    crypto_agent,
    final_synthesis_agent
)


def create_financial_analysis_workflow() -> StateGraph:
    """Create the LangGraph workflow for financial analysis"""
    
    # Create the state graph
    workflow = StateGraph(State)
    
    # Add all agent nodes
    workflow.add_node("market_research", market_research_agent)
    workflow.add_node("financial_data", financial_data_agent)
    workflow.add_node("technical_analysis", technical_analysis_agent)
    workflow.add_node("risk_assessment", risk_assessment_agent)
    workflow.add_node("sentiment_analysis", sentiment_analysis_agent)
    workflow.add_node("portfolio_analysis", portfolio_analysis_agent)
    workflow.add_node("sector_analysis", sector_analysis_agent)
    workflow.add_node("crypto_analysis", crypto_agent)
    workflow.add_node("final_synthesis", final_synthesis_agent)
    
    # Define the workflow edges
    workflow.set_entry_point("market_research")
    
    # All analysis agents can run in parallel after market research
    # Using add_conditional_edges for proper parallel execution
    workflow.add_edge("market_research", "financial_data")
    workflow.add_edge("market_research", "technical_analysis")
    workflow.add_edge("market_research", "risk_assessment")
    workflow.add_edge("market_research", "sentiment_analysis")
    workflow.add_edge("market_research", "portfolio_analysis")
    workflow.add_edge("market_research", "sector_analysis")
    workflow.add_edge("market_research", "crypto_analysis")
    
    # All analyses feed into final synthesis
    workflow.add_edge("financial_data", "final_synthesis")
    workflow.add_edge("technical_analysis", "final_synthesis")
    workflow.add_edge("risk_assessment", "final_synthesis")
    workflow.add_edge("sentiment_analysis", "final_synthesis")
    workflow.add_edge("portfolio_analysis", "final_synthesis")
    workflow.add_edge("sector_analysis", "final_synthesis")
    workflow.add_edge("crypto_analysis", "final_synthesis")
    
    # Final synthesis is the end
    workflow.add_edge("final_synthesis", END)
    
    return workflow.compile()

# Create the workflow instance
financial_analysis_workflow = create_financial_analysis_workflow()
