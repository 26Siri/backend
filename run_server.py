#!/usr/bin/env python3
"""
Simple uvicorn server runner for the plastic detection backend.
Run this from the backend directory: python run_server.py
"""
import subprocess
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
app_module = "backend.app:app"

print(f"Starting uvicorn server...")
print(f"Backend directory: {backend_dir}")
print(f"App module: {app_module}")
print(f"Server will run on http://127.0.0.1:8000")
print(f"Press Ctrl+C to stop.")
print()

try:
    # Run uvicorn
    subprocess.run(
        [sys.executable, "-m", "uvicorn", app_module, 
         "--host", "127.0.0.1", 
         "--port", "8000",
         "--reload"],
        cwd=str(backend_dir.parent),  # Run from project root
        check=False
    )
except KeyboardInterrupt:
    print("\nServer stopped.")
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
