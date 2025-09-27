#!/usr/bin/env python3
"""
Australian Biodiversity Platform - Enterprise Architecture Visualization
=======================================================================
This script generates a comprehensive architecture diagram showing the 
enterprise data lifecycle management system with all contemporary components.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_architecture_diagram():
    """Create a comprehensive architecture diagram"""
    
    # Create figure with larger size for detailed architecture
    fig, ax = plt.subplots(1, 1, figsize=(20, 14))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Define colors for different layers/components
    colors = {
        'data_sources': '#E3F2FD',      # Light blue
        'ingestion': '#BBDEFB',         # Medium blue
        'storage': '#90CAF9',           # Darker blue
        'processing': '#64B5F6',        # Processing blue
        'governance': '#42A5F5',        # Governance blue
        'delivery': '#2196F3',          # Delivery blue
        'monitoring': '#1E88E5',        # Monitoring blue
        'interface': '#1976D2'          # Interface blue
    }
    
    # Title
    ax.text(10, 13.5, 'Australian Biodiversity Platform - Enterprise Architecture', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 13, 'Contemporary Data Lifecycle Management with Enterprise Governance', 
            fontsize=14, ha='center', style='italic')
    
    # Layer 1: External Data Sources
    ax.text(1, 12, 'EXTERNAL DATA SOURCES', fontsize=12, fontweight='bold')
    
    # iNaturalist API
    inaturalist_box = FancyBboxPatch((0.5, 11), 3, 0.8, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=colors['data_sources'],
                                   edgecolor='black', linewidth=1)
    ax.add_patch(inaturalist_box)
    ax.text(2, 11.4, 'iNaturalist API\n🐨 Live Wildlife Data', ha='center', va='center', fontsize=10)
    
    # GBIF API
    gbif_box = FancyBboxPatch((4, 11), 3, 0.8,
                            boxstyle="round,pad=0.1",
                            facecolor=colors['data_sources'],
                            edgecolor='black', linewidth=1)
    ax.add_patch(gbif_box)
    ax.text(5.5, 11.4, 'GBIF API\n🦘 Biodiversity Records', ha='center', va='center', fontsize=10)
    
    # eBird API (Future)
    ebird_box = FancyBboxPatch((7.5, 11), 3, 0.8,
                             boxstyle="round,pad=0.1",
                             facecolor='#F5F5F5',
                             edgecolor='gray', linewidth=1, linestyle='--')
    ax.add_patch(ebird_box)
    ax.text(9, 11.4, 'eBird API\n🦅 Bird Observations\n(Future Extension)', ha='center', va='center', fontsize=9)
    
    # Layer 2: Data Ingestion & Quality Gateway
    ax.text(1, 10, 'DATA INGESTION & QUALITY GATEWAY', fontsize=12, fontweight='bold')
    
    # Enterprise Data Lifecycle Manager
    ingestion_box = FancyBboxPatch((0.5, 8.8), 10, 1,
                                 boxstyle="round,pad=0.1",
                                 facecolor=colors['ingestion'],
                                 edgecolor='black', linewidth=2)
    ax.add_patch(ingestion_box)
    ax.text(5.5, 9.3, 'Enterprise Data Lifecycle Manager', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    ax.text(5.5, 9, '• Schema Validation  • Quality Rules  • Standards Enforcement  • Duplicate Detection', 
            ha='center', va='center', fontsize=10)
    
    # Real-time Quality Monitor (side component)
    quality_monitor_box = FancyBboxPatch((11.5, 8.8), 3.5, 1,
                                       boxstyle="round,pad=0.1",
                                       facecolor=colors['monitoring'],
                                       edgecolor='black', linewidth=1)
    ax.add_patch(quality_monitor_box)
    ax.text(13.25, 9.3, 'Real-time Quality\nMonitoring', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Data Governance (side component)
    governance_box = FancyBboxPatch((15.5, 8.8), 4, 1,
                                  boxstyle="round,pad=0.1",
                                  facecolor=colors['governance'],
                                  edgecolor='black', linewidth=1)
    ax.add_patch(governance_box)
    ax.text(17.5, 9.3, 'Data Governance\n& Compliance', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Layer 3: Modern Data Lake Architecture
    ax.text(1, 7.8, 'MODERN DATA LAKE ARCHITECTURE', fontsize=12, fontweight='bold')
    
    # Bronze Layer (Raw Data)
    bronze_box = FancyBboxPatch((1, 6.5), 5, 1,
                              boxstyle="round,pad=0.1",
                              facecolor='#D7CCC8',  # Bronze color
                              edgecolor='#8D6E63', linewidth=2)
    ax.add_patch(bronze_box)
    ax.text(3.5, 7, 'BRONZE LAYER\nRaw Ingested Data', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    ax.text(3.5, 6.7, '• Unprocessed wildlife observations\n• Original API responses\n• Audit trail maintained', 
            ha='center', va='center', fontsize=9)
    
    # Silver Layer (Cleaned Data)
    silver_box = FancyBboxPatch((7, 6.5), 5, 1,
                              boxstyle="round,pad=0.1",
                              facecolor='#E8EAF6',  # Silver color
                              edgecolor='#7986CB', linewidth=2)
    ax.add_patch(silver_box)
    ax.text(9.5, 7, 'SILVER LAYER\nCleaned & Standardized', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    ax.text(9.5, 6.7, '• Validated species data\n• Standardized locations\n• Quality flags added', 
            ha='center', va='center', fontsize=9)
    
    # Gold Layer (Analytics Ready)
    gold_box = FancyBboxPatch((13, 6.5), 5, 1,
                            boxstyle="round,pad=0.1",
                            facecolor='#FFF9C4',  # Gold color
                            edgecolor='#FBC02D', linewidth=2)
    ax.add_patch(gold_box)
    ax.text(15.5, 7, 'GOLD LAYER\nAnalytics Ready', ha='center', va='center', 
            fontsize=11, fontweight='bold')
    ax.text(15.5, 6.7, '• Aggregated insights\n• Species trends\n• Location analytics', 
            ha='center', va='center', fontsize=9)
    
    # Layer 4: ETL Pipeline
    ax.text(1, 5.8, 'MODERN ETL PIPELINE', fontsize=12, fontweight='bold')
    
    # ETL Processing Engine
    etl_box = FancyBboxPatch((2, 4.5), 14, 1,
                           boxstyle="round,pad=0.1",
                           facecolor=colors['processing'],
                           edgecolor='black', linewidth=2)
    ax.add_patch(etl_box)
    ax.text(9, 5, 'Modern ETL Processing Engine', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    ax.text(9, 4.7, 'Bronze→Silver→Gold Transformations  •  Incremental Processing  •  Quality Gates  •  Data Lineage Tracking', 
            ha='center', va='center', fontsize=10, color='white')
    
    # Layer 5: Data Management Services
    ax.text(1, 4, 'DATA MANAGEMENT SERVICES', fontsize=12, fontweight='bold')
    
    # Data Catalog
    catalog_box = FancyBboxPatch((1, 2.8), 4, 0.8,
                               boxstyle="round,pad=0.1",
                               facecolor=colors['governance'],
                               edgecolor='black', linewidth=1)
    ax.add_patch(catalog_box)
    ax.text(3, 3.2, 'Data Catalog\n& Metadata', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Lineage Tracker
    lineage_box = FancyBboxPatch((5.5, 2.8), 4, 0.8,
                               boxstyle="round,pad=0.1",
                               facecolor=colors['governance'],
                               edgecolor='black', linewidth=1)
    ax.add_patch(lineage_box)
    ax.text(7.5, 3.2, 'Data Lineage\nTracking', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Compliance Manager
    compliance_box = FancyBboxPatch((10, 2.8), 4, 0.8,
                                  boxstyle="round,pad=0.1",
                                  facecolor=colors['governance'],
                                  edgecolor='black', linewidth=1)
    ax.add_patch(compliance_box)
    ax.text(12, 3.2, 'Compliance\nManagement', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Quality Monitoring
    quality_service_box = FancyBboxPatch((14.5, 2.8), 4, 0.8,
                                       boxstyle="round,pad=0.1",
                                       facecolor=colors['monitoring'],
                                       edgecolor='black', linewidth=1)
    ax.add_patch(quality_service_box)
    ax.text(16.5, 3.2, 'Quality Monitoring\n& Alerting', ha='center', va='center', 
            fontsize=10, fontweight='bold', color='white')
    
    # Layer 6: Data Delivery & Interface
    ax.text(1, 2.2, 'DATA DELIVERY & USER INTERFACES', fontsize=12, fontweight='bold')
    
    # Web Dashboard
    dashboard_box = FancyBboxPatch((1, 0.8), 5, 1,
                                 boxstyle="round,pad=0.1",
                                 facecolor=colors['interface'],
                                 edgecolor='black', linewidth=2)
    ax.add_patch(dashboard_box)
    ax.text(3.5, 1.3, 'Flask Web Dashboard\n🌐 Interactive Visualization', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='white')
    
    # Data Explorer
    explorer_box = FancyBboxPatch((7, 0.8), 5, 1,
                                boxstyle="round,pad=0.1",
                                facecolor=colors['interface'],
                                edgecolor='black', linewidth=2)
    ax.add_patch(explorer_box)
    ax.text(9.5, 1.3, 'Data Explorer\n📊 Analytics & Reports', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='white')
    
    # Quality-Assured Delivery
    delivery_box = FancyBboxPatch((13, 0.8), 5, 1,
                                boxstyle="round,pad=0.1",
                                facecolor=colors['delivery'],
                                edgecolor='black', linewidth=2)
    ax.add_patch(delivery_box)
    ax.text(15.5, 1.3, 'Quality-Assured\nData Delivery', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='white')
    
    # Add arrows showing data flow
    # Data Sources to Ingestion
    ax.arrow(2, 11, 1.5, -1.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    ax.arrow(5.5, 11, 1, -1.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Ingestion to Bronze
    ax.arrow(5.5, 8.8, -2, -1.8, head_width=0.1, head_length=0.1, fc='#8D6E63', ec='#8D6E63', lw=2)
    
    # Bronze to Silver
    ax.arrow(6, 7, 1, 0, head_width=0.1, head_length=0.1, fc='#7986CB', ec='#7986CB', lw=2)
    
    # Silver to Gold
    ax.arrow(12, 7, 1, 0, head_width=0.1, head_length=0.1, fc='#FBC02D', ec='#FBC02D', lw=2)
    
    # ETL Pipeline connections
    ax.arrow(9, 6.5, 0, -1, head_width=0.1, head_length=0.1, fc='blue', ec='blue', lw=2)
    
    # Services to Delivery
    ax.arrow(9, 2.8, 0, -1.5, head_width=0.1, head_length=0.1, fc='navy', ec='navy', lw=2)
    
    # Add legend for architectural patterns
    legend_y = 0.3
    ax.text(1, legend_y, 'ARCHITECTURAL PATTERNS:', fontsize=10, fontweight='bold')
    ax.text(1, legend_y-0.2, '• Event-driven processing  • Real-time monitoring  • Data lake architecture', fontsize=9)
    ax.text(1, legend_y-0.35, '• Schema evolution  • Incremental processing  • Quality gates  • Compliance by design', fontsize=9)
    
    # Add technology stack
    ax.text(10, legend_y, 'TECHNOLOGY STACK:', fontsize=10, fontweight='bold')
    ax.text(10, legend_y-0.2, '• Python + Pandas + SQLite  • Flask Web Framework  • Matplotlib Visualization', fontsize=9)
    ax.text(10, legend_y-0.35, '• Contemporary data engineering patterns  • Enterprise governance framework', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('biodiversity_platform_architecture.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_data_flow_diagram():
    """Create a detailed data flow diagram"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'Enterprise Data Flow Architecture', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Define the data flow stages
    stages = [
        {'name': 'API Collection', 'pos': (2, 10), 'color': '#E3F2FD'},
        {'name': 'Quality Validation', 'pos': (2, 8.5), 'color': '#BBDEFB'},
        {'name': 'Bronze Storage', 'pos': (2, 7), 'color': '#D7CCC8'},
        {'name': 'ETL Processing', 'pos': (8, 7), 'color': '#90CAF9'},
        {'name': 'Silver Storage', 'pos': (8, 5.5), 'color': '#E8EAF6'},
        {'name': 'Gold Analytics', 'pos': (8, 4), 'color': '#FFF9C4'},
        {'name': 'Quality Delivery', 'pos': (14, 7), 'color': '#2196F3'}
    ]
    
    # Draw stages
    for stage in stages:
        box = FancyBboxPatch((stage['pos'][0]-1, stage['pos'][1]-0.4), 2, 0.8,
                           boxstyle="round,pad=0.1",
                           facecolor=stage['color'],
                           edgecolor='black', linewidth=1)
        ax.add_patch(box)
        ax.text(stage['pos'][0], stage['pos'][1], stage['name'], 
                ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Add governance components on the side
    governance_components = [
        {'name': 'Data Catalog', 'pos': (14, 10)},
        {'name': 'Lineage Tracking', 'pos': (14, 8.5)},
        {'name': 'Compliance Checks', 'pos': (14, 5.5)},
        {'name': 'Quality Monitoring', 'pos': (14, 4)}
    ]
    
    for comp in governance_components:
        box = FancyBboxPatch((comp['pos'][0]-1, comp['pos'][1]-0.3), 2, 0.6,
                           boxstyle="round,pad=0.05",
                           facecolor='#42A5F5',
                           edgecolor='black', linewidth=1)
        ax.add_patch(box)
        ax.text(comp['pos'][0], comp['pos'][1], comp['name'], 
                ha='center', va='center', fontsize=9, color='white')
    
    # Add arrows for data flow
    flow_arrows = [
        ((2, 9.6), (2, 8.9)),  # Collection to Validation
        ((2, 8.1), (2, 7.4)),  # Validation to Bronze
        ((3, 7), (7, 7)),      # Bronze to ETL
        ((8, 6.6), (8, 5.9)),  # ETL to Silver
        ((8, 5.1), (8, 4.4)),  # Silver to Gold
        ((9, 7), (13, 7))      # Processing to Delivery
    ]
    
    for start, end in flow_arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    
    # Add governance arrows (dotted)
    governance_arrows = [
        ((13, 10), (3, 8.5)),    # Catalog to Validation
        ((13, 8.5), (9, 7)),     # Lineage to ETL
        ((13, 5.5), (9, 4)),     # Compliance to Gold
        ((13, 4), (9, 5.5))      # Quality to Silver
    ]
    
    for start, end in governance_arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=1, color='green', linestyle='--'))
    
    # Add data quality metrics
    metrics_box = FancyBboxPatch((4, 2), 8, 1.5,
                               boxstyle="round,pad=0.1",
                               facecolor='#F5F5F5',
                               edgecolor='black', linewidth=1)
    ax.add_patch(metrics_box)
    ax.text(8, 3, 'CONTINUOUS QUALITY METRICS', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    ax.text(8, 2.5, 'Completeness • Accuracy • Consistency • Timeliness • Validity', 
            ha='center', va='center', fontsize=10)
    ax.text(8, 2.2, 'Real-time Monitoring • Automated Alerts • Threshold Management', 
            ha='center', va='center', fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.savefig('data_flow_architecture.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Generate both architecture diagrams"""
    print("Generating Enterprise Architecture Diagrams...")
    print("=" * 50)
    
    print("1. Creating comprehensive architecture diagram...")
    create_architecture_diagram()
    
    print("2. Creating data flow diagram...")
    create_data_flow_diagram()
    
    print("\nArchitecture diagrams generated:")
    print("  • biodiversity_platform_architecture.png")
    print("  • data_flow_architecture.png")

if __name__ == "__main__":
    main()
