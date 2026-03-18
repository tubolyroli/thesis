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
WINDOW_WEEKS = 156 # Extended to 3 years to capture long horizons
DONUT_WEEKS = list(range(-8, 1)) # July vs October (Excludes Aug & Sept: ~9 weeks)
MIN_DOWNLOADS_52WK = 10

# Milestones (Monday-aligned)
CHATGPT_RELEASE = pd.Timestamp("2022-11-28")
GPT4_RELEASE = pd.Timestamp("2023-03-13")
GPT4_TURBO_RELEASE = pd.Timestamp("2023-11-06")

# Main Analysis Config
MAIN_CUTOFF_NAME = "Main_2021"
MAIN_ANALYSIS_DATA = FINAL_DIR / f"analysis_{MAIN_CUTOFF_NAME}.csv"

# Cutoff Environments
CUTOFFS = {
    "Placebo_2018": pd.Timestamp("2018-09-24"),
    "Placebo_2019": pd.Timestamp("2019-09-30"),
    "Placebo_2020": pd.Timestamp("2020-09-28"),
    MAIN_CUTOFF_NAME: pd.Timestamp("2021-09-27"),
    "Adoption_2023": pd.Timestamp("2023-01-02")
}

# Column Candidates for Mapping
AI_SCORE_COLS = ["ai_score_mean", "ai_mean", "avg_ai_score", "mean_ai_score"]
AI_WEIGHT_COLS = ["ai_score_n", "n_commits", "commit_count", "n"]

# Shared RDD Outcomes
PRIMARY_OUTCOMES = [
    "total_downloads_52wk", 
    "cum_downloads_gpt4", 
    "cum_downloads_gpt4turbo", 
    "cum_downloads_alltime",
    "post_ai_downloads_alltime" # Time-adjusted: downloads since Nov 2022
]
