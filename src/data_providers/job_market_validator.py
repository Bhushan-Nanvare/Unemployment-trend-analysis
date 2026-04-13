"""
job_market_validator.py

JOB MARKET DATA VALIDATOR
==========================

Validates job market data from Adzuna API to ensure quality and consistency.
Discards invalid data and provides clear labeling of data sources.

Author: System Refactoring
Date: 2026-04-13
Version: 1.0.0
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of job market data validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    data_quality_score: float  # 0-100


class JobMarketValidator:
    """Validates job market data with strict rules"""
    
    # Validation thresholds
    MIN_JOB_COUNT = 0
    MAX_JOB_COUNT = 100000
    
    MIN_SALARY = 100000  # 1 LPA minimum
    MAX_SALARY = 50000000  # 5 Crore maximum
    
    MIN_REMOTE_PCT = 0.0
    MAX_REMOTE_PCT = 100.0
    
    REQUIRED_FIELDS = ["total_jobs", "avg_salary", "top_skills", "source"]
    
    @classmethod
    def validate_job_data(cls, data: Dict) -> Tuple[bool, ValidationResult]:
        """
        Validate job market data from Adzuna API.
        
        Args:
            data: Job market data dictionary
            
        Returns:
            (is_valid, validation_result)
        """
        errors = []
        warnings = []
        quality_score = 100.0
        
        # 1. Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
                quality_score -= 25
        
        if errors:
            return False, ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                data_quality_score=0.0
            )
        
        # 2. Validate job count
        total_jobs = data.get("total_jobs", 0)
        if not isinstance(total_jobs, (int, float)):
            errors.append(f"Invalid job count type: {type(total_jobs)}")
            quality_score -= 20
        elif total_jobs < cls.MIN_JOB_COUNT:
            errors.append(f"Job count below minimum: {total_jobs} < {cls.MIN_JOB_COUNT}")
            quality_score -= 20
        elif total_jobs > cls.MAX_JOB_COUNT:
            warnings.append(f"Job count unusually high: {total_jobs}")
            quality_score -= 5
        elif total_jobs == 0:
            warnings.append("Zero jobs found - may indicate no market demand")
            quality_score -= 10
        
        # 3. Validate salary
        avg_salary = data.get("avg_salary", 0)
        if not isinstance(avg_salary, (int, float)):
            errors.append(f"Invalid salary type: {type(avg_salary)}")
            quality_score -= 20
        elif avg_salary < cls.MIN_SALARY:
            errors.append(f"Salary below minimum: {avg_salary} < {cls.MIN_SALARY}")
            quality_score -= 20
        elif avg_salary > cls.MAX_SALARY:
            errors.append(f"Salary above maximum: {avg_salary} > {cls.MAX_SALARY}")
            quality_score -= 20
        
        # 4. Validate skills
        top_skills = data.get("top_skills", [])
        if not isinstance(top_skills, list):
            errors.append(f"Invalid skills type: {type(top_skills)}")
            quality_score -= 15
        elif len(top_skills) == 0:
            warnings.append("No skills data available")
            quality_score -= 10
        elif len(top_skills) < 3:
            warnings.append(f"Limited skills data: only {len(top_skills)} skills")
            quality_score -= 5
        
        # 5. Validate remote percentage (if present)
        if "remote_percentage" in data:
            remote_pct = data.get("remote_percentage", 0)
            if not isinstance(remote_pct, (int, float)):
                warnings.append(f"Invalid remote percentage type: {type(remote_pct)}")
                quality_score -= 5
            elif remote_pct < cls.MIN_REMOTE_PCT or remote_pct > cls.MAX_REMOTE_PCT:
                warnings.append(f"Remote percentage out of range: {remote_pct}")
                quality_score -= 5
        
        # 6. Validate companies (if present)
        if "top_companies" in data:
            companies = data.get("top_companies", [])
            if not isinstance(companies, list):
                warnings.append(f"Invalid companies type: {type(companies)}")
                quality_score -= 5
            elif len(companies) == 0:
                warnings.append("No company data available")
                quality_score -= 5
        
        # 7. Check data source
        source = data.get("source", "unknown")
        if source not in ["adzuna", "historical_csv", "default"]:
            warnings.append(f"Unknown data source: {source}")
            quality_score -= 5
        
        # Calculate final validity
        is_valid = len(errors) == 0 and quality_score >= 60.0
        
        return is_valid, ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            data_quality_score=max(0.0, min(100.0, quality_score))
        )
    
    @classmethod
    def validate_and_clean(cls, data: Dict) -> Tuple[Optional[Dict], ValidationResult]:
        """
        Validate and clean job market data.
        
        Args:
            data: Raw job market data
            
        Returns:
            (cleaned_data or None, validation_result)
        """
        is_valid, result = cls.validate_job_data(data)
        
        if not is_valid:
            logger.error(f"Job market data validation failed: {result.errors}")
            return None, result
        
        # Clean and normalize data
        cleaned_data = {
            "total_jobs": int(data.get("total_jobs", 0)),
            "avg_salary": float(data.get("avg_salary", 0)),
            "top_skills": list(data.get("top_skills", [])),
            "top_companies": list(data.get("top_companies", [])),
            "remote_percentage": float(data.get("remote_percentage", 0.0)),
            "source": data.get("source", "unknown"),
            "market_health": data.get("market_health", "unknown"),
            "demand_level": data.get("demand_level", "unknown"),
            "salary_trend": data.get("salary_trend", "unknown"),
            "data_freshness": data.get("data_freshness", "unknown"),
            "confidence_score": result.data_quality_score / 100.0,  # 0-1 scale
            "validation_passed": True,
            "validation_warnings": result.warnings,
        }
        
        return cleaned_data, result
    
    @classmethod
    def get_data_source_label(cls, data: Dict) -> str:
        """
        Get clear label for data source.
        
        Args:
            data: Job market data
            
        Returns:
            Clear label string
        """
        source = data.get("source", "unknown")
        data_freshness = data.get("data_freshness", "unknown")
        
        if source == "adzuna":
            return "🟢 Live Market Data (Current - 2026)"
        elif source == "historical_csv":
            return "🟡 Historical Baseline (2019 - NOT CURRENT)"
        elif source == "default":
            return "🔴 Default Estimates (Low Confidence)"
        else:
            return "⚠️ Unknown Data Source"
    
    @classmethod
    def get_data_age_warning(cls, data: Dict) -> Optional[str]:
        """
        Get warning message if data is outdated.
        
        Args:
            data: Job market data
            
        Returns:
            Warning message or None
        """
        source = data.get("source", "unknown")
        
        if source == "historical_csv":
            return (
                "⚠️ WARNING: Using historical data from 2019 (7 years old). "
                "Job market has significantly changed since then. "
                "Enable Adzuna API for current market data."
            )
        elif source == "default":
            return (
                "⚠️ WARNING: Using default estimates. "
                "No real market data available. "
                "Results may not reflect actual market conditions."
            )
        
        return None
    
    @classmethod
    def ensure_consistency(cls, data_list: List[Dict]) -> bool:
        """
        Ensure all data in list comes from same source.
        
        Args:
            data_list: List of job market data dictionaries
            
        Returns:
            True if consistent, False if mixed sources
        """
        if not data_list:
            return True
        
        sources = set(d.get("source", "unknown") for d in data_list)
        
        if len(sources) > 1:
            logger.error(f"Mixed data sources detected: {sources}")
            return False
        
        return True
    
    @classmethod
    def get_validation_summary(cls, result: ValidationResult) -> str:
        """
        Get human-readable validation summary.
        
        Args:
            result: ValidationResult
            
        Returns:
            Summary string
        """
        if result.is_valid:
            status = "✅ VALID"
        else:
            status = "❌ INVALID"
        
        summary = f"{status} - Quality Score: {result.data_quality_score:.1f}/100\n"
        
        if result.errors:
            summary += f"\nErrors ({len(result.errors)}):\n"
            for error in result.errors:
                summary += f"  ❌ {error}\n"
        
        if result.warnings:
            summary += f"\nWarnings ({len(result.warnings)}):\n"
            for warning in result.warnings:
                summary += f"  ⚠️ {warning}\n"
        
        return summary


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*80)
    print("JOB MARKET VALIDATOR TEST")
    print("="*80 + "\n")
    
    # Test 1: Valid data
    print("TEST 1: Valid Adzuna data")
    valid_data = {
        "total_jobs": 1500,
        "avg_salary": 800000,
        "top_skills": ["python", "java", "sql", "aws", "docker"],
        "top_companies": ["TCS", "Infosys", "Wipro"],
        "remote_percentage": 35.0,
        "source": "adzuna",
        "market_health": "good",
        "demand_level": "high",
        "salary_trend": "increasing",
        "data_freshness": "2026-04-13"
    }
    
    is_valid, result = JobMarketValidator.validate_job_data(valid_data)
    print(JobMarketValidator.get_validation_summary(result))
    print(f"Data Source Label: {JobMarketValidator.get_data_source_label(valid_data)}")
    
    # Test 2: Invalid data (salary too low)
    print("\n" + "-"*80)
    print("TEST 2: Invalid data (salary too low)")
    invalid_data = {
        "total_jobs": 100,
        "avg_salary": 50000,  # Too low
        "top_skills": ["python"],
        "source": "adzuna"
    }
    
    is_valid, result = JobMarketValidator.validate_job_data(invalid_data)
    print(JobMarketValidator.get_validation_summary(result))
    
    # Test 3: Historical data
    print("\n" + "-"*80)
    print("TEST 3: Historical data")
    historical_data = {
        "total_jobs": 500,
        "avg_salary": 600000,
        "top_skills": ["java", "spring", "hibernate"],
        "source": "historical_csv",
        "data_freshness": "2019-07-01"
    }
    
    is_valid, result = JobMarketValidator.validate_job_data(historical_data)
    print(JobMarketValidator.get_validation_summary(result))
    print(f"Data Source Label: {JobMarketValidator.get_data_source_label(historical_data)}")
    warning = JobMarketValidator.get_data_age_warning(historical_data)
    if warning:
        print(f"\n{warning}")
    
    # Test 4: Consistency check
    print("\n" + "-"*80)
    print("TEST 4: Consistency check")
    data_list = [valid_data, historical_data]
    is_consistent = JobMarketValidator.ensure_consistency(data_list)
    print(f"Mixed sources consistent: {is_consistent}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
