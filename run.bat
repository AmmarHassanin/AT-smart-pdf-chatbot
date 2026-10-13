@echo off
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found.
    echo Create it first: python -m venv venv
    echo Then install dependencies: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

call "venv\Scripts\activate.bat"

echo Starting AT Smart PDF Chatbot...
python -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Streamlit failed to start.
    pause
    exit /b 1
)

endlocal
