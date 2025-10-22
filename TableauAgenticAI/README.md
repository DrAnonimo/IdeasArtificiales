# AI Bubble Analysis - Longitudinal Dashboard

A comprehensive system for tracking and analyzing AI market trends and bubble indicators over time, with Grafana dashboard integration for longitudinal analysis.

## 🎯 **Overview**

This project provides:
- **Daily AI news collection** and analysis
- **5 Key Performance Indicators** for bubble detection
- **Time-series data collection** for longitudinal analysis
- **Grafana dashboard** for real-time monitoring
- **Automated daily collection** with trend analysis

## 🚀 **Quick Start**

### **1. Installation**
```bash
pip install -r requirements.txt
```

### **2. Environment Setup**
Create a `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### **3. Run Demo**
```bash
python demo_longitudinal_analysis.py
```

### **4. Daily Collection**
```bash
python daily_collection.py
```

## 📊 **Key Features**

### **Bubble Analysis**
- **5 KPIs**: Hype Level, Investment Frenzy, Market Speculation, Competitive Intensity, Regulatory Concern
- **Sentiment Analysis**: AI-powered sentiment scoring (-1 to +1)
- **Risk Assessment**: Overall bubble risk scoring (0 to 1)
- **Market Assessment**: Text-based market state evaluation

### **Time Series Collection**
- **Daily snapshots** of AI market data
- **Historical trend analysis** with statistical calculations
- **Volatility tracking** and pattern recognition
- **Risk level evolution** monitoring

### **Grafana Dashboard**
- **Real-time visualizations** of bubble risk evolution
- **Interactive time range** selection
- **Alert system** for risk threshold breaches
- **Multiple chart types** for comprehensive analysis

## 🔧 **Usage**

### **Daily Data Collection**
```bash
# Collect today's data
python daily_collection.py

# Or use CLI
python -m src.time_series_cli collect-daily
```

### **Trend Analysis**
```bash
# Show 30-day trends
python -m src.time_series_cli trends --days 30

# View historical data
python -m src.time_series_cli history --days 30
```

### **Grafana Export**
```bash
# Export data for Grafana
python -m src.time_series_cli export-grafana --days 30
```

### **Original LinkedIn Workflow**
```bash
# Generate LinkedIn posts (original functionality)
python -m src.cli
```

## 📁 **Project Structure**

```
TableauAgenticAI/
├── src/                          # Core source code
│   ├── app.py                    # Main LangGraph workflow
│   ├── bubble_analysis.py        # Bubble analysis engine
│   ├── news_tracker.py           # News tracking system
│   ├── time_series_collector.py  # Time series data collection
│   ├── tableau_export.py         # Tableau export functionality
│   ├── bubble_cli.py             # Bubble analysis CLI
│   ├── time_series_cli.py        # Time series CLI
│   ├── cli.py                    # Original LinkedIn CLI
│   ├── search.py                 # News search functionality
│   ├── summarize.py              # News summarization
│   ├── selection.py              # Post generation and verification
│   └── config.py                 # Configuration management
├── daily_collection.py           # Daily automation script
├── demo_longitudinal_analysis.py # Demo script
├── grafana_dashboard.json        # Grafana dashboard config
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── BUBBLE_ANALYSIS_README.md     # Detailed bubble analysis guide
└── LONGITUDINAL_ANALYSIS_GUIDE.md # Grafana setup guide
```

## 📊 **Data Flow**

```
News Search → Bubble Analysis → Time Series Collection → Grafana Dashboard
     ↓              ↓                    ↓                    ↓
  Tavily API    AI Analysis        Daily Snapshots      Real-time
  Articles     5 KPIs + Sentiment  Historical Data     Visualization
```

## 🔍 **Key Metrics**

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

## 📈 **Grafana Dashboard**

### **Visualizations**
1. **Bubble Risk Evolution** - Main risk score over time
2. **Market Sentiment Analysis** - Sentiment trends and volatility
3. **Bubble Indicators Heatmap** - All 5 KPIs over time
4. **Risk Level Distribution** - Market assessment changes
5. **Correlation Analysis** - Risk vs sentiment scatter plot

### **Features**
- **Real-time updates** with 5-minute refresh
- **Interactive controls** and time range selection
- **Alert system** for risk threshold breaches
- **Export capabilities** for reports

## 🤖 **Automation**

### **Daily Collection**
Set up a cron job for daily collection:
```bash
# Add to crontab for daily collection at 9 AM
0 9 * * * cd /path/to/project && python daily_collection.py >> logs/daily_collection.log 2>&1
```

### **Monitoring**
- **Collection logs** in `logs/` directory
- **Status monitoring** via CLI commands
- **Error handling** and recovery
- **Data quality** validation

## 📋 **Documentation**

- **BUBBLE_ANALYSIS_README.md**: Detailed guide for bubble analysis features
- **LONGITUDINAL_ANALYSIS_GUIDE.md**: Comprehensive Grafana setup guide
- **project_description.txt**: Original project description

## 🔧 **Troubleshooting**

### **Common Issues**
1. **API Key Errors**: Check `.env` file has correct keys
2. **Dependency Issues**: Run `pip install -r requirements.txt`
3. **No Data**: Check daily collection script logs
4. **Grafana Issues**: Follow setup guide in exported files

### **Getting Help**
```bash
# Check status
python -m src.time_series_cli status

# View trends
python -m src.time_series_cli trends

# Check collection logs
ls logs/
```

## 🎉 **Benefits**

- **Longitudinal Analysis**: Track AI bubble risk evolution over time
- **Early Warning System**: Detect bubble formation patterns
- **Data-Driven Insights**: Make informed decisions based on trends
- **Professional Dashboards**: Beautiful Grafana visualizations
- **Automated Collection**: Daily data collection without manual intervention

---

*This system provides comprehensive insights into AI market trends and bubble risk evolution, enabling data-driven decision making through beautiful time-series dashboards.*