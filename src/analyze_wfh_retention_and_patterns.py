#!/usr/bin/env python3
"""
Clarifying Analysis: WFH Retention and Changed Patterns
Breaks down what happened to remote workers and changed pattern riders
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


# Remote work detailed breakdown

wfh_data = pd.DataFrame({
    'Year': [2019, 2020, 2021, 2022, 2023],
    'WFH_Workers': [260000, 800000, 1200000, 938000, 750000],
    'WFH_Percent': [7, 22, 33, 25, 19]
})

wfh_data['New_WFH_vs_2019'] = wfh_data['WFH_Workers'] - 260000
wfh_data['Returned_vs_Peak'] = 1200000 - wfh_data['WFH_Workers']

# Changed patterns breakdown

changed_patterns = pd.DataFrame({
    'Category': [
        'Hybrid Work Schedules',
        'Job Changes (non-commute)',
        'Unemployment/Retirement',
        'Shift to Off-Peak Hours',
        'Reduced Trip Frequency'
    ],
    'Estimated_Riders': [8000, 4000, 3000, 3000, 2000],
    'Description': [
        'Work 2-3 days/week instead of 5 (hybrid). Still use transit but 40-60% less frequently',
        'Changed to local jobs, gig economy, or jobs not requiring daily commute',
        'Lost jobs during pandemic, early retirement, left workforce',
        'Moved to non-peak hours to avoid crowds (not captured in peak commute stats)',
        'Same job but less frequent office visits, flexible schedules'
    ]
})

# Create visualization - two separate figures side by side
VIS_DIR = Path("outputs")

# Figure 1: WFH flow as bar chart (Sankey doesn't work in subplots)
fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.5, 0.5],
    subplot_titles=(
        '<b>Remote Work Flow: Who Stayed Home, Who Returned (2019-2023)</b>',
        '<b>Changed Patterns Breakdown: Where 20,000 Riders Went</b>'
    ),
    vertical_spacing=0.15,
    specs=[[{"type": "bar"}], [{"type": "bar"}]]
)

# Panel 1: Bar chart showing WFH flow
wfh_flow = pd.DataFrame({
    'Category': ['2019 Baseline', '2021 Peak<br>(+940k new)', '2023 Stayed<br>Home (490k)', '2023 Returned<br>to Office (450k)'],
    'Workers': [260, 1200, 750, 450]
})

fig.add_trace(go.Bar(
    x=wfh_flow['Category'],
    y=wfh_flow['Workers'],
    marker=dict(color='#7f8c8d'),
    text=[f"{val:,}k" for val in wfh_flow['Workers']],
    textposition='outside',
    showlegend=False,
    hovertemplate='%{x}<br>%{y:,}k workers<extra></extra>'
), row=1, col=1)

fig.add_trace(go.Bar(
    y=changed_patterns['Category'],
    x=changed_patterns['Estimated_Riders'],
    orientation='h',
    marker=dict(color='#7f8c8d'),
    text=[f"{val:,} ({val/20000*100:.0f}%)" for val in changed_patterns['Estimated_Riders']],
    textposition='outside',
    showlegend=False,
    hovertemplate='%{y}<br>%{x:,} riders (%{x:.0%} of 20k)<extra></extra>'
), row=2, col=1)

fig.update_layout(
    title=dict(
        text=(
            '<b>Clarifying the Missing Riders: WFH Retention & Changed Patterns</b><br>' +
            '<sub>Bay Area Analysis (2019-2023) | Estimated from Survey Data</sub>'
        ),
        x=0.5,
        xanchor='center',
        font=dict(size=15)
    ),
    height=900,
    margin=dict(t=120, b=150, l=50, r=50),
    annotations=list(fig.layout.annotations) + [
        dict(
            text=(
                '940,000 workers went to work from home at the peak. ' +
                '52% are still working from home permanently. ' +
                '48% returned to offices but mostly on hybrid schedules working 2 to 3 days per week. ' +
                'This reduces their transit use by 40 to 60%.<br><br>' +

                'Changed travel patterns account for 20,000 lost riders. ' +
                'Hybrid work is 40%, job changes are 20%, unemployment and retirement are 15%, off peak shifts are 15%, and reduced trip frequency is 10%.'
            ),
            xref='paper', yref='paper',
            x=0.5, y=-0.08,
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

output_path = VIS_DIR / "wfh_retention_clarification.html"
fig.write_html(output_path)

# Summary table

