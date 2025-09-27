@echo off
echo 🦘 Launching Australian Wildlife Analytics Dashboard...
echo =======================================================

echo Checking if database exists...
if not exist "data\aussie_wildlife.db" (
    echo ⚠️  Database not found! Running ETL pipeline first...
    echo Running data collection and ETL processing...
    python scripts\enhanced_etl_demo.py
    echo ✅ ETL pipeline completed!
    echo.
)

echo 🚀 Starting Streamlit web dashboard...
echo 📊 Dashboard will open in your browser at: http://localhost:8501
echo 
echo Press Ctrl+C to stop the dashboard
echo.

python -m streamlit run streamlit_dashboard.py

echo.
echo Dashboard stopped. Thanks for using the Australian Wildlife Analytics Platform!
pause
