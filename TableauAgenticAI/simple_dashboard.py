#!/usr/bin/env python3
"""
Simple Web Dashboard for AI Bubble Analysis
Creates an HTML dashboard that can be opened in any browser
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

def create_html_dashboard():
    """Create an HTML dashboard for the AI bubble analysis data"""
    
    # Read the time series data
    csv_file = Path("time_series_data/grafana_time_series_30d.csv")
    if not csv_file.exists():
        print("❌ No data file found. Run the demo first: python demo_longitudinal_analysis.py")
        return
    
    df = pd.read_csv(csv_file)
    
    # Get the latest data
    latest_data = df[df['metric_type'] == 'summary'].iloc[-1] if len(df) > 0 else None
    
    if latest_data is None:
        print("❌ No summary data found")
        return
    
    # Create HTML dashboard
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Bubble Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
            margin: 10px 0;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .risk-low {{ color: #4ade80; }}
        .risk-moderate {{ color: #fbbf24; }}
        .risk-high {{ color: #f87171; }}
        .sentiment-positive {{ color: #60a5fa; }}
        .sentiment-negative {{ color: #f87171; }}
        .sentiment-neutral {{ color: #a78bfa; }}
        .charts-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .chart-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        .chart-title {{
            font-size: 1.3em;
            margin-bottom: 15px;
            text-align: center;
        }}
        .data-table {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            color: white;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        th {{
            background: rgba(255, 255, 255, 0.1);
            font-weight: bold;
        }}
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .status-online {{ background: #4ade80; }}
        .status-warning {{ background: #fbbf24; }}
        .status-offline {{ background: #f87171; }}
        .refresh-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px;
            transition: all 0.3s ease;
        }}
        .refresh-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AI Bubble Analysis Dashboard</h1>
            <p>Real-time monitoring of AI market trends and bubble indicators</p>
            <p>Last Updated: {latest_data['date']} at {latest_data['timestamp'].split('T')[1][:8]}</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Bubble Risk Score</div>
                <div class="metric-value {'risk-high' if latest_data['average_bubble_risk'] > 0.7 else 'risk-moderate' if latest_data['average_bubble_risk'] > 0.4 else 'risk-low'}">
                    {latest_data['average_bubble_risk']:.3f}
                </div>
                <div class="metric-label">
                    {'🔴 HIGH RISK' if latest_data['average_bubble_risk'] > 0.7 else '🟡 MODERATE RISK' if latest_data['average_bubble_risk'] > 0.4 else '🟢 LOW RISK'}
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Market Sentiment</div>
                <div class="metric-value {'sentiment-positive' if latest_data['average_sentiment'] > 0.3 else 'sentiment-negative' if latest_data['average_sentiment'] < -0.3 else 'sentiment-neutral'}">
                    {latest_data['average_sentiment']:.3f}
                </div>
                <div class="metric-label">
                    {'😊 Positive' if latest_data['average_sentiment'] > 0.3 else '😟 Negative' if latest_data['average_sentiment'] < -0.3 else '😐 Neutral'}
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Concerning Articles</div>
                <div class="metric-value {'risk-high' if latest_data['concerning_articles'] > 3 else 'risk-moderate' if latest_data['concerning_articles'] > 1 else 'risk-low'}">
                    {int(latest_data['concerning_articles'])}
                </div>
                <div class="metric-label">out of {int(latest_data['total_articles'])} articles</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Market Assessment</div>
                <div class="metric-value" style="font-size: 1.5em;">
                    {latest_data['market_assessment']}
                </div>
                <div class="metric-label">
                    <span class="status-indicator {'status-online' if 'LOW' in latest_data['market_assessment'] else 'status-warning' if 'MODERATE' in latest_data['market_assessment'] else 'status-offline'}"></span>
                    Current Status
                </div>
            </div>
        </div>

        <div class="charts-container">
            <div class="chart-card">
                <div class="chart-title">📊 Bubble Indicators</div>
                <canvas id="indicatorsChart" width="400" height="300"></canvas>
            </div>

            <div class="chart-card">
                <div class="chart-title">📈 Risk vs Sentiment</div>
                <canvas id="scatterChart" width="400" height="300"></canvas>
            </div>
        </div>

        <div class="data-table">
            <h3>📋 Detailed Analysis Data</h3>
            <table>
                <thead>
                    <tr>
                        <th>Indicator</th>
                        <th>Value</th>
                        <th>Status</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {create_indicator_rows(df)}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Bubble Indicators Chart
        const indicatorsData = {get_indicators_data(df)};
        const indicatorsCtx = document.getElementById('indicatorsChart').getContext('2d');
        new Chart(indicatorsCtx, {{
            type: 'bar',
            data: {{
                labels: indicatorsData.labels,
                datasets: [{{
                    label: 'Indicator Values',
                    data: indicatorsData.values,
                    backgroundColor: indicatorsData.colors,
                    borderColor: indicatorsData.borderColors,
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: 'white'
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 1,
                        ticks: {{
                            color: 'white'
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.2)'
                        }}
                    }},
                    x: {{
                        ticks: {{
                            color: 'white'
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.2)'
                        }}
                    }}
                }}
            }}
        }});

        // Risk vs Sentiment Scatter Chart
        const scatterData = {get_scatter_data(df)};
        const scatterCtx = document.getElementById('scatterChart').getContext('2d');
        new Chart(scatterCtx, {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Risk vs Sentiment',
                    data: scatterData,
                    backgroundColor: 'rgba(99, 102, 241, 0.6)',
                    borderColor: 'rgba(99, 102, 241, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: 'white'
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: 'Sentiment Score',
                            color: 'white'
                        }},
                        ticks: {{
                            color: 'white'
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.2)'
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Bubble Risk',
                            color: 'white'
                        }},
                        ticks: {{
                            color: 'white'
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.2)'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    return html_content

def create_indicator_rows(df):
    """Create table rows for indicators"""
    indicator_data = df[df['metric_type'] == 'indicator']
    rows = []
    
    for _, row in indicator_data.iterrows():
        status = "🔴 Concerning" if row['indicator_value'] > 0.6 else "🟡 Moderate" if row['indicator_value'] > 0.3 else "🟢 Normal"
        rows.append(f"""
            <tr>
                <td>{row['indicator_name'].replace('_', ' ').title()}</td>
                <td>{row['indicator_value']:.3f}</td>
                <td>{status}</td>
                <td>{get_indicator_description(row['indicator_name'])}</td>
            </tr>
        """)
    
    return ''.join(rows)

def get_indicator_description(indicator_name):
    """Get description for indicator"""
    descriptions = {
        'hype_level': 'Level of hype and superlative language in articles',
        'investment_frenzy': 'Intensity of investment and funding discussions',
        'market_speculation': 'Level of market speculation and future predictions',
        'competitive_intensity': 'Intensity of competitive dynamics mentioned',
        'regulatory_concern': 'Level of regulatory concerns and risks mentioned'
    }
    return descriptions.get(indicator_name, 'Unknown indicator')

def get_indicators_data(df):
    """Get data for indicators chart"""
    indicator_data = df[df['metric_type'] == 'indicator']
    
    labels = [row['indicator_name'].replace('_', ' ').title() for _, row in indicator_data.iterrows()]
    values = [row['indicator_value'] for _, row in indicator_data.iterrows()]
    
    colors = []
    border_colors = []
    for value in values:
        if value > 0.6:
            colors.append('rgba(248, 113, 113, 0.6)')  # Red
            border_colors.append('rgba(248, 113, 113, 1)')
        elif value > 0.3:
            colors.append('rgba(251, 191, 36, 0.6)')   # Yellow
            border_colors.append('rgba(251, 191, 36, 1)')
        else:
            colors.append('rgba(74, 222, 128, 0.6)')   # Green
            border_colors.append('rgba(74, 222, 128, 1)')
    
    return {
        'labels': labels,
        'values': values,
        'colors': colors,
        'borderColors': border_colors
    }

def get_scatter_data(df):
    """Get data for scatter chart"""
    summary_data = df[df['metric_type'] == 'summary']
    return [{'x': row['average_sentiment'], 'y': row['average_bubble_risk']} for _, row in summary_data.iterrows()]

def start_web_server():
    """Start a simple web server to serve the dashboard"""
    class CustomHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(Path.cwd()), **kwargs)
    
    port = 8080
    server = HTTPServer(('localhost', port), CustomHandler)
    
    print(f"🌐 Starting web server on http://localhost:{port}")
    print(f"📊 Dashboard will be available at http://localhost:{port}/dashboard.html")
    print("Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

def main():
    """Main function"""
    print("🚀 Creating AI Bubble Analysis Dashboard...")
    
    # Create the HTML dashboard
    html_content = create_html_dashboard()
    
    # Save the dashboard
    dashboard_file = Path("dashboard.html")
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard created: {dashboard_file.absolute()}")
    print("🌐 Opening dashboard in your browser...")
    
    # Open in browser
    webbrowser.open(f"file://{dashboard_file.absolute()}")
    
    # Ask if user wants to start web server
    response = input("\n🤔 Would you like to start a web server for better functionality? (y/n): ")
    if response.lower() in ['y', 'yes']:
        start_web_server()
    else:
        print("📊 Dashboard is ready! Open dashboard.html in your browser to view it.")

if __name__ == "__main__":
    main()
