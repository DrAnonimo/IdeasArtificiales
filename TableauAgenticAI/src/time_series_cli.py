#!/usr/bin/env python3
"""
CLI for Time Series Data Collection
Provides commands for daily data collection and Grafana export
"""

import argparse
import sys
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from .time_series_collector import TimeSeriesCollector


class TimeSeriesCLI:
    """Command-line interface for time series data collection"""
    
    def __init__(self):
        self.console = Console()
        self.collector = TimeSeriesCollector()

    def run(self):
        """Main CLI entry point"""
        parser = argparse.ArgumentParser(
            description="AI Bubble Analysis - Time Series Data Collection",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python -m src.time_series_cli collect-daily          # Collect today's data
  python -m src.time_series_cli export-grafana         # Export for Grafana
  python -m src.time_series_cli trends                 # Show trend analysis
  python -m src.time_series_cli status                 # Show collection status
  python -m src.time_series_cli history --days 30      # Show historical data
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Collect daily command
        collect_parser = subparsers.add_parser('collect-daily', help='Collect daily snapshot')
        collect_parser.add_argument('--force', action='store_true', help='Force re-analysis of all articles')
        
        # Export Grafana command
        export_parser = subparsers.add_parser('export-grafana', help='Export data for Grafana')
        export_parser.add_argument('--days', type=int, default=30, help='Number of days to export')
        
        # Trends command
        trends_parser = subparsers.add_parser('trends', help='Show trend analysis')
        trends_parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show collection status')
        
        # History command
        history_parser = subparsers.add_parser('history', help='Show historical data')
        history_parser.add_argument('--days', type=int, default=30, help='Number of days to show')
        
        # Clean command
        clean_parser = subparsers.add_parser('clean', help='Clean old data')
        clean_parser.add_argument('--days', type=int, default=90, help='Keep only last N days')
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        try:
            if args.command == 'collect-daily':
                self.collect_daily(args.force)
            elif args.command == 'export-grafana':
                self.export_grafana(args.days)
            elif args.command == 'trends':
                self.show_trends(args.days)
            elif args.command == 'status':
                self.show_status()
            elif args.command == 'history':
                self.show_history(args.days)
            elif args.command == 'clean':
                self.clean_old_data(args.days)
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")
            return 1

    def collect_daily(self, force: bool = False):
        """Collect daily snapshot"""
        self.console.print("[bold blue]📊 Collecting daily snapshot...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Collecting data...", total=None)
            
            snapshot = self.collector.collect_daily_snapshot(force_reanalyze=force)
            
            progress.update(task, description="Saving snapshot...")
        
        # Show results
        self.console.print(f"[green]✅ Daily snapshot collected![/green]")
        self.console.print(f"📅 Date: {snapshot.date}")
        self.console.print(f"📊 Market Assessment: {snapshot.market_assessment}")
        self.console.print(f"⚠️  Bubble Risk: {snapshot.average_bubble_risk:.3f}")
        self.console.print(f"😊 Sentiment: {snapshot.average_sentiment:.3f}")
        self.console.print(f"🚨 Concerning Articles: {snapshot.concerning_articles}")

    def export_grafana(self, days: int):
        """Export data for Grafana"""
        self.console.print(f"[bold blue]📊 Exporting {days} days of data for Grafana...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Exporting data...", total=None)
            
            result = self.collector.export_for_grafana(days)
            
            progress.update(task, description="Creating dashboard config...")
        
        if 'error' in result:
            self.console.print(f"[red]❌ Export failed: {result['error']}[/red]")
            return
        
        self.console.print(f"[green]✅ Export completed![/green]")
        self.console.print(f"📁 Time Series CSV: {result['time_series_csv']}")
        self.console.print(f"📁 Dashboard Config: {result['dashboard_config']}")
        self.console.print(f"📁 Setup Instructions: {result['setup_instructions']}")
        self.console.print(f"📊 Data Points: {result['data_points']}")
        self.console.print(f"📅 Date Range: {result['date_range']}")

    def show_trends(self, days: int):
        """Show trend analysis"""
        self.console.print(f"[bold blue]📈 Analyzing trends over {days} days...[/bold blue]")
        
        trends = self.collector.calculate_trends(days)
        
        if 'error' in trends:
            self.console.print(f"[red]❌ {trends['error']}[/red]")
            return
        
        # Create trends table
        table = Table(title=f"📈 Trend Analysis ({trends['date_range']['start']} to {trends['date_range']['end']})")
        table.add_column("Metric", style="cyan")
        table.add_column("Direction", style="green")
        table.add_column("Change %", style="yellow")
        table.add_column("Start Value", style="blue")
        table.add_column("End Value", style="blue")
        
        # Add trend data
        for metric, trend_data in trends['trends'].items():
            direction_icon = "📈" if trend_data['direction'] == "increasing" else "📉" if trend_data['direction'] == "decreasing" else "➡️"
            table.add_row(
                metric.replace('_', ' ').title(),
                f"{direction_icon} {trend_data['direction']}",
                f"{trend_data['change_percent']:.1f}%",
                f"{trend_data['start_value']:.3f}",
                f"{trend_data['end_value']:.3f}"
            )
        
        self.console.print(table)
        
        # Show indicator trends
        if trends['indicator_trends']:
            self.console.print("\n[bold]📊 Indicator Trends:[/bold]")
            for indicator, trend_data in trends['indicator_trends'].items():
                direction_icon = "📈" if trend_data['direction'] == "increasing" else "📉" if trend_data['direction'] == "decreasing" else "➡️"
                self.console.print(f"  {direction_icon} {indicator.replace('_', ' ').title()}: {trend_data['change_percent']:.1f}% change")
        
        # Show risk level change
        risk_change = trends['risk_level_change']
        if risk_change['change'] != 'insufficient_data':
            change_icon = "🔴" if risk_change['change'] == "increased" else "🟢" if risk_change['change'] == "decreased" else "🟡"
            self.console.print(f"\n{change_icon} Risk Level: {risk_change['start_level']} → {risk_change['end_level']} ({risk_change['change']})")
        
        # Show volatility
        volatility = trends['volatility']['bubble_risk']
        self.console.print(f"\n📊 Bubble Risk Volatility: {volatility:.3f}")

    def show_status(self):
        """Show collection status"""
        status = self.collector.get_status()
        
        # Create status table
        table = Table(title="📊 Time Series Collection Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Snapshots", str(status['total_snapshots']))
        table.add_row("Latest Snapshot", status['latest_snapshot'] or "None")
        table.add_row("Data Directory", status['data_directory'])
        table.add_row("Last Updated", status['last_updated'])
        
        self.console.print(table)
        
        # Show recent snapshots
        if status['total_snapshots'] > 0:
            recent = self.collector.get_latest_snapshots(7)
            self.console.print(f"\n[bold]📅 Recent Snapshots (Last 7 days):[/bold]")
            
            for snapshot in recent:
                risk_color = "red" if snapshot.average_bubble_risk > 0.7 else "yellow" if snapshot.average_bubble_risk > 0.4 else "green"
                self.console.print(f"  📅 {snapshot.date}: [{risk_color}]{snapshot.market_assessment}[/{risk_color}] (Risk: {snapshot.average_bubble_risk:.3f})")

    def show_history(self, days: int):
        """Show historical data"""
        snapshots = self.collector.get_latest_snapshots(days)
        
        if not snapshots:
            self.console.print(f"[yellow]⚠️  No data available for the last {days} days[/yellow]")
            return
        
        # Create history table
        table = Table(title=f"📅 Historical Data (Last {days} days)")
        table.add_column("Date", style="cyan")
        table.add_column("Risk", style="red")
        table.add_column("Sentiment", style="blue")
        table.add_column("Concerning", style="yellow")
        table.add_column("Assessment", style="green")
        
        for snapshot in snapshots:
            risk_color = "red" if snapshot.average_bubble_risk > 0.7 else "yellow" if snapshot.average_bubble_risk > 0.4 else "green"
            table.add_row(
                snapshot.date,
                f"[{risk_color}]{snapshot.average_bubble_risk:.3f}[/{risk_color}]",
                f"{snapshot.average_sentiment:.3f}",
                str(snapshot.concerning_articles),
                snapshot.market_assessment
            )
        
        self.console.print(table)

    def clean_old_data(self, days: int):
        """Clean old data"""
        self.console.print(f"[bold blue]🧹 Cleaning data older than {days} days...[/bold blue]")
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        initial_count = len(self.collector.snapshots)
        self.collector.snapshots = [
            s for s in self.collector.snapshots 
            if s.date >= cutoff_str
        ]
        removed_count = initial_count - len(self.collector.snapshots)
        
        if removed_count > 0:
            self.collector.save_snapshots()
            self.console.print(f"[green]✅ Removed {removed_count} old snapshots[/green]")
        else:
            self.console.print(f"[yellow]ℹ️  No old data to remove[/yellow]")


def main():
    """Main entry point"""
    cli = TimeSeriesCLI()
    cli.run()


if __name__ == "__main__":
    main()
