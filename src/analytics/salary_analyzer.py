"""Salary impact analyzer with location and risk adjustments."""

import numpy as np
from typing import Dict
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_calculators import UserProfile, RiskProfile
from analytics import SalaryEstimate


class SalaryAnalyzer:
    """Computes location-adjusted and risk-adjusted salary estimates"""
    
    # Base salary factors
    BASE_SALARY_FACTORS = {
        "role_level_multiplier": {
            "Entry": 1.0,
            "Mid": 1.4,
            "Senior": 1.9,
            "Lead": 2.5,
            "Executive": 3.5,
        },
        "industry_multiplier": {
            "Technology / software": 1.3,
            "Financial services / fintech": 1.25,
            "Healthcare / biotech": 1.15,
            "Renewable energy / climate": 1.20,
            "Education / edtech": 0.90,
            "Retail / e-commerce ops": 0.85,
            "Manufacturing (traditional)": 0.95,
            "Hospitality / tourism": 0.80,
            "Other / not listed": 1.00,
        },
        "experience_multiplier": 0.03,  # 3% per year
    }
    
    # Location cost-of-living multipliers
    LOCATION_MULTIPLIERS = {
        "Metro / Tier-1 city": 1.50,
        "Tier-2 city": 1.15,
        "Smaller town / rural": 0.85,
    }
    
    # Risk penalty: 2% reduction per 10 points of risk above 30
    RISK_PENALTY_THRESHOLD = 30
    RISK_PENALTY_RATE = 0.02  # per 10 points
    
    def analyze(
        self, 
        profile: UserProfile, 
        risk_profile: RiskProfile
    ) -> SalaryEstimate:
        """
        Calculate salary estimates with adjustments
        
        Algorithm:
        1. Compute base salary:
           base = 50000 * role_multiplier * industry_multiplier * (1 + exp * 0.03)
        2. Apply location multiplier:
           location_adjusted = base * location_multiplier
        3. Apply risk penalty if overall_risk > 30:
           penalty_pct = ((overall_risk - 30) / 10) * 0.02
           risk_adjusted = location_adjusted * (1 - penalty_pct)
        4. Compute confidence interval (±15%)
        5. Generate explanation text
        """
        # Step 1: Compute base salary
        role_mult = self.BASE_SALARY_FACTORS["role_level_multiplier"].get(profile.role_level, 1.0)
        industry_mult = self.BASE_SALARY_FACTORS["industry_multiplier"].get(profile.industry, 1.0)
        exp_mult = 1.0 + (profile.experience_years * self.BASE_SALARY_FACTORS["experience_multiplier"])
        
        base_salary = 50000 * role_mult * industry_mult * exp_mult
        
        # Step 2: Apply location multiplier
        location_mult = self.LOCATION_MULTIPLIERS.get(profile.location, 1.0)
        location_adjusted = base_salary * location_mult
        
        # Step 3: Apply risk penalty
        risk_penalty_pct = 0.0
        if risk_profile.overall_risk > self.RISK_PENALTY_THRESHOLD:
            risk_points_above = risk_profile.overall_risk - self.RISK_PENALTY_THRESHOLD
            risk_penalty_pct = (risk_points_above / 10.0) * self.RISK_PENALTY_RATE
        
        risk_adjusted = location_adjusted * (1.0 - risk_penalty_pct)
        
        # Step 4: Compute confidence interval (±15%)
        confidence_low = risk_adjusted * 0.85
        confidence_high = risk_adjusted * 1.15
        
        # Step 5: Generate explanation
        explanation = self._generate_explanation(
            base_salary, location_mult, risk_penalty_pct, profile, risk_profile
        )
        
        return SalaryEstimate(
            base_salary=round(base_salary, 2),
            location_adjusted=round(location_adjusted, 2),
            risk_adjusted=round(risk_adjusted, 2),
            location_multiplier=location_mult,
            risk_penalty_pct=round(risk_penalty_pct * 100, 1),
            confidence_interval=(round(confidence_low, 2), round(confidence_high, 2)),
            explanation=explanation,
        )
    
    def _generate_explanation(
        self,
        base_salary: float,
        location_mult: float,
        risk_penalty_pct: float,
        profile: UserProfile,
        risk_profile: RiskProfile,
    ) -> str:
        """Generate human-readable explanation"""
        parts = []
        
        parts.append(
            f"Base salary of ${base_salary:,.0f} calculated from {profile.role_level} "
            f"role in {profile.industry} with {profile.experience_years} years experience."
        )
        
        if location_mult != 1.0:
            parts.append(
                f"Location adjustment ({profile.location}): {location_mult:.2f}x multiplier."
            )
        
        if risk_penalty_pct > 0:
            parts.append(
                f"Risk penalty: {risk_penalty_pct*100:.1f}% reduction due to overall risk of "
                f"{risk_profile.overall_risk:.1f}% (above {self.RISK_PENALTY_THRESHOLD}% threshold)."
            )
        else:
            parts.append(
                f"No risk penalty applied (overall risk {risk_profile.overall_risk:.1f}% "
                f"is below {self.RISK_PENALTY_THRESHOLD}% threshold)."
            )
        
        return " ".join(parts)
