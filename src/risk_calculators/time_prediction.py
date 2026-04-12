"""Time-based risk prediction calculator."""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List
from . import UserProfile, RiskProfile


@dataclass
class TimeHorizonPrediction:
    """Risk prediction for a specific time horizon"""
    horizon: str  # "6 months", "1 year", "3 years", "5 years"
    overall_risk: float
    automation_risk: float
    recession_risk: float
    age_discrimination_risk: float
    key_factors: List[str]


class TimePredictionCalculator:
    """Projects risk scores across multiple time horizons"""
    
    # Automation adoption acceleration rates (per year)
    AUTOMATION_ACCELERATION = {
        "Manufacturing (traditional)": 0.08,  # 8% increase per year
        "Retail / e-commerce ops": 0.07,
        "Financial services / fintech": 0.06,
        "Technology / software": 0.04,
        "Healthcare / biotech": 0.03,
        "Education / edtech": 0.04,
        "Renewable energy / climate": 0.05,
        "Hospitality / tourism": 0.06,
        "Other / not listed": 0.05,
    }
    
    # Industry growth/decline rates (per year, negative = risk decreases)
    INDUSTRY_TREND_RATES = {
        "Technology / software": -0.02,  # Negative = risk decreases
        "Renewable energy / climate": -0.03,
        "Healthcare / biotech": -0.02,
        "Manufacturing (traditional)": 0.05,  # Positive = risk increases
        "Hospitality / tourism": 0.04,
        "Retail / e-commerce ops": 0.03,
        "Financial services / fintech": 0.01,
        "Education / edtech": 0.00,
        "Other / not listed": 0.02,
    }
    
    # Skill decay rate (per year without development)
    SKILL_DECAY_RATE = 0.03  # 3% risk increase per year
    
    # Continuous learning benefit (per year with development)
    LEARNING_BENEFIT_RATE = -0.03  # 3% risk decrease per year
    
    def predict_time_horizons(
        self, 
        current_profile: RiskProfile,
        user_profile: UserProfile,
        assumes_learning: bool = False
    ) -> List[TimeHorizonPrediction]:
        """
        Project risk scores for 6mo, 1yr, 3yr, 5yr horizons
        
        Algorithm:
        1. Start with current risk scores
        2. For each time horizon:
           a. Apply automation acceleration for automation risk
           b. Apply industry trend rates for recession risk
           c. Apply age progression for age discrimination risk
           d. Apply skill decay or learning benefit
           e. Ensure monotonic non-decreasing unless learning modeled
        3. Identify key factors driving changes
        """
        time_horizons = [
            ("6 months", 0.5),
            ("1 year", 1.0),
            ("3 years", 3.0),
            ("5 years", 5.0),
        ]
        
        predictions = []
        
        for horizon_name, years in time_horizons:
            # Start with current risks
            overall = current_profile.overall_risk
            automation = current_profile.automation_risk
            recession = current_profile.recession_risk
            age_disc = current_profile.age_discrimination_risk
            
            key_factors = []
            
            # Apply automation acceleration
            auto_accel = self.AUTOMATION_ACCELERATION.get(user_profile.industry, 0.05)
            automation_increase = auto_accel * 100 * years
            automation = min(100.0, automation + automation_increase)
            if automation_increase > 2:
                key_factors.append(f"Automation adoption increasing in {user_profile.industry}")
            
            # Apply industry trend for recession risk
            industry_trend = self.INDUSTRY_TREND_RATES.get(user_profile.industry, 0.02)
            recession_change = industry_trend * 100 * years
            recession = np.clip(recession + recession_change, 0.0, 100.0)
            if abs(recession_change) > 2:
                if recession_change > 0:
                    key_factors.append(f"Industry decline trend affecting job security")
                else:
                    key_factors.append(f"Growing industry reducing recession risk")
            
            # Apply age progression for age discrimination
            # Age increases, so risk may increase
            future_age = user_profile.age + int(years)
            if future_age > 55 and user_profile.age <= 55:
                age_increase = (future_age - 55) * 2.0  # 2% per year after 55
                age_disc = min(100.0, age_disc + age_increase)
                key_factors.append(f"Age progression (will be {future_age}) increasing discrimination risk")
            elif future_age > 55:
                age_increase = years * 2.0
                age_disc = min(100.0, age_disc + age_increase)
            
            # Apply skill decay or learning benefit
            if assumes_learning:
                skill_benefit = abs(self.LEARNING_BENEFIT_RATE) * 100 * years
                overall = max(0.0, overall - skill_benefit)
                automation = max(0.0, automation - skill_benefit * 0.5)
                key_factors.append("Continuous learning reducing overall risk")
            else:
                skill_decay = self.SKILL_DECAY_RATE * 100 * years
                overall = min(100.0, overall + skill_decay)
                key_factors.append("Skill decay without continuous learning")
            
            # Ensure overall risk reflects component changes
            # Weight the components
            weighted_overall = (
                automation * 0.35 +
                recession * 0.35 +
                age_disc * 0.15 +
                overall * 0.15
            )
            overall = np.clip(weighted_overall, 0.0, 100.0)
            
            predictions.append(TimeHorizonPrediction(
                horizon=horizon_name,
                overall_risk=round(overall, 1),
                automation_risk=round(automation, 1),
                recession_risk=round(recession, 1),
                age_discrimination_risk=round(age_disc, 1),
                key_factors=key_factors[:3],  # Top 3 factors
            ))
        
        return predictions
