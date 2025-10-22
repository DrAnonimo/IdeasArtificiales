
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
