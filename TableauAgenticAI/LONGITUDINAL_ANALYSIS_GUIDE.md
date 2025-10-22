# AI Bubble Analysis - Longitudinal Analysis Guide

## Overview

This guide explains how to set up and use the longitudinal AI bubble analysis system with Grafana for time-series visualization. The system collects daily snapshots of AI market data and provides comprehensive trend analysis over time.

## 🎯 **Key Features**

### **Daily Data Collection**
- **Automated daily snapshots** of AI bubble analysis
- **Persistent time-series storage** with historical data
- **Trend analysis** with statistical calculations
- **Risk level evolution** tracking over time

### **Grafana Dashboard**
- **Real-time time-series visualizations**
- **Interactive trend analysis**
- **Risk level monitoring** with alerts
- **Correlation analysis** between different metrics
- **Historical data exploration**

### **Longitudinal Insights**
- **Bubble risk evolution** over weeks/months
- **Sentiment trend analysis** with volatility tracking
- **Indicator correlation** and pattern recognition
- **Market assessment changes** over time
- **Early warning system** for bubble formation

## 🚀 **Quick Start**

### **1. Daily Data Collection**
```bash
# Collect today's data
python daily_collection.py

# Or use the CLI
python -m src.time_series_cli collect-daily
```

### **2. View Trends**
```bash
# Show 30-day trend analysis
python -m src.time_series_cli trends --days 30

# Show historical data
python -m src.time_series_cli history --days 30
```

### **3. Export for Grafana**
```bash
# Export 30 days of data for Grafana
python -m src.time_series_cli export-grafana --days 30
```

## 📊 **Data Collection Workflow**

### **Daily Collection Process**
1. **Search for AI news** using Tavily API
2. **Track top 5 articles** for analysis
3. **Analyze bubble indicators** using AI
4. **Calculate sentiment scores** and risk metrics
5. **Store daily snapshot** with timestamp
6. **Export for Grafana** dashboard
7. **Calculate trends** and changes

### **Data Storage Structure**
```
time_series_data/
├── daily_snapshots.json          # Historical snapshots
├── grafana_time_series_30d.csv   # Grafana export
├── grafana_dashboard.json        # Dashboard config
└── grafana_setup_instructions.md # Setup guide
```

## 📈 **Grafana Dashboard Setup**

### **1. Install Grafana**
```bash
# Using Docker (recommended)
docker run -d --name=grafana -p 3000:3000 grafana/grafana

# Or install locally
# Follow instructions at https://grafana.com/docs/grafana/latest/installation/
```

### **2. Data Source Configuration**

#### **Option A: CSV Data Source**
1. Install CSV plugin: `grafana-csv-datasource`
2. Add data source
3. Upload `grafana_time_series_30d.csv`
4. Configure timestamp column

#### **Option B: InfluxDB (Recommended)**
1. Install InfluxDB
2. Import CSV data
3. Add InfluxDB data source
4. Use measurement: `ai_bubble_analysis`

### **3. Dashboard Import**
1. Go to Dashboards → Import
2. Upload `grafana_dashboard.json`
3. Select your data source
4. Configure time ranges

## 📊 **Dashboard Visualizations**

### **1. Bubble Risk Evolution**
- **Time-series chart** showing bubble risk over time
- **Color-coded thresholds**: Green (0-0.4), Yellow (0.4-0.7), Red (0.7+)
- **Trend lines** and moving averages
- **Risk level changes** highlighted

### **2. Market Sentiment Analysis**
- **Sentiment score evolution** (-1 to +1)
- **Volatility tracking** and pattern recognition
- **Sentiment vs risk correlation**
- **Extreme sentiment alerts**

### **3. Indicator Heatmap**
- **All 5 KPIs** displayed as heatmap
- **Time-based visualization** of indicator changes
- **Pattern recognition** across indicators
- **Concerning indicator highlighting**

### **4. Risk Level Distribution**
- **Pie chart** of market assessments
- **Risk level changes** over time
- **Distribution analysis** by time period
- **Trend identification**

### **5. Correlation Analysis**
- **Bubble risk vs sentiment** scatter plot
- **Indicator correlation** matrix
- **Pattern recognition** and insights
- **Anomaly detection**

## 🔍 **Key Metrics and KPIs**

### **Primary Metrics**
- **Bubble Risk Score** (0-1): Overall risk assessment
- **Sentiment Score** (-1 to +1): Market sentiment
- **Concerning Articles Count**: High-risk articles
- **Analysis Coverage**: Percentage of articles analyzed

### **Trend Metrics**
- **Risk Trend Direction**: Increasing/Decreasing/Stable
- **Sentiment Volatility**: Market stability measure
- **Risk Level Changes**: LOW → MODERATE → HIGH
- **Indicator Correlation**: How indicators move together

### **Alert Thresholds**
- **High Risk Alert**: Bubble risk > 0.7
- **Sentiment Shift**: Change > 0.3 in 1 hour
- **Concerning Articles**: Count > 4
- **Volatility Spike**: Standard deviation > 0.2

## 📅 **Daily Automation**

### **Cron Job Setup**
```bash
# Add to crontab for daily collection at 9 AM
0 9 * * * cd /path/to/project && python daily_collection.py >> logs/daily_collection.log 2>&1
```

### **Manual Collection**
```bash
# Collect today's data
python daily_collection.py

# Force re-analysis
python -m src.time_series_cli collect-daily --force
```

### **Status Monitoring**
```bash
# Check collection status
python -m src.time_series_cli status

# View recent data
python -m src.time_series_cli history --days 7
```

## 📊 **Longitudinal Analysis Insights**

### **Bubble Risk Evolution**
- **Track risk progression** over weeks/months
- **Identify risk accumulation** patterns
- **Detect early warning signs** of bubble formation
- **Monitor risk level transitions**

### **Sentiment Analysis**
- **Market sentiment cycles** and patterns
- **Sentiment volatility** and stability
- **Extreme sentiment events** and recovery
- **Sentiment-risk correlation** changes

### **Indicator Trends**
- **Individual KPI evolution** over time
- **Indicator correlation** changes
- **Leading vs lagging indicators** identification
- **Indicator threshold breaches** and patterns

### **Market Assessment Changes**
- **Risk level transitions** (LOW → MODERATE → HIGH)
- **Assessment stability** and consistency
- **Assessment accuracy** over time
- **Market state evolution** patterns

## 🔧 **Advanced Configuration**

### **Custom Time Ranges**
```bash
# Analyze specific periods
python -m src.time_series_cli trends --days 90
python -m src.time_series_cli history --days 7
```

### **Data Cleaning**
```bash
# Remove old data (keep last 90 days)
python -m src.time_series_cli clean --days 90
```

### **Export Customization**
```bash
# Export different time periods
python -m src.time_series_cli export-grafana --days 60
```

## 📈 **Dashboard Features**

### **Interactive Controls**
- **Time range selection**: 7d, 30d, 90d, 1y
- **Refresh intervals**: 1m, 5m, 15m, 1h
- **Filter controls**: By indicator, risk level, date
- **Zoom and pan**: Detailed time period analysis

### **Alerting System**
- **High risk alerts**: When bubble risk exceeds threshold
- **Sentiment shift alerts**: Significant sentiment changes
- **Volatility alerts**: Unusual market volatility
- **Custom alerts**: User-defined conditions

### **Export Capabilities**
- **Dashboard export**: PNG, PDF, JSON
- **Data export**: CSV, JSON formats
- **Report generation**: Automated reports
- **Sharing**: Dashboard sharing and collaboration

## 🚨 **Monitoring and Alerts**

### **Risk Level Monitoring**
- **Real-time risk assessment** updates
- **Risk level change notifications**
- **Threshold breach alerts**
- **Risk accumulation warnings**

### **Trend Monitoring**
- **Trend direction changes** alerts
- **Volatility spike** notifications
- **Pattern recognition** alerts
- **Anomaly detection** warnings

### **Data Quality Monitoring**
- **Collection success** tracking
- **Data completeness** monitoring
- **API availability** checks
- **Analysis quality** validation

## 📋 **Best Practices**

### **Daily Collection**
1. **Run at consistent times** (e.g., 9 AM daily)
2. **Monitor collection logs** for errors
3. **Verify data quality** after collection
4. **Check API key validity** regularly

### **Dashboard Usage**
1. **Set appropriate time ranges** for analysis
2. **Use filters** to focus on specific periods
3. **Monitor alerts** and notifications
4. **Export data** for external analysis

### **Data Management**
1. **Clean old data** regularly (keep 90+ days)
2. **Backup snapshots** periodically
3. **Monitor storage usage**
4. **Validate data integrity**

## 🔍 **Troubleshooting**

### **Common Issues**
1. **No data appearing**: Check data source connection
2. **Missing snapshots**: Verify daily collection script
3. **API errors**: Check API keys and quotas
4. **Performance issues**: Limit time ranges, optimize queries

### **Data Quality Issues**
1. **Incomplete analysis**: Check API availability
2. **Missing indicators**: Verify analysis configuration
3. **Inconsistent data**: Check for collection errors
4. **Timestamp issues**: Verify timezone settings

## 📊 **Expected Insights**

### **Short-term (1-7 days)**
- **Daily risk fluctuations**
- **Sentiment changes**
- **News impact analysis**
- **Indicator sensitivity**

### **Medium-term (1-4 weeks)**
- **Risk trend identification**
- **Sentiment cycle patterns**
- **Indicator correlation changes**
- **Market assessment evolution**

### **Long-term (1-6 months)**
- **Bubble formation patterns**
- **Market cycle identification**
- **Risk accumulation trends**
- **Predictive insights**

---

*This longitudinal analysis system provides comprehensive insights into AI market trends and bubble risk evolution over time, enabling data-driven decision making and early warning detection.*
