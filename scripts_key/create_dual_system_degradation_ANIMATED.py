#!/usr/bin/env python3
"""
Dual System Degradation Analysis - WITH ANIMATION
Shows BART AND AC Transit both degraded during COVID
NOW WITH TIME SLIDER for Track B animation requirement
"""

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


VIS_DIR = Path("maps")
VIS_DIR.mkdir(exist_ok=True, parents=True)

# BART temporal data
bart_data = pd.DataFrame({
    'Year': [2018, 2019, 2020, 2021, 2022, 2023, 2024],
    'BART_OTP_%': [91.4, 90.1, 88.5, 85.0, 76.0, 71.0, 92.0],
    'BART_Ridership_%': [105.1, 100.0, 80.2, 12.4, 21.0, 36.0, 35.0],
    'Period': ['Pre-COVID', 'Pre-COVID', 'During-COVID', 'During-COVID', 'Post-COVID', 'Post-COVID', 'Post-COVID']
})

# AC Transit data
ac_transit_data = pd.DataFrame({
    'Year': [2019, 2020, 2021, 2022, 2023, 2024],
    'AC_Ridership_%': [100.0, 28.0, 28.0, 60.7, 64.1, 75.2],
    'AC_Service_%': [100, 85, 70, 85, 95, 100],
    'Period': ['Pre-COVID', 'During-COVID', 'During-COVID', 'Post-COVID', 'Post-COVID', 'Post-COVID']
})

# Create figure with animation slider
fig = go.Figure()

# Add all years as separate traces (for animation frames)
years = sorted(set(bart_data['Year'].tolist() + ac_transit_data['Year'].tolist()))

# BART ridership trace
fig.add_trace(go.Scatter(
    x=bart_data['Year'],
    y=bart_data['BART_Ridership_%'],
    mode='lines+markers+text',
    line=dict(color='#95a5a6', width=4),
    marker=dict(size=12),
    text=[f'{val:.1f}%' for val in bart_data['BART_Ridership_%']],
    textposition='top center',
    textfont=dict(size=10, color='#95a5a6'),
    name='BART Berkeley Stations',
    hovertemplate='Year %{x}<br>%{y:.1f}% of 2019 ridership<extra></extra>'
))

# AC Transit ridership trace
fig.add_trace(go.Scatter(
    x=ac_transit_data['Year'],
    y=ac_transit_data['AC_Ridership_%'],
    mode='lines+markers+text',
    line=dict(color='#7f8c8d', width=4),
    marker=dict(size=12),
    text=[f'{val:.1f}%' for val in ac_transit_data['AC_Ridership_%']],
    textposition='bottom center',
    textfont=dict(size=10, color='#7f8c8d'),
    name='AC Transit System',
    hovertemplate='Year %{x}<br>%{y:.1f}% of 2019 ridership<extra></extra>'
))

# Baseline line
fig.add_shape(
    type="line", x0=2018.5, x1=2024.5, y0=100, y1=100,
    line=dict(color="gray", width=2, dash="dash")
)

# Create frames for animation
frames = []
for year in years:
    bart_slice = bart_data[bart_data['Year'] <= year]
    ac_slice = ac_transit_data[ac_transit_data['Year'] <= year]

    frame = go.Frame(
        data=[
            go.Scatter(
                x=bart_slice['Year'],
                y=bart_slice['BART_Ridership_%'],
                mode='lines+markers+text',
                line=dict(color='#95a5a6', width=4),
                marker=dict(size=12),
                text=[f'{val:.1f}%' for val in bart_slice['BART_Ridership_%']],
                textposition='top center',
                textfont=dict(size=10, color='#95a5a6'),
                name='BART Berkeley Stations'
            ),
            go.Scatter(
                x=ac_slice['Year'],
                y=ac_slice['AC_Ridership_%'],
                mode='lines+markers+text',
                line=dict(color='#7f8c8d', width=4),
                marker=dict(size=12),
                text=[f'{val:.1f}%' for val in ac_slice['AC_Ridership_%']],
                textposition='bottom center',
                textfont=dict(size=10, color='#7f8c8d'),
                name='AC Transit System'
            )
        ],
        name=str(year),
        layout=go.Layout(
            title_text=f"<b>Dual System Degradation: BART & AC Transit Ridership (Up to {year})</b>"
        )
    )
    frames.append(frame)

fig.frames = frames

# Add play and pause buttons
fig.update_layout(
    title=dict(
        text='<b>Dual System Degradation: BART & AC Transit Ridership (2018-2024)</b><br>' +
             '<sub>System-Level | Annual Data (2018-2024) | Normalized to 2019 Baseline | Interactive Time Slider</sub>',
        x=0.5,
        xanchor='center',
        font=dict(size=16)
    ),
    xaxis=dict(
        title='<b>Year</b>',
        range=[2018.5, 2024.5],
        showgrid=True,
        gridcolor='lightgray'
    ),
    yaxis=dict(
        title='<b>Ridership (% of 2019 Baseline)</b>',
        range=[0, 120],
        showgrid=True,
        gridcolor='lightgray'
    ),
    height=600,
    margin=dict(t=150, b=200, l=80, r=80),
    showlegend=True,
    legend=dict(
        x=0.02, y=0.98,
        bgcolor='rgba(255,255,255,0.95)',
        bordercolor='black',
        borderwidth=1
    ),
    updatemenus=[
        dict(
            type='buttons',
            showactive=False,
            buttons=[
                dict(label='▶ Play',
                     method='animate',
                     args=[None, dict(frame=dict(duration=800, redraw=True),
                                     fromcurrent=True,
                                     mode='immediate')]),
                dict(label='⏸ Pause',
                     method='animate',
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                       mode='immediate')])
            ],
            x=0.1,
            y=1.15,
            xanchor='left',
            yanchor='top'
        )
    ],
    sliders=[{
        'active': len(frames) - 1,
        'yanchor': 'top',
        'y': -0.2,
        'xanchor': 'left',
        'currentvalue': {
            'prefix': 'Year: ',
            'visible': True,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        'pad': {'b': 10, 't': 10},
        'len': 0.9,
        'x': 0.05,
        'steps': [
            {
                'args': [[f.name], {
                    'frame': {'duration': 0, 'redraw': True},
                    'mode': 'immediate'
                }],
                'label': str(year),
                'method': 'animate'
            }
            for year, f in zip(years, frames)
        ]
    }],
    annotations=[
        dict(
            text=(
                'Both BART and AC Transit lost roughly 72% of their ridership during COVID. ' +
                'BART Berkeley stations dropped to 12.4% of 2019 levels in 2021, ' +
                'while AC Transit system wide dropped to 28% of 2019 levels. ' +
                'This parallel collapse explains why having more bus routes did not protect Downtown Berkeley. ' +
                'When both systems degrade at the same time, multimodal connections provide no backup.<br><br>' +

                'Use the slider above to watch the ridership collapse and partial recovery year by year. ' +
                'The animation shows how both systems followed similar trajectories through the pandemic, ' +
                'reinforcing that this was a simultaneous failure rather than one system compensating for the other.<br><br>' +

                'Data come from BART Quarterly Performance Reports for 2018 through 2024 and AC Transit annual ridership reports. ' +
                'All ridership figures are normalized to 2019 baseline levels to allow direct comparison. ' +
                'The interactive time slider allows year by year comparison of how both systems changed together.'
            ),
            xref='paper', yref='paper',
            x=0.5, y=-0.35,
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
output_path = VIS_DIR / "MAP2_Dual_System_Degradation.html"
fig.write_html(output_path)

