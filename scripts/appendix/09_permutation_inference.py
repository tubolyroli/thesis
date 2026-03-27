import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from config import INTERM_DIR, RESULTS_DIR, FIGURES_DIR, DONUT_WEEKS, WINDOW_WEEKS, HORIZON_WEEKS
from utils import get_weeks_since, run_local_linear_rdd, setup_plotting_style

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    setup_plotting_style()

    # 1. Load and Merge Data
    print("Loading data for permutation inference...")
    pypi_base = pd.read_parquet(INTERM_DIR / "pypi_base.parquet")
    pypi_meta = pd.read_parquet(INTERM_DIR / "pypi_meta.parquet")
    pypi_max = pd.to_datetime(pypi_meta.loc[0, "max_week_start"])

    # 2. Define the Range of Placebo Mondays
    # We need a window where we have both 52 weeks of pre-data and 52 weeks of post-data (bandwidth),
    # plus 52 weeks of follow-up (horizon) for the last package in the post-data.
    # Start: min_week + 52 weeks
    # End: pypi_max - 52 weeks (bandwidth) - 52 weeks (horizon)
    start_date = pypi_base["release_week"].min() + pd.to_timedelta(WINDOW_WEEKS * 7, unit="D")
    end_date = pypi_max - pd.to_timedelta((WINDOW_WEEKS + HORIZON_WEEKS) * 7, unit="D")
    
    all_mondays = pd.date_range(start=start_date, end=end_date, freq="W-MON")
    print(f"Running permutation inference across {len(all_mondays)} Mondays...")
    print(f"Range: {start_date.date()} to {end_date.date()}")

    true_cutoff = pd.Timestamp("2021-09-27")
    results = []

    # 3. Iterative RDD Estimation
    # Outcome: log(1+downloads)
    # Bandwidth: 26 weeks (h=26)
    # Donut: Yes (matching baseline)
    print("--- APPENDIX: Approximate Placebo-Ranking Exercise ---")
    print("NOTE: Using WLS + HC1 for speed in the permutation test (366 iterations).")
    print("Statistical significance is derived from the non-parametric distribution of coefficients.")
    for i, m in enumerate(all_mondays):
        # Calculate running variable for this specific Monday
        df = pypi_base.copy()
        df["dist_to_cutoff"] = get_weeks_since(df["release_week"], m)
        
        # Simple RDD call (using WLS HC1 for speed in permutation)
        res = run_local_linear_rdd(df, "total_downloads_52wk", h=26, donut_weeks=DONUT_WEEKS, label=str(m.date()), cluster_col=None)
        res["cutoff_date"] = m
        res["is_true_cutoff"] = (m == true_cutoff)
        results.append(res)
        
        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(all_mondays)} Mondays...")

    perm_df = pd.DataFrame(results).dropna(subset=["Estimate"])
    perm_df.to_csv(RESULTS_DIR / "permutation_results.csv", index=False)

    # 4. Analysis of the Distribution
    true_est = perm_df.loc[perm_df["is_true_cutoff"], "Estimate"].iloc[0]
    
    # Empirical P-value (Rank): What share of placebos have an estimate MORE negative than the true one?
    # This is a one-sided test for the "penalty" hypothesis.
    p_rank_lower = (perm_df["Estimate"] <= true_est).mean()
    # Two-sided rank p-value: what share are more extreme in absolute terms?
    p_rank_extreme = (perm_df["Estimate"].abs() >= abs(true_est)).mean()

    print("\n=========================================")
    print("      PERMUTATION INFERENCE RESULTS      ")
    print("=========================================\n")
    print(f"True Cutoff (2021-09-27) Estimate: {true_est:.4f}")
    print(f"Number of Placebo Mondays:         {len(perm_df)}")
    print(f"Permutation P-value (One-sided):   {p_rank_lower:.4f}")
    print(f"Permutation P-value (Two-sided):   {p_rank_extreme:.4f}")

    if p_rank_lower > 0.05:
        print("\nCONCLUSION: The September 2021 discontinuity is NOT statistically unusual.")
        print(f"Found {int(p_rank_lower * len(perm_df))} weeks with a larger adoption drop.")
    else:
        print("\nCONCLUSION: The September 2021 discontinuity IS statistically unusual.")

    # 5. Visualization
    plt.figure(figsize=(12, 6))
    sns.histplot(perm_df["Estimate"], bins=40, kde=True, color="skyblue", edgecolor="white")
    plt.axvline(true_est, color="red", linestyle="--", linewidth=2, label=f"True Cutoff (2021-09-27): {true_est:.3f}")
    plt.title("Distribution of RDD Coefficients across All Random Mondays (2017-2024)")
    plt.xlabel("Estimated Discontinuity (log downloads)")
    plt.ylabel("Frequency (Count of Mondays)")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "permutation_distribution.png")
    print(f"\nSaved distribution plot to {FIGURES_DIR / 'permutation_distribution.png'}")

if __name__ == "__main__":
    main()
