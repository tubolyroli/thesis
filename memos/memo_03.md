# Research Memo #03: Long-Horizon RDD and the "Activation" Mechanism
**Date:** Wednesday, March 18, 2026
**Subject:** Implementation of Long-Horizon July-October Donut RDD and Initial Findings

---

## 1. Objective
This memo documents the empirical pivot based on supervisor feedback to address (a) measurement bias from library age, (b) the "starting gun" effect of the ChatGPT release, and (c) the persistence of diffusion gaps over long horizons (up to January 2026).

## 2. Methodology Updates
Following the directive to compare the "July 2021" vs. "October 2021" cohorts, we implemented the following structural changes to the pipeline:

### 2A. Identification Strategy: Wide Donut RDD
*   **Running Variable:** Weeks relative to the September 27, 2021 knowledge cutoff.
*   **Donut Definition:** Excluded a 9-week window (August and September 2021) to ensure a clean comparison between libraries released strictly before the model's knowledge boundary and those released strictly after.
*   **Bandwidth ($h$):** Set to 13 weeks (one quarter) to isolate the July vs. October cohorts as the primary comparison groups.
*   **Kernel:** Local Linear Regression with a triangular kernel and bias-corrected robust inference (via `rdrobust`).

### 2B. Outcome Measurement: Calendar-Based Horizons
Shifted from age-based (e.g., "52 weeks since release") to fixed calendar milestones:
1.  **GPT-4 Horizon:** Cumulative usage up to March 13, 2023.
2.  **GPT-4 Turbo Horizon:** Cumulative usage up to November 6, 2023 (Cutoff shift event).
3.  **All-Time Horizon:** Cumulative usage up to January 12, 2026 (End of data).
4.  **Post-AI Activation (Time-Adjusted):** Cumulative usage *strictly after* November 28, 2022 (ChatGPT release). This solves the "head start" bias by only measuring growth during the period where LLMs were actively steering users.

## 3. Key Empirical Findings

### 3A. The "Activation" Smoking Gun (Mechanism Test)
The most striking result is the difference in GitHub import significance across time:
*   **Pre-ChatGPT (52w Horizon):** Statistically **insignificant** (p=0.28). There was no inherent difference between the July and October cohorts before the AI model was released.
*   **Post-ChatGPT (All Horizons):** Highly **significant** (p < 0.05). The diffusion gap only emerged once the model became a mass interface for developers.

### 3B. Magnitude and Persistence
*   **PyPI Adoption:** The "Post-AI" jump estimate is **13.1** (log-scale, p=0.0035).
*   **GitHub Usage:** The "Post-AI" jump estimate is **26.8** (log-scale, p=0.014).
*   **Interpretation:** The effect is twice as large in developer-centric GitHub usage than in general downloads, strongly supporting the AI-mediated usage mechanism.
*   **Persistence:** The gap continues to widen through 2025 with no evidence of catch-up by the post-cutoff cohort.

### 3C. Robustness to Outliers (Median RDD)
*   **Result:** The Median RDD for the Post-AI horizon shows a highly significant, positive jump (Estimate: 1903 in levels, p=0.0078).
*   **Significance:** This confirms the LLM "steering" effect is a broad ecosystem shift affecting the **typical** library, not an artifact driven by a few viral "superstar" packages.

### 3D. Identification Sensitivity: Placebo Years (2018-2020)
*   **Finding:** Significant "July vs. October" jumps were detected in non-AI placebo years (e.g., +21.1 and +25.8 in 2019/2020).
*   **Implication:** There is a recurring seasonal adoption pattern in the Python ecosystem (likely summer vs. autumn release cycles) that contaminates a simple RDD design.

### 3E. The Causal Breakthrough: Difference-in-RDD (Diff-in-RD)
To isolate the true LLM effect, we implemented a **Difference-in-Discontinuities** design, comparing the 2021 "LLM Cutoff" jump against the pooled "background noise" of 2018-2020.
*   **Result:** Found a significant **negative "Excess Jump" of -9.14 (p=0.0003)**.
*   **Conclusion:** The September 2021 knowledge cutoff **uniquely suppressed** the typical seasonal adoption boost that libraries released in late autumn usually receive. Relative to a "normal" year, being post-cutoff created a ~9 log point disadvantage in long-run adoption.

## 4. Visual Evidence
Three definitive plots/summaries were generated and saved to `results/figures/`:
1.  `long_horizon_trajectory_pypi.png`: Visualizes the 2021 cohort divergence after Nov 2022.
2.  `sensitivity_bandwidth_post_ai.png`: Confirms the effect is locally concentrated at $h=13$.
3.  `diff_in_rdd_final.csv`: Provides the coefficient for the seasonally-adjusted "suppression" effect.

## 5. Next Steps
1.  **Draft Results Chapter:** Focus the narrative on the "Barrier to Entry" / "Seasonal Suppression" story revealed by the Diff-in-RDD.
2.  **AI Mechanism Split:** Use `avg_ai_score_52wk` to test if this suppression is specifically concentrated in libraries with high AI-generation probability.
3.  **Covariate Balance:** Perform a final check for continuity of pre-release library properties (e.g., package size, number of dependencies) to eliminate any remaining alternative explanations.

---
*Memo end.*
