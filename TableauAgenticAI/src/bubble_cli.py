#!/usr/bin/env python3
"""
CLI for AI Bubble Analysis Dashboard
Provides commands for managing news tracking, bubble analysis, and Tableau export
"""

import argparse
import json
from datetime import datetime
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from .news_tracker import NewsTracker
from .bubble_analysis import AIBubbleAnalyzer
from .tableau_export import TableauExporter
from .search import search_ai_news


class BubbleAnalysisCLI:
    """Command-line interface for AI bubble analysis"""
    
    def __init__(self):
        self.console = Console()
        self.tracker = NewsTracker()
        self.analyzer = AIBubbleAnalyzer()
        self.exporter = TableauExporter()

    def run(self):
        """Main CLI entry point"""
        parser = argparse.ArgumentParser(
            description="AI Bubble Analysis Dashboard CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python -m src.bubble_cli search-and-analyze    # Search for news and analyze
  python -m src.bubble_cli analyze               # Analyze existing tracked news
  python -m src.bubble_cli export                # Export data for Tableau
  python -m src.bubble_cli status                # Show current status
  python -m src.bubble_cli report                # Show bubble analysis report
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Search and analyze command
        search_parser = subparsers.add_parser('search-and-analyze', help='Search for AI news and analyze for bubble indicators')
        search_parser.add_argument('--queries', nargs='+', 
                                 default=["AI bubble 2024", "AI market speculation", "AI investment frenzy", 
                                         "AI startup valuations", "AI industry hype"],
                                 help='Search queries to use')
        
        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze existing tracked news for bubble indicators')
        analyze_parser.add_argument('--force', action='store_true', help='Force re-analysis of all articles')
        
        # Export command
        export_parser = subparsers.add_parser('export', help='Export data for Tableau dashboard')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show current status of tracked news')
        
        # Report command
        report_parser = subparsers.add_parser('report', help='Show bubble analysis report')
        
        # Clean command
        clean_parser = subparsers.add_parser('clean', help='Clean old articles')
        clean_parser.add_argument('--days', type=int, default=7, help='Remove articles older than N days')
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        try:
            if args.command == 'search-and-analyze':
                self.search_and_analyze(args.queries)
            elif args.command == 'analyze':
                self.analyze_news(args.force)
            elif args.command == 'export':
                self.export_data()
            elif args.command == 'status':
                self.show_status()
            elif args.command == 'report':
                self.show_report()
            elif args.command == 'clean':
                self.clean_old_articles(args.days)
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")
            return 1

    def search_and_analyze(self, queries: List[str]):
        """Search for news and analyze for bubble indicators"""
        self.console.print("[bold blue]🔍 Searching for AI news...[/bold blue]")
        
        # Search for news
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Searching news...", total=None)
            
            # Simulate search process
            search_state = {"queries": queries}
            search_results = search_ai_news(search_state)
            
            progress.update(task, description="Adding articles to tracker...")
            tracking_result = self.tracker.add_news_articles(search_results["results"])
            
            progress.update(task, description="Analyzing for bubble indicators...")
            analysis_result = self.tracker.analyze_news()
            
            progress.update(task, description="Exporting data for Tableau...")
            export_result = self.exporter.export_all_data()
        
        # Show results
        self.console.print(f"[green]✅ Analysis complete![/green]")
        self.console.print(f"📊 Added {tracking_result['added_articles']} new articles")
        self.console.print(f"🔍 Analyzed {analysis_result['analyzed_count']} articles")
        self.console.print(f"📈 Data exported to Tableau format")
        
        # Show quick summary
        self.show_quick_summary()

    def analyze_news(self, force: bool = False):
        """Analyze existing tracked news"""
        self.console.print("[bold blue]🔍 Analyzing tracked news...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing articles...", total=None)
            
            analysis_result = self.tracker.analyze_news(force_reanalyze=force)
            
            progress.update(task, description="Exporting data...")
            export_result = self.exporter.export_all_data()
        
        self.console.print(f"[green]✅ Analysis complete![/green]")
        self.console.print(f"🔍 Analyzed {analysis_result['analyzed_count']} articles")
        
        self.show_quick_summary()

    def export_data(self):
        """Export data for Tableau"""
        self.console.print("[bold blue]📊 Exporting data for Tableau...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Exporting data...", total=None)
            
            export_result = self.exporter.export_all_data()
        
        self.console.print(f"[green]✅ Export complete![/green]")
        
        # Show export status
        status = self.exporter.get_export_status()
        self.console.print(f"📁 Output directory: {status['output_directory']}")
        self.console.print(f"📄 Files created: {', '.join(status['files_created'])}")

    def show_status(self):
        """Show current status"""
        status = self.tracker.get_status()
        
        # Create status table
        table = Table(title="📊 News Tracker Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Articles", str(status['total_articles']))
        table.add_row("Analyzed Articles", str(status['analyzed_articles']))
        table.add_row("Pending Analysis", str(status['pending_analysis']))
        table.add_row("Data File", status['data_file'])
        table.add_row("Last Updated", status['last_updated'])
        
        self.console.print(table)
        
        # Show article summary
        if status['total_articles'] > 0:
            self.console.print("\n[bold]📰 Tracked Articles:[/bold]")
            articles = self.tracker.get_article_summary()
            
            for i, article in enumerate(articles[:5], 1):  # Show top 5
                status_icon = "✅" if article['is_analyzed'] else "⏳"
                risk_level = ""
                if article.get('bubble_risk'):
                    if article['bubble_risk'] > 0.7:
                        risk_level = "🔴 High Risk"
                    elif article['bubble_risk'] > 0.4:
                        risk_level = "🟡 Moderate Risk"
                    else:
                        risk_level = "🟢 Low Risk"
                
                self.console.print(f"{i}. {status_icon} {article['title'][:80]}...")
                if risk_level:
                    self.console.print(f"   {risk_level} (Risk: {article.get('bubble_risk', 'N/A'):.2f})")

    def show_report(self):
        """Show bubble analysis report"""
        report = self.tracker.get_bubble_report()
        
        if 'error' in report:
            self.console.print(f"[red]❌ {report['error']}[/red]")
            return
        
        # Create report panel
        report_text = f"""
📊 [bold]Bubble Analysis Report[/bold]

📈 [bold]Market Assessment:[/bold] {report['market_assessment']}
📰 [bold]Total Articles:[/bold] {report['total_articles']}
😊 [bold]Average Sentiment:[/bold] {report['average_sentiment']:.3f}
⚠️  [bold]Average Bubble Risk:[/bold] {report['average_bubble_risk']:.3f}
🚨 [bold]Concerning Articles:[/bold] {report['concerning_articles']}

📊 [bold]Indicator Averages:[/bold]
"""
        
        for indicator, value in report['indicator_averages'].items():
            indicator_name = indicator.replace('_', ' ').title()
            status = "🔴" if value > 0.6 else "🟡" if value > 0.3 else "🟢"
            report_text += f"  {status} {indicator_name}: {value:.3f}\n"
        
        self.console.print(Panel(report_text, title="🔍 AI Bubble Analysis", border_style="blue"))
        
        # Show individual articles
        if report['individual_analyses']:
            self.console.print("\n[bold]📰 Individual Article Analysis:[/bold]")
            
            for i, analysis in enumerate(report['individual_analyses'], 1):
                risk_color = "red" if analysis['bubble_risk'] > 0.7 else "yellow" if analysis['bubble_risk'] > 0.4 else "green"
                
                self.console.print(f"\n{i}. [bold]{analysis['title'][:60]}...[/bold]")
                self.console.print(f"   🔗 {analysis['url']}")
                self.console.print(f"   😊 Sentiment: {analysis['sentiment_score']:.3f}")
                self.console.print(f"   ⚠️  Bubble Risk: [{risk_color}]{analysis['bubble_risk']:.3f}[/{risk_color}]")
                self.console.print(f"   📊 Impact: {analysis['market_impact']}")
                
                if analysis['key_phrases']:
                    phrases = ", ".join(analysis['key_phrases'][:3])
                    self.console.print(f"   🏷️  Key Phrases: {phrases}...")

    def show_quick_summary(self):
        """Show quick summary of analysis"""
        report = self.tracker.get_bubble_report()
        
        if 'error' in report:
            return
        
        # Determine risk level
        risk_level = report['average_bubble_risk']
        if risk_level > 0.7:
            risk_status = "🔴 HIGH BUBBLE RISK"
            risk_color = "red"
        elif risk_level > 0.4:
            risk_status = "🟡 MODERATE BUBBLE RISK"
            risk_color = "yellow"
        else:
            risk_status = "🟢 LOW BUBBLE RISK"
            risk_color = "green"
        
        summary_text = f"""
[bold]Quick Summary:[/bold]
📊 Market Assessment: {report['market_assessment']}
⚠️  Bubble Risk: [{risk_color}]{risk_status}[/{risk_color}] ({risk_level:.3f})
😊 Sentiment: {report['average_sentiment']:.3f}
📰 Articles Analyzed: {report['total_articles']}
🚨 Concerning Articles: {report['concerning_articles']}
        """
        
        self.console.print(Panel(summary_text, title="📈 Analysis Summary", border_style="green"))

    def clean_old_articles(self, days: int):
        """Clean old articles"""
        self.console.print(f"[bold blue]🧹 Cleaning articles older than {days} days...[/bold blue]")
        
        removed_count = self.tracker.remove_old_articles(days)
        
        if removed_count > 0:
            self.console.print(f"[green]✅ Removed {removed_count} old articles[/green]")
        else:
            self.console.print("[yellow]ℹ️  No old articles to remove[/yellow]")


def main():
    """Main entry point"""
    cli = BubbleAnalysisCLI()
    cli.run()


if __name__ == "__main__":
    main()
