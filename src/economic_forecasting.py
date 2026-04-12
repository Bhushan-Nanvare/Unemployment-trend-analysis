"""
economic_forecasting.py

Enhanced forecasting engine that incorporates economic relationships:
- Okun's Law (GDP growth → unemployment)
- Phillips Curve (inflation → unemployment)
- Economic fundamentals integration

This provides more realistic forecasts than pure time-series extrapolation.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
from src.live_data import fetch_gdp_growth, _fetch_indicator_series


class EconomicForecastingEngine:
    """
    Forecasting engine that incorporates economic relationships.
    
    Key relationships modeled:
    1. Okun's Law: GDP growth → unemployment change
    2. Phillips Curve: inflation → unemployment (weak in India)
    3. Mean reversion to structural unemployment rate
    """
    
    def __init__(
        self,
        forecast_horizon: int = 5,
        okun_coefficient: float = -0.4,  # India-specific: 1% GDP growth → -0.4% unemployment
        structural_unemployment: float = 4.5,  # India's estimated NAIRU
        phillips_coefficient: float = -0.1,  # Weak Phillips curve in India
    ):
        self.forecast_horizon = forecast_horizon
        self.okun_coefficient = okun_coefficient
        self.structural_unemployment = structural_unemployment
        self.phillips_coefficient = phillips_coefficient
    
    def forecast_with_gdp(
        self, 
        unemployment_df: pd.DataFrame,
        gdp_forecast: Optional[pd.DataFrame] = None,
        inflation_forecast: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Forecast unemployment using GDP growth projections and economic relationships.
        
        Parameters:
        -----------
        unemployment_df : pd.DataFrame
            Historical unemployment data with columns: Year, Unemployment_Rate
        gdp_forecast : pd.DataFrame, optional
            GDP growth forecasts with columns: Year, GDP_Growth
            If None, assumes 6% steady-state growth
        inflation_forecast : pd.DataFrame, optional
            Inflation forecasts with columns: Year, Inflation
            If None, assumes 4% RBI target
            
        Returns:
        --------
        pd.DataFrame with forecasted unemployment incorporating economic relationships
        """
        
        if unemployment_df.empty:
            return pd.DataFrame()
        
        last_year = int(unemployment_df["Year"].max())
        last_unemployment = float(unemployment_df["Unemployment_Rate"].iloc[-1])
        
        # Generate future years
        future_years = list(range(last_year + 1, last_year + 1 + self.forecast_horizon))
        
        # Default GDP growth assumption (India's potential growth)
        if gdp_forecast is None:
            gdp_growth_rates = [6.0] * self.forecast_horizon  # Steady 6% growth
        else:
            gdp_growth_rates = []
            for year in future_years:
                if year in gdp_forecast["Year"].values:
                    rate = gdp_forecast[gdp_forecast["Year"] == year]["GDP_Growth"].iloc[0]
                    gdp_growth_rates.append(float(rate))
                else:
                    gdp_growth_rates.append(6.0)  # Default
        
        # Default inflation assumption (RBI target)
        if inflation_forecast is None:
            inflation_rates = [4.0] * self.forecast_horizon  # RBI target
        else:
            inflation_rates = []
            for year in future_years:
                if year in inflation_forecast["Year"].values:
                    rate = inflation_forecast[inflation_forecast["Year"] == year]["Inflation"].iloc[0]
                    inflation_rates.append(float(rate))
                else:
                    inflation_rates.append(4.0)  # Default
        
        # Forecast unemployment year by year
        forecasted_unemployment = []
        current_unemployment = last_unemployment
        
        for i, (year, gdp_growth, inflation) in enumerate(zip(future_years, gdp_growth_rates, inflation_rates)):
            
            # 1. Okun's Law effect: GDP growth reduces unemployment
            # Okun coefficient is negative: higher GDP growth → lower unemployment
            gdp_effect = self.okun_coefficient * (gdp_growth - 6.0)  # Relative to 6% potential
            
            # 2. Phillips Curve effect (weak in India)
            # Higher inflation slightly reduces unemployment (short-term)
            phillips_effect = self.phillips_coefficient * (inflation - 4.0)  # Relative to 4% target
            
            # 3. Mean reversion to structural unemployment
            # Unemployment tends to return to its natural rate over time
            gap = current_unemployment - self.structural_unemployment
            reversion_effect = -0.2 * gap  # 20% of gap closes each year
            
            # 4. Combine effects
            unemployment_change = gdp_effect + phillips_effect + reversion_effect
            
            # 5. Apply bounds and update
            new_unemployment = current_unemployment + unemployment_change
            new_unemployment = max(1.0, min(15.0, new_unemployment))  # Reasonable bounds
            
            forecasted_unemployment.append(new_unemployment)
            current_unemployment = new_unemployment
        
        # Create forecast DataFrame
        forecast_df = pd.DataFrame({
            "Year": future_years,
            "Predicted_Unemployment": [round(u, 3) for u in forecasted_unemployment],
            "GDP_Growth_Used": gdp_growth_rates,
            "Inflation_Used": inflation_rates,
        })
        
        return forecast_df
    
    def generate_gdp_scenarios(self) -> dict:
        """
        Generate different GDP growth scenarios for sensitivity analysis.
        
        Returns:
        --------
        dict with scenario names and GDP growth paths
        """
        # Base scenarios for first 5 years
        base_scenarios = {
            "Optimistic": [7.5, 7.8, 8.0, 7.5, 7.0],  # High growth
            "Baseline": [6.0, 6.2, 6.5, 6.3, 6.0],    # Potential growth
            "Pessimistic": [4.0, 4.5, 5.0, 5.2, 5.5], # Slow growth
            "Recession": [1.0, 2.0, 4.0, 5.0, 6.0],   # Recovery path
        }
        
        # Extend scenarios to match forecast_horizon
        scenarios = {}
        for name, base_path in base_scenarios.items():
            if self.forecast_horizon <= len(base_path):
                # Truncate if forecast horizon is shorter
                scenarios[name] = base_path[:self.forecast_horizon]
            else:
                # Extend if forecast horizon is longer
                extended_path = base_path.copy()
                last_value = base_path[-1]
                # Gradually converge to long-term potential growth (6%)
                for i in range(len(base_path), self.forecast_horizon):
                    convergence_factor = 0.8  # 80% weight on previous value, 20% on 6%
                    next_value = convergence_factor * last_value + 0.2 * 6.0
                    extended_path.append(round(next_value, 1))
                    last_value = next_value
                scenarios[name] = extended_path
        
        return scenarios
    
    def forecast_multiple_scenarios(
        self, 
        unemployment_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate unemployment forecasts under different GDP scenarios.
        
        Returns:
        --------
        pd.DataFrame with columns: Year, Scenario, Predicted_Unemployment, GDP_Growth
        """
        scenarios = self.generate_gdp_scenarios()
        all_forecasts = []
        
        last_year = int(unemployment_df["Year"].max())
        future_years = list(range(last_year + 1, last_year + 1 + self.forecast_horizon))
        
        for scenario_name, gdp_path in scenarios.items():
            # Ensure GDP path matches forecast horizon
            if len(gdp_path) != self.forecast_horizon:
                # This should not happen with the fixed generate_gdp_scenarios, but safety check
                if len(gdp_path) > self.forecast_horizon:
                    gdp_path = gdp_path[:self.forecast_horizon]
                else:
                    # Extend with last value if needed
                    while len(gdp_path) < self.forecast_horizon:
                        gdp_path.append(gdp_path[-1])
            
            # Ensure arrays have same length
            assert len(future_years) == len(gdp_path), f"Length mismatch: years={len(future_years)}, gdp={len(gdp_path)}"
            
            # Create GDP forecast DataFrame
            gdp_df = pd.DataFrame({
                "Year": future_years,
                "GDP_Growth": gdp_path
            })
            
            # Generate unemployment forecast
            forecast = self.forecast_with_gdp(unemployment_df, gdp_df)
            
            # Add scenario info
            forecast["Scenario"] = scenario_name
            forecast["GDP_Growth"] = gdp_path
            all_forecasts.append(forecast)
        
        # Combine all scenarios
        combined_df = pd.concat(all_forecasts, ignore_index=True)
        return combined_df[["Year", "Scenario", "Predicted_Unemployment", "GDP_Growth"]]
    
    @staticmethod
    def estimate_okun_coefficient(unemployment_df: pd.DataFrame, gdp_df: pd.DataFrame) -> float:
        """
        Estimate Okun's coefficient from historical data.
        
        Returns the coefficient relating GDP growth to unemployment change.
        """
        # Merge data
        merged = pd.merge(unemployment_df, gdp_df, on="Year", how="inner")
        if len(merged) < 10:
            return -0.4  # Default for India
        
        # Calculate unemployment change
        merged = merged.sort_values("Year")
        merged["UE_Change"] = merged["Unemployment_Rate"].diff()
        merged["GDP_Growth"] = merged["Value"] if "Value" in merged.columns else merged["GDP_Growth"]
        
        # Remove outliers (COVID, etc.)
        merged = merged[(merged["UE_Change"].abs() < 3) & (merged["GDP_Growth"] > -5)]
        
        if len(merged) < 5:
            return -0.4
        
        # Simple regression: UE_Change = alpha + beta * GDP_Growth
        from scipy.stats import linregress
        slope, intercept, r_value, p_value, std_err = linregress(
            merged["GDP_Growth"], merged["UE_Change"]
        )
        
        # Okun coefficient should be negative (higher GDP → lower unemployment)
        return min(-0.1, slope)  # Ensure it's negative and reasonable


def create_economic_forecast_demo():
    """
    Demo function showing how to use economic forecasting.
    """
    from src.live_data import fetch_world_bank, fetch_gdp_growth
    
    # Load data
    unemployment_df = fetch_world_bank("India")
    gdp_df = fetch_gdp_growth("India")
    
    if unemployment_df.empty or gdp_df.empty:
        print("Could not fetch data for demo")
        return
    
    # Estimate India-specific Okun coefficient
    engine = EconomicForecastingEngine()
    okun_coef = engine.estimate_okun_coefficient(unemployment_df, gdp_df)
    print(f"Estimated Okun coefficient for India: {okun_coef:.3f}")
    
    # Create engine with estimated coefficient
    engine = EconomicForecastingEngine(okun_coefficient=okun_coef)
    
    # Generate scenario forecasts
    scenario_forecasts = engine.forecast_multiple_scenarios(unemployment_df)
    print("\nUnemployment forecasts under different GDP scenarios:")
    print(scenario_forecasts.pivot(index="Year", columns="Scenario", values="Predicted_Unemployment"))
    
    return scenario_forecasts


if __name__ == "__main__":
    create_economic_forecast_demo()