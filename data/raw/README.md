# Raw Data Sources

This folder contains unmodified data from authoritative public sources.

## ac_transit/
**Source:** AC Transit GTFS Feed (November 2024)
**URL:** https://www.actransit.org/planning-focus/data-resource-center
**Contents:** routes.txt, stops.txt, trips.txt, stop_times.txt, shapes.txt
**License:** Public domain (government data)
**Used for:** Calculating bus route connectivity and service frequency

## census/
**Source:** U.S. Census Bureau TIGER/Line Shapefiles (2021)
**URL:** https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
**Contents:** Census tract and block group boundaries for California
**License:** Public domain (U.S. government data)
**Used for:** Spatial aggregation of demographics to BART station catchment areas

## lehd/
**Source:** U.S. Census LEHD LODES (Longitudinal Employer-Household Dynamics)
**URL:** https://lehd.ces.census.gov/data/
**Contents:** Origin-destination employment statistics (2019, 2021)
**License:** Public domain (U.S. government data)
**Used for:** Exploratory analysis (NOT used in final analysis - see Methods section for explanation)

## Note on BART Data
BART ridership and performance data are manually transcribed from quarterly reports published at:
https://www.bart.gov/about/reports

These are not included as raw files because they are extracted from PDF reports.
Processed CSV files are in `data/processed/` with full source citations.
