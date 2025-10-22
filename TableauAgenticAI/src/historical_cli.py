"""
CLI interface for historical data collection and analysis
"""

import argparse
import sys
from datetime import datetime, timedelta
from rich import print as rprint
from rich.table import Table
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .historical_data_collector import HistoricalDataCollector

console = Console()

def collect_historical_data(days: int = 30, force: bool = False):
    """Collect historical data for the specified number of days"""
    rprint(f"[bold cyan]🕰️  Collecting Historical Data for {days} Days[/bold cyan]")
    rprint("=" * 60)
    
    collector = HistoricalDataCollector()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Collecting historical data...", total=None)
        
        try:
            results = collector.collect_historical_data(days=days, force_recollect=force)
            
            # Display results
            rprint(f"\n[bold green]✅ Historical Data Collection Complete![/bold green]")
            rprint(f"📅 Days Collected: {len(results['collected_days'])}")
            rprint(f"❌ Failed Days: {len(results['failed_days'])}")
            rprint(f"📊 Success Rate: {results['success_rate']:.1%}")
            rprint(f"💾 Total Data Points: {results['data_points']}")
            
            if results['failed_days']:
                rprint(f"\n[bold yellow]⚠️  Failed Days:[/bold yellow]")
                for day in results['failed_days']:
                    rprint(f"   - {day}")
            
        except Exception as e:
            rprint(f"[bold red]❌ Error collecting historical data: {e}[/bold red]")
            return False
    
    return True

def show_historical_summary(days: int = 30):
    """Show summary of historical data"""
    rprint(f"[bold cyan]📊 Historical Data Summary ({days} days)[/bold cyan]")
    rprint("=" * 60)
    
    collector = HistoricalDataCollector()
    summary = collector.get_historical_summary(days=days)
    
    if "error" in summary:
        rprint(f"[bold red]❌ {summary['error']}[/bold red]")
        return
    
    # Display summary
    rprint(f"📅 Period: {summary['date_range']['start']} to {summary['date_range']['end']}")
    rprint(f"📊 Data Points: {summary['period_days']}")
    rprint(f"⚠️  Average Bubble Risk: {summary['average_bubble_risk']:.3f}")
    rprint(f"😊 Average Sentiment: {summary['average_sentiment']:.3f}")
    rprint(f"📈 Bubble Trend: {summary['bubble_trend']}")
    rprint(f"📈 Sentiment Trend: {summary['sentiment_trend']}")
    rprint(f"🚨 Concerning Days: {summary['concerning_days']}/{summary['period_days']}")
    rprint(f"🎯 Market Assessment: {summary['market_assessment']}")
    
    # Data quality distribution
    rprint(f"\n[bold]📋 Data Quality Distribution:[/bold]")
    for quality, count in summary['data_quality_distribution'].items():
        emoji = "✅" if quality == "complete" else "⚠️" if quality == "partial" else "❌"
        rprint(f"   {emoji} {quality.title()}: {count} days")

def show_historical_trends(days: int = 30):
    """Show historical trends in a table format"""
    rprint(f"[bold cyan]📈 Historical Trends ({days} days)[/bold cyan]")
    rprint("=" * 60)
    
    collector = HistoricalDataCollector()
    
    # Get recent data points
    recent_data = collector.historical_data[-days:] if len(collector.historical_data) >= days else collector.historical_data
    
    if not recent_data:
        rprint("[bold red]❌ No historical data available[/bold red]")
        return
    
    # Create trends table
    table = Table(title="Historical Trends")
    table.add_column("Date", style="cyan")
    table.add_column("Articles", justify="right")
    table.add_column("Bubble Risk", justify="right")
    table.add_column("Sentiment", justify="right")
    table.add_column("Assessment", style="yellow")
    table.add_column("Quality", style="green")
    
    for point in recent_data[-10:]:  # Show last 10 days
        bubble_risk = point.bubble_analysis.get("average_bubble_risk", 0)
        sentiment = point.sentiment_summary.get("average_sentiment", 0)
        assessment = point.bubble_analysis.get("market_assessment", "Unknown")
        quality = point.data_quality
        
        # Color coding for bubble risk
        risk_color = "red" if bubble_risk > 0.6 else "yellow" if bubble_risk > 0.3 else "green"
        
        table.add_row(
            point.date,
            str(len(point.articles)),
            f"[{risk_color}]{bubble_risk:.3f}[/{risk_color}]",
            f"{sentiment:.3f}",
            assessment,
            quality
        )
    
    console.print(table)

def export_historical_data(format: str = "csv"):
    """Export historical data"""
    rprint(f"[bold cyan]📤 Exporting Historical Data ({format.upper()})[/bold cyan]")
    rprint("=" * 60)
    
    collector = HistoricalDataCollector()
    results = collector.export_historical_data(format=format)
    
    if "error" in results:
        rprint(f"[bold red]❌ {results['error']}[/bold red]")
        return
    
    rprint(f"[bold green]✅ Export successful![/bold green]")
    rprint(f"📁 File: {results['file_path']}")
    if "rows" in results:
        rprint(f"📊 Rows: {results['rows']}")
    if "data_points" in results:
        rprint(f"📊 Data Points: {results['data_points']}")

def show_data_quality_report():
    """Show detailed data quality report"""
    rprint(f"[bold cyan]🔍 Data Quality Report[/bold cyan]")
    rprint("=" * 60)
    
    collector = HistoricalDataCollector()
    
    if not collector.historical_data:
        rprint("[bold red]❌ No historical data available[/bold red]")
        return
    
    # Analyze data quality
    total_days = len(collector.historical_data)
    complete_days = sum(1 for point in collector.historical_data if point.data_quality == "complete")
    partial_days = sum(1 for point in collector.historical_data if point.data_quality == "partial")
    incomplete_days = sum(1 for point in collector.historical_data if point.data_quality == "incomplete")
    
    rprint(f"📊 Total Days: {total_days}")
    rprint(f"✅ Complete: {complete_days} ({complete_days/total_days:.1%})")
    rprint(f"⚠️  Partial: {partial_days} ({partial_days/total_days:.1%})")
    rprint(f"❌ Incomplete: {incomplete_days} ({incomplete_days/total_days:.1%})")
    
    # Show recent data quality
    rprint(f"\n[bold]📋 Recent Data Quality (Last 7 days):[/bold]")
    recent_data = collector.historical_data[-7:]
    for point in recent_data:
        quality_emoji = "✅" if point.data_quality == "complete" else "⚠️" if point.data_quality == "partial" else "❌"
        rprint(f"   {quality_emoji} {point.date}: {point.data_quality} ({len(point.articles)} articles)")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Historical Data Collection CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Collect historical data")
    collect_parser.add_argument("--days", type=int, default=30, help="Number of days to collect (default: 30)")
    collect_parser.add_argument("--force", action="store_true", help="Force recollect existing data")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show historical data summary")
    summary_parser.add_argument("--days", type=int, default=30, help="Number of days to analyze (default: 30)")
    
    # Trends command
    trends_parser = subparsers.add_parser("trends", help="Show historical trends")
    trends_parser.add_argument("--days", type=int, default=30, help="Number of days to show (default: 30)")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export historical data")
    export_parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Export format (default: csv)")
    
    # Quality command
    quality_parser = subparsers.add_parser("quality", help="Show data quality report")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "collect":
            collect_historical_data(days=args.days, force=args.force)
        elif args.command == "summary":
            show_historical_summary(days=args.days)
        elif args.command == "trends":
            show_historical_trends(days=args.days)
        elif args.command == "export":
            export_historical_data(format=args.format)
        elif args.command == "quality":
            show_data_quality_report()
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        rprint("\n[bold yellow]⚠️  Operation cancelled by user[/bold yellow]")
    except Exception as e:
        rprint(f"[bold red]❌ Unexpected error: {e}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
