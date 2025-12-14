#!/usr/bin/env python3
"""
Fetch Census Block Group Data for Berkeley
Compare tract-level vs block group-level results
"""

import pandas as pd
import geopandas as gpd
import requests
from pathlib import Path

print("="*70)
print("FETCHING CENSUS BLOCK GROUP DATA")
print("="*70)

# Paths
DATA_DIR = Path("data")
PROCESSED_DIR = Path("data/processed")

# Census API endpoint (no key needed for ACS 5-year)
BASE_URL = "https://api.census.gov/data/2021/acs/acs5"

# Alameda County FIPS: 06001
# Variables we need:
VARIABLES = {
    'B19013_001E': 'median_household_income',      # Median household income
    'B01003_001E': 'total_population',              # Total population
    'B14001_001E': 'total_enrollment',              # School enrollment
    'B14001_009E': 'college_grad_enrollment',       # Graduate/professional enrollment
    'B25044_001E': 'total_households',              # Total occupied housing units
    'B25044_003E': 'no_vehicle_owner',              # Owner occupied, no vehicle
    'B25044_010E': 'no_vehicle_renter',             # Renter occupied, no vehicle
    'B23025_001E': 'pop_in_labor_force_universe',   # Population 16+ for employment
    'B23025_003E': 'in_labor_force',                # In labor force
    'B23025_005E': 'unemployed',                    # Unemployed
    'B25001_001E': 'total_housing_units'            # Total housing units
}

# Build query
var_list = ','.join(VARIABLES.keys())
url = f"{BASE_URL}?get=NAME,{var_list}&for=block%20group:*&in=state:06&in=county:001"

print(f"\nFetching from Census API...")
print(f"Geography: Block Groups in Alameda County, CA")
print(f"Variables: {len(VARIABLES)}")

# Fetch data
response = requests.get(url)
response.raise_for_status()
data = response.json()

print(f" Fetched {len(data)-1} block groups")

# Convert to DataFrame
df = pd.DataFrame(data[1:], columns=data[0])

# Rename columns
rename_dict = {k: v for k, v in VARIABLES.items()}
df = df.rename(columns=rename_dict)

# Add GEOID
df['GEOID'] = df['state'] + df['county'] + df['tract'] + df['block group']

# Convert to numeric
for col in VARIABLES.values():
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Calculate derived variables
df['student_population'] = df['college_grad_enrollment']  # Students (grad/prof school proxy)
df['pct_students'] = (df['student_population'] / df['total_population'] * 100).round(2)

df['households_no_vehicle'] = df['no_vehicle_owner'] + df['no_vehicle_renter']
df['pct_no_vehicle'] = (df['households_no_vehicle'] / df['total_households'] * 100).round(2)

df['unemployment_rate'] = (df['unemployed'] / df['in_labor_force'] * 100).round(2)

print("\n" + "="*70)
print("BLOCK GROUP DATA SUMMARY")
print("="*70)
print(f"Total block groups in Alameda County: {len(df)}")
print(f"\nIncome range: ${df['median_household_income'].min():,.0f} - ${df['median_household_income'].max():,.0f}")
print(f"Population range: {df['total_population'].min():.0f} - {df['total_population'].max():.0f}")
print(f"Avg block group population: {df['total_population'].mean():.0f}")
print(f"\nVehicle ownership:")
print(f"  Min % no vehicle: {df['pct_no_vehicle'].min():.1f}%")
print(f"  Max % no vehicle: {df['pct_no_vehicle'].max():.1f}%")
print(f"  Avg % no vehicle: {df['pct_no_vehicle'].mean():.1f}%")

# Save raw data
output_file = PROCESSED_DIR / "alameda_block_groups_demographics.csv"
df.to_csv(output_file, index=False)
print(f"\nSaved: {output_file}")

# Fetch geometries from Census TIGER
print("\n" + "="*70)
print("FETCHING BLOCK GROUP GEOMETRIES")
print("="*70)

tiger_url = "https://www2.census.gov/geo/tiger/TIGER2021/BG/tl_2021_06_bg.zip"
print(f"\nDownloading from: {tiger_url}")

# Load block group shapefile
bg_geo = gpd.read_file(tiger_url)
print(f" Loaded {len(bg_geo)} California block groups")

# Filter to Alameda County
bg_geo = bg_geo[bg_geo['COUNTYFP'] == '001'].copy()
print(f" Filtered to {len(bg_geo)} Alameda County block groups")

# Merge demographics
bg_geo = bg_geo.merge(df, on='GEOID', how='left')

# Filter to Berkeley (approximate by tract - Berkeley tracts are 4220-4240)
berkeley_tracts = [f'4{i:03d}' for i in range(220, 241)]
bg_geo['tract_num'] = bg_geo['TRACTCE'].str[:4]
berkeley_bg = bg_geo[bg_geo['tract_num'].isin(berkeley_tracts)].copy()

print(f"\n Filtered to {len(berkeley_bg)} Berkeley block groups")

# Transform to appropriate projection
berkeley_bg = berkeley_bg.to_crs("EPSG:4326")  # WGS84 for web mapping

# Save Berkeley block groups
output_geo = PROCESSED_DIR / "berkeley_block_groups_with_demographics.geojson"
berkeley_bg.to_file(output_geo, driver='GeoJSON')
print(f" Saved: {output_geo}")

# Show comparison with tracts
print("\n" + "="*70)
print("COMPARISON: TRACTS vs BLOCK GROUPS")
print("="*70)

tracts_geo = gpd.read_file(PROCESSED_DIR / "berkeley_tracts_with_demographics.geojson")

print(f"\nSpatial units:")
print(f"  Census Tracts: {len(tracts_geo)}")
print(f"  Block Groups: {len(berkeley_bg)}")
print(f"  Ratio: {len(berkeley_bg) / len(tracts_geo):.1f}× more granular")

print(f"\nAverage population:")
print(f"  Tract avg: {tracts_geo['total_population'].mean():.0f} people")
print(f"  Block Group avg: {berkeley_bg['total_population'].mean():.0f} people")

print(f"\nIncome variation:")
print(f"  Tract std dev: ${tracts_geo['median_household_income'].std():,.0f}")
print(f"  Block Group std dev: ${berkeley_bg['median_household_income'].std():,.0f}")

print("\n" + "="*70)
print("NEXT STEP: Re-run catchment analysis with block groups")
print("Run: python3 scripts_key/compare_tract_vs_blockgroup_analysis.py")
print("="*70)
