#!/bin/bash
# Run InsightX Streamlit UI

echo "Starting InsightX User Interface..."
echo ""
echo "Streamlit UI will open at: http://localhost:8501"
echo "Make sure the FastAPI server is running (python main.py)"
echo ""

python -m streamlit run app.py --logger.level=error
