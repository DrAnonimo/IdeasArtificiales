from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import pandas as pd
from .news_tracker import NewsTracker
from .bubble_analysis import AIBubbleAnalyzer


@dataclass
class DailySnapshot:
    """Represents a daily snapshot of AI bubble analysis"""
    date: str  # YYYY-MM-DD format
    timestamp: str  # ISO timestamp
    total_articles: int
    analyzed_articles: int
    average_sentiment: float
    average_bubble_risk: float
    market_assessment: str
    concerning_articles: int
    indicator_scores: Dict[str, float]
    top_articles: List[Dict[str, Any]]
    analysis_metadata: Dict[str, Any]


class TimeSeriesCollector:
    """Collects and manages time-series data for longitudinal analysis"""
    
    def __init__(self, data_dir: str = "time_series_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.tracker = NewsTracker()
        self.analyzer = AIBubbleAnalyzer()
        self.snapshots_file = self.data_dir / "daily_snapshots.json"
        self.load_snapshots()

    def collect_daily_snapshot(self, force_reanalyze: bool = False) -> DailySnapshot:
        """Collect a daily snapshot of AI bubble analysis"""
        print(f"📊 Collecting daily snapshot for {datetime.now().strftime('%Y-%m-%d')}...")
        
        # Analyze current news
        analysis_result = self.tracker.analyze_news(force_reanalyze=force_reanalyze)
        bubble_report = self.tracker.get_bubble_report()
        
        if 'error' in bubble_report:
            raise RuntimeError(f"Analysis failed: {bubble_report['error']}")
        
        # Create daily snapshot
        snapshot = DailySnapshot(
            date=datetime.now().strftime('%Y-%m-%d'),
            timestamp=datetime.now().isoformat(),
            total_articles=bubble_report['total_articles'],
            analyzed_articles=analysis_result['analyzed_count'],
            average_sentiment=bubble_report['average_sentiment'],
            average_bubble_risk=bubble_report['average_bubble_risk'],
            market_assessment=bubble_report['market_assessment'],
            concerning_articles=bubble_report['concerning_articles'],
            indicator_scores=bubble_report['indicator_averages'],
            top_articles=[
                {
                    'title': article['title'],
                    'url': article['url'],
                    'sentiment_score': article['sentiment_score'],
                    'bubble_risk': article['bubble_risk'],
                    'market_impact': article['market_impact']
                }
                for article in bubble_report['individual_analyses']
            ],
            analysis_metadata={
                'tracker_status': self.tracker.get_status(),
                'analysis_date': bubble_report['analysis_date'],
                'data_source': 'tavily_api'
            }
        )
        
        # Store snapshot
        self.add_snapshot(snapshot)
        
        print(f"✅ Daily snapshot collected: {snapshot.market_assessment}")
        print(f"   📊 Bubble Risk: {snapshot.average_bubble_risk:.3f}")
        print(f"   😊 Sentiment: {snapshot.average_sentiment:.3f}")
        print(f"   🚨 Concerning Articles: {snapshot.concerning_articles}")
        
        return snapshot

    def add_snapshot(self, snapshot: DailySnapshot) -> None:
        """Add a snapshot to the collection"""
        # Check if snapshot for this date already exists
        existing_snapshot = self.get_snapshot_by_date(snapshot.date)
        if existing_snapshot:
            print(f"⚠️  Snapshot for {snapshot.date} already exists. Updating...")
            self.remove_snapshot_by_date(snapshot.date)
        
        self.snapshots.append(snapshot)
        self.save_snapshots()

    def get_snapshot_by_date(self, date: str) -> Optional[DailySnapshot]:
        """Get snapshot for a specific date"""
        for snapshot in self.snapshots:
            if snapshot.date == date:
                return snapshot
        return None

    def remove_snapshot_by_date(self, date: str) -> bool:
        """Remove snapshot for a specific date"""
        initial_count = len(self.snapshots)
        self.snapshots = [s for s in self.snapshots if s.date != date]
        removed = len(self.snapshots) < initial_count
        if removed:
            self.save_snapshots()
        return removed

    def get_snapshots_in_range(self, start_date: str, end_date: str) -> List[DailySnapshot]:
        """Get snapshots within a date range"""
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        filtered = []
        for snapshot in self.snapshots:
            snapshot_dt = datetime.strptime(snapshot.date, '%Y-%m-%d')
            if start_dt <= snapshot_dt <= end_dt:
                filtered.append(snapshot)
        
        return sorted(filtered, key=lambda x: x.date)

    def get_latest_snapshots(self, days: int = 30) -> List[DailySnapshot]:
        """Get the latest N days of snapshots"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        filtered = []
        for snapshot in self.snapshots:
            if snapshot.date >= cutoff_str:
                filtered.append(snapshot)
        
        return sorted(filtered, key=lambda x: x.date)

    def calculate_trends(self, days: int = 30) -> Dict[str, Any]:
        """Calculate trends over the specified period"""
        recent_snapshots = self.get_latest_snapshots(days)
        
        if len(recent_snapshots) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Calculate trends for key metrics
        bubble_risk_trend = self._calculate_trend(
            [s.average_bubble_risk for s in recent_snapshots]
        )
        sentiment_trend = self._calculate_trend(
            [s.average_sentiment for s in recent_snapshots]
        )
        concerning_articles_trend = self._calculate_trend(
            [s.concerning_articles for s in recent_snapshots]
        )
        
        # Calculate indicator trends
        indicator_trends = {}
        for indicator in recent_snapshots[0].indicator_scores.keys():
            values = [s.indicator_scores.get(indicator, 0) for s in recent_snapshots]
            indicator_trends[indicator] = self._calculate_trend(values)
        
        # Calculate volatility
        bubble_risk_volatility = self._calculate_volatility(
            [s.average_bubble_risk for s in recent_snapshots]
        )
        
        return {
            "period_days": days,
            "snapshots_count": len(recent_snapshots),
            "date_range": {
                "start": recent_snapshots[0].date,
                "end": recent_snapshots[-1].date
            },
            "trends": {
                "bubble_risk": bubble_risk_trend,
                "sentiment": sentiment_trend,
                "concerning_articles": concerning_articles_trend
            },
            "indicator_trends": indicator_trends,
            "volatility": {
                "bubble_risk": bubble_risk_volatility
            },
            "latest_assessment": recent_snapshots[-1].market_assessment,
            "risk_level_change": self._calculate_risk_level_change(recent_snapshots)
        }

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend statistics for a series of values"""
        if len(values) < 2:
            return {"direction": "insufficient_data", "slope": 0, "change_percent": 0}
        
        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        
        # Calculate slope using least squares
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Calculate percentage change
        start_value = values[0]
        end_value = values[-1]
        change_percent = ((end_value - start_value) / start_value * 100) if start_value != 0 else 0
        
        # Determine direction
        if slope > 0.01:
            direction = "increasing"
        elif slope < -0.01:
            direction = "decreasing"
        else:
            direction = "stable"
        
        return {
            "direction": direction,
            "slope": slope,
            "change_percent": change_percent,
            "start_value": start_value,
            "end_value": end_value
        }

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation) of values"""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

    def _calculate_risk_level_change(self, snapshots: List[DailySnapshot]) -> Dict[str, Any]:
        """Calculate how risk levels have changed over time"""
        if len(snapshots) < 2:
            return {"change": "insufficient_data"}
        
        def get_risk_level(bubble_risk: float) -> str:
            if bubble_risk > 0.7:
                return "HIGH"
            elif bubble_risk > 0.4:
                return "MODERATE"
            else:
                return "LOW"
        
        start_level = get_risk_level(snapshots[0].average_bubble_risk)
        end_level = get_risk_level(snapshots[-1].average_bubble_risk)
        
        return {
            "start_level": start_level,
            "end_level": end_level,
            "change": "increased" if end_level > start_level else "decreased" if end_level < start_level else "stable"
        }

    def export_for_grafana(self, days: int = 30) -> Dict[str, str]:
        """Export data in Grafana-compatible formats"""
        recent_snapshots = self.get_latest_snapshots(days)
        
        if not recent_snapshots:
            return {"error": "No data available for export"}
        
        # Create time series data
        time_series_data = []
        for snapshot in recent_snapshots:
            base_record = {
                "timestamp": snapshot.timestamp,
                "date": snapshot.date,
                "total_articles": snapshot.total_articles,
                "analyzed_articles": snapshot.analyzed_articles,
                "average_sentiment": snapshot.average_sentiment,
                "average_bubble_risk": snapshot.average_bubble_risk,
                "concerning_articles": snapshot.concerning_articles,
                "market_assessment": snapshot.market_assessment
            }
            
            # Add individual indicators
            for indicator, value in snapshot.indicator_scores.items():
                record = base_record.copy()
                record.update({
                    "indicator_name": indicator,
                    "indicator_value": value,
                    "metric_type": "indicator"
                })
                time_series_data.append(record)
            
            # Add summary metrics
            summary_record = base_record.copy()
            summary_record.update({
                "indicator_name": "summary",
                "indicator_value": snapshot.average_bubble_risk,
                "metric_type": "summary"
            })
            time_series_data.append(summary_record)
        
        # Export to CSV
        csv_file = self.data_dir / f"grafana_time_series_{days}d.csv"
        df = pd.DataFrame(time_series_data)
        df.to_csv(csv_file, index=False)
        
        # Create Grafana dashboard configuration
        dashboard_config = self._create_grafana_dashboard_config(recent_snapshots)
        dashboard_file = self.data_dir / "grafana_dashboard.json"
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_config, f, indent=2)
        
        # Create setup instructions
        instructions = self._create_grafana_setup_instructions()
        instructions_file = self.data_dir / "grafana_setup_instructions.md"
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        return {
            "time_series_csv": str(csv_file),
            "dashboard_config": str(dashboard_file),
            "setup_instructions": str(instructions_file),
            "data_points": len(time_series_data),
            "date_range": f"{recent_snapshots[0].date} to {recent_snapshots[-1].date}"
        }

    def _create_grafana_dashboard_config(self, snapshots: List[DailySnapshot]) -> Dict[str, Any]:
        """Create Grafana dashboard configuration"""
        return {
            "dashboard": {
                "id": None,
                "title": "AI Bubble Analysis - Time Series Dashboard",
                "tags": ["ai", "bubble", "analysis", "time-series"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Bubble Risk Over Time",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "average_bubble_risk",
                                "legendFormat": "Bubble Risk"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "short",
                                "min": 0,
                                "max": 1,
                                "thresholds": {
                                    "steps": [
                                        {"color": "green", "value": 0},
                                        {"color": "yellow", "value": 0.4},
                                        {"color": "red", "value": 0.7}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": 2,
                        "title": "Sentiment Analysis",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "average_sentiment",
                                "legendFormat": "Sentiment Score"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "short",
                                "min": -1,
                                "max": 1
                            }
                        }
                    },
                    {
                        "id": 3,
                        "title": "Bubble Indicators Heatmap",
                        "type": "heatmap",
                        "targets": [
                            {
                                "expr": "indicator_value",
                                "legendFormat": "{{indicator_name}}"
                            }
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Concerning Articles Count",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "concerning_articles",
                                "legendFormat": "Concerning Articles"
                            }
                        ]
                    }
                ],
                "time": {
                    "from": "now-30d",
                    "to": "now"
                },
                "refresh": "5m"
            }
        }

    def _create_grafana_setup_instructions(self) -> str:
        """Create Grafana setup instructions"""
        return """
# Grafana Setup Instructions for AI Bubble Analysis

## 1. Data Source Setup

### Option A: CSV Data Source
1. Install the CSV data source plugin: `grafana-csv-datasource`
2. Add a new data source
3. Select "CSV" as the type
4. Upload the `grafana_time_series_30d.csv` file
5. Configure the timestamp column as "timestamp"

### Option B: InfluxDB (Recommended for time-series)
1. Install InfluxDB
2. Import the CSV data into InfluxDB
3. Add InfluxDB as a data source in Grafana
4. Use the following measurement: `ai_bubble_analysis`

## 2. Dashboard Import

1. Go to Dashboards → Import
2. Upload the `grafana_dashboard.json` file
3. Select your data source
4. Adjust time ranges and refresh intervals as needed

## 3. Key Visualizations

### Time Series Panels
- **Bubble Risk Over Time**: Shows the evolution of bubble risk
- **Sentiment Analysis**: Tracks market sentiment changes
- **Indicator Trends**: Individual KPI trends over time

### Heatmaps
- **Indicator Heatmap**: Shows all indicators over time
- **Risk Level Heatmap**: Color-coded risk levels

### Stat Panels
- **Current Risk Level**: Latest bubble risk assessment
- **Concerning Articles**: Count of high-risk articles
- **Market Assessment**: Current market state

## 4. Alerts Setup

### High Risk Alert
- Condition: `average_bubble_risk > 0.7`
- Message: "AI Bubble Risk is HIGH: {{$value}}"

### Sentiment Shift Alert
- Condition: `average_sentiment` changes by > 0.3 in 1 hour
- Message: "Significant sentiment shift detected"

## 5. Dashboard Features

### Time Range Controls
- Default: Last 30 days
- Quick ranges: 7d, 30d, 90d, 1y
- Custom range selection

### Refresh Intervals
- Auto-refresh: 5 minutes
- Manual refresh available
- Real-time updates when new data is available

### Filters
- Filter by indicator type
- Filter by risk level
- Filter by date range

## 6. Data Collection

### Daily Collection
Run the daily collection script:
```bash
python -m src.time_series_collector collect-daily
```

### Automated Collection
Set up a cron job for daily collection:
```bash
# Add to crontab
0 9 * * * cd /path/to/project && python -m src.time_series_collector collect-daily
```

## 7. Data Schema

### Time Series Data Structure
- `timestamp`: ISO timestamp
- `date`: YYYY-MM-DD format
- `total_articles`: Number of articles analyzed
- `analyzed_articles`: Number of articles with complete analysis
- `average_sentiment`: Average sentiment score (-1 to 1)
- `average_bubble_risk`: Average bubble risk score (0 to 1)
- `concerning_articles`: Number of articles with concerning indicators
- `market_assessment`: Text assessment of market state
- `indicator_name`: Name of the specific indicator
- `indicator_value`: Value of the indicator
- `metric_type`: Type of metric (indicator, summary)

## 8. Troubleshooting

### Data Not Appearing
1. Check data source connection
2. Verify timestamp format
3. Check data file permissions

### Performance Issues
1. Limit time range for large datasets
2. Use data source caching
3. Optimize query patterns

### Missing Data
1. Check daily collection script logs
2. Verify API keys are valid
3. Check network connectivity
"""

    def load_snapshots(self) -> None:
        """Load snapshots from file"""
        self.snapshots = []
        if not self.snapshots_file.exists():
            return
        
        try:
            with open(self.snapshots_file, 'r') as f:
                data = json.load(f)
            
            for item in data.get('snapshots', []):
                snapshot = DailySnapshot(
                    date=item['date'],
                    timestamp=item['timestamp'],
                    total_articles=item['total_articles'],
                    analyzed_articles=item['analyzed_articles'],
                    average_sentiment=item['average_sentiment'],
                    average_bubble_risk=item['average_bubble_risk'],
                    market_assessment=item['market_assessment'],
                    concerning_articles=item['concerning_articles'],
                    indicator_scores=item['indicator_scores'],
                    top_articles=item['top_articles'],
                    analysis_metadata=item['analysis_metadata']
                )
                self.snapshots.append(snapshot)
                
        except Exception as e:
            print(f"Error loading snapshots: {e}")
            self.snapshots = []

    def save_snapshots(self) -> None:
        """Save snapshots to file"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'snapshots': [asdict(snapshot) for snapshot in self.snapshots]
            }
            
            with open(self.snapshots_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving snapshots: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get collector status"""
        return {
            "total_snapshots": len(self.snapshots),
            "latest_snapshot": self.snapshots[-1].date if self.snapshots else None,
            "data_directory": str(self.data_dir),
            "snapshots_file": str(self.snapshots_file),
            "last_updated": datetime.now().isoformat()
        }
