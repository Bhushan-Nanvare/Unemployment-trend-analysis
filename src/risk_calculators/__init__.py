"""Risk calculator components for job risk assessment."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class UserProfile:
    """Complete user profile for risk assessment"""
    skills: List[str]
    industry: str
    role_level: str  # "Entry", "Mid", "Senior", "Lead", "Executive"
    experience_years: int
    education_level: str
    location: str
    age: int
    company_size: str  # "1-10", "11-50", "51-200", "201-1000", "1001-5000", "5000+"
    remote_capability: bool
    performance_rating: int  # 1-5


@dataclass
class RiskProfile:
    """Unified risk assessment result"""
    overall_risk: float  # 0-100
    automation_risk: float  # 0-100
    recession_risk: float  # 0-100
    age_discrimination_risk: float  # 0-100
    risk_level: str  # "Low", "Medium", "High"
    contributing_factors: Dict[str, float]  # Factor name -> contribution
    timestamp: datetime


@dataclass
class AutomationRiskResult:
    """Automation risk assessment result"""
    score: float  # 0-100
    risk_level: str
    contributing_factors: Dict[str, float]
    recommendations: List[str]


@dataclass
class RecessionRiskResult:
    """Recession vulnerability assessment result"""
    score: float  # 0-100
    risk_level: str
    contributing_factors: Dict[str, float]
    recommendations: List[str]


@dataclass
class AgeDiscriminationRiskResult:
    """Age discrimination risk assessment result"""
    score: float  # 0-100
    risk_level: str
    contributing_factors: Dict[str, float]
    recommendations: List[str]
