#!/usr/bin/env python3
"""
Python-based Dashboard for AI Bubble Analysis
Creates visualizations using matplotlib and displays them
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
from datetime import datetime

def create_dashboard():
    """Create a comprehensive dashboard using matplotlib"""
    
    # Read the data
    csv_file = Path("time_series_data/grafana_time_series_30d.csv")
    if not csv_file.exists():
        print("❌ No data file found. Run the demo first: python demo_longitudinal_analysis.py")
        return
    
    df = pd.read_csv(csv_file)
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('🚀 AI Bubble Analysis Dashboard', fontsize=20, fontweight='bold')
    
    # Get the latest data
    latest_data = df[df['metric_type'] == 'summary'].iloc[-1] if len(df) > 0 else None
    
    if latest_data is None:
        print("❌ No summary data found")
        return
    
    # 1. Bubble Risk Gauge (Top Left)
    ax1 = plt.subplot(2, 3, 1)
    risk_score = latest_data['average_bubble_risk']
    
    # Create a gauge chart
    colors = ['#4ade80', '#fbbf24', '#f87171']  # Green, Yellow, Red
    if risk_score > 0.7:
        color = colors[2]
        risk_level = "HIGH RISK"
    elif risk_score > 0.4:
        color = colors[1]
        risk_level = "MODERATE RISK"
    else:
        color = colors[0]
        risk_level = "LOW RISK"
    
    # Simple bar chart as gauge
    bars = ax1.bar(['Bubble Risk'], [risk_score], color=color, alpha=0.7)
    ax1.set_ylim(0, 1)
    ax1.set_ylabel('Risk Score (0-1)')
    ax1.set_title(f'🎯 Bubble Risk: {risk_score:.3f}\n{risk_level}', fontweight='bold')
    ax1.axhline(y=0.4, color='orange', linestyle='--', alpha=0.7, label='Moderate Threshold')
    ax1.axhline(y=0.7, color='red', linestyle='--', alpha=0.7, label='High Risk Threshold')
    ax1.legend()
    
    # 2. Sentiment Analysis (Top Middle)
    ax2 = plt.subplot(2, 3, 2)
    sentiment = latest_data['average_sentiment']
    
    if sentiment > 0.3:
        sent_color = '#60a5fa'
        sent_level = "POSITIVE"
    elif sentiment < -0.3:
        sent_color = '#f87171'
        sent_level = "NEGATIVE"
    else:
        sent_color = '#a78bfa'
        sent_level = "NEUTRAL"
    
    bars = ax2.bar(['Sentiment'], [sentiment], color=sent_color, alpha=0.7)
    ax2.set_ylim(-1, 1)
    ax2.set_ylabel('Sentiment Score (-1 to +1)')
    ax2.set_title(f'😊 Sentiment: {sentiment:.3f}\n{sent_level}', fontweight='bold')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax2.axhline(y=0.3, color='blue', linestyle='--', alpha=0.7)
    ax2.axhline(y=-0.3, color='red', linestyle='--', alpha=0.7)
    
    # 3. Key Metrics (Top Right)
    ax3 = plt.subplot(2, 3, 3)
    ax3.axis('off')
    
    metrics_text = f"""
    📊 KEY METRICS
    
    📰 Total Articles: {int(latest_data['total_articles'])}
    🔍 Analyzed: {int(latest_data['analyzed_articles'])}
    🚨 Concerning: {int(latest_data['concerning_articles'])}
    
    📅 Last Updated:
    {latest_data['date']}
    
    🎯 Market Assessment:
    {latest_data['market_assessment']}
    """
    
    ax3.text(0.1, 0.9, metrics_text, transform=ax3.transAxes, fontsize=12,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # 4. Bubble Indicators (Bottom Left)
    ax4 = plt.subplot(2, 3, 4)
    indicator_data = df[df['metric_type'] == 'indicator']
    
    indicators = indicator_data['indicator_name'].str.replace('_', ' ').str.title()
    values = indicator_data['indicator_value']
    
    # Color bars based on values
    colors = ['#f87171' if v > 0.6 else '#fbbf24' if v > 0.3 else '#4ade80' for v in values]
    
    bars = ax4.bar(indicators, values, color=colors, alpha=0.7)
    ax4.set_ylabel('Indicator Value (0-1)')
    ax4.set_title('📊 Bubble Indicators', fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    ax4.set_ylim(0, 1)
    
    # Add threshold lines
    ax4.axhline(y=0.3, color='orange', linestyle='--', alpha=0.7, label='Moderate')
    ax4.axhline(y=0.6, color='red', linestyle='--', alpha=0.7, label='High Risk')
    ax4.legend()
    
    # 5. Risk vs Sentiment Scatter (Bottom Middle)
    ax5 = plt.subplot(2, 3, 5)
    summary_data = df[df['metric_type'] == 'summary']
    
    if len(summary_data) > 0:
        ax5.scatter(summary_data['average_sentiment'], summary_data['average_bubble_risk'], 
                   s=100, alpha=0.7, c='purple')
        ax5.set_xlabel('Sentiment Score')
        ax5.set_ylabel('Bubble Risk')
        ax5.set_title('📈 Risk vs Sentiment', fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # Add quadrant lines
        ax5.axhline(y=0.4, color='orange', linestyle='--', alpha=0.7)
        ax5.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    
    # 6. Trend Analysis (Bottom Right)
    ax6 = plt.subplot(2, 3, 6)
    
    # Create a simple trend visualization
    dates = pd.to_datetime(df['date'].unique())
    if len(dates) > 1:
        # If we have multiple dates, show trend
        risk_trend = df[df['metric_type'] == 'summary']['average_bubble_risk'].values
        ax6.plot(dates, risk_trend, marker='o', linewidth=2, markersize=8, color='red')
        ax6.set_title('📈 Risk Trend Over Time', fontweight='bold')
        ax6.set_ylabel('Bubble Risk')
        ax6.tick_params(axis='x', rotation=45)
        ax6.grid(True, alpha=0.3)
    else:
        # Single data point - show current status
        ax6.text(0.5, 0.5, f'Current Status:\n{latest_data["market_assessment"]}', 
                ha='center', va='center', transform=ax6.transAxes, fontsize=14,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        ax6.set_title('📊 Current Status', fontweight='bold')
        ax6.axis('off')
    
    # Adjust layout and save
    plt.tight_layout()
    
    # Save the dashboard
    dashboard_file = 'ai_bubble_dashboard.png'
    plt.savefig(dashboard_file, dpi=300, bbox_inches='tight')
    print(f"✅ Dashboard saved as: {dashboard_file}")
    
    # Show the dashboard
    plt.show()
    
    return dashboard_file

def create_simple_summary():
    """Create a simple text summary"""
    csv_file = Path("time_series_data/grafana_time_series_30d.csv")
    if not csv_file.exists():
        print("❌ No data file found")
        return
    
    df = pd.read_csv(csv_file)
    latest_data = df[df['metric_type'] == 'summary'].iloc[-1]
    
    print("\n" + "="*60)
    print("🚀 AI BUBBLE ANALYSIS SUMMARY")
    print("="*60)
    print(f"📅 Date: {latest_data['date']}")
    print(f"⏰ Time: {latest_data['timestamp'].split('T')[1][:8]}")
    print()
    print(f"🎯 Market Assessment: {latest_data['market_assessment']}")
    print(f"⚠️  Bubble Risk Score: {latest_data['average_bubble_risk']:.3f}")
    print(f"😊 Sentiment Score: {latest_data['average_sentiment']:.3f}")
    print(f"📰 Articles Analyzed: {int(latest_data['analyzed_articles'])}/{int(latest_data['total_articles'])}")
    print(f"🚨 Concerning Articles: {int(latest_data['concerning_articles'])}")
    print()
    
    print("📊 INDICATOR BREAKDOWN:")
    print("-" * 30)
    indicator_data = df[df['metric_type'] == 'indicator']
    for _, row in indicator_data.iterrows():
        indicator_name = row['indicator_name'].replace('_', ' ').title()
        value = row['indicator_value']
        status = "🔴 HIGH" if value > 0.6 else "🟡 MODERATE" if value > 0.3 else "🟢 LOW"
        print(f"{indicator_name:20} {value:.3f} {status}")
    
    print("\n" + "="*60)

def main():
    """Main function"""
    print("🚀 Creating AI Bubble Analysis Dashboard...")
    
    # Create text summary
    create_simple_summary()
    
    # Create visual dashboard
    try:
        dashboard_file = create_dashboard()
        print(f"\n📊 Visual dashboard created: {dashboard_file}")
        print("🖼️  The dashboard should open in a new window")
    except Exception as e:
        print(f"❌ Error creating visual dashboard: {e}")
        print("📝 Text summary is still available above")

if __name__ == "__main__":
    main()
