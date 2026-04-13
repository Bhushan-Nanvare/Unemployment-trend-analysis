"""
shock_scenario.py
Applies an economic shock overlay on top of a baseline forecast.

REFACTORED ECONOMIC MODEL (2026-04-13):
========================================

Economic rationale:
  Shocks typically build up gradually (ramp-up phase), persist at peak,
  then decay exponentially during recovery. This reflects real-world dynamics:
  - Financial crises: gradual contagion, not instant collapse
  - Pandemics: spread over time, not instant full impact
  - Policy responses: take time to implement and show effects

Key improvements:
  1. ADDITIVE shock model (not multiplicative) - more realistic for percentage points
  2. RAMP-UP phase - shock builds gradually during duration period
  3. POLICY EFFECTS - policies actually reduce shock impact
  4. EXPONENTIAL RECOVERY - realistic decay pattern
  5. VALIDATION CONSTRAINTS - prevent unrealistic values
  6. EXPLAINABILITY - track shock components separately
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional


class ShockScenario:
    def __init__(
        self,
        shock_intensity: float = 0.3,
        shock_duration: int = 2,
        recovery_rate: float = 0.3,
        policy_name: Optional[str] = None,
    ):
        """
        Parameters:
        - shock_intensity: absolute percentage point increase in unemployment (0.3 = +0.3pp)
                          Converted from old multiplicative to additive model
        - shock_duration:  number of years for shock to ramp up to full intensity
                          0 = impulse shock (small 1-year spike)
        - recovery_rate:   exponential decay rate during recovery (0–1)
                          Higher = faster recovery
        - policy_name:     policy intervention to apply (reduces shock impact)
        """
        # Convert old multiplicative intensity to additive percentage points
        # Old: 0.3 meant +30% of baseline (e.g., 6% → 7.8%)
        # New: 0.3 means +0.3pp (e.g., 6% → 6.3%)
        # Scale factor: typical baseline ~6%, so 0.3 * 6 = 1.8pp
        self.shock_intensity_pp = shock_intensity * 6.0  # Convert to percentage points
        self.shock_duration = max(0, shock_duration)
        self.recovery_rate = float(np.clip(recovery_rate, 0.0, 1.0))
        self.policy_name = policy_name
        
        # Get policy strength (0-1 scale)
        self.policy_strength = self._get_policy_strength(policy_name)
        
        # Validation constraints
        self.MIN_UNEMPLOYMENT = 3.0  # Realistic minimum
        self.MAX_UNEMPLOYMENT = 10.0  # Realistic maximum
        self.MAX_YEARLY_CHANGE = 2.0  # Maximum change per year (pp)

    def _get_policy_strength(self, policy_name: Optional[str]) -> float:
        """
        Convert policy cushion score to normalized strength (0-1).
        
        Policy cushion scores:
        - Fiscal Stimulus: 35 → 0.35 strength
        - Industry Support: 30 → 0.30 strength
        - Labor Reforms: 25 → 0.25 strength
        - Monetary Policy: 20 → 0.20 strength
        - None: 0 → 0.0 strength
        """
        if not policy_name or policy_name == "None":
            return 0.0
        
        # Import here to avoid circular dependency
        from src.policy_playbook import PolicyPlaybook
        cushion_score = PolicyPlaybook.get_cushion_score(policy_name)
        
        # Normalize to 0-1 scale (max cushion is 35)
        return min(1.0, cushion_score / 100.0)

    def apply(self, baseline_df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies shock + policy + recovery overlay to baseline forecast.

        PHASE 1 - RAMP-UP (years 0 to shock_duration):
            Shock builds gradually: shock_effect = intensity × (t / duration)
            
        PHASE 2 - RECOVERY (after shock_duration):
            Shock decays exponentially: shock_effect × exp(-recovery_rate × t)
            
        POLICY EFFECT (all phases):
            adjusted_shock = shock_effect × (1 - policy_strength)
            
        FINAL CALCULATION:
            scenario_unemployment = baseline + adjusted_shock
            
        CONSTRAINTS:
            - Clamp to [3%, 10%] range
            - Limit yearly change to ±2pp

        Returns DataFrame with columns: 
            Year, Scenario_Unemployment, Shock_Component, Policy_Adjustment, Explanation
        """
        df = baseline_df.copy()
        n = len(df)

        results = []
        previous_value = None
        
        for i in range(n):
            base_val = float(df["Predicted_Unemployment"].iloc[i])
            year = int(df["Year"].iloc[i])
            
            # Calculate raw shock effect (percentage points)
            if self.shock_duration == 0:
                # Impulse shock: small spike in year 1 only
                if i == 0:
                    raw_shock = self.shock_intensity_pp * 0.3  # 30% of full intensity
                else:
                    # Exponential decay from year 2
                    t_recovery = i
                    raw_shock = (self.shock_intensity_pp * 0.3) * np.exp(-self.recovery_rate * t_recovery)
            elif i < self.shock_duration:
                # RAMP-UP PHASE: Gradual increase
                ramp_progress = (i + 1) / self.shock_duration
                raw_shock = self.shock_intensity_pp * ramp_progress
            else:
                # RECOVERY PHASE: Exponential decay
                t_recovery = i - self.shock_duration + 1
                raw_shock = self.shock_intensity_pp * np.exp(-self.recovery_rate * t_recovery)
            
            # Apply policy effect (reduces shock)
            policy_reduction = raw_shock * self.policy_strength
            adjusted_shock = raw_shock - policy_reduction
            
            # Calculate scenario unemployment (ADDITIVE model)
            scenario_val = base_val + adjusted_shock
            
            # Apply validation constraints
            # 1. Clamp to realistic range
            scenario_val = np.clip(scenario_val, self.MIN_UNEMPLOYMENT, self.MAX_UNEMPLOYMENT)
            
            # 2. Limit yearly change
            if previous_value is not None:
                max_change = previous_value + self.MAX_YEARLY_CHANGE
                min_change = previous_value - self.MAX_YEARLY_CHANGE
                scenario_val = np.clip(scenario_val, min_change, max_change)
            
            # Generate explanation
            explanation = self._generate_explanation(
                i, base_val, raw_shock, policy_reduction, adjusted_shock, scenario_val
            )
            
            results.append({
                "Year": year,
                "Scenario_Unemployment": round(scenario_val, 4),
                "Shock_Component": round(adjusted_shock, 4),
                "Policy_Adjustment": round(policy_reduction, 4),
                "Explanation": explanation
            })
            
            previous_value = scenario_val

        return pd.DataFrame(results)
    
    def _generate_explanation(
        self, 
        year_index: int, 
        baseline: float, 
        raw_shock: float, 
        policy_reduction: float,
        adjusted_shock: float,
        final_value: float
    ) -> str:
        """Generate human-readable explanation of unemployment change."""
        
        if self.shock_duration == 0:
            if year_index == 0:
                phase = "Impulse shock"
            else:
                phase = "Recovery"
        elif year_index < self.shock_duration:
            progress = int((year_index + 1) / self.shock_duration * 100)
            phase = f"Ramp-up ({progress}%)"
        else:
            phase = "Recovery"
        
        explanation_parts = [
            f"{phase}:",
            f"Baseline {baseline:.1f}%",
            f"+ Shock {adjusted_shock:+.2f}pp"
        ]
        
        if policy_reduction > 0.01:
            explanation_parts.append(f"(Policy reduced by {policy_reduction:.2f}pp)")
        
        explanation_parts.append(f"= {final_value:.1f}%")
        
        return " ".join(explanation_parts)

    def get_policy_adjusted_scenario(self, baseline_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Returns three scenarios for comparison:
        1. Baseline (no shock)
        2. Shock without policy
        3. Shock with policy (if policy applied)
        """
        # Baseline
        baseline = baseline_df.copy()
        baseline = baseline.rename(columns={"Predicted_Unemployment": "Baseline_Unemployment"})
        
        # Shock without policy
        no_policy_scenario = ShockScenario(
            shock_intensity=self.shock_intensity_pp / 6.0,  # Convert back
            shock_duration=self.shock_duration,
            recovery_rate=self.recovery_rate,
            policy_name=None
        )
        shock_only = no_policy_scenario.apply(baseline_df)
        
        # Shock with policy (current scenario)
        shock_with_policy = self.apply(baseline_df)
        
        return {
            "baseline": baseline,
            "shock_only": shock_only,
            "shock_with_policy": shock_with_policy
        }
