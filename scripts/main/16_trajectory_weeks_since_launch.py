"""Cohort diffusion trajectories on a weeks-since-launch x-axis.

Removes the calendar-time head-start artifact present in
14_visualize_long_horizon_trajectories.py: there both cohorts share a
calendar x-axis, so the July (pre-cutoff) cohort is mechanically ahead
because it was released ~13 weeks earlier. Here both cohorts start at
week 0 (each package's first observed positive download week) so the
gap reflects diffusion under treatment, not the calendar offset.

Produces a 1x2 figure: median (typical package) vs mean (aggregate
volume). The median panel is the honest backup against the mdurl
outlier dependence flagged in CLAUDE.md Issue 4.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import RAW_DIR, FINAL_DIR, FIG_APPENDIX, CHATGPT_RELEASE
from utils import setup_plotting_style, normalize_name


COHORT_PRE = "July 2021 (Pre-Cutoff)"
COHORT_POST = "October 2021 (Post-Cutoff)"


def main():
    setup_plotting_style()
    figures_dir = FIG_APPENDIX
    figures_dir.mkdir(parents=True, exist_ok=True)

    print("Loading cohort metadata...")
    df_meta = pd.read_csv(
        FINAL_DIR / "analysis_Main_2021.csv",
        usecols=["package", "dist_to_cutoff", "post_ai_downloads_alltime"],
    )
    df_meta["cohort"] = "Other"
    df_meta.loc[df_meta["dist_to_cutoff"].between(-12, -9), "cohort"] = COHORT_PRE
    df_meta.loc[df_meta["dist_to_cutoff"].between(1, 4), "cohort"] = COHORT_POST
    df_meta = df_meta[df_meta["cohort"] != "Other"].copy()
    print(f"  Cohort sizes: {df_meta['cohort'].value_counts().to_dict()}")

    print("Loading PyPI weekly panel...")
    df_panel = pd.read_parquet(
        RAW_DIR / "pypi_downloads.parquet",
        columns=["project", "week_start", "downloads"],
    )
    df_panel["package"] = normalize_name(df_panel["project"])
    df_panel["week_start"] = pd.to_datetime(df_panel["week_start"])
    df_panel = df_panel.merge(df_meta[["package", "cohort"]], on="package", how="inner")

    # Per-package launch week = first week with strictly positive downloads.
    print("Computing weeks since launch per package...")
    pos = df_panel[df_panel["downloads"] > 0]
    first_week = pos.groupby("package")["week_start"].min().rename("first_week")
    df_panel = df_panel.merge(first_week, on="package", how="inner")
    df_panel = df_panel[df_panel["week_start"] >= df_panel["first_week"]].copy()
    df_panel["weeks_since_launch"] = (
        (df_panel["week_start"] - df_panel["first_week"]).dt.days // 7
    )

    # Cap horizon at the smallest max-week observed across cohorts so the tail
    # is not driven by survivorship of the older cohort alone.
    cohort_max = df_panel.groupby("cohort")["weeks_since_launch"].max()
    horizon = int(cohort_max.min())
    print(f"  Cohort max weeks: {cohort_max.to_dict()}  -> shared horizon: {horizon}")
    df_panel = df_panel[df_panel["weeks_since_launch"] <= horizon].copy()

    # Aggregate: mean and median weekly downloads per (cohort, week-of-life).
    agg_mean = (
        df_panel.groupby(["weeks_since_launch", "cohort"])["downloads"]
        .mean()
        .reset_index()
    )
    agg_median = (
        df_panel.groupby(["weeks_since_launch", "cohort"])["downloads"]
        .median()
        .reset_index()
    )

    # Cumulative within cohort (over weeks-since-launch, not calendar).
    for agg in (agg_mean, agg_median):
        agg.sort_values(["cohort", "weeks_since_launch"], inplace=True)
        agg["cum_downloads"] = agg.groupby("cohort")["downloads"].cumsum()

    # Median weekly downloads can be 0 in early weeks for many packages; replace
    # zeros with NaN so the log axis does not blow up. Cumulative is fine.
    agg_median.loc[agg_median["downloads"] <= 0, "downloads"] = np.nan

    print("Rendering side-by-side weeks-since-launch trajectories...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=True)

    panels = [
        (axes[0, 0], agg_median, "downloads",
         "Median Weekly Downloads (Typical Package)",
         "Median Weekly Downloads (Log)"),
        (axes[0, 1], agg_mean, "downloads",
         "Mean Weekly Downloads (Aggregate Volume)",
         "Mean Weekly Downloads (Log)"),
        (axes[1, 0], agg_median, "cum_downloads",
         "Cumulative Median Weekly Downloads",
         "Cumulative Median (Log)"),
        (axes[1, 1], agg_mean, "cum_downloads",
         "Cumulative Mean Weekly Downloads",
         "Cumulative Mean (Log)"),
    ]

    for ax, data, ycol, title, ylabel in panels:
        sns.lineplot(
            data=data, x="weeks_since_launch", y=ycol,
            hue="cohort", ax=ax, linewidth=1.8,
            hue_order=[COHORT_PRE, COHORT_POST],
        )
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel("Weeks Since First Observed Download")
        ax.set_ylabel(ylabel)
        ax.set_yscale("log")
        ax.legend(title="Library Cohort", loc="lower right", fontsize=8)

    fig.suptitle(
        "Long-Horizon Diffusion on a Common-Origin Axis: July (Pre) vs October (Post) 2021",
        fontweight="bold", fontsize=13,
    )
    plt.tight_layout()
    out_path = figures_dir / "long_horizon_trajectory_weeks_since_launch.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved: {out_path}")

    # Slide-friendly single-panel cumulative-mean version, matching the layout
    # of the existing calendar-axis cumulative plot but on weeks-since-launch.
    fig2, ax2 = plt.subplots(figsize=(12, 7))
    sns.lineplot(
        data=agg_mean, x="weeks_since_launch", y="cum_downloads",
        hue="cohort", ax=ax2, linewidth=2,
        hue_order=[COHORT_PRE, COHORT_POST],
    )

    # ChatGPT release falls at a different week-of-life for each cohort because
    # the cohorts launched at different calendar dates. Draw two color-matched
    # markers (one per cohort) computed from each cohort's median launch week.
    cohort_launch = first_week.to_frame().merge(
        df_meta[["package", "cohort"]], on="package", how="inner"
    )
    chatgpt = pd.Timestamp(CHATGPT_RELEASE)
    cohort_chatgpt_weeks = {}
    for cohort_name, sub in cohort_launch.groupby("cohort"):
        median_launch = sub["first_week"].median()
        weeks_to_chatgpt = (chatgpt - median_launch).days // 7
        cohort_chatgpt_weeks[cohort_name] = weeks_to_chatgpt

    # Match line colors to seaborn's default cohort palette.
    palette = dict(zip([COHORT_PRE, COHORT_POST], sns.color_palette(n_colors=2)))
    for cohort_name, w in cohort_chatgpt_weeks.items():
        ax2.axvline(
            w, color=palette[cohort_name], linestyle="--", alpha=0.85, linewidth=1.6,
            label=f"ChatGPT release, {cohort_name.split(' (')[0]} cohort (week {w})",
        )

    ax2.set_title(
        "Cumulative Diffusion Advantage on a Common-Origin Axis",
        fontweight="bold",
    )
    ax2.set_xlabel("Weeks Since First Observed Download")
    ax2.set_ylabel("Cumulative Mean Weekly Downloads (Log)")
    ax2.set_yscale("log")
    ax2.legend(loc="lower right", fontsize=9)
    plt.tight_layout()
    out_path_single = figures_dir / "long_horizon_cumulative_weeks_since_launch.png"
    plt.savefig(out_path_single, dpi=300)
    print(f"Saved: {out_path_single}")
    print(f"  ChatGPT week-of-life per cohort: {cohort_chatgpt_weeks}")


if __name__ == "__main__":
    main()
