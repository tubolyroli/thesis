import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import MAIN_ANALYSIS_DATA, RESULTS_DIR, FIGURES_DIR, DONUT_WEEKS
from utils import setup_plotting_style

def plot_horizon_coefficients():
    """Plots RDD estimates across different time horizons."""
    results_path = RESULTS_DIR / "estimation_results_final.csv"
    if not results_path.exists():
        print("Error: Estimation results not found.")
        return
        
    df = pd.read_csv(results_path)
    horizon_df = df[df["Label"].str.contains("Horizon:")].copy()
    horizon_df["weeks"] = horizon_df["Label"].str.extract("(\d+)").astype(int)
    horizon_df = horizon_df.sort_values("weeks")
    
    setup_plotting_style()
    plt.figure(figsize=(8, 6))
    plt.errorbar(horizon_df["weeks"], horizon_df["Estimate"], 
                 yerr=horizon_df["Std.Err"] * 1.96, 
                 fmt='o-', color='darkblue', capsize=5, linewidth=2, markersize=8)
    plt.axhline(0, color='red', linestyle='--', alpha=0.6)
    plt.title("RDD Estimates across Adoption Horizons", fontsize=14)
    plt.xlabel("Weeks since Release", fontsize=12)
    plt.ylabel("Estimated Discontinuity (log downloads)", fontsize=12)
    plt.xticks([12, 26, 52])
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(FIGURES_DIR / "rdd_horizon_coefficients.png", dpi=300, bbox_inches='tight')

def plot_quantile_coefficients():
    """Plots RDD estimates across different percentiles."""
    results_path = RESULTS_DIR / "estimation_results_final.csv"
    if not results_path.exists(): return
    
    df = pd.read_csv(results_path)
    q_df = df[df["Label"].str.contains("Quantile:")].copy()
    q_df["quantile"] = q_df["Label"].str.extract("([\d\.]+)").astype(float)
    q_df = q_df.sort_values("quantile")
    
    setup_plotting_style()
    plt.figure(figsize=(8, 6))
    plt.errorbar(q_df["quantile"], q_df["Estimate"], 
                 yerr=q_df["Std.Err"] * 1.96, 
                 fmt='s-', color='darkgreen', capsize=5, linewidth=2, markersize=8)
    plt.axhline(0, color='red', linestyle='--', alpha=0.6)
    plt.title("RDD Estimates across Adoption Distribution", fontsize=14)
    plt.xlabel("Quantile (Adoption Percentile)", fontsize=12)
    plt.ylabel("Estimated Discontinuity (Level Downloads)", fontsize=12)
    plt.savefig(FIGURES_DIR / "rdd_quantile_coefficients.png", dpi=300, bbox_inches='tight')

def plot_faceted_binscatter():
    """Generates faceted binscatter plots for 12, 26, and 52-week horizons."""
    if not MAIN_ANALYSIS_DATA.exists(): return
    df_full = pd.read_csv(MAIN_ANALYSIS_DATA)
    df_vis = df_full[(df_full["total_downloads_52wk"] >= 10) & (~df_full["dist_to_cutoff"].isin(DONUT_WEEKS))].copy()
    
    horizons = [12, 26, 52]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharex=True)
    for i, h in enumerate(horizons):
        outcome = f"cum_downloads_{h}wk"
        df_vis[f"log_{outcome}"] = np.log1p(df_vis[outcome])
        bins = df_vis.groupby("dist_to_cutoff")[f"log_{outcome}"].mean().reset_index()
        sns.regplot(data=bins[bins["dist_to_cutoff"] < 0], x="dist_to_cutoff", y=f"log_{outcome}", 
                    ax=axes[i], scatter_kws={'alpha':0.4, 'color':'blue'}, line_kws={'color':'darkblue'}, ci=None)
        sns.regplot(data=bins[bins["dist_to_cutoff"] >= 0], x="dist_to_cutoff", y=f"log_{outcome}", 
                    ax=axes[i], scatter_kws={'alpha':0.4, 'color':'orange'}, line_kws={'color':'darkorange'}, ci=None)
        axes[i].axvline(0, color='black', linestyle='--', alpha=0.5)
        axes[i].set_title(f"{h}-Week Downloads")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "rdd_horizon_binscatters.png", dpi=300)

if __name__ == "__main__":
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_horizon_coefficients()
    plot_quantile_coefficients()
    plot_faceted_binscatter()
