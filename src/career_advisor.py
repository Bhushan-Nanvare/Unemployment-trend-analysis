"""
career_advisor.py
Rule-based AI Career & Skill Advisor with Dynamic Skill Detection.

REFACTORED: 2026-04-13 (Version 4.0.0)
- Removed predefined skill lists
- Integrated dynamic skill detection from real job postings
- Automatically evolving skill recommendations

Fix: Thresholds for "growth" vs "risk" classification now scale dynamically
with shock_intensity so that a severe crisis produces appropriately pessimistic
advice rather than falsely optimistic sector labels.
"""
import pandas as pd
from src.dynamic_skill_detector import get_dynamic_trending_skills


class CareerAdvisor:

    # NO MORE PREDEFINED SECTOR_SKILLS
    # Skills are now dynamically detected from real job market data

    @staticmethod
    def _dynamic_thresholds(shock_intensity: float) -> dict:
        """
        As shock intensifies, the bar for being a "growth" sector rises
        and the bar for being "at risk" falls — matching economic reality.

        shock_intensity:  0.0 → 0.2   low shock   → generous thresholds
                          0.2 → 0.4   moderate    → slightly tightened
                          0.4+        severe/crisis → strict thresholds
        """
        if shock_intensity <= 0.2:
            return {"growth_resilience": 55, "growth_stress": 50, "risk_stress": 65}
        elif shock_intensity <= 0.4:
            return {"growth_resilience": 60, "growth_stress": 45, "risk_stress": 55}
        else:
            return {"growth_resilience": 70, "growth_stress": 35, "risk_stress": 45}

    @staticmethod
    def generate_advice(sector_impact_df: pd.DataFrame, shock_intensity: float = 0.0) -> dict:
        """
        Generates career advice based on sector stress and resilience.
        shock_intensity is used to set dynamic classification thresholds.
        
        REFACTORED (v4.0.0): Now uses dynamic skill detection from real job postings.
        NO predefined skill lists - automatically discovers trending skills.
        """
        thresholds = CareerAdvisor._dynamic_thresholds(shock_intensity)
        g_res = thresholds["growth_resilience"]
        g_str = thresholds["growth_stress"]
        r_str = thresholds["risk_stress"]

        sectors = sector_impact_df.to_dict(orient="records")

        advice = {
            "growth_sectors": [],
            "risk_sectors": [],
            "recommended_skills": [],
            "skill_demand_data": {},  # Dynamic skill detection data
            "upskilling_pathways": [],
            "shock_severity": (
                "Low" if shock_intensity <= 0.2 else
                "Moderate" if shock_intensity <= 0.4 else
                "Severe"
            ),
        }

        # Identify growth and risk sectors
        for s in sectors:
            name = s["Sector"]
            resilience = s["Resilience_Score"]
            stress = s["Stress_Score"]

            if resilience > g_res and stress < g_str:
                advice["growth_sectors"].append(name)
            elif stress > r_str:
                advice["risk_sectors"].append(name)

        # Get dynamically detected trending skills from job market
        # NO predefined lists - automatically discovers what's trending
        skill_demand = get_dynamic_trending_skills(top_n=15)
        advice["skill_demand_data"] = skill_demand
        
        # Extract top skills by demand score
        if skill_demand.get("skills"):
            advice["recommended_skills"] = [
                s["name"] for s in skill_demand["skills"]
            ]
        else:
            advice["recommended_skills"] = []

        narrative = []
        severity = advice["shock_severity"]
        if advice["growth_sectors"]:
            narrative.append(
                f"Under {severity.lower()} shock conditions, strongest growth potential remains in: "
                f"{', '.join(advice['growth_sectors'])}."
            )
        else:
            narrative.append(
                f"Under {severity.lower()} economic shock, no sector currently meets the growth threshold. "
                "Focus on resilience-building and transferable skills."
            )

        if advice["risk_sectors"]:
            narrative.append(
                f"High stress observed in: {', '.join(advice['risk_sectors'])}. "
                "Professionals in these areas should prioritize upskilling and pivot planning."
            )

        advice["narrative"] = " ".join(narrative)
        return advice
