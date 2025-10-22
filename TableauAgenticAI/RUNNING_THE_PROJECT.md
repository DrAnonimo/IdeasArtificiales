# How to Run the AI Bubble Analysis Project

## Prerequisites

### 1. Python Environment
- Python 3.8 or higher
- pip package manager

### 2. API Keys Required
You need to set up the following API keys:

#### OpenAI API Key
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

#### Tavily API Key
```bash
export TAVILY_API_KEY="your-tavily-api-key-here"
```

#### Alternative: Create a .env file
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your-openai-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here
```

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
python -c "import openai, tavily; print('✅ Dependencies installed successfully')"
```

## Running the Project

### Option 1: Full AI News Workflow (Original + Bubble Analysis)

#### Basic Run
```bash
python -m src.cli
```

This will:
- Search for AI news using 9 predefined queries
- Track the top 10 most relevant articles
- Analyze articles for bubble indicators
- Export data for Tableau and Grafana
- Collect daily snapshot for longitudinal analysis

#### Interactive Mode
```bash
python -m src.cli
```
Follow the prompts to select which news story to generate a LinkedIn post about.

### Option 2: Bubble Analysis Only

#### Run Bubble Analysis Demo
```bash
python demo_longitudinal_analysis.py
```

This will:
- Search for AI news
- Track and analyze 10 articles
- Collect daily snapshot
- Export data for Grafana
- Show trend analysis

#### Bubble Analysis CLI
```bash
# View current bubble analysis
python -m src.bubble_cli status

# Analyze specific articles
python -m src.bubble_cli analyze

# View bubble report
python -m src.bubble_cli report
```

### Option 3: Time Series Analysis

#### Daily Data Collection
```bash
python daily_collection.py
```

#### Time Series CLI
```bash
# Collect today's data
python -m src.time_series_cli collect-daily

# View trends
python -m src.time_series_cli trends --days 30

# View history
python -m src.time_series_cli history

# Export for Grafana
python -m src.time_series_cli export-grafana
```

### Option 4: Historical Data Analysis (NEW!)

#### Collect Historical Data (30 days)
```bash
python backfill_historical_data.py
```

#### Historical Data CLI
```bash
# Collect historical data
python -m src.historical_cli collect --days 30

# Show historical summary
python -m src.historical_cli summary --days 30

# Show historical trends
python -m src.historical_cli trends --days 30

# Check data quality
python -m src.historical_cli quality

# Export historical data
python -m src.historical_cli export --format csv
```

## Data Visualization

### Option 1: Simple HTML Dashboard
```bash
python simple_dashboard.py
```
This creates an HTML file with a basic dashboard.

### Option 2: Python Matplotlib Dashboard
```bash
python plot_dashboard.py
```
This creates a PNG image with comprehensive charts.

### Option 3: Grafana Dashboard
1. Install Grafana
2. Import the dashboard configuration from `time_series_data/grafana_dashboard.json`
3. Set up CSV data source
4. View the interactive dashboard

## Automated Daily Collection

### Using Cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/TableauAgenticAI && python daily_collection.py
```

### Using Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to daily
4. Set action to run: `python daily_collection.py`
5. Set working directory to project path

## Project Structure

```
TableauAgenticAI/
├── src/
│   ├── app.py                 # Main LangGraph workflow
│   ├── search.py              # News search functionality
│   ├── news_tracker.py        # Article tracking (top 10)
│   ├── bubble_analysis.py     # Bubble indicator analysis
│   ├── time_series_collector.py # Daily data collection
│   ├── tableau_export.py      # Tableau data export
│   ├── cli.py                 # Main CLI interface
│   ├── bubble_cli.py          # Bubble analysis CLI
│   └── time_series_cli.py     # Time series CLI
├── time_series_data/          # Generated data files
├── tracked_news.json          # Tracked articles database
├── requirements.txt           # Python dependencies
├── daily_collection.py        # Daily collection script
├── demo_longitudinal_analysis.py # Demo script
├── simple_dashboard.py        # HTML dashboard
├── plot_dashboard.py          # Matplotlib dashboard
└── grafana_dashboard.json     # Grafana configuration
```

## Troubleshooting

### Common Issues

#### 1. API Key Errors
```
RuntimeError: Configuration Error: OpenAI API key not found
```
**Solution**: Set your API keys as environment variables or in .env file

#### 2. Dependency Conflicts
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```
**Solution**: Run the manual fix:
```bash
pip uninstall openai httpx langchain-openai langchain-core
pip install openai==1.12.0 httpx==0.25.2 langchain-openai==0.1.0 langchain-core==0.1.0
```

#### 3. No Data Found
```
❌ No data found. Run: python demo_longitudinal_analysis.py
```
**Solution**: Run the demo script first to generate initial data

#### 4. Permission Errors
```
Permission denied: grafana.ini
```
**Solution**: Use alternative visualization methods (HTML or Matplotlib dashboards)

### Getting Help

#### Check Project Status
```bash
python -c "
from src.news_tracker import NewsTracker
from src.time_series_collector import TimeSeriesCollector

tracker = NewsTracker()
collector = TimeSeriesCollector()

print(f'📰 Articles tracked: {len(tracker.tracked_news)}')
print(f'📅 Snapshots collected: {len(collector.get_snapshots())}')
print('✅ Project is working correctly')
"
```

#### View Logs
```bash
# Check if there are any error logs
ls -la *.log

# View recent activity
tail -f tracked_news.json
```

## Quick Start Guide

1. **Set up API keys**:
   ```bash
   export OPENAI_API_KEY="your-key"
   export TAVILY_API_KEY="your-key"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the demo**:
   ```bash
   python demo_longitudinal_analysis.py
   ```

4. **View results**:
   ```bash
   python plot_dashboard.py
   ```

5. **Set up daily collection**:
   ```bash
   python daily_collection.py
   ```

## Expected Outputs

### After Running Demo
- `tracked_news.json` - 10 tracked articles with analysis
- `time_series_data/` - CSV files for Grafana
- `ai_bubble_dashboard.png` - Visual dashboard
- Console output showing bubble risk analysis

### Daily Collection
- Daily snapshots in `time_series_data/`
- Updated bubble risk trends
- Export files for visualization

## Next Steps

1. **Customize Search Queries**: Edit `src/search.py` to modify AI news search terms
2. **Adjust Bubble Indicators**: Modify `src/bubble_analysis.py` to change KPI weights
3. **Set up Monitoring**: Configure automated daily collection
4. **Create Alerts**: Set up notifications for high bubble risk levels
5. **Expand Analysis**: Add more data sources or analysis methods

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify API keys are correctly set
3. Ensure all dependencies are installed
4. Check the console output for specific error messages
5. Review the project structure to ensure files are in the correct locations
