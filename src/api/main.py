"""
FastAPI Backend for LangGraph Financial Analyst with Gorq LLM
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from collections import deque
import os
from datetime import datetime
import time
import json

from workflows.financial_analysis_workflow import financial_analysis_workflow
from .models import (
    AnalysisRequest,
    PortfolioRequest,
    AnalysisResponse,
    HistoryResponse,
    AnalysisStats,
    HealthResponse,
    APIInfo,
    ErrorResponse,
    FinancialAnalysisState
)

# Initialize FastAPI app
app = FastAPI(
    title="MarketSage Analyst API",
    description="MarketSage Analytics AI Agent for Financial Analysis with Gorq LLM",
    version="1.0.0"
)

# Add CORS middleware
_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:7860,http://127.0.0.1:7860"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Models are now imported from models.py

# In-memory storage for demo purposes (capped at 100 entries)
query_history: deque = deque(maxlen=100)
analysis_cache = {}

@app.get("/", response_model=APIInfo)
async def root():
    """Root endpoint with API information"""
    return APIInfo(
        message="LangGraph Financial Analyst API",
        version="1.0.0",
        framework="LangGraph + Gorq LLM",
        endpoints={
            "/analyze": "Main financial analysis endpoint",
            "/portfolio": "Portfolio analysis endpoint",
            "/health": "Health check endpoint",
            "/history": "Query history endpoint",
            "/stats": "Analysis statistics endpoint"
        }
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        framework="LangGraph",
        llm="Gorq",
        version="1.0.0"
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_financial_data(request: AnalysisRequest):
    """
    Main financial analysis endpoint
    Runs the complete LangGraph workflow for financial analysis
    """
    start_time = time.time()
    
    try:
        # Create initial state using the correct State type
        from workflows.state import State
        initial_state = State(
            question=request.question,
            analysis_type=request.analysis_type,
            symbols=request.symbols,
            timeframe=request.timeframe,
            risk_tolerance=request.risk_tolerance,
            market_research=None,
            financial_data=None,
            technical_analysis=None,
            risk_assessment=None,
            sentiment_analysis=None,
            portfolio_analysis=None,
            sector_analysis=None,
            crypto_analysis=None,
            final_analysis=None,
            error=None,
            timestamp=datetime.now().isoformat(),
            processing_time=None
        )
        
        # Run the LangGraph workflow
        result = financial_analysis_workflow.invoke(initial_state)
        
        processing_time = time.time() - start_time
        
        # Check for errors
        if result.get('error'):
            return AnalysisResponse(
                success=False,
                error=result['error'],
                processing_time=processing_time
            )
        
        # Store in history
        query_record = {
            "timestamp": datetime.now().isoformat(),
            "question": request.question,
            "analysis_type": request.analysis_type,
            "symbols": request.symbols,
            "processing_time": processing_time,
            "response_length": len(result.get('final_analysis', ''))
        }
        query_history.append(query_record)

        # Prepare response data
        response_data = {
            "final_analysis": result.get('final_analysis', ''),
            "metadata": {
                "analysis_type": request.analysis_type,
                "symbols": request.symbols,
                "timeframe": request.timeframe,
                "risk_tolerance": request.risk_tolerance,
                "timestamp": result.get('timestamp', datetime.now().isoformat()),
                "query_id": len(query_history),
                "framework": "LangGraph",
                "llm": "Gorq"
            },
            "individual_analyses": {
                "market_research": result.get('market_research', ''),
                "financial_data": result.get('financial_data', {}).get('analysis', '') if isinstance(result.get('financial_data'), dict) else '',
                "technical_analysis": result.get('technical_analysis', ''),
                "risk_assessment": result.get('risk_assessment', ''),
                "sentiment_analysis": result.get('sentiment_analysis', ''),
                "portfolio_analysis": result.get('portfolio_analysis', ''),
                "sector_analysis": result.get('sector_analysis', ''),
                "crypto_analysis": result.get('crypto_analysis', '')
            }
        }
        
        return AnalysisResponse(
            success=True,
            data=response_data,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return AnalysisResponse(
            success=False,
            error=f"Analysis failed: {str(e)}",
            processing_time=processing_time
        )

@app.post("/portfolio", response_model=AnalysisResponse)
async def analyze_portfolio(request: PortfolioRequest):
    """
    Portfolio analysis endpoint
    Specialized analysis for portfolio optimization
    """
    start_time = time.time()
    
    try:
        # Create portfolio-specific question
        portfolio_question = f"""
        Portfolio Analysis Request:
        - Symbols: {', '.join(request.symbols)}
        - Weights: {request.weights if request.weights else 'Equal weight'}
        - Risk Tolerance: {request.risk_tolerance}
        
        Please provide comprehensive portfolio analysis and optimization recommendations.
        """
        
        # Create initial state for portfolio analysis
        from workflows.state import State
        initial_state = State(
            question=portfolio_question,
            analysis_type="portfolio",
            symbols=request.symbols,
            timeframe="1y",
            risk_tolerance=request.risk_tolerance,
            market_research=None,
            financial_data=None,
            technical_analysis=None,
            risk_assessment=None,
            sentiment_analysis=None,
            portfolio_analysis=None,
            sector_analysis=None,
            crypto_analysis=None,
            final_analysis=None,
            error=None,
            timestamp=datetime.now().isoformat(),
            processing_time=None
        )
        
        # Run the LangGraph workflow
        result = financial_analysis_workflow.invoke(initial_state)
        
        processing_time = time.time() - start_time
        
        # Check for errors
        if result.get('error'):
            return AnalysisResponse(
                success=False,
                error=result['error'],
                processing_time=processing_time
            )
        
        # Store in history
        query_record = {
            "timestamp": datetime.now().isoformat(),
            "question": portfolio_question,
            "analysis_type": "portfolio",
            "symbols": request.symbols,
            "processing_time": processing_time,
            "response_length": len(result.get('final_analysis', ''))
        }
        query_history.append(query_record)
        
        # Prepare response data
        response_data = {
            "final_analysis": result.get('final_analysis', ''),
            "metadata": {
                "analysis_type": "portfolio",
                "symbols": request.symbols,
                "weights": request.weights,
                "risk_tolerance": request.risk_tolerance,
                "timestamp": result.get('timestamp', datetime.now().isoformat()),
                "query_id": len(query_history),
                "framework": "LangGraph",
                "llm": "Gorq"
            }
        }
        
        return AnalysisResponse(
            success=True,
            data=response_data,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return AnalysisResponse(
            success=False,
            error=f"Portfolio analysis failed: {str(e)}",
            processing_time=processing_time
        )

@app.get("/history", response_model=HistoryResponse)
async def get_query_history():
    """Get query history"""
    from .models import QueryRecord
    
    # Convert dict records to QueryRecord models
    history_records = []
    for record in list(query_history)[-20:]:  # Return last 20 queries
        history_records.append(QueryRecord(**record))
    
    return HistoryResponse(
        history=history_records,
        total_queries=len(query_history)
    )

@app.get("/stats", response_model=AnalysisStats)
async def get_analysis_stats():
    """Get analysis statistics"""
    if not query_history:
        return AnalysisStats(
            total_queries=0,
            average_processing_time=0,
            analysis_types={},
            most_analyzed_symbols=[]
        )
    
    # Calculate statistics
    total_queries = len(query_history)
    avg_processing_time = sum(q.get('processing_time', 0) for q in query_history) / total_queries
    
    # Analysis type distribution
    analysis_types = {}
    for query in query_history:
        analysis_type = query.get('analysis_type', 'unknown')
        analysis_types[analysis_type] = analysis_types.get(analysis_type, 0) + 1
    
    # Most analyzed symbols
    symbol_counts = {}
    for query in query_history:
        for symbol in query.get('symbols', []):
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
    
    most_analyzed_symbols = [[symbol, count] for symbol, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    return AnalysisStats(
        total_queries=total_queries,
        average_processing_time=round(avg_processing_time, 2),
        analysis_types=analysis_types,
        most_analyzed_symbols=most_analyzed_symbols
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
