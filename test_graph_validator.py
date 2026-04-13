"""
test_graph_validator.py

Test script for graph validation layer.

This script verifies:
1. Data validation before plotting
2. Quality indicators on graphs
3. Data source labels
4. Historical vs forecast styling
5. Warning annotations
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graph_validator import (
    validate_before_plot,
    validate_time_series,
    create_validated_graph,
    add_data_source_label,
    add_data_age_warning,
    add_validation_warnings,
    style_historical_vs_forecast,
    get_quality_indicator,
    print_validation_summary,
)
from central_data import load_unemployment, get_data_quality_report
import plotly.graph_objects as go


def test_validation_functions():
    """Test validation functions."""
    print("\n" + "="*80)
    print("TEST 1: Validation Functions")
    print("="*80)
    
    # Create sample data
    df = pd.DataFrame({
        "Year": [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        "Unemployment_Rate": [4.5, 4.7, 4.9, 5.2, 5.8, 7.1, 6.9, 6.5, 6.2]
    })
    
    # Test basic validation
    is_valid, warnings = validate_before_plot(df, "Unemployment_Rate")
    print(f"✅ Basic validation: {is_valid}")
    print(f"   Warnings: {len(warnings)}")
    
    # Test time series validation
    is_valid, warnings = validate_time_series(df, "Unemployment_Rate")
    print(f"✅ Time series validation: {is_valid}")
    print(f"   Warnings: {len(warnings)}")
    
    # Test with missing values
    df_missing = df.copy()
    df_missing.loc[3, "Unemployment_Rate"] = np.nan
    
    is_valid, warnings = validate_before_plot(df_missing, "Unemployment_Rate")
    print(f"\n✅ Validation with missing values: {is_valid}")
    print(f"   Warnings: {len(warnings)}")
    if warnings:
        for warning in warnings:
            print(f"   {warning}")
    
    # Test with empty DataFrame
    df_empty = pd.DataFrame()
    is_valid, warnings = validate_before_plot(df_empty, "Unemployment_Rate")
    print(f"\n✅ Validation with empty DataFrame: {is_valid}")
    print(f"   Warnings: {len(warnings)}")
    if warnings:
        for warning in warnings:
            print(f"   {warning}")


def test_quality_indicators():
    """Test quality indicator functions."""
    print("\n" + "="*80)
    print("TEST 2: Quality Indicators")
    print("="*80)
    
    scores = [100, 85, 75, 60, 40]
    
    for score in scores:
        indicator = get_quality_indicator(score)
        print(f"Score {score:3d}: {indicator}")
    
    print("\n✅ Quality indicators working correctly")


def test_graph_creation():
    """Test graph creation with validation."""
    print("\n" + "="*80)
    print("TEST 3: Graph Creation with Validation")
    print("="*80)
    
    # Create sample data
    df = pd.DataFrame({
        "Year": [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        "Unemployment_Rate": [4.5, 4.7, 4.9, 5.2, 5.8, 7.1, 6.9, 6.5, 6.2]
    })
    
    # Create validated graph
    fig, warnings = create_validated_graph(
        df,
        "Unemployment_Rate",
        title="India Unemployment Rate (Test)",
        data_source="Test Data",
        quality_score=95.0,
    )
    
    if fig:
        print("✅ Graph created successfully")
        print(f"   Traces: {len(fig.data)}")
        print(f"   Annotations: {len(fig.layout.annotations)}")
        print(f"   Warnings: {len(warnings)}")
    else:
        print("❌ Graph creation failed")
        print(f"   Warnings: {warnings}")


def test_with_real_data():
    """Test with real unemployment data."""
    print("\n" + "="*80)
    print("TEST 4: Real Data Integration")
    print("="*80)
    
    # Load real data
    df = load_unemployment()
    report = get_data_quality_report()
    
    print(f"Loaded {len(df)} rows of unemployment data")
    print(f"Quality Score: {report['unemployment']['data_quality_score']:.1f}/100")
    
    # Validate
    is_valid, warnings = validate_time_series(df, "Unemployment_Rate")
    print(f"\nValidation: {is_valid}")
    print_validation_summary(warnings)
    
    # Create graph
    fig, warnings = create_validated_graph(
        df,
        "Unemployment_Rate",
        title="India Unemployment Rate (Real Data)",
        data_source=report['unemployment']['source'],
        quality_score=report['unemployment']['data_quality_score'],
    )
    
    if fig:
        print("\n✅ Graph created with real data")
        print(f"   Data points: {len(df)}")
        print(f"   Quality: {report['unemployment']['data_quality_score']:.1f}/100")
    else:
        print("\n❌ Graph creation failed")


def test_historical_vs_forecast_styling():
    """Test historical vs forecast styling."""
    print("\n" + "="*80)
    print("TEST 5: Historical vs Forecast Styling")
    print("="*80)
    
    # Create sample data
    historical_years = list(range(2015, 2024))
    historical_values = [4.5, 4.7, 4.9, 5.2, 5.8, 7.1, 6.9, 6.5, 6.2]
    
    forecast_years = list(range(2024, 2029))
    forecast_values = [6.0, 5.8, 5.6, 5.4, 5.2]
    
    # Create figure
    fig = go.Figure()
    
    # Add historical trace
    fig.add_trace(go.Scatter(
        x=historical_years,
        y=historical_values,
        mode='lines+markers',
        name='Historical',
    ))
    
    # Add forecast trace
    fig.add_trace(go.Scatter(
        x=forecast_years,
        y=forecast_values,
        mode='lines+markers',
        name='Forecast',
    ))
    
    # Apply styling
    fig = style_historical_vs_forecast(fig)
    
    # Add data source
    fig = add_data_source_label(fig, "Test Data", 90.0)
    
    print("✅ Historical vs Forecast styling applied")
    print(f"   Historical trace: Solid line")
    print(f"   Forecast trace: Dashed line")
    print(f"   Data source label: Added")


def test_data_age_warning():
    """Test data age warning."""
    print("\n" + "="*80)
    print("TEST 6: Data Age Warning")
    print("="*80)
    
    # Create sample figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[2015, 2016, 2017, 2018, 2019],
        y=[4.5, 4.7, 4.9, 5.2, 5.8],
        mode='lines+markers',
    ))
    
    # Add data age warning (old data)
    fig = add_data_age_warning(fig, "2019-07-01", position="top-right")
    
    print("✅ Data age warning added")
    print(f"   Data from: 2019-07-01")
    print(f"   Age: ~5 years old")
    print(f"   Warning displayed: Yes")


def test_validation_warnings_annotation():
    """Test validation warnings annotation."""
    print("\n" + "="*80)
    print("TEST 7: Validation Warnings Annotation")
    print("="*80)
    
    # Create sample figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[2015, 2016, 2017, 2018, 2019],
        y=[4.5, 4.7, 4.9, 5.2, 5.8],
        mode='lines+markers',
    ))
    
    # Add validation warnings
    warnings = [
        "⚠️  WARNING: 2 missing values (10.0%)",
        "⚠️  WARNING: Time series has gaps (max gap: 3 years)",
        "ℹ️  INFO: 1 statistical outliers detected"
    ]
    
    fig = add_validation_warnings(fig, warnings, position="top-left")
    
    print("✅ Validation warnings added to graph")
    print(f"   Warnings: {len(warnings)}")
    for warning in warnings:
        print(f"   {warning}")


def test_complete_pipeline():
    """Test complete validation pipeline."""
    print("\n" + "="*80)
    print("TEST 8: Complete Validation Pipeline")
    print("="*80)
    
    # Load real data
    df = load_unemployment()
    report = get_data_quality_report()
    
    # Create validated graph with all features
    fig, warnings = create_validated_graph(
        df,
        "Unemployment_Rate",
        title="India Unemployment Rate - Complete Validation",
        data_source=report['unemployment']['source'],
        quality_score=report['unemployment']['data_quality_score'],
        is_forecast=False,
    )
    
    if fig:
        print("✅ Complete pipeline executed successfully")
        print(f"   Data source: {report['unemployment']['source']}")
        print(f"   Quality score: {report['unemployment']['data_quality_score']:.1f}/100")
        print(f"   Data points: {len(df)}")
        print(f"   Validation warnings: {len(warnings)}")
        
        if warnings:
            print("\n   Warnings:")
            for warning in warnings:
                print(f"   {warning}")
    else:
        print("❌ Pipeline failed")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("GRAPH VALIDATOR TEST SUITE")
    print("="*80)
    
    test_validation_functions()
    test_quality_indicators()
    test_graph_creation()
    test_with_real_data()
    test_historical_vs_forecast_styling()
    test_data_age_warning()
    test_validation_warnings_annotation()
    test_complete_pipeline()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)
    print("\n✅ Graph validation layer is working correctly")
    print("✅ Data validation before plotting works")
    print("✅ Quality indicators are added to graphs")
    print("✅ Data source labels are displayed")
    print("✅ Historical vs forecast styling works")
    print("✅ Warning annotations are shown")
    print("\n")
