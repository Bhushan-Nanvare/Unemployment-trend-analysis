"""Recession vulnerability calculator based on industry, role, company, and experience."""

import numpy as np
from typing import Dict, List
from . import UserProfile, RecessionRiskResult


class RecessionRiskCalculator:
    """Calculates recession vulnerability based on industry, role, company, experience"""
    
    # Industry recession vulnerability (0-1 scale, higher = more vulnerable)
    INDUSTRY_VULNERABILITY = {
        "Hospitality / tourism": 0.90,
        "Retail / e-commerce ops": 0.75,
        "Manufacturing (traditional)": 0.70,
        "Technology / software": 0.50,
        "Financial services / fintech": 0.55,
        "Healthcare / biotech": 0.25,
        "Education / edtech": 0.40,
        "Renewable energy / climate": 0.45,
        "Other / not listed": 0.60,
    }
    
    # Company size risk multipliers (smaller = higher risk)
    COMPANY_SIZE_MULTIPLIERS = {
        "1-10": 1.35,
        "11-50": 1.25,
        "51-200": 1.10,
        "201-1000": 1.00,
        "1001-5000": 0.90,
        "5000+": 0.85,
    }
    
    # Role level protection factors (higher roles more protected)
    ROLE_LEVEL_PROTECTION = {
        "Entry": 0.0,
        "Mid": 0.10,
        "Senior": 0.20,
        "Lead": 0.25,
        "Executive": 0.30,
    }
    
    def calculate(self, profile: UserProfile) -> RecessionRiskResult:
        """
        Calculate recession vulnerability score (0-100)
        
        Algorithm:
        1. Start with industry vulnerability baseline
        2. Apply company size multiplier
        3. Reduce risk based on experience (5% per 5 years, max 20%)
        4. Adjust for role level (senior roles more protected)
        5. Consider performance rating (high performers more protected)
        6. Normalize to 0-100 scale
        """
        # Step 1: Base vulnerability from industry (convert 0-1 to 0-100)
        industry_vuln = self.INDUSTRY_VULNERABILITY.get(profile.industry, 0.60)
        base_risk = industry_vuln * 100.0
        
        # Step 2: Apply company size multiplier
        company_multiplier = self.COMPANY_SIZE_MULTIPLIERS.get(profile.company_size, 1.00)
        base_risk = base_risk * company_multiplier
        
        # Step 3: Experience protection (5% reduction per 5 years, max 20%)
        experience_protection = min(profile.experience_years / 5.0 * 5.0, 20.0)
        
        # Step 4: Role level protection
        role_protection = self.ROLE_LEVEL_PROTECTION.get(profile.role_level, 0.10) * 100
        
        # Step 5: Performance rating protection (high performers less vulnerable)
        # Rating 1-5, where 5 is top performer
        # Each point above 3 reduces risk by 5%, each point below increases by 5%
        performance_adjustment = (profile.performance_rating - 3) * -5.0
        
        # Step 6: Apply all adjustments
        final_risk = base_risk - experience_protection - role_protection + performance_adjustment
        
        # Remote capability provides some protection (5% reduction)
        if profile.remote_capability:
            final_risk -= 5.0
        
        # Normalize to 0-100
        final_risk = np.clip(final_risk, 0.0, 100.0)
        
        # Determine risk level
        risk_level = self._get_risk_level(final_risk)
        
        # Build contributing factors
        contributing_factors = {
            "industry_vulnerability": round(industry_vuln * 100, 1),
            "company_size_factor": round((company_multiplier - 1.0) * base_risk / company_multiplier, 1),
            "experience_protection": round(-experience_protection, 1),
            "role_level_protection": round(-role_protection, 1),
            "performance_adjustment": round(performance_adjustment, 1),
            "remote_capability_benefit": round(-5.0 if profile.remote_capability else 0.0, 1),
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(final_risk, profile)
        
        return RecessionRiskResult(
            score=round(final_risk, 1),
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommendations=recommendations,
        )
    
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
            # High recession risk
            if profile.experience_years < 10:
                recommendations.append(
                    "Build experience depth (currently {profile.experience_years} years). "
                    "Each 5 years of experience reduces recession vulnerability by 5%."
                )
            
            company_multiplier = self.COMPANY_SIZE_MULTIPLIERS.get(profile.company_size, 1.00)
            if company_multiplier > 1.15:
                recommendations.append(
                    "Consider larger, more established companies for greater stability "
                    "during economic downturns."
                )
            
            industry_vuln = self.INDUSTRY_VULNERABILITY.get(profile.industry, 0.60)
            if industry_vuln > 0.65:
                recommendations.append(
                    "Explore recession-resistant industries like healthcare, education, "
                    "or essential services."
                )
            
            if profile.role_level in ["Entry", "Mid"]:
                recommendations.append(
                    "Aim for senior roles with more strategic responsibilities, "
                    "which are typically more protected during layoffs."
                )
            
            if not profile.remote_capability:
                recommendations.append(
                    "Develop remote work capabilities to access broader job markets "
                    "and increase flexibility."
                )
        else:
            recommendations.append(
                "Your recession vulnerability is relatively low. Maintain your "
                "experience and consider building an emergency fund."
            )
        
        return recommendations[:4]
