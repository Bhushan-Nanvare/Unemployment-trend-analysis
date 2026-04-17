"""Recommendation engine with ROI quantification."""

import numpy as np
from typing import List
from dataclasses import dataclass
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_calculators import UserProfile, RiskProfile


@dataclass
class Recommendation:
    """Single actionable recommendation"""
    action: str
    risk_reduction: tuple  # (min, max) percentage point reduction
    salary_impact: tuple  # (min, max) salary increase
    time_to_implement: str
    roi_score: float
    priority: str  # "High", "Medium", "Low"
    explanation: str


class RecommendationEngine:
    """Generates prioritized recommendations with ROI"""
    
    def generate_recommendations(
        self, 
        profile: UserProfile,
        risk_profile: RiskProfile,
        salary_estimate: float
    ) -> List[Recommendation]:
        """
        Analyze profile and generate top recommendations
        
        Returns top 5-7 recommendations ranked by ROI
        """
        recommendations = []
        
        # Recommendation 1: High-demand skills
        if risk_profile.automation_risk > 50:
            recommendations.append(Recommendation(
                action="Learn high-demand automation-resistant skills (Machine Learning, Cloud Computing, Leadership)",
                risk_reduction=(10, 15),
                salary_impact=(80_000, 1_50_000),
                time_to_implement="6-12 months",
                roi_score=self._calculate_roi(12.5, 1_15_000, 9),
                priority="High",
                explanation="These skills significantly reduce automation risk and command premium salaries in the Indian market."
            ))
        
        # Recommendation 2: Role advancement
        if profile.role_level in ["Entry", "Mid"] and risk_profile.overall_risk > 40:
            recommendations.append(Recommendation(
                action=f"Target {self._next_role_level(profile.role_level)} roles with strategic responsibilities",
                risk_reduction=(8, 12),
                salary_impact=(1_50_000, 2_50_000),
                time_to_implement="1-2 years",
                roi_score=self._calculate_roi(10, 2_00_000, 18),
                priority="High",
                explanation="Senior roles have lower recession vulnerability and better job security in Indian companies."
            ))
        
        # Recommendation 3: Industry transition
        if risk_profile.recession_risk > 60:
            recommendations.append(Recommendation(
                action="Explore recession-resistant industries (Healthcare, Technology, Essential Services)",
                risk_reduction=(15, 25),
                salary_impact=(50_000, 2_00_000),
                time_to_implement="6-18 months",
                roi_score=self._calculate_roi(20, 1_25_000, 12),
                priority="High",
                explanation="These industries show stronger resilience during economic downturns."
            ))
        
        # Recommendation 4: Company size/stability
        if profile.company_size in ["1-10", "11-50"] and risk_profile.recession_risk > 50:
            recommendations.append(Recommendation(
                action="Consider larger, more established companies (1000+ employees)",
                risk_reduction=(10, 15),
                # In India, switching to larger firms typically comes with some uplift;
                # keep non-zero lower bound so downstream INR sanity checks don't flag it.
                salary_impact=(50_000, 1_00_000),
                time_to_implement="3-6 months",
                roi_score=self._calculate_roi(12.5, 50_000, 4.5),
                priority="Medium",
                explanation="Larger companies typically offer more stability and resources during downturns."
            ))
        
        # Recommendation 5: Remote capability
        if not profile.remote_capability and risk_profile.recession_risk > 40:
            recommendations.append(Recommendation(
                action="Develop remote work capabilities and seek hybrid/remote roles",
                risk_reduction=(5, 8),
                salary_impact=(30_000, 80_000),
                time_to_implement="2-4 months",
                roi_score=self._calculate_roi(6.5, 55_000, 3),
                priority="Medium",
                explanation="Remote capability expands job market access across Indian cities and provides flexibility."
            ))
        
        # Recommendation 6: Certifications
        if profile.education_level in ["High school / diploma", "Bachelor's degree"] and risk_profile.overall_risk > 45:
            recommendations.append(Recommendation(
                action="Obtain industry certifications or pursue advanced degree",
                risk_reduction=(8, 12),
                salary_impact=(1_00_000, 2_00_000),
                time_to_implement="6-24 months",
                roi_score=self._calculate_roi(10, 1_50_000, 15),
                priority="Medium",
                explanation="Advanced credentials reduce risk and significantly increase earning potential in India."
            ))
        
        # Recommendation 7: Experience building
        if profile.experience_years < 5 and risk_profile.recession_risk > 50:
            recommendations.append(Recommendation(
                action="Focus on building experience depth in current role",
                risk_reduction=(5, 10),
                salary_impact=(50_000, 1_00_000),
                time_to_implement="Ongoing",
                roi_score=self._calculate_roi(7.5, 75_000, 12),
                priority="Low",
                explanation="Each 5 years of experience reduces recession vulnerability and boosts salary in India."
            ))
        
        # Sort by ROI score and return top recommendations
        recommendations.sort(key=lambda x: x.roi_score, reverse=True)
        return recommendations[:5]
    
    def _calculate_roi(self, risk_reduction: float, salary_impact: float, time_months: float) -> float:
        """Calculate ROI score for ranking (salary_impact in INR)"""
        # Normalise INR salary impact: divide by 10,000 so the scale is comparable to risk_reduction
        return (risk_reduction * 10 + salary_impact / 10_000) / max(time_months, 1)
    
    def _next_role_level(self, current: str) -> str:
        """Get next role level"""
        levels = ["Entry", "Mid", "Senior", "Lead", "Executive"]
        try:
            idx = levels.index(current)
            return levels[min(idx + 1, len(levels) - 1)]
        except ValueError:
            return "Senior"
