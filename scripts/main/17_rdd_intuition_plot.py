"""Slide-6 replacement figure: schematic RDD diagram (left) next to a
zoomed-in binscatter at h=13 (right). Replaces the global-window V-shape
plot, which required a window-edge-artefact caveat that ate presentation
time."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from config import FINAL_DIR, FIG_MAIN, DONUT_WEEKS
from utils import setup_plotting_style


def schematic_panel(ax):
    """Textbook-style RDD intuition: two regression lines on either side
    of a cutoff, with a clear vertical jump labeled β₁. No real data."""
    rng = np.random.default_rng(7)

    x_pre = np.linspace(-13, -1, 60)
    x_post = np.linspace(1, 13, 60)

    # Pre-cutoff trend: gentle downward
    # Post-cutoff jumps UP at the boundary (matches direction of real
    # pre-AI data at h=13 where seasonality boosts post-cutoff cohorts).
    y_pre_line = 6.85 - 0.012 * x_pre
    y_post_line = 7.55 + 0.012 * x_post

    y_pre = y_pre_line + rng.normal(0, 0.18, size=x_pre.size)
    y_post = y_post_line + rng.normal(0, 0.18, size=x_post.size)

    ax.scatter(x_pre, y_pre, color="#3b6fb5", s=22, alpha=0.55, edgecolor="none")
    ax.scatter(x_post, y_post, color="#e08a2c", s=22, alpha=0.55, edgecolor="none")
    ax.plot(x_pre, y_pre_line, color="#1f4e8c", linewidth=2.2)
    ax.plot(x_post, y_post_line, color="#c2680f", linewidth=2.2)

    ax.axvline(0, color="black", linestyle="--", alpha=0.55, linewidth=1.2)

    # Boundary jump arrow (post above pre)
    y_pre_at_zero = 6.85
    y_post_at_zero = 7.55
    arrow = FancyArrowPatch(
        (0.4, y_pre_at_zero), (0.4, y_post_at_zero),
        arrowstyle="<->", mutation_scale=14, color="black", linewidth=1.6,
    )
    ax.add_patch(arrow)
    ax.text(
        0.9, (y_pre_at_zero + y_post_at_zero) / 2,
        r"$\beta_1$" + "\n(boundary jump)",
        va="center", ha="left", fontsize=12,
    )

    ax.text(-12.5, 6.40, "Pre-cutoff", color="#1f4e8c", fontsize=11, fontweight="bold")
    ax.text(8.5, 8.00, "Post-cutoff", color="#c2680f", fontsize=11, fontweight="bold")

    ax.set_xlabel("Weeks from cutoff")
    ax.set_ylabel("Outcome (log scale)")
    ax.set_title("Single-year RDD: estimand", fontweight="bold")
    ax.set_xlim(-14, 14)
    ax.set_ylim(6.0, 8.2)
    ax.set_yticks([])  # schematic — no specific values
    ax.set_xticks([-13, -8, 0, 13])
    ax.grid(alpha=0.25)


def real_data_panel(ax):
    """Local binscatter at h=13 with donut [-8, 0] excluded. Outcome is
    log(1 + post-AI downloads alltime), matching the headline estimand."""
    df = pd.read_csv(FINAL_DIR / "analysis_Main_2021.csv",
                     usecols=["dist_to_cutoff", "post_ai_downloads_alltime", "is_pre_cutoff"])
    df = df[df["dist_to_cutoff"].between(-13, 13)].copy()

    donut_mask = df["dist_to_cutoff"].isin(DONUT_WEEKS)
    df_fit = df[~donut_mask].copy()
    df_fit["log_y"] = np.log1p(df_fit["post_ai_downloads_alltime"])

    bins = (df_fit.groupby(["dist_to_cutoff", "is_pre_cutoff"])["log_y"]
            .mean().reset_index())

    pre = bins[bins["is_pre_cutoff"] == 1]
    post = bins[bins["is_pre_cutoff"] == 0]

    ax.scatter(pre["dist_to_cutoff"], pre["log_y"],
               color="#3b6fb5", s=42, alpha=0.85, label="Pre-cutoff",
               edgecolor="white", linewidth=0.6)
    ax.scatter(post["dist_to_cutoff"], post["log_y"],
               color="#e08a2c", s=42, alpha=0.85, label="Post-cutoff",
               edgecolor="white", linewidth=0.6)

    # Local linear fits on bin means (a binscatter-style summary, not the
    # full rdrobust estimate, but visually consistent with one).
    for sub, color in [(pre, "#1f4e8c"), (post, "#c2680f")]:
        if len(sub) >= 2:
            slope, intercept = np.polyfit(sub["dist_to_cutoff"], sub["log_y"], 1)
            xs = np.linspace(sub["dist_to_cutoff"].min(), sub["dist_to_cutoff"].max(), 50)
            ax.plot(xs, intercept + slope * xs, color=color, linewidth=2.2)

    # Shade donut window
    ax.axvspan(min(DONUT_WEEKS), max(DONUT_WEEKS), color="grey", alpha=0.10)
    ax.text(np.mean(DONUT_WEEKS), ax.get_ylim()[1] if False else 0,
            "", ha="center")  # placeholder, real text below
    ax.axvline(0, color="black", linestyle="--", alpha=0.55, linewidth=1.2)

    ax.set_xlabel("Weeks from cutoff")
    ax.set_ylabel("Log post-AI downloads (alltime)")
    ax.set_title("Single-year RDD: data within bandwidth h = 13",
                 fontweight="bold")
    ax.set_xlim(-13.5, 13.5)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.25)

    # Annotate donut shading after axis limits set
    ymin, ymax = ax.get_ylim()
    ax.text(np.mean(DONUT_WEEKS), ymax - 0.05 * (ymax - ymin),
            "donut\nexcluded", ha="center", va="top", fontsize=9,
            color="#555555")


def main():
    setup_plotting_style()
    figures_dir = FIG_MAIN
    figures_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    schematic_panel(axes[0])
    real_data_panel(axes[1])

    plt.tight_layout()
    out_path = figures_dir / "rdd_intuition_schematic_vs_data.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
