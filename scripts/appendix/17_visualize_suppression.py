import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import FINAL_DIR, RESULTS_DIR, FIGURES_DIR, DONUT_WEEKS, DEFAULT_BW, MIN_SUCCESS_LOW
from utils import setup_plotting_style

def main():
    setup_plotting_style()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load 2018-2020 (Placebos) and 2021 (Main)
    placebos = ["Placebo_2018", "Placebo_2019", "Placebo_2020"]
    main_cutoff = "Main_2021"
    
    dfs = []
    
    # Load Main 2021
    main_path = FINAL_DIR / f"analysis_{main_cutoff}.csv"
    if main_path.exists():
        df_main = pd.read_csv(main_path)
        df_main["period"] = "2021 (LLM Cutoff)"
        dfs.append(df_main)
    
    # Load Placebos
    for p in placebos:
        p_path = FINAL_DIR / f"analysis_{p}.csv"
        if p_path.exists():
            df_p = pd.read_csv(p_path)
            df_p["period"] = "2018-2020 (Placebos)"
            dfs.append(df_p)
            
    if not dfs:
        print("Required analysis files not found.")
        return

    df = pd.concat(dfs, ignore_index=True)
    
    # 2. Filter for "Successful" Libraries (min 500 at 26 weeks)
    df_success = df[df["cum_downloads_26wk"] >= MIN_SUCCESS_LOW].copy()
    print(f"Sample size (Successful @ 26w): {len(df_success)}")

    # 3. Preparation for Plotting
    h = DEFAULT_BW # Match the bandwidth from Diff-in-RDD
    outcome = "post_ai_downloads_alltime"
    
    # Apply Donut and Bandwidth
    df_plot = df_success[~df_success["dist_to_cutoff"].isin(DONUT_WEEKS)].copy()
    df_plot = df_plot[(df_plot["dist_to_cutoff"] >= -h) & (df_plot["dist_to_cutoff"] <= h)].copy()
    
    df_plot["log_y"] = np.log1p(df_plot[outcome])
    
    # 4. Binscatter Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bin averages for cleaner visualization
    bins = df_plot.groupby(["dist_to_cutoff", "period"])["log_y"].mean().reset_index()
    
    sns.scatterplot(data=bins, x="dist_to_cutoff", y="log_y", hue="period", style="period", s=100, ax=ax)
    
    # Fit regression lines separately for pre/post and period
    for period in bins["period"].unique():
        sub = df_plot[df_plot["period"] == period]
        # Pre-cutoff
        sns.regplot(data=sub[sub["dist_to_cutoff"] < 0], x="dist_to_cutoff", y="log_y", 
                    scatter=False, ax=ax, label=f"{period} Pre", 
                    line_kws={'linestyle':'-' if "2021" in period else '--', 'alpha':0.8})
        # Post-cutoff
        sns.regplot(data=sub[sub["dist_to_cutoff"] >= 0], x="dist_to_cutoff", y="log_y", 
                    scatter=False, ax=ax, label=f"{period} Post",
                    line_kws={'linestyle':'-' if "2021" in period else '--', 'alpha':0.8})

    ax.axvline(0, color="black", linestyle=":", alpha=0.5)
    ax.set_title(f"Visualizing the 'Suppression' Effect: 2021 vs Historical Norms\n(Subsample: Successful Libraries, min {MIN_SUCCESS_LOW} downloads @ 26w)", fontsize=13, fontweight='bold')
    ax.set_xlabel("Weeks since Cutoff (Sept 2021 vs. Sept Placebos)", fontsize=11)
    ax.set_ylabel("Log Post-AI Cumulative Downloads", fontsize=11)
    
    # Custom Legend
    handles, labels = ax.get_legend_handles_labels()
    # Only keep the scatterplot handles for simplicity in legend
    ax.legend(handles[:2], labels[:2], title="Cohort Period", loc="best")
    
    # Annotate the suppression
    ax.annotate("Suppression Gap", xy=(5, 12), xytext=(8, 11),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8))

    plt.tight_layout()
    out_path = FIGURES_DIR / f"suppression_visual_success_{MIN_SUCCESS_LOW}.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved suppression plot to {out_path}")

if __name__ == "__main__":
    main()
