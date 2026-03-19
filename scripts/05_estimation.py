import pandas as pd
from config import MAIN_ANALYSIS_DATA, RESULTS_DIR, DONUT_WEEKS, PRIMARY_OUTCOMES, MIN_DOWNLOADS_52WK, MIN_SUCCESS_LOW, MIN_SUCCESS_HIGH
from utils import run_local_linear_rdd, run_rdrobust_est, run_quantile_rdd

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not MAIN_ANALYSIS_DATA.exists():
        print(f"Error: {MAIN_ANALYSIS_DATA} not found.")
        return

    df_full = pd.read_csv(MAIN_ANALYSIS_DATA)

    # 1. Baseline: Broad Ecosystem (min10)
    df_min10 = df_full[df_full["total_downloads_52wk"] >= MIN_DOWNLOADS_52WK].copy()

    # 2. Subsample: "Successful" Libraries (Pre-GPT Winners)
    # Using 26-week horizon as suggested by supervisor (500 and 1000 thresholds)
    df_success_500 = df_full[df_full["cum_downloads_26wk"] >= MIN_SUCCESS_LOW].copy()
    df_success_1000 = df_full[df_full["cum_downloads_26wk"] >= MIN_SUCCESS_HIGH].copy()

    results = []

    # Run RD for different success tiers
    tiers = [
        (df_min10, "Broad (min10)"),
        (df_success_500, "Successful (min500@26w)"),
        (df_success_1000, "Superstar (min1000@26w)")
    ]

    for df_tier, tier_label in tiers:
        print(f"Running analysis for tier: {tier_label} (N={len(df_tier)})...")
        for outcome in PRIMARY_OUTCOMES:
            if outcome in df_tier.columns:
                results.append(run_rdrobust_est(df_tier, outcome, h=13, donut_weeks=DONUT_WEEKS, label=f"{tier_label}: {outcome}"))

    # 3. Mechanism Analysis (GitHub)

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
