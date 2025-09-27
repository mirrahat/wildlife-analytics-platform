# 🎯 Data Engineer URL Guide

## Primary Data Engineering Interface

**Main URL**: `http://localhost:8501` (Streamlit Dashboard)

### Why This is the Data Engineer URL:

#### 🔄 **ETL Pipeline Monitoring**
- Real-time job execution tracking
- Performance metrics and trends
- Success/failure rates
- Duration analysis

#### 🏛️ **Data Lake Management** 
- Bronze layer (raw data) statistics
- Silver layer (clean data) quality metrics
- Gold layer (analytics) aggregation status
- Data flow visualization

#### 📊 **Quality Engineering**
- Field completeness analysis
- Validation rule results
- Data quality score trends
- Issue detection and alerts

#### 🚀 **Pipeline Operations**
- Execute ETL jobs directly from UI
- Monitor real-time processing
- View transformation results
- Access job execution logs

#### 📈 **Enterprise Analytics**
- Australian biodiversity insights
- Species distribution analysis
- Temporal pattern detection
- Geographic data validation

## Secondary Interface

**Alternative URL**: `http://localhost:5000` (Flask Dashboard)
- Basic data viewing
- Simple statistics
- Limited interactivity
- Static charts

## Recommended for Data Engineers

✅ **Primary**: http://localhost:8501 (Streamlit)
- Modern interface
- Real-time ETL monitoring
- Interactive analytics
- Production-grade features

⚪ **Secondary**: http://localhost:5000 (Flask)
- Basic data display
- Legacy interface
- Limited functionality

## Quick Access Commands

```bash
# Launch primary data engineering dashboard
python -m streamlit run streamlit_dashboard.py

# Or use the launcher
python launch_dashboard.py
```

## ETL Pipeline Status

✅ **Pipeline Status**: WORKING PERFECTLY
- Success Rate: 100% (recent runs) 
- Data Flow: Bronze (158) → Silver (360) → Gold (100) ✅
- Analytics Generation: 55+ metrics ✅
- Quality Score: 1.000 (perfect) ✅
- Last Updated: 2025-09-27 19:18:21

## Troubleshooting

If ETL fails, run the repair tool:
```bash
python scripts/etl_repair.py
```

---
**For Data Engineering Work → Use Port 8501**
