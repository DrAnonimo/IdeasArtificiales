from typing import Dict, Any, List
from datetime import datetime
import json
import csv
from pathlib import Path
from .news_tracker import NewsTracker


class TableauExporter:
    """Handles data export for Tableau dashboard integration"""
    
    def __init__(self, output_dir: str = "tableau_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.tracker = NewsTracker()

    def export_all_data(self) -> Dict[str, Any]:
        """Export all data in multiple formats for Tableau"""
        # Get the latest data
        self.tracker.analyze_news()
        
        # Export different data views
        results = {}
        
        # 1. Main articles data
        results['articles'] = self._export_articles_data()
        
        # 2. Bubble indicators data
        results['indicators'] = self._export_indicators_data()
        
        # 3. Time series data
        results['time_series'] = self._export_time_series_data()
        
        # 4. Summary metrics
        results['summary'] = self._export_summary_metrics()
        
        # 5. Generate Tableau workbook instructions
        results['tableau_instructions'] = self._generate_tableau_instructions()
        
        return results

    def _export_articles_data(self) -> str:
        """Export main articles data as CSV"""
        articles_data = self.tracker.export_tableau_data()
        
        if not articles_data:
            return "No data available for export"
        
        # Group by article for main articles table
        articles_by_id = {}
        for record in articles_data:
            article_id = record['article_id']
            if article_id not in articles_by_id:
                articles_by_id[article_id] = {
                    'article_id': article_id,
                    'title': record['title'],
                    'url': record['url'],
                    'analysis_date': record['analysis_date'],
                    'sentiment_score': record['sentiment_score'],
                    'overall_bubble_risk': record['overall_bubble_risk'],
                    'market_impact': record['market_impact'],
                    'key_phrases_count': record['key_phrases_count']
                }
        
        # Write to CSV
        articles_file = self.output_dir / "articles_data.csv"
        with open(articles_file, 'w', newline='', encoding='utf-8') as f:
            if articles_by_id:
                writer = csv.DictWriter(f, fieldnames=list(articles_by_id.values())[0].keys())
                writer.writeheader()
                writer.writerows(articles_by_id.values())
        
        return f"Articles data exported to {articles_file}"

    def _export_indicators_data(self) -> str:
        """Export bubble indicators data as CSV"""
        indicators_data = self.tracker.export_tableau_data()
        
        if not indicators_data:
            return "No data available for export"
        
        # Write to CSV
        indicators_file = self.output_dir / "indicators_data.csv"
        with open(indicators_file, 'w', newline='', encoding='utf-8') as f:
            if indicators_data:
                writer = csv.DictWriter(f, fieldnames=indicators_data[0].keys())
                writer.writeheader()
                writer.writerows(indicators_data)
        
        return f"Indicators data exported to {indicators_file}"

    def _export_time_series_data(self) -> str:
        """Export time series data for trend analysis"""
        articles_data = self.tracker.export_tableau_data()
        
        if not articles_data:
            return "No data available for export"
        
        # Create time series records
        time_series = []
        for record in articles_data:
            time_series.append({
                'date': record['analysis_date'][:10],  # YYYY-MM-DD
                'article_id': record['article_id'],
                'indicator_name': record['indicator_name'],
                'indicator_value': record['indicator_value'],
                'sentiment_score': record['sentiment_score'],
                'bubble_risk': record['overall_bubble_risk'],
                'is_concerning': record['is_concerning']
            })
        
        # Write to CSV
        time_series_file = self.output_dir / "time_series_data.csv"
        with open(time_series_file, 'w', newline='', encoding='utf-8') as f:
            if time_series:
                writer = csv.DictWriter(f, fieldnames=time_series[0].keys())
                writer.writeheader()
                writer.writerows(time_series)
        
        return f"Time series data exported to {time_series_file}"

    def _export_summary_metrics(self) -> str:
        """Export summary metrics for dashboard KPIs"""
        bubble_report = self.tracker.get_bubble_report()
        
        if 'error' in bubble_report:
            return "No data available for summary metrics"
        
        # Create summary metrics
        summary_metrics = {
            'metric_name': [],
            'metric_value': [],
            'metric_type': [],
            'description': []
        }
        
        # Add basic metrics
        summary_metrics['metric_name'].extend([
            'Total Articles',
            'Average Sentiment',
            'Average Bubble Risk',
            'Concerning Articles',
            'Market Assessment'
        ])
        summary_metrics['metric_value'].extend([
            bubble_report['total_articles'],
            bubble_report['average_sentiment'],
            bubble_report['average_bubble_risk'],
            bubble_report['concerning_articles'],
            bubble_report['market_assessment']
        ])
        summary_metrics['metric_type'].extend([
            'count',
            'score',
            'score',
            'count',
            'text'
        ])
        summary_metrics['description'].extend([
            'Total number of tracked articles',
            'Average sentiment score across all articles',
            'Average bubble risk score across all articles',
            'Number of articles with concerning indicators',
            'Overall market assessment based on analysis'
        ])
        
        # Add indicator averages
        for indicator, value in bubble_report['indicator_averages'].items():
            summary_metrics['metric_name'].append(f'{indicator.replace("_", " ").title()} Average')
            summary_metrics['metric_value'].append(value)
            summary_metrics['metric_type'].append('score')
            summary_metrics['description'].append(f'Average {indicator} score across all articles')
        
        # Write to CSV
        summary_file = self.output_dir / "summary_metrics.csv"
        with open(summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['metric_name', 'metric_value', 'metric_type', 'description'])
            for i in range(len(summary_metrics['metric_name'])):
                writer.writerow([
                    summary_metrics['metric_name'][i],
                    summary_metrics['metric_value'][i],
                    summary_metrics['metric_type'][i],
                    summary_metrics['description'][i]
                ])
        
        return f"Summary metrics exported to {summary_file}"

    def _generate_tableau_instructions(self) -> str:
        """Generate instructions for setting up Tableau dashboard"""
        instructions = """
# Tableau Dashboard Setup Instructions

## Data Sources
The following CSV files have been generated in the 'tableau_data' directory:

1. **articles_data.csv** - Main articles information
   - Fields: article_id, title, url, analysis_date, sentiment_score, overall_bubble_risk, market_impact, key_phrases_count

2. **indicators_data.csv** - Detailed bubble indicators
   - Fields: article_id, title, url, analysis_date, sentiment_score, overall_bubble_risk, market_impact, key_phrases_count, indicator_name, indicator_value, indicator_weight, indicator_trend, indicator_threshold, is_concerning, indicator_description

3. **time_series_data.csv** - Time series data for trend analysis
   - Fields: date, article_id, indicator_name, indicator_value, sentiment_score, bubble_risk, is_concerning

4. **summary_metrics.csv** - Key performance indicators
   - Fields: metric_name, metric_value, metric_type, description

## Recommended Dashboard Layout

### 1. Executive Summary Sheet
- **KPI Cards**: Total Articles, Average Sentiment, Average Bubble Risk, Concerning Articles
- **Market Assessment**: Text display of overall market assessment
- **Risk Level Indicator**: Color-coded gauge based on average bubble risk

### 2. Bubble Risk Analysis Sheet
- **Bubble Risk by Article**: Bar chart showing bubble risk for each article
- **Risk Distribution**: Histogram of bubble risk scores
- **Risk Trend**: Line chart showing bubble risk over time

### 3. Sentiment Analysis Sheet
- **Sentiment Distribution**: Histogram of sentiment scores
- **Sentiment vs Bubble Risk**: Scatter plot showing correlation
- **Sentiment Trend**: Line chart showing sentiment over time

### 4. Indicator Analysis Sheet
- **Indicator Heatmap**: Heatmap showing all indicators by article
- **Indicator Trends**: Line charts for each indicator over time
- **Concerning Indicators**: Table highlighting concerning indicators

### 5. Article Details Sheet
- **Article List**: Table with all articles and key metrics
- **Article Details**: Detailed view with full analysis
- **Key Phrases**: Word cloud or list of key phrases

## Key Visualizations

### Bubble Risk Gauge
- **Data**: summary_metrics.csv
- **Filter**: metric_name = "Average Bubble Risk"
- **Visualization**: Gauge chart
- **Color Coding**: 
  - Green: 0-0.3 (Low Risk)
  - Yellow: 0.3-0.6 (Moderate Risk)
  - Red: 0.6-1.0 (High Risk)

### Sentiment vs Bubble Risk Scatter Plot
- **Data**: articles_data.csv
- **X-Axis**: sentiment_score
- **Y-Axis**: overall_bubble_risk
- **Color**: market_impact
- **Size**: key_phrases_count

### Indicator Heatmap
- **Data**: indicators_data.csv
- **Rows**: article_id
- **Columns**: indicator_name
- **Color**: indicator_value
- **Filter**: is_concerning = True

### Time Series Trends
- **Data**: time_series_data.csv
- **X-Axis**: date
- **Y-Axis**: indicator_value
- **Color**: indicator_name
- **Filter**: is_concerning = True

## Calculated Fields

### Risk Level
```
IF [overall_bubble_risk] >= 0.7 THEN "High Risk"
ELSEIF [overall_bubble_risk] >= 0.4 THEN "Moderate Risk"
ELSE "Low Risk"
END
```

### Sentiment Category
```
IF [sentiment_score] >= 0.3 THEN "Positive"
ELSEIF [sentiment_score] <= -0.3 THEN "Negative"
ELSE "Neutral"
END
```

### Indicator Status
```
IF [is_concerning] = TRUE THEN "Concerning"
ELSE "Normal"
END
```

## Filters and Actions
- **Date Range**: Filter by analysis date
- **Risk Level**: Filter by calculated risk level
- **Sentiment**: Filter by sentiment category
- **Indicators**: Filter by specific indicators
- **Market Impact**: Filter by market impact assessment

## Dashboard Actions
- **Drill Down**: Click on article to see detailed analysis
- **Cross Filter**: Select indicators to highlight related articles
- **Highlight**: Click on data points to highlight across all sheets

## Data Refresh
- Run the Python script to update data files
- Refresh data sources in Tableau
- Update dashboard with new analysis

## Color Scheme
- **Low Risk**: Green (#2E8B57)
- **Moderate Risk**: Yellow (#FFD700)
- **High Risk**: Red (#DC143C)
- **Positive Sentiment**: Blue (#4169E1)
- **Negative Sentiment**: Orange (#FF8C00)
- **Neutral Sentiment**: Gray (#808080)
"""
        
        # Save instructions to file
        instructions_file = self.output_dir / "tableau_setup_instructions.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        return f"Tableau setup instructions saved to {instructions_file}"

    def get_export_status(self) -> Dict[str, Any]:
        """Get status of exported files"""
        files = list(self.output_dir.glob("*.csv")) + list(self.output_dir.glob("*.md"))
        
        return {
            "output_directory": str(self.output_dir),
            "files_created": [f.name for f in files],
            "total_files": len(files),
            "last_export": datetime.now().isoformat()
        }
