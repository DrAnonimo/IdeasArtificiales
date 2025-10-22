# AI Bubble Analysis Dashboard

## Overview

This enhanced version of the TableauAgenticAI project adds comprehensive AI bubble analysis capabilities, allowing you to track the top 5 most relevant AI news articles, analyze them for potential bubble indicators, and create a Tableau dashboard to monitor market trends and identify potential AI bubble risks.

## Key Features

### 🔍 **Intelligent News Tracking**
- Automatically tracks the top 5 most relevant AI news articles
- Maintains persistent storage of articles and their analysis
- Removes outdated articles automatically
- Deduplicates articles by URL while keeping the highest-scoring version

### 📊 **Comprehensive Bubble Analysis**
- **5 Key Performance Indicators (KPIs)** for bubble detection:
  - **Hype Level**: Measures superlative language and marketing hype
  - **Investment Frenzy**: Tracks funding discussions and large financial numbers
  - **Market Speculation**: Identifies future predictions and speculative language
  - **Competitive Intensity**: Measures competitive dynamics and market battles
  - **Regulatory Concern**: Tracks regulatory discussions and risk factors

### 🎯 **Advanced Sentiment Analysis**
- Uses AI to analyze article sentiment (-1 to +1 scale)
- Considers market optimism vs. pessimism
- Identifies extreme optimism that might indicate bubble risk
- Provides context-aware sentiment scoring

### 📈 **Tableau Dashboard Integration**
- Exports data in multiple CSV formats optimized for Tableau
- Provides comprehensive setup instructions
- Includes pre-built visualization recommendations
- Supports real-time data updates

## Key Performance Indicators (KPIs)

### 1. **Hype Level** (Weight: 25%)
- **Description**: Measures the level of superlative language and marketing hype
- **Keywords**: "revolutionary", "breakthrough", "game-changer", "disruptive", "transformative"
- **Threshold**: 0.7 (above this indicates concerning hype levels)
- **Calculation**: Counts hype words in title and content, with title weighted 3x more

### 2. **Investment Frenzy** (Weight: 20%)
- **Description**: Tracks intensity of investment and funding discussions
- **Keywords**: "funding", "investment", "valuation", "IPO", "acquisition", "billion", "million"
- **Threshold**: 0.6 (above this indicates investment frenzy)
- **Calculation**: Counts investment-related terms and large financial numbers

### 3. **Market Speculation** (Weight: 20%)
- **Description**: Identifies market speculation and future predictions
- **Keywords**: "bubble", "overvalued", "speculation", "frenzy", "mania", "euphoria"
- **Threshold**: 0.5 (above this indicates high speculation)
- **Calculation**: Counts speculative language and future prediction terms

### 4. **Competitive Intensity** (Weight: 15%)
- **Description**: Measures competitive dynamics and market battles
- **Keywords**: "race", "competition", "battle", "war", "arms race", "gold rush"
- **Threshold**: 0.6 (above this indicates intense competition)
- **Calculation**: Counts competitive terms and company name mentions

### 5. **Regulatory Concern** (Weight: 20%)
- **Description**: Tracks regulatory concerns and risk factors
- **Keywords**: "regulation", "oversight", "compliance", "policy", "government", "ban"
- **Threshold**: 0.4 (above this indicates regulatory concerns)
- **Calculation**: Counts regulatory terms and concern/risk language

## Installation and Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file with your API keys:
```bash
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run Bubble Analysis
```bash
# Search for news and analyze
python -m src.bubble_cli search-and-analyze

# Analyze existing tracked news
python -m src.bubble_cli analyze

# Export data for Tableau
python -m src.bubble_cli export

# Show current status
python -m src.bubble_cli status

# Show bubble analysis report
python -m src.bubble_cli report
```

## Data Export for Tableau

The system exports data in multiple CSV formats optimized for Tableau:

### 1. **articles_data.csv**
Main articles information with key metrics:
- `article_id`: Unique identifier
- `title`: Article title
- `url`: Article URL
- `analysis_date`: When analysis was performed
- `sentiment_score`: Sentiment score (-1 to +1)
- `overall_bubble_risk`: Overall bubble risk score (0 to 1)
- `market_impact`: Market impact assessment
- `key_phrases_count`: Number of key phrases identified

### 2. **indicators_data.csv**
Detailed bubble indicators for each article:
- All article fields plus:
- `indicator_name`: Name of the specific indicator
- `indicator_value`: Value of the indicator (0 to 1)
- `indicator_weight`: Importance weight of the indicator
- `indicator_trend`: Trend direction (increasing/decreasing/stable)
- `indicator_threshold`: Threshold for concern
- `is_concerning`: Boolean indicating if indicator exceeds threshold
- `indicator_description`: Human-readable description

### 3. **time_series_data.csv**
Time series data for trend analysis:
- `date`: Analysis date (YYYY-MM-DD)
- `article_id`: Article identifier
- `indicator_name`: Indicator name
- `indicator_value`: Indicator value
- `sentiment_score`: Sentiment score
- `bubble_risk`: Overall bubble risk
- `is_concerning`: Whether indicator is concerning

### 4. **summary_metrics.csv**
Key performance indicators for dashboard:
- `metric_name`: Name of the metric
- `metric_value`: Value of the metric
- `metric_type`: Type (count, score, text)
- `description`: Description of the metric

## Tableau Dashboard Setup

### 1. **Import Data**
1. Open Tableau Desktop
2. Connect to the CSV files in the `tableau_data` directory
3. Create relationships between the data sources using `article_id`

### 2. **Recommended Visualizations**

#### **Executive Summary Sheet**
- **KPI Cards**: Total Articles, Average Sentiment, Average Bubble Risk, Concerning Articles
- **Market Assessment**: Text display of overall market assessment
- **Risk Level Indicator**: Color-coded gauge based on average bubble risk

#### **Bubble Risk Analysis Sheet**
- **Bubble Risk by Article**: Bar chart showing bubble risk for each article
- **Risk Distribution**: Histogram of bubble risk scores
- **Risk Trend**: Line chart showing bubble risk over time

#### **Sentiment Analysis Sheet**
- **Sentiment Distribution**: Histogram of sentiment scores
- **Sentiment vs Bubble Risk**: Scatter plot showing correlation
- **Sentiment Trend**: Line chart showing sentiment over time

#### **Indicator Analysis Sheet**
- **Indicator Heatmap**: Heatmap showing all indicators by article
- **Indicator Trends**: Line charts for each indicator over time
- **Concerning Indicators**: Table highlighting concerning indicators

### 3. **Color Scheme**
- **Low Risk**: Green (#2E8B57)
- **Moderate Risk**: Yellow (#FFD700)
- **High Risk**: Red (#DC143C)
- **Positive Sentiment**: Blue (#4169E1)
- **Negative Sentiment**: Orange (#FF8C00)
- **Neutral Sentiment**: Gray (#808080)

## Usage Examples

### Basic Analysis Workflow
```bash
# 1. Search for latest AI news and analyze
python -m src.bubble_cli search-and-analyze

# 2. Check the analysis results
python -m src.bubble_cli report

# 3. Export data for Tableau
python -m src.bubble_cli export

# 4. Check status of tracked articles
python -m src.bubble_cli status
```

### Advanced Analysis
```bash
# Force re-analysis of all articles
python -m src.bubble_cli analyze --force

# Clean old articles (older than 7 days)
python -m src.bubble_cli clean --days 7

# Search with custom queries
python -m src.bubble_cli search-and-analyze --queries "AI startup valuations" "AI market crash" "AI investment bubble"
```

## Understanding the Analysis

### **Bubble Risk Levels**
- **0.0 - 0.3**: Low Risk (Green) - Normal market conditions
- **0.3 - 0.6**: Moderate Risk (Yellow) - Some concerning indicators
- **0.6 - 1.0**: High Risk (Red) - Multiple bubble indicators present

### **Sentiment Scores**
- **-1.0 to -0.3**: Negative/Pessimistic - Market concerns
- **-0.3 to +0.3**: Neutral - Balanced sentiment
- **+0.3 to +1.0**: Positive/Optimistic - Market optimism

### **Market Assessment Categories**
- **HIGH BUBBLE RISK**: Average bubble risk > 0.7
- **MODERATE BUBBLE RISK**: Average bubble risk 0.5-0.7
- **OPTIMISTIC MARKET**: High sentiment but few concerning indicators
- **PESSIMISTIC MARKET**: Low sentiment and market concerns
- **NEUTRAL MARKET**: Balanced market sentiment

## Integration with Existing Workflow

The bubble analysis functionality is seamlessly integrated into the existing LangGraph workflow:

1. **Search Phase**: Searches for AI news using Tavily API
2. **Summarization Phase**: Creates LinkedIn-optimized summaries
3. **News Tracking Phase**: Tracks top 5 articles for bubble analysis
4. **Bubble Analysis Phase**: Analyzes articles for bubble indicators
5. **Tableau Export Phase**: Exports data for dashboard creation
6. **Human Selection Phase**: Presents options for LinkedIn post creation
7. **Post Generation Phase**: Creates professional LinkedIn posts
8. **Verification Phase**: Verifies post accuracy

## Data Persistence

The system maintains persistent storage of:
- Tracked news articles with metadata
- Complete bubble analysis results
- Historical analysis data for trend tracking
- Export status and file locations

Data is stored in JSON format in `tracked_news.json` and can be easily backed up or migrated.

## Troubleshooting

### Common Issues

1. **No articles found**: Check your Tavily API key and internet connection
2. **Analysis errors**: Ensure OpenAI API key is valid and has sufficient credits
3. **Export failures**: Check file permissions in the output directory
4. **Missing data**: Run `python -m src.bubble_cli status` to check tracked articles

### Getting Help

- Check the status with `python -m src.bubble_cli status`
- View detailed reports with `python -m src.bubble_cli report`
- Clean old data with `python -m src.bubble_cli clean`

## Future Enhancements

- **Real-time monitoring**: Continuous news monitoring and analysis
- **Alert system**: Notifications when bubble risk exceeds thresholds
- **Historical analysis**: Long-term trend analysis and pattern recognition
- **Custom indicators**: User-defined bubble indicators
- **API integration**: REST API for external system integration
- **Machine learning**: Predictive models for bubble risk forecasting

---

*This bubble analysis system provides a comprehensive approach to monitoring AI market trends and identifying potential bubble indicators, helping you make informed decisions about AI investments and market timing.*
