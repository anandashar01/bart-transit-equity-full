#!/usr/bin/env python3
"""
AC Transit Route Network Map - Dark Matter Basemap
Shows all AC Transit routes serving Berkeley BART stations
"""

import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
from pathlib import Path
import numpy as np


# Paths
AC_TRANSIT_DIR = Path("data/raw/ac_transit")
PROCESSED_DIR = Path("data/processed")
VIS_DIR = Path("outputs")

# Load AC Transit GTFS
routes = pd.read_csv(AC_TRANSIT_DIR / "routes.txt")
stops = pd.read_csv(AC_TRANSIT_DIR / "stops.txt")
stop_times = pd.read_csv(AC_TRANSIT_DIR / "stop_times.txt")
trips = pd.read_csv(AC_TRANSIT_DIR / "trips.txt")
shapes = pd.read_csv(AC_TRANSIT_DIR / "shapes.txt")

# BART station coordinates
bart_stations = pd.DataFrame({
    'Station': ['Downtown Berkeley', 'North Berkeley', 'Ashby'],
    'lat': [37.8703, 37.8740, 37.8530],
    'lon': [-122.2680, -122.2834, -122.2697]
})

# Load connectivity data
connectivity = pd.read_csv(PROCESSED_DIR / "bart_ac_transit_connectivity.csv")
bart_stations = bart_stations.merge(connectivity[['Station', 'AC_Routes', 'Peak_Frequency', 'Income_Category']],
                                     on='Station', how='left')

# Create figure
fig = go.Figure()

# Get unique routes serving Berkeley area
# Filter stops in Berkeley area (37.85-37.88 lat, -122.30 to -122.25 lon)
berkeley_stops = stops[
    (stops['stop_lat'] >= 37.85) &
    (stops['stop_lat'] <= 37.88) &
    (stops['stop_lon'] >= -122.30) &
    (stops['stop_lon'] <= -122.25)
]

# Get trips serving Berkeley stops
berkeley_trips = stop_times[stop_times['stop_id'].isin(berkeley_stops['stop_id'])]['trip_id'].unique()

# Get routes for these trips
berkeley_route_ids = trips[trips['trip_id'].isin(berkeley_trips)]['route_id'].unique()


# Plot route shapes - SINGLE COLOR (no gradient, colorblind-friendly)
plotted_shapes = set()
for route_id in berkeley_route_ids[:30]:  # Limit to 30 routes to avoid clutter
    # Get shape_ids for this route
    route_trips = trips[trips['route_id'] == route_id]
    shape_ids = route_trips['shape_id'].dropna().unique()

    for shape_id in shape_ids[:1]:  # Just first shape per route
        if shape_id in plotted_shapes:
            continue
        plotted_shapes.add(shape_id)

        shape_data = shapes[shapes['shape_id'] == shape_id].sort_values('shape_pt_sequence')

        if len(shape_data) < 2:
            continue

        # Get route info
        route_info = routes[routes['route_id'] == route_id].iloc[0]

        fig.add_trace(go.Scattermapbox(
            lon=shape_data['shape_pt_lon'].tolist(),
            lat=shape_data['shape_pt_lat'].tolist(),
            mode='lines',
            line=dict(
                width=2,
                color='rgba(255, 165, 0, 0.7)'
            ),
            name=f"Route {route_info['route_short_name']}",
            hovertemplate=f"<b>Route {route_info['route_short_name']}</b><br>{route_info['route_long_name']}<extra></extra>",
            showlegend=True
        ))

income_colors = {'Low-Income Area': '#e74c3c', 'Non-Low-Income Area': '#2c3e50'}

for _, row in bart_stations.iterrows():
    fig.add_trace(go.Scattermapbox(
        lon=[row['lon']],
        lat=[row['lat']],
        mode='markers+text',
        marker=dict(
            size=row['AC_Routes'] * 3,  # Size by number of routes
            color=income_colors.get(row['Income_Category'], '#95a5a6'),
            opacity=0.9,
            symbol='circle'
        ),
        text=row['Station'],
        textposition='top center',
        textfont=dict(size=11, color='black', family='Arial Black'),  # Black text with bold font for visibility
        hovertemplate=(
            f"<b>{row['Station']}</b><br>" +
            f"AC Transit Routes: {row['AC_Routes']:.0f}<br>" +
            f"Peak Frequency: {row['Peak_Frequency']:.1f} trips/hr<br>" +
            f"Income Category: {row['Income_Category']}<br>" +
            '<extra></extra>'
        ),
        name=row['Station'],
        showlegend=True
    ))

# Layout with DARK MATTER basemap
fig.update_layout(
    title=dict(
        text=(
            '<b>AC Transit Route Network Serving Berkeley BART Stations</b><br>' +
            '<sub>Station Level Analysis (2024) | AC Transit GTFS Data</sub>'
        ),
        x=0.5,
        xanchor='center',
        font=dict(size=16)
    ),
    mapbox=dict(
        style='carto-darkmatter',  # DARK MATTER BASEMAP - only map background, not whole viz
        center=dict(lat=37.865, lon=-122.275),
        zoom=13
    ),
    height=700,
    margin=dict(t=120, b=250, l=50, r=50),
    showlegend=True,
    legend=dict(
        x=0.02, y=0.98,
        bgcolor='rgba(255,255,255,0.95)',
        bordercolor='black',
        borderwidth=1,
        font=dict(size=11)
    ),
    annotations=[
        dict(
            text=(
                'Orange lines show AC Transit bus routes. ' +
                'Red markers show Downtown Berkeley (low income area), gray shows North Berkeley and Ashby (higher income areas). ' +
                'Larger circles mean more routes.<br><br>' +

                'Downtown Berkeley has 18 AC Transit routes with 104 trips per hour during peak times. ' +
                'North Berkeley has 9 routes and 47 trips per hour. Ashby has 9 routes and 45 trips per hour. ' +
                'Downtown riders had twice as many bus alternatives when BART failed.<br><br>' +

                'This bus access did not protect ridership. Downtown still lost 64% of its riders. ' +
                'Both systems degraded at the same time. BART on time performance fell from 91% to 71%. AC Transit cut 15 to 30% of service.<br><br>' +

                'Data from AC Transit GTFS November 2024 and Census ACS 2019 to 2023.'
            ),
            xref='paper', yref='paper',
            x=0.5, y=-0.18,
            xanchor='center', yanchor='top',
            showarrow=False,
            font=dict(size=10),
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='black',
            borderwidth=1,
            align='left'
        )
    ]
)

# Save
output_path = VIS_DIR / "ac_transit_route_network.html"
fig.write_html(output_path)


