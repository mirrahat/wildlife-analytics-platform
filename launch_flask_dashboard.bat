@echo off
echo.
echo =================================================
echo    Australian Wildlife Analytics - Flask Dashboard
echo =================================================
echo.
echo Starting Flask Web Dashboard...
echo.
echo Dashboard Features:
echo   - Real-time ETL Pipeline Monitoring
echo   - Interactive Species Explorer  
echo   - Multi-Source Data Analytics
echo   - Data Quality Dashboard
echo   - Australian Biodiversity Insights
echo.
echo Press Ctrl+C to stop the server
echo =================================================
echo.

cd /d "%~dp0"
python launch_flask_dashboard.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start Flask dashboard
    echo.
    echo Troubleshooting:
    echo   1. Ensure Python is installed and in PATH
    echo   2. Install dependencies: pip install -r requirements.txt
    echo   3. Try manual start: python flask_dashboard.py
    echo.
    pause
)
