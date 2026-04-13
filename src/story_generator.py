"""
story_generator.py
Generates intelligent, data-driven narrative timeline from scenario vs baseline data.

ENHANCED: Version 7.0.0
- Intelligent economic interpretation
- Trend analysis (increasing/decreasing)
- Phase transitions (shock → recovery → stabilization)
- Evidence-based reasoning
- No external causes or assumptions

Fix: Peak year check now runs BEFORE the year-0 stable default, so if the
shock peaks at year 0 it is correctly labelled as a shock event.
"""
import pandas as pd


class StoryGenerator:

    @staticmethod
    def generate_story(scenario_df: pd.DataFrame, baseline_df: pd.DataFrame) -> list:
        """
        Returns a list of story event dicts with keys:
          year, title, body, type, scenario_val, baseline_val, delta
        type is one of: 'shock', 'recovery', 'stable'
        
        ENHANCED: Now includes intelligent interpretation based on:
        - Unemployment value and trend
        - Distance from baseline
        - Change from previous year
        - Phase identification (peak, declining, stabilizing)
        """
        merged = pd.merge(baseline_df, scenario_df, on="Year", how="inner")
        merged["Delta"] = merged["Scenario_Unemployment"] - merged["Predicted_Unemployment"]

        story = []
        peak_idx = merged["Scenario_Unemployment"].idxmax()
        
        # Calculate trends for intelligent interpretation
        merged["Trend"] = merged["Scenario_Unemployment"].diff()

        for i, row in merged.iterrows():
            year = int(row["Year"])
            delta = row["Delta"]
            scenario_val = round(row["Scenario_Unemployment"], 2)
            baseline_val = round(row["Predicted_Unemployment"], 2)
            trend = row["Trend"] if pd.notna(row["Trend"]) else 0
            
            # Get previous year value for comparison
            prev_val = merged.iloc[i-1]["Scenario_Unemployment"] if i > 0 else scenario_val
            
            # Determine trend direction
            is_increasing = trend > 0.05
            is_decreasing = trend < -0.05
            is_stable_trend = abs(trend) <= 0.05
            
            # Determine position relative to baseline
            is_peak = (i == peak_idx and delta > 0.3)
            is_high_above = delta > 0.8
            is_above = delta > 0.3
            is_near_baseline = abs(delta) <= 0.3
            
            # Generate intelligent interpretation
            if is_peak:
                event_type = "shock"
                title = f"{year}: Peak Unemployment Shock"
                
                # Intelligent interpretation for peak
                body = (
                    f"Unemployment peaks at {scenario_val}% — {round(delta, 2)}pp above baseline ({baseline_val}%). "
                    f"This represents maximum stress on labor markets, indicating the most severe phase of economic disruption. "
                )
                
                if is_increasing:
                    body += "The upward trajectory suggests intensifying pressure on employment conditions."
                else:
                    body += "While at peak levels, the trend suggests this may mark a turning point."
                    
            elif is_high_above and is_increasing:
                event_type = "shock"
                title = f"{year}: Intensifying Stress"
                
                body = (
                    f"Unemployment rises to {scenario_val}%, now {round(delta, 2)}pp above baseline ({baseline_val}%). "
                    f"The {round(abs(trend), 2)}pp increase from {round(prev_val, 2)}% indicates escalating labor market stress. "
                    f"This upward momentum suggests the shock phase continues to deepen."
                )
                
            elif is_above and is_decreasing:
                event_type = "recovery"
                title = f"{year}: Recovery Momentum"
                
                body = (
                    f"Unemployment declines to {scenario_val}%, though still {round(delta, 2)}pp above baseline ({baseline_val}%). "
                    f"The {round(abs(trend), 2)}pp decrease from {round(prev_val, 2)}% suggests early recovery momentum is building. "
                )
                
                if delta > 0.5:
                    body += "However, elevated stress remains, indicating recovery is in early stages."
                else:
                    body += "The narrowing gap indicates gradual convergence toward baseline conditions."
                    
            elif is_above and is_stable_trend:
                event_type = "shock"
                title = f"{year}: Persistent Elevation"
                
                body = (
                    f"Unemployment remains at {scenario_val}%, {round(delta, 2)}pp above baseline ({baseline_val}%). "
                    f"The stable trend at elevated levels suggests labor market stress persists without significant improvement. "
                    f"This plateau phase reflects ongoing adjustment pressures."
                )
                
            elif is_near_baseline and is_decreasing:
                event_type = "recovery"
                title = f"{year}: Approaching Stabilization"
                
                body = (
                    f"Unemployment eases to {scenario_val}%, converging toward baseline ({baseline_val}%) with only {round(delta, 2)}pp gap. "
                    f"The declining trend indicates recovery is advancing, with labor market conditions approaching pre-shock levels. "
                    f"This convergence suggests stabilization is near."
                )
                
            elif is_near_baseline and is_stable_trend:
                event_type = "stable"
                title = f"{year}: Stabilization Achieved"
                
                body = (
                    f"Unemployment stabilizes at {scenario_val}%, closely aligned with baseline ({baseline_val}%). "
                    f"The minimal {round(abs(delta), 2)}pp gap and stable trend indicate labor market equilibrium has been restored. "
                    f"This reflects successful absorption of the economic shock."
                )
                
            elif i == 0:
                # Year-0 baseline
                event_type = "stable"
                title = f"{year}: Economic Baseline"
                
                body = (
                    f"Unemployment stands at {scenario_val}%, closely tracking the baseline of {baseline_val}%. "
                    f"This represents the pre-shock equilibrium state of the labor market."
                )
                
            else:
                # Default case
                event_type = "stable"
                title = f"{year}: Continued Stability"
                
                body = (
                    f"Unemployment at {scenario_val}%, maintaining near-baseline levels ({baseline_val}%). "
                    f"The sustained stability suggests recovery has been consolidated."
                )

            story.append({
                "year": year,
                "title": title,
                "body": body,
                "type": event_type,
                "scenario_val": scenario_val,
                "baseline_val": baseline_val,
                "delta": round(delta, 2),
                "trend": round(trend, 2) if pd.notna(trend) else 0,
            })

        return story
