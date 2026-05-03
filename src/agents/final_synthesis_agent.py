"""
Final Synthesis Agent
Combines all analyses into a comprehensive executive report with actionable recommendations.
"""

import json
import logging
from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
from tools.groq_llm import get_llm
from agents.shared_prompts import build_prompt
from workflows.state import State


def final_synthesis_agent(state: State) -> State:
    """Final Synthesis Agent - Combines all analyses into a report tailored to analysis type"""
    try:
        llm = get_llm()
        
        # Combine all analyses
        analyses = {
            'market_research': state.get('market_research', ''),
            'financial_data': (state.get('financial_data') or {}).get('analysis', ''),
            'technical_analysis': state.get('technical_analysis', ''),
            'risk_assessment': state.get('risk_assessment', ''),
            'sentiment_analysis': state.get('sentiment_analysis', ''),
            'portfolio_analysis': state.get('portfolio_analysis', ''),
            'sector_analysis': state.get('sector_analysis', ''),
            'crypto_analysis': state.get('crypto_analysis', '')
        }

        # Get analysis type
        analysis_type = state.get('analysis_type', 'comprehensive')
        symbols_list = state.get('symbols', []) or []
        symbols_text = ', '.join(symbols_list) if symbols_list else 'General market analysis'
        
        # Create tailored prompt based on analysis type
        if analysis_type == 'sentiment':
            prompt = f"""
            As a Market Sentiment Specialist, synthesize the following sentiment analysis:
            
            **Question:** {state['question']}
            **Symbols:** {symbols_text}
            **Timeframe:** {state['timeframe']}
            
            **Available Analyses:**
            - Market Research: {analyses['market_research'][:500] if analyses['market_research'] else 'N/A'}
            - Sentiment Analysis: {analyses['sentiment_analysis']}
            
            Create a SENTIMENT-FOCUSED report with:
            
            ## 😊 Sentiment Overview
            - Current market sentiment (bullish/bearish/neutral)
            - Sentiment score and confidence level
            
            ## 📰 News Sentiment Analysis
            - Recent news sentiment breakdown
            - Key themes in media coverage
            - Positive vs negative news ratio
            
            ## 💬 Social Media & Retail Sentiment
            - Social media sentiment trends
            - Retail investor mood
            - Fear & Greed indicators
            
            ## 🏦 Institutional Sentiment
            - Analyst ratings summary
            - Institutional positioning
            - Smart money signals
            
            ## 📊 Sentiment Trends
            - How sentiment has changed recently
            - Momentum and direction
            
            ## 💡 Sentiment Implications
            - What current sentiment means for prices
            - Contrarian opportunities
            - Key sentiment drivers to watch
            
            **IMPORTANT:** Focus ONLY on sentiment analysis. Do NOT provide buy/sell recommendations or price targets.
            """
        
        elif analysis_type == 'technical':
            prompt = f"""
            As a Technical Analysis Specialist, synthesize the following technical analysis:
            
            **Question:** {state['question']}
            **Symbols:** {symbols_text}
            **Timeframe:** {state['timeframe']}
            
            **Available Analyses:**
            - Technical Analysis: {analyses['technical_analysis']}
            - Financial Data: {analyses['financial_data'][:500] if analyses['financial_data'] else 'N/A'}
            
            Create a TECHNICAL ANALYSIS report with:
            
            ## 📈 Technical Summary
            - Current trend direction
            - Key support and resistance levels
            
            ## 📊 Technical Indicators
            - Moving averages (SMA, EMA)
            - RSI analysis
            - MACD signals
            - Volatility indicators
            
            ## 📉 Chart Patterns
            - Identified patterns (if any)
            - Breakout/breakdown levels
            
            ## 🎯 Trading Signals
            - Entry/exit levels
            - Stop-loss recommendations
            - Price targets based on technicals
            
            ## ⏰ Timeframe Analysis
            - Short-term outlook
            - Medium-term trends
            
            Focus on technical indicators and chart analysis.
            """
        
        elif analysis_type == 'risk':
            prompt = f"""
            As a Risk Assessment Specialist, synthesize the following risk analysis:
            
            **Question:** {state['question']}
            **Symbols:** {symbols_text}
            **Risk Tolerance:** {state.get('risk_tolerance', 'moderate')}
            
            **Available Analyses:**
            - Risk Assessment: {analyses['risk_assessment']}
            - Financial Data: {analyses['financial_data'][:500] if analyses['financial_data'] else 'N/A'}
            
            Create a RISK-FOCUSED report with:
            
            ## ⚠️ Risk Summary
            - Overall risk level
            - Key risk factors
            
            ## 📊 Risk Metrics
            - Volatility analysis
            - Beta and correlation
            - Maximum drawdown potential
            
            ## 🔍 Specific Risks
            - Market risks
            - Company-specific risks
            - Regulatory risks
            - Sector risks
            
            ## 🛡️ Risk Mitigation
            - Diversification strategies
            - Hedging opportunities
            - Position sizing recommendations
            
            ## 💼 Risk-Adjusted Returns
            - Sharpe ratio analysis
            - Risk vs reward assessment
            
            Focus on risk identification and mitigation strategies.
            """
        
        elif analysis_type == 'portfolio':
            prompt = f"""
            As a Portfolio Management Specialist, synthesize the following portfolio analysis:
            
            **Question:** {state['question']}
            **Symbols:** {symbols_text}
            **Risk Tolerance:** {state.get('risk_tolerance', 'moderate')}
            
            **Available Analyses:**
            - Portfolio Analysis: {analyses['portfolio_analysis']}
            - Risk Assessment: {analyses['risk_assessment'][:500] if analyses['risk_assessment'] else 'N/A'}
            
            Create a PORTFOLIO-FOCUSED report with:
            
            ## 📊 Portfolio Overview
            - Current allocation breakdown
            - Diversification score
            
            ## 🎯 Optimization Recommendations
            - Suggested allocation changes
            - Rebalancing strategy
            
            ## 📈 Performance Analysis
            - Expected returns
            - Risk-adjusted performance
            
            ## 🔄 Rebalancing Strategy
            - When to rebalance
            - Tactical adjustments
            
            ## 💡 Portfolio Improvements
            - Gaps in diversification
            - Alternative investments to consider
            
            Focus on portfolio optimization and allocation strategies.
            """
        
        elif analysis_type == 'crypto':
            prompt = f"""
            As a Cryptocurrency Specialist, synthesize the following crypto analysis:
            
            **Question:** {state['question']}
            **Symbols:** {symbols_text}
            **Timeframe:** {state['timeframe']}
            
            **Available Analyses:**
            - Crypto Analysis: {analyses['crypto_analysis']}
            - Market Research: {analyses['market_research'][:500] if analyses['market_research'] else 'N/A'}
            
            Create a CRYPTO-FOCUSED report with:
            
            ## 💎 Crypto Market Summary
            - Current price levels
            - Market cap and dominance
            
            ## 📊 Technical Indicators (Crypto)
            - RSI and MACD for crypto assets
            - Crypto-specific momentum indicators
            
            ## 🔗 Blockchain Metrics
            - On-chain activity (if available)
            - Network fundamentals
            
            ## 📈 Crypto Market Trends
            - DeFi and NFT impact
            - Institutional adoption signals
            
            ## ⚠️ Crypto-Specific Risks
            - Regulatory concerns
            - Market volatility
            - Security considerations
            
            Focus on cryptocurrency-specific analysis and metrics.
            """
        
        elif analysis_type == 'quick':
            prompt = f"""
            As a Financial Analyst, provide a QUICK SUMMARY:
            
            **Question:** {state['question']}
            **Symbols:** {symbols_text}
            
            **Available Analysis:**
            - Market Research: {analyses['market_research'][:300] if analyses['market_research'] else 'N/A'}
            
            Provide a brief, concise analysis (3-5 paragraphs) covering:
            1. Current market situation
            2. Key points to know
            3. Quick outlook
            
            Keep it short and actionable.
            """
        
        else:  # comprehensive or default
            prompt = build_prompt(
                role=f"Master Financial Analyst (risk tolerance: {state.get('risk_tolerance', 'moderate')})",
                question=state.get("question", ""),
                symbols=symbols_list,
                timeframe=state.get("timeframe", "1mo"),
                data_summary=json.dumps(analyses, default=str)[:3000],
                analysis_points=[
                    "Executive Summary - Key findings, market outlook, and investment thesis",
                    "Investment Recommendations - Buy/sell/hold with price targets and confidence",
                    "Risk Considerations - Key risks, mitigation, and portfolio impact",
                    "Market Outlook - Short and long-term expectations and catalysts",
                    "Actionable Next Steps - Immediate actions, monitoring schedule, contingencies",
                ],
            )

        response = llm.invoke([HumanMessage(content=prompt)])
        state['final_analysis'] = response.content if hasattr(response, 'content') else str(response)

    except Exception as exc:
        logging.getLogger(__name__).error("final_synthesis_agent error: %s", exc, exc_info=True)
        state['error'] = f"Final synthesis error: {exc}"
        state['final_analysis'] = f"Synthesis unavailable: {exc}"

    return state
