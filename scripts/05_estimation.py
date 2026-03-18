import pandas as pd
from config import MAIN_ANALYSIS_DATA, RESULTS_DIR, DONUT_WEEKS, PRIMARY_OUTCOMES
from utils import run_local_linear_rdd, run_rdrobust_est, run_quantile_rdd

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not MAIN_ANALYSIS_DATA.exists():
        print(f"Error: {MAIN_ANALYSIS_DATA} not found.")
        return

    df_full = pd.read_csv(MAIN_ANALYSIS_DATA)
    # Apply baseline sample restriction for adoption analysis
    df_min10 = df_full[df_full["total_downloads_52wk"] >= 10].copy()
    results = []
    
    # 1. Main Adoption Horizons (PyPI)
    print("Running PyPI Adoption Horizons...")
    # PRIMARY_OUTCOMES include total_downloads_52wk, cum_downloads_gpt4, cum_downloads_gpt4turbo, cum_downloads_alltime, post_ai_downloads_alltime
    for outcome in PRIMARY_OUTCOMES:
        if outcome in df_min10.columns:
            # Using a quarter-based bandwidth (h=13) to capture July/October as requested
            results.append(run_rdrobust_est(df_min10, outcome, h=13, donut_weeks=DONUT_WEEKS, label=f"PyPI: {outcome}"))

    # 2. Mechanism Analysis (GitHub)
    print("Running GitHub Mechanism Analysis...")
    df_gh = df_full[df_full["matched_to_github"] == 1].copy()
    gh_outcomes = [
        "cum_imports_52wk",
        "cum_imports_gpt4",
        "cum_imports_gpt4turbo",
        "cum_imports_alltime",
        "post_ai_imports_alltime"
    ]
    for outcome in gh_outcomes:
        if outcome in df_gh.columns:
            results.append(run_rdrobust_est(df_gh, outcome, h=13, donut_weeks=DONUT_WEEKS, label=f"GitHub: {outcome}"))

    # 3. AI Intensity Split (Direct Mechanism Test)
    # We will run this in script 10, but let's add a basic check here for the AI score itself
    if "avg_ai_score_52wk" in df_gh.columns:
        results.append(run_rdrobust_est(df_gh, "avg_ai_score_52wk", h=13, donut_weeks=DONUT_WEEKS, label="GitHub: AI Score intensity"))

    # Compile and Save
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "estimation_results_final.csv", index=False)
    
    print("\n=========================================")
    print("      FINAL RDD ESTIMATION RESULTS       ")
    print("=========================================\n")
    print(results_df[["Label", "Outcome", "Estimate", "Std.Err", "P-value", "Method", "N"]].round(4).to_string(index=False))
    print(f"\nSaved final results to: {RESULTS_DIR / 'estimation_results_final.csv'}")

if __name__ == "__main__":
    main()
