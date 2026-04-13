"""
central_data.py

SINGLE SOURCE OF TRUTH FOR ALL DATA
====================================

This module is the ONLY place where raw data is loaded and validated.
NO other module should directly access CSV files or fetch external data.

Author: Refactored System Architecture
Date: 2026-04-13
Version: 2.0.0

Rules:
------
1. All data MUST pass validation before being returned
2. All modules MUST import from this module
3. No direct CSV access allowed elsewhere
4. All data sources are explicitly documented
5. Data quality issues are logged and reported

Data Sources:
-------------
- Unemployment: data/raw/india_unemployment_realistic.csv (CURATED)
- Inflation: data/raw/india_inflation_corrected.csv (CURATED)
- Fallback: World Bank API (with quality warnings)
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# DATA SOURCE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DataSource:
    """Metadata about a data source."""
    name: str
    path: Optional[Path]
    description: str
    quality_level: str  # "HIGH", "MEDIUM", "LOW", "UNKNOWN"
    last_updated: Optional[str]
    source_authority: str
    notes: str


# Primary data sources (curated, validated)
UNEMPLOYMENT_SOURCE = DataSource(
    name="India Unemployment (Realistic)",
    path=Path("data/raw/india_unemployment_realistic.csv"),
    description="Curated unemployment data with corrected COVID values",
    quality_level="HIGH",
    last_updated="2024",
    source_authority="PLFS/CMIE (curated)",
    notes="COVID peak corrected to 7.1% annual average (not 23.5% monthly)"
)

INFLATION_SOURCE = DataSource(
    name="India Inflation (Corrected)",
    path=Path("data/raw/india_inflation_corrected.csv"),
    description="Corrected inflation data matching RBI CPI statistics",
    quality_level="HIGH",
    last_updated="2024",
    source_authority="RBI CPI Data (curated)",
    notes="Realistic ranges 3.4-13.9%, not 20%+"
)

# Fallback sources (lower quality)
UNEMPLOYMENT_FALLBACK = DataSource(
    name="India Unemployment (Original)",
    path=Path("data/raw/india_unemployment.csv"),
    description="Original World Bank data (uncorrected)",
    quality_level="MEDIUM",
    last_updated="Unknown",
    source_authority="World Bank API",
    notes="Contains unrealistic COVID spike (23.5%)"
)


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION RULES
# ═══════════════════════════════════════════════════════════════════════════

class ValidationRules:
    """Strict validation rules for Indian economic data."""
    
    # Unemployment bounds (%)
    UNEMPLOYMENT_MIN = 2.0
    UNEMPLOYMENT_MAX = 10.0
    UNEMPLOYMENT_REALISTIC_MIN = 3.0
    UNEMPLOYMENT_REALISTIC_MAX = 8.0
    
    # Inflation bounds (%)
    INFLATION_MIN = 2.0
    INFLATION_MAX = 15.0
    INFLATION_REALISTIC_MIN = 3.0
    INFLATION_REALISTIC_MAX = 14.0
    
    # Year-over-year change limits (percentage points)
    MAX_YOY_UNEMPLOYMENT_CHANGE = 3.0
    MAX_YOY_INFLATION_CHANGE = 5.0
    
    # Data completeness
    MIN_YEARS_REQUIRED = 20
    MAX_MISSING_VALUES_PCT = 10.0
    
    # COVID-19 specific validation
    COVID_YEAR = 2020
    COVID_UNEMPLOYMENT_MAX = 8.0  # Annual average, not monthly peak
    
    @classmethod
    def validate_unemployment_value(cls, value: float, year: int) -> Tuple[bool, str]:
        """Validate a single unemployment value."""
        if pd.isna(value):
            return False, "Missing value"
        
        if value < cls.UNEMPLOYMENT_MIN:
            return False, f"Below minimum ({cls.UNEMPLOYMENT_MIN}%)"
        
        if value > cls.UNEMPLOYMENT_MAX:
            return False, f"Above maximum ({cls.UNEMPLOYMENT_MAX}%)"
        
        # Special COVID validation
        if year == cls.COVID_YEAR and value > cls.COVID_UNEMPLOYMENT_MAX:
            return False, f"COVID year exceeds realistic annual average ({cls.COVID_UNEMPLOYMENT_MAX}%)"
        
        return True, "Valid"
    
    @classmethod
    def validate_inflation_value(cls, value: float) -> Tuple[bool, str]:
        """Validate a single inflation value."""
        if pd.isna(value):
            return False, "Missing value"
        
        if value < cls.INFLATION_MIN:
            return False, f"Below minimum ({cls.INFLATION_MIN}%)"
        
        if value > cls.INFLATION_MAX:
            return False, f"Above maximum ({cls.INFLATION_MAX}%)"
        
        return True, "Valid"
    
    @classmethod
    def validate_yoy_change(cls, current: float, previous: float, 
                           metric: str) -> Tuple[bool, str]:
        """Validate year-over-year change."""
        if pd.isna(current) or pd.isna(previous):
            return True, "Skipped (missing data)"
        
        change = abs(current - previous)
        
        if metric == "unemployment":
            max_change = cls.MAX_YOY_UNEMPLOYMENT_CHANGE
        elif metric == "inflation":
            max_change = cls.MAX_YOY_INFLATION_CHANGE
        else:
            return True, "Unknown metric"
        
        if change > max_change:
            return False, f"YoY change {change:.1f}pp exceeds limit ({max_change}pp)"
        
        return True, "Valid"


# ═══════════════════════════════════════════════════════════════════════════
# DATA VALIDATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    corrections_applied: List[str]
    data_quality_score: float  # 0-100
    source_used: DataSource


class DataValidator:
    """Validates and corrects data according to strict rules."""
    
    def __init__(self, auto_correct: bool = True):
        self.auto_correct = auto_correct
        self.validation_log: List[str] = []
    
    def validate_unemployment_data(
        self, 
        df: pd.DataFrame, 
        source: DataSource
    ) -> Tuple[pd.DataFrame, ValidationResult]:
        """
        Validate unemployment data with strict rules.
        
        Returns:
            (corrected_df, validation_result)
        """
        errors = []
        warnings = []
        corrections = []
        
        df = df.copy()
        
        # 1. Check required columns
        if "Year" not in df.columns or "Unemployment_Rate" not in df.columns:
            errors.append("Missing required columns: Year, Unemployment_Rate")
            return df, ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                corrections_applied=corrections,
                data_quality_score=0.0,
                source_used=source
            )
        
        # 2. Check data completeness
        total_rows = len(df)
        missing_count = df["Unemployment_Rate"].isna().sum()
        missing_pct = (missing_count / total_rows) * 100 if total_rows > 0 else 100
        
        if total_rows < ValidationRules.MIN_YEARS_REQUIRED:
            warnings.append(
                f"Insufficient data: {total_rows} years "
                f"(minimum {ValidationRules.MIN_YEARS_REQUIRED})"
            )
        
        if missing_pct > ValidationRules.MAX_MISSING_VALUES_PCT:
            errors.append(
                f"Too many missing values: {missing_pct:.1f}% "
                f"(max {ValidationRules.MAX_MISSING_VALUES_PCT}%)"
            )
        
        # 3. Validate each value
        invalid_count = 0
        for idx, row in df.iterrows():
            year = int(row["Year"])
            value = row["Unemployment_Rate"]
            
            is_valid, msg = ValidationRules.validate_unemployment_value(value, year)
            
            if not is_valid:
                invalid_count += 1
                self.validation_log.append(f"Year {year}: {msg} (value={value})")
                
                if self.auto_correct and not pd.isna(value):
                    # Apply correction
                    if value > ValidationRules.UNEMPLOYMENT_MAX:
                        corrected = ValidationRules.UNEMPLOYMENT_REALISTIC_MAX
                        df.at[idx, "Unemployment_Rate"] = corrected
                        corrections.append(
                            f"Year {year}: Capped {value:.1f}% → {corrected:.1f}%"
                        )
                    elif value < ValidationRules.UNEMPLOYMENT_MIN:
                        corrected = ValidationRules.UNEMPLOYMENT_REALISTIC_MIN
                        df.at[idx, "Unemployment_Rate"] = corrected
                        corrections.append(
                            f"Year {year}: Raised {value:.1f}% → {corrected:.1f}%"
                        )
        
        # 4. Validate year-over-year changes
        df_sorted = df.sort_values("Year").reset_index(drop=True)
        yoy_violations = 0
        
        for i in range(1, len(df_sorted)):
            current = df_sorted.loc[i, "Unemployment_Rate"]
            previous = df_sorted.loc[i-1, "Unemployment_Rate"]
            year = df_sorted.loc[i, "Year"]
            
            is_valid, msg = ValidationRules.validate_yoy_change(
                current, previous, "unemployment"
            )
            
            if not is_valid:
                yoy_violations += 1
                warnings.append(f"Year {year}: {msg}")
        
        # 5. Calculate quality score
        quality_score = 100.0
        quality_score -= (missing_pct * 0.5)  # -0.5 per % missing
        quality_score -= (invalid_count / total_rows) * 30  # -30 for all invalid
        quality_score -= (yoy_violations / total_rows) * 20  # -20 for all violations
        quality_score = max(0.0, min(100.0, quality_score))
        
        # 6. Determine overall validity
        is_valid = (
            len(errors) == 0 and
            quality_score >= 70.0 and
            missing_pct <= ValidationRules.MAX_MISSING_VALUES_PCT
        )
        
        return df, ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            corrections_applied=corrections,
            data_quality_score=quality_score,
            source_used=source
        )
    
    def validate_inflation_data(
        self, 
        df: pd.DataFrame, 
        source: DataSource
    ) -> Tuple[pd.DataFrame, ValidationResult]:
        """
        Validate inflation data with strict rules.
        
        Returns:
            (corrected_df, validation_result)
        """
        errors = []
        warnings = []
        corrections = []
        
        df = df.copy()
        
        # 1. Check required columns
        if "Year" not in df.columns or "Inflation_Rate" not in df.columns:
            errors.append("Missing required columns: Year, Inflation_Rate")
            return df, ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                corrections_applied=corrections,
                data_quality_score=0.0,
                source_used=source
            )
        
        # 2. Check data completeness
        total_rows = len(df)
        missing_count = df["Inflation_Rate"].isna().sum()
        missing_pct = (missing_count / total_rows) * 100 if total_rows > 0 else 100
        
        if total_rows < ValidationRules.MIN_YEARS_REQUIRED:
            warnings.append(
                f"Insufficient data: {total_rows} years "
                f"(minimum {ValidationRules.MIN_YEARS_REQUIRED})"
            )
        
        if missing_pct > ValidationRules.MAX_MISSING_VALUES_PCT:
            errors.append(
                f"Too many missing values: {missing_pct:.1f}% "
                f"(max {ValidationRules.MAX_MISSING_VALUES_PCT}%)"
            )
        
        # 3. Validate each value
        invalid_count = 0
        for idx, row in df.iterrows():
            year = int(row["Year"])
            value = row["Inflation_Rate"]
            
            is_valid, msg = ValidationRules.validate_inflation_value(value)
            
            if not is_valid:
                invalid_count += 1
                self.validation_log.append(f"Year {year}: {msg} (value={value})")
                
                if self.auto_correct and not pd.isna(value):
                    # Apply correction
                    if value > ValidationRules.INFLATION_MAX:
                        corrected = ValidationRules.INFLATION_REALISTIC_MAX
                        df.at[idx, "Inflation_Rate"] = corrected
                        corrections.append(
                            f"Year {year}: Capped {value:.1f}% → {corrected:.1f}%"
                        )
                    elif value < ValidationRules.INFLATION_MIN:
                        corrected = ValidationRules.INFLATION_REALISTIC_MIN
                        df.at[idx, "Inflation_Rate"] = corrected
                        corrections.append(
                            f"Year {year}: Raised {value:.1f}% → {corrected:.1f}%"
                        )
        
        # 4. Validate year-over-year changes
        df_sorted = df.sort_values("Year").reset_index(drop=True)
        yoy_violations = 0
        
        for i in range(1, len(df_sorted)):
            current = df_sorted.loc[i, "Inflation_Rate"]
            previous = df_sorted.loc[i-1, "Inflation_Rate"]
            year = df_sorted.loc[i, "Year"]
            
            is_valid, msg = ValidationRules.validate_yoy_change(
                current, previous, "inflation"
            )
            
            if not is_valid:
                yoy_violations += 1
                warnings.append(f"Year {year}: {msg}")
        
        # 5. Calculate quality score
        quality_score = 100.0
        quality_score -= (missing_pct * 0.5)
        quality_score -= (invalid_count / total_rows) * 30
        quality_score -= (yoy_violations / total_rows) * 20
        quality_score = max(0.0, min(100.0, quality_score))
        
        # 6. Determine overall validity
        is_valid = (
            len(errors) == 0 and
            quality_score >= 70.0 and
            missing_pct <= ValidationRules.MAX_MISSING_VALUES_PCT
        )
        
        return df, ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            corrections_applied=corrections,
            data_quality_score=quality_score,
            source_used=source
        )


# ═══════════════════════════════════════════════════════════════════════════
# CENTRAL DATA LOADER
# ═══════════════════════════════════════════════════════════════════════════

class CentralDataLoader:
    """
    SINGLE SOURCE OF TRUTH for all economic data.
    
    All modules MUST use this class to access data.
    Direct CSV access is FORBIDDEN.
    """
    
    def __init__(self):
        self.validator = DataValidator(auto_correct=True)
        self._unemployment_cache: Optional[Tuple[pd.DataFrame, ValidationResult]] = None
        self._inflation_cache: Optional[Tuple[pd.DataFrame, ValidationResult]] = None
        self.load_timestamp = datetime.now()
    
    def load_unemployment_data(
        self, 
        force_reload: bool = False
    ) -> Tuple[pd.DataFrame, ValidationResult]:
        """
        Load and validate unemployment data.
        
        Priority:
        1. Curated realistic data (HIGH quality)
        2. Original data (MEDIUM quality)
        3. Empty DataFrame with error
        
        Returns:
            (dataframe, validation_result)
        """
        if self._unemployment_cache is not None and not force_reload:
            return self._unemployment_cache
        
        # Try primary source (curated data)
        if UNEMPLOYMENT_SOURCE.path and UNEMPLOYMENT_SOURCE.path.exists():
            try:
                df = pd.read_csv(UNEMPLOYMENT_SOURCE.path)
                df, result = self.validator.validate_unemployment_data(
                    df, UNEMPLOYMENT_SOURCE
                )
                
                if result.is_valid or result.data_quality_score >= 70.0:
                    self._unemployment_cache = (df, result)
                    return df, result
            except Exception as e:
                print(f"⚠️  Failed to load primary unemployment source: {e}")
        
        # Try fallback source
        if UNEMPLOYMENT_FALLBACK.path and UNEMPLOYMENT_FALLBACK.path.exists():
            try:
                df = pd.read_csv(UNEMPLOYMENT_FALLBACK.path)
                df, result = self.validator.validate_unemployment_data(
                    df, UNEMPLOYMENT_FALLBACK
                )
                
                result.warnings.append(
                    "Using fallback data source (lower quality)"
                )
                
                self._unemployment_cache = (df, result)
                return df, result
            except Exception as e:
                print(f"⚠️  Failed to load fallback unemployment source: {e}")
        
        # No data available
        empty_df = pd.DataFrame(columns=["Year", "Unemployment_Rate"])
        result = ValidationResult(
            is_valid=False,
            errors=["No unemployment data source available"],
            warnings=[],
            corrections_applied=[],
            data_quality_score=0.0,
            source_used=DataSource(
                name="None",
                path=None,
                description="No data available",
                quality_level="UNKNOWN",
                last_updated=None,
                source_authority="None",
                notes="CRITICAL: No data source found"
            )
        )
        
        return empty_df, result
    
    def load_inflation_data(
        self, 
        force_reload: bool = False
    ) -> Tuple[pd.DataFrame, ValidationResult]:
        """
        Load and validate inflation data.
        
        Returns:
            (dataframe, validation_result)
        """
        if self._inflation_cache is not None and not force_reload:
            return self._inflation_cache
        
        # Try primary source (corrected data)
        if INFLATION_SOURCE.path and INFLATION_SOURCE.path.exists():
            try:
                df = pd.read_csv(INFLATION_SOURCE.path)
                df, result = self.validator.validate_inflation_data(
                    df, INFLATION_SOURCE
                )
                
                if result.is_valid or result.data_quality_score >= 70.0:
                    self._inflation_cache = (df, result)
                    return df, result
            except Exception as e:
                print(f"⚠️  Failed to load inflation source: {e}")
        
        # No data available
        empty_df = pd.DataFrame(columns=["Year", "Inflation_Rate"])
        result = ValidationResult(
            is_valid=False,
            errors=["No inflation data source available"],
            warnings=[],
            corrections_applied=[],
            data_quality_score=0.0,
            source_used=DataSource(
                name="None",
                path=None,
                description="No data available",
                quality_level="UNKNOWN",
                last_updated=None,
                source_authority="None",
                notes="CRITICAL: No data source found"
            )
        )
        
        return empty_df, result
    
    def get_data_quality_report(self) -> Dict:
        """
        Generate comprehensive data quality report.
        
        Returns:
            Dictionary with quality metrics for all data sources
        """
        unemployment_df, unemployment_result = self.load_unemployment_data()
        inflation_df, inflation_result = self.load_inflation_data()
        
        return {
            "timestamp": self.load_timestamp.isoformat(),
            "unemployment": {
                "source": unemployment_result.source_used.name,
                "quality_level": unemployment_result.source_used.quality_level,
                "data_quality_score": unemployment_result.data_quality_score,
                "is_valid": unemployment_result.is_valid,
                "rows": len(unemployment_df),
                "year_range": (
                    f"{unemployment_df['Year'].min()}-{unemployment_df['Year'].max()}"
                    if not unemployment_df.empty else "N/A"
                ),
                "errors": unemployment_result.errors,
                "warnings": unemployment_result.warnings,
                "corrections": unemployment_result.corrections_applied,
            },
            "inflation": {
                "source": inflation_result.source_used.name,
                "quality_level": inflation_result.source_used.quality_level,
                "data_quality_score": inflation_result.data_quality_score,
                "is_valid": inflation_result.is_valid,
                "rows": len(inflation_df),
                "year_range": (
                    f"{inflation_df['Year'].min()}-{inflation_df['Year'].max()}"
                    if not inflation_df.empty else "N/A"
                ),
                "errors": inflation_result.errors,
                "warnings": inflation_result.warnings,
                "corrections": inflation_result.corrections_applied,
            },
            "overall_system_health": (
                "HEALTHY" if (
                    unemployment_result.is_valid and 
                    inflation_result.is_valid
                ) else "DEGRADED" if (
                    unemployment_result.data_quality_score >= 70 and
                    inflation_result.data_quality_score >= 70
                ) else "CRITICAL"
            )
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE (Singleton Pattern)
# ═══════════════════════════════════════════════════════════════════════════

_CENTRAL_DATA_LOADER: Optional[CentralDataLoader] = None


def get_central_data_loader() -> CentralDataLoader:
    """Get the global central data loader instance."""
    global _CENTRAL_DATA_LOADER
    if _CENTRAL_DATA_LOADER is None:
        _CENTRAL_DATA_LOADER = CentralDataLoader()
    return _CENTRAL_DATA_LOADER


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API (What other modules should use)
# ═══════════════════════════════════════════════════════════════════════════

def load_unemployment() -> pd.DataFrame:
    """
    Load validated unemployment data.
    
    This is the ONLY function other modules should use for unemployment data.
    
    Returns:
        DataFrame with columns: Year, Unemployment_Rate
    """
    loader = get_central_data_loader()
    df, result = loader.load_unemployment_data()
    
    if not result.is_valid:
        print("⚠️  WARNING: Unemployment data failed validation")
        for error in result.errors:
            print(f"   ERROR: {error}")
    
    if result.warnings:
        for warning in result.warnings:
            print(f"   WARNING: {warning}")
    
    return df


def load_inflation() -> pd.DataFrame:
    """
    Load validated inflation data.
    
    This is the ONLY function other modules should use for inflation data.
    
    Returns:
        DataFrame with columns: Year, Inflation_Rate
    """
    loader = get_central_data_loader()
    df, result = loader.load_inflation_data()
    
    if not result.is_valid:
        print("⚠️  WARNING: Inflation data failed validation")
        for error in result.errors:
            print(f"   ERROR: {error}")
    
    if result.warnings:
        for warning in result.warnings:
            print(f"   WARNING: {warning}")
    
    return df


def get_data_quality_report() -> Dict:
    """
    Get comprehensive data quality report.
    
    Returns:
        Dictionary with quality metrics
    """
    loader = get_central_data_loader()
    return loader.get_data_quality_report()


def print_data_quality_report() -> None:
    """Print formatted data quality report to console."""
    report = get_data_quality_report()
    
    print("\n" + "="*80)
    print("DATA QUALITY REPORT")
    print("="*80)
    print(f"Timestamp: {report['timestamp']}")
    print(f"System Health: {report['overall_system_health']}")
    print()
    
    print("UNEMPLOYMENT DATA:")
    print(f"  Source: {report['unemployment']['source']}")
    print(f"  Quality Level: {report['unemployment']['quality_level']}")
    print(f"  Quality Score: {report['unemployment']['data_quality_score']:.1f}/100")
    print(f"  Valid: {report['unemployment']['is_valid']}")
    print(f"  Rows: {report['unemployment']['rows']}")
    print(f"  Year Range: {report['unemployment']['year_range']}")
    
    if report['unemployment']['errors']:
        print("  Errors:")
        for error in report['unemployment']['errors']:
            print(f"    - {error}")
    
    if report['unemployment']['warnings']:
        print("  Warnings:")
        for warning in report['unemployment']['warnings']:
            print(f"    - {warning}")
    
    if report['unemployment']['corrections']:
        print("  Corrections Applied:")
        for correction in report['unemployment']['corrections']:
            print(f"    - {correction}")
    
    print()
    print("INFLATION DATA:")
    print(f"  Source: {report['inflation']['source']}")
    print(f"  Quality Level: {report['inflation']['quality_level']}")
    print(f"  Quality Score: {report['inflation']['data_quality_score']:.1f}/100")
    print(f"  Valid: {report['inflation']['is_valid']}")
    print(f"  Rows: {report['inflation']['rows']}")
    print(f"  Year Range: {report['inflation']['year_range']}")
    
    if report['inflation']['errors']:
        print("  Errors:")
        for error in report['inflation']['errors']:
            print(f"    - {error}")
    
    if report['inflation']['warnings']:
        print("  Warnings:")
        for warning in report['inflation']['warnings']:
            print(f"    - {warning}")
    
    if report['inflation']['corrections']:
        print("  Corrections Applied:")
        for correction in report['inflation']['corrections']:
            print(f"    - {correction}")
    
    print("="*80 + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# MODULE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test the central data loader
    print_data_quality_report()
