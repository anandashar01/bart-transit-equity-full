# BART Transit Equity Analysis: Berkeley Stations (2019-2024)

**Live Visualization:** [https://anandashar01.github.io/bart-transit-equity-full/](https://anandashar01.github.io/bart-transit-equity-full/)

## Project Overview

This repository contains a comprehensive geospatial and temporal analysis examining transit equity impacts during the COVID-19 pandemic across three Berkeley BART stations: Downtown Berkeley, North Berkeley, and Ashby. The analysis reveals an unexpected paradox: the low-income, transit-dependent area (Downtown Berkeley) had superior multimodal connectivity yet experienced comparable ridership collapse to wealthier stations, exposing fundamental vulnerabilities in transit system resilience.

**Research Question:** How did BART ridership collapse and incomplete recovery (2019-2024) differentially impact Berkeley's three stations (Downtown Berkeley, North Berkeley, Ashby) across varying income levels and multimodal connectivity, and where did the missing regional riders go?

## Key Findings

### 1. The Paradox of Better Access
- **Downtown Berkeley** (low-income): 18 AC Transit routes, 103.6 trips/hr peak frequency
- **North Berkeley** (affluent): 9 routes, 47.0 trips/hr
- **Ashby** (middle-income): 9 routes, 44.5 trips/hr

Despite 2x better bus connectivity, Downtown Berkeley still lost 64% of BART ridership (11,566 → 4,170 daily).

### 2. Dual System Degradation
Both transit systems degraded simultaneously:
- **BART On-Time Performance:** 91% (2019) → 71% (2023)
- **AC Transit Service Cuts:** 15-30% reduction during pandemic
- **Result:** Multimodal resilience eliminated when both systems fail together

### 3. The Missing 66,000 Daily Riders
Bay Area permanently lost 66,000 daily transit riders post-pandemic. They went to:
- **Remote Work (Primary):** +490,000 permanent WFH workers → ~64,000 former transit commuters
- **Population Exodus:** 190,000 left Bay Area (2020-2023) → ~25,000 riders
- **Mode Shift to Driving:** Transit share 13% → 7% (permanent) → ~30,000 riders
- **Changed Patterns:** Hybrid schedules, reduced frequency → ~20,000 riders

### 4. Transit-Dependent vs. Choice Riders
- **Affluent stations** (Rockridge, Orinda): 30% retention → choice riders left permanently
- **Low-income stations** (Downtown Berkeley): 36% retention → transit-dependent riders had no alternatives
- **Equity implication:** Those with resources (car, WFH capability) abandoned transit; low-income riders remained captive to degraded service

## Visualizations

### Interactive Maps (Plotly)
1. **Station Comparison Map** - Geospatial overview of ridership change, income, and connectivity
2. **AC Transit Route Network** - Dark-matter basemap showing bus density serving each station
3. **Dual System Degradation (Animated)** - Time-slider visualization of parallel BART/AC Transit collapse

### Supporting Analysis
- Temporal service quality chart (BART OTP trends)
- Regional ridership decline comparison
- Returner mode choice analysis (450k office workers)
- WFH retention patterns
- Missing riders decomposition (4-panel analysis)

## Data Sources

All data is from authoritative public sources:

| Metric | Source | Specific Table/Report |
|--------|--------|----------------------|
| BART Ridership (2018-2024) | [BART Quarterly Reports](https://www.bart.gov/about/reports#quarterly) | Quarterly fare gate entries |
| Transit Mode Share (13% → 7%) | [U.S. Census ACS](https://data.census.gov) | Table B08301 "Journey to Work" |
| Median Household Income | [U.S. Census ACS](https://data.census.gov) | Table B19013 (2019-2023) |
| Vehicle Ownership | [U.S. Census ACS](https://data.census.gov) | Table B25044 |
| AC Transit Routes/Frequency | [AC Transit GTFS](https://www.actransit.org/planning-focus/data-resource-center) | November 2024 feed |
| BART On-Time Performance | [BART Performance Reports](https://www.bart.gov/about/reports#performance) | 2018-2024 system metrics |
| Population Migration | [CA Dept of Finance](https://dof.ca.gov/forecasting/demographics/estimates/) | E-4 Population Estimates |
| Remote Work Estimates | [Bay Area Council Economic Institute](https://www.bayareacouncil.org/economy/) | COVID-19 Economic Impact Surveys |
| LEHD Employment Data | [U.S. Census LEHD](https://lehd.ces.census.gov/) | Exploratory analysis only |

## Repository Structure

```
bart-transit-equity-full/
├── index.html                          # Main interactive report (GitHub Pages site)
├── requirements.txt                    # Python dependencies for reproducibility
├── README.md                           # This file
├── data/
│   ├── raw/                            # Unmodified source data
│   │   ├── ac_transit/                 # AC Transit GTFS feed (November 2024)
│   │   │   ├── routes.txt
│   │   │   ├── stops.txt
│   │   │   ├── trips.txt
│   │   │   ├── stop_times.txt
│   │   │   └── shapes.txt
│   │   └── census/                     # Census TIGER/Line Shapefiles (2021)
│   │       ├── tl_2021_06_bg/          # Block groups for California
│   │       └── tl_2021_06_tract/       # Tracts for California
│   └── processed/                      # Derived analytical datasets
│       ├── station_demographics_BLOCKGROUP_level.csv
│       ├── bart_ac_transit_connectivity.csv
│       └── bart_ridership_2019_2024.csv
├── src/                                # Python scripts for all analyses
│   ├── create_station_comparison_map.py
│   ├── create_ac_transit_route_network_map.py
│   ├── create_dual_system_degradation_ANIMATED.py
│   ├── create_temporal_service_chart.py
│   ├── analyze_returner_mode_choice.py
│   ├── analyze_wfh_retention_and_patterns.py
│   ├── fetch_block_group_data.py
│   └── fetch_lehd_commute_data.py
└── outputs/                            # Generated HTML visualizations
    ├── MAP1_Transit_Equity_Context.html
    ├── MAP2_Dual_System_Degradation.html
    ├── ac_transit_route_network.html
    ├── multimodal_connectivity_paradox.html
    ├── temporal_service_quality_chart.html
    ├── returner_mode_choice_analysis.html
    └── wfh_retention_clarification.html
```

## Technical Details

- **Spatial Analysis:** GeoPandas 0.5-mile walking buffer analysis for AC Transit route connectivity
- **Temporal Analysis:** 2018-2024 quarterly BART data, ACS 1-year estimates 2019-2023
- **Classification:** Income categories based on ACS 5-year estimates (2019-2023) median household income relative to county median
- **Normalization:** Absolute counts shown in main visualizations; per-capita metrics provided in supporting analysis
- **Visualization Framework:** Plotly (interactive HTML), Carto basemaps, colorblind-friendly gray palette
- **Spatial Resolution:** Census block groups for demographics (finer than tracts), 0.5-mile pedestrian catchment areas for transit access

## How to View

**Option 1 - Live Site (Recommended):**
Visit [https://anandashar01.github.io/bart-transit-equity-full/](https://anandashar01.github.io/bart-transit-equity-full/)

**Option 2 - Run Locally:**
```bash
git clone https://github.com/anandashar01/bart-transit-equity-full.git
cd bart-transit-equity-full
# Open index.html in browser
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or double-click index.html in Windows
```

**Option 3 - Reproduce Analysis from Scratch:**
```bash
# 1. Clone the repository
git clone https://github.com/anandashar01/bart-transit-equity-full.git
cd bart-transit-equity-full

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run visualization scripts (generates HTML files)
python3 src/create_station_comparison_map.py
python3 src/create_ac_transit_route_network_map.py
python3 src/create_dual_system_degradation_ANIMATED.py
python3 src/analyze_returner_mode_choice.py
python3 src/analyze_wfh_retention_and_patterns.py
python3 src/create_missing_riders_analysis.py

# 4. Output files will be generated in:
#    - outputs/
#    (all outputs in outputs/ directory)

# 5. Open index.html in browser to view complete report
open index.html
```

**Note on Data Organization:**
- **Raw data** (`data/raw/`): Unmodified source files from authoritative sources (GTFS feeds, Census shapefiles). See `data/raw/README.md` for complete source documentation, URLs, and licenses.
- **Processed data** (`data/processed/`): Derived analytical datasets generated from raw data using documented Python scripts. All processing steps are reproducible.
- No additional data downloads required - repository is fully self-contained for complete reproducibility

## Policy Implications

1. **Multimodal resilience requires ALL systems to function** - Better bus access doesn't help if buses also degrade
2. **Transit is becoming a service for the transit-dependent poor** - Choice riders left permanently; remaining riders lack alternatives
3. **Remote work is the primary driver of ridership loss** - Not safety concerns or service quality (though those matter)
4. **Recovery requires addressing multiple barriers** - Service restoration alone won't bring back riders who moved away or switched to WFH/driving

## Authors

Anand Ashar and Sean Yue
University of California, Berkeley
City Planning 101
December 2024

## License

Data sources are public domain (Census, BART, AC Transit). Analysis code and visualizations are available for educational and research use.

## Acknowledgments

- BART for publishing detailed performance and ridership data
- AC Transit for maintaining GTFS feeds
- US Census Bureau for ACS demographic data
- Bay Area Council Economic Institute for remote work research
