"""
Demo script for MarketSage Analytics
This script demonstrates the system working without requiring API keys
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def demo_financial_tools():
    """Demonstrate financial tools working"""
    print("🔧 Testing Financial Tools...")
    
    try:
        from tools.financial_tools import get_stock_data, search_financial_news
        
        # Test stock data
        print("📊 Fetching stock data for AAPL...")
        stock_data = get_stock_data.invoke({"symbols": ["AAPL"], "timeframe": "1d"})
        
        if "AAPL" in stock_data and "error" not in stock_data["AAPL"]:
            aapl_data = stock_data["AAPL"]
            print(f"✅ AAPL Data Retrieved:")
            print(f"   Current Price: ${aapl_data['price_data']['current_price']:.2f}")
            print(f"   Volume: {aapl_data['price_data']['volume']:,}")
            print(f"   Market Cap: ${aapl_data['info']['market_cap']:,}")
            print(f"   Sector: {aapl_data['info']['sector']}")
        else:
            print("❌ Failed to retrieve AAPL data")
            return False
        
        # Test news search
        print("\n📰 Fetching financial news...")
        news = search_financial_news.invoke({"query": "Apple stock news", "max_results": 3})
        
        if news and len(news) > 0:
            print(f"✅ Retrieved {len(news)} news articles:")
            for i, article in enumerate(news[:2], 1):
                print(f"   {i}. {article['title'][:60]}...")
        else:
            print("❌ Failed to retrieve news")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Financial tools error: {e}")
        return False

def demo_workflow_creation():
    """Demonstrate workflow creation"""
    print("\n🔄 Testing Workflow Creation...")
    
    try:
        from workflows.financial_analysis_workflow import create_financial_analysis_workflow
        
        workflow = create_financial_analysis_workflow()
        print("✅ LangGraph workflow created successfully")
        print(f"   Workflow type: {type(workflow).__name__}")
        
        # Show workflow structure
        if hasattr(workflow, 'nodes'):
            print(f"   Number of nodes: {len(workflow.nodes)}")
            print("   Nodes:", list(workflow.nodes.keys()))
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow creation error: {e}")
        return False

def demo_api_structure():
    """Demonstrate API structure"""
    print("\n🌐 Testing API Structure...")
    
    try:
        from api.main import app
        
        print("✅ FastAPI app created successfully")
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        
        # Show available routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        print(f"   Available routes: {len(routes)}")
        for route in routes[:5]:  # Show first 5 routes
            print(f"     - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ API structure error: {e}")
        return False

def demo_frontend_structure():
    """Demonstrate frontend structure"""
    print("\n🖥️ Testing Frontend Structure...")
    
    try:
        # Check if frontend file exists and can be imported
        frontend_path = src_path / "frontend" / "gradio_app.py"
        if frontend_path.exists():
            print("✅ Gradio frontend file exists")
            print(f"   Frontend path: {frontend_path}")
            
            # Read first few lines to check structure
            with open(frontend_path, 'r') as f:
                lines = f.readlines()[:10]
                if any('gradio' in line.lower() for line in lines):
                    print("   ✅ Gradio imports detected")
                if any('langgraph' in line.lower() for line in lines):
                    print("   ✅ LangGraph integration detected")
                if any('gorq' in line.lower() for line in lines):
                    print("   ✅ Gorq LLM integration detected")
            
            return True
        else:
            print("❌ Frontend file not found")
            return False
        
    except Exception as e:
        print(f"❌ Frontend structure error: {e}")
        return False

def main():
    """Run the demo"""
    print("🚀 LangGraph Financial Analyst with Gorq LLM - Demo")
    print("=" * 60)
    
    demos = [
        ("Financial Tools", demo_financial_tools),
        ("Workflow Creation", demo_workflow_creation),
        ("API Structure", demo_api_structure),
        ("Frontend Structure", demo_frontend_structure)
    ]
    
    passed = 0
    total = len(demos)
    
    for demo_name, demo_func in demos:
        print(f"\n{'='*20} {demo_name} {'='*20}")
        if demo_func():
            passed += 1
            print(f"✅ {demo_name} demo completed successfully")
        else:
            print(f"❌ {demo_name} demo failed")
    
    print(f"\n{'='*60}")
    print(f"📊 Demo Results: {passed}/{total} demos passed")
    
    if passed == total:
        print("\n🎉 All demos passed! The LangGraph Financial Analyst system is ready.")
        print("\n📋 Next Steps:")
        print("1. Set up your API keys in .env file:")
        print("   - GORQ_API_KEY=your_gorq_api_key_here")
        print("   - OPENAI_API_KEY=your_openai_api_key_here (fallback)")
        print("2. Run the backend: python main.py")
        print("3. Run the frontend: python run_frontend.py")
        print("4. Access the app at http://localhost:8501")
    else:
        print(f"\n⚠️ {total - passed} demos failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
