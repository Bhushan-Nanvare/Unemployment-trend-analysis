"""Analytics components for job risk assessment."""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class SalaryEstimate:
    """Salary analysis result"""
    base_salary: float  # Base estimate for role/industry/experience
    location_adjusted: float  # After location multiplier
    risk_adjusted: float  # After risk penalty
    location_multiplier: float  # Applied multiplier
    risk_penalty_pct: float  # Percentage reduction due to risk
    confidence_interval: Tuple[float, float]  # (low, high)
    explanation: str  # Human-readable explanation


@dataclass
class BenchmarkResult:
    """Peer comparison result"""
    user_risk: float
    percentile: float  # User's percentile (0-100)
    peer_distribution: List[float]  # Risk scores of synthetic peers
    percentile_markers: Dict[str, float]  # 25th, 50th, 75th, 90th
    peer_count: int
    comparison_text: str  # "You are in the 35th percentile..."
