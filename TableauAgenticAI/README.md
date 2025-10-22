# AI Bubble Analysis - TableauAgenticAI

An advanced AI system for tracking and analyzing AI-related news to predict potential market bubbles using LangGraph workflows, OpenAI LLM, and Tavily API.

## 🎯 **Quick Start**

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

## 📊 **Main Dashboard**

**`fixed_statistical_dashboard.html`** - Primary dashboard featuring:
- **Article Analysis Breakdown** with 95% confidence interval error bars
- **Risk Indicators Over Time** (30-day evolution)
- **Correlation Matrix** showing indicator relationships
- **Distribution Analysis** with quartile visualization
- **Real Historical Data** from 30 days of AI news analysis

## 📁 **Project Structure**

See `PROJECT_STRUCTURE.md` for detailed file organization and capabilities.

## 🔧 **Core Features**

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

## 📈 **Key Metrics**

### **5 Risk Indicators**
1. **Hype Level** - Market hype and excitement
2. **Investment Frenzy** - Funding activity intensity
3. **Market Speculation** - Speculative behavior
4. **Competitive Intensity** - Market competition level
5. **Regulatory Concern** - Regulatory attention and warnings

### **Statistical Validation**
- ✅ **All indicators normally distributed** (Shapiro-Wilk p > 0.05)
- ✅ **95% confidence intervals** for all measurements
- ✅ **Error quantification** with Standard Error of Mean (SEM)
- ✅ **Correlation analysis** showing indicator relationships

## 🎉 **Key Achievements**

- ✅ **Real Historical Data**: 30 days of actual AI news analysis
- ✅ **Statistical Validation**: All indicators normally distributed
- ✅ **Error Quantification**: Proper confidence intervals and error bars
- ✅ **Financial Integration**: Market data without API calls
- ✅ **Interactive Dashboards**: Working charts with real data
- ✅ **Automation**: Daily collection and historical backfill
- ✅ **Clean Codebase**: Organized, documented, and maintainable

## 📊 **Data Flow**

```
News Collection → Article Analysis → Financial Data → Statistical Analysis → Dashboard
     ↓              ↓                  ↓                ↓                    ↓
  Tavily API    AI Analysis      yfinance API    Error Bars &        Interactive
  Articles      5 KPIs +         Market Data     Correlations        Charts
                Sentiment        (No API calls)  (Normal dist.)     (Real data)
```

## 🔧 **Usage**

### **Historical Data Collection**
```bash
# Collect 30 days of historical data
python backfill_historical_data.py
```

### **Daily Data Collection**
```bash
# Collect today's data
python daily_collection.py
```

### **View Trends**
```bash
# Show trends via CLI
python -m src.time_series_cli trends --days 30
```

### **Original LinkedIn Workflow**
```bash
# Generate LinkedIn posts (original functionality)
python -m src.cli
```

## 📋 **Documentation**

- **PROJECT_STRUCTURE.md**: Detailed file organization and capabilities
- **RUNNING_THE_PROJECT.md**: Comprehensive setup and usage instructions
- **AI_NEWS_CONCEPTS_REVIEW.md**: AI news identification concepts

## 🔧 **Troubleshooting**

### **Common Issues**
1. **API Key Errors**: Check `.env` file has correct keys
2. **Dependency Issues**: Run `pip install -r requirements.txt`
3. **No Data**: Check daily collection script logs
4. **Dashboard Issues**: Ensure `fixed_statistical_dashboard.html` is generated

### **Getting Help**
```bash
# Check status
python -m src.time_series_cli status

# View trends
python -m src.time_series_cli trends

# Check collection logs
ls logs/
```

---

*This system provides comprehensive insights into AI market trends and bubble risk evolution, enabling data-driven decision making through statistical analysis and interactive dashboards.*