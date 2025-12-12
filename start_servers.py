#!/usr/bin/env python3
"""
Start both Frontend and API servers
"""
import subprocess
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def start_api_server():
    """Start API server on port 5000"""
    print("🚀 Starting API Server...")
    api_cmd = [
        sys.executable,
        "-m", "uvicorn",
        "src.backend.api_server:app",
        "--host", "0.0.0.0",
        "--port", "5001"
    ]
    return subprocess.Popen(api_cmd, cwd=PROJECT_ROOT)

def start_frontend_server():
    """Start frontend server on port 8000"""
    print("🌐 Starting Frontend Server...")
    frontend_cmd = [
        sys.executable,
        "src/frontend/server.py"
    ]
    return subprocess.Popen(frontend_cmd, cwd=PROJECT_ROOT)

if __name__ == "__main__":
    print("=" * 60)
    print("🏃 Starting NACC PDF Digitizer")
    print("=" * 60)
    
    try:
        # Start API server
        api_process = start_api_server()
        time.sleep(2)
        
        # Start frontend server
        frontend_process = start_frontend_server()
        
        print("\n✅ Both servers started!")
        print(f"📱 Frontend: http://localhost:8000")
        print(f"🔧 API: http://localhost:5000")
        print(f"📖 API Docs: http://localhost:5000/docs")
        print(f"\nPress Ctrl+C to stop both servers\n")
        
        # Wait for processes
        api_process.wait()
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        api_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped")
