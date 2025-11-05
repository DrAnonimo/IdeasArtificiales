"""
Statistical analysis module for global warming data.
This module contains functions to analyze temperature trends and other climate indicators.
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import linregress
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class ClimateAnalyzer:
    """Main class for analyzing climate data and determining trends."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.results = {}
    
    def load_data(self, filename: str) -> pd.DataFrame:
        """Load data from CSV file."""
        filepath = f"{self.data_dir}/{filename}"
        try:
            df = pd.read_csv(filepath)
            return df
        except FileNotFoundError:
            print(f"File {filepath} not found. Please run data collection first.")
            return pd.DataFrame()
    
    def analyze_temperature_trend(self, df: pd.DataFrame) -> Dict:
        """
        Analyze global temperature trends over the 20th century.
        
        Args:
            df: DataFrame with temperature data
            
        Returns:
            Dictionary with trend analysis results
        """
        if df.empty:
            return {}
        
        print("Analyzing temperature trends...")
        
        # Calculate annual averages
        annual_temp = df.groupby('year')['temperature_anomaly'].mean().reset_index()
        
        # Filter for 20th century (1900-2000)
        century_data = annual_temp[(annual_temp['year'] >= 1900) & (annual_temp['year'] <= 2000)]
        
        if len(century_data) < 10:
            print("Insufficient data for trend analysis")
            return {}
        
        # Linear regression analysis
        slope, intercept, r_value, p_value, std_err = linregress(
            century_data['year'], century_data['temperature_anomaly']
        )
        
        # Calculate temperature change over the century
        temp_change_century = slope * 100  # Change per century
        
        # Calculate decadal trends
        decades = []
        for decade_start in range(1900, 2000, 10):
            decade_data = century_data[
                (century_data['year'] >= decade_start) & 
                (century_data['year'] < decade_start + 10)
            ]
            if len(decade_data) > 5:
                decade_slope, _, _, _, _ = linregress(
                    decade_data['year'], decade_data['temperature_anomaly']
                )
                decades.append({
                    'decade': f"{decade_start}s",
                    'trend_per_decade': decade_slope * 10,
                    'mean_anomaly': decade_data['temperature_anomaly'].mean()
                })
        
        # Statistical significance test
        is_significant = p_value < 0.05
        
        results = {
            'total_temperature_change_century': temp_change_century,
            'trend_per_year': slope,
            'correlation_coefficient': r_value,
            'p_value': p_value,
            'is_statistically_significant': is_significant,
            'standard_error': std_err,
            'decadal_trends': decades,
            'data_points': len(century_data),
            'year_range': f"{century_data['year'].min()}-{century_data['year'].max()}"
        }
        
        self.results['temperature'] = results
        return results
    
    def analyze_sea_level_trend(self, df: pd.DataFrame) -> Dict:
        """
        Analyze sea level rise trends.
        """
        if df.empty:
            return {}
        
        print("Analyzing sea level trends...")
        
        # Filter for 20th century
        century_data = df[(df['year'] >= 1900) & (df['year'] <= 2000)]
        
        if len(century_data) < 10:
            return {}
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = linregress(
            century_data['year'], century_data['sea_level_rise_mm']
        )
        
        # Calculate sea level rise per century
        slr_per_century = slope * 100
        
        # Calculate acceleration (second derivative approximation)
        if len(century_data) > 20:
            mid_point = len(century_data) // 2
            first_half_slope, _, _, _, _ = linregress(
                century_data.iloc[:mid_point]['year'],
                century_data.iloc[:mid_point]['sea_level_rise_mm']
            )
            second_half_slope, _, _, _, _ = linregress(
                century_data.iloc[mid_point:]['year'],
                century_data.iloc[mid_point:]['sea_level_rise_mm']
            )
            acceleration = second_half_slope - first_half_slope
        else:
            acceleration = 0
        
        results = {
            'sea_level_rise_per_century_mm': slr_per_century,
            'trend_per_year_mm': slope,
            'correlation_coefficient': r_value,
            'p_value': p_value,
            'is_statistically_significant': p_value < 0.05,
            'acceleration_mm_per_year': acceleration,
            'total_rise_century_mm': century_data['sea_level_rise_mm'].iloc[-1] - century_data['sea_level_rise_mm'].iloc[0]
        }
        
        self.results['sea_level'] = results
        return results
    
    def analyze_ocean_temperature_trend(self, df: pd.DataFrame) -> Dict:
        """
        Analyze ocean temperature warming trends.
        """
        if df.empty:
            return {}
        
        print("Analyzing ocean temperature trends...")
        
        century_data = df[(df['year'] >= 1900) & (df['year'] <= 2000)]
        
        if len(century_data) < 10:
            return {}
        
        slope, intercept, r_value, p_value, std_err = linregress(
            century_data['year'], century_data['temperature_anomaly_c']
        )
        
        ocean_warming_per_century = slope * 100
        
        results = {
            'ocean_warming_per_century_c': ocean_warming_per_century,
            'trend_per_year_c': slope,
            'correlation_coefficient': r_value,
            'p_value': p_value,
            'is_statistically_significant': p_value < 0.05,
            'total_warming_century_c': century_data['temperature_anomaly_c'].iloc[-1] - century_data['temperature_anomaly_c'].iloc[0]
        }
        
        self.results['ocean_temperature'] = results
        return results
    
    def analyze_glacier_retreat(self, df: pd.DataFrame) -> Dict:
        """
        Analyze glacier retreat trends.
        """
        if df.empty:
            return {}
        
        print("Analyzing glacier retreat trends...")
        
        century_data = df[(df['year'] >= 1900) & (df['year'] <= 2000)]
        
        if len(century_data) < 5:
            return {}
        
        slope, intercept, r_value, p_value, std_err = linregress(
            century_data['year'], century_data['total_retreat_m']
        )
        
        retreat_per_century = slope * 100
        
        results = {
            'retreat_per_century_m': retreat_per_century,
            'trend_per_year_m': slope,
            'correlation_coefficient': r_value,
            'p_value': p_value,
            'is_statistically_significant': p_value < 0.05,
            'total_retreat_century_m': century_data['total_retreat_m'].iloc[-1] - century_data['total_retreat_m'].iloc[0],
            'final_length_m': century_data['glacier_length_m'].iloc[-1],
            'initial_length_m': century_data['glacier_length_m'].iloc[0]
        }
        
        self.results['glacier'] = results
        return results
    
    def analyze_co2_trend(self, df: pd.DataFrame) -> Dict:
        """
        Analyze atmospheric CO2 concentration trends.
        """
        if df.empty:
            return {}
        
        print("Analyzing CO2 concentration trends...")
        
        century_data = df[(df['year'] >= 1900) & (df['year'] <= 2000)]
        
        if len(century_data) < 10:
            return {}
        
        slope, intercept, r_value, p_value, std_err = linregress(
            century_data['year'], century_data['co2_ppm']
        )
        
        co2_increase_per_century = slope * 100
        
        results = {
            'co2_increase_per_century_ppm': co2_increase_per_century,
            'trend_per_year_ppm': slope,
            'correlation_coefficient': r_value,
            'p_value': p_value,
            'is_statistically_significant': p_value < 0.05,
            'total_increase_century_ppm': century_data['co2_ppm'].iloc[-1] - century_data['co2_ppm'].iloc[0],
            'final_co2_ppm': century_data['co2_ppm'].iloc[-1],
            'initial_co2_ppm': century_data['co2_ppm'].iloc[0]
        }
        
        self.results['co2'] = results
        return results
    
    def comprehensive_analysis(self) -> Dict:
        """
        Perform comprehensive analysis of all climate indicators.
        """
        print("Starting comprehensive climate analysis...")
        
        # Load all datasets
        temperature_df = self.load_data("noaa_global_temperature.csv")
        sea_level_df = self.load_data("sea_level_data.csv")
        ocean_temp_df = self.load_data("ocean_temperature_data.csv")
        glacier_df = self.load_data("glacier_data.csv")
        co2_df = self.load_data("co2_data.csv")
        
        # Perform analyses
        temp_results = self.analyze_temperature_trend(temperature_df)
        slr_results = self.analyze_sea_level_trend(sea_level_df)
        ocean_results = self.analyze_ocean_temperature_trend(ocean_temp_df)
        glacier_results = self.analyze_glacier_retreat(glacier_df)
        co2_results = self.analyze_co2_trend(co2_df)
        
        # Summary analysis
        summary = self._create_summary_analysis()
        
        comprehensive_results = {
            'temperature': temp_results,
            'sea_level': slr_results,
            'ocean_temperature': ocean_results,
            'glacier': glacier_results,
            'co2': co2_results,
            'summary': summary
        }
        
        return comprehensive_results
    
    def _create_summary_analysis(self) -> Dict:
        """Create a summary of all analyses."""
        summary = {
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'indicators_analyzed': len(self.results),
            'key_findings': []
        }
        
        # Extract key findings
        if 'temperature' in self.results:
            temp_change = self.results['temperature']['total_temperature_change_century']
            summary['key_findings'].append(
                f"Global temperature increased by {temp_change:.2f}°C over the 20th century"
            )
        
        if 'sea_level' in self.results:
            slr = self.results['sea_level']['sea_level_rise_per_century_mm']
            summary['key_findings'].append(
                f"Sea level rose by {slr:.1f} mm over the 20th century"
            )
        
        if 'ocean_temperature' in self.results:
            ocean_warming = self.results['ocean_temperature']['ocean_warming_per_century_c']
            summary['key_findings'].append(
                f"Ocean temperature increased by {ocean_warming:.2f}°C over the 20th century"
            )
        
        if 'glacier' in self.results:
            retreat = self.results['glacier']['retreat_per_century_m']
            summary['key_findings'].append(
                f"Glaciers retreated by {retreat:.1f} meters over the 20th century"
            )
        
        if 'co2' in self.results:
            co2_increase = self.results['co2']['co2_increase_per_century_ppm']
            summary['key_findings'].append(
                f"Atmospheric CO2 increased by {co2_increase:.1f} ppm over the 20th century"
            )
        
        return summary
    
    def save_results(self, filename: str = "analysis_results.json"):
        """Save analysis results to JSON file."""
        import json
        
        filepath = f"{self.data_dir}/{filename}"
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"Analysis results saved to {filepath}")

def main():
    """Main function to run analysis."""
    analyzer = ClimateAnalyzer()
    results = analyzer.comprehensive_analysis()
    
    print("\n=== CLIMATE ANALYSIS RESULTS ===")
    print(f"Analysis completed on {results['summary']['analysis_date']}")
    print(f"Indicators analyzed: {results['summary']['indicators_analyzed']}")
    
    print("\nKey Findings:")
    for finding in results['summary']['key_findings']:
        print(f"- {finding}")
    
    # Save results
    analyzer.save_results()
    
    return results

if __name__ == "__main__":
    main()
