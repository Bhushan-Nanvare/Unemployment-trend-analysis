"""
Risk calculator orchestrator that coordinates all risk assessments.

DATA QUALITY & VALIDATION:
- All inputs are validated before calculation
- Invalid inputs trigger clear error messages
- Insufficient data is flagged explicitly
- All calculations are deterministic and explainable
"""

from datetime import datetime
from typing import Dict, Tuple, List
import sys
import os

# Add parent directory to path to import job_risk_model
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from . import UserProfile, RiskProfile
from .automation_risk import AutomationRiskCalculator
from .recession_risk import RecessionRiskCalculator
from .age_discrimination_risk import AgeDiscriminationRiskCalculator
from job_risk_model import predict_job_risk, parse_skills


class RiskCalculatorOrchestrator:
    """
    Coordinates execution of all risk calculators with validation.
    
    Features:
    - Input validation before calculation
    - Data quality checks
    - Clear error messages for invalid inputs
    - Deterministic calculations
    """
    
    def __init__(self):
        self.automation_calc = AutomationRiskCalculator()
        self.recession_calc = RecessionRiskCalculator()
        self.age_disc_calc = AgeDiscriminationRiskCalculator()
        self.validation_warnings: List[str] = []
    
    def validate_profile(self, profile: UserProfile) -> Tuple[bool, List[str]]:
        """
        Validate user profile has sufficient data for risk calculation.
        
        Returns:
            (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check required fields
        if not profile.skills or len(profile.skills) == 0:
            warnings.append("⚠️  INSUFFICIENT DATA: No skills provided")
        
        if not profile.industry:
            warnings.append("⚠️  INSUFFICIENT DATA: No industry specified")
        
        if not profile.role_level:
            warnings.append("⚠️  INSUFFICIENT DATA: No role level specified")
        
        # Validate ranges
        if profile.experience_years < 0:
            warnings.append("❌ INVALID DATA: Experience years cannot be negative")
        
        if profile.experience_years > 60:
            warnings.append("⚠️  WARNING: Experience years seems unusually high (>60)")
        
        if profile.age < 18:
            warnings.append("❌ INVALID DATA: Age must be at least 18")
        
        if profile.age > 80:
            warnings.append("⚠️  WARNING: Age seems unusually high (>80)")
        
        if profile.performance_rating < 1 or profile.performance_rating > 5:
            warnings.append("❌ INVALID DATA: Performance rating must be 1-5")
        
        # Check data consistency
        if profile.age < 18 + profile.experience_years:
            warnings.append(
                f"⚠️  WARNING: Age ({profile.age}) and experience ({profile.experience_years} years) "
                "seem inconsistent (age should be at least 18 + experience)"
            )
        
        # Determine if valid (no critical errors)
        critical_errors = [w for w in warnings if "❌" in w]
        is_valid = len(critical_errors) == 0
        
        return is_valid, warnings
    
    def calculate_all_risks(self, profile: UserProfile) -> RiskProfile:
        """
        Execute all risk calculators and aggregate results.
        
        Validates input before calculation and includes data quality warnings.
        """
        # Reset warnings
        self.validation_warnings = []
        
        # Validate profile
        is_valid, warnings = self.validate_profile(profile)
        self.validation_warnings = warnings
        
        if not is_valid:
            # Return error profile with zero risks
            return RiskProfile(
                overall_risk=0.0,
                automation_risk=0.0,
                recession_risk=0.0,
                age_discrimination_risk=0.0,
                risk_level="Error",
                contributing_factors={"error": "Invalid input data"},
                timestamp=datetime.now(),
                data_quality_warnings=warnings,
            )
        
        # Calculate individual risk scores
        try:
            automation_result = self.automation_calc.calculate(profile)
        except Exception as e:
            warnings.append(f"⚠️  Automation risk calculation failed: {str(e)}")
            automation_result = None
        
        try:
            recession_result = self.recession_calc.calculate(profile)
        except Exception as e:
            warnings.append(f"⚠️  Recession risk calculation failed: {str(e)}")
            recession_result = None
        
        try:
            age_disc_result = self.age_disc_calc.calculate(profile)
        except Exception as e:
            warnings.append(f"⚠️  Age discrimination risk calculation failed: {str(e)}")
            age_disc_result = None
        
        # Calculate overall risk using existing model
        try:
            skills_text = ", ".join(profile.skills)
            overall_result = predict_job_risk(
                skills_text=skills_text,
                education_label=profile.education_level,
                experience_years=profile.experience_years,
                location_label=profile.location,
                industry_label=profile.industry,
            )
            overall_risk = overall_result.high_risk_probability_pct
            
            # Add model warnings
            if hasattr(overall_result, 'data_quality_warning'):
                warnings.append(overall_result.data_quality_warning)
        except Exception as e:
            warnings.append(f"⚠️  Overall risk calculation failed: {str(e)}")
            overall_risk = 0.0
            overall_result = None
        
        # Aggregate contributing factors from all calculators
        contributing_factors = {}
        
        # Add overall risk factors
        if overall_result and overall_result.contributions:
            for key, value in overall_result.contributions.items():
                contributing_factors[f"overall_{key}"] = value
        
        # Add automation risk factors
        if automation_result:
            for key, value in automation_result.contributing_factors.items():
                contributing_factors[f"automation_{key}"] = value
        
        # Add recession risk factors
        if recession_result:
            for key, value in recession_result.contributing_factors.items():
                contributing_factors[f"recession_{key}"] = value
        
        # Add age discrimination risk factors
        if age_disc_result:
            for key, value in age_disc_result.contributing_factors.items():
                contributing_factors[f"age_disc_{key}"] = value
        
        # Determine overall risk level
        risk_level = self.get_risk_level(overall_risk)
        
        return RiskProfile(
            overall_risk=overall_risk,
            automation_risk=automation_result.score if automation_result else 0.0,
            recession_risk=recession_result.score if recession_result else 0.0,
            age_discrimination_risk=age_disc_result.score if age_disc_result else 0.0,
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            timestamp=datetime.now(),
            data_quality_warnings=warnings if warnings else None,
        )
    
    def get_risk_level(self, overall_risk: float) -> str:
        """Map risk score to level: Low (0-35), Medium (35-62), High (62-100)"""
        if overall_risk >= 62.0:
            return "High"
        elif overall_risk >= 35.0:
            return "Medium"
        else:
            return "Low"
