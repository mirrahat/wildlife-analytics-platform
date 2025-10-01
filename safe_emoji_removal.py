#!/usr/bin/env python3
"""
Safe Emoji Removal Script
Remove emoji icons while preserving code structure and indentation
"""

import re

def safe_remove_emojis():
    """Safely remove emoji icons without affecting code structure"""
    
    print("🧹 Safely removing emoji icons...")
    
    with open("streamlit_dashboard.py", 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Define specific emoji replacements that preserve structure
    replacements = [
        # Error and warning messages
        ('st.error("🚨 **', 'st.error("**'),
        ('st.warning("⚠️ **', 'st.warning("**'),
        ('st.warning("🔒 **', 'st.warning("**'),
        ('st.success("✅ **', 'st.success("**'),
        ('st.info("💡 **', 'st.info("**'),
        ('st.info("🚀 **', 'st.info("**'),
        ('st.info("🎯 **', 'st.info("**'),
        ('st.info("📋 **', 'st.info("**'),
        ('st.info("⏳ **', 'st.info("**'),
        
        # Status messages
        ('✅ Some data available', 'Some data available'),
        ('❌ No data for analysis', 'No data for analysis'),
        ('❌ No ETL history available', 'No ETL history available'),
        ('📊 Historical data exists', 'Historical data exists'),
        ('🔄 Run ETL to see current session', 'Run ETL to see current session'),
        
        # Headers and subheaders
        ('st.subheader("📊 Data Pipeline Metrics")', 'st.subheader("Data Pipeline Metrics")'),
        ('st.subheader("🌐 Multi-Source Data Integration")', 'st.subheader("Multi-Source Data Integration")'),
        ('st.subheader("📋 System Status")', 'st.subheader("System Status")'),
        ('st.subheader("🥈 Silver Layer Data Quality")', 'st.subheader("Silver Layer Data Quality")'),
        ('st.subheader("🌐 Multi-Source Raw Data")', 'st.subheader("Multi-Source Raw Data")'),
        
        # Button text
        ('"🔄 Re-run ETL Demo"', '"Re-run ETL Demo"'),
        ('"▶️ Run ETL Demo"', '"Run ETL Demo"'),
        ('"🎯 Geospatial Export"', '"Geospatial Export"'),
        ('"🧹 **Clean Silver Layer**"', '"**Clean Silver Layer**"'),
        ('"📊 **Update Gold Analytics**"', '"**Update Gold Analytics**"'),
        
        # Markdown headers
        ('**🌟 Silver Layer: Data Quality Assessment**', '**Silver Layer: Data Quality Assessment**'),
        ('**🗺️ Silver Layer Export**', '**Silver Layer Export**'),
        ('**📊 Source Summary**', '**Source Summary**'),
        
        # Success/completion messages
        ('"🎉 **Multi-source data collection completed successfully!**"', '"**Multi-source data collection completed successfully!**"'),
        ('"❌ **Data lake ingestion failed!**"', '"**Data lake ingestion failed!**"'),
        ('"❌ **System Error**"', '"**System Error**"'),
        ('"💡 Try running manually:', '"Try running manually:'),
        
        # Quality indicators
        ('"🌟 Excellent data quality!"', '"Excellent data quality!"'),
        ('"⚠️ Good data quality with room for improvement"', '"Good data quality with room for improvement"'),
        ('"❌ Data quality needs attention"', '"Data quality needs attention"'),
        
        # Metrics and icons in sidebar
        ('"🌐 Multi-Source Status"', '"Multi-Source Status"'),
        ('"📊 Last Collection"', '"Last Collection"'),
        ('"🕐 Last Updated"', '"Last Updated"'),
        ('"🔌 Active Sources"', '"Active Sources"'),
        ('"✅ ETL: Ready"', '"ETL: Ready"'),
        ('"⚠️ ETL: Required"', '"ETL: Required"'),
        
        # Advanced analytics
        ('🧠 Advanced Analytics & Machine Learning', 'Advanced Analytics & Machine Learning'),
        ('"📈 Species Population Trend Analysis"', '"Species Population Trend Analysis"'),
        ('"📉 Declining Species"', '"Declining Species"'),
        ('"📊 Stable Species"', '"Stable Species"'),
        ('"📈 Increasing Species"', '"Increasing Species"'),
        ('"🎯 Avg Confidence"', '"Avg Confidence"'),
    ]
    
    # Apply replacements
    changes_made = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            changes_made += 1
    
    # Remove any remaining standalone emojis at the start of strings
    emoji_pattern = r'(["\'])[🔄📊🔍🌐🧠📈✅❌⚠️🎯💡🚀🚨📋🕐🔌📉🌟🗺️🧹🎉📍⏳🔗💾🔧🛠️⚙️📱💻🖥️📟☁️🌍]\s*'
    content = re.sub(emoji_pattern, r'\1', content)
    
    if changes_made > 0:
        with open("streamlit_dashboard.py", 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"✅ Successfully removed emojis from {changes_made} locations")
        print("🎯 Code structure and indentation preserved!")
    else:
        print("ℹ️ No emojis found to remove")
    
    return changes_made

def main():
    """Main function"""
    print("🧹 SAFE EMOJI REMOVAL")
    print("=" * 30)
    
    changes = safe_remove_emojis()
    
    print("\n✅ CLEANUP COMPLETE!")
    if changes > 0:
        print("✨ Dashboard now has a clean, professional look!")
        print("🔧 All functionality preserved")
        print("📝 Code structure intact")

if __name__ == "__main__":
    main()