# 🦘 Australian Wildlife Analytics Web Dashboard

## Overview

Your enterprise-grade ETL pipeline now has a modern, interactive web interface! The dashboard provides real-time visualization and monitoring of your Australian wildlife biodiversity data.

## 🚀 Quick Start

### Option 1: Automatic Launch (Recommended)
```bash
# Windows
launch_dashboard.bat

# Or using Python (cross-platform)
python launch_dashboard.py
```

### Option 2: Manual Launch
```bash
# Ensure data exists (run ETL pipeline first if needed)
python scripts/enhanced_etl_demo.py

# Launch dashboard
python -m streamlit run streamlit_dashboard.py
```

## 📊 Dashboard Features

### 🏠 Main Dashboard
- **Real-time ETL Metrics**: Bronze/Silver/Gold layer statistics
- **Interactive Species Map**: Geographic distribution of wildlife observations
- **Species Charts**: Top observed species with dynamic filtering
- **Data Quality Indicators**: Quality scores and pipeline success rates

### 🔄 ETL Monitoring
- **Job Execution History**: Real-time ETL pipeline monitoring
- **Performance Metrics**: Duration trends and success rates
- **Quality Assessment**: Data validation results and issues
- **Pipeline Controls**: Run ETL jobs directly from the dashboard

### 📊 Data Quality Dashboard
- **Completeness Analysis**: Field-by-field data completeness
- **Quality Score Distribution**: Visual analysis of data quality
- **Source Breakdown**: Data source contributions
- **Validation Metrics**: Real-time quality monitoring

### 🐨 Species Explorer
- **Interactive Species Selection**: Explore individual species data
- **Location Analysis**: Geographic distribution patterns
- **Temporal Trends**: Observation patterns over time
- **Detailed Statistics**: Comprehensive species insights

## 🎯 Key Features

### Real-time Data Processing
```
Your ETL Pipeline → Streamlit Dashboard
     ↓                      ↑
Bronze Layer ────────────── Live Updates
Silver Layer ────────────── Interactive Charts  
Gold Layer  ────────────── Real-time Metrics
```

### Australian Biodiversity Focus
- **Native Species**: Koala, Kangaroo, Echidna, Wombat, Platypus
- **Geographic Coverage**: Continental Australia coordinate validation
- **Conservation Insights**: Quality-assured data for research
- **Real API Data**: Live iNaturalist integration

### Enterprise Features
- **Data Lineage Tracking**: Complete transformation visibility
- **Quality Monitoring**: Automated validation and alerts
- **Performance Analytics**: ETL job execution metrics
- **Multi-layer Architecture**: Bronze → Silver → Gold data lake

## 🛠️ Dashboard Navigation

1. **🏠 Dashboard**: Overview and key metrics
2. **🔄 ETL Monitoring**: Pipeline execution and performance
3. **📊 Data Quality**: Completeness and validation metrics
4. **🐨 Species Explorer**: Individual species deep-dive analysis

## 📈 Using the Dashboard

### Monitoring ETL Performance
```python
# Dashboard shows:
✅ Success Rate: 100% (15/15 jobs)
📊 Records Processed: 180 validated records  
⚡ Avg Duration: 2.3 seconds per job
🎯 Quality Score: 0.98 average
```

### Exploring Species Data
1. Navigate to **Species Explorer**
2. Select species from dropdown (e.g., "Koala")
3. View location distribution, temporal trends, and quality metrics
4. Access detailed observation tables

### Quality Monitoring
- **Real-time Validation**: See data completeness by field
- **Quality Trends**: Track improvements over time
- **Issue Detection**: Identify and resolve data quality problems

## 🔧 Advanced Usage

### Running ETL from Dashboard
1. Go to **ETL Monitoring** page
2. Click "🚀 Run ETL Pipeline Demo"
3. Monitor real-time execution
4. View updated metrics immediately

### Data Refresh
- Click "Refresh Data" in sidebar to update all visualizations
- Dashboard auto-refreshes ETL job status
- Live data updates from your ETL pipeline

## 🌐 Web Interface Details

- **URL**: http://localhost:8501
- **Framework**: Streamlit with Plotly visualizations
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live data synchronization
- **Interactive Charts**: Click, zoom, and explore data

## 🔍 Troubleshooting

### Dashboard Won't Start
```bash
# Check Python and Streamlit installation
python -m streamlit --version

# Install if missing
pip install streamlit plotly

# Launch manually
python -m streamlit run streamlit_dashboard.py
```

### No Data Showing
```bash
# Run ETL pipeline to generate data
python scripts/enhanced_etl_demo.py

# Verify database exists
ls data/aussie_wildlife.db
```

### Port Already in Use
```bash
# Use different port
python -m streamlit run streamlit_dashboard.py --server.port 8502
```

## 📊 Data Sources Integration

The dashboard displays data from your ETL pipeline:

- **Bronze Layer**: Raw API data from iNaturalist
- **Silver Layer**: Cleaned, validated Australian wildlife observations  
- **Gold Layer**: Analytics-ready biodiversity metrics
- **ETL Jobs**: Pipeline execution history and performance

## 🎯 Next Steps

1. **Schedule ETL Jobs**: Set up automated data collection
2. **Custom Dashboards**: Add your own visualizations
3. **Real-time Monitoring**: Implement data quality alerts
4. **API Integration**: Connect additional biodiversity data sources

## 🌿 Enterprise Ready

Your dashboard includes:
- ✅ **Production-grade ETL pipeline monitoring**
- ✅ **Real-time data quality assessment**  
- ✅ **Interactive species exploration**
- ✅ **Australian biodiversity focus**
- ✅ **Modern web interface**

---

**Built with Enterprise ETL Architecture | Australian Wildlife Research Focus**

🦘 **Koala** | 🦘 **Kangaroo** | 🦔 **Echidna** | 🐨 **Wombat** | 🦫 **Platypus**
