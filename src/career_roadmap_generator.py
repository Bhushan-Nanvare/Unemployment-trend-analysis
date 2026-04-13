"""
career_roadmap_generator.py

PERSONALIZED CAREER ROADMAP ENGINE
===================================

Generates step-by-step learning paths based on:
- User profile (level, known skills, target role)
- Real-time job market trends (dynamic skill detection)

Author: System Refactoring
Date: 2026-04-13
Version: 5.0.0 (Personalized Roadmaps)

CRITICAL RULES:
- NO hardcoded fake suggestions
- NO generic/random roadmaps
- Roadmap must be logical, ordered, and practical
- Use real detected trending skills to prioritize learning
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
from src.dynamic_skill_detector import get_dynamic_trending_skills


# ═══════════════════════════════════════════════════════════════════════════
# ROLE SKILL REQUIREMENTS (Phase 2)
# ═══════════════════════════════════════════════════════════════════════════

ROLE_REQUIREMENTS = {
    "Data Scientist": {
        "foundation": ["Python", "SQL", "Statistics"],
        "intermediate": ["Data Analysis", "Data Visualization", "Pandas"],
        "advanced": ["Machine Learning", "Deep Learning", "Feature Engineering"],
        "projects": [
            "Build a predictive model for real-world dataset",
            "Create interactive dashboard with visualizations",
            "End-to-end ML pipeline with deployment"
        ]
    },
    "ML Engineer": {
        "foundation": ["Python", "Machine Learning", "Git"],
        "intermediate": ["Deep Learning", "Model Optimization", "Docker"],
        "advanced": ["MLOps", "Kubernetes", "System Design", "Cloud (AWS/Azure)"],
        "projects": [
            "Build and deploy ML model to production",
            "Create ML pipeline with CI/CD",
            "Implement model monitoring and retraining system"
        ]
    },
    "Data Engineer": {
        "foundation": ["Python", "SQL", "Linux"],
        "intermediate": ["ETL", "Data Warehousing", "Spark"],
        "advanced": ["Kafka", "Airflow", "Cloud (AWS/Azure)", "Data Pipeline Design"],
        "projects": [
            "Build scalable ETL pipeline",
            "Design and implement data warehouse",
            "Create real-time data streaming system"
        ]
    },
    "Cloud Engineer": {
        "foundation": ["Linux", "Networking", "Python"],
        "intermediate": ["AWS", "Azure", "Docker", "Terraform"],
        "advanced": ["Kubernetes", "DevOps", "Infrastructure as Code", "Security"],
        "projects": [
            "Deploy multi-tier application on cloud",
            "Implement CI/CD pipeline with automation",
            "Design highly available cloud architecture"
        ]
    },
    "Full Stack Developer": {
        "foundation": ["HTML", "CSS", "JavaScript", "Git"],
        "intermediate": ["React", "Node.js", "SQL", "REST API"],
        "advanced": ["System Design", "Microservices", "Cloud Deployment", "DevOps"],
        "projects": [
            "Build full-stack web application",
            "Create RESTful API with authentication",
            "Deploy scalable application to cloud"
        ]
    },
    "DevOps Engineer": {
        "foundation": ["Linux", "Git", "Python", "Bash"],
        "intermediate": ["Docker", "Jenkins", "CI/CD", "Monitoring"],
        "advanced": ["Kubernetes", "Terraform", "AWS", "Infrastructure Automation"],
        "projects": [
            "Implement complete CI/CD pipeline",
            "Automate infrastructure provisioning",
            "Build monitoring and alerting system"
        ]
    },
    "Cybersecurity Analyst": {
        "foundation": ["Networking", "Linux", "Security Fundamentals"],
        "intermediate": ["Penetration Testing", "Security Tools", "Incident Response"],
        "advanced": ["Threat Intelligence", "Security Operations", "Compliance"],
        "projects": [
            "Conduct security audit and vulnerability assessment",
            "Build security monitoring dashboard",
            "Implement incident response playbook"
        ]
    },
    "Backend Developer": {
        "foundation": ["Python", "SQL", "Git", "REST API"],
        "intermediate": ["Django/Flask", "Database Design", "Authentication"],
        "advanced": ["Microservices", "Caching", "System Design", "Cloud"],
        "projects": [
            "Build scalable REST API",
            "Implement microservices architecture",
            "Deploy backend system to production"
        ]
    },
    "AI/ML Researcher": {
        "foundation": ["Python", "Mathematics", "Statistics", "Machine Learning"],
        "intermediate": ["Deep Learning", "NLP", "Computer Vision", "PyTorch/TensorFlow"],
        "advanced": ["Research Methods", "Paper Implementation", "Model Architecture"],
        "projects": [
            "Implement research paper from scratch",
            "Develop novel ML algorithm or technique",
            "Publish findings and open-source code"
        ]
    },
    "Product Manager": {
        "foundation": ["Product Strategy", "User Research", "Agile"],
        "intermediate": ["Data Analysis", "SQL", "Product Metrics", "Roadmapping"],
        "advanced": ["Technical Product Management", "Stakeholder Management", "Go-to-Market"],
        "projects": [
            "Define and launch new product feature",
            "Conduct user research and create PRD",
            "Build product roadmap with metrics"
        ]
    }
}


# ═══════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UserProfile:
    """User profile for roadmap generation."""
    user_level: str  # Beginner, Intermediate, Advanced
    known_skills: List[str]
    target_role: str


@dataclass
class RoadmapStep:
    """Single step in learning roadmap."""
    step_number: int
    skill: str
    category: str  # foundation, intermediate, advanced, project
    priority: str  # high, medium, low (based on job market trends)
    estimated_weeks: int
    is_trending: bool
    trend_rank: Optional[int]


@dataclass
class CareerRoadmap:
    """Complete personalized career roadmap."""
    target_role: str
    user_level: str
    known_skills: List[str]
    missing_skills: List[str]
    priority_skills: List[str]  # Based on job market trends
    roadmap_steps: List[RoadmapStep]
    suggested_projects: List[str]
    total_duration_weeks: int
    timestamp: datetime


# ═══════════════════════════════════════════════════════════════════════════
# CAREER ROADMAP GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

class CareerRoadmapGenerator:
    """
    Generates personalized career roadmaps based on user profile and job market trends.
    """
    
    def __init__(self):
        self.trending_skills_cache = None
        self.cache_timestamp = None
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 3: SKILL GAP ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════
    
    def analyze_skill_gap(self, user_profile: UserProfile) -> Tuple[List[str], List[str]]:
        """
        Compare required skills vs known skills and identify gaps.
        
        Phase 3: Skill Gap Analysis
        - Get required skills for target role
        - Remove already known skills
        - Return missing skills
        
        Args:
            user_profile: User's profile with known skills and target role
        
        Returns:
            Tuple of (all_required_skills, missing_skills)
        """
        role_reqs = ROLE_REQUIREMENTS.get(user_profile.target_role)
        
        if not role_reqs:
            # If role not found, return empty
            return [], []
        
        # Collect all required skills (excluding projects)
        all_required = []
        for category in ["foundation", "intermediate", "advanced"]:
            all_required.extend(role_reqs.get(category, []))
        
        # Normalize skill names for comparison (case-insensitive)
        known_skills_lower = [s.lower() for s in user_profile.known_skills]
        
        # Find missing skills
        missing_skills = [
            skill for skill in all_required
            if skill.lower() not in known_skills_lower
        ]
        
        return all_required, missing_skills
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 4: TREND INTEGRATION
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_trending_skills(self) -> Dict:
        """
        Get trending skills from job market (with caching).
        
        Phase 4: Trend Integration
        - Fetch trending skills from dynamic detector
        - Cache results to avoid repeated API calls
        
        Returns:
            Dictionary with trending skills data
        """
        # Use cache if available and fresh (within 1 hour)
        if self.trending_skills_cache and self.cache_timestamp:
            age = (datetime.now() - self.cache_timestamp).total_seconds()
            if age < 3600:  # 1 hour
                return self.trending_skills_cache
        
        # Fetch fresh trending skills
        trending = get_dynamic_trending_skills(top_n=20)
        
        # Cache results
        self.trending_skills_cache = trending
        self.cache_timestamp = datetime.now()
        
        return trending
    
    def prioritize_by_trends(self, missing_skills: List[str]) -> List[str]:
        """
        Prioritize missing skills based on job market trends.
        
        Phase 4: Trend Integration
        - Check which missing skills are trending
        - Rank by demand score
        - Return prioritized list
        
        Args:
            missing_skills: List of skills user needs to learn
        
        Returns:
            List of skills prioritized by job market demand
        """
        trending_data = self.get_trending_skills()
        trending_skills = trending_data.get("skills", [])
        
        # Create mapping of skill name to trend rank and score
        trend_map = {
            skill["name"].lower(): {
                "rank": skill["rank"],
                "demand": skill["demand"]
            }
            for skill in trending_skills
        }
        
        # Separate trending and non-trending skills
        trending_missing = []
        non_trending_missing = []
        
        for skill in missing_skills:
            skill_lower = skill.lower()
            
            # Check for exact match or partial match
            is_trending = False
            for trend_skill in trend_map.keys():
                if skill_lower in trend_skill or trend_skill in skill_lower:
                    trending_missing.append((skill, trend_map[trend_skill]["rank"]))
                    is_trending = True
                    break
            
            if not is_trending:
                non_trending_missing.append(skill)
        
        # Sort trending skills by rank (lower rank = higher priority)
        trending_missing.sort(key=lambda x: x[1])
        priority_skills = [skill for skill, _ in trending_missing]
        
        # Combine: trending first, then non-trending
        return priority_skills + non_trending_missing
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 5: ROADMAP GENERATION
    # ═══════════════════════════════════════════════════════════════════════
    
    def generate_roadmap_steps(
        self,
        user_profile: UserProfile,
        missing_skills: List[str],
        priority_skills: List[str]
    ) -> List[RoadmapStep]:
        """
        Create ordered roadmap with logical dependencies.
        
        Phase 5: Roadmap Generation
        - Maintain logical order: foundation → intermediate → advanced
        - Prioritize trending skills within each category
        - Assign estimated duration
        
        Args:
            user_profile: User's profile
            missing_skills: Skills user needs to learn
            priority_skills: Skills prioritized by trends
        
        Returns:
            List of RoadmapStep objects in learning order
        """
        role_reqs = ROLE_REQUIREMENTS.get(user_profile.target_role, {})
        trending_data = self.get_trending_skills()
        trending_skills_list = [s["name"].lower() for s in trending_data.get("skills", [])]
        
        # Create trend rank mapping
        trend_rank_map = {
            s["name"].lower(): s["rank"]
            for s in trending_data.get("skills", [])
        }
        
        roadmap_steps = []
        step_number = 1
        
        # Helper function to check if skill is trending
        def is_skill_trending(skill: str) -> Tuple[bool, Optional[int]]:
            skill_lower = skill.lower()
            for trend_skill in trending_skills_list:
                if skill_lower in trend_skill or trend_skill in skill_lower:
                    return True, trend_rank_map.get(trend_skill)
            return False, None
        
        # Helper function to get priority level
        def get_priority(skill: str, is_trending: bool) -> str:
            if is_trending:
                return "high"
            elif skill in priority_skills[:5]:
                return "medium"
            else:
                return "low"
        
        # Phase 6: Personalization - Adjust based on user level
        categories_to_include = []
        
        if user_profile.user_level == "Beginner":
            categories_to_include = ["foundation", "intermediate", "advanced"]
        elif user_profile.user_level == "Intermediate":
            categories_to_include = ["intermediate", "advanced"]
        else:  # Advanced
            categories_to_include = ["advanced"]
        
        # Generate steps for each category
        for category in categories_to_include:
            category_skills = role_reqs.get(category, [])
            
            # Filter to only missing skills
            missing_in_category = [
                skill for skill in category_skills
                if skill in missing_skills
            ]
            
            # Sort by priority (trending first)
            missing_in_category.sort(
                key=lambda s: (
                    not is_skill_trending(s)[0],  # Trending first
                    priority_skills.index(s) if s in priority_skills else 999
                )
            )
            
            # Create steps
            for skill in missing_in_category:
                is_trending, trend_rank = is_skill_trending(skill)
                priority = get_priority(skill, is_trending)
                
                # Estimate duration based on category and level
                if category == "foundation":
                    weeks = 3
                elif category == "intermediate":
                    weeks = 4
                else:  # advanced
                    weeks = 4
                
                roadmap_steps.append(RoadmapStep(
                    step_number=step_number,
                    skill=skill,
                    category=category,
                    priority=priority,
                    estimated_weeks=weeks,
                    is_trending=is_trending,
                    trend_rank=trend_rank
                ))
                
                step_number += 1
        
        # Phase 7: Project Integration
        projects = role_reqs.get("projects", [])
        for i, project in enumerate(projects):
            roadmap_steps.append(RoadmapStep(
                step_number=step_number,
                skill=project,
                category="project",
                priority="high",
                estimated_weeks=4,
                is_trending=False,
                trend_rank=None
            ))
            step_number += 1
        
        return roadmap_steps
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 9: OUTPUT
    # ═══════════════════════════════════════════════════════════════════════
    
    def generate_roadmap(self, user_profile: UserProfile) -> CareerRoadmap:
        """
        Main entry point: Generate complete personalized roadmap.
        
        Orchestrates all phases:
        1. Input validation
        2. Role skill requirements lookup
        3. Skill gap analysis
        4. Trend integration
        5. Roadmap generation
        6. Personalization
        7. Project integration
        8. Timeline calculation
        9. Output formatting
        
        Args:
            user_profile: User's profile with level, known skills, target role
        
        Returns:
            CareerRoadmap with complete personalized learning path
        """
        # Phase 3: Skill Gap Analysis
        all_required, missing_skills = self.analyze_skill_gap(user_profile)
        
        if not missing_skills:
            # User already knows all required skills
            return CareerRoadmap(
                target_role=user_profile.target_role,
                user_level=user_profile.user_level,
                known_skills=user_profile.known_skills,
                missing_skills=[],
                priority_skills=[],
                roadmap_steps=[],
                suggested_projects=ROLE_REQUIREMENTS.get(user_profile.target_role, {}).get("projects", []),
                total_duration_weeks=0,
                timestamp=datetime.now()
            )
        
        # Phase 4: Trend Integration
        priority_skills = self.prioritize_by_trends(missing_skills)
        
        # Phase 5-8: Roadmap Generation
        roadmap_steps = self.generate_roadmap_steps(
            user_profile,
            missing_skills,
            priority_skills
        )
        
        # Calculate total duration
        total_weeks = sum(step.estimated_weeks for step in roadmap_steps)
        
        # Get projects
        projects = ROLE_REQUIREMENTS.get(user_profile.target_role, {}).get("projects", [])
        
        return CareerRoadmap(
            target_role=user_profile.target_role,
            user_level=user_profile.user_level,
            known_skills=user_profile.known_skills,
            missing_skills=missing_skills,
            priority_skills=priority_skills[:5],  # Top 5 priority skills
            roadmap_steps=roadmap_steps,
            suggested_projects=projects,
            total_duration_weeks=total_weeks,
            timestamp=datetime.now()
        )


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

def generate_career_roadmap(
    user_level: str,
    known_skills: List[str],
    target_role: str
) -> Dict:
    """
    Generate personalized career roadmap.
    
    Args:
        user_level: "Beginner", "Intermediate", or "Advanced"
        known_skills: List of skills user already knows
        target_role: Target job role (e.g., "Data Scientist")
    
    Returns:
        Dictionary with roadmap data
    """
    profile = UserProfile(
        user_level=user_level,
        known_skills=known_skills,
        target_role=target_role
    )
    
    generator = CareerRoadmapGenerator()
    roadmap = generator.generate_roadmap(profile)
    
    # Format output
    return {
        "target_role": roadmap.target_role,
        "user_level": roadmap.user_level,
        "known_skills": roadmap.known_skills,
        "missing_skills": roadmap.missing_skills,
        "priority_skills": roadmap.priority_skills,
        "roadmap_steps": [
            {
                "step": step.step_number,
                "skill": step.skill,
                "category": step.category,
                "priority": step.priority,
                "weeks": step.estimated_weeks,
                "is_trending": step.is_trending,
                "trend_rank": step.trend_rank
            }
            for step in roadmap.roadmap_steps
        ],
        "suggested_projects": roadmap.suggested_projects,
        "total_duration_weeks": roadmap.total_duration_weeks,
        "total_duration_months": round(roadmap.total_duration_weeks / 4, 1),
        "timestamp": roadmap.timestamp.isoformat(),
        "available_roles": list(ROLE_REQUIREMENTS.keys())
    }


def get_available_roles() -> List[str]:
    """Get list of available target roles."""
    return list(ROLE_REQUIREMENTS.keys())


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*80)
    print("PERSONALIZED CAREER ROADMAP TEST")
    print("="*80)
    print()
    
    # Test case
    result = generate_career_roadmap(
        user_level="Intermediate",
        known_skills=["Python", "SQL", "Git"],
        target_role="Data Scientist"
    )
    
    print(f"Target Role: {result['target_role']}")
    print(f"User Level: {result['user_level']}")
    print(f"Known Skills: {', '.join(result['known_skills'])}")
    print(f"Missing Skills: {len(result['missing_skills'])}")
    print(f"Priority Skills (Trending): {', '.join(result['priority_skills'])}")
    print(f"Total Duration: {result['total_duration_months']} months")
    print()
    print("Personalized Roadmap:")
    print("-"*80)
    
    for step in result['roadmap_steps']:
        trending_badge = "🔥 TRENDING" if step['is_trending'] else ""
        priority_badge = f"[{step['priority'].upper()}]"
        print(f"{step['step']:2d}. {step['skill']:<40} "
              f"{priority_badge:<8} {step['weeks']} weeks  {trending_badge}")
    
    print()
    print("Suggested Projects:")
    for i, project in enumerate(result['suggested_projects'], 1):
        print(f"  {i}. {project}")
