"""
Script 19: Compute descriptive percentage differences and normalized time series plots.

Outputs:
  1. Weekly log-ratio of pre- vs post-cutoff cohort means (PyPI + GitHub) with bootstrapped CIs.
  2. Summary table of percentage differences at key time points (for intro punchline).
  3. Normalized time series figure (replacement for Figure 5.5).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import (
    RAW_DIR, FINAL_DIR, RESULTS_DIR, FIGURES_DIR,
    CHATGPT_RELEASE, GPT4_RELEASE, CUTOFFS, MAIN_CUTOFF_NAME, DONUT_WEEKS
)
from utils import setup_plotting_style, normalize_name

N_BOOTSTRAP = 500
RNG_SEED = 42


def load_cohorts(pre_range=(-12, -9), post_range=(1, 4)):
    """Load pre- and post-cutoff cohort packages from the 2021 analysis file."""
    df_meta = pd.read_csv(
        FINAL_DIR / "analysis_Main_2021.csv",
        usecols=["package", "dist_to_cutoff", "release_week", "matched_to_github"]
    )
    df_meta["cohort"] = "Other"
    df_meta.loc[
        (df_meta["dist_to_cutoff"] >= pre_range[0]) & (df_meta["dist_to_cutoff"] <= pre_range[1]),
        "cohort"
    ] = "Pre-cutoff"
    df_meta.loc[
        (df_meta["dist_to_cutoff"] >= post_range[0]) & (df_meta["dist_to_cutoff"] <= post_range[1]),
        "cohort"
    ] = "Post-cutoff"
    df_meta = df_meta[df_meta["cohort"] != "Other"].copy()
    print(f"  Cohort sizes: {df_meta['cohort'].value_counts().to_dict()}")
    return df_meta


def compute_weekly_ratio_pypi(df_meta):
    """Compute weekly mean downloads per cohort and the log-ratio.

    Returns a pre-aggregated (package, week) table for fast bootstrapping,
    plus the wide ratio table.
    """
    print("Loading PyPI panel (this may take a moment)...")
    cohort_packages = set(df_meta["package"].unique())

    df_panel = pd.read_parquet(
        RAW_DIR / "pypi_downloads.parquet",
        columns=["project", "week_start", "downloads"]
    )
    df_panel["package"] = normalize_name(df_panel["project"])
    df_panel["week_start"] = pd.to_datetime(df_panel["week_start"])

    # Filter to cohort packages early to reduce memory
    df_panel = df_panel[df_panel["package"].isin(cohort_packages)].copy()
    print(f"  Filtered panel to {len(df_panel):,} rows for {len(cohort_packages)} cohort packages")

    # Merge with cohort labels
    df = df_panel.merge(df_meta[["package", "cohort"]], on="package", how="inner")
    del df_panel

    # Pre-aggregate to (package, week, cohort) level for fast bootstrapping
    pkg_week = df.groupby(["package", "week_start", "cohort"])["downloads"].sum().reset_index()

    # Cohort-level weekly means
    agg = pkg_week.groupby(["week_start", "cohort"])["downloads"].mean().reset_index()
    agg.columns = ["week_start", "cohort", "mean_downloads"]

    wide = agg.pivot(index="week_start", columns="cohort", values="mean_downloads").dropna()
    wide = wide.sort_index()

    wide["log_ratio"] = np.log(wide["Pre-cutoff"] + 1) - np.log(wide["Post-cutoff"] + 1)
    wide["pct_diff"] = (wide["Pre-cutoff"] - wide["Post-cutoff"]) / wide["Post-cutoff"] * 100

    return pkg_week, wide


def bootstrap_ci_pypi(pkg_week, n_boot=N_BOOTSTRAP, seed=RNG_SEED):
    """Bootstrap CIs for the weekly log-ratio by resampling libraries within cohorts.

    Uses pre-aggregated (package, week) data for efficiency.
    """
    rng = np.random.default_rng(seed)

    pre_pkgs = pkg_week.loc[pkg_week["cohort"] == "Pre-cutoff", "package"].unique()
    post_pkgs = pkg_week.loc[pkg_week["cohort"] == "Post-cutoff", "package"].unique()
    n_pre, n_post = len(pre_pkgs), len(post_pkgs)

    # Index package-week data for fast lookup
    pre_data = pkg_week[pkg_week["cohort"] == "Pre-cutoff"].set_index(["package", "week_start"])["downloads"]
    post_data = pkg_week[pkg_week["cohort"] == "Post-cutoff"].set_index(["package", "week_start"])["downloads"]

    boot_ratios = []

    for b in range(n_boot):
        if b % 100 == 0:
            print(f"  Bootstrap iteration {b}/{n_boot}...")

        # Resample package indices (with replacement)
        pre_sample = rng.choice(pre_pkgs, size=n_pre, replace=True)
        post_sample = rng.choice(post_pkgs, size=n_post, replace=True)

        # Compute weekly means for resampled packages
        pre_dl = (pkg_week[pkg_week["package"].isin(set(pre_sample))]
                  .groupby("week_start")["downloads"].mean())
        post_dl = (pkg_week[pkg_week["package"].isin(set(post_sample))]
                   .groupby("week_start")["downloads"].mean())

        common_weeks = pre_dl.index.intersection(post_dl.index)
        ratio = np.log(pre_dl[common_weeks] + 1) - np.log(post_dl[common_weeks] + 1)
        boot_ratios.append(ratio)

    boot_df = pd.DataFrame(boot_ratios)
    ci_lower = boot_df.quantile(0.025)
    ci_upper = boot_df.quantile(0.975)

    return ci_lower, ci_upper


def compute_weekly_ratio_github(df_meta):
    """Compute weekly mean imports per cohort and the log-ratio for GitHub data."""
    print("Loading GitHub panel...")
    gh = pd.read_csv(RAW_DIR / "github_library_week_panel.csv")
    gh["package"] = normalize_name(gh["library"])
    gh["week_start"] = pd.to_datetime(gh["week_start"])

    # Only keep packages matched to GitHub
    gh_packages = df_meta[df_meta["matched_to_github"] == 1][["package", "cohort"]]
    print(f"  GitHub-matched cohort sizes: {gh_packages['cohort'].value_counts().to_dict()}")

    df = gh.merge(gh_packages, on="package", how="inner")

    agg = df.groupby(["week_start", "cohort"])["import_count"].agg(["mean", "count"]).reset_index()
    agg.columns = ["week_start", "cohort", "mean_imports", "n_packages"]

    wide = agg.pivot(index="week_start", columns="cohort", values="mean_imports").dropna()
    wide = wide.sort_index()

    wide["log_ratio"] = np.log(wide["Pre-cutoff"] + 1) - np.log(wide["Post-cutoff"] + 1)
    wide["pct_diff"] = (wide["Pre-cutoff"] - wide["Post-cutoff"]) / wide["Post-cutoff"] * 100

    return wide


def compute_summary_stats(wide_pypi, wide_gh):
    """Compute percentage differences at key time points for the intro punchline."""
    results = []

    # Define key time points
    timepoints = {
        "ChatGPT + 6 months": pd.Timestamp("2023-05-29"),
        "ChatGPT + 12 months": pd.Timestamp("2023-11-27"),
        "ChatGPT + 24 months": pd.Timestamp("2024-11-25"),
        "January 2026": pd.Timestamp("2026-01-12"),
    }

    # Also compute post-ChatGPT averages (Nov 2022 onward)
    for label, date in timepoints.items():
        # PyPI: find nearest week
        idx_pypi = wide_pypi.index[wide_pypi.index <= date]
        if len(idx_pypi) > 0:
            row = wide_pypi.loc[idx_pypi[-1]]
            results.append({
                "Source": "PyPI",
                "Period": label,
                "Pre-cutoff mean": f"{row['Pre-cutoff']:.1f}",
                "Post-cutoff mean": f"{row['Post-cutoff']:.1f}",
                "Pct difference": f"{row['pct_diff']:.1f}%",
                "Log ratio": f"{row['log_ratio']:.3f}",
            })

        # GitHub
        if wide_gh is not None:
            idx_gh = wide_gh.index[wide_gh.index <= date]
            if len(idx_gh) > 0:
                row_gh = wide_gh.loc[idx_gh[-1]]
                results.append({
                    "Source": "GitHub",
                    "Period": label,
                    "Pre-cutoff mean": f"{row_gh['Pre-cutoff']:.1f}",
                    "Post-cutoff mean": f"{row_gh['Post-cutoff']:.1f}",
                    "Pct difference": f"{row_gh['pct_diff']:.1f}%",
                    "Log ratio": f"{row_gh['log_ratio']:.3f}",
                })

    # Post-ChatGPT average (Nov 2022 - end of panel)
    post_chatgpt = wide_pypi[wide_pypi.index >= CHATGPT_RELEASE]
    if len(post_chatgpt) > 0:
        avg_pre = post_chatgpt["Pre-cutoff"].mean()
        avg_post = post_chatgpt["Post-cutoff"].mean()
        pct = (avg_pre - avg_post) / avg_post * 100
        results.append({
            "Source": "PyPI",
            "Period": "Post-ChatGPT average",
            "Pre-cutoff mean": f"{avg_pre:.1f}",
            "Post-cutoff mean": f"{avg_post:.1f}",
            "Pct difference": f"{pct:.1f}%",
            "Log ratio": f"{np.log(avg_pre + 1) - np.log(avg_post + 1):.3f}",
        })

    return pd.DataFrame(results)


def plot_normalized_timeseries(wide_pypi, ci_lower, ci_upper):
    """Plot the normalized log-ratio time series with bootstrap CIs."""
    setup_plotting_style()
    fig, ax = plt.subplots(figsize=(12, 6))

    weeks = wide_pypi.index
    ratio = wide_pypi["log_ratio"]

    # Smooth with 4-week rolling average for readability
    ratio_smooth = ratio.rolling(4, center=True, min_periods=2).mean()
    ci_lower_smooth = ci_lower.reindex(weeks).rolling(4, center=True, min_periods=2).mean()
    ci_upper_smooth = ci_upper.reindex(weeks).rolling(4, center=True, min_periods=2).mean()

    # Only plot from mid-2021 onward (when both cohorts exist)
    cutoff_date = CUTOFFS[MAIN_CUTOFF_NAME]
    mask = weeks >= pd.Timestamp("2021-10-01")

    ax.plot(weeks[mask], ratio_smooth[mask], color="steelblue", linewidth=2, label="Log ratio (4-week MA)")
    ax.fill_between(
        weeks[mask],
        ci_lower_smooth[mask],
        ci_upper_smooth[mask],
        alpha=0.2, color="steelblue", label="95% Bootstrap CI"
    )

    # Reference line at 0
    ax.axhline(0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)

    # Milestone lines
    ax.axvline(CHATGPT_RELEASE, color="red", linestyle="-", alpha=0.8, linewidth=1.5, label="ChatGPT release")
    ax.axvline(GPT4_RELEASE, color="darkred", linestyle=":", alpha=0.8, linewidth=1.5, label="GPT-4 release")

    ax.set_xlabel("Calendar Date", fontsize=12)
    ax.set_ylabel("Log ratio: Pre-cutoff / Post-cutoff\n(positive = pre-cutoff advantage)", fontsize=11)
    ax.set_title("Normalized Diffusion Gap: Pre- vs Post-Cutoff Libraries (PyPI)", fontsize=13, fontweight="bold")

    ax.legend(loc="upper left", fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    fig.autofmt_xdate()

    plt.tight_layout()
    out_path = FIGURES_DIR / "normalized_diffusion_gap_pypi.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved normalized plot to {out_path}")
    plt.close()


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load cohorts
    print("Step 1: Loading cohorts...")
    df_meta = load_cohorts()

    # 2. Compute PyPI weekly ratios
    print("\nStep 2: Computing PyPI weekly ratios...")
    pkg_week, wide_pypi = compute_weekly_ratio_pypi(df_meta)

    # 3. Bootstrap CIs for PyPI
    print("\nStep 3: Bootstrapping CIs (this takes a few minutes)...")
    ci_lower, ci_upper = bootstrap_ci_pypi(pkg_week, n_boot=N_BOOTSTRAP)
    del pkg_week  # free memory

    # 4. Compute GitHub weekly ratios
    print("\nStep 4: Computing GitHub weekly ratios...")
    wide_gh = compute_weekly_ratio_github(df_meta)

    # 5. Summary statistics at key time points
    print("\nStep 5: Computing summary statistics...")
    summary = compute_summary_stats(wide_pypi, wide_gh)
    summary.to_csv(RESULTS_DIR / "descriptive_percentage_summary.csv", index=False)
    print("\n" + "=" * 60)
    print("DESCRIPTIVE PERCENTAGE DIFFERENCES AT KEY TIME POINTS")
    print("=" * 60)
    print(summary.to_string(index=False))

    # 6. Generate normalized plot
    print("\nStep 6: Generating normalized plot...")
    plot_normalized_timeseries(wide_pypi, ci_lower, ci_upper)

    # 7. Save weekly ratio data for reference
    wide_pypi.to_csv(RESULTS_DIR / "weekly_ratio_pypi.csv")
    wide_gh.to_csv(RESULTS_DIR / "weekly_ratio_github.csv")

    print("\nDone.")


if __name__ == "__main__":
    main()
