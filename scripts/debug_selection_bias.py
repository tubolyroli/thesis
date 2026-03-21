import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy import stats
from config import MAIN_ANALYSIS_DATA, DONUT_WEEKS, MIN_SUCCESS_LOW

def run_selection_check(df, outcome_col, label):
    # Clean data
    sub = df[~df["in_donut"].astype(bool)].copy()
    sub = sub[(sub["dist_to_cutoff"] >= -26) & (sub["dist_to_cutoff"] <= 26)].copy()
    
    # Prepare RDD variables
    sub["treat"] = sub["is_pre_cutoff"]
    sub["x"] = sub["dist_to_cutoff"]
    sub["treat_x"] = sub["treat"] * sub["x"]
    
    X = sub[["treat", "x", "treat_x"]]
    y = sub[outcome_col]
    
    # Simple OLS with sklearn
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate simple SE (non-clustered for speed/feasibility here)
    y_pred = model.predict(X)
    mse = np.sum((y - y_pred)**2) / (len(y) - X.shape[1] - 1)
    var_b = mse * np.linalg.inv(np.dot(X.T, X) + np.eye(X.shape[1])*1e-10).diagonal()
    se = np.sqrt(np.maximum(var_b, 0))
    
    coef = model.coef_[0] # Coefficient for 'treat'
    t_stat = coef / se[0] if se[0] > 0 else 0
    p_val = 2 * (1 - stats.t.cdf(np.abs(t_stat), df=len(y)-X.shape[1]-1))

    print(f"--- Selection Test: {label} ---")
    print(f"Outcome: {outcome_col}")
    print(f"RDD Estimate (Jump at Cutoff): {coef:.4f}")
    print(f"P-value: {p_val:.4f}")
    print(f"N: {len(sub)}\n")
    return coef, p_val

def main():
    if not MAIN_ANALYSIS_DATA.exists():
        print("Data not found.")
        return
        
    df = pd.read_csv(MAIN_ANALYSIS_DATA)
    # Re-calculate success based on 26-week horizon
    df["is_successful"] = (df["cum_downloads_26wk"] >= MIN_SUCCESS_LOW).astype(int)
    
    print("=========================================")
    print("   RIGOROUS BIAS & SELECTION DIAGNOSIS   ")
    print("=========================================\n")
    
    # 1. Test for Selection Bias in Success Filter
    run_selection_check(df, "is_successful", "Success Filter (500 downloads @ 26w)")
    
    # 2. Test for Selection Bias in GitHub Matching
    run_selection_check(df, "matched_to_github", "GitHub Matching")
    
    # 3. Test for Endogeneity of AI Score
    df_gh = df[df["matched_to_github"] == 1].copy()
    if "avg_ai_score_52wk" in df_gh.columns:
        df_ai = df_gh.dropna(subset=["avg_ai_score_52wk"])
        if not df_ai.empty:
            run_selection_check(df_ai, "avg_ai_score_52wk", "AI Exposure Score")

    # 4. Formal Density Check (Simple McCrary-style)
    counts = df.groupby("dist_to_cutoff").size().reset_index(name="n_libs")
    counts["is_pre_cutoff"] = (counts["dist_to_cutoff"] < 0).astype(int)
    counts_near = counts[(counts["dist_to_cutoff"] >= -13) & (counts["dist_to_cutoff"] <= 13) & (~counts["dist_to_cutoff"].isin(DONUT_WEEKS))].copy()
    
    if not counts_near.empty:
        X_dens = counts_near[["is_pre_cutoff", "dist_to_cutoff"]]
        y_dens = counts_near["n_libs"]
        model_dens = LinearRegression().fit(X_dens, y_dens)
        
        print("--- Density Test (McCrary-style) ---")
        print(f"Jump in library counts at cutoff: {model_dens.coef_[0]:.4f}")
        print("Verdict: Visual check of density plot recommended.")

if __name__ == "__main__":
    main()
