#!/usr/bin/env python3
"""
Main execution script for Global Warming Analysis Project.
This script orchestrates the entire analysis pipeline.
"""

import sys
import os
import argparse
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_collection.climate_data_collector import ClimateDataCollector
from analysis.climate_analyzer import ClimateAnalyzer
from visualization.climate_visualizer import ClimateVisualizer

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Global Warming Analysis Project')
    parser.add_argument('--collect-data', action='store_true', 
                       help='Collect climate data from sources')
    parser.add_argument('--analyze', action='store_true', 
                       help='Perform statistical analysis')
    parser.add_argument('--visualize', action='store_true', 
                       help='Create visualizations')
    parser.add_argument('--all', action='store_true', 
                       help='Run complete analysis pipeline')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GLOBAL WARMING ANALYSIS PROJECT")
    print("Analyzing Climate Change Over the 20th Century")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run complete pipeline if --all is specified
    if args.all or (not args.collect_data and not args.analyze and not args.visualize):
        args.collect_data = True
        args.analyze = True
        args.visualize = True
    
    # Step 1: Data Collection
    if args.collect_data:
        print("STEP 1: DATA COLLECTION")
        print("-" * 30)
        collector = ClimateDataCollector()
        datasets = collector.collect_all_data()
        
        if datasets:
            print(f"\n✓ Successfully collected {len(datasets)} datasets")
            for name, df in datasets.items():
                print(f"  - {name}: {len(df)} records")
        else:
            print("✗ Data collection failed")
            return
        print()
    
    # Step 2: Analysis
    if args.analyze:
        print("STEP 2: STATISTICAL ANALYSIS")
        print("-" * 30)
        analyzer = ClimateAnalyzer()
        results = analyzer.comprehensive_analysis()
        
        if results and 'summary' in results:
            print(f"\n✓ Analysis completed successfully")
            print(f"  - Indicators analyzed: {results['summary']['indicators_analyzed']}")
            print("\nKey Findings:")
            for finding in results['summary']['key_findings']:
                print(f"  • {finding}")
            
            # Save results
            analyzer.save_results()
        else:
            print("✗ Analysis failed")
            return
        print()
    
    # Step 3: Visualization
    if args.visualize:
        print("STEP 3: VISUALIZATION")
        print("-" * 30)
        visualizer = ClimateVisualizer()
        
        # Load data for visualization
        temp_df = visualizer.load_data("noaa_global_temperature.csv")
        sea_level_df = visualizer.load_data("sea_level_data.csv")
        results = visualizer.load_analysis_results()
        
        if not temp_df.empty and not sea_level_df.empty and results:
            print("Creating visualizations...")
            visualizer.create_temperature_trend_plot(temp_df, results)
            visualizer.create_sea_level_plot(sea_level_df, results)
            visualizer.create_comprehensive_dashboard()
            visualizer.create_interactive_plotly_dashboard()
            visualizer.create_trend_comparison_plot(results)
            print("✓ All visualizations created successfully")
        else:
            print("✗ Visualization failed - missing data or results")
            return
        print()
    
    # Summary
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nGenerated files:")
    print("📊 Data files: data/")
    print("📈 Visualizations: results/")
    print("📋 Analysis results: data/analysis_results.json")
    print("\nTo view interactive dashboard:")
    print("🌐 Open: results/interactive_dashboard.html in your browser")
    print("=" * 60)

if __name__ == "__main__":
    main()
