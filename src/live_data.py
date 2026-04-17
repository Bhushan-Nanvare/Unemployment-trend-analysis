"""
live_data.py
Offline data access layer.

This project previously fetched live time series from the World Bank Open API.
For Streamlit Cloud reliability (network/rate-limit variability), we now run in
offline-only mode and load curated local CSVs bundled with the repo.
"""
import time
import pandas as pd
from pathlib import Path
from typing import Optional

WB_API = "https://api.worldbank.org/v2/country/{iso}/indicator/SL.UEM.TOTL.ZS"
WB_INDICATOR_API = "https://api.worldbank.org/v2/country/{iso}/indicator/{indicator}"
FALLBACK_CSV = Path("data/raw/india_unemployment.csv")
COUNTRY_ISO = {"India": "IN"}

# Disable all live HTTP calls (Streamlit Cloud reliability).
OFFLINE_ONLY = True

# ── World Bank sector indicators ───────────────────────────────────────────────
# These three sector categories (Agriculture, Industry, Services) are the standard
# World Bank / ILO breakdown available for India.
# Manufacturing is a sub-component of Industry and has its own dedicated series.
SECTOR_INDICATORS = {
    "Agriculture": {
        "employment": "SL.AGR.EMPL.ZS",   # % of total employment
        "gdp":        "NV.AGR.TOTL.ZS",   # % of GDP
    },
    "Industry": {
        "employment": "SL.IND.EMPL.ZS",
        "gdp":        "NV.IND.TOTL.ZS",
    },
    "Manufacturing": {
        "employment": None,                # ILO sub-series not available via WB
        "gdp":        "NV.IND.MANF.ZS",   # % of GDP
    },
    "Services": {
        "employment": "SL.SRV.EMPL.ZS",
        "gdp":        "NV.SRV.TOTL.ZS",
    },
    "Construction": {
        "employment": None,
        "gdp":        None,   # Not available for India via World Bank API
    },
}

# World Bank unemployment data is updated annually.
# Cache entries expire after 24 hours so a long-running server
# eventually refreshes rather than serving indefinitely stale data.
_CACHE_TTL_SECONDS = 86_400   # 24 hours

_cache: dict = {}          # key → {"df": pd.DataFrame, "ts": float}


def fetch_world_bank(country: str = "India", per_page: int = 65) -> pd.DataFrame:
    """
    Offline-only: pulls unemployment rate from realistic local data.
    Returns DataFrame with columns: Year (int), Unemployment_Rate (float).
    """
    iso = COUNTRY_ISO.get(country, "IN")
    cache_key = f"{country}_{per_page}"

    entry = _cache.get(cache_key)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL_SECONDS:
        return entry["df"]

    # Use realistic local data
    realistic_df = _load_fallback(country)
    if not realistic_df.empty and len(realistic_df) >= 20:
        # Use realistic data if it has sufficient coverage
        _cache[cache_key] = {"df": realistic_df, "ts": time.time()}
        return realistic_df

    return realistic_df


def _load_fallback(country: str = "India") -> pd.DataFrame:
    """Load local CSV as fallback when API is unavailable."""
    try:
        # First try the realistic India unemployment data
        realistic_path = Path("data/raw/india_unemployment_realistic.csv")
        if realistic_path.exists():
            df = pd.read_csv(realistic_path)
            if "Year" in df.columns and "Unemployment_Rate" in df.columns:
                return df[["Year", "Unemployment_Rate"]].dropna()
        
        # Fallback to original data loader
        from src.data_loader import DataLoader
        df = DataLoader(str(FALLBACK_CSV), country).load_clean_data()
        return df
    except Exception:
        return pd.DataFrame(columns=["Year", "Unemployment_Rate"])


def get_data_source_label(country: str = "India") -> str:
    """Describe the current data mode (offline-only)."""
    realistic_path = Path("data/raw/india_unemployment_realistic.csv")
    if realistic_path.exists():
        return "🟡 Offline — Curated local CSV (no live API)"
    return "🟡 Offline — Local CSV (no live API)"


def clear_cache() -> None:
    """Evict all cached entries (useful in tests or when forcing a refresh)."""
    _cache.clear()


# ── Live labor market indicators (time series) ──────────────────────────────────

LABOR_MARKET_INDICATORS = {
    "Unemployment Rate (%)":          "SL.UEM.TOTL.ZS",
    "Youth Unemployment 15-24 (%)":   "SL.UEM.1524.ZS",
    "Female Unemployment (%)":        "SL.UEM.TOTL.FE.ZS",
    "Male Unemployment (%)":          "SL.UEM.TOTL.MA.ZS",
    "Labor Force Participation (%)":  "SL.TLF.CACT.ZS",
    "Employment-to-Population (%)":   "SL.EMP.TOTL.SP.ZS",
    "Vulnerable Employment (%)":      "SL.EMP.VULN.ZS",
    "Long-Term Unemployment (%)":     "SL.UEM.LTRM.ZS",
}


def _fetch_indicator_series(
    indicator: str,
    iso: str = "IN",
    per_page: int = 40,
) -> pd.DataFrame:
    """
    Fetch the full time-series for a single World Bank indicator.
    Returns DataFrame with columns: Year (int), Value (float).
    Returns empty DataFrame on any error.
    """
    if OFFLINE_ONLY:
        return pd.DataFrame(columns=["Year", "Value"])
    url = WB_INDICATOR_API.format(iso=iso, indicator=indicator)
    params = {"format": "json", "per_page": per_page, "mrv": per_page}
    try:
        import requests
        resp = requests.get(url, params=params, timeout=12)
        resp.raise_for_status()
        data = resp.json()
        if not data or len(data) < 2 or not data[1]:
            return pd.DataFrame(columns=["Year", "Value"])
        records = []
        for entry in data[1]:
            yr  = entry.get("date")
            val = entry.get("value")
            if yr and val is not None:
                try:
                    records.append({"Year": int(yr), "Value": round(float(val), 3)})
                except (ValueError, TypeError):
                    continue
        if not records:
            return pd.DataFrame(columns=["Year", "Value"])
        return (
            pd.DataFrame(records)
            .sort_values("Year")
            .dropna()
            .reset_index(drop=True)
        )
    except Exception:
        return pd.DataFrame(columns=["Year", "Value"])


def fetch_gdp_growth(country: str = "India", per_page: int = 35) -> pd.DataFrame:
    """
    Fetch GDP growth rate (NY.GDP.MKTP.KD.ZG) time series for a country.
    Returns DataFrame with columns: Year (int), Value (float).
    Retries once on timeout.
    """
    iso = COUNTRY_ISO.get(country, "IN")
    cache_key = f"gdp_growth_{country}"
    entry = _cache.get(cache_key)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL_SECONDS:
        return entry["df"]

    if OFFLINE_ONLY:
        return pd.DataFrame(columns=["Year", "Value"])
    for attempt in range(2):
        df = _fetch_indicator_series("NY.GDP.MKTP.KD.ZG", iso=iso, per_page=per_page)
        if not df.empty:
            _cache[cache_key] = {"df": df, "ts": time.time()}
            return df
        time.sleep(1)
    return pd.DataFrame(columns=["Year", "Value"])


def fetch_labor_market_pulse(country: str = "India") -> dict:
    """
    Fetch time-series data for all key Indian labor market indicators.

    Returns:
        dict mapping indicator_label → pd.DataFrame(Year, Value)
    Uses a 24-hour cache to avoid hammering the World Bank API.
    """
    cache_key = f"labor_market_pulse_{country}"
    entry = _cache.get(cache_key)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL_SECONDS:
        return entry["df"]

    # Offline-only: provide what we have locally.
    # We can always provide the unemployment series from the bundled CSV.
    result = {}
    if country.lower() == "india":
        ue = fetch_world_bank("India")
        if ue is not None and not ue.empty:
            result["Unemployment Rate (%)"] = ue.rename(
                columns={"Unemployment_Rate": "Value"}
            )[["Year", "Value"]].copy()
    if result:
        _cache[cache_key] = {"df": result, "ts": time.time()}
    return result


# ── Live sector data ───────────────────────────────────────────────────────────

def _fetch_single_indicator(
    indicator: str,
    iso: str = "IN",
    mrv: int = 10,
) -> Optional[float]:
    """
    Pull the most-recent non-null value for a single World Bank indicator.
    Returns the value as a float, or None if unavailable.
    We ask for up to `mrv` most-recent values and take the first non-null one,
    because some series have a 1-2 year reporting lag.
    """
    if OFFLINE_ONLY:
        return None
    url = WB_INDICATOR_API.format(iso=iso, indicator=indicator)
    params = {"format": "json", "mrv": mrv}
    try:
        import requests
        resp = requests.get(url, params=params, timeout=25)
        resp.raise_for_status()
        data = resp.json()
        if not data or len(data) < 2 or not data[1]:
            return None
        for entry in data[1]:
            val = entry.get("value")
            if val is not None:
                return float(val)
    except Exception:
        pass
    return None


def fetch_sector_indicators(country: str = "India") -> pd.DataFrame:
    """
    Fetch the latest World Bank sector employment-share and GDP-share figures
    for India and return a tidy DataFrame.

    Columns:
        Sector              — sector name
        Employment_Share    — % of total employment (float or NaN)
        GDP_Share           — % of GDP (float or NaN)
        Source              — "World Bank (live)" or "Unavailable"

    Falls back gracefully: if an indicator is unavailable its column is NaN.
    The entire function never raises — worst case it returns an empty DataFrame.
    """
    cache_key = f"sector_indicators_{country}"
    entry = _cache.get(cache_key)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL_SECONDS:
        return entry["df"]

    if OFFLINE_ONLY:
        return pd.DataFrame(columns=["Sector", "Employment_Share", "GDP_Share", "Source"])

    iso = COUNTRY_ISO.get(country, "IN")
    rows = []
    any_live = False

    for sector, codes in SECTOR_INDICATORS.items():
        emp_code = codes.get("employment")
        gdp_code = codes.get("gdp")

        emp_val = _fetch_single_indicator(emp_code, iso) if emp_code else None
        gdp_val = _fetch_single_indicator(gdp_code, iso) if gdp_code else None

        if emp_val is not None or gdp_val is not None:
            any_live = True

        rows.append({
            "Sector":           sector,
            "Employment_Share": round(emp_val, 2) if emp_val is not None else float("nan"),
            "GDP_Share":        round(gdp_val, 2) if gdp_val is not None else float("nan"),
            "Source":           "World Bank (live)" if (emp_val or gdp_val) else "Unavailable",
        })

    if not rows:
        return pd.DataFrame(columns=["Sector", "Employment_Share", "GDP_Share", "Source"])

    df = pd.DataFrame(rows)
    if any_live:
        _cache[cache_key] = {"df": df, "ts": time.time()}
    return df


# ── India state-level unemployment (PLFS 2022-23 curated) ─────────────────────
# Source: Annual Report of Periodic Labour Force Survey (PLFS) 2022-23,
# Ministry of Statistics & Programme Implementation, Government of India.
# Usual Principal Status (UPS) unemployment rate (%), 15+ years.
# State-level data is NOT available on World Bank API — this is curated from
# official MOSPI PLFS reports and is updated when a new annual report is released.

_PLFS_STATE_DATA = [
    {"State": "Jammu & Kashmir",    "Urban_UE": 18.7, "Rural_UE": 5.2,  "Combined_UE": 9.8,  "Region": "North"},
    {"State": "Himachal Pradesh",   "Urban_UE": 8.0,  "Rural_UE": 2.5,  "Combined_UE": 3.5,  "Region": "North"},
    {"State": "Punjab",             "Urban_UE": 8.4,  "Rural_UE": 3.8,  "Combined_UE": 5.4,  "Region": "North"},
    {"State": "Uttarakhand",        "Urban_UE": 7.3,  "Rural_UE": 3.1,  "Combined_UE": 4.5,  "Region": "North"},
    {"State": "Haryana",            "Urban_UE": 11.3, "Rural_UE": 5.2,  "Combined_UE": 7.4,  "Region": "North"},
    {"State": "Rajasthan",          "Urban_UE": 9.5,  "Rural_UE": 2.9,  "Combined_UE": 4.8,  "Region": "West"},
    {"State": "Uttar Pradesh",      "Urban_UE": 8.2,  "Rural_UE": 3.5,  "Combined_UE": 4.9,  "Region": "North"},
    {"State": "Bihar",              "Urban_UE": 9.1,  "Rural_UE": 2.2,  "Combined_UE": 3.7,  "Region": "East"},
    {"State": "Sikkim",             "Urban_UE": 4.3,  "Rural_UE": 2.0,  "Combined_UE": 2.8,  "Region": "Northeast"},
    {"State": "Arunachal Pradesh",  "Urban_UE": 7.8,  "Rural_UE": 3.1,  "Combined_UE": 4.3,  "Region": "Northeast"},
    {"State": "Nagaland",           "Urban_UE": 18.6, "Rural_UE": 7.1,  "Combined_UE": 9.6,  "Region": "Northeast"},
    {"State": "Manipur",            "Urban_UE": 11.7, "Rural_UE": 5.6,  "Combined_UE": 7.3,  "Region": "Northeast"},
    {"State": "Mizoram",            "Urban_UE": 4.1,  "Rural_UE": 2.3,  "Combined_UE": 3.1,  "Region": "Northeast"},
    {"State": "Tripura",            "Urban_UE": 8.6,  "Rural_UE": 4.8,  "Combined_UE": 6.1,  "Region": "Northeast"},
    {"State": "Meghalaya",          "Urban_UE": 11.2, "Rural_UE": 3.8,  "Combined_UE": 5.7,  "Region": "Northeast"},
    {"State": "Assam",              "Urban_UE": 12.3, "Rural_UE": 3.6,  "Combined_UE": 5.9,  "Region": "Northeast"},
    {"State": "West Bengal",        "Urban_UE": 6.8,  "Rural_UE": 4.5,  "Combined_UE": 5.3,  "Region": "East"},
    {"State": "Jharkhand",          "Urban_UE": 8.3,  "Rural_UE": 3.3,  "Combined_UE": 4.8,  "Region": "East"},
    {"State": "Odisha",             "Urban_UE": 8.1,  "Rural_UE": 2.5,  "Combined_UE": 3.6,  "Region": "East"},
    {"State": "Chhattisgarh",       "Urban_UE": 5.6,  "Rural_UE": 1.8,  "Combined_UE": 2.8,  "Region": "Central"},
    {"State": "Madhya Pradesh",     "Urban_UE": 7.4,  "Rural_UE": 2.1,  "Combined_UE": 3.4,  "Region": "Central"},
    {"State": "Gujarat",            "Urban_UE": 4.1,  "Rural_UE": 1.5,  "Combined_UE": 2.3,  "Region": "West"},
    {"State": "Maharashtra",        "Urban_UE": 4.8,  "Rural_UE": 2.3,  "Combined_UE": 3.4,  "Region": "West"},
    {"State": "Andhra Pradesh",     "Urban_UE": 5.4,  "Rural_UE": 3.6,  "Combined_UE": 4.2,  "Region": "South"},
    {"State": "Karnataka",          "Urban_UE": 4.2,  "Rural_UE": 1.8,  "Combined_UE": 2.8,  "Region": "South"},
    {"State": "Goa",                "Urban_UE": 5.3,  "Rural_UE": 1.8,  "Combined_UE": 3.7,  "Region": "West"},
    {"State": "Kerala",             "Urban_UE": 8.9,  "Rural_UE": 6.8,  "Combined_UE": 7.6,  "Region": "South"},
    {"State": "Tamil Nadu",         "Urban_UE": 5.1,  "Rural_UE": 3.8,  "Combined_UE": 4.4,  "Region": "South"},
    {"State": "Telangana",          "Urban_UE": 5.6,  "Rural_UE": 3.1,  "Combined_UE": 4.2,  "Region": "South"},
    {"State": "Delhi",              "Urban_UE": 8.4,  "Rural_UE": None, "Combined_UE": 8.4,  "Region": "North"},
]


def get_state_unemployment() -> pd.DataFrame:
    """
    Return curated PLFS 2022-23 state-level unemployment rate data for India.
    Columns: State, Urban_UE, Rural_UE, Combined_UE, Region.

    Data source: PLFS Annual Report 2022-23, MOSPI (Government of India).
    """
    df = pd.DataFrame(_PLFS_STATE_DATA)
    df["Urban_UE"]    = pd.to_numeric(df["Urban_UE"], errors="coerce")
    df["Rural_UE"]    = pd.to_numeric(df["Rural_UE"], errors="coerce")
    df["Combined_UE"] = pd.to_numeric(df["Combined_UE"], errors="coerce")
    return df.sort_values("Combined_UE", ascending=False).reset_index(drop=True)
