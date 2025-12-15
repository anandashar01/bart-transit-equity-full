#!/usr/bin/env python3
"""
Standalone Temporal Service Quality Chart
Shows OTP and EWT trends 2018-2025 clearly
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


# Load data
DATA_DIR = Path("data/processed")
VIS_DIR = Path("outputs")

historical_perf = pd.read_csv(DATA_DIR / "bart_historical_performance_metrics.csv")
temporal_equity = pd.read_csv(DATA_DIR / "temporal_equity_analysis.csv")

# Prepare data
otp_data = historical_perf.copy()
otp_data['Year'] = otp_data['Fiscal_Year'].astype(int)

# Create figure with 2 charts stacked
fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.5, 0.5],
    subplot_titles=(
        '<b>On-Time Performance Degradation (2018-2025)</b>',
        '<b>Excess Wait Time by Income Category (2018-2025)</b>'
    ),
    vertical_spacing=0.15
)

# ============================================================================
# PANEL 1: OTP TIMELINE
# ============================================================================

# NO background shading - instructor said remove colors

fig.add_trace(go.Scatter(
    x=otp_data['Year'],
    y=otp_data['On_Time_Performance_%'],
    mode='lines+markers+text',
    line=dict(color='#7f8c8d', width=4),
    marker=dict(size=12, color='#7f8c8d'),
    text=[f"{val:.1f}%" for val in otp_data['On_Time_Performance_%']],
    textposition='top center',
    textfont=dict(size=11, color='#7f8c8d'),
    name='On-Time Performance',
    hovertemplate='%{x}: %{y:.1f}% OTP<extra></extra>'
), row=1, col=1)

# Goal line
fig.add_shape(
    type="line", x0=2017.5, x1=2024.5, y0=91, y1=91,
    line=dict(color="green", width=3, dash="dash"),
    row=1, col=1
)

# Goal line label
fig.add_annotation(
    x=2024.3, y=91, text="91% Goal", showarrow=False,
    font=dict(size=10, color='green'), xanchor="left", row=1, col=1
)

# Crisis annotation
fig.add_annotation(
    x=2023, y=71, text="<b>CRISIS LOW<br>71% OTP<br>(-20 points)</b>",
    showarrow=True, arrowhead=2, arrowcolor='red',
    font=dict(size=10, color='red'), row=1, col=1,
    ax=40, ay=-40
)

# Recovery annotation
fig.add_annotation(
    x=2024, y=92, text="<b>RECOVERY<br>92% OTP<br>(+21 points)</b>",
    showarrow=True, arrowhead=2, arrowcolor='green',
    font=dict(size=10, color='green'), row=1, col=1,
    ax=-40, ay=-40
)

ewt_by_income = temporal_equity.groupby(['Fiscal_Year', 'Income_Category'], as_index=False)['Estimated_EWT_Min'].mean()
ewt_by_income['Year'] = ewt_by_income['Fiscal_Year'].astype(int)
for income_cat in ['Low-Income Area', 'Non-Low-Income Area']:
    data = ewt_by_income[ewt_by_income['Income_Category'] == income_cat]

    fig.add_trace(go.Scatter(
        x=data['Year'],
        y=data['Estimated_EWT_Min'],
        mode='lines+markers',
        line=dict(color='#7f8c8d', width=4),
        marker=dict(size=11),
        name=income_cat,
        hovertemplate='%{x}: %{y:.1f} min EWT<extra></extra>'
    ), row=2, col=1)

# Peak annotation
fig.add_annotation(
    x=2023, y=6.6, text="<b>PEAK EWT<br>6.6 minutes<br>(3× scheduled)</b>",
    showarrow=True, arrowhead=2, arrowcolor='red',
    font=dict(size=10, color='red'), row=2, col=1,
    ax=40, ay=-40
)

fig.update_xaxes(
    title_text="<b>Year</b>",
    showgrid=True, gridwidth=1, gridcolor='lightgray',
    range=[2017.5, 2024.5],
    row=1, col=1
)

fig.update_xaxes(
    title_text="<b>Year</b>",
    showgrid=True, gridwidth=1, gridcolor='lightgray',
    range=[2017.5, 2024.5],
    row=2, col=1
)

fig.update_yaxes(
    title_text="<b>On-Time Performance (%)</b>",
    showgrid=True, gridwidth=1, gridcolor='lightgray',
    range=[65, 100],
    row=1, col=1
)

fig.update_yaxes(
    title_text="<b>Excess Wait Time (minutes)</b>",
    showgrid=True, gridwidth=1, gridcolor='lightgray',
    range=[0, 8],
    row=2, col=1
)

fig.update_layout(
    title=dict(
        text=(
            '<b>BART Service Quality Degradation and Recovery (2018-2025)</b><br>' +
            '<sub>System Level | Annual Data (2018-2024)</sub>'
        ),
        x=0.5,
        xanchor='center',
        font=dict(size=16)
    ),
    height=900,
    margin=dict(t=120, b=320, l=80, r=80),
    showlegend=True,
    legend=dict(
        title=dict(text='<b>Income Categories</b>', font=dict(size=12)),
        x=0.02,
        y=0.35,
        bgcolor='rgba(255,255,255,0.95)',
        bordercolor='black',
        borderwidth=1,
        font=dict(size=11)
    ),
    annotations=list(fig.layout.annotations) + [
        dict(
            text=(
                'BART on time performance dropped from 91% in 2018 to 71% in 2023. ' +
                'Then it recovered to 92% in 2024, exceeding the 91% goal. ' +
                'Riders experienced almost no excess wait time in 2018 and 2019 when trains ran on schedule. ' +
                'This spiked to 6.6 minutes by 2023 as trains ran late, then dropped back to nearly zero by 2024.<br><br>' +

                'Service degradation affected both income groups equally. Both got the same poor service from 2022 to 2023. ' +
                'The difference lies in who could leave versus who stayed. ' +
                'Wealthier riders switched to cars or work from home. ' +
                'Transit dependent riders at Downtown Berkeley had fewer alternatives and showed 36% retention.<br><br>' +

                'The 2022 to 2023 spike came from a staffing crisis, deferred maintenance, and labor disputes. ' +
                'Ridership was already down 70%, and then service degraded further. ' +
                'By 2024, BART restored service to 92% on time performance, but riders still have not returned.<br><br>' +

                'Data from BART Quarterly Performance Reports 2018 to 2024.'
            ),
            xref='paper', yref='paper',
            x=0.5, y=-0.18,
            xanchor='center', yanchor='top',
            showarrow=False,
            font=dict(size=10, family='Arial', color='#222'),
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#999',
            borderwidth=1,
            borderpad=12,
            align='left',
            width=1100
        )
    ]
)

# Save
output_path = VIS_DIR / "temporal_service_quality_chart.html"
fig.write_html(output_path)


