#!/usr/bin/env python3
"""
Daily AI Bubble Analysis Data Collection Script
This script should be run daily to collect time-series data for longitudinal analysis
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.time_series_collector import TimeSeriesCollector
from src.news_tracker import NewsTracker
from src.search import search_ai_news


def setup_logging():
    """Setup logging for the daily collection"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"daily_collection_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['OPENAI_API_KEY', 'TAVILY_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True


def collect_daily_data():
    """Main function to collect daily data"""
    logger = setup_logging()
    
    try:
        logger.info("🚀 Starting daily AI bubble analysis data collection")
        
        # Check environment
        logger.info("🔍 Checking environment variables...")
        check_environment()
        logger.info("✅ Environment variables are set")
        
        # Initialize collector
        logger.info("📊 Initializing time series collector...")
        collector = TimeSeriesCollector()
        
        # Check if we already have data for today
        today = datetime.now().strftime('%Y-%m-%d')
        existing_snapshot = collector.get_snapshot_by_date(today)
        
        if existing_snapshot:
            logger.info(f"⚠️  Snapshot for {today} already exists. Updating...")
            collector.remove_snapshot_by_date(today)
        
        # Collect daily snapshot
        logger.info("📊 Collecting daily snapshot...")
        snapshot = collector.collect_daily_snapshot(force_reanalyze=True)
        
        logger.info(f"✅ Daily snapshot collected successfully")
        logger.info(f"   📅 Date: {snapshot.date}")
        logger.info(f"   📊 Market Assessment: {snapshot.market_assessment}")
        logger.info(f"   ⚠️  Bubble Risk: {snapshot.average_bubble_risk:.3f}")
        logger.info(f"   😊 Sentiment: {snapshot.average_sentiment:.3f}")
        logger.info(f"   🚨 Concerning Articles: {snapshot.concerning_articles}")
        
        # Export for Grafana
        logger.info("📊 Exporting data for Grafana...")
        export_result = collector.export_for_grafana(days=30)
        
        if 'error' in export_result:
            logger.error(f"❌ Export failed: {export_result['error']}")
        else:
            logger.info(f"✅ Grafana export completed")
            logger.info(f"   📁 Time Series CSV: {export_result['time_series_csv']}")
            logger.info(f"   📁 Dashboard Config: {export_result['dashboard_config']}")
            logger.info(f"   📊 Data Points: {export_result['data_points']}")
        
        # Calculate trends
        logger.info("📈 Calculating trends...")
        trends = collector.calculate_trends(days=30)
        
        if 'error' not in trends:
            logger.info(f"📊 Trend Analysis Summary:")
            logger.info(f"   📈 Bubble Risk Trend: {trends['trends']['bubble_risk']['direction']} ({trends['trends']['bubble_risk']['change_percent']:.1f}%)")
            logger.info(f"   😊 Sentiment Trend: {trends['trends']['sentiment']['direction']} ({trends['trends']['sentiment']['change_percent']:.1f}%)")
            logger.info(f"   🚨 Concerning Articles Trend: {trends['trends']['concerning_articles']['direction']} ({trends['trends']['concerning_articles']['change_percent']:.1f}%)")
            
            # Log risk level changes
            risk_change = trends['risk_level_change']
            if risk_change['change'] != 'insufficient_data':
                logger.info(f"   🔴 Risk Level Change: {risk_change['start_level']} → {risk_change['end_level']} ({risk_change['change']})")
        
        # Show status
        status = collector.get_status()
        logger.info(f"📊 Collection Status:")
        logger.info(f"   📅 Total Snapshots: {status['total_snapshots']}")
        logger.info(f"   📅 Latest Snapshot: {status['latest_snapshot']}")
        
        logger.info("🎉 Daily collection completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Daily collection failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """Main entry point"""
    success = collect_daily_data()
    
    if success:
        print("✅ Daily collection completed successfully!")
        sys.exit(0)
    else:
        print("❌ Daily collection failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
