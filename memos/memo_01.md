# Comprehensive Project History & Results Memo: LLM Cutoffs and Library Diffusion

**Date:** March 10, 2026  
**Subject:** Technical Evolution and Final Empirical Findings of the Master’s Thesis  
**Status:** Finalized Baseline Analysis

---

## 1. Project Genesis: The Research Question
This thesis began with a fundamental question in the economics of technology: **Does the "static knowledge" of Large Language Models (LLMs) shape the adoption of new software tools?**

As LLMs like GPT-3.5 and GPT-4 become primary interfaces for developers, their training cutoffs (e.g., September 2021) create a potential "knowledge wall." Libraries released *before* the cutoff are "known" to the model; libraries released *after* the cutoff are "invisible" to the model's weights at the time of deployment.

**The Hypothesis (H1):** Libraries released just before a cutoff will diffuse significantly faster than those released just after, due to this "Pre-training Advantage."

---

## 2. Phase 1: Data Construction (From Scratch)
We built a high-frequency (weekly) panel of the Python ecosystem following a conservative linkage strategy:

1.  **PyPI Universe:** Full set of PyPI libraries. "Release Week" defined as the first week of recorded positive downloads.
2.  **GitHub Linkage:** Merged with a GitHub panel counting `import` statements in public repositories.
3.  **Matching:** Done via normalized names. Only ~3% of PyPI libraries have detectable GitHub usage at this scale.
4.  **AI Scores:** Integrated commit-level scores to test if any "Pre-training Advantage" is stronger for AI-assisted developers.

---

## 3. Phase 2: Initial RDD Implementation
We applied a **Regression Discontinuity Design (RDD)** around the September 2021 cutoff.

*   **Initial Findings:** Early passes using standard inference suggested a significant drop in adoption for post-cutoff libraries.
*   **Complication:** These results proved highly sensitive to the choice of estimator and the handling of seasonality.

---

## 4. Phase 3: The "September Effect" and Seasonality
To validate the 2021 finding, we ran "Placebo Cutoffs" for the same calendar date in 2018, 2019, and 2020. 

**The Discovery:** Significant adoption "dips" occur in multiple placebo years (e.g., 2018 and 2020).
*   **Conclusion:** The Python ecosystem has a recurring **Seasonal Cycle**. September releases often underperform relative to summer releases, likely due to cyclic ecosystem behavior.
*   **Implication:** This seasonality complicates naive 2021 comparisons; we cannot easily attribute a 2021 drop to AI if it occurs regularly in placebo years.

---

## 5. Phase 4: Technical Refinement (Robust Inference)
Following supervisor feedback, we audited our identification strategy. Key refinements included:

1.  **Clustered Inference:** Shifting to **Week-Clustered Standard Errors** to account for mass points in the weekly running variable.
2.  **Sample Construction:** Moving to a "Full Sample" construction to avoid selection bias from pre-estimation filters (like a "zombie filter").

---

## 6. Phase 5: Diff-in-RDD as a Supportive Check
To separate seasonality from any potential "LLM Effect," we implemented a **Difference-in-RDD (Diff-in-RDD)** comparing 2021 against previous years.

*   **Finding:** Comparing 2021 to 2020 suggests that the 2021 seasonal dip was smaller than the 2020 dip.
*   **Status:** While informative, this is treated as a **secondary robustness check** because it relies on the strong assumption of "parallel discontinuities" between years and is sensitive to the choice of historical baseline.

---

## 7. Phase 6: Assumption-Free Robustness
We implemented two additional tests that do not rely on historical seasonal comparisons.

### A. Permutation Inference
We compared the September 2021 discontinuity to a distribution of discontinuities from 366 random "Monday Cutoffs."
*   **Result:** The 2021 discontinuity is indistinguishable from background noise in the permutation distribution ($p = 0.60$).
*   **Verdict:** September 2021 is not a statistically "unusual" week for library adoption.

### B. AI-Exposure Mechanism Split
We split the sample into **High AI Exposure** vs. **Low AI Exposure** libraries.
*   **Result:** The difference in RDD coefficients between the two groups was statistically zero ($p = 0.49$).
*   **Verdict:** Even among libraries heavily used in AI-generated code, exclusion from training data does not create a detectable barrier to adoption.

---

## 8. Final Conclusions (Synthesis)

### A. Estimator Hierarchy & Primary Results
The thesis adopts **rdrobust (Robust Bias-Corrected)** as the **Primary Estimator**. 

*   **Main Result:** We find no robust evidence of a broad "Knowledge Wall." The 2021 discontinuity is statistically null in the primary `rdrobust` specification ($p = 0.45$) and clustered WLS ($p = 0.66$).
*   **Successful Libraries:** A "Freshness Premium" appears among successful libraries in some estimators, but this result is sensitive to the specific model choice.

### B. Longitudinal Dynamics (Catch-up)
Longitudinal analysis suggests that any early adoption "tax" tends to disappear at 52 weeks, though the estimates remain noisy.

### C. Final Verdict
The software ecosystem appears resilient to technical training cutoffs. While LLMs shift individual developer workflows, they do not appear to steer aggregate ecosystem adoption toward older tools in a statistically robust way. The training cutoff is not a significant barrier to diffusion in the Python ecosystem.
