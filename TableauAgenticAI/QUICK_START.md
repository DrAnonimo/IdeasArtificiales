# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Set API Keys
```bash
export OPENAI_API_KEY="your-openai-key"
export TAVILY_API_KEY="your-tavily-key"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Demo
```bash
python demo_longitudinal_analysis.py
```

### 4. View Results
```bash
python plot_dashboard.py
```

## 📊 Common Commands

### Full Workflow
```bash
python -m src.cli                    # Complete AI news workflow
```

### Bubble Analysis Only
```bash
python demo_longitudinal_analysis.py # Demo with 10 articles
python -m src.bubble_cli status      # Check current status
```

### Daily Collection
```bash
python daily_collection.py          # Collect today's data
python -m src.time_series_cli trends # View trends
```

### Visualization
```bash
python simple_dashboard.py          # HTML dashboard
python plot_dashboard.py            # PNG charts
```

## 🔧 Troubleshooting

### Fix Dependencies
```bash
pip uninstall openai httpx langchain-openai langchain-core
pip install openai==1.12.0 httpx==0.25.2 langchain-openai==0.1.0 langchain-core==0.1.0
```

### Check Status
```bash
python -c "
from src.news_tracker import NewsTracker
tracker = NewsTracker()
print(f'Articles: {len(tracker.tracked_news)}')
"
```

## 📁 Key Files

- `tracked_news.json` - Your 10 tracked articles
- `time_series_data/` - Historical data for trends
- `ai_bubble_dashboard.png` - Visual dashboard
- `requirements.txt` - Dependencies

## 🎯 What You Get

- **10 most relevant AI articles** tracked daily
- **5 bubble indicators** analyzed per article
- **Longitudinal trends** over time
- **Visual dashboards** for monitoring
- **Export data** for Grafana/Tableau
