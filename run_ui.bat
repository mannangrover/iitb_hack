@echo off
REM Run InsightX Streamlit UI

echo Starting InsightX User Interface...
echo.
echo StreamLit UI will open at: http://localhost:8501
echo Make sure the FastAPI server is running (python main.py)
echo.

D:/Dhiraj/insightx_ai/.venv/Scripts/python.exe -m streamlit run app.py --logger.level=error
