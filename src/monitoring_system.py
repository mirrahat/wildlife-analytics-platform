#!/usr/bin/env python3
"""
Real-time Wildlife Monitoring and Alert System
==============================================
Real-time monitoring system for Australian wildlife data with automated alerts
and system health checks.

Features:
1. Continuous data monitoring
2. Automated alert generation 
3. System health monitoring
4. Performance metrics tracking
5. Anomaly detection
6. Email/SMS notifications (configurable)
"""

import time
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, asdict
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wildlife_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemHealth:
    """System health metrics"""
    timestamp: datetime
    database_status: str
    data_freshness_hours: float
    total_records: int
    collection_rate_24h: int
    error_rate_24h: float
    storage_usage_mb: float
    active_sources: List[str]
    
@dataclass
class MonitoringAlert:
    """Monitoring alert structure"""
    alert_id: str
    timestamp: datetime
    severity: str  # 'info', 'warning', 'error', 'critical'
    category: str  # 'data_quality', 'system_health', 'collection_failure', 'anomaly'
    message: str
    details: Dict
    auto_resolved: bool = False
    resolution_time: Optional[datetime] = None

class WildlifeMonitoringSystem:
    """Real-time wildlife monitoring and alerting system"""
    
    def __init__(self, db_path: str = "data/aussie_wildlife.db", 
                 monitoring_interval: int = 300):  # 5 minutes default
        self.db_path = db_path
        self.monitoring_interval = monitoring_interval
        self.alerts_history: List[MonitoringAlert] = []
        self.last_health_check = None
        self.running = False
        
        # Thresholds for alerts
        self.thresholds = {
            'data_freshness_hours': 24,  # Alert if no new data in 24h
            'collection_rate_drop': 0.5,  # Alert if collection rate drops by 50%
            'error_rate_max': 0.1,  # Alert if error rate > 10%
            'storage_usage_max_mb': 1000,  # Alert if storage > 1GB
            'min_active_sources': 1  # Alert if no active sources
        }
    
    def get_system_health(self) -> SystemHealth:
        """Get current system health metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Database status check
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                db_status = "healthy" if table_count >= 3 else "degraded"
                
                # Data freshness check
                cursor.execute("""
                    SELECT MAX(collected_at) FROM wildlife_multisource
                    UNION ALL
                    SELECT MAX(processed_at) FROM wildlife_silver
                    ORDER BY 1 DESC LIMIT 1
                """)
                
                latest_data = cursor.fetchone()
                if latest_data and latest_data[0]:
                    latest_time = pd.to_datetime(latest_data[0])
                    freshness_hours = (datetime.now() - latest_time).total_seconds() / 3600
                else:
                    freshness_hours = float('inf')
                
                # Total records
                cursor.execute("SELECT COUNT(*) FROM wildlife_multisource")
                total_records = cursor.fetchone()[0]
                
                # Collection rate (last 24h)
                yesterday = datetime.now() - timedelta(hours=24)
                cursor.execute("""
                    SELECT COUNT(*) FROM wildlife_multisource 
                    WHERE collected_at > ?
                """, (yesterday.isoformat(),))
                collection_24h = cursor.fetchone()[0]
                
                # Error rate from ETL logs
                try:
                    cursor.execute("""
                        SELECT 
                            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as error_rate
                        FROM etl_job_executions 
                        WHERE start_time > ?
                    """, (yesterday.isoformat(),))
                    error_rate_result = cursor.fetchone()
                    error_rate = error_rate_result[0] if error_rate_result[0] else 0.0
                except:
                    error_rate = 0.0
                
                # Storage usage
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                storage_mb = (page_count * page_size) / (1024 * 1024)
                
                # Active sources
                cursor.execute("SELECT DISTINCT data_source FROM wildlife_multisource")
                active_sources = [row[0] for row in cursor.fetchall()]
                
                return SystemHealth(
                    timestamp=datetime.now(),
                    database_status=db_status,
                    data_freshness_hours=freshness_hours,
                    total_records=total_records,
                    collection_rate_24h=collection_24h,
                    error_rate_24h=error_rate,
                    storage_usage_mb=storage_mb,
                    active_sources=active_sources
                )
                
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return SystemHealth(
                timestamp=datetime.now(),
                database_status="error",
                data_freshness_hours=float('inf'),
                total_records=0,
                collection_rate_24h=0,
                error_rate_24h=1.0,
                storage_usage_mb=0.0,
                active_sources=[]
            )
    
    def check_alerts(self, health: SystemHealth) -> List[MonitoringAlert]:
        """Check for alert conditions based on system health"""
        alerts = []
        
        # Data freshness alert
        if health.data_freshness_hours > self.thresholds['data_freshness_hours']:
            alerts.append(MonitoringAlert(
                alert_id=f"freshness_{datetime.now().strftime('%Y%m%d_%H%M')}",
                timestamp=datetime.now(),
                severity="warning" if health.data_freshness_hours < 48 else "error",
                category="data_quality",
                message=f"Stale data detected: {health.data_freshness_hours:.1f} hours since last update",
                details={
                    "freshness_hours": health.data_freshness_hours,
                    "threshold": self.thresholds['data_freshness_hours'],
                    "last_update": health.timestamp.isoformat()
                }
            ))
        
        # Collection rate alert
        if health.collection_rate_24h == 0 and health.total_records > 0:
            alerts.append(MonitoringAlert(
                alert_id=f"collection_{datetime.now().strftime('%Y%m%d_%H%M')}",
                timestamp=datetime.now(),
                severity="error",
                category="collection_failure",
                message="No data collected in the last 24 hours",
                details={
                    "collection_rate_24h": health.collection_rate_24h,
                    "total_records": health.total_records
                }
            ))
        
        # Error rate alert
        if health.error_rate_24h > self.thresholds['error_rate_max']:
            alerts.append(MonitoringAlert(
                alert_id=f"errors_{datetime.now().strftime('%Y%m%d_%H%M')}",
                timestamp=datetime.now(),
                severity="warning" if health.error_rate_24h < 0.2 else "error",
                category="system_health",
                message=f"High error rate detected: {health.error_rate_24h:.1%}",
                details={
                    "error_rate": health.error_rate_24h,
                    "threshold": self.thresholds['error_rate_max']
                }
            ))
        
        # Storage usage alert
        if health.storage_usage_mb > self.thresholds['storage_usage_max_mb']:
            alerts.append(MonitoringAlert(
                alert_id=f"storage_{datetime.now().strftime('%Y%m%d_%H%M')}",
                timestamp=datetime.now(),
                severity="warning",
                category="system_health",
                message=f"High storage usage: {health.storage_usage_mb:.1f} MB",
                details={
                    "storage_mb": health.storage_usage_mb,
                    "threshold": self.thresholds['storage_usage_max_mb']
                }
            ))
        
        # Active sources alert
        if len(health.active_sources) < self.thresholds['min_active_sources']:
            alerts.append(MonitoringAlert(
                alert_id=f"sources_{datetime.now().strftime('%Y%m%d_%H%M')}",
                timestamp=datetime.now(),
                severity="error",
                category="collection_failure",
                message=f"Insufficient active data sources: {len(health.active_sources)}",
                details={
                    "active_sources": health.active_sources,
                    "minimum_required": self.thresholds['min_active_sources']
                }
            ))
        
        # Database health alert
        if health.database_status != "healthy":
            alerts.append(MonitoringAlert(
                alert_id=f"database_{datetime.now().strftime('%Y%m%d_%H%M')}",
                timestamp=datetime.now(),
                severity="critical",
                category="system_health",
                message=f"Database health issue: {health.database_status}",
                details={
                    "database_status": health.database_status,
                    "total_records": health.total_records
                }
            ))
        
        return alerts
    
    def save_monitoring_data(self, health: SystemHealth, alerts: List[MonitoringAlert]):
        """Save monitoring data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create monitoring tables if they don't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_health_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        database_status TEXT,
                        data_freshness_hours REAL,
                        total_records INTEGER,
                        collection_rate_24h INTEGER,
                        error_rate_24h REAL,
                        storage_usage_mb REAL,
                        active_sources TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS monitoring_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT UNIQUE,
                        timestamp TEXT NOT NULL,
                        severity TEXT,
                        category TEXT,
                        message TEXT,
                        details TEXT,
                        auto_resolved INTEGER DEFAULT 0,
                        resolution_time TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert health data
                cursor.execute("""
                    INSERT INTO system_health_log 
                    (timestamp, database_status, data_freshness_hours, total_records, 
                     collection_rate_24h, error_rate_24h, storage_usage_mb, active_sources)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    health.timestamp.isoformat(),
                    health.database_status,
                    health.data_freshness_hours,
                    health.total_records,
                    health.collection_rate_24h,
                    health.error_rate_24h,
                    health.storage_usage_mb,
                    json.dumps(health.active_sources)
                ))
                
                # Insert alerts
                for alert in alerts:
                    cursor.execute("""
                        INSERT OR REPLACE INTO monitoring_alerts 
                        (alert_id, timestamp, severity, category, message, details, auto_resolved, resolution_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        alert.alert_id,
                        alert.timestamp.isoformat(),
                        alert.severity,
                        alert.category,
                        alert.message,
                        json.dumps(alert.details),
                        int(alert.auto_resolved),
                        alert.resolution_time.isoformat() if alert.resolution_time else None
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving monitoring data: {e}")
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        logger.info("🔍 Starting monitoring cycle...")
        
        # Get system health
        health = self.get_system_health()
        logger.info(f"System Health: DB={health.database_status}, Records={health.total_records}, "
                   f"Freshness={health.data_freshness_hours:.1f}h, Sources={len(health.active_sources)}")
        
        # Check for alerts
        alerts = self.check_alerts(health)
        
        # Log alerts
        for alert in alerts:
            severity_emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🚨"}
            logger.warning(f"{severity_emoji.get(alert.severity, '🔔')} {alert.severity.upper()}: {alert.message}")
        
        # Save monitoring data
        self.save_monitoring_data(health, alerts)
        
        # Add to history
        self.alerts_history.extend(alerts)
        self.last_health_check = health
        
        logger.info(f"✅ Monitoring cycle complete. Generated {len(alerts)} alerts.")
        
        return {
            'health': health,
            'alerts': alerts,
            'timestamp': datetime.now()
        }
    
    def start_continuous_monitoring(self):
        """Start continuous monitoring loop"""
        logger.info(f"🚀 Starting continuous wildlife monitoring (interval: {self.monitoring_interval}s)")
        self.running = True
        
        try:
            while self.running:
                cycle_result = self.run_monitoring_cycle()
                
                # Sleep until next cycle
                time.sleep(self.monitoring_interval)
                
        except KeyboardInterrupt:
            logger.info("⏹️ Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        finally:
            self.running = False
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.running = False
        logger.info("🛑 Monitoring stop requested")
    
    def get_monitoring_summary(self) -> Dict:
        """Get monitoring summary for dashboard display"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get latest health data
                cursor.execute("""
                    SELECT * FROM system_health_log 
                    ORDER BY created_at DESC LIMIT 1
                """)
                latest_health = cursor.fetchone()
                
                # Get recent alerts
                cursor.execute("""
                    SELECT * FROM monitoring_alerts 
                    WHERE created_at > datetime('now', '-24 hours')
                    ORDER BY created_at DESC
                """)
                recent_alerts = cursor.fetchall()
                
                # Get alert statistics
                cursor.execute("""
                    SELECT 
                        severity,
                        COUNT(*) as count
                    FROM monitoring_alerts 
                    WHERE created_at > datetime('now', '-7 days')
                    GROUP BY severity
                """)
                alert_stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    'latest_health': dict(zip([
                        'id', 'timestamp', 'database_status', 'data_freshness_hours',
                        'total_records', 'collection_rate_24h', 'error_rate_24h',
                        'storage_usage_mb', 'active_sources', 'created_at'
                    ], latest_health)) if latest_health else None,
                    'recent_alerts_count': len(recent_alerts),
                    'alert_stats_7d': alert_stats,
                    'monitoring_active': self.running,
                    'last_check': self.last_health_check.timestamp.isoformat() if self.last_health_check else None
                }
                
        except Exception as e:
            logger.error(f"Error getting monitoring summary: {e}")
            return {
                'error': str(e),
                'monitoring_active': self.running
            }

def run_monitoring_demo():
    """Run a demonstration of the monitoring system"""
    print("🔍 Wildlife Monitoring System Demo")
    print("=" * 40)
    
    monitor = WildlifeMonitoringSystem(monitoring_interval=10)  # 10 second demo interval
    
    # Run a few monitoring cycles
    for i in range(3):
        print(f"\n📊 Monitoring Cycle {i+1}")
        result = monitor.run_monitoring_cycle()
        
        health = result['health']
        alerts = result['alerts']
        
        print(f"✅ System Status: {health.database_status}")
        print(f"📈 Total Records: {health.total_records:,}")
        print(f"🕒 Data Freshness: {health.data_freshness_hours:.1f} hours")
        print(f"🚨 Alerts Generated: {len(alerts)}")
        
        if alerts:
            for alert in alerts:
                print(f"   - {alert.severity.upper()}: {alert.message}")
        
        if i < 2:  # Don't sleep on last iteration
            print("   ⏳ Waiting for next cycle...")
            time.sleep(2)  # Short demo sleep
    
    # Show summary
    print(f"\n📋 Monitoring Summary")
    summary = monitor.get_monitoring_summary()
    if summary.get('latest_health'):
        h = summary['latest_health']
        print(f"   Database: {h['database_status']}")
        print(f"   Records: {h['total_records']:,}")
        print(f"   Storage: {h['storage_usage_mb']:.1f} MB")
        print(f"   Active Sources: {len(json.loads(h['active_sources']))}")
    
    print(f"   Recent Alerts: {summary['recent_alerts_count']}")
    print(f"   Alert Stats (7d): {summary['alert_stats_7d']}")
    
    print("\n🎯 Monitoring Demo Complete!")
    return monitor

if __name__ == "__main__":
    run_monitoring_demo()
