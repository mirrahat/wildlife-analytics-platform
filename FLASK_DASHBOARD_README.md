# Australian Wildlife Analytics - Flask Dashboard

🦘 **Enterprise-Grade Flask Web Interface for Australian Biodiversity Data**

## 🌟 Overview

The Flask Dashboard provides a comprehensive, modern web interface for exploring wildlife observation data and monitoring ETL pipeline results. Built specifically for Australian biodiversity research with real-time data visualization and multi-source analytics.

## 🚀 Quick Start

### Method 1: Windows Batch File (Recommended)
```bash
# Double-click or run from command prompt
launch_flask_dashboard.bat
```

### Method 2: Python Launcher
```bash
python launch_flask_dashboard.py
```

### Method 3: Direct Launch
```bash
python flask_dashboard.py
```

**Dashboard URL:** http://localhost:5000

## 📊 Dashboard Features

### 🏠 **Main Dashboard**
- **ETL Pipeline Status**: Bronze/Silver/Gold layer metrics
- **Species Distribution Map**: Interactive map of wildlife observations across Australia  
- **Top Species Charts**: Real-time observation statistics
- **Quick Actions**: Run ETL, collect multi-source data, explore species

### 🔄 **ETL Monitoring**
- **Job History**: Recent ETL job executions with status tracking
- **Performance Charts**: Success rates, duration trends, records processed
- **Real-time Execution**: Run ETL pipelines directly from the dashboard
- **Error Diagnostics**: Detailed error reporting and troubleshooting

### 📊 **Data Quality Dashboard**
- **Completeness Analysis**: Field-by-field data completeness metrics
- **Quality Score Distribution**: Statistical analysis of data quality
- **Source Validation**: Data source breakdown and validation
- **Quality Actions**: Data cleaning and validation tools

### 🐨 **Species Explorer**
- **Interactive Species Selection**: Dropdown with all available species
- **Detailed Species Metrics**: Observations, locations, quality scores
- **Location Analysis**: Top locations for each species
- **Timeline Visualization**: Observation patterns over time
- **Recent Observations**: Detailed observation records

### 🌐 **Multi-Source Analytics**
- **Cross-Platform Comparison**: Data from iNaturalist, GBIF, eBird, ALA
- **Source Quality Analysis**: Quality vs volume by data source
- **Geographic Coverage**: Multi-source observation mapping
- **Species Validation**: Cross-source species confirmation
- **Data Export**: CSV exports for analysis (summary, coordinates, full dataset)

## 🛠️ Technical Architecture

### Backend (Flask)
- **Flask Framework**: Modern Python web framework
- **SQLite Database**: Local data storage with Bronze/Silver/Gold layers
- **RESTful API**: JSON API endpoints for all dashboard functions
- **Real-time Processing**: Background ETL execution and monitoring
- **Error Handling**: Comprehensive error recovery and reporting

### Frontend (Bootstrap + Plotly)
- **Bootstrap 5**: Responsive, modern UI framework
- **Plotly.js**: Interactive charts and visualizations
- **Font Awesome**: Professional icons and styling
- **Responsive Design**: Mobile and desktop optimized
- **Real-time Updates**: AJAX-based dynamic content loading

### Data Pipeline Integration
- **ETL Pipeline**: Full integration with Bronze/Silver/Gold ETL processes
- **Multi-Source Collection**: Automated data collection from multiple APIs
- **Data Quality**: Real-time quality scoring and validation
- **Export Capabilities**: Multiple export formats and options

## 📁 File Structure

```
flask_dashboard.py              # Main Flask application
launch_flask_dashboard.py       # Dashboard launcher with checks
launch_flask_dashboard.bat      # Windows batch launcher
templates/                      # HTML templates
├── base.html                  # Base template with navigation
├── index.html                 # Main dashboard page  
├── etl_monitoring.html        # ETL monitoring interface
├── data_quality.html          # Data quality dashboard
├── species_explorer.html      # Species exploration interface
└── multi_source_analytics.html # Multi-source analytics
static/                        # Static assets (CSS, JS, images)
data/aussie_wildlife.db        # SQLite database
```

## 🔌 API Endpoints

### Core Data APIs
- `GET /api/etl-summary` - ETL pipeline summary metrics
- `GET /api/species-map` - Species distribution map data
- `GET /api/species-observations` - Species observation charts
- `GET /api/species/<name>` - Individual species details

### Monitoring APIs  
- `GET /api/etl-performance` - ETL performance charts
- `GET /api/data-quality-charts` - Data quality visualizations
- `GET /api/multisource-analytics` - Multi-source analysis data

### Action APIs
- `POST /api/run-etl` - Execute ETL pipeline
- `POST /api/run-multisource` - Run multi-source collection
- `GET /api/export/<type>` - Export data (summary/coordinates/full)

## 🎛️ Dashboard Controls

### Navigation Bar
- **Dashboard**: Main overview and metrics
- **ETL Monitoring**: Pipeline status and performance  
- **Data Quality**: Completeness and validation metrics
- **Species Explorer**: Individual species analysis
- **Multi-Source Analytics**: Cross-platform data comparison

### Quick Actions
- **Run ETL**: Execute complete ETL pipeline demonstration
- **Refresh**: Reload dashboard data
- **Export Data**: Download analysis results
- **Multi-Source Collection**: Gather data from multiple APIs

## 🔧 Configuration

### Environment Variables
```bash
FLASK_DEBUG=1                   # Enable debug mode
FLASK_ENV=development           # Development environment
```

### Database Configuration
- **Default Path**: `data/aussie_wildlife.db`
- **Auto-Creation**: Database created automatically by ETL pipeline
- **Schema**: Bronze/Silver/Gold layers with job tracking

### Port Configuration
- **Default Port**: 5000
- **Alternative Ports**: 5001, 5002, 5003, 8000, 8080 (auto-detected)
- **URL**: http://localhost:[port]

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# The launcher automatically finds alternative ports
# Or manually specify: python flask_dashboard.py --port 5001
```

**2. Database Not Found**
```bash
# Run ETL pipeline to generate data
python scripts/enhanced_etl_demo.py
```

**3. Missing Dependencies**
```bash
# Install required packages
pip install -r requirements.txt
```

**4. Import Errors**
```bash
# Check Python path and package installation
python -c "import flask, pandas, plotly; print('All packages available')"
```

### Manual Debugging
```bash
# Check Flask installation
python -c "import flask; print(flask.__version__)"

# Test database connection
python -c "import sqlite3; print('DB access:', sqlite3.connect('data/aussie_wildlife.db'))"

# Verify port availability  
python -c "import socket; s=socket.socket(); print('Port 5000:', s.connect_ex(('localhost', 5000)))"
```

## 📈 Performance Optimization

### Database Optimization
- **Indexed Queries**: Key fields indexed for fast lookups
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized SQL for large datasets

### Frontend Performance  
- **Lazy Loading**: Charts loaded on demand
- **Responsive Design**: Optimized for all screen sizes
- **Caching**: Browser caching for static assets
- **Compression**: Minified CSS and JavaScript

### Scalability
- **Modular Design**: Easy to extend with new features
- **API-First**: RESTful design for integration
- **Database Agnostic**: Can be adapted for PostgreSQL/MySQL
- **Cloud Ready**: Deployable to AWS/Azure/GCP

## 🔄 Development Workflow

### Adding New Features
1. **Backend**: Add new route in `flask_dashboard.py`
2. **API**: Create corresponding API endpoint
3. **Frontend**: Add HTML template and JavaScript
4. **Testing**: Test with sample data
5. **Documentation**: Update README and comments

### Database Schema Updates
1. **Migration**: Update ETL pipeline schema
2. **Dashboard**: Modify database queries
3. **API**: Update API responses
4. **Frontend**: Adjust visualizations
5. **Testing**: Validate with new/old data

## 🌐 Deployment Options

### Local Development
```bash
python flask_dashboard.py
# Access: http://localhost:5000
```

### Production Deployment
```bash
# Using Gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 flask_dashboard:app

# Using Docker
docker build -t wildlife-dashboard .
docker run -p 5000:5000 wildlife-dashboard
```

### Cloud Deployment
- **AWS**: Deploy to Elastic Beanstalk or ECS
- **Azure**: Deploy to App Service or Container Instances  
- **GCP**: Deploy to App Engine or Cloud Run
- **Heroku**: Direct deployment with git integration

## 🤝 Integration Points

### ETL Pipeline
- **Bronze Layer**: Raw API data ingestion
- **Silver Layer**: Cleaned and standardized data
- **Gold Layer**: Analytics-ready aggregations
- **Job Tracking**: Execution history and performance

### External APIs
- **iNaturalist**: Citizen science observations
- **GBIF**: Global biodiversity database
- **eBird**: Bird observation data
- **Atlas of Living Australia**: Australian species data

### Export Formats
- **CSV**: Comma-separated values for analysis
- **JSON**: Structured data for applications
- **Excel**: Formatted spreadsheets
- **PDF**: Reports and summaries

---

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the Flask application logs
3. Verify database and API connectivity
4. Check system requirements and dependencies

**Happy Exploring! 🦘🌿**
