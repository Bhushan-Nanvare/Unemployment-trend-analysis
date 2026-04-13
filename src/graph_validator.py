"""
graph_validator.py

GRAPH VALIDATION LAYER
======================

Validates data before plotting and adds quality indicators to all graphs.

Features:
- Pre-plot data validation
- Data source labels
- Quality score indicators
- Historical vs forecast styling
- Missing data warnings
- Data age indicators

Author: Refactored System Architecture
Date: 2026-04-13
Version: 2.0.0
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Tuple, List, Optional, Dict
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def validate_before_plot(
    df: pd.DataFrame,
    value_col: str,
    year_col: str = "Year"
) -> Tuple[bool, List[str]]:
    """
    Validate data is suitable for plotting.
    
    Args:
        df: DataFrame to validate
        value_col: Name of the value column
        year_col: Name of the year column
    
    Returns:
        (is_valid, list_of_warnings)
    """
    warnings = []
    
    # Check if DataFrame is empty
    if df.empty:
        warnings.append("❌ ERROR: No data to plot")
        return False, warnings
    
    # Check if required columns exist
    if value_col not in df.columns:
        warnings.append(f"❌ ERROR: Column '{value_col}' not found")
        return False, warnings
    
    if year_col not in df.columns:
        warnings.append(f"❌ ERROR: Column '{year_col}' not found")
        return False, warnings
    
    # Check if all values are missing
    if df[value_col].isna().all():
        warnings.append(f"❌ ERROR: All values in '{value_col}' are missing")
        return False, warnings
    
    # Check for missing values (warning only)
    missing_count = df[value_col].isna().sum()
    if missing_count > 0:
        missing_pct = (missing_count / len(df)) * 100
        warnings.append(f"⚠️  WARNING: {missing_count} missing values ({missing_pct:.1f}%)")
    
    # Check for negative values (warning only)
    if (df[value_col] < 0).any():
        neg_count = (df[value_col] < 0).sum()
        warnings.append(f"⚠️  WARNING: {neg_count} negative values found")
    
    # Check for outliers (informational)
    if len(df) >= 5:
        q1 = df[value_col].quantile(0.25)
        q3 = df[value_col].quantile(0.75)
        iqr = q3 - q1
        outliers = ((df[value_col] < (q1 - 1.5 * iqr)) | 
                   (df[value_col] > (q3 + 1.5 * iqr))).sum()
        if outliers > 0:
            warnings.append(f"ℹ️  INFO: {outliers} statistical outliers detected")
    
    # All critical checks passed
    return True, warnings


def validate_time_series(
    df: pd.DataFrame,
    value_col: str,
    year_col: str = "Year"
) -> Tuple[bool, List[str]]:
    """
    Validate time series data for plotting.
    
    Args:
        df: DataFrame to validate
        value_col: Name of the value column
        year_col: Name of the year column
    
    Returns:
        (is_valid, list_of_warnings)
    """
    is_valid, warnings = validate_before_plot(df, value_col, year_col)
    
    if not is_valid:
        return False, warnings
    
    # Check for gaps in time series
    df_sorted = df.sort_values(year_col)
    years = df_sorted[year_col].values
    
    if len(years) > 1:
        year_diffs = pd.Series(years).diff().dropna()
        max_gap = year_diffs.max()
        
        if max_gap > 1:
            warnings.append(f"⚠️  WARNING: Time series has gaps (max gap: {int(max_gap)} years)")
    
    # Check for duplicate years
    duplicates = df[year_col].duplicated().sum()
    if duplicates > 0:
        warnings.append(f"⚠️  WARNING: {duplicates} duplicate years found")
    
    return True, warnings


# ═══════════════════════════════════════════════════════════════════════════
# GRAPH ANNOTATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def add_data_source_label(
    fig: go.Figure,
    source: str,
    quality_score: Optional[float] = None,
    position: str = "bottom"
) -> go.Figure:
    """
    Add data source and quality indicator to graph.
    
    Args:
        fig: Plotly figure
        source: Data source name
        quality_score: Quality score (0-100), optional
        position: "bottom" or "top"
    
    Returns:
        Updated figure
    """
    # Build label text
    if quality_score is not None:
        # Add quality indicator emoji
        if quality_score >= 90:
            quality_emoji = "🟢"
        elif quality_score >= 70:
            quality_emoji = "🟡"
        else:
            quality_emoji = "🔴"
        
        label = f"{quality_emoji} Source: {source} | Quality: {quality_score:.0f}/100"
    else:
        label = f"Source: {source}"
    
    # Position
    y_pos = -0.15 if position == "bottom" else 1.05
    
    # Add annotation
    fig.add_annotation(
        text=label,
        xref="paper", yref="paper",
        x=0.5, y=y_pos,
        xanchor="center",
        showarrow=False,
        font=dict(size=10, color="gray"),
    )
    
    return fig


def add_data_age_warning(
    fig: go.Figure,
    data_date: str,
    position: str = "top-right"
) -> go.Figure:
    """
    Add data age warning to graph.
    
    Args:
        fig: Plotly figure
        data_date: Date of data (e.g., "2019-07-01")
        position: "top-right", "top-left", "bottom-right", "bottom-left"
    
    Returns:
        Updated figure
    """
    # Calculate age
    try:
        data_datetime = datetime.strptime(data_date, "%Y-%m-%d")
        age_years = (datetime.now() - data_datetime).days / 365.25
        
        if age_years > 3:
            # Old data warning
            warning = f"⚠️  Data from {data_date} ({age_years:.1f} years old)"
            
            # Position
            if position == "top-right":
                x, y = 0.98, 0.98
                xanchor, yanchor = "right", "top"
            elif position == "top-left":
                x, y = 0.02, 0.98
                xanchor, yanchor = "left", "top"
            elif position == "bottom-right":
                x, y = 0.98, 0.02
                xanchor, yanchor = "right", "bottom"
            else:  # bottom-left
                x, y = 0.02, 0.02
                xanchor, yanchor = "left", "bottom"
            
            fig.add_annotation(
                text=warning,
                xref="paper", yref="paper",
                x=x, y=y,
                xanchor=xanchor, yanchor=yanchor,
                showarrow=False,
                font=dict(size=9, color="orange"),
                bgcolor="rgba(255, 165, 0, 0.1)",
                bordercolor="orange",
                borderwidth=1,
                borderpad=4,
            )
    except Exception:
        pass  # Skip if date parsing fails
    
    return fig


def add_validation_warnings(
    fig: go.Figure,
    warnings: List[str],
    position: str = "top-left"
) -> go.Figure:
    """
    Add validation warnings to graph.
    
    Args:
        fig: Plotly figure
        warnings: List of warning messages
        position: "top-left", "top-right", "bottom-left", "bottom-right"
    
    Returns:
        Updated figure
    """
    if not warnings:
        return fig
    
    # Filter to only show warnings and errors (not info)
    important_warnings = [w for w in warnings if "⚠️" in w or "❌" in w]
    
    if not important_warnings:
        return fig
    
    # Build warning text
    warning_text = "<br>".join(important_warnings[:3])  # Show max 3 warnings
    if len(important_warnings) > 3:
        warning_text += f"<br>... and {len(important_warnings) - 3} more"
    
    # Position
    if position == "top-left":
        x, y = 0.02, 0.98
        xanchor, yanchor = "left", "top"
    elif position == "top-right":
        x, y = 0.98, 0.98
        xanchor, yanchor = "right", "top"
    elif position == "bottom-left":
        x, y = 0.02, 0.02
        xanchor, yanchor = "left", "bottom"
    else:  # bottom-right
        x, y = 0.98, 0.02
        xanchor, yanchor = "right", "bottom"
    
    fig.add_annotation(
        text=warning_text,
        xref="paper", yref="paper",
        x=x, y=y,
        xanchor=xanchor, yanchor=yanchor,
        showarrow=False,
        font=dict(size=9, color="red"),
        bgcolor="rgba(255, 0, 0, 0.05)",
        bordercolor="red",
        borderwidth=1,
        borderpad=4,
    )
    
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# STYLING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def style_historical_vs_forecast(
    fig: go.Figure,
    historical_trace_name: str = "Historical",
    forecast_trace_name: str = "Forecast",
    historical_color: str = "#1f77b4",
    forecast_color: str = "#ff7f0e"
) -> go.Figure:
    """
    Style historical data as solid line, forecast as dashed line.
    
    Args:
        fig: Plotly figure
        historical_trace_name: Name of historical trace
        forecast_trace_name: Name of forecast trace
        historical_color: Color for historical data
        forecast_color: Color for forecast data
    
    Returns:
        Updated figure
    """
    for trace in fig.data:
        if historical_trace_name.lower() in trace.name.lower():
            trace.line.color = historical_color
            trace.line.width = 2
            trace.line.dash = "solid"
        elif forecast_trace_name.lower() in trace.name.lower():
            trace.line.color = forecast_color
            trace.line.width = 2
            trace.line.dash = "dash"
    
    return fig


def add_confidence_bands(
    fig: go.Figure,
    x: List,
    lower: List,
    upper: List,
    name: str = "Confidence Band",
    color: str = "rgba(255, 127, 14, 0.2)"
) -> go.Figure:
    """
    Add confidence bands to forecast.
    
    Args:
        fig: Plotly figure
        x: X-axis values (years)
        lower: Lower bound values
        upper: Upper bound values
        name: Name for the band
        color: Fill color (rgba)
    
    Returns:
        Updated figure
    """
    # Add upper bound
    fig.add_trace(go.Scatter(
        x=x,
        y=upper,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip',
    ))
    
    # Add lower bound with fill
    fig.add_trace(go.Scatter(
        x=x,
        y=lower,
        mode='lines',
        line=dict(width=0),
        fillcolor=color,
        fill='tonexty',
        name=name,
        hoverinfo='skip',
    ))
    
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# COMPLETE VALIDATION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

def create_validated_graph(
    df: pd.DataFrame,
    value_col: str,
    year_col: str = "Year",
    title: str = "Time Series",
    data_source: str = "Unknown",
    quality_score: Optional[float] = None,
    data_date: Optional[str] = None,
    is_forecast: bool = False
) -> Tuple[Optional[go.Figure], List[str]]:
    """
    Create a validated graph with all quality indicators.
    
    Args:
        df: DataFrame with data
        value_col: Name of value column
        year_col: Name of year column
        title: Graph title
        data_source: Data source name
        quality_score: Quality score (0-100)
        data_date: Date of data (for age warning)
        is_forecast: Whether this is forecast data
    
    Returns:
        (figure, list_of_warnings)
    """
    # Validate data
    is_valid, warnings = validate_time_series(df, value_col, year_col)
    
    if not is_valid:
        # Return None if data is invalid
        return None, warnings
    
    # Create figure
    fig = go.Figure()
    
    # Add trace
    line_style = dict(dash="dash", width=2) if is_forecast else dict(width=2)
    color = "#ff7f0e" if is_forecast else "#1f77b4"
    
    fig.add_trace(go.Scatter(
        x=df[year_col],
        y=df[value_col],
        mode='lines+markers',
        name="Forecast" if is_forecast else "Historical",
        line=line_style,
        marker=dict(size=4, color=color),
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=value_col,
        hovermode='x unified',
        template='plotly_white',
    )
    
    # Add data source label
    fig = add_data_source_label(fig, data_source, quality_score)
    
    # Add data age warning if applicable
    if data_date:
        fig = add_data_age_warning(fig, data_date)
    
    # Add validation warnings if any
    if warnings:
        fig = add_validation_warnings(fig, warnings)
    
    return fig, warnings


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_quality_indicator(quality_score: float) -> str:
    """
    Get quality indicator emoji based on score.
    
    Args:
        quality_score: Quality score (0-100)
    
    Returns:
        Emoji indicator
    """
    if quality_score >= 90:
        return "🟢 Excellent"
    elif quality_score >= 80:
        return "🟢 Good"
    elif quality_score >= 70:
        return "🟡 Fair"
    elif quality_score >= 50:
        return "🟠 Poor"
    else:
        return "🔴 Critical"


def print_validation_summary(warnings: List[str]) -> None:
    """Print validation summary to console."""
    if not warnings:
        print("✅ Data validation passed - no issues found")
        return
    
    errors = [w for w in warnings if "❌" in w]
    warnings_only = [w for w in warnings if "⚠️" in w]
    info = [w for w in warnings if "ℹ️" in w]
    
    if errors:
        print(f"❌ {len(errors)} error(s) found:")
        for error in errors:
            print(f"  {error}")
    
    if warnings_only:
        print(f"⚠️  {len(warnings_only)} warning(s) found:")
        for warning in warnings_only:
            print(f"  {warning}")
    
    if info:
        print(f"ℹ️  {len(info)} informational message(s):")
        for i in info:
            print(f"  {i}")


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test with sample data
    import numpy as np
    
    print("\n" + "="*80)
    print("GRAPH VALIDATOR TEST")
    print("="*80 + "\n")
    
    # Create sample data
    years = list(range(2015, 2025))
    values = [4.5, 4.7, 4.9, 5.2, 5.8, 7.1, 6.9, 6.5, 6.2, 6.0]
    
    df = pd.DataFrame({
        "Year": years,
        "Unemployment_Rate": values
    })
    
    # Test validation
    print("TEST 1: Validate sample data")
    is_valid, warnings = validate_time_series(df, "Unemployment_Rate")
    print(f"Valid: {is_valid}")
    print_validation_summary(warnings)
    
    # Test graph creation
    print("\nTEST 2: Create validated graph")
    fig, warnings = create_validated_graph(
        df,
        "Unemployment_Rate",
        title="India Unemployment Rate",
        data_source="Curated PLFS/CMIE Data",
        quality_score=100.0,
    )
    
    if fig:
        print("✅ Graph created successfully")
        print(f"   Warnings: {len(warnings)}")
    else:
        print("❌ Graph creation failed")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
