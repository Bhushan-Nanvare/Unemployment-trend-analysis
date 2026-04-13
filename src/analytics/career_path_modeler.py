"""AI-powered career path modeling with market awareness."""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime
import logging

from src.data_providers.career_data_manager import CareerDataManager
from src.risk_calculators import UserProfile

logger = logging.getLogger(__name__)


@dataclass
class CareerTransition:
    """Single career transition"""
    from_role: str
    to_role: str
    success_probability: float  # 0-100
    time_to_transition: str
    required_skills: List[str]
    skill_gaps: List[str]
    market_demand: str  # "very_high", "high", "medium", "low", "very_low"
    salary_change: str  # "+20-30%"
    market_insights: List[str]


@dataclass
class CareerPath:
    """Complete career progression path"""
    path_name: str
    transitions: List[CareerTransition]
    total_timeline: str
    overall_success_probability: float  # 0-100
    total_salary_growth: str
    market_viability: str  # "excellent", "good", "fair", "limited"
    key_milestones: List[str]
    recommended_actions: List[str]


class CareerPathModeler:
    """Generates market-aware career paths"""
    
    def __init__(self):
        self.data_manager = CareerDataManager()
        self.career_graph = self._build_career_graph()
        self.industry_trends = self.data_manager.get_industry_trends()
    
    def generate_paths(self, user_profile: UserProfile) -> List[CareerPath]:
        """
        Generate 3-5 career paths based on user profile and market conditions
        
        Args:
            user_profile: User's current profile
            
        Returns:
            List of career paths sorted by viability
        """
        
        current_role = self._normalize_role(user_profile.role_level)
        possible_roles = self._get_possible_next_roles(current_role, user_profile.industry)
        
        paths = []
        
        for next_role in possible_roles:
            try:
                path = self._generate_single_path(user_profile, current_role, next_role)
                if path:
                    paths.append(path)
            except Exception as e:
                logger.error(f"Error generating path to {next_role}: {e}")
        
        # Sort by overall success probability
        paths.sort(key=lambda p: p.overall_success_probability, reverse=True)
        
        return paths[:5]  # Return top 5 paths
    
    def _generate_single_path(
        self, 
        user_profile: UserProfile, 
        current_role: str, 
        target_role: str
    ) -> Optional[CareerPath]:
        """Generate a single career path"""
        
        # Get market data for target role
        market_data = self.data_manager.get_role_market_data(target_role, "india")
        
        if not market_data.get("success"):
            return None
        
        # Calculate transition details
        transition = self._calculate_transition(
            user_profile, current_role, target_role, market_data
        )
        
        # Create path
        path = CareerPath(
            path_name=f"{current_role} → {target_role}",
            transitions=[transition],
            total_timeline=transition.time_to_transition,
            overall_success_probability=transition.success_probability,
            total_salary_growth=transition.salary_change,
            market_viability=market_data.get("market_health", "stable"),
            key_milestones=self._generate_milestones(transition),
            recommended_actions=self._generate_recommendations(transition, user_profile)
        )
        
        return path
    
    def _calculate_transition(
        self,
        user_profile: UserProfile,
        from_role: str,
        to_role: str,
        market_data: Dict
    ) -> CareerTransition:
        """Calculate detailed transition information"""
        
        # Get role requirements
        role_requirements = self._get_role_requirements(to_role)
        
        # Calculate skill gaps
        current_skills = [s.lower().strip() for s in user_profile.skills]
        required_skills = role_requirements.get("required_skills", [])
        skill_gaps = [skill for skill in required_skills if skill.lower() not in current_skills]
        
        # Calculate success probability
        success_prob = self._calculate_success_probability(
            user_profile, to_role, market_data, skill_gaps
        )
        
        # Estimate timeline
        timeline = self._estimate_timeline(skill_gaps, user_profile.experience_years)
        
        # Calculate salary change
        salary_change = self._estimate_salary_change(from_role, to_role, user_profile.industry)
        
        # Generate market insights
        insights = self._generate_market_insights(to_role, market_data)
        
        return CareerTransition(
            from_role=from_role,
            to_role=to_role,
            success_probability=success_prob,
            time_to_transition=timeline,
            required_skills=required_skills,
            skill_gaps=skill_gaps,
            market_demand=market_data.get("demand_level", "medium"),
            salary_change=salary_change,
            market_insights=insights
        )
    
    def _calculate_success_probability(
        self,
        user_profile: UserProfile,
        target_role: str,
        market_data: Dict,
        skill_gaps: List[str]
    ) -> float:
        """
        Calculate success probability based on multiple factors
        
        Weights:
        - Skill match: 40%
        - Experience: 20%
        - Market demand: 25%
        - Industry health: 15%
        """
        
        # Skill match score (0-100)
        role_requirements = self._get_role_requirements(target_role)
        required_skills = role_requirements.get("required_skills", [])
        
        if not required_skills:
            skill_score = 70  # Default if no requirements defined
        else:
            matched_skills = len(required_skills) - len(skill_gaps)
            skill_score = (matched_skills / len(required_skills)) * 100
        
        # Experience score (0-100)
        min_exp = role_requirements.get("min_experience", 0)
        if user_profile.experience_years >= min_exp:
            exp_score = min(100, 60 + (user_profile.experience_years - min_exp) * 5)
        else:
            exp_score = max(20, 60 - (min_exp - user_profile.experience_years) * 10)
        
        # Market demand score (0-100)
        demand_scores = {
            "very_high": 95,
            "high": 85,
            "medium": 70,
            "low": 50,
            "very_low": 30
        }
        market_score = demand_scores.get(market_data.get("demand_level", "medium"), 70)
        
        # Industry health score (0-100)
        industry_trend = self.industry_trends.get(user_profile.industry, {})
        growth_rate = industry_trend.get("growth", 0)
        
        if growth_rate > 0.10:
            industry_score = 90
        elif growth_rate > 0.05:
            industry_score = 80
        elif growth_rate > 0:
            industry_score = 70
        elif growth_rate > -0.05:
            industry_score = 60
        else:
            industry_score = 40
        
        # Weighted average
        final_score = (
            skill_score * 0.40 +
            exp_score * 0.20 +
            market_score * 0.25 +
            industry_score * 0.15
        )
        
        # Performance rating bonus
        if user_profile.performance_rating >= 4:
            final_score += 5
        elif user_profile.performance_rating <= 2:
            final_score -= 5
        
        return max(10, min(95, final_score))  # Clamp between 10-95%
    
    def _estimate_timeline(self, skill_gaps: List[str], experience: int) -> str:
        """Estimate time to transition based on skill gaps and experience"""
        
        if not skill_gaps:
            if experience >= 5:
                return "6-12 months"
            else:
                return "12-18 months"
        
        # Estimate learning time for skills
        skill_learning_time = {
            "leadership": 6,
            "management": 6,
            "system design": 4,
            "architecture": 6,
            "mentoring": 3,
            "project management": 4,
            "strategic planning": 8,
            "team building": 4,
            "communication": 3,
            "technical writing": 2,
        }
        
        total_months = sum(skill_learning_time.get(skill, 3) for skill in skill_gaps)
        
        # Adjust for experience (experienced people learn faster)
        if experience >= 8:
            total_months *= 0.7
        elif experience >= 5:
            total_months *= 0.8
        elif experience >= 3:
            total_months *= 0.9
        
        total_months = max(6, total_months)  # Minimum 6 months
        
        if total_months <= 12:
            return f"{int(total_months)}-{int(total_months + 6)} months"
        else:
            years = total_months / 12
            return f"{years:.1f}-{years + 0.5:.1f} years"
    
    def _estimate_salary_change(self, from_role: str, to_role: str, industry: str) -> str:
        """Estimate salary change for transition"""
        
        # Role level salary multipliers
        role_multipliers = {
            "entry": 1.0,
            "mid": 1.4,
            "senior": 1.9,
            "lead": 2.5,
            "executive": 3.5,
            "manager": 2.8,
            "director": 4.0,
            "principal": 3.2,
            "staff": 2.7
        }
        
        from_mult = self._get_role_multiplier(from_role, role_multipliers)
        to_mult = self._get_role_multiplier(to_role, role_multipliers)
        
        if to_mult > from_mult:
            change_pct = ((to_mult / from_mult) - 1) * 100
            return f"+{change_pct:.0f}-{change_pct + 10:.0f}%"
        else:
            return "Similar range"
    
    def _get_role_multiplier(self, role: str, multipliers: Dict) -> float:
        """Get salary multiplier for a role"""
        
        role_lower = role.lower()
        for key, mult in multipliers.items():
            if key in role_lower:
                return mult
        return 1.5  # Default
    
    def _generate_market_insights(self, role: str, market_data: Dict) -> List[str]:
        """Generate market insights for the role"""
        
        insights = []
        
        # Job availability
        total_jobs = market_data.get("total_jobs", 0)
        if total_jobs > 1000:
            insights.append(f"🔥 High demand: {total_jobs:,}+ job openings")
        elif total_jobs > 500:
            insights.append(f"✅ Good demand: {total_jobs:,} job openings")
        elif total_jobs > 100:
            insights.append(f"⚠️ Moderate demand: {total_jobs} job openings")
        else:
            insights.append(f"⚠️ Limited demand: {total_jobs} job openings")
        
        # Remote work
        remote_pct = market_data.get("remote_percentage", 0)
        if remote_pct > 50:
            insights.append(f"🏠 High remote work: {remote_pct:.0f}% of jobs")
        elif remote_pct > 25:
            insights.append(f"🏠 Some remote work: {remote_pct:.0f}% of jobs")
        
        # Top skills
        top_skills = market_data.get("top_skills", [])[:3]
        if top_skills:
            insights.append(f"🎯 Hot skills: {', '.join(top_skills)}")
        
        # Salary trend
        salary_trend = market_data.get("salary_trend", "stable")
        if salary_trend == "increasing":
            insights.append("💰 Salaries trending upward")
        elif salary_trend == "below_market":
            insights.append("💰 Salaries below market average")
        
        return insights
    
    def _generate_milestones(self, transition: CareerTransition) -> List[str]:
        """Generate key milestones for the transition"""
        
        milestones = []
        
        if transition.skill_gaps:
            milestones.append(f"Learn {len(transition.skill_gaps)} key skills")
        
        milestones.append("Build relevant project portfolio")
        milestones.append("Network with industry professionals")
        milestones.append("Apply for target positions")
        
        return milestones
    
    def _generate_recommendations(
        self, 
        transition: CareerTransition, 
        user_profile: UserProfile
    ) -> List[str]:
        """Generate specific recommendations"""
        
        recommendations = []
        
        # Skill-based recommendations
        if transition.skill_gaps:
            top_gaps = transition.skill_gaps[:3]
            recommendations.append(f"Priority: Learn {', '.join(top_gaps)}")
        
        # Experience-based recommendations
        if user_profile.experience_years < 3:
            recommendations.append("Focus on building hands-on experience")
        
        # Performance-based recommendations
        if user_profile.performance_rating < 4:
            recommendations.append("Improve performance rating in current role")
        
        # Market-based recommendations
        if transition.market_demand in ["low", "very_low"]:
            recommendations.append("Consider alternative roles with higher demand")
        
        return recommendations
    
    def _build_career_graph(self) -> Dict:
        """Build career progression graph"""
        
        return {
            "entry": {
                "next_roles": ["mid", "senior"],
                "typical_years": 2
            },
            "mid": {
                "next_roles": ["senior", "lead", "manager"],
                "typical_years": 3
            },
            "senior": {
                "next_roles": ["lead", "principal", "manager", "director"],
                "typical_years": 4
            },
            "lead": {
                "next_roles": ["principal", "manager", "director"],
                "typical_years": 3
            },
            "executive": {
                "next_roles": ["director", "vp"],
                "typical_years": 5
            }
        }
    
    def _get_possible_next_roles(self, current_role: str, industry: str) -> List[str]:
        """Get possible next roles based on current role and industry"""
        
        # Industry-specific role mappings
        role_mappings = {
            "Technology / software": {
                "entry": ["Software Engineer II", "Senior Software Engineer", "Full Stack Developer"],
                "mid": ["Senior Software Engineer", "Tech Lead", "Engineering Manager", "Staff Engineer"],
                "senior": ["Staff Engineer", "Principal Engineer", "Engineering Manager", "Director of Engineering"],
                "lead": ["Principal Engineer", "Engineering Manager", "Director of Engineering"],
                "executive": ["VP of Engineering", "CTO", "Head of Engineering"]
            },
            "Financial services / fintech": {
                "entry": ["Financial Analyst II", "Senior Analyst", "Associate"],
                "mid": ["Senior Analyst", "Team Lead", "Manager", "Principal Analyst"],
                "senior": ["Manager", "Senior Manager", "Director", "Principal"],
                "lead": ["Director", "VP", "Head of Department"],
                "executive": ["VP", "SVP", "Chief Financial Officer"]
            },
            "Healthcare / biotech": {
                "entry": ["Research Associate II", "Senior Associate", "Specialist"],
                "mid": ["Senior Associate", "Team Lead", "Manager", "Principal Scientist"],
                "senior": ["Manager", "Senior Manager", "Director", "Principal"],
                "lead": ["Director", "VP", "Head of Research"],
                "executive": ["VP", "Chief Medical Officer", "Head of R&D"]
            }
        }
        
        # Default mapping for other industries
        default_mapping = {
            "entry": ["Senior Associate", "Team Lead", "Specialist"],
            "mid": ["Senior Specialist", "Team Lead", "Manager", "Principal"],
            "senior": ["Manager", "Senior Manager", "Director", "Principal"],
            "lead": ["Director", "VP", "Head of Department"],
            "executive": ["VP", "SVP", "C-Level"]
        }
        
        current_normalized = self._normalize_role(current_role)
        industry_roles = role_mappings.get(industry, default_mapping)
        
        return industry_roles.get(current_normalized, ["Senior " + current_role])
    
    def _normalize_role(self, role_level: str) -> str:
        """Normalize role level to standard categories"""
        
        role_lower = role_level.lower()
        
        if "entry" in role_lower or "junior" in role_lower or "associate" in role_lower:
            return "entry"
        elif "senior" in role_lower or "sr" in role_lower:
            return "senior"
        elif "lead" in role_lower or "principal" in role_lower or "staff" in role_lower:
            return "lead"
        elif "executive" in role_lower or "director" in role_lower or "vp" in role_lower or "head" in role_lower:
            return "executive"
        else:
            return "mid"
    
    def _get_role_requirements(self, role: str) -> Dict:
        """Get requirements for a specific role"""
        
        # Simplified role requirements database
        requirements = {
            "Senior Software Engineer": {
                "min_experience": 3,
                "required_skills": ["system design", "mentoring", "code review", "architecture"]
            },
            "Tech Lead": {
                "min_experience": 5,
                "required_skills": ["leadership", "technical strategy", "project management", "mentoring"]
            },
            "Engineering Manager": {
                "min_experience": 6,
                "required_skills": ["leadership", "people management", "strategic planning", "communication"]
            },
            "Staff Engineer": {
                "min_experience": 7,
                "required_skills": ["system design", "architecture", "technical leadership", "mentoring"]
            },
            "Principal Engineer": {
                "min_experience": 8,
                "required_skills": ["architecture", "technical strategy", "leadership", "innovation"]
            },
            "Director of Engineering": {
                "min_experience": 10,
                "required_skills": ["strategic planning", "team building", "leadership", "business acumen"]
            }
        }
        
        return requirements.get(role, {
            "min_experience": 3,
            "required_skills": ["leadership", "communication", "problem solving"]
        })