from pathlib import Path
import pandas as pd

# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
INTERM_DIR = BASE_DIR / "data" / "intermediate"
FINAL_DIR = BASE_DIR / "data" / "final"
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

# Analysis Parameters
WINDOW_WEEKS = 52
DONUT_WEEKS = [-2, -1, 0, 1, 2]
MIN_DOWNLOADS_52WK = 10
HORIZON_WEEKS = 52

# Main Analysis Config
MAIN_CUTOFF_NAME = "Main_2021"
MAIN_ANALYSIS_DATA = FINAL_DIR / f"analysis_{MAIN_CUTOFF_NAME}.csv"

# Cutoff Environments
CUTOFFS = {
    "Placebo_2018": pd.Timestamp("2018-09-24"), # Monday
    "Placebo_2019": pd.Timestamp("2019-09-30"), # Monday
    "Placebo_2020": pd.Timestamp("2020-09-28"), # Monday
    MAIN_CUTOFF_NAME: pd.Timestamp("2021-09-27"), # Monday
    "Adoption_2023": pd.Timestamp("2023-01-02") # Monday
}

# Column Candidates for Mapping
AI_SCORE_COLS = ["ai_score_mean", "ai_mean", "avg_ai_score", "mean_ai_score"]
AI_WEIGHT_COLS = ["ai_score_n", "n_commits", "commit_count", "n"]

# Shared RDD Outcomes
PRIMARY_OUTCOMES = ["total_downloads_52wk", "cum_imports_12wk", "cum_imports_26wk", "cum_imports_52wk"]
