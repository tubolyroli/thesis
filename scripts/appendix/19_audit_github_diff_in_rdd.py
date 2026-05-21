"""Audit: re-run the GitHub matched-sample Diff-in-RDD with spike weeks excluded.

Slide 10 of the TDK deck reports:
  - PyPI Diff-in-RDD baseline-adjusted: -7.29 log pts (full sample, N=88,001)
  - GitHub Diff-in-RDD baseline-adjusted: +2.12 log pts (matched, N=6,582)
and frames this as "opposite signs on the same matched sample."

The audit (notebooks/sample_composition_audit_executed.ipynb) showed that the PyPI
estimate on the full sample collapses from -7.29 to -0.65 when three contaminated
placebo weeks are excluded. The audit did NOT re-run the matched-sample GitHub
estimate. This script does that.

Output: results/audit/audit_matched_diff_in_rdd.csv
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from config import FINAL_DIR, RESULTS_AUDIT, DONUT_WEEKS, DEFAULT_BW, MIN_DOWNLOADS_FILTER


SPIKE_DATES = {
    ("Placebo_2018", "2018-07-16"),
    ("Placebo_2020", "2020-07-20"),
    ("Placebo_2020", "2020-07-27"),
}


def load_pooled():
    cohort_files = {
        "Placebo_2018": FINAL_DIR / "analysis_Placebo_2018.csv",
        "Placebo_2019": FINAL_DIR / "analysis_Placebo_2019.csv",
        "Placebo_2020": FINAL_DIR / "analysis_Placebo_2020.csv",
        "Main_2021":    FINAL_DIR / "analysis_Main_2021.csv",
    }
    dfs = []
    for name, path in cohort_files.items():
        d = pd.read_csv(path)
        d["cohort"] = name
        d["cutoff_year"] = int(name.split("_")[1])
        d["is_2021"] = int(name == "Main_2021")
        dfs.append(d)
    df = pd.concat(dfs, ignore_index=True)
    df["release_week"] = pd.to_datetime(df["release_week"])
    rw_str = df["release_week"].dt.strftime("%Y-%m-%d")
    df["is_spike"] = [(c, r) in SPIKE_DATES for c, r in zip(df["cohort"], rw_str)]
    return df


def run_diff_rdd(df, outcome, bw=DEFAULT_BW, adjusted=True):
    sub = df[(~df["dist_to_cutoff"].isin(DONUT_WEEKS)) &
             (df["dist_to_cutoff"].abs() <= bw)].copy()
    sub["log_y"] = np.log1p(sub[outcome])
    sub["x"] = sub["dist_to_cutoff"]
    sub["treated"] = (sub["x"] >= 0).astype(int)
    sub["weight"] = 1 - sub["x"].abs() / bw
    sub = sub[sub["weight"] > 0]
    sub["cluster_idx"] = sub["cutoff_year"].astype(str) + "_" + sub["x"].astype(str)
    if adjusted:
        sub["log_baseline"] = np.log1p(sub["total_downloads_52wk"])
        formula = "log_y ~ log_baseline + treated * is_2021 + x * treated * is_2021"
    else:
        formula = "log_y ~ treated * is_2021 + x * treated * is_2021"
    m = smf.wls(formula, data=sub, weights=sub["weight"]).fit(
        cov_type="cluster", cov_kwds={"groups": sub["cluster_idx"]}
    )
    return {
        "coef": float(m.params["treated:is_2021"]),
        "se":   float(m.bse["treated:is_2021"]),
        "p":    float(m.pvalues["treated:is_2021"]),
        "n":    int(m.nobs),
    }


def main():
    df = load_pooled()
    df_broad = df[df["total_downloads_52wk"] >= MIN_DOWNLOADS_FILTER].copy()

    print(f"\nFull pooled Broad sample: N={len(df_broad):,}")
    print(f"  Spike rows in pool: {df_broad['is_spike'].sum():,}")

    df_matched = df_broad[df_broad["matched_to_github"] == 1].copy()
    print(f"\nMatched (GitHub-PyPI) Broad sample: N={len(df_matched):,}")
    print(f"  Spike rows in matched pool: {df_matched['is_spike'].sum():,}")

    rows = []
    specs = [
        ("Full sample, PyPI",         df_broad,                          "post_ai_downloads_alltime"),
        ("Full sample, PyPI (-spikes)", df_broad[~df_broad["is_spike"]], "post_ai_downloads_alltime"),
        ("Matched sample, PyPI",          df_matched,                            "post_ai_downloads_alltime"),
        ("Matched sample, PyPI (-spikes)", df_matched[~df_matched["is_spike"]],  "post_ai_downloads_alltime"),
        ("Matched sample, GitHub",          df_matched,                            "cum_imports_alltime"),
        ("Matched sample, GitHub (-spikes)", df_matched[~df_matched["is_spike"]],  "cum_imports_alltime"),
        ("Matched sample, GitHub post_ai",          df_matched,                            "post_ai_imports_alltime"),
        ("Matched sample, GitHub post_ai (-spikes)", df_matched[~df_matched["is_spike"]],  "post_ai_imports_alltime"),
    ]

    for label, data, outcome in specs:
        try:
            r = run_diff_rdd(data, outcome, bw=DEFAULT_BW, adjusted=True)
            rows.append({"Spec": label, "Outcome": outcome, **r})
            print(f"  {label:48s} {outcome:30s} coef={r['coef']:+7.3f}  SE={r['se']:5.3f}  p={r['p']:.4f}  N={r['n']:,}")
        except Exception as e:
            print(f"  {label}: ERROR ({e})")

    out = pd.DataFrame(rows)
    RESULTS_AUDIT.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_AUDIT / "audit_matched_diff_in_rdd.csv"
    out.to_csv(out_path, index=False)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
