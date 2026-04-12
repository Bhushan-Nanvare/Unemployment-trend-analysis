"""Age discrimination risk calculator based on age, industry, and role level."""

import numpy as np
from typing import Dict, List
from . import UserProfile, AgeDiscriminationRiskResult


class AgeDiscriminationRiskCalculator:
    """Calculates age discrimination risk based on age, industry, role level"""
    
    # Industry age diversity scores (0-1, higher = better diversity/less discrimination)
    INDUSTRY_AGE_DIVERSITY = {
        "Technology / software": 0.45,  # Known for youth bias
        "Healthcare / biotech": 0.75,
        "Financial services / fintech": 0.60,
        "Education / edtech": 0.70,
        "Manufacturing (traditional)": 0.65,
        "Retail / e-commerce ops": 0.55,
        "Hospitality / tourism": 0.60,
        "Renewable energy / climate": 0.58,
        "Other / not listed": 0.60,
    }
    
    # Role level protection (senior roles less affected)
    ROLE_LEVEL_PROTECTION = {
        "Entry": 0.0,
        "Mid": 0.10,
        "Senior": 0.20,
        "Lead": 0.25,
        "Executive": 0.30,
    }
    
    def calculate(self, profile: UserProfile) -> AgeDiscriminationRiskResult:
        """
        Calculate age discrimination risk score (0-100)
        
        Algorithm:
        1. Compute base risk from age curve (U-shaped, minimum at 30-50)
        2. Adjust for industry age diversity practices
        3. Apply role level protection
        4. Consider experience as mitigating factor
        5. Normalize to 0-100 scale
        """
        # Step 1: Base risk from age curve
        base_risk = self._age_risk_curve(profile.age) * 100.0
        
        # Step 2: Adjust for industry age diversity
        # Lower diversity score = higher discrimination risk
        industry_diversity = self.INDUSTRY_AGE_DIVERSITY.get(profile.industry, 0.60)
        # Convert diversity to risk multiplier (low diversity = high multiplier)
        diversity_multiplier = 2.0 - industry_diversity
        base_risk = base_risk * diversity_multiplier
        
        # Step 3: Apply role level protection
        role_protection = self.ROLE_LEVEL_PROTECTION.get(profile.role_level, 0.10) * 100
        
        # Step 4: Experience as mitigating factor
        # More experience reduces age discrimination risk (shows value)
        # Each 5 years of experience reduces risk by 3%, max 15%
        experience_benefit = min(profile.experience_years / 5.0 * 3.0, 15.0)
        
        # Step 5: Apply adjustments
        final_risk = base_risk - role_protection - experience_benefit
        
        # Normalize to 0-100
        final_risk = np.clip(final_risk, 0.0, 100.0)
        
        # Determine risk level
        risk_level = self._get_risk_level(final_risk)
        
        # Build contributing factors
        contributing_factors = {
            "age_factor": round(self._age_risk_curve(profile.age) * 100, 1),
            "industry_diversity_adjustment": round((diversity_multiplier - 1.0) * base_risk / diversity_multiplier, 1),
            "role_level_protection": round(-role_protection, 1),
            "experience_benefit": round(-experience_benefit, 1),
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(final_risk, profile)
        
        return AgeDiscriminationRiskResult(
            score=round(final_risk, 1),
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommendations=recommendations,
        )
    
    def _age_risk_curve(self, age: int) -> float:
        """
        U-shaped curve with minimum at 35-45
        Returns base risk 0-1
        """
        if 30 <= age <= 50:
            # Minimal risk in prime working years
            # Slight dip at 35-45
            if 35 <= age <= 45:
                return 0.08
            else:
                return 0.12
        elif age < 30:
            # Slight increase for very young (perceived inexperience)
            return 0.15 + (30 - age) * 0.015
        else:  # age > 50
            # Increases with age after 50
            return 0.15 + (age - 50) * 0.020
    
    def _get_risk_level(self, score: float) -> str:
        """Map risk score to level"""
        if score >= 62.0:
            return "High"
        elif score >= 35.0:
            return "Medium"
        else:
            return "Low"
    
    def _generate_recommendations(self, risk_score: float, profile: UserProfile) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if risk_score >= 50:
            # High age discrimination risk
            if profile.role_level in ["Entry", "Mid"]:
                recommendations.append(
                    "Target senior or leadership roles where experience is highly valued "
                    "and age discrimination is less prevalent."
                )
            
            industry_diversity = self.INDUSTRY_AGE_DIVERSITY.get(profile.industry, 0.60)
            if industry_diversity < 0.55:
                recommendations.append(
                    "Consider industries with better age diversity like healthcare, "
                    "education, or financial services."
                )
            
            if profile.age > 50:
                recommendations.append(
                    "Emphasize your extensive experience and proven track record. "
                    "Consider consulting or advisory roles that value seasoned expertise."
                )
            
            recommendations.append(
                "Stay current with modern skills and technologies to counter age-related "
                "stereotypes about adaptability."
            )
            
            if profile.age < 30:
                recommendations.append(
                    "Build credibility through certifications, projects, and demonstrated "
                    "results to overcome youth-related perception challenges."
                )
        else:
            if 30 <= profile.age <= 50:
                recommendations.append(
                    "You're in the optimal age range for most roles. Continue building "
                    "experience and skills to maintain your competitive position."
                )
            else:
                recommendations.append(
                    "Your age discrimination risk is manageable. Focus on demonstrating "
                    "value through results and staying current with industry trends."
                )
        
        return recommendations[:4]
