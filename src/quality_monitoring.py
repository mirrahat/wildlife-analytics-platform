#!/usr/bin/env python3
"""
Real-Time Data Quality Monitoring System
========================================
Contemporary data quality monitoring with automated alerts and continuous assessment.

This module provides enterprise-grade data quality monitoring including:
- Real-time quality metric calculation
- Automated quality threshold monitoring
- Data drift detection and alerts
- Quality trend analysis and reporting
- Proactive quality issue identification
- Statistical process control for data quality
"""

import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import statistics
import threading
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

@dataclass
class QualityMetric:
    """Represents a data quality metric measurement"""
    metric_id: str
    asset_id: str
    metric_name: str
    metric_type: str  # completeness, accuracy, consistency, timeliness, validity
    value: float
    threshold_lower: Optional[float]
    threshold_upper: Optional[float]
    measurement_timestamp: str
    dimensions: Dict[str, Any]  # Additional context like field names, rules applied

@dataclass
class QualityAlert:
    """Represents a data quality alert"""
    alert_id: str
    metric_id: str
    alert_type: str  # threshold_breach, trend_degradation, anomaly_detected
    severity: str  # critical, high, medium, low
    message: str
    triggered_timestamp: str
    acknowledged: bool
    resolved: bool
    resolution_notes: Optional[str]

@dataclass
class QualityTrend:
    """Represents quality trend analysis results"""
    metric_name: str
    trend_direction: str  # improving, stable, degrading
    trend_magnitude: float
    confidence_level: float
    observation_period_days: int
    statistical_significance: bool

class RealTimeQualityMonitor:
    """
    Real-time data quality monitoring with automated alerting.
    Continuously assesses data quality and triggers alerts for issues.
    """
    
    def __init__(self, db_path: str = "aussie_wildlife.db", monitoring_interval: int = 300):
        self.db_path = db_path
        self.monitoring_interval = monitoring_interval  # seconds
        self.monitoring_active = False
        self.alert_handlers = []
        self.setup_monitoring_tables()
        self.quality_thresholds = self._initialize_quality_thresholds()
    
    def setup_monitoring_tables(self):
        """Initialize monitoring database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Quality metrics history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics_history (
                    metric_id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    threshold_lower REAL,
                    threshold_upper REAL,
                    measurement_timestamp TIMESTAMP NOT NULL,
                    dimensions TEXT -- JSON
                )
            ''')
            
            # Quality alerts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_alerts (
                    alert_id TEXT PRIMARY KEY,
                    metric_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    triggered_timestamp TIMESTAMP NOT NULL,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolution_notes TEXT,
                    FOREIGN KEY (metric_id) REFERENCES quality_metrics_history (metric_id)
                )
            ''')
            
            # Monitoring configuration
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_config (
                    config_key TEXT PRIMARY KEY,
                    config_value TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def _initialize_quality_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize quality thresholds for different metrics"""
        return {
            'completeness': {
                'critical_lower': 0.95,
                'warning_lower': 0.90,
                'target': 0.98
            },
            'accuracy': {
                'critical_lower': 0.90,
                'warning_lower': 0.85,
                'target': 0.95
            },
            'consistency': {
                'critical_lower': 0.85,
                'warning_lower': 0.80,
                'target': 0.95
            },
            'timeliness': {
                'critical_upper': 48.0,  # hours
                'warning_upper': 24.0,
                'target': 12.0
            },
            'validity': {
                'critical_lower': 0.95,
                'warning_lower': 0.90,
                'target': 0.98
            }
        }
    
    def start_monitoring(self):
        """Start the real-time monitoring process"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        logger.info(f"Started real-time quality monitoring (interval: {self.monitoring_interval}s)")
    
    def stop_monitoring(self):
        """Stop the real-time monitoring process"""
        self.monitoring_active = False
        logger.info("Stopped real-time quality monitoring")
    
    def _monitoring_loop(self):
        """Main monitoring loop that runs continuously"""
        while self.monitoring_active:
            try:
                # Calculate current quality metrics
                current_metrics = self.calculate_current_quality_metrics()
                
                # Store metrics
                for metric in current_metrics:
                    self._store_quality_metric(metric)
                
                # Check for threshold breaches and anomalies
                alerts = self._check_quality_thresholds(current_metrics)
                alerts.extend(self._detect_quality_anomalies())
                
                # Trigger alerts
                for alert in alerts:
                    self._trigger_alert(alert)
                
                # Sleep until next monitoring cycle
                time.sleep(self.monitoring_interval)
            
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait before retrying
    
    def calculate_current_quality_metrics(self) -> List[QualityMetric]:
        """Calculate current data quality metrics"""
        metrics = []
        current_time = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Completeness metrics
            cursor.execute('SELECT COUNT(*) FROM wildlife_sightings')
            total_records = cursor.fetchone()[0]
            
            if total_records > 0:
                # Field completeness
                key_fields = ['common_name', 'location_description', 'observed_date', 'latitude', 'longitude']
                
                for field in key_fields:
                    cursor.execute(f'''
                        SELECT COUNT(*) FROM wildlife_sightings 
                        WHERE {field} IS NOT NULL AND {field} != ''
                    ''')
                    complete_count = cursor.fetchone()[0]
                    completeness = complete_count / total_records
                    
                    metrics.append(QualityMetric(
                        metric_id=f"completeness_{field}_{int(time.time())}",
                        asset_id="wildlife_observations",
                        metric_name=f"completeness_{field}",
                        metric_type="completeness",
                        value=completeness,
                        threshold_lower=self.quality_thresholds['completeness']['critical_lower'],
                        threshold_upper=None,
                        measurement_timestamp=current_time,
                        dimensions={"field": field, "total_records": total_records}
                    ))
                
                # Accuracy metrics (coordinate validity)
                cursor.execute('''
                    SELECT COUNT(*) FROM wildlife_sightings 
                    WHERE latitude BETWEEN -45 AND -9 AND longitude BETWEEN 112 AND 154
                ''')
                valid_coordinates = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM wildlife_sightings WHERE latitude IS NOT NULL AND longitude IS NOT NULL')
                total_coordinates = cursor.fetchone()[0]
                
                if total_coordinates > 0:
                    coordinate_accuracy = valid_coordinates / total_coordinates
                    
                    metrics.append(QualityMetric(
                        metric_id=f"accuracy_coordinates_{int(time.time())}",
                        asset_id="wildlife_observations",
                        metric_name="accuracy_coordinates",
                        metric_type="accuracy",
                        value=coordinate_accuracy,
                        threshold_lower=self.quality_thresholds['accuracy']['critical_lower'],
                        threshold_upper=None,
                        measurement_timestamp=current_time,
                        dimensions={"valid_coords": valid_coordinates, "total_coords": total_coordinates}
                    ))
                
                # Timeliness metrics (data freshness)
                cursor.execute('''
                    SELECT AVG(JULIANDAY('now') - JULIANDAY(created_at)) * 24 as avg_age_hours
                    FROM wildlife_sightings 
                    WHERE created_at IS NOT NULL
                ''')
                result = cursor.fetchone()
                avg_age_hours = result[0] if result[0] else 0
                
                metrics.append(QualityMetric(
                    metric_id=f"timeliness_data_age_{int(time.time())}",
                    asset_id="wildlife_observations",
                    metric_name="timeliness_data_age",
                    metric_type="timeliness",
                    value=avg_age_hours,
                    threshold_lower=None,
                    threshold_upper=self.quality_thresholds['timeliness']['critical_upper'],
                    measurement_timestamp=current_time,
                    dimensions={"unit": "hours", "calculation": "average_age"}
                ))
                
                # Consistency metrics (duplicate detection)
                cursor.execute('''
                    SELECT COUNT(*) - COUNT(DISTINCT common_name || location_description || observed_date || observer_name) 
                    FROM wildlife_sightings
                ''')
                duplicate_count = cursor.fetchone()[0]
                consistency_score = 1.0 - (duplicate_count / total_records) if total_records > 0 else 1.0
                
                metrics.append(QualityMetric(
                    metric_id=f"consistency_duplicates_{int(time.time())}",
                    asset_id="wildlife_observations",
                    metric_name="consistency_duplicates",
                    metric_type="consistency",
                    value=consistency_score,
                    threshold_lower=self.quality_thresholds['consistency']['critical_lower'],
                    threshold_upper=None,
                    measurement_timestamp=current_time,
                    dimensions={"duplicate_count": duplicate_count, "total_records": total_records}
                ))
        
        return metrics
    
    def _store_quality_metric(self, metric: QualityMetric):
        """Store quality metric in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO quality_metrics_history
                (metric_id, asset_id, metric_name, metric_type, value, 
                 threshold_lower, threshold_upper, measurement_timestamp, dimensions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.metric_id,
                metric.asset_id,
                metric.metric_name,
                metric.metric_type,
                metric.value,
                metric.threshold_lower,
                metric.threshold_upper,
                metric.measurement_timestamp,
                json.dumps(metric.dimensions)
            ))
    
    def _check_quality_thresholds(self, metrics: List[QualityMetric]) -> List[QualityAlert]:
        """Check metrics against quality thresholds and generate alerts"""
        alerts = []
        
        for metric in metrics:
            alert = None
            
            # Check lower thresholds
            if metric.threshold_lower is not None and metric.value < metric.threshold_lower:
                severity = "critical" if metric.value < metric.threshold_lower else "high"
                alert = QualityAlert(
                    alert_id=f"alert_{metric.metric_id}",
                    metric_id=metric.metric_id,
                    alert_type="threshold_breach",
                    severity=severity,
                    message=f"Quality metric {metric.metric_name} fell below threshold: {metric.value:.3f} < {metric.threshold_lower:.3f}",
                    triggered_timestamp=datetime.now().isoformat(),
                    acknowledged=False,
                    resolved=False,
                    resolution_notes=None
                )
            
            # Check upper thresholds
            elif metric.threshold_upper is not None and metric.value > metric.threshold_upper:
                severity = "critical" if metric.value > metric.threshold_upper else "high"
                alert = QualityAlert(
                    alert_id=f"alert_{metric.metric_id}",
                    metric_id=metric.metric_id,
                    alert_type="threshold_breach",
                    severity=severity,
                    message=f"Quality metric {metric.metric_name} exceeded threshold: {metric.value:.3f} > {metric.threshold_upper:.3f}",
                    triggered_timestamp=datetime.now().isoformat(),
                    acknowledged=False,
                    resolved=False,
                    resolution_notes=None
                )
            
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def _detect_quality_anomalies(self) -> List[QualityAlert]:
        """Detect quality anomalies using statistical methods"""
        alerts = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Look for metrics with significant degradation trends
            cursor.execute('''
                SELECT metric_name, AVG(value) as avg_value, COUNT(*) as count
                FROM quality_metrics_history 
                WHERE measurement_timestamp > datetime('now', '-24 hours')
                GROUP BY metric_name
                HAVING count >= 5
            ''')
            
            recent_metrics = cursor.fetchall()
            
            for metric_name, avg_recent, count in recent_metrics:
                # Compare with historical average
                cursor.execute('''
                    SELECT AVG(value) as historical_avg
                    FROM quality_metrics_history 
                    WHERE metric_name = ? 
                    AND measurement_timestamp BETWEEN datetime('now', '-7 days') AND datetime('now', '-24 hours')
                ''', (metric_name,))
                
                historical_result = cursor.fetchone()
                
                if historical_result and historical_result[0]:
                    historical_avg = historical_result[0]
                    
                    # Check for significant degradation (>10% drop)
                    if avg_recent < historical_avg * 0.90:
                        alert = QualityAlert(
                            alert_id=f"anomaly_{metric_name}_{int(time.time())}",
                            metric_id=f"trend_{metric_name}",
                            alert_type="trend_degradation",
                            severity="medium",
                            message=f"Quality degradation detected for {metric_name}: {avg_recent:.3f} vs historical {historical_avg:.3f}",
                            triggered_timestamp=datetime.now().isoformat(),
                            acknowledged=False,
                            resolved=False,
                            resolution_notes=None
                        )
                        alerts.append(alert)
        
        return alerts
    
    def _trigger_alert(self, alert: QualityAlert):
        """Trigger and store a quality alert"""
        # Store alert in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO quality_alerts
                (alert_id, metric_id, alert_type, severity, message, 
                 triggered_timestamp, acknowledged, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id,
                alert.metric_id,
                alert.alert_type,
                alert.severity,
                alert.message,
                alert.triggered_timestamp,
                alert.acknowledged,
                alert.resolved
            ))
        
        # Log the alert
        logger.warning(f"Quality Alert [{alert.severity.upper()}]: {alert.message}")
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def add_alert_handler(self, handler: Callable[[QualityAlert], None]):
        """Add a custom alert handler function"""
        self.alert_handlers.append(handler)
    
    def get_quality_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive quality dashboard data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Current quality metrics
            cursor.execute('''
                SELECT metric_name, metric_type, value, measurement_timestamp
                FROM quality_metrics_history q1
                WHERE measurement_timestamp = (
                    SELECT MAX(measurement_timestamp) 
                    FROM quality_metrics_history q2 
                    WHERE q2.metric_name = q1.metric_name
                )
                ORDER BY metric_name
            ''')
            current_metrics = [dict(row) for row in cursor.fetchall()]
            
            # Recent alerts
            cursor.execute('''
                SELECT alert_type, severity, message, triggered_timestamp, resolved
                FROM quality_alerts
                WHERE triggered_timestamp > datetime('now', '-24 hours')
                ORDER BY triggered_timestamp DESC
                LIMIT 10
            ''')
            recent_alerts = [dict(row) for row in cursor.fetchall()]
            
            # Quality trends
            trends = self._calculate_quality_trends()
            
            # Overall quality score
            overall_score = self._calculate_overall_quality_score()
            
            return {
                'current_metrics': current_metrics,
                'recent_alerts': recent_alerts,
                'quality_trends': trends,
                'overall_quality_score': overall_score,
                'monitoring_status': 'active' if self.monitoring_active else 'inactive',
                'last_updated': datetime.now().isoformat()
            }
    
    def _calculate_quality_trends(self) -> List[QualityTrend]:
        """Calculate quality trends over time"""
        trends = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get metrics for trend analysis
            cursor.execute('''
                SELECT DISTINCT metric_name FROM quality_metrics_history
                WHERE measurement_timestamp > datetime('now', '-7 days')
            ''')
            
            metric_names = [row[0] for row in cursor.fetchall()]
            
            for metric_name in metric_names:
                cursor.execute('''
                    SELECT value, measurement_timestamp
                    FROM quality_metrics_history
                    WHERE metric_name = ?
                    AND measurement_timestamp > datetime('now', '-7 days')
                    ORDER BY measurement_timestamp
                ''', (metric_name,))
                
                data_points = cursor.fetchall()
                
                if len(data_points) >= 5:  # Need minimum data points for trend analysis
                    values = [point[0] for point in data_points]
                    
                    # Simple linear trend calculation
                    n = len(values)
                    x = list(range(n))
                    
                    # Calculate correlation coefficient for trend strength
                    if n > 1:
                        correlation = np.corrcoef(x, values)[0, 1] if not np.isnan(np.corrcoef(x, values)[0, 1]) else 0
                        
                        # Determine trend direction
                        if correlation > 0.3:
                            direction = "improving"
                        elif correlation < -0.3:
                            direction = "degrading"
                        else:
                            direction = "stable"
                        
                        trends.append(QualityTrend(
                            metric_name=metric_name,
                            trend_direction=direction,
                            trend_magnitude=abs(correlation),
                            confidence_level=min(abs(correlation) * 2, 1.0),  # Simple confidence calculation
                            observation_period_days=7,
                            statistical_significance=abs(correlation) > 0.5
                        ))
        
        return trends
    
    def _calculate_overall_quality_score(self) -> float:
        """Calculate overall quality score across all metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get latest values for each metric type
            cursor.execute('''
                SELECT metric_type, AVG(value) as avg_value
                FROM quality_metrics_history q1
                WHERE measurement_timestamp = (
                    SELECT MAX(measurement_timestamp) 
                    FROM quality_metrics_history q2 
                    WHERE q2.metric_name = q1.metric_name
                )
                GROUP BY metric_type
            ''')
            
            metric_averages = dict(cursor.fetchall())
            
            if not metric_averages:
                return 0.0
            
            # Weight different metric types
            weights = {
                'completeness': 0.25,
                'accuracy': 0.30,
                'consistency': 0.20,
                'timeliness': 0.15,
                'validity': 0.10
            }
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for metric_type, avg_value in metric_averages.items():
                weight = weights.get(metric_type, 0.1)
                
                # Normalize timeliness (lower is better)
                if metric_type == 'timeliness':
                    # Convert hours to score (24 hours = 1.0, 0 hours = 0.0)
                    normalized_value = max(0, min(1, 1 - (avg_value / 24)))
                else:
                    normalized_value = avg_value
                
                weighted_score += normalized_value * weight
                total_weight += weight
            
            return weighted_score / total_weight if total_weight > 0 else 0.0

def console_alert_handler(alert: QualityAlert):
    """Simple console-based alert handler"""
    print(f"\n🚨 QUALITY ALERT [{alert.severity.upper()}]")
    print(f"Type: {alert.alert_type}")
    print(f"Message: {alert.message}")
    print(f"Time: {alert.triggered_timestamp}")
    print("-" * 50)

def main():
    """Demonstrate the real-time quality monitoring system"""
    print("REAL-TIME DATA QUALITY MONITORING")
    print("=" * 40)
    
    # Initialize monitor
    monitor = RealTimeQualityMonitor(monitoring_interval=60)  # Check every minute for demo
    
    # Add console alert handler
    monitor.add_alert_handler(console_alert_handler)
    
    # Calculate current metrics
    print("Calculating current quality metrics...")
    metrics = monitor.calculate_current_quality_metrics()
    
    print(f"Calculated {len(metrics)} quality metrics:")
    for metric in metrics:
        print(f"  • {metric.metric_name}: {metric.value:.3f} ({metric.metric_type})")
    
    # Get dashboard data
    dashboard_data = monitor.get_quality_dashboard_data()
    
    print(f"\nOverall Quality Score: {dashboard_data['overall_quality_score']:.3f}")
    print(f"Active Alerts: {len([a for a in dashboard_data['recent_alerts'] if not a['resolved']])}")
    
    # Display trends
    if dashboard_data['quality_trends']:
        print("\nQuality Trends:")
        for trend in dashboard_data['quality_trends']:
            print(f"  • {trend.metric_name}: {trend.trend_direction} (confidence: {trend.confidence_level:.2f})")
    
    print(f"\nReal-time monitoring system ready. Status: {dashboard_data['monitoring_status']}")
    
    # Optionally start monitoring (commented out for demo)
    # monitor.start_monitoring()
    # print("Monitoring started - press Ctrl+C to stop")
    # try:
    #     while True:
    #         time.sleep(10)
    # except KeyboardInterrupt:
    #     monitor.stop_monitoring()
    #     print("Monitoring stopped")

if __name__ == "__main__":
    main()
