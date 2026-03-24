"""
Run the Enhanced MarketSage Analytics Frontend
Advanced Financial Analysis Platform with Multi-Agent AI
"""

import sys
import os
import socket
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def get_local_ip():
    """Get the local IP address for network access"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "localhost"

def check_backend():
    """Check if backend is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=3)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 MarketSage Analytics - Enhanced Frontend")
    print("=" * 60)
    
    # Check backend status
    if check_backend():
        print("✅ Backend API is running on http://localhost:8000")
    else:
        print("⚠️  Backend API not detected on http://localhost:8000")
        print("   Please start the backend first: python main.py")
        print()
    
    # Get network info
    local_ip = get_local_ip()
    print(f"📱 Local Access: http://localhost:7860")
    print(f"🌐 Network Access: http://{local_ip}:7860")
    print("🔧 Make sure devices are on the same network")
    print("=" * 60)
    
    # Import and run the enhanced frontend
    try:
        from frontend.gradio_app import create_interface
        
        demo = create_interface()
        demo.launch(
            server_name="0.0.0.0",  # Allow access from any IP
            server_port=7860,
            share=True,  # Create public link
            show_error=True
        )
    except ImportError as e:
        print(f"❌ Error importing frontend: {e}")
        print("Please make sure all dependencies are installed.")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        print("Please check the configuration and try again.")
