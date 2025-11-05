# Global Warming Analysis Project

## Overview
This project provides a comprehensive analysis of global warming trends over the 20th century using reliable scientific data sources. It examines temperature increases, sea level rise, ocean warming, and glacier retreat to determine the extent of climate change.

## Key Findings
Based on scientific data analysis, the project demonstrates that:

- **Global average surface temperature** has risen significantly over the 20th century
- **Sea levels** have been rising at an accelerating rate
- **Ocean temperatures** have increased substantially
- **Glaciers worldwide** have been retreating
- **Atmospheric CO₂ concentrations** have increased dramatically

## Data Sources
The project utilizes data from the following reliable scientific institutions:

### Temperature Data
- **NOAA Global Surface Temperature Dataset**: Global surface temperatures since 1880
- **HadCRUT Dataset**: Combined sea surface and land surface air temperature data from 1850
- **Berkeley Earth**: Independent global temperature analysis

### Sea Level Data
- **NASA Sea Level Change Portal**: Satellite observations and historical records
- **NOAA Sea Level Rise**: Tide gauge and satellite data

### Ocean Temperature Data
- **International Comprehensive Ocean-Atmosphere Data Set (ICOADS)**: Sea surface temperatures
- **NOAA Ocean Heat Content**: Ocean temperature measurements

### Glacier Data
- **World Glacier Monitoring Service (WGMS)**: Glacier mass balance and length changes
- **National Snow and Ice Data Center (NSIDC)**: Glacier and ice sheet data

### Atmospheric CO₂ Data
- **Keeling Curve**: Atmospheric CO₂ concentrations since 1958

## Project Structure
```
globalWarming/
├── data/                    # Raw and processed data files
│   ├── noaa_global_temperature.csv
│   ├── sea_level_data.csv
│   ├── ocean_temperature_data.csv
│   ├── glacier_data.csv
│   ├── co2_data.csv
│   └── analysis_results.json
├── src/                     # Source code
│   ├── data_collection/     # Scripts to collect data from sources
│   │   └── climate_data_collector.py
│   ├── analysis/           # Statistical analysis modules
│   │   └── climate_analyzer.py
│   └── visualization/       # Plotting and visualization tools
│       └── climate_visualizer.py
├── notebooks/              # Jupyter notebooks for analysis
├── results/                # Generated plots and analysis results
│   ├── temperature_trends.png
│   ├── sea_level_rise.png
│   ├── comprehensive_dashboard.png
│   ├── interactive_dashboard.html
│   └── trend_comparison.png
├── docs/                   # Documentation and reports
├── main.py                 # Main execution script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup
1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd globalWarming
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the analysis**:
   ```bash
   python main.py --all
   ```

## Usage

### Complete Analysis Pipeline
Run the entire analysis pipeline:
```bash
python main.py --all
```

### Individual Steps
You can also run individual steps:

1. **Data Collection Only**:
   ```bash
   python main.py --collect-data
   ```

2. **Analysis Only** (requires data to be collected first):
   ```bash
   python main.py --analyze
   ```

3. **Visualization Only** (requires data and analysis):
   ```bash
   python main.py --visualize
   ```

### Using Individual Modules
You can also use the modules independently:

```python
# Data Collection
from src.data_collection.climate_data_collector import ClimateDataCollector
collector = ClimateDataCollector()
datasets = collector.collect_all_data()

# Analysis
from src.analysis.climate_analyzer import ClimateAnalyzer
analyzer = ClimateAnalyzer()
results = analyzer.comprehensive_analysis()

# Visualization
from src.visualization.climate_visualizer import ClimateVisualizer
visualizer = ClimateVisualizer()
visualizer.create_comprehensive_dashboard()
```

## Output Files

### Data Files (`data/` directory)
- `noaa_global_temperature.csv`: Global temperature anomaly data
- `sea_level_data.csv`: Sea level rise measurements
- `ocean_temperature_data.csv`: Ocean temperature data
- `glacier_data.csv`: Glacier retreat data
- `co2_data.csv`: Atmospheric CO₂ concentration data
- `analysis_results.json`: Statistical analysis results

### Visualizations (`results/` directory)
- `temperature_trends.png`: Temperature trend analysis
- `sea_level_rise.png`: Sea level rise visualization
- `comprehensive_dashboard.png`: Multi-panel climate dashboard
- `interactive_dashboard.html`: Interactive Plotly dashboard
- `trend_comparison.png`: Comparison of all climate trends

## Analysis Methods

### Statistical Analysis
The project performs comprehensive statistical analysis including:

- **Linear regression** to determine trends
- **Correlation analysis** to assess relationships
- **Statistical significance testing** (p-values)
- **Decadal trend analysis** for temperature data
- **Acceleration analysis** for sea level rise

### Key Metrics
- Temperature change per century (°C)
- Sea level rise per century (mm)
- Ocean warming per century (°C)
- Glacier retreat per century (m)
- CO₂ increase per century (ppm)

## Scientific Background

### Temperature Trends
Global average surface temperature has risen by approximately **0.13°C per decade** over the past 50 years, nearly double the rate observed in the previous half-century.

### Sea Level Rise
Sea levels have been rising at an accelerating rate due to:
- Thermal expansion of seawater
- Melting of glaciers and ice sheets
- Changes in land water storage

### Ocean Warming
Ocean temperatures have increased significantly, affecting:
- Marine ecosystems
- Weather patterns
- Sea level rise through thermal expansion

### Glacier Retreat
Glaciers worldwide have been retreating due to:
- Rising temperatures
- Changes in precipitation patterns
- Increased melting rates

## Contributing

### Adding New Data Sources
To add new climate data sources:

1. Create a new method in `ClimateDataCollector` class
2. Add corresponding analysis method in `ClimateAnalyzer` class
3. Update visualization methods in `ClimateVisualizer` class
4. Update the main execution script

### Improving Analysis
To enhance the statistical analysis:

1. Modify methods in `ClimateAnalyzer` class
2. Add new statistical tests or metrics
3. Update visualization methods accordingly

## License
This project is for educational and research purposes. Please cite appropriate data sources when using the results.

## Contact
For questions or contributions, please refer to the project documentation or contact the maintainers.

## References
- NOAA Climate.gov: https://www.climate.gov/
- NASA Climate Change: https://climate.nasa.gov/
- Berkeley Earth: http://berkeleyearth.org/
- World Glacier Monitoring Service: https://wgms.ch/
- National Snow and Ice Data Center: https://nsidc.org/