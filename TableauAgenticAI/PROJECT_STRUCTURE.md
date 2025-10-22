# 📁 AI Bubble Analysis - Project Structure

## 🎯 **Core Project Files**

### **📊 Main Dashboard**
- `fixed_statistical_dashboard.html` - **Primary dashboard** with error bars, statistical analysis, and real historical data
- `fixed_statistical_dashboard.py` - Script to generate the statistical dashboard

### **🔧 Core Functionality**
- `src/` - Main source code directory
  - `app.py` - LangGraph workflow definition
  - `bubble_analysis.py` - AI bubble analysis engine
  - `news_tracker.py` - News article tracking and management
  - `financial_data_collector.py` - Financial data collection (no API calls)
  - `financial_indicators.py` - Financial indicators calculation
  - `time_series_collector.py` - Time series data collection
  - `historical_data_collector.py` - Historical data backfill
  - `config.py` - Configuration and API setup
  - `search.py` - News search functionality
  - `summarize.py` - Article summarization
  - `selection.py` - Article selection logic
  - `tableau_export.py` - Data export for Tableau
  - `bubble_cli.py` - Command-line interface for bubble analysis
  - `time_series_cli.py` - CLI for time series management
  - `historical_cli.py` - CLI for historical data management

### **📈 Data Collection & Analysis**
- `backfill_historical_data.py` - Collect 30 days of historical AI news data
- `daily_collection.py` - Automated daily data collection script

### **📚 Documentation**
- `README.md` - Main project documentation
- `RUNNING_THE_PROJECT.md` - Detailed setup and usage instructions
- `AI_NEWS_CONCEPTS_REVIEW.md` - AI news identification concepts
- `PROJECT_STRUCTURE.md` - This file (project structure overview)

### **🔧 Utilities**
- `graphviz_workflow.py` - Generate workflow visualization
- `requirements.txt` - Python dependencies

## 🗂️ **Data Directories**

### **📊 Time Series Data**
- `time_series_data/` - Daily snapshots and historical data
  - `daily_snapshots.json` - Daily bubble analysis snapshots
  - `grafana_time_series_30d.csv` - Grafana-compatible time series data

### **📈 Historical Data**
- `historical_data/` - 30 days of historical AI news
  - `historical_data.json` - Complete historical dataset
  - `historical_data.csv` - CSV format for analysis

## 🚀 **Quick Start Commands**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Collect Historical Data**
```bash
python backfill_historical_data.py
```

### **3. View Dashboard**
```bash
python fixed_statistical_dashboard.py
# Then open: fixed_statistical_dashboard.html
```

### **4. Daily Data Collection**
```bash
python daily_collection.py
```

## 📊 **Dashboard Features**

### **📈 Statistical Analysis Dashboard**
- **Article Analysis Breakdown** with 95% confidence interval error bars
- **Risk Indicators Over Time** showing 30-day evolution
- **Correlation Matrix** displaying indicator relationships
- **Distribution Analysis** with quartile visualization
- **Real Historical Data** from 30 days of AI news analysis

### **🔍 Key Metrics**
- **5 Risk Indicators**: Hype Level, Investment Frenzy, Market Speculation, Competitive Intensity, Regulatory Concern
- **Statistical Validation**: All indicators normally distributed (Shapiro-Wilk p > 0.05)
- **Error Quantification**: Standard Error of Mean (SEM) and 95% confidence intervals
- **Correlation Analysis**: Strong correlations between investment activity and competition

## 🎯 **Project Capabilities**

### **📰 News Analysis**
- Tracks top 10 most relevant AI news articles daily
- Analyzes articles for bubble risk indicators
- Sentiment analysis and market impact assessment
- Historical data collection and trend analysis

### **💰 Financial Integration**
- Real-time stock market data (no API calls required)
- Financial indicators calculation
- Combined risk scoring (70% article + 30% financial)
- Market volatility and momentum analysis

### **📊 Statistical Analysis**
- Distribution testing (normality tests)
- Correlation analysis over time
- Error bar calculations with confidence intervals
- Trend analysis and pattern recognition

### **🔄 Automation**
- Daily data collection scripts
- Automated historical data backfill
- Command-line interfaces for all operations
- Grafana integration for time series visualization

## 📈 **Data Flow**

1. **News Collection** → Tavily API searches for AI news
2. **Article Analysis** → AI analyzes articles for bubble indicators
3. **Financial Data** → yfinance collects market data
4. **Statistical Analysis** → Risk indicators calculated with error bars
5. **Dashboard Visualization** → Interactive charts with real data
6. **Historical Tracking** → 30-day trend analysis and correlation

## 🎉 **Key Achievements**

- ✅ **Real Historical Data**: 30 days of actual AI news analysis
- ✅ **Statistical Validation**: All indicators normally distributed
- ✅ **Error Quantification**: Proper confidence intervals and error bars
- ✅ **Financial Integration**: Market data without API calls
- ✅ **Interactive Dashboards**: Working charts with real data
- ✅ **Automation**: Daily collection and historical backfill
- ✅ **Clean Codebase**: Organized, documented, and maintainable
