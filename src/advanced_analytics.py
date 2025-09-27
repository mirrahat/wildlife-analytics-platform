#!/usr/bin/env python3
"""
Advanced Australian Wildlife Analytics & Machine Learning Module
===============================================================
Advanced analytics, machine learning models, and conservation insights 
for the Australian Biodiversity Analytics Platform.

Features:
1. Species Population Trend Analysis
2. Biodiversity Hotspot Detection
3. Conservation Risk Assessment
4. Species Distribution Modeling
5. Climate Change Impact Prediction
6. Ecosystem Health Scoring
7. Real-time Alert System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
import json

# Machine Learning & Analytics
try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Note: scikit-learn not available. Install with: pip install scikit-learn")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Note: Plotly not available. Install with: pip install plotly")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConservationAlert:
    """Conservation alert data structure"""
    species: str
    alert_type: str  # 'population_decline', 'habitat_loss', 'range_shift', 'anomaly'
    severity: str    # 'low', 'medium', 'high', 'critical'
    description: str
    confidence: float
    recommendations: List[str]
    detected_at: datetime

@dataclass
class BiodiversityHotspot:
    """Biodiversity hotspot data structure"""
    center_lat: float
    center_lon: float
    radius_km: float
    species_count: int
    endemic_species: List[str]
    conservation_priority: float
    ecosystem_type: str

class AdvancedWildlifeAnalytics:
    """Advanced analytics and machine learning for wildlife data"""
    
    def __init__(self, db_path: str = "data/aussie_wildlife.db"):
        self.db_path = db_path
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        
    def load_comprehensive_data(self) -> pd.DataFrame:
        """Load and combine all available wildlife data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load from all available sources with corrected schema
                queries = []
                
                # Multi-source data (primary data source)
                queries.append("""
                SELECT 
                    common_name as species,
                    scientific_name,
                    latitude,
                    longitude,
                    observed_date,
                    location_description as location,
                    data_source,
                    quality_grade as quality_score,
                    collected_at as processed_at,
                    'multisource' as source_table
                FROM wildlife_multisource
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                """)
                
                # Silver layer data if available
                try:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA table_info(wildlife_silver)")
                    silver_columns = [row[1] for row in cursor.fetchall()]
                    
                    if 'common_name' in silver_columns:
                        queries.append("""
                        SELECT 
                            common_name as species,
                            scientific_name,
                            latitude,
                            longitude,
                            observed_date,
                            location_description as location,
                            'silver' as data_source,
                            quality_score,
                            processed_at,
                            'silver' as source_table
                        FROM wildlife_silver
                        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                        """)
                except:
                    pass
                
                # Bronze layer data if available
                try:
                    cursor.execute("PRAGMA table_info(wildlife_bronze)")
                    bronze_columns = [row[1] for row in cursor.fetchall()]
                    
                    if 'common_name' in bronze_columns:
                        queries.append("""
                        SELECT 
                            common_name as species,
                            scientific_name,
                            latitude,
                            longitude,
                            observed_date,
                            location_description as location,
                            'bronze' as data_source,
                            1.0 as quality_score,
                            created_at as processed_at,
                            'bronze' as source_table
                        FROM wildlife_bronze
                        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                        """)
                except:
                    pass
                
                # Combine all available data
                if not queries:
                    logger.warning("No suitable data tables found")
                    return pd.DataFrame()
                
                combined_query = " UNION ALL ".join(queries) + " ORDER BY observed_date DESC"
                
                df = pd.read_sql_query(combined_query, conn)
                
                # Data preprocessing
                df['observed_date'] = pd.to_datetime(df['observed_date'], errors='coerce')
                df['year'] = df['observed_date'].dt.year
                df['month'] = df['observed_date'].dt.month
                df['day_of_year'] = df['observed_date'].dt.dayofyear
                
                # Add Australian states based on coordinates (simplified)
                df['state'] = df.apply(self._estimate_australian_state, axis=1)
                
                logger.info(f"Loaded {len(df)} records for advanced analysis")
                return df
                
        except Exception as e:
            logger.error(f"Error loading comprehensive data: {e}")
            return pd.DataFrame()
    
    def analyze_population_trends(self, data: pd.DataFrame, min_observations: int = 10) -> Dict:
        """Analyze population trends for Australian species"""
        if not SKLEARN_AVAILABLE:
            logger.warning("Scikit-learn required for trend analysis")
            return {}
            
        trends = {}
        
        # Group by species
        for species, group in data.groupby('species'):
            if len(group) < min_observations:
                continue
                
            try:
                # Prepare time series data - create explicit copy and ensure datetime
                group_df = group.reset_index(drop=True).copy()
                
                # Ensure observed_date is datetime
                if 'observed_date' in group_df.columns:
                    group_df['observed_date'] = pd.to_datetime(group_df['observed_date'], errors='coerce')
                    group_df = group_df.dropna(subset=['observed_date'])
                    group_df = group_df.sort_values('observed_date')
                
                if len(group_df) < min_observations:
                    continue
                
                # Create monthly counts without relying on existing column structure
                group_df['year'] = group_df['observed_date'].dt.year
                group_df['month'] = group_df['observed_date'].dt.month
                
                monthly_counts = group_df.groupby(['year', 'month']).size().reset_index(name='count')
                monthly_counts['date'] = pd.to_datetime(monthly_counts[['year', 'month']].assign(day=1))
                monthly_counts = monthly_counts.sort_values('date')
                monthly_counts['days_from_start'] = (monthly_counts['date'] - monthly_counts['date'].min()).dt.days
                
                if len(monthly_counts) < 3:
                    continue
                
                # Fit trend model
                X = monthly_counts[['days_from_start']].values
                y = monthly_counts['count'].values
                
                model = RandomForestRegressor(n_estimators=50, random_state=42)
                model.fit(X, y)
                
                # Calculate trend
                predictions = model.predict(X)
                trend_slope = np.polyfit(X.flatten(), predictions, 1)[0]
                
                # Assess trend significance
                r2 = r2_score(y, predictions)
                
                # Classify trend
                if trend_slope > 0.1 and r2 > 0.3:
                    trend_status = "increasing"
                elif trend_slope < -0.1 and r2 > 0.3:
                    trend_status = "declining"
                else:
                    trend_status = "stable"
                
                trends[species] = {
                    'trend_status': trend_status,
                    'trend_slope': float(trend_slope),
                    'confidence': float(r2),
                    'total_observations': len(group),
                    'observation_months': len(monthly_counts),
                    'latest_count': int(monthly_counts.iloc[-1]['count']),
                    'average_monthly_count': float(monthly_counts['count'].mean())
                }
                
            except Exception as e:
                logger.warning(f"Trend analysis failed for {species}: {e}")
                
        return trends
    
    def detect_biodiversity_hotspots(self, data: pd.DataFrame, eps_km: float = 50.0, 
                                   min_species: int = 5) -> List[BiodiversityHotspot]:
        """Detect biodiversity hotspots using clustering"""
        if not SKLEARN_AVAILABLE:
            logger.warning("Scikit-learn required for hotspot detection")
            return []
            
        try:
            # Prepare coordinate data
            coords_data = data[['latitude', 'longitude', 'species']].dropna()
            
            if len(coords_data) < min_species * 2:
                return []
            
            # Convert to kilometers (approximate)
            coords_km = coords_data[['latitude', 'longitude']].copy()
            coords_km['lat_km'] = coords_km['latitude'] * 111.0  # 1 degree ≈ 111 km
            coords_km['lon_km'] = coords_km['longitude'] * 111.0 * np.cos(np.radians(coords_km['latitude'].mean()))
            
            # DBSCAN clustering
            clustering = DBSCAN(eps=eps_km, min_samples=min_species)
            coords_data['cluster'] = clustering.fit_predict(coords_km[['lat_km', 'lon_km']])
            
            hotspots = []
            
            for cluster_id in coords_data['cluster'].unique():
                if cluster_id == -1:  # Noise points
                    continue
                    
                cluster_data = coords_data[coords_data['cluster'] == cluster_id]
                
                # Calculate hotspot properties
                center_lat = cluster_data['latitude'].mean()
                center_lon = cluster_data['longitude'].mean()
                species_list = cluster_data['species'].unique().tolist()
                species_count = len(species_list)
                
                # Calculate radius (max distance from center)
                distances = []
                for _, row in cluster_data.iterrows():
                    dist = self._haversine_distance(center_lat, center_lon, 
                                                  row['latitude'], row['longitude'])
                    distances.append(dist)
                radius_km = max(distances) if distances else 0
                
                # Conservation priority (based on species diversity and endemic species)
                endemic_species = self._identify_endemic_species(species_list)
                priority = min(species_count / 20.0 + len(endemic_species) / 5.0, 1.0)
                
                hotspot = BiodiversityHotspot(
                    center_lat=center_lat,
                    center_lon=center_lon,
                    radius_km=radius_km,
                    species_count=species_count,
                    endemic_species=endemic_species,
                    conservation_priority=priority,
                    ecosystem_type=self._classify_ecosystem(center_lat, center_lon)
                )
                
                hotspots.append(hotspot)
            
            # Sort by conservation priority
            hotspots.sort(key=lambda x: x.conservation_priority, reverse=True)
            
            logger.info(f"Detected {len(hotspots)} biodiversity hotspots")
            return hotspots
            
        except Exception as e:
            logger.error(f"Hotspot detection failed: {e}")
            return []
    
    def assess_conservation_risk(self, trends: Dict, data: pd.DataFrame) -> List[ConservationAlert]:
        """Assess conservation risks and generate alerts"""
        alerts = []
        
        try:
            for species, trend_info in trends.items():
                recommendations = []
                alert_type = None
                severity = "low"
                confidence = trend_info['confidence']
                
                # Population decline analysis
                if trend_info['trend_status'] == 'declining':
                    if trend_info['trend_slope'] < -0.5:
                        severity = "critical"
                        alert_type = "population_decline"
                        recommendations.extend([
                            "Immediate habitat protection measures",
                            "Population monitoring program",
                            "Breeding program assessment"
                        ])
                    elif trend_info['trend_slope'] < -0.2:
                        severity = "high"
                        alert_type = "population_decline"
                        recommendations.extend([
                            "Enhanced habitat monitoring",
                            "Threat assessment required"
                        ])
                    else:
                        severity = "medium"
                        alert_type = "population_decline"
                        recommendations.append("Continue monitoring")
                
                # Range analysis
                species_data = data[data['species'] == species]
                if len(species_data) > 10:
                    # Check for range changes
                    recent_data = species_data[species_data['observed_date'] > 
                                             (datetime.now() - timedelta(days=365))]
                    historical_data = species_data[species_data['observed_date'] <= 
                                                 (datetime.now() - timedelta(days=365))]
                    
                    if len(recent_data) > 5 and len(historical_data) > 5:
                        recent_range = self._calculate_range_area(recent_data)
                        historical_range = self._calculate_range_area(historical_data)
                        
                        if recent_range < historical_range * 0.7:  # 30% range loss
                            if alert_type != "population_decline" or severity in ["low", "medium"]:
                                alert_type = "habitat_loss"
                                severity = "high"
                                recommendations.extend([
                                    "Habitat connectivity assessment",
                                    "Land use change analysis"
                                ])
                
                # Low observation count
                if trend_info['total_observations'] < 50 and trend_info['observation_months'] > 6:
                    if not alert_type:
                        alert_type = "low_detection"
                        severity = "medium"
                        recommendations.extend([
                            "Survey effort increase needed",
                            "Citizen science engagement"
                        ])
                
                # Create alert if significant risk detected
                if alert_type:
                    description = self._generate_alert_description(species, alert_type, 
                                                                 trend_info, severity)
                    
                    alert = ConservationAlert(
                        species=species,
                        alert_type=alert_type,
                        severity=severity,
                        description=description,
                        confidence=confidence,
                        recommendations=recommendations,
                        detected_at=datetime.now()
                    )
                    
                    alerts.append(alert)
            
            # Sort by severity and confidence
            severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            alerts.sort(key=lambda x: (severity_order[x.severity], x.confidence), reverse=True)
            
            logger.info(f"Generated {len(alerts)} conservation alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"Conservation risk assessment failed: {e}")
            return []
    
    def generate_ecosystem_health_report(self, data: pd.DataFrame, hotspots: List[BiodiversityHotspot], 
                                       alerts: List[ConservationAlert]) -> Dict:
        """Generate comprehensive ecosystem health report"""
        try:
            # Safely handle dates
            try:
                earliest_date = str(data['observed_date'].min()) if not data.empty and 'observed_date' in data.columns else "Unknown"
                latest_date = str(data['observed_date'].max()) if not data.empty and 'observed_date' in data.columns else "Unknown"
            except:
                earliest_date = "Unknown"
                latest_date = "Unknown"
            
            # Safely handle coordinates
            try:
                lat_min = float(data['latitude'].min()) if 'latitude' in data.columns and not data['latitude'].isna().all() else 0.0
                lat_max = float(data['latitude'].max()) if 'latitude' in data.columns and not data['latitude'].isna().all() else 0.0
                lon_min = float(data['longitude'].min()) if 'longitude' in data.columns and not data['longitude'].isna().all() else 0.0
                lon_max = float(data['longitude'].max()) if 'longitude' in data.columns and not data['longitude'].isna().all() else 0.0
            except:
                lat_min = lat_max = lon_min = lon_max = 0.0
            
            # Safely handle states
            try:
                states_dict = {}
                if 'state' in data.columns:
                    state_counts = data['state'].value_counts()
                    states_dict = {str(k): int(v) for k, v in state_counts.items()}
            except:
                states_dict = {}
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'data_summary': {
                    'total_records': len(data),
                    'species_count': data['species'].nunique() if 'species' in data.columns else 0,
                    'date_range': {
                        'earliest': earliest_date,
                        'latest': latest_date
                    },
                    'geographic_coverage': {
                        'states': states_dict,
                        'lat_range': [lat_min, lat_max],
                        'lon_range': [lon_min, lon_max]
                    }
                },
                'biodiversity_metrics': {
                    'hotspots_count': len(hotspots),
                    'high_priority_hotspots': len([h for h in hotspots if h.conservation_priority > 0.7]),
                    'total_hotspot_species': sum([h.species_count for h in hotspots]),
                    'endemic_species_in_hotspots': len(set([str(es) for es in sum([h.endemic_species for h in hotspots], [])]))
                },
                'conservation_status': {
                    'total_alerts': len(alerts),
                    'critical_alerts': len([a for a in alerts if a.severity == 'critical']),
                    'high_risk_alerts': len([a for a in alerts if a.severity == 'high']),
                    'species_at_risk': [str(a.species) for a in alerts]
                },
                'ecosystem_health_score': float(self._calculate_ecosystem_health_score(data, hotspots, alerts)),
                'recommendations': self._generate_ecosystem_recommendations(hotspots, alerts)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Ecosystem health report generation failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {}
    
    def _estimate_australian_state(self, row) -> str:
        """Estimate Australian state/territory from coordinates"""
        lat, lon = row['latitude'], row['longitude']
        
        if pd.isna(lat) or pd.isna(lon):
            return "Unknown"
        
        # Simplified state boundaries (approximate)
        if -44 <= lat <= -39 and 140 <= lon <= 150:
            return "Victoria"
        elif -37 <= lat <= -28 and 140 <= lon <= 154:
            return "New South Wales"
        elif -29 <= lat <= -9 and 138 <= lon <= 154:
            return "Queensland"
        elif -35 <= lat <= -26 and 129 <= lon <= 141:
            return "South Australia"
        elif -35 <= lat <= -15 and 112 <= lon <= 129:
            return "Western Australia"
        elif -43 <= lat <= -39 and 143 <= lon <= 149:
            return "Tasmania"
        elif -26 <= lat <= -11 and 129 <= lon <= 138:
            return "Northern Territory"
        elif -36 <= lat <= -35 and 148 <= lon <= 150:
            return "Australian Capital Territory"
        else:
            return "Other/External Territory"
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
    
    def _identify_endemic_species(self, species_list: List[str]) -> List[str]:
        """Identify potentially endemic Australian species (simplified)"""
        # This is a simplified version - in practice, would use a comprehensive database
        endemic_indicators = ['wallaby', 'kangaroo', 'koala', 'wombat', 'echidna', 
                            'platypus', 'bandicoot', 'quoll', 'bilby', 'numbat']
        
        endemic_species = []
        for species in species_list:
            species_lower = species.lower()
            if any(indicator in species_lower for indicator in endemic_indicators):
                endemic_species.append(species)
        
        return endemic_species
    
    def _classify_ecosystem(self, lat: float, lon: float) -> str:
        """Classify ecosystem type based on coordinates (simplified)"""
        # Simplified ecosystem classification for Australia
        if lat < -35:
            return "Temperate Forest"
        elif -35 <= lat < -25:
            if lon < 130:
                return "Arid/Semi-arid"
            else:
                return "Woodland/Grassland"
        else:
            if lon > 145:
                return "Tropical Rainforest"
            else:
                return "Tropical Savanna"
    
    def _calculate_range_area(self, data: pd.DataFrame) -> float:
        """Calculate approximate range area from coordinate data"""
        if len(data) < 3:
            return 0
        
        lat_range = data['latitude'].max() - data['latitude'].min()
        lon_range = data['longitude'].max() - data['longitude'].min()
        
        # Rough approximation (not accounting for Earth's curvature)
        return lat_range * lon_range * 111.0 * 111.0  # Convert to km²
    
    def _generate_alert_description(self, species: str, alert_type: str, 
                                  trend_info: Dict, severity: str) -> str:
        """Generate human-readable alert description"""
        descriptions = {
            "population_decline": f"{species} showing {severity} population decline "
                                f"(trend: {trend_info['trend_slope']:.3f}, "
                                f"confidence: {trend_info['confidence']:.2f})",
            "habitat_loss": f"{species} experiencing habitat range reduction",
            "low_detection": f"{species} has low observation frequency, may indicate "
                           f"population issues or insufficient monitoring"
        }
        return descriptions.get(alert_type, f"{species} conservation concern detected")
    
    def _calculate_ecosystem_health_score(self, data: pd.DataFrame, 
                                        hotspots: List[BiodiversityHotspot], 
                                        alerts: List[ConservationAlert]) -> float:
        """Calculate overall ecosystem health score (0-1)"""
        if data.empty:
            return 0.0
        
        # Base score from species diversity
        species_diversity_score = min(data['species'].nunique() / 100.0, 1.0)
        
        # Hotspot health contribution
        hotspot_score = min(len(hotspots) / 10.0, 1.0) if hotspots else 0.0
        
        # Alert penalty
        critical_alerts = len([a for a in alerts if a.severity == 'critical'])
        high_alerts = len([a for a in alerts if a.severity == 'high'])
        alert_penalty = min((critical_alerts * 0.2 + high_alerts * 0.1), 0.5)
        
        # Data quality bonus - safely convert to numeric
        try:
            if 'quality_score' in data.columns:
                quality_scores = pd.to_numeric(data['quality_score'], errors='coerce').dropna()
                quality_bonus = float(quality_scores.mean()) * 0.2 if len(quality_scores) > 0 else 0.0
            else:
                quality_bonus = 0.0
        except Exception:
            quality_bonus = 0.0
        
        health_score = max(0, species_diversity_score * 0.4 + hotspot_score * 0.3 + 
                          quality_bonus - alert_penalty + 0.3)
        
        return min(health_score, 1.0)
    
    def _generate_ecosystem_recommendations(self, hotspots: List[BiodiversityHotspot], 
                                         alerts: List[ConservationAlert]) -> List[str]:
        """Generate ecosystem management recommendations"""
        recommendations = []
        
        # Hotspot-based recommendations
        if hotspots:
            high_priority_hotspots = [h for h in hotspots if h.conservation_priority > 0.7]
            if high_priority_hotspots:
                recommendations.append(
                    f"Prioritize conservation efforts in {str(len(high_priority_hotspots))} "
                    f"high-priority biodiversity hotspots"
                )
            
            recommendations.append("Establish wildlife corridors between identified hotspots")
        
        # Alert-based recommendations
        critical_species = [str(a.species) for a in alerts if a.severity == 'critical']
        if critical_species:
            recommendations.append(
                f"Immediate intervention required for critically declining species: "
                f"{', '.join(critical_species[:3])}{'...' if len(critical_species) > 3 else ''}"
            )
        
        # General recommendations
        recommendations.extend([
            "Enhance citizen science monitoring programs",
            "Implement real-time biodiversity monitoring systems",
            "Develop climate change adaptation strategies",
            "Strengthen habitat connectivity and restoration programs"
        ])
        
        return recommendations

def run_advanced_analytics_demo():
    """Run a demonstration of advanced analytics capabilities"""
    print("🧠 Advanced Wildlife Analytics Demo")
    print("=" * 50)
    
    analytics = AdvancedWildlifeAnalytics()
    
    # Load data
    print("\n📊 Loading comprehensive wildlife data...")
    data = analytics.load_comprehensive_data()
    
    if data.empty:
        print("❌ No data available for analysis")
        return
    
    print(f"✅ Loaded {len(data)} records for {data['species'].nunique()} species")
    
    # Analyze trends
    print("\n📈 Analyzing population trends...")
    trends = analytics.analyze_population_trends(data)
    
    if trends:
        print(f"✅ Analyzed trends for {len(trends)} species")
        
        # Show some interesting trends
        declining_species = [s for s, t in trends.items() if t['trend_status'] == 'declining']
        increasing_species = [s for s, t in trends.items() if t['trend_status'] == 'increasing']
        
        if declining_species:
            print(f"⚠️  {len(declining_species)} species showing declining trends")
        if increasing_species:
            print(f"📈 {len(increasing_species)} species showing increasing trends")
    
    # Detect hotspots
    print("\n🌍 Detecting biodiversity hotspots...")
    hotspots = analytics.detect_biodiversity_hotspots(data)
    
    if hotspots:
        print(f"✅ Detected {len(hotspots)} biodiversity hotspots")
        top_hotspot = hotspots[0]
        print(f"🏆 Top hotspot: {top_hotspot.species_count} species at "
              f"({top_hotspot.center_lat:.2f}, {top_hotspot.center_lon:.2f})")
    
    # Conservation assessment
    print("\n🚨 Assessing conservation risks...")
    alerts = analytics.assess_conservation_risk(trends, data)
    
    if alerts:
        print(f"✅ Generated {len(alerts)} conservation alerts")
        critical_alerts = [a for a in alerts if a.severity == 'critical']
        if critical_alerts:
            print(f"🚨 {len(critical_alerts)} critical alerts requiring immediate attention")
    
    # Generate ecosystem report
    print("\n📋 Generating ecosystem health report...")
    report = analytics.generate_ecosystem_health_report(data, hotspots, alerts)
    
    if report:
        health_score = report['ecosystem_health_score']
        print(f"✅ Ecosystem Health Score: {health_score:.2f}/1.00")
        
        if health_score > 0.8:
            print("🌟 Excellent ecosystem health!")
        elif health_score > 0.6:
            print("✅ Good ecosystem health")
        elif health_score > 0.4:
            print("⚠️  Moderate ecosystem health - attention needed")
        else:
            print("🚨 Poor ecosystem health - urgent action required")
    
    print("\n🎯 Advanced Analytics Demo Complete!")
    return {
        'trends': trends,
        'hotspots': hotspots,
        'alerts': alerts,
        'report': report
    }

if __name__ == "__main__":
    if not SKLEARN_AVAILABLE:
        print("Installing required dependencies...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'scikit-learn'])
    
    run_advanced_analytics_demo()
