"""
validation_engine.py

COMPREHENSIVE DATA VALIDATION ENGINE
=====================================

This module provides advanced validation, anomaly detection, and data correction
capabilities for economic time series data.

Author: Refactored System Architecture
Date: 2026-04-13
Version: 2.0.0

Features:
---------
1. Range validation (min/max bounds)
2. Spike detection (statistical outliers)
3. Missing value detection and interpolation
4. Consistency checks (year-over-year changes)
5. Automated correction with logging
6. Comprehensive validation reports
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ValidationConfig:
    """Configuration for validation rules."""
    
    # Range limits
    min_value: float
    max_value: float
    realistic_min: float
    realistic_max: float
    
    # Change limits
    max_yoy_change: float  # Maximum year-over-year change (percentage points)
    max_yoy_change_pct: float  # Maximum year-over-year change (%)
    
    # Spike detection
    spike_threshold_std: float = 2.5  # Standard deviations for spike detection
    
    # Missing data
    max_missing_pct: float = 10.0
    interpolation_method: str = "linear"  # linear, polynomial, spline
    
    # Metadata
    metric_name: str = "Value"
    unit: str = "%"


# Predefined configurations for Indian economic data
UNEMPLOYMENT_CONFIG = ValidationConfig(
    min_value=2.0,
    max_value=10.0,
    realistic_min=3.0,
    realistic_max=8.0,
    max_yoy_change=3.0,
    max_yoy_change_pct=50.0,
    spike_threshold_std=2.5,
    max_missing_pct=10.0,
    interpolation_method="linear",
    metric_name="Unemployment Rate",
    unit="%"
)

INFLATION_CONFIG = ValidationConfig(
    min_value=2.0,
    max_value=15.0,
    realistic_min=3.0,
    realistic_max=14.0,
    max_yoy_change=5.0,
    max_yoy_change_pct=100.0,
    spike_threshold_std=2.5,
    max_missing_pct=10.0,
    interpolation_method="linear",
    metric_name="Inflation Rate",
    unit="%"
)


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION RESULTS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    year: int
    issue_type: str  # "range", "spike", "missing", "yoy_change"
    severity: str  # "error", "warning", "info"
    message: str
    original_value: Optional[float]
    corrected_value: Optional[float]


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    is_valid: bool
    quality_score: float  # 0-100
    total_issues: int
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    corrections: List[ValidationIssue]
    statistics: Dict
    recommendations: List[str]


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def validate_ranges(
    df: pd.DataFrame,
    value_col: str,
    year_col: str,
    config: ValidationConfig
) -> List[ValidationIssue]:
    """
    Validate that all values are within acceptable ranges.
    
    Args:
        df: DataFrame with time series data
        value_col: Name of the value column
        year_col: Name of the year column
        config: Validation configuration
    
    Returns:
        List of validation issues found
    """
    issues = []
    
    for idx, row in df.iterrows():
        year = int(row[year_col])
        value = row[value_col]
        
        if pd.isna(value):
            continue  # Handled by check_missing_values
        
        # Check absolute bounds
        if value < config.min_value:
            issues.append(ValidationIssue(
                year=year,
                issue_type="range",
                severity="error",
                message=f"Value {value:.2f}{config.unit} below minimum ({config.min_value}{config.unit})",
                original_value=value,
                corrected_value=config.realistic_min
            ))
        elif value > config.max_value:
            issues.append(ValidationIssue(
                year=year,
                issue_type="range",
                severity="error",
                message=f"Value {value:.2f}{config.unit} above maximum ({config.max_value}{config.unit})",
                original_value=value,
                corrected_value=config.realistic_max
            ))
        # Check realistic bounds (warnings only)
        elif value < config.realistic_min:
            issues.append(ValidationIssue(
                year=year,
                issue_type="range",
                severity="warning",
                message=f"Value {value:.2f}{config.unit} below typical range ({config.realistic_min}{config.unit})",
                original_value=value,
                corrected_value=None
            ))
        elif value > config.realistic_max:
            issues.append(ValidationIssue(
                year=year,
                issue_type="range",
                severity="warning",
                message=f"Value {value:.2f}{config.unit} above typical range ({config.realistic_max}{config.unit})",
                original_value=value,
                corrected_value=None
            ))
    
    return issues


def detect_spikes(
    df: pd.DataFrame,
    value_col: str,
    year_col: str,
    config: ValidationConfig
) -> List[ValidationIssue]:
    """
    Detect statistical outliers (spikes) in the time series.
    
    Uses modified Z-score method with median absolute deviation (MAD)
    for robust outlier detection.
    
    Args:
        df: DataFrame with time series data
        value_col: Name of the value column
        year_col: Name of the year column
        config: Validation configuration
    
    Returns:
        List of validation issues found
    """
    issues = []
    
    # Remove NaN values for statistical analysis
    df_clean = df.dropna(subset=[value_col])
    
    if len(df_clean) < 5:
        return issues  # Not enough data for spike detection
    
    values = df_clean[value_col].values
    
    # Calculate modified Z-scores using MAD (more robust than std)
    median = np.median(values)
    mad = np.median(np.abs(values - median))
    
    if mad == 0:
        # Fallback to standard deviation if MAD is zero
        std = np.std(values)
        if std == 0:
            return issues  # No variation in data
        z_scores = np.abs((values - np.mean(values)) / std)
    else:
        # Modified Z-score: 0.6745 is the 75th percentile of standard normal
        modified_z_scores = 0.6745 * (values - median) / mad
        z_scores = np.abs(modified_z_scores)
    
    # Detect spikes
    threshold = config.spike_threshold_std
    spike_indices = np.where(z_scores > threshold)[0]
    
    for idx in spike_indices:
        year = int(df_clean.iloc[idx][year_col])
        value = df_clean.iloc[idx][value_col]
        z_score = z_scores[idx]
        
        # Calculate suggested correction (move toward median)
        suggested = median + (value - median) * 0.5
        suggested = np.clip(suggested, config.realistic_min, config.realistic_max)
        
        issues.append(ValidationIssue(
            year=year,
            issue_type="spike",
            severity="warning",
            message=f"Statistical outlier detected (Z-score: {z_score:.2f})",
            original_value=value,
            corrected_value=suggested
        ))
    
    return issues


def check_missing_values(
    df: pd.DataFrame,
    value_col: str,
    year_col: str,
    config: ValidationConfig
) -> List[ValidationIssue]:
    """
    Check for missing values and gaps in the time series.
    
    Args:
        df: DataFrame with time series data
        value_col: Name of the value column
        year_col: Name of the year column
        config: Validation configuration
    
    Returns:
        List of validation issues found
    """
    issues = []
    
    # Check for NaN values
    missing_mask = df[value_col].isna()
    missing_count = missing_mask.sum()
    
    if missing_count > 0:
        missing_years = df.loc[missing_mask, year_col].tolist()
        
        for year in missing_years:
            issues.append(ValidationIssue(
                year=int(year),
                issue_type="missing",
                severity="error",
                message="Missing value",
                original_value=None,
                corrected_value=None  # Will be filled by interpolation
            ))
    
    # Check for gaps in year sequence
    df_sorted = df.sort_values(year_col)
    years = df_sorted[year_col].values
    
    if len(years) > 1:
        year_diffs = np.diff(years)
        gap_indices = np.where(year_diffs > 1)[0]
        
        for idx in gap_indices:
            year_before = int(years[idx])
            year_after = int(years[idx + 1])
            gap_size = int(year_diffs[idx] - 1)
            
            issues.append(ValidationIssue(
                year=year_before,
                issue_type="missing",
                severity="warning",
                message=f"Gap of {gap_size} year(s) between {year_before} and {year_after}",
                original_value=None,
                corrected_value=None
            ))
    
    return issues


def enforce_consistency(
    df: pd.DataFrame,
    value_col: str,
    year_col: str,
    config: ValidationConfig
) -> List[ValidationIssue]:
    """
    Check year-over-year consistency (no extreme jumps).
    
    Args:
        df: DataFrame with time series data
        value_col: Name of the value column
        year_col: Name of the year column
        config: Validation configuration
    
    Returns:
        List of validation issues found
    """
    issues = []
    
    df_sorted = df.sort_values(year_col).reset_index(drop=True)
    
    for i in range(1, len(df_sorted)):
        year = int(df_sorted.loc[i, year_col])
        current = df_sorted.loc[i, value_col]
        previous = df_sorted.loc[i-1, value_col]
        
        if pd.isna(current) or pd.isna(previous):
            continue
        
        # Check absolute change
        abs_change = abs(current - previous)
        
        if abs_change > config.max_yoy_change:
            issues.append(ValidationIssue(
                year=year,
                issue_type="yoy_change",
                severity="warning",
                message=f"Large YoY change: {abs_change:.2f}pp (max: {config.max_yoy_change}pp)",
                original_value=current,
                corrected_value=None
            ))
        
        # Check percentage change
        if previous != 0:
            pct_change = abs((current - previous) / previous * 100)
            
            if pct_change > config.max_yoy_change_pct:
                issues.append(ValidationIssue(
                    year=year,
                    issue_type="yoy_change",
                    severity="warning",
                    message=f"Large YoY % change: {pct_change:.1f}% (max: {config.max_yoy_change_pct}%)",
                    original_value=current,
                    corrected_value=None
                ))
    
    return issues


# ═══════════════════════════════════════════════════════════════════════════
# DATA CORRECTION
# ═══════════════════════════════════════════════════════════════════════════

def interpolate_missing_values(
    df: pd.DataFrame,
    value_col: str,
    year_col: str,
    method: str = "linear"
) -> pd.DataFrame:
    """
    Interpolate missing values in the time series.
    
    Args:
        df: DataFrame with time series data
        value_col: Name of the value column
        year_col: Name of the year column
        method: Interpolation method ("linear", "polynomial", "spline")
    
    Returns:
        DataFrame with interpolated values
    """
    df = df.copy()
    df = df.sort_values(year_col).reset_index(drop=True)
    
    if method == "linear":
        df[value_col] = df[value_col].interpolate(method="linear", limit_direction="both")
    elif method == "polynomial":
        df[value_col] = df[value_col].interpolate(method="polynomial", order=2, limit_direction="both")
    elif method == "spline":
        df[value_col] = df[value_col].interpolate(method="spline", order=3, limit_direction="both")
    else:
        # Default to linear
        df[value_col] = df[value_col].interpolate(method="linear", limit_direction="both")
    
    return df


def apply_corrections(
    df: pd.DataFrame,
    value_col: str,
    year_col: str,
    issues: List[ValidationIssue],
    config: ValidationConfig
) -> Tuple[pd.DataFrame, List[ValidationIssue]]:
    """
    Apply automated corrections to validation issues.
    
    Args:
        df: DataFrame with time series data
        value_col: Name of the value column
        year_col: Name of the year column
        issues: List of validation issues
        config: Validation configuration
    
    Returns:
        (corrected_df, list_of_applied_corrections)
    """
    df = df.copy()
    applied_corrections = []
    
    # Group issues by type
    range_issues = [i for i in issues if i.issue_type == "range" and i.severity == "error"]
    spike_issues = [i for i in issues if i.issue_type == "spike"]
    missing_issues = [i for i in issues if i.issue_type == "missing" and i.severity == "error"]
    
    # 1. Fix range violations
    for issue in range_issues:
        if issue.corrected_value is not None:
            mask = df[year_col] == issue.year
            df.loc[mask, value_col] = issue.corrected_value
            applied_corrections.append(issue)
    
    # 2. Interpolate missing values
    if missing_issues:
        df = interpolate_missing_values(df, value_col, year_col, config.interpolation_method)
        
        for issue in missing_issues:
            mask = df[year_col] == issue.year
            if mask.any():
                interpolated_value = df.loc[mask, value_col].values[0]
                issue.corrected_value = interpolated_value
                applied_corrections.append(issue)
    
    # 3. Smooth spikes (optional - only if very extreme)
    extreme_spikes = [i for i in spike_issues if i.original_value and 
                     (i.original_value > config.max_value or i.original_value < config.min_value)]
    
    for issue in extreme_spikes:
        if issue.corrected_value is not None:
            mask = df[year_col] == issue.year
            df.loc[mask, value_col] = issue.corrected_value
            applied_corrections.append(issue)
    
    return df, applied_corrections


# ═══════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_time_series(
    df: pd.DataFrame,
    value_col: str,
    year_col: str,
    config: ValidationConfig,
    auto_correct: bool = True
) -> Tuple[pd.DataFrame, ValidationReport]:
    """
    Perform comprehensive validation on a time series.
    
    Args:
        df: DataFrame with time series data
        value_col: Name of the value column
        year_col: Name of the year column
        config: Validation configuration
        auto_correct: Whether to automatically apply corrections
    
    Returns:
        (corrected_df, validation_report)
    """
    df = df.copy()
    all_issues = []
    
    # Run all validation checks
    all_issues.extend(validate_ranges(df, value_col, year_col, config))
    all_issues.extend(detect_spikes(df, value_col, year_col, config))
    all_issues.extend(check_missing_values(df, value_col, year_col, config))
    all_issues.extend(enforce_consistency(df, value_col, year_col, config))
    
    # Separate by severity
    errors = [i for i in all_issues if i.severity == "error"]
    warnings = [i for i in all_issues if i.severity == "warning"]
    
    # Apply corrections if requested
    corrections = []
    if auto_correct and (errors or warnings):
        df, corrections = apply_corrections(df, value_col, year_col, all_issues, config)
    
    # Calculate statistics
    df_clean = df.dropna(subset=[value_col])
    statistics = {
        "total_rows": len(df),
        "valid_rows": len(df_clean),
        "missing_rows": len(df) - len(df_clean),
        "missing_pct": ((len(df) - len(df_clean)) / len(df) * 100) if len(df) > 0 else 0,
        "mean": float(df_clean[value_col].mean()) if not df_clean.empty else 0,
        "median": float(df_clean[value_col].median()) if not df_clean.empty else 0,
        "std": float(df_clean[value_col].std()) if not df_clean.empty else 0,
        "min": float(df_clean[value_col].min()) if not df_clean.empty else 0,
        "max": float(df_clean[value_col].max()) if not df_clean.empty else 0,
        "year_range": f"{df[year_col].min()}-{df[year_col].max()}" if not df.empty else "N/A"
    }
    
    # Calculate quality score
    quality_score = 100.0
    quality_score -= len(errors) * 10  # -10 per error
    quality_score -= len(warnings) * 2  # -2 per warning
    quality_score -= statistics["missing_pct"] * 0.5  # -0.5 per % missing
    quality_score = max(0.0, min(100.0, quality_score))
    
    # Generate recommendations
    recommendations = []
    if errors:
        recommendations.append(f"Fix {len(errors)} critical error(s) in the data")
    if warnings:
        recommendations.append(f"Review {len(warnings)} warning(s) for potential issues")
    if statistics["missing_pct"] > 5:
        recommendations.append(f"Address {statistics['missing_pct']:.1f}% missing data")
    if quality_score < 70:
        recommendations.append("Data quality is below acceptable threshold (70/100)")
    if not recommendations:
        recommendations.append("Data quality is acceptable")
    
    # Determine overall validity
    is_valid = (
        len(errors) == 0 and
        quality_score >= 70.0 and
        statistics["missing_pct"] <= config.max_missing_pct
    )
    
    report = ValidationReport(
        is_valid=is_valid,
        quality_score=quality_score,
        total_issues=len(all_issues),
        errors=errors,
        warnings=warnings,
        corrections=corrections,
        statistics=statistics,
        recommendations=recommendations
    )
    
    return df, report


def print_validation_report(report: ValidationReport, metric_name: str = "Data") -> None:
    """Print formatted validation report."""
    print("\n" + "="*80)
    print(f"VALIDATION REPORT: {metric_name}")
    print("="*80)
    print(f"Overall Status: {'✅ VALID' if report.is_valid else '❌ INVALID'}")
    print(f"Quality Score: {report.quality_score:.1f}/100")
    print(f"Total Issues: {report.total_issues}")
    print()
    
    print("STATISTICS:")
    for key, value in report.statistics.items():
        print(f"  {key}: {value}")
    print()
    
    if report.errors:
        print(f"ERRORS ({len(report.errors)}):")
        for error in report.errors[:10]:  # Show first 10
            print(f"  Year {error.year}: {error.message}")
        if len(report.errors) > 10:
            print(f"  ... and {len(report.errors) - 10} more")
        print()
    
    if report.warnings:
        print(f"WARNINGS ({len(report.warnings)}):")
        for warning in report.warnings[:10]:  # Show first 10
            print(f"  Year {warning.year}: {warning.message}")
        if len(report.warnings) > 10:
            print(f"  ... and {len(report.warnings) - 10} more")
        print()
    
    if report.corrections:
        print(f"CORRECTIONS APPLIED ({len(report.corrections)}):")
        for correction in report.corrections[:10]:  # Show first 10
            if correction.original_value is not None and correction.corrected_value is not None:
                print(f"  Year {correction.year}: {correction.original_value:.2f} → {correction.corrected_value:.2f}")
            else:
                print(f"  Year {correction.year}: {correction.message}")
        if len(report.corrections) > 10:
            print(f"  ... and {len(report.corrections) - 10} more")
        print()
    
    if report.recommendations:
        print("RECOMMENDATIONS:")
        for rec in report.recommendations:
            print(f"  • {rec}")
    
    print("="*80 + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test with sample data
    test_data = pd.DataFrame({
        "Year": [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        "Unemployment_Rate": [4.5, 4.7, 4.9, 5.2, 5.8, 7.1, 6.9, 6.5, 6.2]
    })
    
    df_corrected, report = validate_time_series(
        test_data,
        "Unemployment_Rate",
        "Year",
        UNEMPLOYMENT_CONFIG,
        auto_correct=True
    )
    
    print_validation_report(report, "Test Unemployment Data")
