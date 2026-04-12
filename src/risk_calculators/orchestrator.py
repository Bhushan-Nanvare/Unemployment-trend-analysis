"""Risk calculator orchestrator that coordinates all risk assessments."""

from datetime import datetime
from typing import Dict
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
    """Coordinates execution of all risk calculators"""
    
    def __init__(self):
        self.automation_calc = AutomationRiskCalculator()
        self.recession_calc = RecessionRiskCalculator()
        self.age_disc_calc = AgeDiscriminationRiskCalculator()
    
    def calculate_all_risks(self, profile: UserProfile) -> RiskProfile:
        """Execute all risk calculators and aggregate results"""
        
        # Calculate individual risk scores
        automation_result = self.automation_calc.calculate(profile)
        recession_result = self.recession_calc.calculate(profile)
        age_disc_result = self.age_disc_calc.calculate(profile)
        
        # Calculate overall risk using existing model
        skills_text = ", ".join(profile.skills)
        overall_result = predict_job_risk(
            skills_text=skills_text,
            education_label=profile.education_level,
            experience_years=profile.experience_years,
            location_label=profile.location,
            industry_label=profile.industry,
        )
        overall_risk = overall_result.high_risk_probability_pct
        
        # Aggregate contributing factors from all calculators
        contributing_factors = {}
        
        # Add overall risk factors
        if overall_result.contributions:
            for key, value in overall_result.contributions.items():
                contributing_factors[f"overall_{key}"] = value
        
        # Add automation risk factors
        for key, value in automation_result.contributing_factors.items():
            contributing_factors[f"automation_{key}"] = value
        
        # Add recession risk factors
        for key, value in recession_result.contributing_factors.items():
            contributing_factors[f"recession_{key}"] = value
        
        # Add age discrimination risk factors
        for key, value in age_disc_result.contributing_factors.items():
            contributing_factors[f"age_disc_{key}"] = value
        
        # Determine overall risk level
        risk_level = self.get_risk_level(overall_risk)
        
        return RiskProfile(
            overall_risk=overall_risk,
            automation_risk=automation_result.score,
            recession_risk=recession_result.score,
            age_discrimination_risk=age_disc_result.score,
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            timestamp=datetime.now(),
        )
    
    def get_risk_level(self, overall_risk: float) -> str:
        """Map risk score to level: Low (0-35), Medium (35-62), High (62-100)"""
        if overall_risk >= 62.0:
            return "High"
        elif overall_risk >= 35.0:
            return "Medium"
        else:
            return "Low"
