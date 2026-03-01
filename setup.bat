@echo off
REM InsightX Setup Script for Windows

echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete! 
echo.
echo Next steps:
echo 1. (Optional) Edit .env file to add OpenAI API key
echo 2. Load data: python -m src.database.data_loader
echo 3. Run server: python main.py
echo.
echo API will be available at: http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo.
echo Note: SQLite database will be created automatically!

