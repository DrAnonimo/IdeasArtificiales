#!/usr/bin/env python3
"""
Test script for historical data collection
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from historical_data_collector import HistoricalDataCollector
from rich import print as rprint

def main():
    """Test historical data collection"""
    rprint("[bold cyan]🧪 Testing Historical Data Collection[/bold cyan]")
    rprint("=" * 60)
    
    # Initialize collector
    rprint("[blue]📊 Initializing historical data collector...[/blue]")
    collector = HistoricalDataCollector()
    rprint("✅ Collector initialized successfully")
    
    # Show current status
    rprint(f"📅 Current data points: {len(collector.historical_data)}")
    
    # Test with a small sample (1 day)
    rprint("\n[blue]🔄 Testing with 1 day of data...[/blue]")
    rprint("Note: This will make API calls to collect real data")
    
    try:
        results = collector.collect_historical_data(days=1, force_recollect=True)
        
        rprint(f"\n[green]✅ Collection Results:[/green]")
        rprint(f"📅 Days Collected: {len(results['collected_days'])}")
        rprint(f"❌ Failed Days: {len(results['failed_days'])}")
        rprint(f"📊 Success Rate: {results['success_rate']:.1%}")
        rprint(f"💾 Total Data Points: {results['data_points']}")
        
        if results['collected_days']:
            rprint(f"\n[green]✅ Successfully Collected:[/green]")
            for day in results['collected_days']:
                rprint(f"   📅 {day}")
        
        if results['failed_days']:
            rprint(f"\n[yellow]⚠️  Failed Days:[/yellow]")
            for day in results['failed_days']:
                rprint(f"   ❌ {day}")
        
        # Show summary
        rprint(f"\n[blue]📊 Historical Summary:[/blue]")
        summary = collector.get_historical_summary(days=1)
        
        if "error" not in summary:
            rprint(f"📅 Period: {summary['date_range']['start']} to {summary['date_range']['end']}")
            rprint(f"⚠️  Average Bubble Risk: {summary['average_bubble_risk']:.3f}")
            rprint(f"😊 Average Sentiment: {summary['average_sentiment']:.3f}")
            rprint(f"📈 Bubble Trend: {summary['bubble_trend']}")
            rprint(f"📈 Sentiment Trend: {summary['sentiment_trend']}")
            rprint(f"🚨 Concerning Days: {summary['concerning_days']}/{summary['period_days']}")
            rprint(f"🎯 Market Assessment: {summary['market_assessment']}")
        else:
            rprint(f"⚠️  Summary error: {summary['error']}")
        
        # Test export
        rprint(f"\n[blue]📤 Testing Export...[/blue]")
        export_results = collector.export_historical_data(format="csv")
        
        if "error" not in export_results:
            rprint(f"✅ CSV Export: {export_results['file_path']}")
            rprint(f"📊 Rows: {export_results['rows']}")
        else:
            rprint(f"❌ Export error: {export_results['error']}")
        
        rprint(f"\n[green]✅ Historical data collection test completed successfully![/green]")
        
    except Exception as e:
        rprint(f"[red]❌ Error during collection: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        rprint(f"\n[bold green]🎉 Test completed successfully![/bold green]")
        rprint("You can now run the full historical data collection:")
        rprint("  python backfill_historical_data.py")
    else:
        rprint(f"\n[bold red]❌ Test failed![/bold red]")
        sys.exit(1)
