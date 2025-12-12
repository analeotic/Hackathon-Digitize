#!/usr/bin/env python3
"""
Simple HTTP server for frontend development
Run this script to serve the frontend on localhost:8000
"""
import http.server
import socketserver
import os
from pathlib import Path

PORT = 8000
FRONTEND_DIR = Path(__file__).parent

os.chdir(FRONTEND_DIR)

Handler = http.server.SimpleHTTPRequestHandler

print(f"🚀 Starting frontend server...")
print(f"📁 Serving: {FRONTEND_DIR}")
print(f"🌐 Open: http://localhost:{PORT}")
print(f"\nPress Ctrl+C to stop\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
