"""
Converts the Naukri.com Kaggle dataset into the format expected by the app.
Run from the san/ directory:
    python scripts/convert_naukri_dataset.py
"""
import re
import pandas as pd
from pathlib import Path

SRC = Path("marketing_sample_for_naukri_com-jobs__20190701_20190830__30k_data.csv")
DST = Path("data/market_pulse/job_postings_sample.csv")


def parse_salary(salary_str: str):
    """
    Extract min/max LPA from strings like:
      '3,00,000 - 6,00,000 PA'  → 3.0, 6.0
      '10 - 15 LPA'             → 10.0, 15.0
      'Not Disclosed...'        → None, None
    """
    if not salary_str or not isinstance(salary_str, str):
        return None, None
    s = salary_str.replace(",", "").upper()
    nums = re.findall(r"[\d]+(?:\.\d+)?", s)
    if len(nums) < 2:
        return None, None
    lo, hi = float(nums[0]), float(nums[1])
    # If values look like annual rupees (e.g. 300000), convert to LPA
    if lo > 1000:
        lo = round(lo / 100000, 2)
        hi = round(hi / 100000, 2)
    return lo, hi


def main():
    print(f"Reading {SRC} ...")
    df = pd.read_csv(SRC, low_memory=False)
    print(f"  {len(df):,} rows loaded")

    out = pd.DataFrame()

    # post_date — use crawl timestamp, keep date part only
    out["post_date"] = pd.to_datetime(
        df["Crawl Timestamp"], errors="coerce"
    ).dt.date.astype(str)

    out["job_title"] = df["Job Title"].fillna("").astype(str).str.strip()

    # description — combine Key Skills + Functional Area + Role
    out["description"] = (
        df["Key Skills"].fillna("").astype(str)
        + " "
        + df["Functional Area"].fillna("").astype(str)
        + " "
        + df["Role"].fillna("").astype(str)
        + " "
        + df["Industry"].fillna("").astype(str)
    ).str.lower().str.strip()

    # location — take first city before comma
    out["location"] = (
        df["Location"].fillna("").astype(str)
        .str.split(",").str[0]
        .str.strip()
    )

    # salary
    salary_parsed = df["Job Salary"].apply(parse_salary)
    out["salary_min_lpa"] = [x[0] for x in salary_parsed]
    out["salary_max_lpa"] = [x[1] for x in salary_parsed]

    # Drop rows with no title or date
    out = out[out["job_title"] != ""].dropna(subset=["post_date"])
    out = out[out["post_date"] != "NaT"]

    DST.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(DST, index=False)
    print(f"  Saved {len(out):,} rows → {DST}")
    print("Done. Restart the app to see real data.")


if __name__ == "__main__":
    main()
