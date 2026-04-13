"""
ai_insights_engine.py

AI EXPLANATION ENGINE
======================

Generates insights using DATA + EVIDENCE-BASED INTERPRETATION.

Author: System Refactoring
Date: 2026-04-13
Version: 6.0.0 (AI Insights)

STRICT RULES:
- Use ONLY available system data
- NO absolute claims
- NO assumed external causes
- Cautious reasoning with "suggests", "indicates", "may reflect"
- Data-supported conclusions only
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


# ═══════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Insight:
    """Single insight with data, pattern, and interpretation."""
    category: str  # skill_trends, sector_analysis, unemployment_trends, market_dynamics
    title: str
    data_observation: str  # What is observed in the data
    pattern_identified: str  # Comparison or trend identification
    interpretation: str  # Cautious reasoning
    confidence: str  # high, medium, low
    supporting_data: Dict  # Raw data supporting this insight
    timestamp: datetime


# ═══════════════════════════════════════════════════════════════════════════
# AI INSIGHTS ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class AIInsightsEngine:
    """
    Generates data-driven insights with evidence-based interpretation.
    
    Uses ONLY available system data:
    - Skill demand trends (from dynamic detector)
    - Sector stress/resilience scores
    - Unemployment trends
    - Job market data
    """
    
    def __init__(self):
        pass
    
    # ═══════════════════════════════════════════════════════════════════════
    # SKILL TREND INSIGHTS
    # ═══════════════════════════════════════════════════════════════════════
    
    def analyze_skill_trends(self, skill_demand_data: Dict) -> List[Insight]:
        """
        Generate insights from skill demand data.
        
        SKILL RULE:
        - Explain demand differences
        - Identify growth patterns
        - Link ONLY to observed job data
        
        Args:
            skill_demand_data: Data from dynamic skill detector
        
        Returns:
            List of Insight objects
        """
        insights = []
        
        if not skill_demand_data or not skill_demand_data.get("skills"):
            return insights
        
        skills = skill_demand_data["skills"]
        
        # Insight 1: Top Skill Dominance
        if len(skills) >= 3:
            top_skill = skills[0]
            second_skill = skills[1]
            third_skill = skills[2]
            
            demand_gap = top_skill["demand"] - second_skill["demand"]
            
            if demand_gap > 0.15:  # Significant gap
                insights.append(Insight(
                    category="skill_trends",
                    title="Dominant Skill Demand Pattern",
                    data_observation=f"{top_skill['name']} shows {top_skill['demand']:.1%} demand score, "
                                   f"compared to {second_skill['name']} at {second_skill['demand']:.1%}.",
                    pattern_identified=f"A {demand_gap:.1%} gap exists between the top two skills, "
                                     f"with {top_skill['name']} mentioned in {top_skill['job_count']} job postings.",
                    interpretation=f"This suggests {top_skill['name']} may be experiencing particularly high "
                                 f"market demand relative to other skills. The frequency of mentions "
                                 f"({top_skill['frequency']} times across {skill_demand_data.get('jobs_analyzed', 0)} jobs) "
                                 f"indicates widespread requirement across multiple roles.",
                    confidence="high",
                    supporting_data={
                        "top_skill": top_skill["name"],
                        "top_demand": top_skill["demand"],
                        "second_demand": second_skill["demand"],
                        "gap": demand_gap,
                        "job_count": top_skill["job_count"]
                    },
                    timestamp=datetime.now()
                ))
        
        # Insight 2: Emerging Technology Clusters
        tech_keywords = ["ai", "ml", "machine learning", "deep learning", "nlp", "computer vision"]
        cloud_keywords = ["aws", "azure", "gcp", "cloud", "kubernetes", "docker"]
        data_keywords = ["data", "sql", "analytics", "pandas", "spark"]
        
        tech_skills = [s for s in skills if any(kw in s["name"].lower() for kw in tech_keywords)]
        cloud_skills = [s for s in skills if any(kw in s["name"].lower() for kw in cloud_keywords)]
        data_skills = [s for s in skills if any(kw in s["name"].lower() for kw in data_keywords)]
        
        if len(tech_skills) >= 2:
            avg_tech_demand = sum(s["demand"] for s in tech_skills) / len(tech_skills)
            tech_names = [s["name"] for s in tech_skills[:3]]
            
            insights.append(Insight(
                category="skill_trends",
                title="AI/ML Technology Cluster",
                data_observation=f"{len(tech_skills)} AI/ML-related skills detected in top rankings: "
                               f"{', '.join(tech_names)}.",
                pattern_identified=f"These skills show an average demand score of {avg_tech_demand:.1%}, "
                                 f"appearing across multiple job postings.",
                interpretation="This pattern suggests a sustained market interest in AI/ML capabilities. "
                             "The presence of multiple related skills in top rankings may reflect "
                             "growing integration of AI technologies across various roles and industries.",
                confidence="high",
                supporting_data={
                    "cluster_size": len(tech_skills),
                    "avg_demand": avg_tech_demand,
                    "skills": tech_names
                },
                timestamp=datetime.now()
            ))
        
        # Insight 3: Infrastructure vs Application Skills
        if cloud_skills and data_skills:
            avg_cloud = sum(s["demand"] for s in cloud_skills) / len(cloud_skills)
            avg_data = sum(s["demand"] for s in data_skills) / len(data_skills)
            
            if abs(avg_cloud - avg_data) > 0.1:
                higher_category = "cloud infrastructure" if avg_cloud > avg_data else "data/analytics"
                higher_score = max(avg_cloud, avg_data)
                lower_score = min(avg_cloud, avg_data)
                
                insights.append(Insight(
                    category="skill_trends",
                    title="Infrastructure vs Application Skill Balance",
                    data_observation=f"Cloud infrastructure skills average {avg_cloud:.1%} demand, "
                                   f"while data/analytics skills average {avg_data:.1%} demand.",
                    pattern_identified=f"{higher_category.title()} skills show {(higher_score - lower_score):.1%} "
                                     f"higher demand on average.",
                    interpretation=f"This difference may indicate current market emphasis on {higher_category} "
                                 f"capabilities. However, both categories remain present in job requirements, "
                                 f"suggesting complementary rather than competing demand.",
                    confidence="medium",
                    supporting_data={
                        "cloud_avg": avg_cloud,
                        "data_avg": avg_data,
                        "cloud_count": len(cloud_skills),
                        "data_count": len(data_skills)
                    },
                    timestamp=datetime.now()
                ))
        
        # Insight 4: Salary vs Demand Correlation
        if len(skills) >= 5:
            high_salary_skills = sorted(skills, key=lambda x: x.get("avg_salary", 0), reverse=True)[:3]
            high_demand_skills = skills[:3]
            
            overlap = set(s["name"] for s in high_salary_skills) & set(s["name"] for s in high_demand_skills)
            
            if overlap:
                insights.append(Insight(
                    category="skill_trends",
                    title="High-Value Skill Alignment",
                    data_observation=f"Skills {', '.join(overlap)} appear in both top demand and top salary rankings.",
                    pattern_identified="These skills show both high frequency in job postings and above-average "
                                     "salary offerings.",
                    interpretation="This alignment suggests these skills may represent particularly valuable "
                                 "capabilities in the current market. The combination of high demand and "
                                 "competitive salaries indicates potential supply-demand imbalance.",
                    confidence="high",
                    supporting_data={
                        "overlap_skills": list(overlap),
                        "count": len(overlap)
                    },
                    timestamp=datetime.now()
                ))
        
        return insights
    
    # ═══════════════════════════════════════════════════════════════════════
    # SECTOR ANALYSIS INSIGHTS
    # ═══════════════════════════════════════════════════════════════════════
    
    def analyze_sector_patterns(self, sector_data: pd.DataFrame) -> List[Insight]:
        """
        Generate insights from sector stress/resilience data.
        
        SECTOR RULE:
        - Explain relative stress/resilience
        - Identify comparative exposure
        - DO NOT invent causes
        
        Args:
            sector_data: DataFrame with sector stress and resilience scores
        
        Returns:
            List of Insight objects
        """
        insights = []
        
        if sector_data.empty:
            return insights
        
        # Insight 1: Resilience Leaders
        top_resilient = sector_data.nlargest(3, "Resilience_Score")
        if len(top_resilient) > 0:
            top_sector = top_resilient.iloc[0]
            avg_resilience = sector_data["Resilience_Score"].mean()
            
            insights.append(Insight(
                category="sector_analysis",
                title="High Resilience Sectors",
                data_observation=f"{top_sector['Sector']} shows {top_sector['Resilience_Score']:.1f} resilience score, "
                               f"compared to sector average of {avg_resilience:.1f}.",
                pattern_identified=f"Top 3 resilient sectors: {', '.join(top_resilient['Sector'].tolist())} "
                                 f"with scores above {top_resilient['Resilience_Score'].min():.1f}.",
                interpretation="Higher resilience scores suggest these sectors may have structural characteristics "
                             "that provide relative stability. This could reflect factors such as essential service "
                             "nature, diversified revenue streams, or adaptive capacity, though specific causes "
                             "require further investigation.",
                confidence="medium",
                supporting_data={
                    "top_sector": top_sector['Sector'],
                    "top_score": float(top_sector['Resilience_Score']),
                    "avg_score": float(avg_resilience),
                    "top_3": top_resilient['Sector'].tolist()
                },
                timestamp=datetime.now()
            ))
        
        # Insight 2: Stress Concentration
        high_stress = sector_data[sector_data["Stress_Score"] > 60]
        if len(high_stress) > 0:
            stress_sectors = high_stress['Sector'].tolist()
            avg_stress = high_stress["Stress_Score"].mean()
            
            insights.append(Insight(
                category="sector_analysis",
                title="Elevated Stress Indicators",
                data_observation=f"{len(high_stress)} sectors show stress scores above 60: {', '.join(stress_sectors)}.",
                pattern_identified=f"These sectors average {avg_stress:.1f} stress score, compared to "
                                 f"overall average of {sector_data['Stress_Score'].mean():.1f}.",
                interpretation="Elevated stress scores indicate these sectors may be experiencing relatively higher "
                             "exposure to current economic conditions. The concentration of stress in specific "
                             "sectors suggests differential impact patterns rather than uniform market pressure.",
                confidence="high",
                supporting_data={
                    "high_stress_count": len(high_stress),
                    "sectors": stress_sectors,
                    "avg_stress": float(avg_stress)
                },
                timestamp=datetime.now()
            ))
        
        # Insight 3: Resilience-Stress Balance
        balanced = sector_data[
            (sector_data["Resilience_Score"] > 50) & 
            (sector_data["Stress_Score"] < 50)
        ]
        
        if len(balanced) > 0:
            insights.append(Insight(
                category="sector_analysis",
                title="Balanced Sector Performance",
                data_observation=f"{len(balanced)} sectors show both above-average resilience (>50) "
                               f"and below-average stress (<50).",
                pattern_identified=f"Balanced sectors: {', '.join(balanced['Sector'].tolist())}.",
                interpretation="This balance suggests these sectors may be maintaining relative stability "
                             "in current conditions. The combination of resilience and controlled stress "
                             "indicates potential for sustained performance, though external factors could "
                             "shift this balance.",
                confidence="medium",
                supporting_data={
                    "balanced_count": len(balanced),
                    "sectors": balanced['Sector'].tolist()
                },
                timestamp=datetime.now()
            ))
        
        # Insight 4: Comparative Sector Exposure
        if len(sector_data) >= 5:
            stress_range = sector_data["Stress_Score"].max() - sector_data["Stress_Score"].min()
            
            if stress_range > 30:
                insights.append(Insight(
                    category="sector_analysis",
                    title="Differential Sector Exposure",
                    data_observation=f"Stress scores range from {sector_data['Stress_Score'].min():.1f} "
                                   f"to {sector_data['Stress_Score'].max():.1f}, a spread of {stress_range:.1f} points.",
                    pattern_identified="Wide variation in stress levels across sectors indicates non-uniform impact.",
                    interpretation="This differential exposure pattern suggests sector-specific factors play a "
                                 "significant role in determining stress levels. The wide range may reflect "
                                 "differences in business models, market dependencies, or operational structures, "
                                 "though specific drivers would require detailed sector analysis.",
                    confidence="high",
                    supporting_data={
                        "stress_range": float(stress_range),
                        "min_stress": float(sector_data["Stress_Score"].min()),
                        "max_stress": float(sector_data["Stress_Score"].max())
                    },
                    timestamp=datetime.now()
                ))
        
        return insights
    
    # ═══════════════════════════════════════════════════════════════════════
    # MARKET DYNAMICS INSIGHTS
    # ═══════════════════════════════════════════════════════════════════════
    
    def analyze_market_dynamics(
        self,
        skill_demand_data: Dict,
        sector_data: pd.DataFrame,
        growth_sectors: List[str],
        risk_sectors: List[str]
    ) -> List[Insight]:
        """
        Generate insights from combined market data.
        
        Args:
            skill_demand_data: Skill demand trends
            sector_data: Sector performance data
            growth_sectors: List of growth sectors
            risk_sectors: List of risk sectors
        
        Returns:
            List of Insight objects
        """
        insights = []
        
        # Insight 1: Growth vs Risk Balance
        if growth_sectors and risk_sectors:
            growth_count = len(growth_sectors)
            risk_count = len(risk_sectors)
            total = len(sector_data) if not sector_data.empty else growth_count + risk_count
            
            insights.append(Insight(
                category="market_dynamics",
                title="Market Opportunity Distribution",
                data_observation=f"{growth_count} sectors identified as growth opportunities, "
                               f"{risk_count} sectors showing elevated risk indicators.",
                pattern_identified=f"Growth sectors represent {(growth_count/total)*100:.1f}% of analyzed sectors, "
                                 f"risk sectors represent {(risk_count/total)*100:.1f}%.",
                interpretation="This distribution suggests a mixed market environment with differentiated "
                             "opportunities. The presence of both growth and risk sectors indicates selective "
                             "rather than uniform market conditions, which may favor strategic sector positioning.",
                confidence="high",
                supporting_data={
                    "growth_count": growth_count,
                    "risk_count": risk_count,
                    "growth_pct": (growth_count/total)*100,
                    "risk_pct": (risk_count/total)*100
                },
                timestamp=datetime.now()
            ))
        
        # Insight 2: Skill-Sector Alignment
        if skill_demand_data and not sector_data.empty:
            total_skills = skill_demand_data.get("total_skills", 0)
            jobs_analyzed = skill_demand_data.get("jobs_analyzed", 0)
            
            if total_skills > 0 and jobs_analyzed > 0:
                insights.append(Insight(
                    category="market_dynamics",
                    title="Job Market Skill Diversity",
                    data_observation=f"{total_skills} distinct skills detected across {jobs_analyzed} job postings.",
                    pattern_identified=f"Average of {jobs_analyzed/total_skills:.1f} job mentions per skill detected.",
                    interpretation="This skill diversity suggests a varied job market with multiple capability "
                                 "requirements. Higher diversity may indicate evolving role definitions and "
                                 "cross-functional skill demands, though it could also reflect market fragmentation.",
                    confidence="medium",
                    supporting_data={
                        "total_skills": total_skills,
                        "jobs_analyzed": jobs_analyzed,
                        "avg_mentions": jobs_analyzed/total_skills
                    },
                    timestamp=datetime.now()
                ))
        
        return insights
    
    # ═══════════════════════════════════════════════════════════════════════
    # MAIN ORCHESTRATOR
    # ═══════════════════════════════════════════════════════════════════════
    
    def generate_all_insights(
        self,
        skill_demand_data: Dict,
        sector_data: pd.DataFrame,
        growth_sectors: List[str],
        risk_sectors: List[str]
    ) -> Dict:
        """
        Generate all insights from available data.
        
        Args:
            skill_demand_data: Skill demand trends from dynamic detector
            sector_data: Sector stress/resilience data
            growth_sectors: List of growth sectors
            risk_sectors: List of risk sectors
        
        Returns:
            Dictionary with categorized insights
        """
        all_insights = []
        
        # Generate insights from each category
        all_insights.extend(self.analyze_skill_trends(skill_demand_data))
        all_insights.extend(self.analyze_sector_patterns(sector_data))
        all_insights.extend(self.analyze_market_dynamics(
            skill_demand_data, sector_data, growth_sectors, risk_sectors
        ))
        
        # Categorize insights
        categorized = {
            "skill_trends": [],
            "sector_analysis": [],
            "market_dynamics": [],
            "all": all_insights
        }
        
        for insight in all_insights:
            categorized[insight.category].append({
                "title": insight.title,
                "data": insight.data_observation,
                "pattern": insight.pattern_identified,
                "interpretation": insight.interpretation,
                "confidence": insight.confidence,
                "supporting_data": insight.supporting_data,
                "timestamp": insight.timestamp.isoformat()
            })
        
        return {
            "insights": categorized,
            "total_insights": len(all_insights),
            "timestamp": datetime.now().isoformat(),
            "data_sources": {
                "skills": "Dynamic skill detector (Adzuna API)",
                "sectors": "Sector stress/resilience analysis",
                "market": "Combined market indicators"
            }
        }


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

def generate_ai_insights(
    skill_demand_data: Dict,
    sector_data: pd.DataFrame,
    growth_sectors: List[str],
    risk_sectors: List[str]
) -> Dict:
    """
    Generate AI-powered insights from system data.
    
    Args:
        skill_demand_data: Skill demand trends
        sector_data: Sector performance data
        growth_sectors: List of growth sectors
        risk_sectors: List of risk sectors
    
    Returns:
        Dictionary with categorized insights
    """
    engine = AIInsightsEngine()
    return engine.generate_all_insights(
        skill_demand_data,
        sector_data,
        growth_sectors,
        risk_sectors
    )


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*80)
    print("AI INSIGHTS ENGINE TEST")
    print("="*80)
    print()
    
    # Mock data for testing
    mock_skill_data = {
        "skills": [
            {"name": "Python", "demand": 0.92, "job_count": 312, "frequency": 487, "avg_salary": 1650000},
            {"name": "Machine Learning", "demand": 0.86, "job_count": 187, "frequency": 298, "avg_salary": 1850000},
            {"name": "AWS", "demand": 0.82, "job_count": 245, "frequency": 356, "avg_salary": 1720000},
        ],
        "total_skills": 78,
        "jobs_analyzed": 1250
    }
    
    mock_sector_data = pd.DataFrame({
        "Sector": ["IT", "Healthcare", "Manufacturing"],
        "Resilience_Score": [75, 68, 45],
        "Stress_Score": [35, 42, 68]
    })
    
    result = generate_ai_insights(
        skill_demand_data=mock_skill_data,
        sector_data=mock_sector_data,
        growth_sectors=["IT", "Healthcare"],
        risk_sectors=["Manufacturing"]
    )
    
    print(f"Total Insights Generated: {result['total_insights']}")
    print()
    
    for category, insights in result['insights'].items():
        if category != "all" and insights:
            print(f"\n{category.upper().replace('_', ' ')}:")
            print("-"*80)
            for insight in insights:
                print(f"\n📊 {insight['title']}")
                print(f"   Confidence: {insight['confidence'].upper()}")
                print(f"\n   DATA: {insight['data']}")
                print(f"\n   PATTERN: {insight['pattern']}")
                print(f"\n   INTERPRETATION: {insight['interpretation']}")
