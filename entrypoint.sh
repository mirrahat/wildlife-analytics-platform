#!/bin/bash
# Azure App Service startup script for Streamlit

python -m streamlit run streamlit_dashboard.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true