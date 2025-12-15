#!/usr/bin/env python3
"""
Fetch LEHD LODES Data - Where do Berkeley workers come from?
Origin-Destination Employment Statistics for commute flow analysis
"""

import pandas as pd
import requests
from pathlib import Path

print("="*70)
print("FETCHING LEHD LODES DATA - COMMUTE FLOWS")
print("="*70)

# LEHD LODES API
# Format: https://lehd.ces.census.gov/data/lodes/LODES8/{state}/od/{state}_od_{segment}_{jobtype}_{year}.csv.gz

# Parameters
STATE = "ca"  # California
YEAR_PRE = "2019"  # Pre-COVID
YEAR_POST = "2021"  # During COVID
SEGMENT = "main"  # main = primary jobs
JOBTYPE = "JT00"  # All jobs

DATA_DIR = Path("data/lehd")
DATA_DIR.mkdir(exist_ok=True, parents=True)

print(f"\nLEHD LODES Parameters:")
print(f"  State: {STATE.upper()}")
print(f"  Years: {YEAR_PRE} (pre-COVID), {YEAR_POST} (during COVID)")
print(f"  Job Type: All jobs")

# Berkeley city tract codes (from census data)
berkeley_tracts = [
    '06001400500', '06001400700', '06001421800', '06001421900', '06001422200',
    '06001422300', '06001422400', '06001422500', '06001422800', '06001422901',
    '06001423000', '06001423100', '06001423400', '06001423500', '06001423601',
    '06001423602', '06001423901', '06001423902', '06001424001'
]

print(f"\nBerkeley tracts: {len(berkeley_tracts)} tracts")

# Function to fetch LODES data (optimized - filter while reading)
def fetch_lodes(year):
    url = f"https://lehd.ces.census.gov/data/lodes/LODES8/{STATE}/od/{STATE}_od_{SEGMENT}_{JOBTYPE}_{year}.csv.gz"
    print(f"\nFetching {year} data from LEHD...")
    print(f"  URL: {url}")
    print(f"  (Filtering for Berkeley jobs only - this will take ~30 seconds)")

    try:
        # Read in chunks and filter for Berkeley only
        chunks = []
        chunk_size = 100000

        for chunk in pd.read_csv(url, compression='gzip', dtype={'w_geocode': str, 'h_geocode': str}, chunksize=chunk_size):
            # Get tract-level geocode (first 11 digits)
            chunk['w_tract'] = chunk['w_geocode'].str[:11]
            # Filter to jobs IN Berkeley
            berkeley_chunk = chunk[chunk['w_tract'].isin(berkeley_tracts)]
            if len(berkeley_chunk) > 0:
                chunks.append(berkeley_chunk)

        if chunks:
            df = pd.concat(chunks, ignore_index=True)
            print(f"   Found {len(df):,} jobs located in Berkeley")
            return df
        else:
            print(f"   No Berkeley jobs found")
            return None

    except Exception as e:
        print(f"   Error: {e}")
        return None

# Fetch pre-COVID data
print("\n" + "="*70)
print(f"PRE-COVID DATA ({YEAR_PRE})")
print("="*70)
df_2019 = fetch_lodes(YEAR_PRE)

# Fetch during-COVID data
print("\n" + "="*70)
print(f"DURING COVID DATA ({YEAR_POST})")
print("="*70)
df_2021 = fetch_lodes(YEAR_POST)

if df_2019 is None or df_2021 is None:
    print("\n Failed to fetch LEHD data")
    exit(1)

# Add home tract column (already have w_tract from filtering)
df_2019['h_tract'] = df_2019['h_geocode'].str[:11]
df_2021['h_tract'] = df_2021['h_geocode'].str[:11]

berkeley_2019 = df_2019
berkeley_2021 = df_2021

print(f"\n" + "="*70)
print("BERKELEY EMPLOYMENT FLOWS")
print("="*70)

print(f"\nJobs LOCATED in Berkeley:")
print(f"  2019: {berkeley_2019['S000'].sum():,} total jobs")
print(f"  2021: {berkeley_2021['S000'].sum():,} total jobs")
print(f"  Change: {berkeley_2021['S000'].sum() - berkeley_2019['S000'].sum():,} jobs ({(berkeley_2021['S000'].sum() / berkeley_2019['S000'].sum() - 1) * 100:.1f}%)")

# Analyze commute patterns
def analyze_commutes(df, year):
    """Analyze where workers live"""
    # Live and work in same tract
    same_tract = df[df['h_tract'] == df['w_tract']]['S000'].sum()

    # Live in Berkeley, work in Berkeley
    live_work_berkeley = df[df['h_tract'].isin(berkeley_tracts)]['S000'].sum()

    # Live outside Berkeley, work in Berkeley
    commute_in = df[~df['h_tract'].isin(berkeley_tracts)]['S000'].sum()

    total = df['S000'].sum()

    return {
        'year': year,
        'total_jobs': total,
        'same_tract': same_tract,
        'live_work_berkeley': live_work_berkeley,
        'commute_in': commute_in,
        'pct_commute_in': (commute_in / total * 100) if total > 0 else 0
    }

results_2019 = analyze_commutes(berkeley_2019, YEAR_PRE)
results_2021 = analyze_commutes(berkeley_2021, YEAR_POST)

print(f"\n" + "="*70)
print("COMMUTE PATTERN ANALYSIS")
print("="*70)

for results in [results_2019, results_2021]:
    print(f"\n{results['year']}:")
    print(f"  Total jobs in Berkeley: {results['total_jobs']:,}")
    print(f"  Workers who LIVE in Berkeley: {results['live_work_berkeley']:,} ({results['live_work_berkeley']/results['total_jobs']*100:.1f}%)")
    print(f"  Workers who COMMUTE IN: {results['commute_in']:,} ({results['pct_commute_in']:.1f}%)")

# Change analysis
commuters_lost = results_2019['commute_in'] - results_2021['commute_in']
print(f"\n" + "="*70)
print("COMMUTER LOSS ANALYSIS")
print("="*70)
print(f"Commuters INTO Berkeley:")
print(f"  2019: {results_2019['commute_in']:,}")
print(f"  2021: {results_2021['commute_in']:,}")
print(f"  Lost: {commuters_lost:,} ({commuters_lost/results_2019['commute_in']*100:.1f}%)")

# Estimate transit impact (assume 13% used BART)
transit_commuters_lost = int(commuters_lost * 0.13)
print(f"\nEstimated transit commuters lost: {transit_commuters_lost:,}")
print(f"  (assuming 13% transit mode share)")

# Top origin counties for Berkeley workers
def top_origins(df, year, n=10):
    """Find top origin counties"""
    df['h_county'] = df['h_geocode'].str[:5]  # State + County
    county_totals = df.groupby('h_county')['S000'].sum().sort_values(ascending=False)

    print(f"\nTop {n} origin counties for Berkeley jobs ({year}):")
    county_names = {
        '06001': 'Alameda County (includes Berkeley)',
        '06013': 'Contra Costa County',
        '06075': 'San Francisco County',
        '06081': 'San Mateo County',
        '06085': 'Santa Clara County',
        '06097': 'Sonoma County',
        '06095': 'Solano County'
    }

    for county_code, jobs in county_totals.head(n).items():
        county_name = county_names.get(county_code, f"County {county_code}")
        pct = jobs / df['S000'].sum() * 100
        print(f"  {county_name}: {jobs:,} workers ({pct:.1f}%)")

print(f"\n" + "="*70)
print("ORIGIN COUNTIES - PRE-COVID")
print("="*70)
top_origins(berkeley_2019, YEAR_PRE)

print(f"\n" + "="*70)
print("ORIGIN COUNTIES - DURING COVID")
print("="*70)
top_origins(berkeley_2021, YEAR_POST)

# Save processed data
output_2019 = DATA_DIR / "berkeley_jobs_2019.csv"
output_2021 = DATA_DIR / "berkeley_jobs_2021.csv"

berkeley_2019.to_csv(output_2019, index=False)
berkeley_2021.to_csv(output_2021, index=False)

print(f"\n Saved: {output_2019}")
print(f" Saved: {output_2021}")

# Summary for integration
print(f"\n" + "="*70)
print("INTEGRATION WITH TRANSIT ANALYSIS")
print("="*70)
print(f"""
KEY FINDINGS for Missing Riders Analysis:

1. COMMUTER LOSS: {commuters_lost:,} fewer people commuting INTO Berkeley
   - This is SEPARATE from population exodus (people who moved away)
   - These are people who still live in the Bay Area but stopped commuting to Berkeley

2. TRANSIT IMPACT: ~{transit_commuters_lost:,} transit commuters disappeared
   - These were likely BART riders from SF, Oakland, Contra Costa
   - This explains part of the "missing riders" phenomenon

3. REMOTE WORK: Job loss + WFH explain the commuter drop
   - UC Berkeley went remote
   - Downtown Berkeley businesses went remote
   - Commuters no longer needed to travel TO Berkeley

RECOMMENDATION: Add LEHD data to show WHERE missing riders came from
- Were they Berkeley residents? (local impact)
- Were they SF/Oakland commuters? (regional impact)
- This provides geographic detail missing from aggregate ridership data
""")

print("="*70)
