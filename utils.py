import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Optional

def aggregate_data_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate data by year, summing up all pathogen data.
    
    Args:
        df: DataFrame with research data
        
    Returns:
        DataFrame with data aggregated by year
    """
    # Ensure Total column exists
    if "Total" not in df.columns:
        df = df.copy()
        df["Total"] = df["Positive"] + df["Negative"]
        
    return df.groupby('Year').agg({
        'Positive': 'sum',
        'Negative': 'sum',
        'Total': 'sum'
    }).reset_index()

def aggregate_data_by_pathogen(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate data by pathogen, summing up all year data.
    
    Args:
        df: DataFrame with research data
        
    Returns:
        DataFrame with data aggregated by pathogen
    """
    # Ensure Total column exists
    if "Total" not in df.columns:
        df = df.copy()
        df["Total"] = df["Positive"] + df["Negative"]
        
    return df.groupby('Pathogen').agg({
        'Positive': 'sum',
        'Negative': 'sum',
        'Total': 'sum'
    }).reset_index()

def calculate_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate various statistics from the research data.
    
    Args:
        df: DataFrame with research data
        
    Returns:
        Dictionary with calculated statistics
    """
    # Ensure Total column exists
    if "Total" not in df.columns:
        df = df.copy()
        df["Total"] = df["Positive"] + df["Negative"]  # Total is sum of positive and negative only
    
    total_samples = df["Total"].sum()
    stats = {
        'total_positive': df['Positive'].sum(),
        'total_negative': df['Negative'].sum(),
        'total_samples': total_samples,
        'positive_ratio': df['Positive'].sum() / total_samples if total_samples > 0 else 0,
        'negative_ratio': df['Negative'].sum() / total_samples if total_samples > 0 else 0,
        'pathogen_count': df['Pathogen'].nunique(),
        'year_range': (df['Year'].min(), df['Year'].max()),
        'years_count': df['Year'].nunique(),
        
        # Per pathogen stats
        'pathogen_stats': aggregate_data_by_pathogen(df).to_dict('records'),
        
        # Per year stats
        'year_stats': aggregate_data_by_year(df).to_dict('records')
    }
    
    return stats

def create_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a summary table with statistics for each pathogen.
    
    Args:
        df: DataFrame with research data
        
    Returns:
        DataFrame with summary statistics
    """
    # Ensure Total column exists
    if "Total" not in df.columns:
        df = df.copy()
        df["Total"] = df["Positive"] + df["Negative"]
    
    # Group by pathogen and calculate summary statistics
    summary = df.groupby('Pathogen').agg({
        'Positive': ['sum', 'mean', 'max'],
        'Negative': ['sum', 'mean', 'max'],
        'Total': ['sum', 'mean', 'max']
    })
    
    # Flatten the multi-level column index
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    
    # Calculate percentages
    summary['Positive_pct'] = (summary['Positive_sum'] / summary['Total_sum'] * 100).round(1)
    summary['Negative_pct'] = (summary['Negative_sum'] / summary['Total_sum'] * 100).round(1)
    
    return summary.reset_index()

def create_heatmap(df: pd.DataFrame, value_column: str, colors: Dict[str, str]) -> go.Figure:
    """
    Create a heatmap visualization of the data.
    
    Args:
        df: DataFrame with research data
        value_column: Column to use for heatmap values ('Positive', 'Negative', 'Total')
        colors: Dictionary of colors to use
        
    Returns:
        Plotly figure object
    """
    # Ensure Total column exists if needed
    if value_column == "Total" and "Total" not in df.columns:
        df = df.copy()
        df["Total"] = df["Positive"] + df["Negative"]
    
    # Pivot the data for the heatmap
    pivot_df = df.pivot_table(
        values=value_column,
        index='Pathogen',
        columns='Year',
        aggfunc='sum',
        fill_value=0
    )
    
    # Create the heatmap
    color_key = value_column.lower()
    if color_key not in colors and color_key == "total":
        color_key = "total"  # Default for Total
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale=[
            [0, 'white'],
            [1, colors[color_key]]
        ],
        showscale=True,
        text=pivot_df.values,
        hovertemplate='Pathogen: %{y}<br>Year: %{x}<br>%{z} %{text}<extra></extra>',
        texttemplate='%{z}',
        hoverongaps=False
    ))
    
    # Update layout
    fig.update_layout(
        title=f'{value_column} Counts by Year and Pathogen',
        xaxis_title='Year',
        yaxis_title='Pathogen',
        height=600,
        width=900,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    return fig

def create_pie_chart(df: pd.DataFrame, colors: Dict[str, str]) -> go.Figure:
    """
    Create a pie chart showing the distribution of positive and negative counts only.
    
    Args:
        df: DataFrame with research data
        colors: Dictionary of colors to use
        
    Returns:
        Plotly figure object
    """
    # Calculate total values
    totals = {
        'Positive': df['Positive'].sum(),
        'Negative': df['Negative'].sum()
    }
    
    # Create pie chart without Unknown
    marker_colors = [colors['positive'], colors['negative']]
    
    fig = go.Figure(data=go.Pie(
        labels=list(totals.keys()),
        values=list(totals.values()),
        marker_colors=marker_colors,
        textinfo='label+percent',
        hoverinfo='label+value',
        hole=0.4,
        pull=[0.05, 0]  # Pull out the positive slice slightly
    ))
    
    # Update layout
    fig.update_layout(
        title='Distribution of Test Results',
        height=500,
        annotations=[{
            'text': f"Total: {sum(totals.values())}",
            'showarrow': False,
            'font': {'size': 16},
            'x': 0.5,
            'y': 0.5
        }]
    )
    
    return fig

def create_time_series(df: pd.DataFrame, colors: Dict[str, str]) -> go.Figure:
    """
    Create a time series visualization of the data by year.
    
    Args:
        df: DataFrame with research data
        colors: Dictionary of colors to use
        
    Returns:
        Plotly figure object
    """
    # Aggregate data by year
    year_data = aggregate_data_by_year(df)
    
    # Create figure
    fig = go.Figure()
    
    # Add traces for each data type
    fig.add_trace(go.Scatter(
        x=year_data['Year'],
        y=year_data['Positive'],
        mode='lines+markers',
        name='Positive',
        line=dict(color=colors['positive'], width=3),
        marker=dict(size=8),
        hovertemplate='Year: %{x}<br>Positive: %{y}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=year_data['Year'],
        y=year_data['Negative'],
        mode='lines+markers',
        name='Negative',
        line=dict(color=colors['negative'], width=3),
        marker=dict(size=8),
        hovertemplate='Year: %{x}<br>Negative: %{y}<extra></extra>'
    ))
    
    # Add Total trace
    fig.add_trace(go.Scatter(
        x=year_data['Year'],
        y=year_data['Total'],
        mode='lines+markers',
        name='Total',
        line=dict(color=colors['total'], width=3, dash='dot'),
        marker=dict(size=8),
        hovertemplate='Year: %{x}<br>Total: %{y}<extra></extra>'
    ))
    
    # Add labels for specific data points if desired
    for i, year in enumerate(year_data['Year']):
        if i % 3 == 0:  # Label every 3rd year to avoid clutter
            fig.add_annotation(
                x=year,
                y=year_data['Total'].iloc[i],
                text=str(year_data['Total'].iloc[i]),
                showarrow=True,
                arrowhead=1,
                yshift=10
            )
    
    # Update layout
    fig.update_layout(
        title='Trends Over Time',
        xaxis_title='Year',
        yaxis_title='Count',
        height=500,
        width=900,
        margin=dict(l=60, r=60, t=80, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes
    fig.update_xaxes(
        tickangle=45,
        nticks=len(year_data['Year'])
    )
    
    fig.update_yaxes(
        rangemode="tozero"
    )
    
    return fig 