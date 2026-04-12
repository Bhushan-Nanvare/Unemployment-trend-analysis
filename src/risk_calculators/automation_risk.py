"""Automation risk calculator based on skills, industry, and role level."""

import numpy as np
from typing import Dict, List
from . import UserProfile, AutomationRiskResult


class AutomationRiskCalculator:
    """Calculates automation risk based on skills, industry, and role"""
    
    # Automation susceptibility by industry (0-1 scale, higher = more susceptible)
    INDUSTRY_AUTOMATION_RATES = {
        "Manufacturing (traditional)": 0.85,
        "Retail / e-commerce ops": 0.75,
        "Financial services / fintech": 0.65,
        "Technology / software": 0.45,
        "Healthcare / biotech": 0.35,
        "Education / edtech": 0.40,
        "Renewable energy / climate": 0.50,
        "Hospitality / tourism": 0.70,
        "Other / not listed": 0.60,
    }
    
    # Role-level automation resistance (0-1 scale, higher = more resistant)
    ROLE_LEVEL_RESISTANCE = {
        "Entry": 0.2,
        "Mid": 0.4,
        "Senior": 0.6,
        "Lead": 0.75,
        "Executive": 0.85,
    }
    
    # Skills that reduce automation risk (skill -> reduction factor)
    AUTOMATION_RESISTANT_SKILLS = {
        "machine learning": 0.25,
        "deep learning": 0.24,
        "artificial intelligence": 0.23,
        "leadership": 0.20,
        "strategic planning": 0.22,
        "creative design": 0.23,
        "complex problem solving": 0.21,
        "communication": 0.18,
        "project management": 0.19,
        "product management": 0.20,
        "data science": 0.22,
        "cybersecurity": 0.21,
        "cloud computing": 0.18,
        "devops": 0.17,
        "innovation": 0.20,
        "research": 0.19,
        "consulting": 0.18,
        "negotiation": 0.17,
    }
    
    # Skills that increase automation risk
    AUTOMATION_VULNERABLE_SKILLS = {
        "data entry": 0.30,
        "typing": 0.25,
        "filing": 0.28,
        "manual testing": 0.20,
        "basic computer": 0.22,
        "microsoft word": 0.18,
        "powerpoint": 0.15,
        "excel": 0.12,  # Basic Excel usage
        "fax": 0.25,
        "copying": 0.23,
    }
    
    def calculate(self, profile: UserProfile) -> AutomationRiskResult:
        """
        Calculate automation risk score (0-100)
        
        Algorithm:
        1. Start with base risk from industry automation rate
        2. Adjust for role level (higher levels more resistant)
        3. Reduce risk for automation-resistant skills
        4. Increase risk for automation-vulnerable skills
        5. Normalize to 0-100 scale
        """
        # Step 1: Base risk from industry (convert 0-1 to 0-100)
        industry_rate = self.INDUSTRY_AUTOMATION_RATES.get(profile.industry, 0.60)
        base_risk = industry_rate * 100.0
        
        # Step 2: Adjust for role level resistance
        role_resistance = self.ROLE_LEVEL_RESISTANCE.get(profile.role_level, 0.4)
        # Higher role levels reduce risk
        base_risk = base_risk * (1.0 - role_resistance * 0.5)
        
        # Step 3: Analyze skills
        skills_lower = [s.lower() for s in profile.skills]
        skills_blob = " ".join(skills_lower)
        
        # Count resistant skills
        resistant_reduction = 0.0
        matched_resistant = []
        for skill, reduction in self.AUTOMATION_RESISTANT_SKILLS.items():
            if skill in skills_blob:
                resistant_reduction += reduction
                matched_resistant.append(skill)
        
        # Cap resistant skills benefit at 40 percentage points
        resistant_reduction = min(resistant_reduction * 100, 40.0)
        
        # Count vulnerable skills
        vulnerable_increase = 0.0
        matched_vulnerable = []
        for skill, increase in self.AUTOMATION_VULNERABLE_SKILLS.items():
            if skill in skills_blob:
                vulnerable_increase += increase
                matched_vulnerable.append(skill)
        
        # Cap vulnerable skills penalty at 30 percentage points
        vulnerable_increase = min(vulnerable_increase * 100, 30.0)
        
        # Step 4: Apply skill adjustments
        final_risk = base_risk - resistant_reduction + vulnerable_increase
        
        # Step 5: Normalize to 0-100
        final_risk = np.clip(final_risk, 0.0, 100.0)
        
        # Determine risk level
        risk_level = self._get_risk_level(final_risk)
        
        # Build contributing factors
        contributing_factors = {
            "industry_automation_rate": round(industry_rate * 100, 1),
            "role_level_protection": round(-role_resistance * base_risk * 0.5, 1),
            "resistant_skills_benefit": round(-resistant_reduction, 1),
            "vulnerable_skills_penalty": round(vulnerable_increase, 1),
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            final_risk, matched_resistant, matched_vulnerable, profile
        )
        
        return AutomationRiskResult(
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
    
    def _generate_recommendations(
        self,
        risk_score: float,
        matched_resistant: List[str],
        matched_vulnerable: List[str],
        profile: UserProfile,
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if risk_score >= 50:
            if len(matched_resistant) < 2:
                recommendations.append(
                    "Learn automation-resistant skills like machine learning, "
                    "leadership, or strategic planning to reduce automation risk."
                )
            
            if matched_vulnerable:
                recommendations.append(
                    f"Consider transitioning away from automation-vulnerable skills "
                    f"like {', '.join(matched_vulnerable[:2])}."
                )
            
            if profile.role_level in ["Entry", "Mid"]:
                recommendations.append(
                    "Aim for senior roles that involve more strategic decision-making "
                    "and less routine tasks."
                )
            
            industry_rate = self.INDUSTRY_AUTOMATION_RATES.get(profile.industry, 0.60)
            if industry_rate > 0.65:
                recommendations.append(
                    "Consider industries with lower automation rates like healthcare, "
                    "education, or technology services."
                )
        else:
            recommendations.append(
                "Your automation risk is relatively low. Continue developing "
                "skills in creative, strategic, and interpersonal areas."
            )
        
        return recommendations[:4]
