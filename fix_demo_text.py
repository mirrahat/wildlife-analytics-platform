#!/usr/bin/env python3
"""
Quick script to replace remaining 'Run Demo' with 'Run ETL Demo'
"""

# Read the file
with open('streamlit_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the text
content = content.replace("Please click 'Run Demo'", "Please click 'Run ETL Demo'")

# Write back to file
with open('streamlit_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully replaced all 'Run Demo' with 'Run ETL Demo'")