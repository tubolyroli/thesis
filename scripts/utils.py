import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns

def normalize_name(s: pd.Series) -> pd.Series:
    """Normalize package/library names for consistent merging."""
    return (
        s.astype(str)
        .str.lower()
        .str.replace("_", "-", regex=False)
        .str.strip()
    )

def detect_column(columns, candidates):
    """Safely detect the presence of expected column names in a dataframe."""
    for c in candidates:
        if c in columns:
            return c
    return None

def check_monday_alignment(df: pd.DataFrame, date_col: str = "week_start") -> None:
    """Assert that all date values in a column are Monday-aligned."""
    bad_weekdays = df.loc[df[date_col].dt.weekday != 0, date_col].drop_duplicates()
    if not bad_weekdays.empty:
        raise ValueError(
            f"Found non-Monday values in {date_col}: {bad_weekdays.head().tolist()}"
        )

def get_weeks_since(start_col: pd.Series, end_col: pd.Series) -> pd.Series:
    """Calculate the number of weeks between two dates."""
    return ((start_col - end_col).dt.days // 7).astype("int64")

def setup_plotting_style():
    """Configure consistent seaborn/matplotlib style for the project."""
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "font.size": 16,
        "axes.labelsize": 16,
        "axes.titlesize": 18,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
        "legend.fontsize": 14,
        "legend.title_fontsize": 16
    })

import rdrobust

def run_local_linear_rdd(df: pd.DataFrame, outcome_col: str, h: float = None, donut_weeks: list = None, label: str = "", cluster_col: str = None, covs_cols: list = None):
    """
    Implements a Local Linear RDD using Weighted Least Squares (WLS) with a triangular kernel.
    Specification: log(1+Y) ~ alpha + beta*Pre + gamma1*Dist + gamma2*Dist*Pre [+ covariates]
    """
    sub = df.copy()

    # 1. Apply Donut
    if donut_weeks:
        sub = sub[~sub["dist_to_cutoff"].isin(donut_weeks)]

    # 2. Restrict to bandwidth h
    sub = sub[(sub["dist_to_cutoff"] >= -h) & (sub["dist_to_cutoff"] <= h)].copy()

    # Drop NAs in outcome
    sub = sub.dropna(subset=[outcome_col])

    if len(sub) < 10:
        return {"Label": label, "Outcome": outcome_col, "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan, "N": len(sub), "BW": h, "Donut": "Yes" if donut_weeks else "No", "Method": "WLS", "Baseline_Adjusted": "Yes" if covs_cols else "No"}

    # 3. Construct variables
    # Log transform for count-based outcomes
    if any(k in outcome_col for k in ["downloads", "imports", "cum"]):
        sub["y"] = np.log1p(sub[outcome_col])
    else:
        sub["y"] = sub[outcome_col]

    sub["x"] = sub["dist_to_cutoff"]
    sub["treated"] = (sub["x"] >= 0).astype(int)
    sub["x_treated"] = sub["x"] * sub["treated"]

    # 4. Build formula with optional covariates
    formula = "y ~ treated + x + x_treated"
    if covs_cols:
        for c in covs_cols:
            cov_name = f"cov_{c}"
            if any(k in c for k in ["downloads", "imports", "cum"]):
                sub[cov_name] = np.log1p(sub[c])
            else:
                sub[cov_name] = sub[c]
            formula += f" + {cov_name}"
        sub = sub.dropna(subset=[f"cov_{c}" for c in covs_cols])

    # 5. Triangular weights: w = 1 - |x/h|
    sub["weight"] = 1 - (np.abs(sub["x"]) / h)
    sub = sub[sub["weight"] > 0]

    # 6. Estimation
    try:
        cov_type = 'HC1'
        fit_kwargs = {'cov_type': cov_type}
        if cluster_col and cluster_col in sub.columns:
            sub['cluster_idx'] = sub[cluster_col].astype('category').cat.codes
            fit_kwargs['cov_type'] = 'cluster'
            fit_kwargs['cov_kwds'] = {'groups': sub['cluster_idx']}

        model = smf.wls(formula, data=sub, weights=sub["weight"]).fit(**fit_kwargs)
        return {
            "Label": label,
            "Outcome": outcome_col,
            "Estimate": model.params["treated"],
            "Std.Err": model.bse["treated"],
            "P-value": model.pvalues["treated"],
            "N": int(model.nobs),
            "BW": h,
            "Donut": "Yes" if donut_weeks else "No",
            "Method": f"WLS ({fit_kwargs['cov_type']})",
            "Baseline_Adjusted": "Yes" if covs_cols else "No"
        }
    except Exception as e:
        print(f"CRITICAL: WLS failed for {label}/{outcome_col}: {str(e)}")
        return {"Label": label, "Outcome": outcome_col, "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan, "N": 0, "BW": h, "Donut": "Yes" if donut_weeks else "No", "Method": f"WLS ERROR: {type(e).__name__}", "Baseline_Adjusted": "Yes" if covs_cols else "No"}

def run_rdrobust_est(df: pd.DataFrame, outcome_col: str, h: float = None, donut_weeks: list = None, label: str = "", covs_cols: list = None):
    """
    Wrapper for the rdrobust package providing bias-corrected RD estimates.
    Returns a dictionary containing Conventional, Bias-Corrected, and Robust estimates.
    """
    sub = df.copy()
    if donut_weeks:
        sub = sub[~sub["dist_to_cutoff"].isin(donut_weeks)]

    sub = sub.dropna(subset=[outcome_col])

    if len(sub) < 10:
        return {
            "Label": label, "Outcome": outcome_col,
            "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan,
            "Estimate_Conv": np.nan, "Std.Err_Conv": np.nan, "P-value_Conv": np.nan,
            "Estimate_BC": np.nan, "Std.Err_BC": np.nan, "P-value_BC": np.nan,
            "N": len(sub), "BW": h, "Donut": "Yes" if donut_weeks else "No",
            "Method": "rdrobust (insufficient N)", "Baseline_Adjusted": "Yes" if covs_cols else "No"
        }

    if any(k in outcome_col for k in ["downloads", "imports", "cum"]):
        y = np.log1p(sub[outcome_col])
    else:
        y = sub[outcome_col]

    x = sub["dist_to_cutoff"]

    # Build covariates matrix if requested
    covs_arg = None
    if covs_cols:
        covs_data = {}
        for c in covs_cols:
            if any(k in c for k in ["downloads", "imports", "cum"]):
                covs_data[c] = np.log1p(sub[c])
            else:
                covs_data[c] = sub[c]
        covs_df = pd.DataFrame(covs_data, index=sub.index)
        covs_df = covs_df.dropna()
        valid_idx = covs_df.index.intersection(y.index)
        y = y.loc[valid_idx]
        x = x.loc[valid_idx]
        covs_arg = covs_df.loc[valid_idx]

    try:
        res = rdrobust.rdrobust(y=y, x=x, c=0, h=h, kernel='triangular', covs=covs_arg)

        bw_val = res.bws.loc['h', 'left'] if 'h' in res.bws.index else np.nan

        # Primary Estimate: Robust (Bias-Corrected with Robust SE)
        est_robust = res.coef.loc['Robust', 'Coeff']
        se_robust = res.se.loc['Robust', 'Std. Err.']
        pv_robust = res.pv.loc['Robust', 'P>|t|']

        # Stability Check
        if np.abs(est_robust) > 500:
            print(f"WARNING: Exploding coefficient ({est_robust:.2e}) detected for {label}/{outcome_col}. Returning NaN.")
            return {
                "Label": label, "Outcome": outcome_col,
                "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan,
                "N": int(res.N[0] + res.N[1]), "BW": bw_val, "Donut": "Yes" if donut_weeks else "No",
                "Method": "rdrobust (Unstable)", "Baseline_Adjusted": "Yes" if covs_cols else "No"
            }

        return {
            "Label": label,
            "Outcome": outcome_col,
            "Estimate": est_robust,
            "Std.Err": se_robust,
            "P-value": pv_robust,

            "Estimate_Conv": res.coef.loc['Conventional', 'Coeff'],
            "Std.Err_Conv": res.se.loc['Conventional', 'Std. Err.'],
            "P-value_Conv": res.pv.loc['Conventional', 'P>|t|'],

            "N": int(res.N[0] + res.N[1]),
            "BW": bw_val,
            "Donut": "Yes" if donut_weeks else "No",
            "Method": "rdrobust (Robust/Bias-Corrected)",
            "Baseline_Adjusted": "Yes" if covs_cols else "No"
        }
    except Exception as e:
        import traceback
        print(f"CRITICAL: rdrobust failed for {label}/{outcome_col}: {str(e)}")
        return {
            "Label": label, "Outcome": outcome_col,
            "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan,
            "Estimate_Conv": np.nan, "Std.Err_Conv": np.nan, "P-value_Conv": np.nan,
            "Estimate_BC": np.nan, "Std.Err_BC": np.nan, "P-value_BC": np.nan,
            "N": 0, "BW": h, "Donut": "Yes" if donut_weeks else "No",
            "Method": f"rdrobust ERROR: {type(e).__name__}", "Baseline_Adjusted": "Yes" if covs_cols else "No"
        }

def run_quantile_rdd(df: pd.DataFrame, outcome_col: str, q: float = 0.5, h: float = None, donut_weeks: list = None, label: str = ""):
    """
    Implements a Quantile RDD using Quantile Regression (QuantReg).
    Default q=0.5 (Median RDD).
    Specification: Y ~ alpha + beta*Treated + gamma1*Dist + gamma2*Dist*Treated
    By default uses raw Y to provide a robust-to-outliers level estimate.
    """
    sub = df.copy()
    
    # 1. Apply Donut
    if donut_weeks:
        sub = sub[~sub["dist_to_cutoff"].isin(donut_weeks)]
    
    # 2. Restrict to bandwidth h
    sub = sub[(sub["dist_to_cutoff"] >= -h) & (sub["dist_to_cutoff"] <= h)].copy()
    
    # Drop NAs in outcome
    sub = sub.dropna(subset=[outcome_col])
    
    if len(sub) < 20: # Quantile regression needs more points
        return {"Label": label, "Outcome": outcome_col, "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan, "N": len(sub), "BW": h, "Donut": "Yes" if donut_weeks else "No", "Method": f"QuantReg({q})"}

    # 3. Construct variables
    sub["y"] = sub[outcome_col]
    sub["x"] = sub["dist_to_cutoff"]
    sub["treated"] = (sub["x"] >= 0).astype(int)
    sub["x_treated"] = sub["x"] * sub["treated"]
    
    # 4. Estimation (Unweighted within bandwidth for standard QuantReg)
    try:
        model = smf.quantreg("y ~ treated + x + x_treated", data=sub).fit(q=q)
        return {
            "Label": label,
            "Outcome": outcome_col,
            "Estimate": model.params["treated"],
            "Std.Err": model.bse["treated"],
            "P-value": model.pvalues["treated"],
            "N": int(model.nobs),
            "BW": h, "Donut": "Yes" if donut_weeks else "No", "Method": f"QuantReg({q})"
        }
    except Exception as e:
        print(f"CRITICAL: QuantReg failed for {label}/{outcome_col}: {str(e)}")
        return {"Label": label, "Outcome": outcome_col, "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan, "N": 0, "BW": h, "Donut": "Yes" if donut_weeks else "No", "Method": f"QuantReg ERROR: {type(e).__name__}"}
