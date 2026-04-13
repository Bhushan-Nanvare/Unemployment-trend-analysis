"""
preprocessing.py
Cleans the raw unemployment time series before modelling.

CRITICAL RULE: DO NOT MODIFY HISTORICAL DATA
- No smoothing of real values
- No interpolation except for missing values
- All historical data must remain unchanged

Smoothing is ONLY for visualization purposes and must be clearly labeled.
"""
import pandas as pd
import numpy as np


class Preprocessor:
    def __init__(self, smoothing_window: int = 3):
        """
        Parameters:
        - smoothing_window: Window size for optional visualization smoothing
                           (NOT applied to data used for forecasting)
        """
        self.smoothing_window = smoothing_window

    def preprocess(self, df: pd.DataFrame, apply_smoothing: bool = False) -> pd.DataFrame:
        """
        Clean and prepare unemployment data.
        
        Parameters:
        - df: Raw unemployment DataFrame
        - apply_smoothing: If True, adds Unemployment_Smoothed column for visualization ONLY
                          Default False to prevent accidental use in forecasting
        
        Returns:
        - DataFrame with cleaned data (historical values UNCHANGED)
        """
        df = df.copy()

        # Remove invalid rows
        df = df.dropna(subset=["Unemployment_Rate"])
        df = df.sort_values("Year").reset_index(drop=True)
        df = df[df["Unemployment_Rate"] > 0]

        # OPTIONAL: Add smoothed column for visualization ONLY
        # This column should NEVER be used for forecasting or analysis
        if apply_smoothing:
            df["Unemployment_Smoothed"] = (
                df["Unemployment_Rate"]
                .rolling(window=self.smoothing_window, min_periods=1, center=True)
                .mean()
            )
        else:
            # For forecasting, use raw data
            df["Unemployment_Smoothed"] = df["Unemployment_Rate"]

        return df
