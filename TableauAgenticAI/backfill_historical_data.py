#!/usr/bin/env python3
"""
Backfill Historical Data Script

This script collects historical data from the past 30 days to provide
better context for bubble prediction and trend analysis.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from historical_data_collector import HistoricalDataCollector
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

def main():
    """Main backfill function"""
    rprint("[bold cyan]🕰️  AI Bubble Analysis - Historical Data Backfill[/bold cyan]")
    rprint("=" * 70)
    rprint("This script will collect historical data from the past 30 days")
    rprint("to provide better context for bubble prediction and trend analysis.")
    rprint()
    
    # Check if API keys are set
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        rprint("[bold red]❌ API keys not found![/bold red]")
        rprint("Please set your API keys:")
        rprint("  export OPENAI_API_KEY='your-openai-key'")
        rprint("  export TAVILY_API_KEY='your-tavily-key'")
        rprint()
        rprint("Or create a .env file with:")
        rprint("  OPENAI_API_KEY=your-openai-key")
        rprint("  TAVILY_API_KEY=your-tavily-key")
        return False
    
    # Initialize collector
    rprint("[bold blue]📊 Initializing historical data collector...[/bold blue]")
    collector = HistoricalDataCollector()
    
    # Show current status
    existing_data = len(collector.historical_data)
    rprint(f"📅 Existing data points: {existing_data}")
    
    if existing_data > 0:
        latest_date = collector.historical_data[-1].date
        rprint(f"📅 Latest data: {latest_date}")
    
    rprint()
    
    # Collect historical data
    rprint("[bold blue]🔄 Starting historical data collection...[/bold blue]")
    rprint("This may take several minutes due to API rate limiting.")
    rprint()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Collecting historical data...", total=30)
            
            # Collect data for 30 days
            results = collector.collect_historical_data(days=30, force_recollect=False)
            
            # Update progress
            progress.update(task, completed=len(results['collected_days']))
        
        # Display results
        rprint()
        rprint("[bold green]✅ Historical Data Collection Complete![/bold green]")
        rprint("=" * 50)
        rprint(f"📅 Days Collected: {len(results['collected_days'])}")
        rprint(f"❌ Failed Days: {len(results['failed_days'])}")
        rprint(f"📊 Success Rate: {results['success_rate']:.1%}")
        rprint(f"💾 Total Data Points: {results['data_points']}")
        
        if results['collected_days']:
            rprint(f"\n[bold green]✅ Successfully Collected:[/bold green]")
            for day in results['collected_days'][-5:]:  # Show last 5 days
                rprint(f"   📅 {day}")
            if len(results['collected_days']) > 5:
                rprint(f"   ... and {len(results['collected_days']) - 5} more days")
        
        if results['failed_days']:
            rprint(f"\n[bold yellow]⚠️  Failed Days:[/bold yellow]")
            for day in results['failed_days']:
                rprint(f"   ❌ {day}")
        
        # Show summary
        rprint(f"\n[bold blue]📊 Historical Data Summary:[/bold blue]")
        summary = collector.get_historical_summary(days=30)
        
        if "error" not in summary:
            rprint(f"📅 Period: {summary['date_range']['start']} to {summary['date_range']['end']}")
            rprint(f"⚠️  Average Bubble Risk: {summary['average_bubble_risk']:.3f}")
            rprint(f"😊 Average Sentiment: {summary['average_sentiment']:.3f}")
            rprint(f"📈 Bubble Trend: {summary['bubble_trend']}")
            rprint(f"📈 Sentiment Trend: {summary['sentiment_trend']}")
            rprint(f"🚨 Concerning Days: {summary['concerning_days']}/{summary['period_days']}")
            rprint(f"🎯 Market Assessment: {summary['market_assessment']}")
        
        # Export data
        rprint(f"\n[bold blue]📤 Exporting data...[/bold blue]")
        export_results = collector.export_historical_data(format="csv")
        
        if "error" not in export_results:
            rprint(f"✅ CSV Export: {export_results['file_path']}")
            rprint(f"📊 Rows: {export_results['rows']}")
        
        # Show next steps
        rprint(f"\n[bold cyan]🚀 Next Steps:[/bold cyan]")
        rprint("1. View trends: python -m src.historical_cli trends")
        rprint("2. Show summary: python -m src.historical_cli summary")
        rprint("3. Check quality: python -m src.historical_cli quality")
        rprint("4. Run daily collection: python daily_collection.py")
        rprint("5. View dashboard: python plot_dashboard.py")
        
        return True
        
    except KeyboardInterrupt:
        rprint("\n[bold yellow]⚠️  Collection cancelled by user[/bold yellow]")
        return False
    except Exception as e:
        rprint(f"\n[bold red]❌ Error during collection: {e}[/bold red]")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
