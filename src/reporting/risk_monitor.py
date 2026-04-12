"""Risk Monitor for tracking risk changes over time."""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np


@dataclass
class AssessmentHistory:
    """Single historical risk assessment"""
    timestamp: str  # ISO format datetime string
    overall_risk: float
    automation_risk: float
    recession_risk: float
    age_discrimination_risk: float
    risk_level: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AssessmentHistory":
        """Create from dictionary"""
        return cls(**data)


class RiskMonitor:
    """Tracks risk changes over time for users"""
    
    MAX_HISTORY_SIZE = 12  # Retain only last 12 assessments
    
    def __init__(self, storage_dir: str = ".cache/risk_history"):
        """
        Initialize Risk Monitor
        
        Args:
            storage_dir: Directory to store historical assessments
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_user_file(self, user_id: str) -> Path:
        """Get the storage file path for a user"""
        return self.storage_dir / f"{user_id}.json"
    
    def store_assessment(self, risk_profile, user_id: str = "default") -> None:
        """
        Store a risk assessment with timestamp
        
        Args:
            risk_profile: RiskProfile object with risk scores
            user_id: User identifier (default: "default")
        
        Requirements: 15.1, 15.2
        """
        # Create assessment history entry
        assessment = AssessmentHistory(
            timestamp=datetime.now().isoformat(),
            overall_risk=risk_profile.overall_risk,
            automation_risk=risk_profile.automation_risk,
            recession_risk=risk_profile.recession_risk,
            age_discrimination_risk=risk_profile.age_discrimination_risk,
            risk_level=risk_profile.risk_level,
        )
        
        # Load existing history
        history = self._load_history(user_id)
        
        # Append new assessment
        history.append(assessment)
        
        # Enforce history size constraint: retain only last 12 assessments
        if len(history) > self.MAX_HISTORY_SIZE:
            history = history[-self.MAX_HISTORY_SIZE:]
        
        # Save updated history
        self._save_history(user_id, history)
    
    def get_history(self, user_id: str = "default") -> List[AssessmentHistory]:
        """
        Retrieve assessment history for a user
        
        Args:
            user_id: User identifier (default: "default")
        
        Returns:
            List of AssessmentHistory objects, ordered by timestamp (oldest first)
        """
        return self._load_history(user_id)
    
    def compute_rate_of_change(self, user_id: str = "default") -> Dict[str, float]:
        """
        Calculate rate of change in risk scores using linear regression
        
        Args:
            user_id: User identifier (default: "default")
        
        Returns:
            Dictionary with rate of change (points per month) for each risk type:
            {
                "overall": -2.5,  # Negative = decreasing risk
                "automation": 1.2,  # Positive = increasing risk
                "recession": -0.8,
                "age_discrimination": 0.3
            }
        
        Requirements: 15.5
        """
        history = self._load_history(user_id)
        
        if len(history) < 2:
            # Need at least 2 data points for rate of change
            return {
                "overall": 0.0,
                "automation": 0.0,
                "recession": 0.0,
                "age_discrimination": 0.0,
            }
        
        # Convert timestamps to months since first assessment
        timestamps = [datetime.fromisoformat(h.timestamp) for h in history]
        first_time = timestamps[0]
        months = [(t - first_time).total_seconds() / (30.44 * 24 * 3600) for t in timestamps]
        
        # Extract risk scores
        overall_risks = [h.overall_risk for h in history]
        automation_risks = [h.automation_risk for h in history]
        recession_risks = [h.recession_risk for h in history]
        age_disc_risks = [h.age_discrimination_risk for h in history]
        
        # Calculate slopes using linear regression (least squares)
        def calculate_slope(x: List[float], y: List[float]) -> float:
            """Calculate slope of linear regression line"""
            if len(x) < 2:
                return 0.0
            
            x_arr = np.array(x)
            y_arr = np.array(y)
            
            # Linear regression: y = mx + b
            # Slope m = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
            n = len(x_arr)
            sum_x = np.sum(x_arr)
            sum_y = np.sum(y_arr)
            sum_xy = np.sum(x_arr * y_arr)
            sum_x2 = np.sum(x_arr ** 2)
            
            denominator = n * sum_x2 - sum_x ** 2
            if abs(denominator) < 1e-10:
                return 0.0
            
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            return slope
        
        return {
            "overall": calculate_slope(months, overall_risks),
            "automation": calculate_slope(months, automation_risks),
            "recession": calculate_slope(months, recession_risks),
            "age_discrimination": calculate_slope(months, age_disc_risks),
        }
    
    def identify_significant_changes(
        self, user_id: str = "default"
    ) -> List[Dict[str, any]]:
        """
        Identify significant changes (>10 percentage points) between consecutive assessments
        
        Args:
            user_id: User identifier (default: "default")
        
        Returns:
            List of significant changes with details:
            [
                {
                    "from_timestamp": "2024-01-01T10:00:00",
                    "to_timestamp": "2024-02-01T10:00:00",
                    "risk_type": "overall",
                    "from_value": 45.2,
                    "to_value": 32.1,
                    "change": -13.1,
                    "direction": "decreased"
                },
                ...
            ]
        
        Requirements: 15.4
        """
        history = self._load_history(user_id)
        
        if len(history) < 2:
            return []
        
        significant_changes = []
        
        # Check consecutive assessments
        for i in range(len(history) - 1):
            prev = history[i]
            curr = history[i + 1]
            
            # Check each risk type
            risk_types = [
                ("overall", prev.overall_risk, curr.overall_risk),
                ("automation", prev.automation_risk, curr.automation_risk),
                ("recession", prev.recession_risk, curr.recession_risk),
                ("age_discrimination", prev.age_discrimination_risk, curr.age_discrimination_risk),
            ]
            
            for risk_type, prev_value, curr_value in risk_types:
                change = curr_value - prev_value
                
                # Significant if absolute change > 10 percentage points
                if abs(change) > 10.0:
                    significant_changes.append({
                        "from_timestamp": prev.timestamp,
                        "to_timestamp": curr.timestamp,
                        "risk_type": risk_type,
                        "from_value": prev_value,
                        "to_value": curr_value,
                        "change": change,
                        "direction": "increased" if change > 0 else "decreased",
                    })
        
        return significant_changes
    
    def _load_history(self, user_id: str) -> List[AssessmentHistory]:
        """Load history from storage"""
        user_file = self._get_user_file(user_id)
        
        if not user_file.exists():
            return []
        
        try:
            with open(user_file, "r") as f:
                data = json.load(f)
                return [AssessmentHistory.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError, TypeError):
            # Corrupted file, return empty history
            return []
    
    def _save_history(self, user_id: str, history: List[AssessmentHistory]) -> None:
        """Save history to storage"""
        user_file = self._get_user_file(user_id)
        
        data = [h.to_dict() for h in history]
        
        with open(user_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def clear_history(self, user_id: str = "default") -> None:
        """
        Clear all history for a user (useful for testing)
        
        Args:
            user_id: User identifier (default: "default")
        """
        user_file = self._get_user_file(user_id)
        if user_file.exists():
            user_file.unlink()
