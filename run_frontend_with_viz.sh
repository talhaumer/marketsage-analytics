#!/bin/bash

# Run MarketSage Analytics Frontend with Visualizations

echo "📊 MarketSage Analytics - Frontend with Visualizations"
echo "======================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install visualization dependencies
echo "📦 Installing visualization dependencies..."
pip install plotly==5.24.1 kaleido==0.2.1 --quiet

# Check if backend is running
echo "🔍 Checking backend API..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend API not running on http://localhost:8000"
    echo "   Please start the backend first: python main.py"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Backend API is running"
fi

# Run the enhanced frontend
echo ""
echo "🚀 Starting enhanced frontend with visualizations..."
echo "📊 Features: AI Analysis + Interactive Charts"
echo "📱 Local:   http://localhost:7860"
echo "🌐 Network: http://$(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $1}'):7860"
echo ""

python src/frontend/gradio_app_with_viz.py

