import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
from config import INTERM_DIR, FINAL_DIR, CUTOFFS, WINDOW_WEEKS, DONUT_WEEKS
from utils import get_weeks_since

def process_cutoff(name, date, pypi_base, gh_agg, pypi_max, gh_max):
    # 1. Merge PyPI and GitHub
    df = pypi_base.merge(gh_agg, on="package", how="left", indicator="gh_merge_status")
    df["matched_to_github"] = (df["gh_merge_status"] == "both").astype(int)
    
    # Track matching stats before filtering
    n_pypi = len(pypi_base)
    n_matched = df["matched_to_github"].sum()
    
    df = df.drop(columns=["gh_merge_status"])

    # Keep imports as missing for unmatched packages (don't fillna(0))
    if "avg_ai_score_52wk" not in df.columns:
        df["avg_ai_score_52wk"] = np.nan

    # 2. Running variable
    df["dist_to_cutoff"] = get_weeks_since(df["release_week"], date)
    df["is_pre_cutoff"] = (df["dist_to_cutoff"] < 0).astype(int)
    
    # Wide Donut (e.g. Aug & Sept)
    df["in_donut"] = df["dist_to_cutoff"].isin(DONUT_WEEKS).astype(int)

    # 3. Time Filtering (Bandwidth)
    n_before_time = len(df)
    df = df.loc[(df["dist_to_cutoff"] >= -WINDOW_WEEKS) & (df["dist_to_cutoff"] <= WINDOW_WEEKS)].copy()
    
    # Relaxing age-censoring: For Sept 2021 cutoff, all within WINDOW_WEEKS 
    # already have data up to the current data max (Jan 2026).
    n_after_time = len(df)

    # Note: MIN_DOWNLOADS_52WK filter removed from main dataset to avoid selection bias.
    # It will be applied as a sensitivity check in estimation scripts.
    
    return df, {
        "n_pypi": n_pypi, 
        "n_matched": int(df["matched_to_github"].sum()), 
        "n_final": len(df), 
        "n_time_drop": n_before_time - n_after_time,
        "match_rate": df["matched_to_github"].mean()
    }

def main() -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    pypi_base = pd.read_parquet(INTERM_DIR / "pypi_base.parquet")
    gh_agg = pd.read_parquet(INTERM_DIR / "github_agg.parquet")
    pypi_meta = pd.read_parquet(INTERM_DIR / "pypi_meta.parquet")
    gh_meta = pd.read_parquet(INTERM_DIR / "github_meta.parquet")

    pypi_max = pd.to_datetime(pypi_meta.loc[0, "max_week_start"])
    gh_max = pd.to_datetime(gh_meta.loc[0, "max_week_start"])

    summaries = []
    for name, date in CUTOFFS.items():
        print(f"Processing {name} at {date.date()}...")
        df_final, stats = process_cutoff(name, date, pypi_base, gh_agg, pypi_max, gh_max)
        
        out_path = FINAL_DIR / f"analysis_{name}.csv"
        df_final.to_csv(out_path, index=False)
        
        stats["cutoff"] = name
        summaries.append(stats)
        print(f"  Saved {len(df_final):,} rows to {out_path.name}")

    # Save matching and attrition summary
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(FINAL_DIR / "matching_summary.csv", index=False)
    print(f"Saved matching summary to {FINAL_DIR / 'matching_summary.csv'}")

if __name__ == "__main__":
    main()
