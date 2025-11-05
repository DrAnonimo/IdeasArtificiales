"""
Visualization module for global warming analysis.
This module creates comprehensive visualizations of climate data and trends.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from typing import Dict, List, Optional
import os

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ClimateVisualizer:
    """Main class for creating climate data visualizations."""
    
    def __init__(self, data_dir: str = "data", results_dir: str = "results"):
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.ensure_results_directory()
    
    def ensure_results_directory(self):
        """Ensure results directory exists."""
        os.makedirs(self.results_dir, exist_ok=True)
    
    def load_data(self, filename: str) -> pd.DataFrame:
        """Load data from CSV file."""
        filepath = f"{self.data_dir}/{filename}"
        try:
            df = pd.read_csv(filepath)
            return df
        except FileNotFoundError:
            print(f"File {filepath} not found.")
            return pd.DataFrame()
    
    def load_analysis_results(self, filename: str = "analysis_results.json") -> Dict:
        """Load analysis results from JSON file."""
        filepath = f"{self.data_dir}/{filename}"
        try:
            with open(filepath, 'r') as f:
                results = json.load(f)
            return results
        except FileNotFoundError:
            print(f"Analysis results file {filepath} not found.")
            return {}
    
    def create_temperature_trend_plot(self, df: pd.DataFrame, results: Dict) -> None:
        """Create temperature trend visualization."""
        if df.empty:
            return
        
        print("Creating temperature trend visualization...")
        
        # Calculate annual averages
        annual_temp = df.groupby('year')['temperature_anomaly'].mean().reset_index()
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Temperature anomaly over time
        ax1.plot(annual_temp['year'], annual_temp['temperature_anomaly'], 
                linewidth=2, color='red', alpha=0.7)
        ax1.scatter(annual_temp['year'], annual_temp['temperature_anomaly'], 
                   s=20, color='darkred', alpha=0.6)
        
        # Add trend line
        if 'temperature' in results and results['temperature']:
            slope = results['temperature']['trend_per_year']
            intercept = results['temperature']['trend_per_year'] * 1900
            trend_line = slope * annual_temp['year'] + intercept
            ax1.plot(annual_temp['year'], trend_line, '--', color='black', 
                    linewidth=2, alpha=0.8, label=f'Trend: {slope:.3f}°C/year')
        
        ax1.set_title('Global Temperature Anomaly Over Time', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Year', fontsize=12)
        ax1.set_ylabel('Temperature Anomaly (°C)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Add 20th century highlight
        ax1.axvspan(1900, 2000, alpha=0.2, color='yellow', label='20th Century')
        
        # Plot 2: Decadal trends
        if 'temperature' in results and 'decadal_trends' in results['temperature']:
            decades = results['temperature']['decadal_trends']
            decade_names = [d['decade'] for d in decades]
            decade_trends = [d['trend_per_decade'] for d in decades]
            
            bars = ax2.bar(decade_names, decade_trends, color='orange', alpha=0.7)
            ax2.set_title('Temperature Trend by Decade (20th Century)', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Decade', fontsize=12)
            ax2.set_ylabel('Temperature Change per Decade (°C)', fontsize=12)
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, value in zip(bars, decade_trends):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                        f'{value:.3f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f"{self.results_dir}/temperature_trends.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_sea_level_plot(self, df: pd.DataFrame, results: Dict) -> None:
        """Create sea level rise visualization."""
        if df.empty:
            return
        
        print("Creating sea level rise visualization...")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot sea level rise
        ax.plot(df['year'], df['sea_level_rise_mm'], linewidth=2, color='blue', alpha=0.7)
        ax.scatter(df['year'], df['sea_level_rise_mm'], s=20, color='darkblue', alpha=0.6)
        
        # Add trend line
        if 'sea_level' in results and results['sea_level']:
            slope = results['sea_level']['trend_per_year_mm']
            intercept = results['sea_level']['trend_per_year_mm'] * 1900
            trend_line = slope * df['year'] + intercept
            ax.plot(df['year'], trend_line, '--', color='black', 
                   linewidth=2, alpha=0.8, label=f'Trend: {slope:.2f} mm/year')
        
        ax.set_title('Global Sea Level Rise Over Time', fontsize=16, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Sea Level Rise (mm)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Add 20th century highlight
        ax.axvspan(1900, 2000, alpha=0.2, color='yellow', label='20th Century')
        
        plt.tight_layout()
        plt.savefig(f"{self.results_dir}/sea_level_rise.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_comprehensive_dashboard(self) -> None:
        """Create a comprehensive dashboard with all climate indicators."""
        print("Creating comprehensive climate dashboard...")
        
        # Load all data
        temp_df = self.load_data("noaa_global_temperature.csv")
        sea_level_df = self.load_data("sea_level_data.csv")
        ocean_temp_df = self.load_data("ocean_temperature_data.csv")
        glacier_df = self.load_data("glacier_data.csv")
        co2_df = self.load_data("co2_data.csv")
        
        # Load analysis results
        results = self.load_analysis_results()
        
        # Create subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Global Warming Analysis: 20th Century Climate Indicators', 
                    fontsize=20, fontweight='bold')
        
        # Temperature
        if not temp_df.empty:
            annual_temp = temp_df.groupby('year')['temperature_anomaly'].mean().reset_index()
            axes[0, 0].plot(annual_temp['year'], annual_temp['temperature_anomaly'], 
                           color='red', linewidth=2)
            axes[0, 0].set_title('Global Temperature Anomaly', fontweight='bold')
            axes[0, 0].set_ylabel('Temperature Anomaly (°C)')
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].axvspan(1900, 2000, alpha=0.2, color='yellow')
        else:
            axes[0, 0].text(0.5, 0.5, 'Temperature data\nnot available', 
                           ha='center', va='center', transform=axes[0, 0].transAxes,
                           fontsize=12, bbox=dict(boxstyle='round', facecolor='lightgray'))
            axes[0, 0].set_title('Global Temperature Anomaly', fontweight='bold')
        
        # Sea Level
        if not sea_level_df.empty:
            axes[0, 1].plot(sea_level_df['year'], sea_level_df['sea_level_rise_mm'], 
                           color='blue', linewidth=2)
            axes[0, 1].set_title('Sea Level Rise', fontweight='bold')
            axes[0, 1].set_ylabel('Sea Level Rise (mm)')
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].axvspan(1900, 2000, alpha=0.2, color='yellow')
        
        # Ocean Temperature
        if not ocean_temp_df.empty:
            axes[0, 2].plot(ocean_temp_df['year'], ocean_temp_df['temperature_anomaly_c'], 
                           color='cyan', linewidth=2)
            axes[0, 2].set_title('Ocean Temperature Anomaly', fontweight='bold')
            axes[0, 2].set_ylabel('Temperature Anomaly (°C)')
            axes[0, 2].grid(True, alpha=0.3)
            axes[0, 2].axvspan(1900, 2000, alpha=0.2, color='yellow')
        
        # Glacier Retreat
        if not glacier_df.empty:
            axes[1, 0].plot(glacier_df['year'], glacier_df['total_retreat_m'], 
                           color='purple', linewidth=2)
            axes[1, 0].set_title('Glacier Retreat', fontweight='bold')
            axes[1, 0].set_ylabel('Total Retreat (m)')
            axes[1, 0].set_xlabel('Year')
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].axvspan(1900, 2000, alpha=0.2, color='yellow')
        
        # CO2 Concentration
        if not co2_df.empty:
            axes[1, 1].plot(co2_df['year'], co2_df['co2_ppm'], 
                           color='green', linewidth=2)
            axes[1, 1].set_title('Atmospheric CO₂ Concentration', fontweight='bold')
            axes[1, 1].set_ylabel('CO₂ (ppm)')
            axes[1, 1].set_xlabel('Year')
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].axvspan(1900, 2000, alpha=0.2, color='yellow')
        
        # Summary statistics
        axes[1, 2].axis('off')
        if results and 'summary' in results:
            summary_text = "Key Findings:\n\n"
            for finding in results['summary']['key_findings']:
                summary_text += f"• {finding}\n"
            
            axes[1, 2].text(0.1, 0.9, summary_text, transform=axes[1, 2].transAxes,
                           fontsize=12, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(f"{self.results_dir}/comprehensive_dashboard.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_interactive_plotly_dashboard(self) -> None:
        """Create an interactive Plotly dashboard."""
        print("Creating interactive Plotly dashboard...")
        
        # Load data
        temp_df = self.load_data("noaa_global_temperature.csv")
        sea_level_df = self.load_data("sea_level_data.csv")
        ocean_temp_df = self.load_data("ocean_temperature_data.csv")
        glacier_df = self.load_data("glacier_data.csv")
        co2_df = self.load_data("co2_data.csv")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=('Global Temperature Anomaly', 'Sea Level Rise', 
                          'Ocean Temperature Anomaly', 'Glacier Retreat', 
                          'Atmospheric CO₂', 'Summary'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}, {"type": "table"}]]
        )
        
        # Temperature
        if not temp_df.empty:
            annual_temp = temp_df.groupby('year')['temperature_anomaly'].mean().reset_index()
            fig.add_trace(
                go.Scatter(x=annual_temp['year'], y=annual_temp['temperature_anomaly'],
                          mode='lines+markers', name='Temperature Anomaly',
                          line=dict(color='red', width=2)),
                row=1, col=1
            )
        
        # Sea Level
        if not sea_level_df.empty:
            fig.add_trace(
                go.Scatter(x=sea_level_df['year'], y=sea_level_df['sea_level_rise_mm'],
                          mode='lines+markers', name='Sea Level Rise',
                          line=dict(color='blue', width=2)),
                row=1, col=2
            )
        
        # Ocean Temperature
        if not ocean_temp_df.empty:
            fig.add_trace(
                go.Scatter(x=ocean_temp_df['year'], y=ocean_temp_df['temperature_anomaly_c'],
                          mode='lines+markers', name='Ocean Temperature',
                          line=dict(color='cyan', width=2)),
                row=1, col=3
            )
        
        # Glacier Retreat
        if not glacier_df.empty:
            fig.add_trace(
                go.Scatter(x=glacier_df['year'], y=glacier_df['total_retreat_m'],
                          mode='lines+markers', name='Glacier Retreat',
                          line=dict(color='purple', width=2)),
                row=2, col=1
            )
        
        # CO2
        if not co2_df.empty:
            fig.add_trace(
                go.Scatter(x=co2_df['year'], y=co2_df['co2_ppm'],
                          mode='lines+markers', name='CO₂ Concentration',
                          line=dict(color='green', width=2)),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text="Global Warming Analysis: 20th Century Climate Indicators",
            title_x=0.5,
            height=800,
            showlegend=False
        )
        
        # Add 20th century highlights
        for i in range(1, 3):
            for j in range(1, 4):
                if not (i == 2 and j == 3):  # Skip summary cell
                    fig.add_vrect(x0=1900, x1=2000, fillcolor="yellow", 
                                opacity=0.2, layer="below", line_width=0,
                                row=i, col=j)
        
        # Save and show
        fig.write_html(f"{self.results_dir}/interactive_dashboard.html")
        fig.show()
    
    def create_trend_comparison_plot(self, results: Dict) -> None:
        """Create a comparison plot of all trends."""
        if not results:
            return
        
        print("Creating trend comparison plot...")
        
        indicators = []
        trends_per_century = []
        colors = ['red', 'blue', 'cyan', 'purple', 'green']
        
        if 'temperature' in results and results['temperature']:
            indicators.append('Temperature\n(°C)')
            trends_per_century.append(results['temperature']['total_temperature_change_century'])
        
        if 'sea_level' in results and results['sea_level']:
            indicators.append('Sea Level\n(mm)')
            trends_per_century.append(results['sea_level']['sea_level_rise_per_century_mm'])
        
        if 'ocean_temperature' in results and results['ocean_temperature']:
            indicators.append('Ocean Temp\n(°C)')
            trends_per_century.append(results['ocean_temperature']['ocean_warming_per_century_c'])
        
        if 'glacier' in results and results['glacier']:
            indicators.append('Glacier Retreat\n(m)')
            trends_per_century.append(results['glacier']['retreat_per_century_m'])
        
        if 'co2' in results and results['co2']:
            indicators.append('CO₂\n(ppm)')
            trends_per_century.append(results['co2']['co2_increase_per_century_ppm'])
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars = ax.bar(indicators, trends_per_century, color=colors[:len(indicators)], alpha=0.7)
        
        ax.set_title('Climate Change Trends Over the 20th Century', fontsize=16, fontweight='bold')
        ax.set_ylabel('Change Over 100 Years', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, trends_per_century):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + abs(height)*0.01,
                   f'{value:.2f}', ha='center', va='bottom' if height >= 0 else 'top', 
                   fontsize=11, fontweight='bold')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f"{self.results_dir}/trend_comparison.png", dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Main function to create all visualizations."""
    visualizer = ClimateVisualizer()
    
    # Load data and results
    temp_df = visualizer.load_data("noaa_global_temperature.csv")
    sea_level_df = visualizer.load_data("sea_level_data.csv")
    results = visualizer.load_analysis_results()
    
    # Create visualizations
    visualizer.create_temperature_trend_plot(temp_df, results)
    visualizer.create_sea_level_plot(sea_level_df, results)
    visualizer.create_comprehensive_dashboard()
    visualizer.create_interactive_plotly_dashboard()
    visualizer.create_trend_comparison_plot(results)
    
    print("All visualizations created and saved to results/ directory")

if __name__ == "__main__":
    main()
