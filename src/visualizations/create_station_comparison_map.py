#!/usr/bin/env python3
"""
Berkeley BART Station Comparison Map - MAP 1 for Report
Choropleth showing transit dependency (% no vehicle) with station overlays
"""

import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
from pathlib import Path


# Load geospatial data
PROCESSED_DIR = Path("data/processed")
tracts_geo = gpd.read_file(PROCESSED_DIR / "berkeley_tracts_with_demographics.geojson")
catchments = gpd.read_file(PROCESSED_DIR / "bart_station_catchments.geojson")

# Station data with all metrics
stations = pd.DataFrame({
    'Station': ['Downtown Berkeley', 'North Berkeley', 'Ashby'],
    'lat': [37.8703, 37.8740, 37.8530],
    'lon': [-122.2680, -122.2834, -122.2697],

    # Ridership (2019 vs 2024)
    'Ridership_2019': [11566, 5894, 7522],
    'Ridership_2024': [4170, 2248, 2264],

    # AC Transit connectivity
    'AC_Routes': [18, 9, 9],
    'Peak_Frequency': [103.6, 47.0, 44.5],

    # Demographics
    'Median_Income': [63596, 95556, 103532],
    'Pct_No_Vehicle': [33.2, 15.6, 14.9],
    'Income_Category': ['Low-Income Area', 'Non-Low-Income Area', 'Non-Low-Income Area']
})

# Calculate metrics
stations['Loss'] = stations['Ridership_2019'] - stations['Ridership_2024']
stations['Pct_Loss'] = ((stations['Ridership_2019'] - stations['Ridership_2024']) / stations['Ridership_2019'] * 100).round(1)
stations['Retention'] = (100 - stations['Pct_Loss']).round(1)

# Create figure
fig = go.Figure()

# CHOROPLETH LAYER: % households without vehicle (transit dependency)
fig.add_trace(go.Choroplethmapbox(
    geojson=tracts_geo.__geo_interface__,
    locations=tracts_geo.index,
    z=tracts_geo['pct_no_vehicle'],
    colorscale='YlOrRd',  # Yellow-Orange-Red
    zmin=0,
    zmax=50,
    marker_opacity=0.6,
    marker_line_width=0.5,
    marker_line_color='white',
    colorbar=dict(
        title=dict(
            text="% Households<br>Without Vehicle",
            font=dict(size=13, family='Arial')
        ),
        x=1.02,
        len=0.7,
        thickness=18,
        ticksuffix="%",
        tickfont=dict(size=11)
    ),
    hovertemplate=(
        '<b>Census Tract</b><br>' +
        'Transit Dependency: %{z:.1f}%<br>' +
        'Median Income: $%{customdata[0]:,.0f}<br>' +
        '<extra></extra>'
    ),
    customdata=tracts_geo[['median_household_income']].values,
    name='Transit Dependency',
    showlegend=False
))

# Catchment boundaries (0.5-mile walkable buffers) - COMMENTED OUT FOR CLEANER VISUALIZATION
# The 0.5-mile buffer methodology is still used for income classification (explained in methods/caption)
# but the visual boundary lines clutter the map. Uncomment if you want to see the circles.
# for idx, row in catchments.iterrows():
#     if row.geometry.geom_type == 'Polygon':
#         coords = list(row.geometry.exterior.coords)
#         lons = [c[0] for c in coords]
#         lats = [c[1] for c in coords]
#
#         fig.add_trace(go.Scattermapbox(
#             lon=lons,
#             lat=lats,
#             mode='lines',
#             line=dict(width=2, color='rgba(0,0,255,0.8)'),
#             name=f"{row['Station']}<br>0.5-mi Buffer",
#             hoverinfo='name',
#             showlegend=True
#         ))

# STATION MARKERS: sized by ridership loss, colored by income (RED = low-income, DARK BLUE = higher-income)
colors = {'Low-Income Area': '#e74c3c', 'Non-Low-Income Area': '#2c3e50'}

for _, row in stations.iterrows():
    fig.add_trace(go.Scattermapbox(
        lon=[row['lon']],
        lat=[row['lat']],
        mode='markers+text',
        marker=dict(
            size=row['Loss'] / 100,  # Size by absolute loss
            color=colors[row['Income_Category']],
            opacity=0.95,
            sizemode='diameter'
        ),
        text=row['Station'].replace(' Berkeley', '<br>Berkeley'),
        textposition='top center',
        textfont=dict(size=13, color='white', family='Arial Black'),
        hovertemplate=(
            f"<b>{row['Station']}</b><br><br>" +
            f"<b>RIDERSHIP (2019→2024):</b><br>" +
            f"  2019: {row['Ridership_2019']:,} daily<br>" +
            f"  2024: {row['Ridership_2024']:,} daily<br>" +
            f"  <b>Lost: {row['Loss']:,} ({row['Pct_Loss']:.1f}%)</b><br>" +
            f"  Retained: {row['Retention']:.1f}%<br><br>" +

            f"<b>AC TRANSIT ACCESS:</b><br>" +
            f"  {row['AC_Routes']} bus routes<br>" +
            f"  {row['Peak_Frequency']:.1f} trips/hr (peak)<br><br>" +

            f"<b>DEMOGRAPHICS:</b><br>" +
            f"  Median Income: ${row['Median_Income']:,}<br>" +
            f"  No Vehicle: {row['Pct_No_Vehicle']:.1f}%<br>" +
            f"  {row['Income_Category']}<br>" +
            '<extra></extra>'
        ),
        name=row['Station'],
        showlegend=True
    ))

# Layout
fig.update_layout(
    title=dict(
        text=(
            '<b>Berkeley BART Stations: Multimodal Connectivity Paradox</b><br>' +
            '<sub>Census Tract Level | ACS 2019-2023</sub>'
        ),
        x=0.5,
        xanchor='center',
        font=dict(size=15, family='Arial')
    ),
    mapbox=dict(
        style='carto-positron',
        center=dict(lat=37.865, lon=-122.27),
        zoom=12.3
    ),
    height=750,
    margin=dict(t=120, b=320, l=50, r=150),
    legend=dict(
        title=dict(text='<b>BART Stations</b>', font=dict(size=12)),
        x=0.02,
        y=0.98,
        bgcolor='rgba(255,255,255,0.95)',
        bordercolor='black',
        borderwidth=1,
        font=dict(size=11)
    ),
    annotations=[
        dict(
            text=(
                'Background color shows households without vehicles by census tract. Darker red means more transit dependency. ' +
                'Red markers show Downtown Berkeley (low income area), dark blue shows North Berkeley and Ashby (higher income areas). ' +
                'Larger circles mean more riders lost.<br><br>' +

                'Downtown Berkeley has 33% no vehicle households and 18 AC Transit routes. ' +
                'North Berkeley and Ashby have 15% no vehicle households and 9 bus routes each. ' +
                'All three stations lost about 65% of riders from 2019 to 2024. Better bus access did not protect against losses.<br><br>' +

                'Both systems failed together. BART on time performance dropped from 91% to 71%. AC Transit cut service by 15 to 30%. ' +
                'When both degrade at once, more bus routes provide no benefit.<br><br>' +

                'Downtown Berkeley appears low income largely because UC Berkeley students report very low incomes while enrolled but often have family support. ' +
                'This differs from permanent economic disadvantage.<br><br>' +

                'Data from US Census ACS 2019 to 2023, BART Quarterly Reports 2019 to 2024, and AC Transit GTFS November 2024.'
            ),
            xref='paper', yref='paper',
            x=0.5, y=-0.2,
            xanchor='center', yanchor='top',
            showarrow=False,
            font=dict(size=10, family='Arial'),
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='black',
            borderwidth=1,
            align='left'
        )
    ]
)

# Save
output_dir = Path("supporting_analysis")
output_dir.mkdir(exist_ok=True, parents=True)
output_path = output_dir / "multimodal_connectivity_paradox.html"
fig.write_html(output_path)

