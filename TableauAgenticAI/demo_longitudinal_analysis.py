#!/usr/bin/env python3
"""
Demo script for Longitudinal AI Bubble Analysis
This script demonstrates the time-series data collection and Grafana export functionality
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.time_series_collector import TimeSeriesCollector
from src.news_tracker import NewsTracker
from src.search import search_ai_news


def demo_longitudinal_analysis():
    """Demonstrate the longitudinal analysis functionality"""
    print("🚀 AI Bubble Analysis - Longitudinal Analysis Demo")
    print("=" * 60)
    
    # Check if API keys are set
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        print("❌ Please set OPENAI_API_KEY and TAVILY_API_KEY environment variables")
        print("   You can create a .env file with:")
        print("   OPENAI_API_KEY=your_key_here")
        print("   TAVILY_API_KEY=your_key_here")
        return
    
    try:
        # Step 1: Initialize time series collector
        print("\n📊 Step 1: Initializing time series collector...")
        collector = TimeSeriesCollector()
        print("✅ Time series collector initialized")
        
        # Step 2: Search for AI news
        print("\n🔍 Step 2: Searching for AI news...")
        search_queries = [
            "AI bubble 2024",
            "AI market speculation", 
            "AI investment frenzy",
            "AI startup valuations",
            "AI industry hype"
        ]
        
        search_state = {"queries": search_queries}
        search_results = search_ai_news(search_state)
        print(f"   Found {len(search_results['results'])} articles")
        
        # Step 3: Track news articles
        print("\n📊 Step 3: Tracking news articles...")
        tracking_result = collector.tracker.add_news_articles(search_results["results"])
        print(f"   Added {tracking_result['added_articles']} new articles")
        
        # Step 4: Collect daily snapshot
        print("\n📅 Step 4: Collecting daily snapshot...")
        snapshot = collector.collect_daily_snapshot(force_reanalyze=True)
        print(f"   ✅ Daily snapshot collected for {snapshot.date}")
        print(f"   📊 Market Assessment: {snapshot.market_assessment}")
        print(f"   ⚠️  Bubble Risk: {snapshot.average_bubble_risk:.3f}")
        print(f"   😊 Sentiment: {snapshot.average_sentiment:.3f}")
        print(f"   🚨 Concerning Articles: {snapshot.concerning_articles}")
        
        # Step 5: Calculate trends
        print("\n📈 Step 5: Calculating trends...")
        trends = collector.calculate_trends(days=30)
        
        if 'error' in trends:
            print(f"   ⚠️  {trends['error']}")
        else:
            print(f"   📊 Trend Analysis ({trends['date_range']['start']} to {trends['date_range']['end']}):")
            print(f"   📈 Bubble Risk Trend: {trends['trends']['bubble_risk']['direction']} ({trends['trends']['bubble_risk']['change_percent']:.1f}%)")
            print(f"   😊 Sentiment Trend: {trends['trends']['sentiment']['direction']} ({trends['trends']['sentiment']['change_percent']:.1f}%)")
            print(f"   🚨 Concerning Articles Trend: {trends['trends']['concerning_articles']['direction']} ({trends['trends']['concerning_articles']['change_percent']:.1f}%)")
            
            # Show indicator trends
            print(f"\n   📊 Indicator Trends:")
            for indicator, trend_data in trends['indicator_trends'].items():
                direction_icon = "📈" if trend_data['direction'] == "increasing" else "📉" if trend_data['direction'] == "decreasing" else "➡️"
                print(f"      {direction_icon} {indicator.replace('_', ' ').title()}: {trend_data['change_percent']:.1f}% change")
            
            # Show risk level change
            risk_change = trends['risk_level_change']
            if risk_change['change'] != 'insufficient_data':
                change_icon = "🔴" if risk_change['change'] == "increased" else "🟢" if risk_change['change'] == "decreased" else "🟡"
                print(f"   {change_icon} Risk Level: {risk_change['start_level']} → {risk_change['end_level']} ({risk_change['change']})")
        
        # Step 6: Export for Grafana
        print("\n📊 Step 6: Exporting data for Grafana...")
        export_result = collector.export_for_grafana(days=30)
        
        if 'error' in export_result:
            print(f"   ❌ Export failed: {export_result['error']}")
        else:
            print(f"   ✅ Grafana export completed!")
            print(f"   📁 Time Series CSV: {export_result['time_series_csv']}")
            print(f"   📁 Dashboard Config: {export_result['dashboard_config']}")
            print(f"   📁 Setup Instructions: {export_result['setup_instructions']}")
            print(f"   📊 Data Points: {export_result['data_points']}")
            print(f"   📅 Date Range: {export_result['date_range']}")
        
        # Step 7: Show collection status
        print("\n📊 Step 7: Collection status...")
        status = collector.get_status()
        print(f"   📅 Total Snapshots: {status['total_snapshots']}")
        print(f"   📅 Latest Snapshot: {status['latest_snapshot']}")
        print(f"   📁 Data Directory: {status['data_directory']}")
        
        # Step 8: Show recent snapshots
        print("\n📅 Step 8: Recent snapshots...")
        recent_snapshots = collector.get_latest_snapshots(7)
        
        if recent_snapshots:
            print(f"   📅 Recent Snapshots (Last 7 days):")
            for snapshot in recent_snapshots:
                risk_color = "🔴" if snapshot.average_bubble_risk > 0.7 else "🟡" if snapshot.average_bubble_risk > 0.4 else "🟢"
                print(f"      📅 {snapshot.date}: {risk_color} {snapshot.market_assessment} (Risk: {snapshot.average_bubble_risk:.3f})")
        else:
            print("   ⚠️  No recent snapshots available")
        
        print("\n✅ Longitudinal analysis demo completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Set up Grafana using the exported configuration")
        print("2. Run daily collection: python daily_collection.py")
        print("3. Monitor trends: python -m src.time_series_cli trends")
        print("4. View historical data: python -m src.time_series_cli history")
        print("5. Set up automated daily collection with cron job")
        
        print("\n🔧 Daily Collection Commands:")
        print("   python daily_collection.py                    # Collect today's data")
        print("   python -m src.time_series_cli collect-daily   # Alternative collection")
        print("   python -m src.time_series_cli trends --days 30 # View trends")
        print("   python -m src.time_series_cli export-grafana  # Export for Grafana")
        
    except Exception as e:
        print(f"❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_longitudinal_analysis()
