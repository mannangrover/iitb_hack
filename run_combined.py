#!/usr/bin/env python
"""
Run both FastAPI backend and Streamlit frontend in a single process.
FastAPI runs on port 8000, Streamlit runs on the PORT environment variable.
"""
import subprocess
import os
import sys
import time

def run_combined():
    # Start FastAPI backend in the background
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the API time to start and load data (can take 1-2 minutes for 250K records)
    print("⏳ Starting FastAPI backend and loading data (this may take 1-2 minutes)...")
    time.sleep(5)
    
    # Get the port for Streamlit
    port = os.getenv("PORT", "8501")
    
    # Start Streamlit frontend
    print(f"🎈 Starting Streamlit on port {port}...")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", 
         "--server.port", port,
         "--server.address", "0.0.0.0",
         "--logger.level=info"],
    )
    
    # Wait for Streamlit process
    streamlit_process.wait()

if __name__ == "__main__":
    run_combined()
