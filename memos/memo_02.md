# Memo 02: Advanced RDD Results - Catch-up, Median, and Relative Suppression

**Date:** March 11, 2026  
**Subject:** Empirical Results from Distributional and Longitudinal Analysis  
**Status:** Phase 2 Results (Responding to Faculty Feedback)

---

## 1. Executive Summary
Following the supervisor's feedback on long-run outcomes and outliers, we extended the RDD analysis to include **multiple time horizons** (12, 26, 52 weeks) and **quantile-based estimation** (Median RDD). These tests suggest potential nuance in the adoption-cutoff relationship, though the "average" log-mean effect remains statistically noisy and null in primary specifications.

---

## 2. Longitudinal Analysis: The "Catch-up" Hypothesis
We tested whether the exclusion from LLM training data leads to a permanent exclusion or merely a temporary delay in adoption.

| Horizon | RDD Estimate (Log Downloads) | P-value | Interpretation |
| :--- | :--- | :--- | :--- |
| **12 Weeks** | **-0.0501** | 0.344 | Suggestive initial ~5% "tax" |
| **26 Weeks** | **+0.0658** | 0.271 | Mid-year recovery |
| **52 Weeks** | **+0.0350** | 0.589 | Long-run catch-up |

**The "Dip-and-Recovery" Pattern:** While the point estimates show a sign-flip from negative to positive over the first year, they remain statistically insignificant. This provides **suggestive but not conclusive** support for the **Catch-up Hypothesis**: if libraries face an initial "discovery tax," they may overcome it through other ecosystem channels within 52 weeks.

---

## 3. Distributional Analysis: Beyond the Mean (Quantile RDD)
To address concerns that a few high-growth outliers were skewing the results, we moved from mean-based models to **Quantile RDD** (Median).

| Quantile | Estimate (Level Downloads) | P-value | Method |
| :--- | :--- | :--- | :--- |
| **Q25 (Small)** | **+122.3** | **0.0000** | QuantReg (0.25) |
| **Q50 (Median)** | **+168.7** | **0.0045** | QuantReg (0.50) |
| **Q75 (High)** | **+715.8** | **0.0001** | QuantReg (0.75) |
| **Q90 (Superstar)** | **+1653.1** | **0.0075** | QuantReg (0.90) |

**Finding:** In level-based Quantile RDDs, we observe a positive **"Post-Cutoff Bonus."** However, this finding is sensitive to the choice of estimator and does not necessarily imply an LLM-driven effect; it may reflect a broader "Freshness Premium" where newness is a positive signal for adopters, regardless of training inclusion.

---

## 4. The "Relative Suppression" Framework (Stacked Analysis)
To test if the 2021 result is simply a reflection of normal seasonality, we compared the 2021 discontinuity to a **Stacked Average of Placebos (2018-2020)**.

*   **Stacked Placebo Jump (Median):** **+1,694 downloads** (Historical Average)
*   **Main 2021 Jump (Median):** **+169 downloads** (LLM Year)

**Thesis Argument:** While the 2021 jump is positive, it is significantly smaller than the historical seasonal average. This suggests a **"Relative Suppression"** story: the training cutoff may not have created a "dip" from zero, but it may have dampened the natural growth momentum that new tools typically enjoy in late September. However, this interpretation is sensitive to the choice of historical baseline and the parallel discontinuities assumption.

---

## 5. Mechanism Check: AI-Mediated Usage
We split the sample into libraries with high vs. low AI-scored GitHub usage.

*   **Finding:** The difference-in-discontinuities between High-AI and Low-AI groups was **+0.36 log points (p=0.49)**.
*   **Interpretation:** The result is statistically null. We do not find robust evidence that AI-exposed tools are more or less affected by the training cutoff than their counterparts.

---

## 6. Final Result Synthesis for Thesis
1.  **Suggestive Catch-up:** Any early adoption disadvantage appears to be temporary, though the results are not yet robust.
2.  **Relative Suppression as an Alternative Narrative:** The "cost" of the training cutoff is best framed not as an absolute drop, but as a potential dampening of seasonal growth momentum.
3.  **Estimator Sensitivity:** The positive "Freshness Premium" is estimator-dependent and must be interpreted with caution in the final thesis text.
