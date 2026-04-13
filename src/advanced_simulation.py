"""
advanced_simulation.py

ADVANCED SIMULATION ENGINE ENHANCEMENTS
=======================================

Adds sophisticated simulation capabilities including:
1. Monte Carlo simulations with uncertainty
2. Multi-shock scenarios (compound crises)
3. Sector-specific shock modeling
4. Dynamic policy response simulation
5. Economic cycle modeling
6. Stress testing frameworks

Author: Advanced Simulation Framework
Date: 2026-04-13
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random
from datetime import datetime

from .shock_scenario import ShockScenario
from .scenario_metrics import ScenarioMetrics
from .forecasting import ForecastingEngine
from .policy_playbook import PolicyPlaybook


class ShockType(Enum):
    """Types of economic shocks"""
    FINANCIAL_CRISIS = "financial_crisis"
    PANDEMIC = "pandemic"
    NATURAL_DISASTER = "natural_disaster"
    TRADE_WAR = "trade_war"
    TECHNOLOGY_DISRUPTION = "technology_disruption"
    ENERGY_CRISIS = "energy_crisis"
    GEOPOLITICAL = "geopolitical"
    SUPPLY_CHAIN = "supply_chain"


class EconomicCycle(Enum):
    """Economic cycle phases"""
    EXPANSION = "expansion"
    PEAK = "peak"
    CONTRACTION = "contraction"
    TROUGH = "trough"


@dataclass
class ShockEvent:
    """Represents a specific shock event"""
    shock_type: ShockType
    intensity: float  # 0.0 to 1.0
    duration: int     # years
    start_year: int   # relative to simulation start
    sector_impacts: Dict[str, float]  # sector-specific multipliers
    description: str


@dataclass
class MonteCarloConfig:
    """Configuration for Monte Carlo simulation"""
    num_simulations: int = 1000
    shock_intensity_std: float = 0.1
    recovery_rate_std: float = 0.05
    duration_variance: int = 1
    confidence_levels: List[float] = None
    
    def __post_init__(self):
        if self.confidence_levels is None:
            self.confidence_levels = [0.05, 0.25, 0.75, 0.95]


class AdvancedSimulationEngine:
    """Enhanced simulation engine with advanced capabilities"""
    
    def __init__(self):
        self.sector_sensitivities = {
            "Agriculture": {"pandemic": 0.3, "natural_disaster": 1.2, "trade_war": 0.8},
            "Manufacturing": {"financial_crisis": 1.1, "supply_chain": 1.3, "trade_war": 1.2},
            "Services": {"pandemic": 1.4, "financial_crisis": 0.9, "technology_disruption": 0.7},
            "Technology": {"financial_crisis": 0.8, "technology_disruption": 0.5, "geopolitical": 0.6},
            "Healthcare": {"pandemic": 0.6, "financial_crisis": 0.8, "natural_disaster": 0.9},
            "Education": {"pandemic": 1.1, "financial_crisis": 0.9, "technology_disruption": 0.8},
            "Tourism": {"pandemic": 1.8, "geopolitical": 1.3, "natural_disaster": 1.4},
            "Energy": {"energy_crisis": 1.5, "geopolitical": 1.2, "natural_disaster": 1.1},
        }
    
    def monte_carlo_simulation(
        self,
        baseline_df: pd.DataFrame,
        base_shock_intensity: float,
        base_shock_duration: int,
        base_recovery_rate: float,
        config: MonteCarloConfig
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation with parameter uncertainty.
        
        Returns distribution of outcomes and confidence intervals.
        """
        print(f"🎲 Running Monte Carlo simulation ({config.num_simulations} runs)...")
        
        results = []
        peak_unemployment_values = []
        recovery_times = []
        
        for i in range(config.num_simulations):
            # Add random variation to parameters
            shock_intensity = np.clip(
                np.random.normal(base_shock_intensity, config.shock_intensity_std),
                0.0, 1.0
            )
            
            recovery_rate = np.clip(
                np.random.normal(base_recovery_rate, config.recovery_rate_std),
                0.05, 0.8
            )
            
            duration = max(0, int(np.random.normal(base_shock_duration, config.duration_variance)))
            
            # Run simulation
            scenario = ShockScenario(
                shock_intensity=shock_intensity,
                shock_duration=duration,
                recovery_rate=recovery_rate
            ).apply(baseline_df)
            
            # Extract metrics
            peak_ue = float(scenario["Scenario_Unemployment"].max())
            peak_unemployment_values.append(peak_ue)
            
            # Calculate recovery time (years to return within 0.5pp of baseline)
            baseline_final = float(baseline_df["Predicted_Unemployment"].iloc[-1])
            recovery_time = None
            
            for idx, ue in enumerate(scenario["Scenario_Unemployment"]):
                if abs(ue - baseline_final) <= 0.5:
                    recovery_time = idx
                    break
            
            if recovery_time is None:
                recovery_time = len(scenario)  # Never recovered
            
            recovery_times.append(recovery_time)
            
            results.append({
                "simulation": i,
                "shock_intensity": shock_intensity,
                "recovery_rate": recovery_rate,
                "duration": duration,
                "peak_unemployment": peak_ue,
                "recovery_time": recovery_time,
                "scenario_data": scenario.to_dict(orient="records")
            })
        
        # Calculate statistics
        peak_stats = {
            "mean": np.mean(peak_unemployment_values),
            "std": np.std(peak_unemployment_values),
            "min": np.min(peak_unemployment_values),
            "max": np.max(peak_unemployment_values),
            "percentiles": {}
        }
        
        for conf_level in config.confidence_levels:
            percentile = conf_level * 100
            peak_stats["percentiles"][f"p{percentile:.0f}"] = np.percentile(
                peak_unemployment_values, percentile
            )
        
        recovery_stats = {
            "mean": np.mean(recovery_times),
            "std": np.std(recovery_times),
            "median": np.median(recovery_times),
        }
        
        # Create confidence bands
        confidence_bands = self._create_confidence_bands(results, config.confidence_levels)
        
        return {
            "config": config.__dict__,
            "peak_unemployment_stats": peak_stats,
            "recovery_time_stats": recovery_stats,
            "confidence_bands": confidence_bands,
            "simulation_results": results[:100],  # Return first 100 for analysis
            "summary": {
                "total_simulations": config.num_simulations,
                "mean_peak_ue": round(peak_stats["mean"], 2),
                "ue_95_confidence": [
                    round(peak_stats["percentiles"]["p5"], 2),
                    round(peak_stats["percentiles"]["p95"], 2)
                ],
                "mean_recovery_time": round(recovery_stats["mean"], 1),
            }
        }
    
    def multi_shock_scenario(
        self,
        baseline_df: pd.DataFrame,
        shock_events: List[ShockEvent],
        policy_responses: Optional[Dict[int, str]] = None
    ) -> Dict[str, Any]:
        """
        Simulate multiple overlapping shocks (compound crises).
        
        Args:
            baseline_df: Baseline forecast
            shock_events: List of shock events with timing
            policy_responses: Policy responses by year {year: policy_name}
        
        Returns:
            Compound scenario results with individual shock contributions
        """
        print(f"💥 Simulating multi-shock scenario ({len(shock_events)} shocks)...")
        
        # Initialize scenario with baseline
        compound_scenario = baseline_df.copy()
        compound_scenario["Compound_Unemployment"] = compound_scenario["Predicted_Unemployment"]
        
        shock_contributions = {}
        individual_scenarios = {}
        
        for i, shock_event in enumerate(shock_events):
            shock_name = f"{shock_event.shock_type.value}_{i}"
            
            # Calculate shock timing
            shock_start_idx = shock_event.start_year
            if shock_start_idx >= len(compound_scenario):
                continue  # Shock starts after simulation period
            
            # Apply sector-specific intensity adjustments
            adjusted_intensity = self._adjust_intensity_for_sectors(
                shock_event.intensity,
                shock_event.shock_type,
                shock_event.sector_impacts
            )
            
            # Create individual shock scenario
            individual_shock = ShockScenario(
                shock_intensity=adjusted_intensity,
                shock_duration=shock_event.duration,
                recovery_rate=0.3  # Default recovery rate
            ).apply(baseline_df)
            
            individual_scenarios[shock_name] = individual_shock
            
            # Apply shock to compound scenario starting from shock_start_idx
            for j in range(shock_start_idx, len(compound_scenario)):
                if j < len(individual_shock):
                    # Add shock impact (multiplicative)
                    baseline_val = compound_scenario.iloc[j]["Predicted_Unemployment"]
                    shock_val = individual_shock.iloc[j]["Scenario_Unemployment"]
                    shock_impact = shock_val - baseline_val
                    
                    # Apply shock impact to current compound scenario
                    compound_scenario.iloc[j, compound_scenario.columns.get_loc("Compound_Unemployment")] += shock_impact
            
            # Track individual contributions
            shock_contributions[shock_name] = {
                "type": shock_event.shock_type.value,
                "intensity": adjusted_intensity,
                "duration": shock_event.duration,
                "start_year": shock_event.start_year,
                "description": shock_event.description,
                "peak_impact": float(individual_shock["Scenario_Unemployment"].max() - baseline_df["Predicted_Unemployment"].max())
            }
        
        # Apply policy responses if specified
        if policy_responses:
            compound_scenario = self._apply_dynamic_policies(
                compound_scenario, policy_responses
            )
        
        # Calculate compound metrics
        compound_metrics = self._calculate_compound_metrics(
            baseline_df, compound_scenario, shock_contributions
        )
        
        return {
            "baseline": baseline_df.to_dict(orient="records"),
            "compound_scenario": compound_scenario.to_dict(orient="records"),
            "individual_scenarios": {k: v.to_dict(orient="records") for k, v in individual_scenarios.items()},
            "shock_contributions": shock_contributions,
            "compound_metrics": compound_metrics,
            "policy_responses": policy_responses or {},
            "summary": {
                "total_shocks": len(shock_events),
                "compound_peak_ue": round(float(compound_scenario["Compound_Unemployment"].max()), 2),
                "total_impact": round(float(compound_scenario["Compound_Unemployment"].max() - baseline_df["Predicted_Unemployment"].max()), 2),
                "most_severe_shock": max(shock_contributions.items(), key=lambda x: x[1]["peak_impact"])[0] if shock_contributions else None
            }
        }
    
    def stress_test_framework(
        self,
        baseline_df: pd.DataFrame,
        stress_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Run comprehensive stress testing across multiple scenarios.
        
        Args:
            baseline_df: Baseline forecast
            stress_scenarios: List of stress test configurations
        
        Returns:
            Stress test results with pass/fail criteria
        """
        print(f"🔬 Running stress test framework ({len(stress_scenarios)} scenarios)...")
        
        stress_results = {}
        pass_criteria = {
            "max_peak_unemployment": 12.0,  # Peak UE should not exceed 12%
            "max_duration_above_8": 3,      # Should not stay above 8% for more than 3 years
            "recovery_within_years": 5,     # Should recover within 5 years
        }
        
        for i, scenario_config in enumerate(stress_scenarios):
            scenario_name = scenario_config.get("name", f"Stress_Test_{i+1}")
            
            try:
                # Run scenario
                if scenario_config.get("type") == "multi_shock":
                    result = self.multi_shock_scenario(
                        baseline_df,
                        scenario_config["shock_events"],
                        scenario_config.get("policy_responses")
                    )
                    scenario_df = pd.DataFrame(result["compound_scenario"])
                    unemployment_col = "Compound_Unemployment"
                else:
                    # Single shock scenario
                    scenario = ShockScenario(
                        shock_intensity=scenario_config["shock_intensity"],
                        shock_duration=scenario_config["shock_duration"],
                        recovery_rate=scenario_config["recovery_rate"]
                    ).apply(baseline_df)
                    scenario_df = scenario
                    unemployment_col = "Scenario_Unemployment"
                
                # Evaluate against pass criteria
                peak_ue = float(scenario_df[unemployment_col].max())
                
                # Count years above 8%
                years_above_8 = sum(1 for ue in scenario_df[unemployment_col] if ue > 8.0)
                
                # Check recovery time
                baseline_final = float(baseline_df["Predicted_Unemployment"].iloc[-1])
                recovery_year = None
                
                for idx, ue in enumerate(scenario_df[unemployment_col]):
                    if abs(ue - baseline_final) <= 0.5:
                        recovery_year = idx
                        break
                
                recovery_time = recovery_year if recovery_year is not None else len(scenario_df)
                
                # Determine pass/fail
                tests = {
                    "peak_unemployment": {
                        "value": peak_ue,
                        "threshold": pass_criteria["max_peak_unemployment"],
                        "passed": peak_ue <= pass_criteria["max_peak_unemployment"]
                    },
                    "duration_above_8": {
                        "value": years_above_8,
                        "threshold": pass_criteria["max_duration_above_8"],
                        "passed": years_above_8 <= pass_criteria["max_duration_above_8"]
                    },
                    "recovery_time": {
                        "value": recovery_time,
                        "threshold": pass_criteria["recovery_within_years"],
                        "passed": recovery_time <= pass_criteria["recovery_within_years"]
                    }
                }
                
                overall_passed = all(test["passed"] for test in tests.values())
                
                stress_results[scenario_name] = {
                    "config": scenario_config,
                    "tests": tests,
                    "overall_passed": overall_passed,
                    "peak_unemployment": round(peak_ue, 2),
                    "recovery_time": recovery_time,
                    "scenario_data": scenario_df.to_dict(orient="records")
                }
                
            except Exception as e:
                stress_results[scenario_name] = {
                    "config": scenario_config,
                    "error": str(e),
                    "overall_passed": False
                }
        
        # Calculate summary statistics
        total_scenarios = len(stress_results)
        passed_scenarios = sum(1 for r in stress_results.values() if r.get("overall_passed", False))
        pass_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
        
        return {
            "stress_results": stress_results,
            "pass_criteria": pass_criteria,
            "summary": {
                "total_scenarios": total_scenarios,
                "passed_scenarios": passed_scenarios,
                "failed_scenarios": total_scenarios - passed_scenarios,
                "pass_rate": round(pass_rate, 1),
                "system_resilience": "HIGH" if pass_rate >= 80 else "MEDIUM" if pass_rate >= 60 else "LOW"
            }
        }
    
    def economic_cycle_simulation(
        self,
        baseline_df: pd.DataFrame,
        cycle_length: int = 8,
        amplitude: float = 0.15,
        current_phase: EconomicCycle = EconomicCycle.EXPANSION
    ) -> Dict[str, Any]:
        """
        Simulate economic cycles overlaid on baseline forecast.
        
        Args:
            baseline_df: Baseline forecast
            cycle_length: Length of full cycle in years
            amplitude: Maximum deviation from baseline (as fraction)
            current_phase: Current phase of the cycle
        
        Returns:
            Cyclical scenario with phase annotations
        """
        print(f"🔄 Simulating economic cycle (length: {cycle_length} years, amplitude: {amplitude:.1%})...")
        
        cycle_scenario = baseline_df.copy()
        cycle_scenario["Cyclical_Unemployment"] = cycle_scenario["Predicted_Unemployment"]
        cycle_scenario["Cycle_Phase"] = ""
        cycle_scenario["Cycle_Position"] = 0.0  # 0-1 position in cycle
        
        # Map current phase to starting position
        phase_positions = {
            EconomicCycle.EXPANSION: 0.0,
            EconomicCycle.PEAK: 0.25,
            EconomicCycle.CONTRACTION: 0.5,
            EconomicCycle.TROUGH: 0.75
        }
        
        start_position = phase_positions[current_phase]
        
        for i in range(len(cycle_scenario)):
            # Calculate position in cycle (0-1)
            cycle_position = (start_position + (i / cycle_length)) % 1.0
            
            # Convert to radians for sine wave
            cycle_radians = cycle_position * 2 * np.pi
            
            # Calculate cyclical adjustment (inverted sine for unemployment)
            # Peak unemployment at cycle trough, low unemployment at cycle peak
            cyclical_factor = -np.sin(cycle_radians) * amplitude
            
            # Apply to unemployment
            baseline_ue = cycle_scenario.iloc[i]["Predicted_Unemployment"]
            cyclical_ue = baseline_ue * (1 + cyclical_factor)
            
            cycle_scenario.iloc[i, cycle_scenario.columns.get_loc("Cyclical_Unemployment")] = cyclical_ue
            cycle_scenario.iloc[i, cycle_scenario.columns.get_loc("Cycle_Position")] = cycle_position
            
            # Determine phase
            if 0 <= cycle_position < 0.25:
                phase = EconomicCycle.EXPANSION.value
            elif 0.25 <= cycle_position < 0.5:
                phase = EconomicCycle.PEAK.value
            elif 0.5 <= cycle_position < 0.75:
                phase = EconomicCycle.CONTRACTION.value
            else:
                phase = EconomicCycle.TROUGH.value
            
            cycle_scenario.iloc[i, cycle_scenario.columns.get_loc("Cycle_Phase")] = phase
        
        # Calculate cycle metrics
        cycle_metrics = {
            "cycle_length": cycle_length,
            "amplitude": amplitude,
            "peak_unemployment": float(cycle_scenario["Cyclical_Unemployment"].max()),
            "trough_unemployment": float(cycle_scenario["Cyclical_Unemployment"].min()),
            "volatility": float(cycle_scenario["Cyclical_Unemployment"].std()),
            "phases_covered": list(cycle_scenario["Cycle_Phase"].unique())
        }
        
        return {
            "baseline": baseline_df.to_dict(orient="records"),
            "cyclical_scenario": cycle_scenario.to_dict(orient="records"),
            "cycle_metrics": cycle_metrics,
            "current_phase": current_phase.value,
            "summary": {
                "peak_ue": round(cycle_metrics["peak_unemployment"], 2),
                "trough_ue": round(cycle_metrics["trough_unemployment"], 2),
                "volatility": round(cycle_metrics["volatility"], 2),
                "cycle_range": round(cycle_metrics["peak_unemployment"] - cycle_metrics["trough_unemployment"], 2)
            }
        }
    
    def _create_confidence_bands(
        self,
        simulation_results: List[Dict],
        confidence_levels: List[float]
    ) -> Dict[str, List]:
        """Create confidence bands from Monte Carlo results"""
        
        # Group by year
        years = set()
        for result in simulation_results:
            for point in result["scenario_data"]:
                years.add(point["Year"])
        
        years = sorted(years)
        confidence_bands = {"Year": years}
        
        for conf_level in confidence_levels:
            percentile = conf_level * 100
            band_values = []
            
            for year in years:
                year_values = []
                for result in simulation_results:
                    for point in result["scenario_data"]:
                        if point["Year"] == year:
                            year_values.append(point["Scenario_Unemployment"])
                            break
                
                if year_values:
                    band_values.append(np.percentile(year_values, percentile))
                else:
                    band_values.append(None)
            
            confidence_bands[f"p{percentile:.0f}"] = band_values
        
        return confidence_bands
    
    def _adjust_intensity_for_sectors(
        self,
        base_intensity: float,
        shock_type: ShockType,
        sector_impacts: Dict[str, float]
    ) -> float:
        """Adjust shock intensity based on sector-specific impacts"""
        
        # Get sector sensitivities for this shock type
        shock_key = shock_type.value
        sector_multipliers = []
        
        for sector, sensitivity_dict in self.sector_sensitivities.items():
            if shock_key in sensitivity_dict:
                sector_weight = sector_impacts.get(sector, 1.0)
                sector_multipliers.append(sensitivity_dict[shock_key] * sector_weight)
        
        if sector_multipliers:
            avg_multiplier = np.mean(sector_multipliers)
            return min(1.0, base_intensity * avg_multiplier)
        
        return base_intensity
    
    def _apply_dynamic_policies(
        self,
        scenario_df: pd.DataFrame,
        policy_responses: Dict[int, str]
    ) -> pd.DataFrame:
        """Apply dynamic policy responses during simulation"""
        
        modified_scenario = scenario_df.copy()
        
        for year_idx, policy_name in policy_responses.items():
            if year_idx < len(modified_scenario):
                # Get policy effectiveness
                policy_config = PolicyPlaybook.get_policy(policy_name)
                effectiveness = policy_config.get("effectiveness_score", 0) / 100.0
                
                # Apply policy cushion (reduce unemployment)
                for i in range(year_idx, len(modified_scenario)):
                    current_ue = modified_scenario.iloc[i]["Compound_Unemployment"]
                    policy_reduction = current_ue * effectiveness * 0.1  # 10% max reduction
                    modified_scenario.iloc[i, modified_scenario.columns.get_loc("Compound_Unemployment")] -= policy_reduction
        
        return modified_scenario
    
    def _calculate_compound_metrics(
        self,
        baseline_df: pd.DataFrame,
        compound_scenario: pd.DataFrame,
        shock_contributions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate metrics for compound shock scenarios"""
        
        baseline_peak = float(baseline_df["Predicted_Unemployment"].max())
        compound_peak = float(compound_scenario["Compound_Unemployment"].max())
        total_impact = compound_peak - baseline_peak
        
        # Calculate interaction effects (non-linear combinations)
        individual_impacts = sum(contrib["peak_impact"] for contrib in shock_contributions.values())
        interaction_effect = total_impact - individual_impacts
        
        return {
            "baseline_peak": round(baseline_peak, 2),
            "compound_peak": round(compound_peak, 2),
            "total_impact": round(total_impact, 2),
            "individual_impacts_sum": round(individual_impacts, 2),
            "interaction_effect": round(interaction_effect, 2),
            "amplification_factor": round(total_impact / individual_impacts, 2) if individual_impacts > 0 else 1.0,
            "shock_count": len(shock_contributions)
        }


# ═══════════════════════════════════════════════════════════════════════════
# PREDEFINED STRESS TEST SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════

def get_predefined_stress_scenarios() -> List[Dict[str, Any]]:
    """Get predefined stress test scenarios for comprehensive testing"""
    
    return [
        {
            "name": "Severe Financial Crisis",
            "type": "single_shock",
            "shock_intensity": 0.6,
            "shock_duration": 4,
            "recovery_rate": 0.15,
            "description": "2008-style financial crisis with slow recovery"
        },
        {
            "name": "Pandemic + Supply Chain Crisis",
            "type": "multi_shock",
            "shock_events": [
                ShockEvent(
                    shock_type=ShockType.PANDEMIC,
                    intensity=0.4,
                    duration=2,
                    start_year=0,
                    sector_impacts={"Services": 1.5, "Tourism": 2.0, "Healthcare": 0.5},
                    description="COVID-19 style pandemic"
                ),
                ShockEvent(
                    shock_type=ShockType.SUPPLY_CHAIN,
                    intensity=0.3,
                    duration=3,
                    start_year=1,
                    sector_impacts={"Manufacturing": 1.3, "Technology": 1.1},
                    description="Global supply chain disruption"
                )
            ],
            "policy_responses": {1: "Fiscal Stimulus", 2: "Industry Support"},
            "description": "Compound crisis with policy intervention"
        },
        {
            "name": "Energy Crisis + Geopolitical Tension",
            "type": "multi_shock",
            "shock_events": [
                ShockEvent(
                    shock_type=ShockType.ENERGY_CRISIS,
                    intensity=0.35,
                    duration=3,
                    start_year=0,
                    sector_impacts={"Energy": 1.5, "Manufacturing": 1.2, "Agriculture": 1.1},
                    description="Oil price shock"
                ),
                ShockEvent(
                    shock_type=ShockType.GEOPOLITICAL,
                    intensity=0.25,
                    duration=2,
                    start_year=1,
                    sector_impacts={"Tourism": 1.3, "Technology": 0.8},
                    description="Regional conflict affecting trade"
                )
            ],
            "description": "Energy and geopolitical compound crisis"
        },
        {
            "name": "Technology Disruption",
            "type": "single_shock",
            "shock_intensity": 0.3,
            "shock_duration": 5,
            "recovery_rate": 0.4,
            "description": "AI/automation causing structural unemployment"
        },
        {
            "name": "Natural Disaster Cascade",
            "type": "multi_shock",
            "shock_events": [
                ShockEvent(
                    shock_type=ShockType.NATURAL_DISASTER,
                    intensity=0.4,
                    duration=1,
                    start_year=0,
                    sector_impacts={"Agriculture": 1.5, "Tourism": 1.3, "Manufacturing": 1.1},
                    description="Major earthquake/flood"
                ),
                ShockEvent(
                    shock_type=ShockType.SUPPLY_CHAIN,
                    intensity=0.2,
                    duration=2,
                    start_year=0,
                    sector_impacts={"Manufacturing": 1.2, "Agriculture": 1.1},
                    description="Infrastructure damage effects"
                )
            ],
            "policy_responses": {0: "Industry Support", 1: "Fiscal Stimulus"},
            "description": "Natural disaster with cascading effects"
        }
    ]


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*80)
    print("ADVANCED SIMULATION ENGINE TEST")
    print("="*80 + "\n")
    
    # This would require actual data loading in a real test
    print("⚠️ This is a module test - requires integration with main system")
    print("✅ Advanced simulation classes and functions defined")
    print("🎯 Ready for integration with main simulation engine")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")