#!/usr/bin/env python3
"""
Australian Wildlife Data Streamlit Dashboard
==========================================
Modern, interactive web interface for exploring wildlife observation data and ETL pipeline results.

Features:
- Real-time data visualization with Plotly
- ETL pipeline monitoring
- Interactive species exploration
- Data quality dashboard
- Australian biodiversity insights

Run with: streamlit run streamlit_dashboard.py
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import os
import sys
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Page configuration
st.set_page_config(
    page_title="Australian Wildlife Analytics",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    .stMetric {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    
    /* Compact sidebar styling */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Make sidebar buttons smaller */
    .stSidebar .stButton > button {
        height: 35px !important;
        padding: 4px 8px !important;
        font-size: 14px !important;
        margin-bottom: 4px !important;
        line-height: 1.2 !important;
    }
    
    /* Reduce sidebar title and text sizes */
    .stSidebar h1 {
        font-size: 20px !important;
        margin-bottom: 10px !important;
        padding-bottom: 5px !important;
    }
    
    .stSidebar h2 {
        font-size: 16px !important;
        margin-bottom: 8px !important;
        margin-top: 8px !important;
    }
    
    .stSidebar h3 {
        font-size: 14px !important;
        margin-bottom: 6px !important;
        margin-top: 6px !important;
    }
    
    /* Reduce sidebar text and markdown spacing */
    .stSidebar .stMarkdown {
        margin-bottom: 4px !important;
    }
    
    .stSidebar p {
        font-size: 13px !important;
        margin-bottom: 4px !important;
    }
    
    /* Make sidebar metrics more compact */
    .stSidebar .metric-container {
        margin-bottom: 6px !important;
    }
    
    /* Reduce sidebar selectbox height */
    .stSidebar .stSelectbox {
        margin-bottom: 6px !important;
    }
    
    /* Compact sidebar sections */
    .stSidebar hr {
        margin: 8px 0 !important;
    }
    
    /* Reduce caption text size */
    .stSidebar .caption {
        font-size: 11px !important;
        margin-top: 2px !important;
        margin-bottom: 6px !important;
    }
    
    /* Sliding Developer Credit Popup */
    .developer-popup {
        position: fixed;
        top: 20px;
        right: -400px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 999999;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        font-size: 16px;
        animation: slideInAndOut 6s ease-in-out;
        white-space: nowrap;
    }
    
    @keyframes slideInAndOut {
        0% {
            right: -400px;
            opacity: 0;
        }
        15% {
            right: 20px;
            opacity: 1;
        }
        70% {
            right: 20px;
            opacity: 1;
        }
        100% {
            right: -400px;
            opacity: 0;
        }
    }
    
    .developer-popup::before {
        content: "�";
        margin-right: 10px;
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

class WildlifeDashboard:
    def __init__(self, db_path="data/aussie_wildlife.db"):
        self.db_path = db_path
        
    def get_connection(self):
        """Get database connection"""
        if not os.path.exists(self.db_path):
            st.error(f"Database not found: {self.db_path}")
            st.info("Run the ETL pipeline first to generate data.")
            return None
        return sqlite3.connect(self.db_path)
    
    def load_wildlife_observations(self):
        """Load wildlife observations data"""
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
        
        try:
            df = pd.read_sql_query("""
                SELECT * FROM wildlife_observations
                ORDER BY observed_date DESC
            """, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading wildlife data: {e}")
            return pd.DataFrame()
    
    def load_etl_layers_summary(self):
        """Load ETL layers summary"""
        conn = self.get_connection()
        if conn is None:
            return {}
        
        try:
            cursor = conn.cursor()
            
            # Bronze layer
            cursor.execute("SELECT COUNT(*) FROM wildlife_bronze")
            bronze_count = cursor.fetchone()[0]
            
            # Silver layer
            cursor.execute("SELECT COUNT(*) FROM wildlife_silver")
            silver_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(quality_score) FROM wildlife_silver")
            avg_quality = cursor.fetchone()[0] or 0
            
            # Gold layer
            cursor.execute("SELECT COUNT(*) FROM wildlife_gold")
            gold_count = cursor.fetchone()[0]
            
            # Multi-source layer
            try:
                cursor.execute("SELECT COUNT(*) FROM wildlife_multisource")
                multisource_count = cursor.fetchone()[0]
            except:
                multisource_count = 0
            
            # ETL jobs
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN status = 'success' THEN 1 END) as successful
                FROM etl_job_executions
            """)
            job_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'bronze_count': bronze_count,
                'silver_count': silver_count,
                'gold_count': gold_count,
                'multisource_count': multisource_count,
                'avg_quality': avg_quality,
                'total_jobs': job_stats[0],
                'successful_jobs': job_stats[1]
            }
        except Exception as e:
            st.error(f"Error loading ETL summary: {e}")
            return {}
    
    def load_etl_job_history(self):
        """Load ETL job execution history"""
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
        
        try:
            df = pd.read_sql_query("""
                SELECT job_name, status, 
                       records_extracted, records_transformed, records_loaded,
                       datetime(start_time) as start_time,
                       datetime(end_time) as end_time,
                       ROUND((julianday(end_time) - julianday(start_time)) * 86400, 2) as duration_seconds,
                       quality_issues
                FROM etl_job_executions
                ORDER BY start_time DESC
                LIMIT 20
            """, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading ETL history: {e}")
            return pd.DataFrame()
    
    def load_silver_layer_data(self):
        """Load cleaned data from silver layer"""
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
        
        try:
            df = pd.read_sql_query("""
                SELECT common_name, scientific_name, location_description,
                       latitude, longitude, observed_date, observer_name,
                       data_source, processed_at, quality_score
                FROM wildlife_silver
                WHERE common_name IS NOT NULL
                ORDER BY processed_at DESC
            """, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading silver layer data: {e}")
            return pd.DataFrame()
    
    def load_multisource_data(self):
        """Load multi-source data from all 4 biodiversity APIs"""
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
        
        try:
            df = pd.read_sql_query("""
                SELECT common_name, scientific_name, location_description,
                       latitude, longitude, observed_date, observer_name,
                       data_source, collected_at
                FROM wildlife_multisource
                WHERE common_name IS NOT NULL
                ORDER BY collected_at DESC
            """, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading multi-source data: {e}")
            return pd.DataFrame()
    
    def check_etl_execution_status(self, check_session_state=True):
        """Check if ETL pipeline has been executed recently"""
        
        # If checking session state and ETL was run in current session, return True
        if check_session_state:
            import streamlit as st
            if hasattr(st, 'session_state') and getattr(st.session_state, 'etl_run_in_session', False):
                # Get data counts to show in message
                conn = self.get_connection()
                if conn is not None:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM wildlife_multisource")
                        multisource_count = cursor.fetchone()[0]
                        cursor.execute("SELECT COUNT(*) FROM etl_job_executions WHERE status = 'success'")
                        job_count = cursor.fetchone()[0]
                        conn.close()
                        return True, f"ETL executed in current session ({multisource_count} multi-source records, {job_count} successful jobs)"
                    except:
                        conn.close()
                        return True, "ETL executed in current session"
                return True, "ETL executed in current session"
        
        # If ETL hasn't been run in current session, always return False
        # This forces the user to run ETL in this session to see the "executed recently" status
        return False, "ETL needs to be executed - click 'Run ETL Demo' to collect fresh wildlife data"
    
    def has_sufficient_data(self):
        """Check if we have sufficient data to show meaningful results"""
        conn = self.get_connection()
        if conn is None:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Check multisource data count
            cursor.execute("SELECT COUNT(*) FROM wildlife_multisource")
            multisource_count = cursor.fetchone()[0]
            
            # Check silver data count  
            cursor.execute("SELECT COUNT(*) FROM wildlife_silver")
            silver_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Consider sufficient if we have either substantial multisource data or silver data
            return multisource_count >= 100 or silver_count >= 50
            
        except Exception as e:
            conn.close()
            return False
    
    def load_multi_source_data(self):
        """Load multi-source data from data lake inventory (Bronze layer)"""
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
        
        try:
            # Try to load from data_lake_inventory which has the multi-source data
            df = pd.read_sql_query("""
                SELECT record_data, data_source, created_at, record_count
                FROM data_lake_inventory
                WHERE data_layer = 'bronze'
                AND record_data IS NOT NULL
                ORDER BY created_at DESC
            """, conn)
            
            if df.empty:
                # Fallback to wildlife_sightings if available
                df = pd.read_sql_query("""
                    SELECT common_name, scientific_name, location as location_description,
                           latitude, longitude, observation_date as observed_date, 
                           observer_name, data_source, created_at
                    FROM wildlife_sightings
                    WHERE common_name IS NOT NULL
                    ORDER BY created_at DESC
                """, conn)
            
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading multi-source data: {e}")
            return pd.DataFrame()

def render_main_dashboard():
    """Render the main dashboard"""
    
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("Australian Wildlife Analytics Platform")
    st.markdown("**Enterprise ETL Pipeline & Biodiversity Data Explorer**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    dashboard = WildlifeDashboard()
    
    # Check ETL status for main dashboard
    etl_executed, etl_message = dashboard.check_etl_execution_status()
    has_data = dashboard.has_sufficient_data()
    
    # Show ETL status banner and conditional content
    if not etl_executed or not has_data:
        st.error("🚨 **ETL Pipeline Not Executed** - Click 'Run ETL Demo' in sidebar to collect wildlife data")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("📋 **Step 1**: Click sidebar 'Run ETL Demo'")
        with col2:
            st.info("⏳ **Step 2**: Wait for completion")
        with col3:
            st.info("🎯 **Step 3**: Explore full dashboard")
        
        # Show placeholder metrics when ETL not run
        st.markdown("---")
        st.subheader("📊 Data Pipeline Metrics")
        st.info("🚀 **Metrics will appear here after running ETL Demo**")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Bronze Layer (Raw Data)", "---", help="Run ETL Demo to see data")
        with col2:
            st.metric("Silver Layer (Cleaned)", "---", help="Run ETL Demo to see data")
        with col3:
            st.metric("Gold Layer (Analytics)", "---", help="Run ETL Demo to see data")
        with col4:
            st.metric("Multi-Source Records", "---", help="Run ETL Demo to see data")
        with col5:
            st.metric("Average Quality Score", "---", help="Run ETL Demo to see data")
        with col6:
            st.metric("ETL Success Rate", "---", help="Run ETL Demo to see data")
        
        st.markdown("---")
        st.warning("🔒 **All dashboard features locked** - Run ETL Demo to unlock data visualizations and analytics")
        return  # Exit early, don't show any data
    
    else:
        st.success(f"✅ **System Ready**: {etl_message}")
        
        # Load ETL summary only when ETL has been executed
        etl_summary = dashboard.load_etl_layers_summary()
        
        if etl_summary:
            # Enhanced Multi-Source Metrics Row
            col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric(
                label="Bronze Layer (Raw Data)",
                value=f"{etl_summary['bronze_count']:,}",
                help="Raw data records from APIs"
            )
        
        with col2:
            st.metric(
                label="Silver Layer (Cleaned)",
                value=f"{etl_summary['silver_count']:,}",
                help="Validated and standardized records"
            )
        
        with col3:
            st.metric(
                label="Gold Layer (Analytics)",
                value=f"{etl_summary['gold_count']:,}",
                help="Analytics-ready aggregations"
            )
        
        with col4:
            # Multi-source data count
            multisource_count = etl_summary.get('multisource_count', 0)
            st.metric(
                label="Multi-Source Records",
                value=f"{multisource_count:,}",
                help="Cross-platform validated records"
            )
        
        with col5:
            st.metric(
                label="Average Quality Score",
                value=f"{etl_summary['avg_quality']:.3f}",
                help="Average data quality score (0-1)"
            )
        
        with col6:
            success_rate = 0
            if etl_summary['total_jobs'] > 0:
                success_rate = (etl_summary['successful_jobs'] / etl_summary['total_jobs']) * 100
            
            st.metric(
                label="ETL Success Rate",
                value=f"{success_rate:.1f}%",
                help=f"{etl_summary['successful_jobs']}/{etl_summary['total_jobs']} jobs"
            )
        
        st.markdown("---")
        
        # Multi-Source Data Overview (only show when ETL executed)
        if etl_summary.get('multisource_count', 0) > 0:
            st.subheader("🌐 Multi-Source Data Integration")
            
            # Load and display source breakdown
            conn = dashboard.get_connection()
            if conn:
                try:
                    multisource_data = pd.read_sql_query("""
                        SELECT source, COUNT(*) as count 
                        FROM wildlife_multisource 
                        GROUP BY source
                    """, conn)
                    conn.close()
                
                    if not multisource_data.empty:
                        col1, col2, col3 = st.columns([2, 1, 1])
                    
                        with col1:
                            # Source distribution chart
                            fig = px.pie(
                                multisource_data,
                                values='count',
                                names='source',
                                title="Active Data Sources Distribution"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                        with col2:
                            st.markdown("**📊 Source Summary**")
                            for _, row in multisource_data.iterrows():
                                source_icon = "🔵" if row['source'] == 'iNaturalist' else "🟢"
                                st.markdown(f"{source_icon} **{row['source']}**: {row['count']:,} records")
                    
                        with col3:
                            total_sources = len(multisource_data)
                            total_records = multisource_data['count'].sum()
                            avg_per_source = total_records / total_sources if total_sources > 0 else 0
                            
                            st.metric("Active Sources", total_sources)
                            st.metric("Total Records", f"{total_records:,}")
                            st.metric("Avg per Source", f"{avg_per_source:.0f}")
                except Exception as e:
                    st.warning("Multi-source data unavailable")
            
            st.markdown("---")
    
        # Data visualizations (only show when ETL executed)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Species Distribution Map")
        
            # Load silver layer data for mapping
            silver_data = dashboard.load_silver_layer_data()
            
            if not silver_data.empty and 'latitude' in silver_data.columns:
                # Filter for valid coordinates
                map_data = silver_data.dropna(subset=['latitude', 'longitude'])
            
                if not map_data.empty:
                    fig = px.scatter_map(
                        map_data,
                        lat="latitude",
                        lon="longitude",
                        hover_name="common_name",
                        hover_data={"location_description": True, "observed_date": True, "quality_score": ":.3f"},
                        color="common_name",
                        zoom=4,
                        height=500,
                        title="Wildlife Observations Across Australia"
                    )
                
                    fig.update_layout(
                        margin={"r": 0, "t": 50, "l": 0, "b": 0}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No coordinate data available for mapping.")
            else:
                st.info("No location data available. Run the ETL pipeline to process geographic data.")
    
        with col2:
            st.subheader("Species Observations")
            
            if not silver_data.empty:
                species_counts = silver_data['common_name'].value_counts().head(10)
                
                fig = px.bar(
                    x=species_counts.values,
                    y=species_counts.index,
                    orientation='h',
                    title="Top 10 Most Observed Species",
                    labels={'x': 'Observations', 'y': 'Species'}
                )
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

def render_etl_monitoring():
    """Render ETL monitoring dashboard"""
    
    # Import required modules at function level
    import subprocess
    import sys
    import os
    
    st.header("ETL Pipeline Monitoring")
    
    dashboard = WildlifeDashboard()
    
    # Check ETL execution status
    etl_executed, etl_message = dashboard.check_etl_execution_status()
    has_data = dashboard.has_sufficient_data()
    
    if not etl_executed or not has_data:
        st.error("🚨 **ETL Pipeline Required for Monitoring Dashboard**")
        st.info(f"**Status**: {etl_message}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **To view ETL monitoring and job history:**
            1. Click **"Run ETL Demo"** in the sidebar
            2. Wait for pipeline execution
            3. Return here to monitor ETL performance and job history
            """)
        
        with col2:
            st.markdown("**Current System:**")
            if has_data:
                st.warning("📊 Historical data exists")
                st.info("🔄 Run ETL to see current session")
            else:
                st.error("❌ No ETL history available")
        
        # Show basic status without detailed history
        st.markdown("---")
        st.subheader("📋 System Status")
        st.info("🚀 **ETL monitoring will show detailed job history after running ETL Demo**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ETL Status", "Pending", help="Run ETL Demo to activate")
        with col2:
            st.metric("Active Jobs", "---", help="Run ETL Demo to see jobs")
        with col3:
            st.metric("Success Rate", "---", help="Run ETL Demo to see metrics")
        
        return
    
    st.success(f"✅ **ETL Status**: {etl_message}")
    
    etl_history = dashboard.load_etl_job_history()
    
    if not etl_history.empty:
        # Enhanced ETL Job Status Overview with Multi-Source Context
        st.subheader("🔄 ETL Pipeline Performance Dashboard")
        
        # Multi-source integration status
        multi_source_jobs = etl_history[etl_history['job_name'].str.contains('multi_source', case=False, na=False)]
        if not multi_source_jobs.empty:
            latest_multi_job = multi_source_jobs.iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🌐 Multi-Source Status", 
                         "✅ Active" if latest_multi_job['status'] == 'success' else "❌ Failed")
            
            with col2:
                st.metric("📊 Last Collection", 
                         f"{latest_multi_job['records_loaded']:,} records")
            
            with col3:
                st.metric("🕐 Last Updated", 
                         pd.to_datetime(latest_multi_job['start_time']).strftime('%H:%M'))
            
            with col4:
                sources_info = latest_multi_job.get('quality_issues', '')
                source_count = sources_info.count(',') + 1 if ',' in str(sources_info) else 1
                st.metric("🔌 Active Sources", source_count)
        
        # ETL Job History Table
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Recent ETL Job Executions")
            
            # Enhanced job display with multi-source highlighting
            etl_history['job_type'] = etl_history['job_name'].apply(
                lambda x: '🌐 Multi-Source' if 'multi_source' in str(x).lower() 
                else '🔄 Standard ETL'
            )
            
            etl_history['status_icon'] = etl_history['status'].map({
                'success': '✅ Success',
                'failed': '❌ Failed'
            })
            
            # Display enhanced job history table
            display_cols = ['job_type', 'job_name', 'status_icon', 'records_extracted', 
                          'records_loaded', 'duration_seconds', 'start_time']
            
            display_df = etl_history[display_cols].rename(columns={
                'job_type': 'Type',
                'job_name': 'Job Name',
                'status_icon': 'Status',
                'records_extracted': 'Extracted',
                'records_loaded': 'Loaded',
                'duration_seconds': 'Duration (s)',
                'start_time': 'Execution Time'
            })
            
            st.dataframe(display_df, use_container_width=True)
        
        with col2:
            st.subheader("Job Performance")
            
            # Enhanced success rate with multi-source context
            success_counts = etl_history['status'].value_counts()
            
            if len(success_counts) > 0:
                # Calculate multi-source vs standard job success rates
                multi_jobs = etl_history[etl_history['job_name'].str.contains('multi_source', case=False, na=False)]
                standard_jobs = etl_history[~etl_history['job_name'].str.contains('multi_source', case=False, na=False)]
                
                # Multi-source success rate
                multi_success_rate = (multi_jobs['status'] == 'success').mean() * 100 if not multi_jobs.empty else 0
                standard_success_rate = (standard_jobs['status'] == 'success').mean() * 100 if not standard_jobs.empty else 0
                
                # Display success rates
                st.metric("🌐 Multi-Source Success Rate", f"{multi_success_rate:.1f}%")
                st.metric("🔄 Standard ETL Success Rate", f"{standard_success_rate:.1f}%")
                
                # Overall status pie chart
                fig = px.pie(
                    values=success_counts.values,
                    names=success_counts.index,
                    title="Overall ETL Job Status",
                    color_discrete_map={'success': '#28a745', 'failed': '#dc3545'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced Performance Trends
        st.subheader("📈 Performance Trends & Multi-Source Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Duration trend with job type differentiation
            etl_history['start_time'] = pd.to_datetime(etl_history['start_time'])
            
            fig = px.line(
                etl_history,
                x='start_time',
                y='duration_seconds',
                color='job_type',
                title="ETL Job Duration: Multi-Source vs Standard",
                labels={'start_time': 'Execution Time', 'duration_seconds': 'Duration (seconds)'},
                color_discrete_map={'🌐 Multi-Source': '#17a2b8', '🔄 Standard ETL': '#6c757d'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Records processed with job type highlighting
            recent_jobs = etl_history.head(10).copy()
            
            fig = px.bar(
                recent_jobs,
                x='job_name',
                y='records_loaded',
                color='job_type',
                title="Records Processed by Job Type",
                color_discrete_map={'🌐 Multi-Source': '#17a2b8', '🔄 Standard ETL': '#6c757d'}
            )
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Multi-Source Performance Deep Dive
        if not multi_source_jobs.empty:
            st.subheader("🌐 Multi-Source Collection Performance")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_records = multi_source_jobs['records_loaded'].mean()
                st.metric("📊 Avg Records per Collection", f"{avg_records:,.0f}")
            
            with col2:
                avg_duration = multi_source_jobs['duration_seconds'].mean()
                st.metric("⏱️ Avg Collection Time", f"{avg_duration:.1f}s")
            
            with col3:
                records_per_second = avg_records / avg_duration if avg_duration > 0 else 0
                st.metric("🚀 Processing Rate", f"{records_per_second:.0f} rec/s")
    
    else:
        st.info("No ETL job history found. Run the ETL pipeline to see monitoring data.")
        
        if st.button("Run ETL Pipeline Demo"):
            with st.spinner("Running ETL pipeline..."):
                # Integration point for ETL pipeline
                
                try:
                    # Get the correct paths
                    current_dir = os.getcwd()
                    script_path = os.path.join(current_dir, "scripts", "enhanced_etl_demo.py")
                    
                    # Check if script exists
                    if not os.path.exists(script_path):
                        st.error(f"ETL script not found at: {script_path}")
                        return
                    
                    # Run the ETL pipeline with proper encoding
                    result = subprocess.run(
                        [sys.executable, script_path], 
                        capture_output=True, 
                        text=True,
                        cwd=current_dir,
                        timeout=180,  # 3 minute timeout
                        encoding='utf-8',
                        errors='replace',
                        env=dict(os.environ, PYTHONIOENCODING='utf-8')
                    )
                    
                    if result.returncode == 0:
                        st.success("ETL pipeline execution completed successfully!")
                        
                        # Show key results from output
                        output_lines = result.stdout.split('\n')
                        success_lines = [line for line in output_lines if '✓' in line or 'SUCCESS' in line.upper()]
                        
                        if success_lines:
                            st.subheader("ETL Results:")
                            for line in success_lines[-10:]:  # Show last 10 success messages
                                if line.strip():
                                    st.text(line.strip())
                        
                        # Show full output in expandable section
                        with st.expander("View Full ETL Output"):
                            st.text(result.stdout[-2000:])  # Last 2000 chars
                        
                        # Refresh the dashboard data
                        st.cache_data.clear()
                        st.info("Dashboard data refreshed. Navigate to other pages to see updated results!")
                        
                    else:
                        st.error("ETL pipeline failed!")
                        st.subheader("Error Details:")
                        st.text(result.stderr)
                        
                        # Also show stdout in case there are useful messages
                        if result.stdout:
                            with st.expander("ETL Output (for debugging)"):
                                st.text(result.stdout[-1500:])
                
                except subprocess.TimeoutExpired:
                    st.error("⏰ ETL pipeline timed out after 3 minutes. This may indicate an issue with API connectivity.")
                    st.info("Try running the pipeline manually: `python scripts/enhanced_etl_demo.py`")
                
                except Exception as e:
                    st.error(f"Error running ETL pipeline: {str(e)}")
                    
                    # Provide helpful debugging info
                    st.subheader("Debugging Information:")
                    st.text(f"Current directory: {os.getcwd()}")
                    st.text(f"Python executable: {sys.executable}")
                    st.text(f"Script path: {script_path if 'script_path' in locals() else 'Not determined'}")
                    
                    # Suggest manual execution
                    st.info("**Manual Execution:** Try running in terminal:")
                    st.code("cd " + os.getcwd().replace('\\', '/') + "\npython scripts/enhanced_etl_demo.py")

def render_data_quality_dashboard():
    """Render data quality dashboard"""
    
    st.header("Data Quality Dashboard")
    
    dashboard = WildlifeDashboard()
    
    # Check ETL execution status first
    etl_executed, etl_message = dashboard.check_etl_execution_status()
    has_data = dashboard.has_sufficient_data()
    
    # Show ETL dependency warning if needed
    if not etl_executed or not has_data:
        st.warning("⚠️ **ETL Pipeline Required**")
        st.info(f"**Status**: {etl_message}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            **To view complete data quality analysis, please:**
            1. Navigate to the sidebar
            2. Click **"Run ETL Demo"** button  
            3. Wait for completion (may take 1-2 minutes)
            4. Return to this page for full analysis
            """)
        
        with col2:
            st.markdown("**Current Data Status:**")
            if has_data:
                st.success("✅ Some data available")
            else:
                st.error("❌ No data for analysis")
                
        # Show minimal preview if data exists
        if has_data:
            st.subheader("📊 Limited Data Preview")
            silver_data = dashboard.load_silver_layer_data() 
            multisource_data = dashboard.load_multisource_data()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Silver Layer Records", len(silver_data))
            with col2:
                st.metric("Multi-Source Records", len(multisource_data))
            
            st.info("💡 **Run ETL Demo** for complete analysis with quality charts, source comparisons, and detailed metrics!")
        else:
            st.error("🚫 **No data available** - Please run ETL Demo first to collect and process wildlife data.")
            
        return  # Exit early if ETL not properly executed
    
    # ETL executed successfully - show full dashboard
    st.success(f"✅ **ETL Status**: {etl_message}")
    
    silver_data = dashboard.load_silver_layer_data()
    
    # Display data source metrics first  
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥈 Silver Layer Data Quality")
        if not silver_data.empty and 'data_source' in silver_data.columns:
            silver_source_counts = silver_data['data_source'].value_counts()
            
            st.write(f"**Total Records:** {len(silver_data)}")
            for source, count in silver_source_counts.items():
                st.write(f"• {source}: {count} records")
            
            # Silver layer source pie chart
            fig = px.pie(
                values=silver_source_counts.values,
                names=silver_source_counts.index,
                title="Silver Layer Data Sources"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No silver layer data available")
    
    with col2:
        st.subheader("🌐 Multi-Source Raw Data")
        
        # Load actual multi-source data
        multisource_data = dashboard.load_multisource_data()
        
        if not multisource_data.empty:
            source_counts = multisource_data['data_source'].value_counts()
            
            st.write(f"**Total Records:** {len(multisource_data)}")
            
            # Map source names for better display
            source_display_names = {
                'inaturalist': 'iNaturalist',
                'gbif': 'GBIF',
                'ebird': 'eBird',
                'ala': 'Atlas of Living Australia'
            }
            
            for source, count in source_counts.items():
                display_name = source_display_names.get(source, source)
                st.write(f"• {display_name}: {count} records")
            
            # Multi-source pie chart with proper names
            display_counts = source_counts.copy()
            display_counts.index = [source_display_names.get(idx, idx) for idx in display_counts.index]
            
            fig = px.pie(
                values=display_counts.values,
                names=display_counts.index,
                title="Multi-Source Data Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No multi-source data found. Run ETL pipeline to collect data.")
    
    # Data quality analysis for silver layer
    if not silver_data.empty:
        st.subheader("Data Completeness Analysis")
        
        completeness_data = []
        for column in ['common_name', 'scientific_name', 'location_description', 
                      'latitude', 'longitude', 'observed_date', 'observer_name']:
            if column in silver_data.columns:
                completeness = (silver_data[column].notna().sum() / len(silver_data)) * 100
                completeness_data.append({'Field': column, 'Completeness (%)': completeness})
        
        if completeness_data:
            completeness_df = pd.DataFrame(completeness_data)
            
            fig = px.bar(
                completeness_df,
                x='Field',
                y='Completeness (%)',
                title="Silver Layer Field Completeness",
                color='Completeness (%)',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Data quality indicators based on completeness
        st.subheader("Data Quality Indicators")
        
        # Calculate quality indicators
        coord_completeness = 0
        if 'latitude' in silver_data.columns and 'longitude' in silver_data.columns:
            coord_completeness = ((silver_data['latitude'].notna() & 
                                 silver_data['longitude'].notna()).sum() / len(silver_data)) * 100
        
        species_completeness = 0
        if 'scientific_name' in silver_data.columns:
            species_completeness = (silver_data['scientific_name'].notna().sum() / len(silver_data)) * 100
        
        overall_quality = (coord_completeness + species_completeness) / 2
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Coordinate Quality", f"{coord_completeness:.1f}%")
        with col2:
            st.metric("Species Name Quality", f"{species_completeness:.1f}%")
        with col3:
            st.metric("Overall Quality", f"{overall_quality:.1f}%")
        
        # Quality assessment
        if overall_quality >= 80:
            st.success("🌟 Excellent data quality!")
        elif overall_quality >= 60:
            st.warning("⚠️ Good data quality with room for improvement")
        else:
            st.error("❌ Data quality needs attention")
    
    # Comprehensive Multi-Source Quality Analysis
    multisource_data = dashboard.load_multisource_data()
    if not multisource_data.empty:
        st.subheader("🌍 Multi-Source Quality Analysis")
        st.write(f"**Analyzing {len(multisource_data)} records from 4 biodiversity APIs**")
        
        # Source-by-source quality analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Data Quality by Source:**")
            
            source_display_names = {
                'inaturalist': 'iNaturalist',
                'gbif': 'GBIF', 
                'ebird': 'eBird',
                'ala': 'Atlas of Living Australia'
            }
            
            quality_data = []
            
            for source in multisource_data['data_source'].unique():
                source_data = multisource_data[multisource_data['data_source'] == source]
                display_name = source_display_names.get(source, source)
                
                # Calculate quality metrics
                coord_complete = (source_data['latitude'].notna() & source_data['longitude'].notna()).sum()
                coord_pct = (coord_complete / len(source_data)) * 100
                
                sci_complete = source_data['scientific_name'].notna().sum()
                sci_pct = (sci_complete / len(source_data)) * 100
                
                loc_complete = source_data['location_description'].notna().sum()
                loc_pct = (loc_complete / len(source_data)) * 100
                
                obs_complete = source_data['observer_name'].notna().sum()
                obs_pct = (obs_complete / len(source_data)) * 100
                
                overall_source_quality = (coord_pct + sci_pct + loc_pct + obs_pct) / 4
                
                quality_data.append({
                    'Source': display_name,
                    'Records': len(source_data),
                    'Coordinates': coord_pct,
                    'Scientific Names': sci_pct,
                    'Locations': loc_pct,
                    'Observers': obs_pct,
                    'Overall Quality': overall_source_quality
                })
                
                # Display detailed metrics
                st.markdown(f"**{display_name}** ({len(source_data)} records)")
                st.progress(overall_source_quality / 100)
                st.markdown(f"  - Coordinates: {coord_pct:.1f}%")
                st.markdown(f"  - Scientific names: {sci_pct:.1f}%")
                st.markdown(f"  - Locations: {loc_pct:.1f}%")
                st.markdown(f"  - Observers: {obs_pct:.1f}%")
                st.markdown("---")
        
        with col2:
            # Quality comparison chart
            if quality_data:
                quality_df = pd.DataFrame(quality_data)
                
                fig = px.bar(
                    quality_df,
                    x='Source',
                    y='Overall Quality',
                    title="Data Quality by Source",
                    color='Overall Quality',
                    color_continuous_scale='RdYlGn',
                    text='Records'
                )
                fig.update_traces(texttemplate='%{text}<br>records', textposition='outside')
                fig.update_layout(xaxis_tickangle=45)
                fig.update_yaxes(range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)
        
        # Multi-source species diversity
        st.subheader("🦘 Species Diversity Across Sources")
        
        species_by_source = multisource_data.groupby('data_source')['common_name'].nunique().reset_index()
        species_by_source.columns = ['data_source', 'unique_species']
        
        # Map source names
        species_by_source['display_source'] = species_by_source['data_source'].map(source_display_names)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                species_by_source,
                x='display_source',
                y='unique_species',
                title="Unique Species per Source",
                color='unique_species',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Show top species across all sources
            top_species = multisource_data['common_name'].value_counts().head(10)
            st.markdown("**Most Observed Species:**")
            for species, count in top_species.items():
                sources = multisource_data[multisource_data['common_name'] == species]['data_source'].nunique()
                st.markdown(f"• **{species}**: {count} observations ({sources} sources)")
    
    else:
        st.info("No quality data available. Run the ETL pipeline to generate quality metrics.")

def render_species_explorer():
    """Render species exploration interface"""
    
    st.header("Species Explorer")
    
    dashboard = WildlifeDashboard()
    
    # Check ETL execution status
    etl_executed, etl_message = dashboard.check_etl_execution_status()
    has_data = dashboard.has_sufficient_data()
    
    if not etl_executed or not has_data:
        st.error("🚨 **ETL Pipeline Required for Species Explorer**")
        st.info(f"**Status**: {etl_message}")
        
        st.markdown("""
        **To explore species data:**
        1. Click **"Run ETL Demo"** in the sidebar
        2. Wait for data collection and processing
        3. Return here to explore species observations
        """)
        
        if not has_data:
            st.warning("🔒 **No species data available** - Run ETL Demo to collect wildlife observations")
        return
    
    st.success(f"✅ **ETL Status**: {etl_message}")
    
    silver_data = dashboard.load_silver_layer_data()
    
    if not silver_data.empty:
        # Species selection
        species_list = sorted(silver_data['common_name'].dropna().unique())
        selected_species = st.selectbox("Select a species to explore:", species_list)
        
        if selected_species:
            species_data = silver_data[silver_data['common_name'] == selected_species]
            
            # Species overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Observations", len(species_data))
            
            with col2:
                unique_locations = species_data['location_description'].nunique()
                st.metric("Unique Locations", unique_locations)
            
            with col3:
                avg_quality = species_data['quality_score'].mean()
                st.metric("Avg Quality Score", f"{avg_quality:.3f}")
            
            with col4:
                date_range = species_data['observed_date'].nunique()
                st.metric("Observation Days", date_range)
            
            # Detailed analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"{selected_species} Locations")
                
                location_counts = species_data['location_description'].value_counts().head(10)
                
                fig = px.bar(
                    x=location_counts.values,
                    y=location_counts.index,
                    orientation='h',
                    title=f"Top Locations for {selected_species}",
                    labels={'x': 'Observations', 'y': 'Location'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader(f"{selected_species} Timeline")
                
                if 'observed_date' in species_data.columns:
                    species_data = species_data.copy()
                    try:
                        # Convert to datetime with proper error handling
                        species_data['observed_date_dt'] = pd.to_datetime(species_data['observed_date'], errors='coerce')
                        
                        # Check if we have valid datetime data after conversion
                        if not species_data['observed_date_dt'].isna().all():
                            # Group by date using the converted datetime column
                            daily_counts = species_data.groupby(species_data['observed_date_dt'].dt.date).size()
                        else:
                            # Fallback: try to parse as string dates directly
                            date_counts = species_data['observed_date'].value_counts()
                            daily_counts = date_counts
                    except Exception as e:
                        # Final fallback if all datetime operations fail
                        daily_counts = pd.Series([len(species_data)], index=['All Observations'])
                    
                    fig = px.line(
                        x=daily_counts.index,
                        y=daily_counts.values,
                        title=f"{selected_species} Observations Over Time",
                        labels={'x': 'Date', 'y': 'Observations'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Recent observations table
            st.subheader(f"Recent {selected_species} Observations")
            recent_observations = species_data.head(10)[
                ['location_description', 'observed_date', 'observer_name', 'quality_score']
            ].rename(columns={
                'location_description': 'Location',
                'observed_date': 'Date',
                'observer_name': 'Observer',
                'quality_score': 'Quality'
            })
            
            st.dataframe(recent_observations, use_container_width=True)
    
    else:
        st.info("No species data available. Run the ETL pipeline to load species observations.")

def render_multi_source_analytics():
    """Render multi-source data analytics dashboard with data lake architecture"""
    
    # Import required modules at function level to ensure availability
    import subprocess
    import sys
    import os
    
    st.header("Multi-Source Data Lake Analytics")
    st.markdown("**Enterprise Data Lake: Cross-platform biodiversity data integration & validation**")
    
    # Data Lake Architecture Overview
    with st.expander("Data Lake Architecture Overview", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **Bronze Layer (Raw Ingestion)**
            - Direct API feeds from multiple sources
            - iNaturalist, GBIF, eBird, ALA
            - Real-time data collection
            - No transformation applied
            """)
        
        with col2:
            st.markdown("""
            **Silver Layer (Standardized)**
            - Cross-source data harmonization
            - Species name standardization
            - Geographic coordinate validation
            - Quality scoring & deduplication
            """)
        
        with col3:
            st.markdown("""
            **Gold Layer (Analytics-Ready)**
            - Multi-source species validation
            - Conservation status aggregation
            - Temporal trend analysis
            - Research-grade datasets
            """)
    
    dashboard = WildlifeDashboard()
    
    # Check ETL execution status
    etl_executed, etl_message = dashboard.check_etl_execution_status()
    has_data = dashboard.has_sufficient_data()
    
    if not etl_executed or not has_data:
        st.error("🚨 **ETL Pipeline Required for Multi-Source Analytics**")
        st.info(f"**Status**: {etl_message}")
        
        st.markdown("""
        **To view multi-source analytics:**
        1. Click **"Run ETL Demo"** in the sidebar
        2. Wait for multi-source data collection
        3. Return here for cross-platform analytics
        """)
        
        if not has_data:
            st.warning("🔒 **No multi-source data available** - Run ETL Demo to collect and integrate data from multiple sources")
        return
    
    st.success(f"✅ **ETL Status**: {etl_message}")
    
    # Check for multi-source data
    conn = dashboard.get_connection()
    if conn is None:
        return
    
    try:
        # Check if multi-source table exists, create if needed
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wildlife_multisource (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                scientific_name TEXT,
                common_name TEXT,
                latitude REAL,
                longitude REAL,
                observed_date TEXT,
                location_description TEXT,
                observer_name TEXT,
                quality_score REAL,
                raw_data TEXT,
                collected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()
        
        # Load multi-source data
        multisource_data = pd.read_sql_query("""
            SELECT * FROM wildlife_multisource 
            ORDER BY collected_at DESC
            LIMIT 1000
        """, conn)
        
        if multisource_data.empty:
            # Enhanced multi-source data collection interface
            st.warning("**Data Lake Status**: Multi-source Bronze layer is empty - Ready for first ingestion")
            
            # Check if multi-source collector exists
            collector_path = os.path.join(os.getcwd(), "src", "multi_source_collector.py")
            collector_exists = os.path.exists(collector_path)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if collector_exists:
                    st.info("""
                    **Multi-Source Data Collection Pipeline**
                    
                    The data lake infrastructure is ready to ingest data from multiple biodiversity platforms:
                    - **iNaturalist**: Citizen science observations (Global)
                    - **GBIF**: Global biodiversity database (🏛️ Research-grade)
                    - **eBird**: Bird observation network (Specialized)
                    - **Atlas of Living Australia**: Australian species data (Local focus)
                    
                    **Data Lake Layers:**
                    - **Bronze**: Raw API responses stored as-is
                    - **Silver**: Standardized and validated records  
                    - **Gold**: Analytics-ready aggregations
                    
                    Click below to start the enterprise data ingestion pipeline.
                    """)
                else:
                    st.error("""
                    **❌ Multi-Source Collector Not Found**
                    
                    The multi-source collector script is missing. Expected location:
                    `src/multi_source_collector.py`
                    
                    Please ensure the collector module is properly installed or run the ETL demo first.
                    """)
            
            with col2:
                st.metric("📡 Data Sources", "4", help="Available biodiversity APIs")
                st.metric("🎯 Expected Records", "1000+", help="Estimated collection volume per run")
                st.metric("Collector Status", "Ready" if collector_exists else "Missing", 
                         help="Multi-source collector availability")
            
            # Enhanced collection interface
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if collector_exists and st.button("🚀 **Start Data Lake Ingestion**", help="Run full multi-source collection"):
                    with st.spinner("Running enterprise data lake ingestion pipeline..."):
                        
                        try:
                            script_path = os.path.join(current_dir, "src", "multi_source_collector.py")
                            
                            # Show progress placeholder
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            status_text.text("Initializing data lake Bronze layer...")
                            progress_bar.progress(20)
                            
                            result = subprocess.run(
                                [sys.executable, script_path], 
                                capture_output=True, 
                                text=True,
                                timeout=300,  # 5 minute timeout
                                encoding='utf-8',
                                errors='replace',
                                env=dict(os.environ, 
                                        PYTHONIOENCODING='utf-8',
                                        PYTHONLEGACYWINDOWSFSENCODING='0',
                                        PYTHONUTF8='1')
                            )
                            
                            progress_bar.progress(60)
                            status_text.text("Processing Silver layer transformations...")
                            time.sleep(1)
                            
                            progress_bar.progress(80)
                            status_text.text("Finalizing Gold layer analytics...")
                            time.sleep(1)
                            
                            if result.returncode == 0:
                                progress_bar.progress(100)
                                status_text.text("✅ Data lake ingestion completed!")
                                st.success("🎉 **Multi-source data collection completed successfully!**")
                                
                                # Show collection summary
                                output_lines = result.stdout.split('\n')
                                success_lines = [line for line in output_lines if 
                                               'collected' in line.lower() or 
                                               'records' in line.lower() or
                                               'saved' in line.lower() or
                                               'species' in line.lower() or
                                               'sources' in line.lower() or
                                               'completed' in line.lower()]
                                
                                if success_lines:
                                    with st.expander("📊 Collection Summary", expanded=True):
                                        for line in success_lines[-10:]:  # Show more lines for better summary
                                            if line.strip() and len(line.strip()) > 5:  # Filter out empty/short lines
                                                st.text(line.strip())
                                
                                # Also show final summary lines
                                final_lines = result.stdout.split('\n')[-15:]  # Last 15 lines
                                summary_section = False
                                summary_lines = []
                                for line in final_lines:
                                    if 'COLLECTION SUMMARY' in line or summary_section:
                                        summary_section = True
                                        summary_lines.append(line.strip())
                                
                                if summary_lines:
                                    with st.expander("📋 Detailed Summary"):
                                        for line in summary_lines:
                                            if line:
                                                st.text(line)
                                
                                # Show data lake status
                                st.info("Refreshing dashboard to show new multi-source data...")
                                st.cache_data.clear()
                                time.sleep(2)  # Brief pause for user to see results
                                st.experimental_rerun()
                            else:
                                st.error("❌ **Data lake ingestion failed!**")
                                st.text("**Error Details:**")
                                st.text(result.stderr[:1000])  # Limit error text
                                
                                # Enhanced troubleshooting suggestions
                                with st.expander("Troubleshooting Guide"):
                                    st.markdown("""
                                    **Common Issues & Solutions:**
                                    
                                    🔸 **API Rate Limiting**: Wait 5-10 minutes and try again
                                    🔸 **Network Issues**: Check internet connectivity
                                    🔸 **Missing Dependencies**: Ensure all packages in requirements.txt are installed
                                    🔸 **API Keys**: Some APIs may require authentication (optional)
                                    
                                    **Alternative Approaches:**
                                    
                                    1. **Manual Collection**: Run in terminal for detailed output
                                    ```bash
                                    cd src
                                    python multi_source_collector.py
                                    ```
                                    
                                    2. **Use ETL Demo**: Run the main ETL pipeline first
                                    ```bash
                                    python scripts/enhanced_etl_demo.py
                                    ```
                                    
                                    3. **Check Dependencies**: Verify all packages are installed
                                    ```bash
                                    pip install -r requirements.txt
                                    ```
                                    """)
                        except subprocess.TimeoutExpired:
                            st.error("⏰ **Data lake ingestion timed out** (5 minutes)")
                            st.warning("This might indicate API rate limiting or network issues.")
                            st.info("💡 Try running manually: `python src/multi_source_collector.py`")
                        except Exception as e:
                            st.error(f"❌ **System Error**: {e}")
                            st.info("💡 Try running the collector manually from terminal for more details")
                
                elif not collector_exists:
                    if st.button("**Create Multi-Source Collector**", help="Generate the missing collector module"):
                        st.info("""
                        **Missing Collector Module**
                        
                        The multi-source collector appears to be missing. You can:
                        
                        1. Run the main ETL demo first (this may create missing components)
                        2. Check that all project files are properly installed
                        3. Verify the `src/` directory structure
                        """)
                        
                        # Check if we can find it elsewhere
                        possible_paths = [
                            "multi_source_collector.py",
                            "src/collectors.py", 
                            "scripts/multi_source_demo.py"
                        ]
                        
                        st.text("Searching for alternative collector modules...")
                        for path in possible_paths:
                            if os.path.exists(path):
                                st.success(f"Found alternative collector: {path}")
                            else:
                                st.text(f"❌ Not found: {path}")
            
            with col2:
                if st.button("📋 **View Collection Status**", help="Check data lake ingestion history"):
                    # Check for any existing collection attempts
                    try:
                        # First check if table has any data
                        cursor.execute("SELECT COUNT(*) FROM wildlife_multisource")
                        total_records = cursor.fetchone()[0]
                        
                        if total_records > 0:
                            status_data = pd.read_sql_query("""
                                SELECT source, COUNT(*) as records, MAX(collected_at) as last_update
                                FROM wildlife_multisource 
                                GROUP BY source
                            """, conn)
                            
                            st.subheader("📈 Previous Collections")
                            st.dataframe(status_data, use_container_width=True)
                            
                            # Additional stats
                            st.metric("Total Records", f"{total_records:,}")
                        else:
                            st.info("✨ **Data Lake is Ready**")
                            st.markdown("""
                            **Status**: Multi-source table initialized but empty
                            
                            **Next Steps**:
                            - Click "Start Data Lake Ingestion" to begin collection
                            - Data will be collected from 4 biodiversity APIs
                            - Estimated time: 2-5 minutes for first run
                            """)
                    except Exception as e:
                        st.warning(f"Unable to check collection status: {e}")
                        st.info("💡 Try initializing the data lake first")
            
            with col3:
                if st.button("**Initialize Data Lake**", help="Set up multi-source tables"):
                    with st.spinner("Setting up data lake infrastructure..."):
                        try:
                            # Create multi-source table if it doesn't exist
                            cursor = conn.cursor()
                            cursor.execute("""
                                CREATE TABLE IF NOT EXISTS wildlife_multisource (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    source TEXT NOT NULL,
                                    scientific_name TEXT,
                                    common_name TEXT,
                                    latitude REAL,
                                    longitude REAL,
                                    observed_date TEXT,
                                    location_description TEXT,
                                    observer_name TEXT,
                                    quality_score REAL,
                                    raw_data TEXT,
                                    collected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                                    processed BOOLEAN DEFAULT 0
                                )
                            """)
                            conn.commit()
                            st.success("✅ Data lake infrastructure initialized!")
                        except Exception as e:
                            st.error(f"Error initializing data lake: {e}")
            
            conn.close()
            return
        
        # Enhanced Data Lake Metrics Dashboard
        st.subheader("🏗️ Data Lake Overview")
        
        # Primary metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_records = len(multisource_data)
            st.metric("🗃️ Total Records", f"{total_records:,}", help="All ingested records in Bronze layer")
        
        with col2:
            unique_sources = multisource_data['source'].nunique()
            st.metric("🔌 Active Sources", unique_sources, help="Connected biodiversity APIs")
        
        with col3:
            unique_species = multisource_data['scientific_name'].nunique()
            st.metric("🐾 Species Catalog", unique_species, help="Unique species across all sources")
        
        with col4:
            date_range = multisource_data['observed_date'].nunique()
            st.metric("📅 Temporal Span", f"{date_range} days", help="Date range coverage")
        
        with col5:
            # Calculate data freshness
            latest_collection = pd.to_datetime(multisource_data['collected_at']).max()
            hours_since = (datetime.now() - latest_collection).total_seconds() / 3600
            st.metric("⏰ Data Freshness", f"{hours_since:.1f}h ago", help="Time since last ingestion")
        
        # Data lake health indicators
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Data completeness score
            completeness_score = (
                multisource_data['scientific_name'].notna().mean() * 0.3 +
                multisource_data[['latitude', 'longitude']].notna().all(axis=1).mean() * 0.3 +
                multisource_data['observed_date'].notna().mean() * 0.2 +
                multisource_data['common_name'].notna().mean() * 0.2
            ) * 100
            
            st.metric(
                "🎯 Data Completeness", 
                f"{completeness_score:.1f}%",
                help="Overall data quality across all fields"
            )
        
        with col2:
            # Cross-validation score (species found in multiple sources)
            species_source_matrix = multisource_data.groupby(['scientific_name', 'source']).size().unstack(fill_value=0)
            validated_species = ((species_source_matrix > 0).sum(axis=1) > 1).sum()
            validation_rate = (validated_species / len(species_source_matrix)) * 100
            
            st.metric(
                "✅ Cross-Validation", 
                f"{validation_rate:.1f}%",
                help="Species confirmed by multiple sources"
            )
        
        with col3:
            # Geographic coverage (Australian focus)
            aus_coords = multisource_data[
                (multisource_data['latitude'].between(-44, -10)) & 
                (multisource_data['longitude'].between(113, 154))
            ]
            aus_coverage = (len(aus_coords) / len(multisource_data)) * 100
            
            st.metric(
                "🇦🇺 Australian Coverage", 
                f"{aus_coverage:.1f}%",
                help="Records within Australian boundaries"
            )
        
        st.markdown("---")
        
        # Enhanced Data Lake Visualizations
        st.subheader("📈 Data Lake Analytics")
        
        # Source distribution and volume analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Source Distribution & Volume**")
            source_counts = multisource_data['source'].value_counts()
            
            # Enhanced pie chart with data lake context
            fig = px.pie(
                values=source_counts.values,
                names=source_counts.index,
                title="Bronze Layer: Data Distribution by Source API",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hover_data=[source_counts.values]
            )
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Records: %{value:,}<br>Percentage: %{percent}<extra></extra>'
            )
            fig.update_layout(
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**🌟 Silver Layer: Data Quality Assessment**")
            # Enhanced quality metrics calculation
            quality_by_source = []
            
            for source in multisource_data['source'].unique():
                source_data = multisource_data[multisource_data['source'] == source]
                
                # Comprehensive quality scoring
                quality_metrics = {
                    'coordinates': (source_data[['latitude', 'longitude']].notna().all(axis=1)).mean(),
                    'species_info': source_data['scientific_name'].notna().mean(),
                    'date_info': source_data['observed_date'].notna().mean(),
                    'location_info': source_data['location_description'].notna().mean(),
                    'observer_info': source_data['observer_name'].notna().mean() if 'observer_name' in source_data else 0
                }
                
                # Weighted quality score (coordinates and species most important)
                weighted_score = (
                    quality_metrics['coordinates'] * 0.35 +
                    quality_metrics['species_info'] * 0.35 +
                    quality_metrics['date_info'] * 0.15 +
                    quality_metrics['location_info'] * 0.10 +
                    quality_metrics['observer_info'] * 0.05
                )
                
                quality_by_source.append({
                    'Source': source,
                    'Quality Score': weighted_score,
                    'Records': len(source_data),
                    'Completeness': weighted_score * 100,
                    'Source Type': 'Citizen Science' if source in ['iNaturalist', 'eBird'] else 'Research Database'
                })
            
            quality_df = pd.DataFrame(quality_by_source)
            
            # Enhanced bubble chart with source type coloring
            fig = px.scatter(
                quality_df,
                x='Records',
                y='Quality Score',
                size='Records',
                color='Source Type',
                hover_name='Source',
                title="Silver Layer: Quality vs Volume Analysis",
                hover_data={
                    'Records': ':,',
                    'Quality Score': ':.3f',
                    'Completeness': ':.1f%'
                },
                color_discrete_map={
                    'Citizen Science': '#FF6B6B',
                    'Research Database': '#4ECDC4'
                }
            )
            fig.update_layout(
                yaxis_range=[0, 1],
                xaxis_title="Record Volume (Bronze Layer)",
                yaxis_title="Quality Score (Silver Layer Processing)"
            )
            fig.add_hline(y=0.7, line_dash="dash", line_color="green", 
                         annotation_text="Quality Threshold (70%)")
            st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced Geographic Data Lake Analysis
        st.subheader("🗺️ Gold Layer: Geospatial Data Lake Analytics")
        
        # Filter data with valid coordinates
        geo_data = multisource_data.dropna(subset=['latitude', 'longitude'])
        
        if not geo_data.empty:
            # Add Australian region classification for better analysis
            def classify_region(lat, lon):
                if -28 <= lat <= -17 and 113 <= lon <= 123:
                    return "Western Australia"
                elif -38 <= lat <= -28 and 140 <= lon <= 150:
                    return "Victoria/NSW"
                elif -28 <= lat <= -17 and 138 <= lon <= 150:
                    return "Queensland"
                elif -35 <= lat <= -26 and 129 <= lon <= 141:
                    return "South Australia"
                elif -44 <= lat <= -35 and 143 <= lon <= 148:
                    return "Tasmania"
                elif -26 <= lat <= -12 and 129 <= lon <= 138:
                    return "Northern Territory"
                else:
                    return "Other/International"
            
            geo_data = geo_data.copy()
            geo_data['region'] = geo_data.apply(
                lambda row: classify_region(row['latitude'], row['longitude']), 
                axis=1
            )
            
            # Enhanced map with region context and data lake metadata
            fig = px.scatter_map(
                geo_data,
                lat="latitude",
                lon="longitude",
                color="source",
                size_max=15,
                hover_name="common_name",
                hover_data={
                    "scientific_name": True, 
                    "observed_date": True, 
                    "source": True,
                    "region": True,
                    "latitude": ":.4f",
                    "longitude": ":.4f"
                },
                title="Data Lake Geospatial Distribution: Multi-Source Species Observations",
                zoom=4,
                height=700,
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            
            # Focus on Australia
            fig.update_layout(
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                map_center={"lat": -25, "lon": 135},  # Center on Australia
                map_zoom=4
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Regional data summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🏞️ Regional Distribution Summary**")
                region_summary = geo_data.groupby('region').agg({
                    'scientific_name': 'nunique',
                    'source': lambda x: ', '.join(x.unique()),
                    'latitude': 'count'
                }).rename(columns={
                    'scientific_name': 'Species Count',
                    'source': 'Data Sources',
                    'latitude': 'Total Records'
                })
                st.dataframe(region_summary, use_container_width=True)
            
            with col2:
                st.markdown("**📊 Source Coverage by Region**")
                region_source = pd.crosstab(geo_data['region'], geo_data['source'])
                fig_heatmap = px.imshow(
                    region_source.values,
                    labels=dict(x="Data Source", y="Region", color="Records"),
                    x=region_source.columns,
                    y=region_source.index,
                    aspect="auto",
                    title="Cross-Source Regional Coverage Heatmap"
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Temporal analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Temporal Coverage by Source")
            
            # Convert dates and create temporal analysis
            temporal_data = multisource_data.copy()
            temporal_data['observed_date'] = pd.to_datetime(temporal_data['observed_date'], errors='coerce')
            temporal_data = temporal_data.dropna(subset=['observed_date'])
            
            if not temporal_data.empty:
                temporal_data['year_month'] = temporal_data['observed_date'].dt.to_period('M').astype(str)
                monthly_counts = temporal_data.groupby(['year_month', 'source']).size().reset_index(name='count')
                
                fig = px.line(
                    monthly_counts,
                    x='year_month',
                    y='count',
                    color='source',
                    title="Observations Over Time by Source",
                    markers=True
                )
                fig.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Data Freshness Analysis")
            
            # Calculate data freshness
            if 'collected_at' in multisource_data.columns:
                freshness_data = multisource_data.copy()
                freshness_data['collected_at'] = pd.to_datetime(freshness_data['collected_at'])
                freshness_data['hours_old'] = (datetime.now() - freshness_data['collected_at']).dt.total_seconds() / 3600
                
                freshness_by_source = freshness_data.groupby('source')['hours_old'].agg(['mean', 'min', 'max']).reset_index()
                freshness_by_source.columns = ['Source', 'Avg Hours', 'Min Hours', 'Max Hours']
                
                fig = px.bar(
                    freshness_by_source,
                    x='Source',
                    y='Avg Hours',
                    title="Average Data Age by Source (Hours)",
                    color='Avg Hours',
                    color_continuous_scale='Viridis_r'
                )
                fig.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        
        # Cross-source species validation
        st.subheader("🔍 Cross-Source Species Validation")
        
        # Find species reported by multiple sources
        species_source_matrix = multisource_data.groupby(['scientific_name', 'source']).size().unstack(fill_value=0)
        species_source_matrix['total_sources'] = (species_source_matrix > 0).sum(axis=1)
        
        multi_source_species = species_source_matrix[species_source_matrix['total_sources'] > 1].sort_values('total_sources', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if not multi_source_species.empty:
                st.write("**Species Confirmed by Multiple Sources:**")
                display_species = multi_source_species.head(10)[['total_sources']].rename(columns={'total_sources': 'Sources'})
                st.dataframe(display_species, use_container_width=True)
            else:
                st.info("No species found in multiple sources yet.")
        
        with col2:
            if not multi_source_species.empty:
                validation_summary = {
                    'Single Source': len(species_source_matrix[species_source_matrix['total_sources'] == 1]),
                    'Multiple Sources': len(multi_source_species),
                    'All Sources': len(species_source_matrix[species_source_matrix['total_sources'] == unique_sources])
                }
                
                fig = px.bar(
                    x=list(validation_summary.keys()),
                    y=list(validation_summary.values()),
                    title="Species Validation Status",
                    color=list(validation_summary.values()),
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced Data Lake Export & Management
        st.subheader("📁 Data Lake Export & Management")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**📊 Bronze Layer Export**")
            if st.button("� Raw Data Export", help="Export Bronze layer (raw ingested data)"):
                summary_data = multisource_data.groupby('source').agg({
                    'scientific_name': 'nunique',
                    'latitude': 'count',
                    'observed_date': ['min', 'max'],
                    'collected_at': 'max'
                }).round(3)
                
                # Add metadata
                summary_data.columns = ['Unique_Species', 'Total_Records', 'Date_Min', 'Date_Max', 'Last_Collection']
                summary_data['Export_Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                csv = summary_data.to_csv()
                st.download_button(
                    label="📄 Download Bronze Summary",
                    data=csv,
                    file_name=f"datalake_bronze_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            st.markdown("**🗺️ Silver Layer Export**")
            if st.button("🎯 Geospatial Export", help="Export Silver layer (processed geographic data)"):
                if not geo_data.empty:
                    geo_export = geo_data[['source', 'scientific_name', 'common_name', 
                                         'latitude', 'longitude', 'location_description', 
                                         'region', 'observed_date']].copy()
                    geo_export['data_quality'] = 'Silver'
                    geo_export['export_date'] = datetime.now().strftime('%Y-%m-%d')
                    
                    csv = geo_export.to_csv(index=False)
                    st.download_button(
                        label="🌏 Download Geospatial Data",
                        data=csv,
                        file_name=f"datalake_silver_geospatial_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No geospatial data available")
        
        with col3:
            st.markdown("**🥇 Gold Layer Export**")
            if st.button("⭐ Analytics Dataset", help="Export Gold layer (analytics-ready data)"):
                # Create analytics-ready dataset with enhanced metadata
                analytics_data = multisource_data.copy()
                
                # Add data lake enrichments
                analytics_data['data_layer'] = 'Gold'
                analytics_data['quality_tier'] = analytics_data.apply(
                    lambda row: 'High' if pd.notna(row['latitude']) and pd.notna(row['scientific_name']) 
                    else 'Medium' if pd.notna(row['scientific_name']) 
                    else 'Low', axis=1
                )
                analytics_data['export_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                csv = analytics_data.to_csv(index=False)
                st.download_button(
                    label="📈 Download Analytics Data",
                    data=csv,
                    file_name=f"datalake_gold_analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
        
        with col4:
            st.markdown("**Data Lake Admin**")
            if st.button("Generate Data Catalog", help="Export complete data lake catalog"):
                # Create comprehensive data catalog
                catalog_data = {
                    'Data Lake Summary': {
                        'Bronze Records': len(multisource_data),
                        'Silver Quality Records': len(geo_data),
                        'Gold Analytics Records': len(multisource_data[multisource_data['scientific_name'].notna()]),
                        'Active Sources': multisource_data['source'].nunique(),
                        'Species Catalog': multisource_data['scientific_name'].nunique(),
                        'Last Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    },
                    'Source Breakdown': multisource_data['source'].value_counts().to_dict(),
                    'Quality Metrics': {
                        'Coordinate Completeness': f"{(multisource_data[['latitude', 'longitude']].notna().all(axis=1).mean()*100):.1f}%",
                        'Species Name Completeness': f"{(multisource_data['scientific_name'].notna().mean()*100):.1f}%",
                        'Date Completeness': f"{(multisource_data['observed_date'].notna().mean()*100):.1f}%"
                    }
                }
                
                catalog_json = json.dumps(catalog_data, indent=2)
                st.download_button(
                    label="📋 Download Data Catalog",
                    data=catalog_json,
                    file_name=f"datalake_catalog_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )
        
        # Data lake management actions
        st.markdown("---")
        st.subheader("⚙️ Data Lake Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("**Refresh Data Lake**", help="Re-run multi-source collection"):
                st.info("💡 Use the 'Start Data Lake Ingestion' button above to refresh data")
        
        with col2:
            if st.button("🧹 **Clean Silver Layer**", help="Remove low-quality records"):
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM wildlife_multisource 
                        WHERE scientific_name IS NULL 
                        AND latitude IS NULL 
                        AND longitude IS NULL
                    """)
                    deleted_count = cursor.rowcount
                    conn.commit()
                    st.success(f"✅ Cleaned {deleted_count} low-quality records from Silver layer")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Error cleaning data: {e}")
        
        with col3:
            if st.button("📊 **Update Gold Analytics**", help="Regenerate analytics aggregations"):
                st.info("💡 Gold layer analytics are updated automatically with each collection cycle")
        
        conn.close()
        
    except Exception as e:
        st.error(f"Error loading multi-source data: {e}")
        if conn:
            conn.close()

def render_advanced_analytics():
    """Advanced Machine Learning and Conservation Analytics Page"""
    st.markdown('<div class="main-header"><h1>🧠 Advanced Analytics & Machine Learning</h1></div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    **Advanced biodiversity analytics powered by machine learning for conservation insights and decision-making.**
    """)
    
    # Import advanced analytics at function level
    try:
        from src.advanced_analytics import AdvancedWildlifeAnalytics
        analytics_available = True
    except ImportError:
        st.error("❌ Advanced analytics module not available. Please install required dependencies:")
        st.code("pip install scikit-learn", language="bash")
        analytics_available = False
        return
    
    if not analytics_available:
        return
    
    # Check ETL execution status
    from streamlit_dashboard import WildlifeDashboard
    dashboard = WildlifeDashboard()
    etl_executed, etl_message = dashboard.check_etl_execution_status()
    has_data = dashboard.has_sufficient_data()
    
    if not etl_executed or not has_data:
        st.error("🚨 **ETL Pipeline Required for Advanced Analytics**")
        st.info(f"**Status**: {etl_message}")
        
        st.markdown("""
        **To use advanced analytics and machine learning:**
        1. Click **"Run ETL Demo"** in the sidebar
        2. Wait for complete data collection and processing
        3. Return here for ML-powered conservation insights
        """)
        
        if not has_data:
            st.warning("🔒 **No data available for ML analysis** - Run ETL Demo to collect biodiversity data")
        return
    
    st.success(f"✅ **ETL Status**: {etl_message}")
    
    # Initialize analytics
    analytics = AdvancedWildlifeAnalytics()
    
    # Analytics Controls in main content area
    st.subheader("Analytics Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        auto_run = st.checkbox("Auto-run analytics", value=True)
    
    with col2:
        min_observations = st.slider("Min observations for trends", 5, 50, 10)
    
    with col3:
        hotspot_radius = st.slider("Hotspot radius (km)", 10, 100, 50)
    
    with col4:
        if st.button("Run Full Analysis"):
            st.session_state.run_advanced_analytics = True
    
    st.markdown("---")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Population Trends", 
        "Biodiversity Hotspots", 
        "Conservation Alerts", 
        "Ecosystem Health", 
        "ML Insights"
    ])
    
    # Load data once
    if auto_run or st.session_state.get('run_advanced_analytics', False):
        with st.spinner("Loading comprehensive wildlife data for advanced analysis..."):
            try:
                data = analytics.load_comprehensive_data()
                
                if data.empty:
                    st.warning("⚠️ No data available for advanced analysis. Please run ETL pipeline first.")
                    return
                
                st.success(f"✅ Loaded {len(data)} records for {data['species'].nunique()} species")
                
                # Population Trends Tab
                with tab1:
                    st.subheader("📈 Species Population Trend Analysis")
                    
                    with st.spinner("Analyzing population trends..."):
                        trends = analytics.analyze_population_trends(data, min_observations)
                    
                    if trends:
                        # Create trend summary
                        trend_summary = {}
                        for trend_type in ['declining', 'stable', 'increasing']:
                            trend_summary[trend_type] = len([s for s, t in trends.items() 
                                                           if t['trend_status'] == trend_type])
                        
                        # Display metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("📉 Declining Species", trend_summary['declining'], 
                                     delta=-trend_summary['declining'] if trend_summary['declining'] > 0 else None)
                        
                        with col2:
                            st.metric("📊 Stable Species", trend_summary['stable'])
                        
                        with col3:
                            st.metric("📈 Increasing Species", trend_summary['increasing'], 
                                     delta=trend_summary['increasing'] if trend_summary['increasing'] > 0 else None)
                        
                        with col4:
                            avg_confidence = sum([t['confidence'] for t in trends.values()]) / len(trends)
                            st.metric("🎯 Avg Confidence", f"{avg_confidence:.2f}")
                        
                        # Trend details
                        st.markdown("#### 📋 Species Trend Details")
                        
                        trend_df = pd.DataFrame([
                            {
                                'Species': species,
                                'Trend Status': info['trend_status'].title(),
                                'Trend Slope': f"{info['trend_slope']:.3f}",
                                'Confidence': f"{info['confidence']:.2f}",
                                'Total Observations': info['total_observations'],
                                'Avg Monthly Count': f"{info['average_monthly_count']:.1f}"
                            }
                            for species, info in trends.items()
                        ])
                        
                        # Color-code by trend status
                        def color_trend_status(val):
                            if val == 'Declining':
                                return 'background-color: #ffebee'
                            elif val == 'Increasing':
                                return 'background-color: #e8f5e8'
                            else:
                                return 'background-color: #fff3e0'
                        
                        styled_df = trend_df.style.map(color_trend_status, subset=['Trend Status'])
                        st.dataframe(styled_df, use_container_width=True)
                        
                        # Download trends data
                        csv = trend_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Trends Data",
                            data=csv,
                            file_name=f"population_trends_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )
                    
                    else:
                        st.info("ℹ️ Insufficient data for trend analysis. Increase observation data or lower minimum thresholds.")
                
                # Biodiversity Hotspots Tab
                with tab2:
                    st.subheader("🌍 Biodiversity Hotspot Detection")
                    
                    with st.spinner("Detecting biodiversity hotspots..."):
                        hotspots = analytics.detect_biodiversity_hotspots(data, hotspot_radius, 5)
                    
                    if hotspots:
                        st.success(f"✅ Detected {len(hotspots)} biodiversity hotspots")
                        
                        # Hotspot summary metrics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            total_species = sum([h.species_count for h in hotspots])
                            st.metric("🌟 Total Hotspot Species", total_species)
                        
                        with col2:
                            high_priority = len([h for h in hotspots if h.conservation_priority > 0.7])
                            st.metric("🔥 High Priority Hotspots", high_priority)
                        
                        with col3:
                            avg_priority = sum([h.conservation_priority for h in hotspots]) / len(hotspots)
                            st.metric("⭐ Avg Priority Score", f"{avg_priority:.2f}")
                        
                        # Hotspot details
                        st.markdown("#### 📍 Hotspot Details")
                        
                        hotspot_data = []
                        for i, hotspot in enumerate(hotspots):
                            hotspot_data.append({
                                'Rank': i + 1,
                                'Location': f"{hotspot.center_lat:.2f}, {hotspot.center_lon:.2f}",
                                'Species Count': hotspot.species_count,
                                'Radius (km)': f"{hotspot.radius_km:.1f}",
                                'Priority Score': f"{hotspot.conservation_priority:.2f}",
                                'Ecosystem Type': hotspot.ecosystem_type,
                                'Endemic Species': len(hotspot.endemic_species)
                            })
                        
                        hotspot_df = pd.DataFrame(hotspot_data)
                        st.dataframe(hotspot_df, use_container_width=True)
                        
                        # Map visualization
                        try:
                            import plotly.graph_objects as go
                            
                            fig = go.Figure()
                            
                            # Add hotspots to map
                            for hotspot in hotspots:
                                fig.add_trace(go.Scattergeo(
                                    lon=[hotspot.center_lon],
                                    lat=[hotspot.center_lat],
                                    text=f"Species: {hotspot.species_count}<br>Priority: {hotspot.conservation_priority:.2f}",
                                    mode='markers',
                                    marker=dict(
                                        size=10 + hotspot.conservation_priority * 20,
                                        color=hotspot.conservation_priority,
                                        colorscale='Viridis',
                                        showscale=True,
                                        colorbar=dict(title="Priority Score")
                                    ),
                                    name="Biodiversity Hotspots"
                                ))
                            
                            fig.update_layout(
                                title="🌍 Australian Biodiversity Hotspots",
                                geo=dict(
                                    scope='oceania',  # Fixed: was 'australia', now 'oceania'
                                    showland=True,
                                    landcolor='lightgray',
                                    coastlinecolor='black',
                                    projection_type='natural earth'
                                ),
                                height=500
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                        except ImportError:
                            st.info("📍 Map visualization requires plotly. Install with: pip install plotly")
                    
                    else:
                        st.info("ℹ️ No biodiversity hotspots detected. Try adjusting parameters or adding more data.")
                
                # Conservation Alerts Tab
                with tab3:
                    st.subheader("🚨 Conservation Risk Assessment")
                    
                    with st.spinner("Assessing conservation risks..."):
                        alerts = analytics.assess_conservation_risk(trends if 'trends' in locals() else {}, data)
                    
                    if alerts:
                        # Alert summary
                        alert_counts = {}
                        for severity in ['critical', 'high', 'medium', 'low']:
                            alert_counts[severity] = len([a for a in alerts if a.severity == severity])
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("🚨 Critical Alerts", alert_counts['critical'], 
                                     delta=-alert_counts['critical'] if alert_counts['critical'] > 0 else None)
                        
                        with col2:
                            st.metric("⚠️ High Risk", alert_counts['high'])
                        
                        with col3:
                            st.metric("🔔 Medium Risk", alert_counts['medium'])
                        
                        with col4:
                            st.metric("ℹ️ Low Risk", alert_counts['low'])
                        
                        # Alert details
                        st.markdown("#### 🚨 Active Conservation Alerts")
                        
                        for alert in alerts:
                            severity_colors = {
                                'critical': '🚨',
                                'high': '⚠️',
                                'medium': '🔔',
                                'low': 'ℹ️'
                            }
                            
                            with st.expander(f"{severity_colors[alert.severity]} {alert.species} - {alert.alert_type.replace('_', ' ').title()}"):
                                st.markdown(f"**Description:** {alert.description}")
                                st.markdown(f"**Confidence:** {alert.confidence:.2f}")
                                st.markdown(f"**Detected:** {alert.detected_at.strftime('%Y-%m-%d %H:%M')}")
                                
                                if alert.recommendations:
                                    st.markdown("**Recommendations:**")
                                    for rec in alert.recommendations:
                                        st.markdown(f"• {rec}")
                    
                    else:
                        st.success("✅ No critical conservation alerts detected!")
                
                # Ecosystem Health Tab
                with tab4:
                    st.subheader("🌿 Ecosystem Health Report")
                    
                    with st.spinner("Generating ecosystem health report..."):
                        hotspots_for_report = hotspots if 'hotspots' in locals() else []
                        alerts_for_report = alerts if 'alerts' in locals() else []
                        report = analytics.generate_ecosystem_health_report(data, hotspots_for_report, alerts_for_report)
                    
                    if report:
                        # Health score display
                        health_score = report['ecosystem_health_score']
                        
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # Create a gauge chart for health score
                            fig = go.Figure(go.Indicator(
                                mode = "gauge+number+delta",
                                value = health_score * 100,
                                domain = {'x': [0, 1], 'y': [0, 1]},
                                title = {'text': "Ecosystem Health Score"},
                                delta = {'reference': 80},
                                gauge = {
                                    'axis': {'range': [None, 100]},
                                    'bar': {'color': "darkgreen" if health_score > 0.8 else "orange" if health_score > 0.6 else "red"},
                                    'steps': [
                                        {'range': [0, 50], 'color': "lightgray"},
                                        {'range': [50, 80], 'color': "gray"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': 90
                                    }
                                }
                            ))
                            
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.markdown("#### 📊 Key Metrics")
                            
                            metrics = report['data_summary']
                            biodiversity = report['biodiversity_metrics']
                            conservation = report['conservation_status']
                            
                            st.metric("📈 Total Records", f"{metrics['total_records']:,}")
                            st.metric("🐨 Species Count", metrics['species_count'])
                            st.metric("🌍 Hotspots", biodiversity['hotspots_count'])
                            st.metric("🚨 Active Alerts", conservation['total_alerts'])
                        
                        # Detailed report sections
                        with st.expander("📋 Detailed Report", expanded=True):
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**Geographic Coverage**")
                                state_data = metrics['geographic_coverage']['states']
                                for state, count in list(state_data.items())[:5]:  # Show top 5
                                    st.markdown(f"• {state}: {count:,} records")
                            
                            with col2:
                                st.markdown("**Conservation Summary**")
                                if conservation['species_at_risk']:
                                    st.markdown("**Species at Risk:**")
                                    for species in conservation['species_at_risk'][:5]:
                                        st.markdown(f"• {species}")
                                    if len(conservation['species_at_risk']) > 5:
                                        st.markdown(f"• ... and {len(conservation['species_at_risk'])-5} more")
                            

                            st.markdown("**🎯 Management Recommendations**")
                            for i, rec in enumerate(report.get('recommendations', []), 1):
                                st.markdown(f"{i}. {rec}")
                        
                        # Download report
                        report_json = json.dumps(report, indent=2, default=str)
                        st.download_button(
                            label="📥 Download Full Report",
                            data=report_json,
                            file_name=f"ecosystem_health_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                            mime="application/json"
                        )
                
                # ML Insights Tab
                with tab5:
                    st.subheader("🤖 Machine Learning Insights")
                    
                    st.markdown("""
                    **Advanced ML capabilities available in this analytics platform:**
                    """)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        **🔍 Current ML Features:**
                        - Population trend analysis using Random Forest
                        - Biodiversity hotspot detection with DBSCAN clustering
                        - Anomaly detection for conservation alerts
                        - Spatial pattern recognition
                        - Time series forecasting capabilities
                        """)
                    
                    with col2:
                        st.markdown("""
                        **🚀 Future ML Enhancements:**
                        - Deep learning species classification
                        - Climate change impact prediction
                        - Migration pattern analysis
                        - Habitat suitability modeling
                        - Real-time early warning systems
                        """)
                    
                    # Model performance metrics if available
                    if 'trends' in locals() and trends:
                        st.markdown("#### 📊 Model Performance")
                        
                        confidences = [t['confidence'] for t in trends.values()]
                        avg_confidence = sum(confidences) / len(confidences)
                        high_confidence = len([c for c in confidences if c > 0.7])
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("🎯 Avg Model Confidence", f"{avg_confidence:.2f}")
                        
                        with col2:
                            st.metric("✅ High Confidence Predictions", high_confidence)
                        
                        with col3:
                            st.metric("📈 Models Evaluated", len(trends))
                    
                    # ML Configuration
                    with st.expander("⚙️ ML Configuration", expanded=False):
                        st.markdown("**Current ML Parameters:**")
                        st.code(f"""
# Trend Analysis
- Min observations: {min_observations}
- Model: Random Forest Regressor
- Cross-validation: Temporal splits
- R² threshold: 0.3

# Clustering
- Algorithm: DBSCAN
- Distance metric: Haversine (geographic)
- Epsilon: {hotspot_radius} km
- Min samples: 5

# Anomaly Detection
- Method: Isolation Forest
- Contamination: 0.1
- Features: Spatial, temporal, abundance
                        """)
                
                # Reset the run flag
                if st.session_state.get('run_advanced_analytics', False):
                    st.session_state.run_advanced_analytics = False
                
            except Exception as e:
                st.error(f"Error in advanced analytics: {e}")
                st.exception(e)
    
    else:
        st.info("👆 Enable 'Auto-run analytics' in the sidebar or click 'Run Full Analysis' to begin.")
        
        # Show preview capabilities
        st.markdown("#### 🚀 Advanced Analytics Capabilities")
        
        features = [
            ("📈 Population Trends", "Machine learning-powered trend analysis using Random Forest regression"),
            ("🌍 Biodiversity Hotspots", "Spatial clustering to identify high-diversity conservation areas"),
            ("🚨 Conservation Alerts", "Automated risk assessment with severity classification"),
            ("🌿 Ecosystem Health", "Comprehensive health scoring with management recommendations"),
            ("🤖 ML Insights", "Advanced machine learning model performance and configuration")
        ]
        
        for feature, description in features:
            with st.expander(feature):
                st.markdown(description)

# ...existing code...

def main():
    """Main Streamlit application"""
    
    # Import required modules at function level
    import subprocess
    import sys
    import os
    
    # Animated Developer Credit Popup
    st.markdown("""
    <div class="developer-popup">
        Developed by - Mir Hasibul Hasan Rahat
    </div>
    """, unsafe_allow_html=True)
    
    # Compact sidebar navigation
    st.sidebar.title("Wildlife Analytics")
    
    # Initialize session state for page selection
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "Dashboard"
    
    # Create navigation buttons with descriptions
    pages = {
        "Dashboard": render_main_dashboard,
        "ETL Monitoring": render_etl_monitoring,
        "Data Quality": render_data_quality_dashboard,
        "Species Explorer": render_species_explorer,
        "Multi-Source Analytics": render_multi_source_analytics,
        "Advanced Analytics": render_advanced_analytics
    }
    
    # Compact page descriptions
    page_descriptions = {
        "Dashboard": "Overview & metrics",
        "ETL Monitoring": "Pipeline status",
        "Data Quality": "Data analysis",
        "Species Explorer": "Species insights",
        "Multi-Source Analytics": "Cross-platform data",
        "Advanced Analytics": "ML analysis"
    }
    
    # Current page indicator (more compact)
    st.sidebar.markdown(f"**Active:** {st.session_state.selected_page}")
    
    # Navigation buttons (more compact)
    
    for i, page_name in enumerate(pages.keys(), 1):
        # Use different styling for current page
        button_type = "primary" if page_name == st.session_state.selected_page else "secondary"
        
        # Compact button label
        button_label = f"{i}. {page_name}"
        
        if st.sidebar.button(
            button_label, 
            key=f"nav_{page_name}", 
            use_container_width=True,
            type=button_type,
            help=page_descriptions.get(page_name, "")
        ):
            st.session_state.selected_page = page_name
            st.rerun()  # Refresh to show new page immediately
    
    selected_page = st.session_state.selected_page
    
    # Compact ETL Controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("ETL")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        # Initialize session state for ETL tracking
        if 'etl_last_run' not in st.session_state:
            st.session_state.etl_last_run = None
        if 'etl_status' not in st.session_state:
            st.session_state.etl_status = 'Not Run'
        if 'etl_run_in_session' not in st.session_state:
            st.session_state.etl_run_in_session = False
            
        # Create enhanced ETL button
        dashboard_temp = WildlifeDashboard()
        etl_executed, etl_message = dashboard_temp.check_etl_execution_status()
        
        if etl_executed:
            button_text = "🔄 Re-run ETL Demo"
            button_help = "Re-execute ETL pipeline to refresh data"
        else:
            button_text = "▶️ Run ETL Demo"
            button_help = "Execute ETL pipeline to collect wildlife data"
            
        if st.button(button_text, help=button_help):
            with st.spinner("Running ETL pipeline..."):
                
                try:
                    # Get the correct paths
                    current_dir = os.getcwd()
                    script_path = os.path.join(current_dir, "scripts", "enhanced_etl_demo.py")
                    
                    # Update session state
                    st.session_state.etl_status = 'Running'
                    
                    # Run the ETL pipeline with proper encoding
                    result = subprocess.run(
                        [sys.executable, script_path], 
                        capture_output=True, 
                        text=True,
                        cwd=current_dir,
                        timeout=120,  # 2 minute timeout for sidebar
                        encoding='utf-8',
                        errors='replace',
                        env=dict(os.environ, PYTHONIOENCODING='utf-8')
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ ETL demo completed!")
                        st.session_state.etl_status = 'Success'
                        st.session_state.etl_last_run = pd.Timestamp.now()
                        st.session_state.etl_run_in_session = True  # Mark ETL as run in this session
                        st.cache_data.clear()  # Refresh dashboard data
                        st.info("🔄 **Data refreshed!** Navigate to other pages to see updated results.")
                    else:
                        st.error("❌ ETL demo failed!")
                        st.session_state.etl_status = 'Failed'
                        if result.stderr:
                            st.text(f"Error: {result.stderr[:200]}...")
                
                except subprocess.TimeoutExpired:
                    st.error("⏰ ETL timed out. Try manual execution.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Try: `python scripts/enhanced_etl_demo.py`")
    
    with col2:
        if st.button("Refresh Data", help="Refresh dashboard data"):
            st.cache_data.clear()
            st.success("Data refreshed!")
    
    # ETL Status Indicator
    st.sidebar.markdown("---")
    dashboard_temp = WildlifeDashboard()
    etl_executed, etl_message = dashboard_temp.check_etl_execution_status()
    
    if etl_executed:
        st.sidebar.success("✅ ETL: Ready")
        st.sidebar.caption("Wildlife data available")
    else:
        st.sidebar.error("⚠️ ETL: Required")
        st.sidebar.caption("Run ETL Demo first")
    
    # Compact Stats (conditional on ETL execution)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Stats")
    
    dashboard_temp = WildlifeDashboard()
    etl_executed, _ = dashboard_temp.check_etl_execution_status()
    
    if etl_executed:
        # Show real stats only after ETL is run in current session
        etl_summary = dashboard_temp.load_etl_layers_summary()
        
        if etl_summary:
            st.sidebar.metric("Total Records", f"{etl_summary['silver_count']:,}")
            st.sidebar.metric("Data Quality", f"{etl_summary['avg_quality']:.3f}")
            
            if etl_summary['total_jobs'] > 0:
                success_rate = (etl_summary['successful_jobs'] / etl_summary['total_jobs']) * 100
                st.sidebar.metric("ETL Success Rate", f"{success_rate:.1f}%")
    else:
        # Show placeholder stats before ETL is run
        st.sidebar.metric("Total Records", "---", help="Run ETL Demo to see stats")
        st.sidebar.metric("Data Quality", "---", help="Run ETL Demo to see stats")
        st.sidebar.metric("ETL Success Rate", "---", help="Run ETL Demo to see stats")
    
    # Render selected page
    pages[selected_page]()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Australian Biodiversity Analytics Platform | Built with Streamlit & Real Wildlife Data</p>
        <p><strong>Developed by - Mir Hasibul Hasan Rahat</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
