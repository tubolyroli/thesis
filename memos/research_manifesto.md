# Research Manifesto: The Evolution of the "Knowledge Wall" Thesis

**Project Title:** Do LLMs Know About New Things? Training Cutoffs and the Diffusion of Python Libraries  
**Researcher:** Roland Tuboly  
**Supervisor Perspective:** Dr. Gemini (Thesis Co-Supervisor)  
**Date:** March 11, 2026

---

## 1. The Core Research Question
Does the "static" nature of LLM training data (fixed cutoffs) create an adoption barrier for software tools released after that cutoff? We test if libraries present in the model's pre-training data (e.g., GPT-3.5/4's September 2021 cutoff) diffuse more widely than those released shortly after.

**Conceptual Benchmark:** Doshi and Hauser (2024). We apply their "individual enhancement vs. collective narrowing" logic to software: Do LLMs make developers faster at the cost of steering the whole ecosystem toward older, "known" libraries?

---

## 2. Chronological Evolution of the Research (Step-by-Step)

### Step 1: Scoping the "Interface Shock" (Sept 2021)
*   **Action:** Identified September 2021 as the critical cutoff for GPT-3.5 and GPT-4.
*   **Logic:** This date represents the "Knowledge Wall" that existed when ChatGPT was released in late 2022, potentially affecting how the first wave of AI-assisted developers discovered new tools.

### Step 2: Data Engineering & Measurement Discipline
*   **Action:** Built a high-frequency (weekly) panel of PyPI downloads and GitHub imports.
*   **Measurement:** Defined the **Running Variable** as the number of weeks relative to the September 1, 2021 cutoff.
*   **Unit of Observation:** Library-week level, aggregated to cumulative totals at 12, 26, and 52 weeks post-release.
*   **Restriction:** Applied a "1-year horizon" rule—only libraries with a full 52 weeks of post-release data are included to ensure fair comparison of long-run diffusion.

### Step 3: Establishing the Estimator Hierarchy
*   **Action:** Moved from simple OLS to a formal Regression Discontinuity Design (RDD).
*   **Primary Estimator:** `rdrobust` (Robust Bias-Corrected Local Linear Regression).
*   **Secondary Estimator:** Clustered WLS (Weighted Least Squares) and Permutation Inference.
*   **Logic:** `rdrobust` is the industry standard for minimizing bias near the cutoff, while WLS provides a sanity check on global trends.

### Step 4: The Discovery of the "Toy Package" Noise
*   **Action:** Observed high variance in the full sample. Introduced the `min100` download threshold.
*   **Finding:** Most Python libraries are "dead on arrival" (zero or near-zero downloads). The real economic action is among libraries that reach a baseline of success.
*   **Result:** The `min100` sample revealed a **positive "Freshness Premium"** ($\beta \approx 0.16$), suggesting successful new tools actually outperform older ones, even without LLM training inclusion.

### Step 5: The "September Effect" Pivot (Placebo Testing)
*   **Action:** Ran RDDs on "Placebo Cutoffs" (Sept 2018, 2019, 2020).
*   **Finding:** A significant adoption "dip" occurs every September, regardless of LLM training dates.
*   **Logic:** This shifted the narrative from "LLM exclusion" to "Seasonality." We cannot attribute the 2021 drop to AI if it happens every year.

### Step 6: Permutation & Diff-in-RDD
*   **Action:** Ran 366 random "Monday Cutoffs" across 7 years to build a distribution of "natural" adoption jumps.
*   **Finding:** The 2021 discontinuity is indistinguishable from background noise ($p = 0.60$).
*   **Action:** Implemented **Difference-in-RDD** ($RD_{2021} - RD_{2020}$) to net out the seasonal effect.

### Step 7: Mechanism Testing (AI vs. Human)
*   **Action:** Used AI-exposure scores from GitHub commits to split the sample.
*   **Finding:** No significant difference in the RDD coefficient between high-AI and low-AI usage libraries.
*   **Interpretation:** Even libraries heavily used in AI-generated code do not suffer from the training cutoff.

### Step 8: Longitudinal & Distributional Extensions (Response to Supervisor)
*   **Action:** Analyzed horizons at 12, 26, and 52 weeks to test for **Catch-up Dynamics**.
*   **Finding:** A small -5% dip at 12 weeks recovers to a +3.5% gain by 52 weeks, suggesting any LLM exclusion cost is temporary.
*   **Action:** Implemented **Quantile RDD** (Median) to address outlier concerns and measure level-based adoption jumps.
*   **Finding:** A robust "Post-Cutoff Bonus" exists across the distribution (+169 at median, +1,653 at Q90).
*   **Action:** Developed the **"Relative Suppression"** framework by stacking historical cutoffs (2018-2020).
*   **Finding:** The 2021 adoption boost was **90% smaller** than the historical seasonal average, providing the strongest evidence of LLM-driven adoption suppression.

---

## 3. Final Thesis Logic & Estimands

### Primary Estimand
The Local Average Treatment Effect (LATE) of being released *after* a documented LLM training cutoff on cumulative library adoption at 52 weeks.

### Identifying Assumptions
1.  **Continuity:** All other factors affecting adoption (besides the LLM cutoff) vary smoothly across the threshold.
2.  **No Manipulation:** Library authors do not strategically time their releases based on anticipated LLM training dates (highly plausible).

### Main Threats to Identification (and mitigations)
1.  **Seasonality:** Addressed via Placebo Cutoffs and Diff-in-RDD.
2.  **Release-Date Ambiguity:** Addressed via a **2-week Donut-Hole RDD** (excluding libraries released within 7 days of the cutoff).
3.  **Outliers:** Addressed via log-transformations and the `min100` success filter.

---

## 4. Current Findings Summary
1.  **Resilience:** The software ecosystem is remarkably resilient to LLM "knowledge gaps."
2.  **No Knowledge Wall:** Broad adoption patterns are not significantly altered by exclusion from training data.
3.  **Freshness Premium:** Among successful tools, "newness" is a stronger signal than "LLM-knowability."
4.  **Seasonality Caution:** The most significant "dips" in adoption are driven by cyclic ecosystem behavior, not technical training artifacts.

---

## 5. Remaining Work & Future Extensions
*   **Refine Linkage:** Improve the PyPI-to-GitHub matching rate to increase power.
*   **2023 Interface Shock:** Deepen the analysis of the Jan 2023 "ChatGPT adoption wave."
*   **Formal Writing:** Transition these findings into the Methods and Results chapters of the thesis.
