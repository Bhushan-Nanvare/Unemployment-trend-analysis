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
                salary_impact=(8000, 15000),
                time_to_implement="6-12 months",
                roi_score=self._calculate_roi(12.5, 11500, 9),
                priority="High",
                explanation="These skills significantly reduce automation risk and command premium salaries in the market."
            ))
        
        # Recommendation 2: Role advancement
        if profile.role_level in ["Entry", "Mid"] and risk_profile.overall_risk > 40:
            recommendations.append(Recommendation(
                action=f"Target {self._next_role_level(profile.role_level)} roles with strategic responsibilities",
                risk_reduction=(8, 12),
                salary_impact=(15000, 25000),
                time_to_implement="1-2 years",
                roi_score=self._calculate_roi(10, 20000, 18),
                priority="High",
                explanation="Senior roles have lower recession vulnerability and better job security."
            ))
        
        # Recommendation 3: Industry transition
        if risk_profile.recession_risk > 60:
            recommendations.append(Recommendation(
                action="Explore recession-resistant industries (Healthcare, Technology, Essential Services)",
                risk_reduction=(15, 25),
                salary_impact=(5000, 20000),
                time_to_implement="6-18 months",
                roi_score=self._calculate_roi(20, 12500, 12),
                priority="High",
                explanation="These industries show stronger resilience during economic downturns."
            ))
        
        # Recommendation 4: Company size/stability
        if profile.company_size in ["1-10", "11-50"] and risk_profile.recession_risk > 50:
            recommendations.append(Recommendation(
                action="Consider larger, more established companies (1000+ employees)",
                risk_reduction=(10, 15),
                salary_impact=(0, 10000),
                time_to_implement="3-6 months",
                roi_score=self._calculate_roi(12.5, 5000, 4.5),
                priority="Medium",
                explanation="Larger companies typically offer more stability and resources during downturns."
            ))
        
        # Recommendation 5: Remote capability
        if not profile.remote_capability and risk_profile.recession_risk > 40:
            recommendations.append(Recommendation(
                action="Develop remote work capabilities and seek hybrid/remote roles",
                risk_reduction=(5, 8),
                salary_impact=(3000, 8000),
                time_to_implement="2-4 months",
                roi_score=self._calculate_roi(6.5, 5500, 3),
                priority="Medium",
                explanation="Remote capability expands job market access and provides flexibility."
            ))
        
        # Recommendation 6: Certifications
        if profile.education_level in ["High school / diploma", "Bachelor's degree"] and risk_profile.overall_risk > 45:
            recommendations.append(Recommendation(
                action="Obtain industry certifications or pursue advanced degree",
                risk_reduction=(8, 12),
                salary_impact=(10000, 20000),
                time_to_implement="6-24 months",
                roi_score=self._calculate_roi(10, 15000, 15),
                priority="Medium",
                explanation="Advanced credentials reduce risk and increase earning potential."
            ))
        
        # Recommendation 7: Experience building
        if profile.experience_years < 5 and risk_profile.recession_risk > 50:
            recommendations.append(Recommendation(
                action="Focus on building experience depth in current role",
                risk_reduction=(5, 10),
                salary_impact=(5000, 10000),
                time_to_implement="Ongoing",
                roi_score=self._calculate_roi(7.5, 7500, 12),
                priority="Low",
                explanation="Each 5 years of experience reduces recession vulnerability by 5%."
            ))
        
        # Sort by ROI score and return top recommendations
        recommendations.sort(key=lambda x: x.roi_score, reverse=True)
        return recommendations[:5]
    
    def _calculate_roi(self, risk_reduction: float, salary_impact: float, time_months: float) -> float:
        """Calculate ROI score for ranking"""
        # ROI = (risk_reduction * 10 + salary_impact / 1000) / time_months
        return (risk_reduction * 10 + salary_impact / 1000) / max(time_months, 1)
    
    def _next_role_level(self, current: str) -> str:
        """Get next role level"""
        levels = ["Entry", "Mid", "Senior", "Lead", "Executive"]
        try:
            idx = levels.index(current)
            return levels[min(idx + 1, len(levels) - 1)]
        except ValueError:
            return "Senior"
