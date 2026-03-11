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
    plt.rcParams["figure.figsize"] = (10, 6)

import rdrobust

def run_local_linear_rdd(df: pd.DataFrame, outcome_col: str, h: float = None, donut_weeks: list = None, label: str = "", cluster_col: str = None):
    """
    Implements a Local Linear RDD using Weighted Least Squares (WLS) with a triangular kernel.
    Specification: log(1+Y) ~ alpha + beta*Pre + gamma1*Dist + gamma2*Dist*Pre
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
        return {"Label": label, "Outcome": outcome_col, "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan, "N": len(sub), "BW": h, "Donut": "Yes" if donut_weeks else "No", "Method": "WLS"}

    # 3. Construct variables
    # Log transform only for download/import counts, not for binary outcomes
    if outcome_col.startswith("cum") or "downloads" in outcome_col:
        sub["y"] = np.log1p(sub[outcome_col])
    else:
        sub["y"] = sub[outcome_col]

    sub["x"] = sub["dist_to_cutoff"]
    sub["treated"] = (sub["x"] >= 0).astype(int)
    sub["x_treated"] = sub["x"] * sub["treated"]
    
    # 4. Triangular weights: w = 1 - |x/h|
    sub["weight"] = 1 - (np.abs(sub["x"]) / h)
    sub = sub[sub["weight"] > 0]
    
    # 5. Estimation
    try:
        cov_type = 'HC1'
        fit_kwargs = {'cov_type': cov_type}
        if cluster_col and cluster_col in sub.columns:
            sub['cluster_idx'] = sub[cluster_col].astype('category').cat.codes
            fit_kwargs['cov_type'] = 'cluster'
            fit_kwargs['cov_kwds'] = {'groups': sub['cluster_idx']}

        model = smf.wls("y ~ treated + x + x_treated", data=sub, weights=sub["weight"]).fit(**fit_kwargs)
        return {
            "Label": label,
            "Outcome": outcome_col,
            "Estimate": model.params["treated"],
            "Std.Err": model.bse["treated"],
            "P-value": model.pvalues["treated"],
            "N": int(model.nobs),
            "BW": h,
            "Donut": "Yes" if donut_weeks else "No",
            "Method": f"WLS ({fit_kwargs['cov_type']})"
        }
    except Exception as e:
        print(f"Error in WLS: {e}")
        return {"Label": label, "Outcome": outcome_col, "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan, "N": 0, "BW": h, "Donut": "Yes" if donut_weeks else "No", "Method": "WLS"}

def run_rdrobust_est(df: pd.DataFrame, outcome_col: str, h: float = None, donut_weeks: list = None, label: str = ""):
    """
    Wrapper for the rdrobust package providing bias-corrected RD estimates.
    """
    sub = df.copy()
    if donut_weeks:
        sub = sub[~sub["dist_to_cutoff"].isin(donut_weeks)]
    
    sub = sub.dropna(subset=[outcome_col])
    
    if outcome_col.startswith("cum") or "downloads" in outcome_col:
        y = np.log1p(sub[outcome_col])
    else:
        y = sub[outcome_col]
    
    x = sub["dist_to_cutoff"]
    
    try:
        # rdrobust expects x=0 to be the cutoff. Our dist_to_cutoff is 0 at the cutoff.
        # However, rdrobust treats x>=0 as treated by default. 
        # In our case, dist_to_cutoff < 0 is PRE-cutoff.
        # rdrobust implementation in Python might have different conventions, 
        # but let's assume res.coef.loc['Robust', 'Coeff'] is the jump.
        res = rdrobust.rdrobust(y=y, x=x, c=0, h=h, kernel='triangular')
        
        # rdrobust returns a class with results. 
        # Indices in pv are 'Conventional', 'Bias-Corrected', 'Robust'
        # Column names are 'Coeff', 'Std. Err.', 'P>|t|'
        
        # Bandwidths are in res.bws
        bw_val = res.bws.loc['h', 'left'] if 'h' in res.bws.index else np.nan
        
        # rdrobust returns the jump at c=0 (Post - Pre). 
        # This matches our WLS 'treated' coefficient convention.
        return {
            "Label": label,
            "Outcome": outcome_col,
            "Estimate": res.coef.loc['Robust', 'Coeff'],
            "Std.Err": res.se.loc['Robust', 'Std. Err.'],
            "P-value": res.pv.loc['Robust', 'P>|t|'],
            "N": int(res.N[0] + res.N[1]),
            "BW": bw_val,
            "Donut": "Yes" if donut_weeks else "No",
            "Method": "rdrobust (Robust)"
        }
    except Exception as e:
        # Check if error is 'P>|t|' (key error)
        print(f"Error in rdrobust: {e}")
        return {"Label": label, "Outcome": outcome_col, "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan, "N": 0, "BW": h, "Donut": "Yes" if donut_weeks else "No", "Method": "rdrobust"}

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
        print(f"Error in QuantReg: {e}")
        return {"Label": label, "Outcome": outcome_col, "Estimate": np.nan, "Std.Err": np.nan, "P-value": np.nan, "N": 0, "BW": h, "Donut": "Yes" if donut_weeks else "No", "Method": f"QuantReg({q})"}
