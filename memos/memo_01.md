# Comprehensive Project History & Results Memo: LLM Cutoffs and Library Diffusion

**Date:** March 10, 2026  
**Subject:** Technical Evolution and Final Empirical Findings of the Master’s Thesis  
**Status:** Finalized Baseline Analysis

---

## 1. Project Genesis: The Research Question
This thesis began with a fundamental question in the economics of technology: **Does the "static knowledge" of Large Language Models (LLMs) shape the adoption of new software tools?**

As LLMs like GPT-3.5 and GPT-4 become primary interfaces for developers, their training cutoffs (e.g., September 2021) create a potential "knowledge wall." Libraries released *before* the cutoff are "known" to the model and can be easily recommended; libraries released *after* the cutoff are "invisible" to the model's weights.

**The Hypothesis (H1):** Libraries released just before a cutoff will diffuse significantly faster than those released just after, due to this "Pre-training Advantage."

---

## 2. Phase 1: Data Construction (From Scratch)
We built a high-frequency (weekly) panel of the Python ecosystem. The construction followed a conservative linkage strategy:

1.  **PyPI Universe:** We started with the full set of PyPI libraries. The "Release Week" was defined as the first week a library recorded a positive download on PyPI.
2.  **GitHub Linkage:** We merged this with a massive GitHub panel that counts how many times a library is `import`-ed in public repositories.
3.  **The Matching Challenge:** Matching is done via normalized names (lowercasing, `_` to `-` conversion). We found that only ~3% of PyPI libraries have detectable GitHub usage at this scale—a finding that highlights the "Long-Tail" nature of software.
4.  **AI Scores:** We integrated commit-level scores (the probability that code was written by AI) to test if the "Pre-training Advantage" is stronger for AI-assisted developers.

---

## 3. Phase 2: The Initial RDD Implementation
We applied a **Regression Discontinuity Design (RDD)** around the September 27, 2021 cutoff (the documented GPT-3.5 cutoff).

*   **Initial Filter:** We originally applied a "zombie filter" (minimum 10 downloads in the first year) during data construction to remove spam/broken packages.
*   **Naive Results:** Our first pass using standard (HC1) inference showed a statistically significant **-10% drop** in downloads for libraries released after the cutoff. For a moment, it looked like the hypothesis was confirmed.

---

## 4. Phase 3: The "September Effect" Mystery (The Placebos)
To validate the 2021 finding, we ran "Placebo Cutoffs" for the same calendar date in 2018, 2019, and 2020. 

**The Discovery:** We found massive "dips" in 2018 (-27%) and 2020 (-120%)—years when GPT-3.5 didn't even exist. 
*   **Conclusion:** The Python ecosystem has a recurring **Seasonal Cycle**. September releases systematically underperform relative to summer releases, likely due to corporate budget cycles or academic semesters.
*   **The Problem:** Our 2021 "Main" result was being contaminated by this seasonality. We couldn't tell the difference between an "LLM Effect" and a "September Effect."

---

## 5. Phase 4: Technical Refinement (Robust Inference)
Following the mandates of the thesis co-supervisor, we performed a deep technical audit. We identified two major threats to our initial conclusions:

1.  **Mass Points in the Running Variable:** Our data is weekly. This means we have thousands of libraries sharing the same "Running Variable" values (e.g., 5,000 libraries all released exactly 3 weeks after the cutoff). Standard HC1 inference underestimates the noise in this structure.
    *   **The Fix:** We shifted to **Week-Clustered Standard Errors**, which treat each week (not each library) as the unit of independent variation.
2.  **Selection Bias:** The "Zombie Filter" (requiring >10 downloads) was being applied *before* the analysis. This created a bias: if the cutoff actually hurts adoption, it might "push" marginal libraries below the 10-download threshold, causing us to drop them from the data and underestimate the effect.
    *   **The Fix:** We moved to a "Full Sample" construction and only applied thresholds (`min10`, `min100`) as sensitivity checks in the estimation phase.

---

## 6. Phase 5: The Breakthrough (Diff-in-RDD)
To finally separate "Seasonality" from the "LLM Effect," we implemented a **Difference-in-RDD (Diff-in-RDD)**. This compares the 2021 jump against the 2020 seasonal baseline.

**The Final Result:**
*   **Diff-in-RDD Coefficient:** **+1.1297 (p=0.0388)**.
*   **Interpretation:** While both years saw a dip in September, the 2021 dip was **significantly smaller** than the 2020 dip. If the training cutoff were a barrier, we should have seen a *larger* dip in 2021. Instead, we see a relative gain.

---

## 7. Phase 6: Advanced Robustness (Permutation & Mechanism Splits)
To resolve the seasonality debate without making assumptions about previous years, we implemented two additional assumption-free tests.

### A. Alternative 1: Permutation Inference (Is Sept 2021 "Unusual"?)
Instead of comparing years, we compared September 27, 2021, to **every other Monday** in our dataset (366 random Mondays). 
*   **Method:** We ran 366 independent RDDs (WLS + HC1) to see how "unusual" the 2021 jump was relative to random weekly noise.
*   **Result:** 221 out of 366 random weeks (60%) had a larger adoption drop than our true cutoff.
*   **Verdict:** The September 2021 discontinuity is statistically indistinguishable from background noise (**one-sided $p = 0.60$, two-sided $p = 0.81$**).

### B. Alternative 2: Mechanism-Driven Split (AI vs. Human Usage)
We tested if the knowledge cutoff specifically hurts developers using AI. 
*   **Design:** We split the sample into **High AI Exposure** vs. **Low AI Exposure** libraries (Exploratory Appendix).
*   **Warning:** This analysis is descriptive/exploratory as it splits on a post-treatment variable (AI score).
*   **Result:** The difference in RDD coefficients between the two groups was statistically zero (**Z-score = 0.69, $p = 0.49$**).
*   **Verdict:** We find no evidence that AI-heavy development is more sensitive to the training cutoff. Even for libraries with high AI usage, being released after the cutoff does not create a detectable barrier to adoption.

---

## 8. Final Conclusions (As of March 10, 2026)

### A. Estimator Hierarchy & Primary Results
For the final thesis, we adopt **rdrobust (Robust Bias-Corrected)** as our **Primary Estimator** due to its superior handling of bias in local linear regressions. Clustered WLS and Permutation Inference are treated as secondary robustness checks.

*   **Main Result (Full Sample):** We find no statistically significant impact of the LLM training cutoff on broad library adoption (**Primary rdrobust: $\beta = 0.05$, $p = 0.45$**).
*   **Successful Libraries (min100):** For libraries that achieve a baseline of success, there is a **positive "Freshness Premium"** (**Primary rdrobust: $\beta = 0.16$, $p = 0.003$**). Being released after the cutoff is associated with *higher* adoption, directly contradicting the "Collective Narrowing" hypothesis.

### B. The 2023 "Interface Shock" Re-interpreted
With our standardized $Post - Pre$ sign convention, the **Adoption 2023** cutoff (Jan 2023) shows a **large negative jump** ($\beta = -1.68$, $p = 0.001$).
*   **Interpretation:** This does *not* mean the post-cutoff libraries were absolute failures. Instead, it highlights that **pre-cutoff libraries** (those released in late 2022) were the primary beneficiaries of the massive adoption spike triggered by ChatGPT's public release. 
*   Post-cutoff libraries released in early 2023, while successful, did not keep pace with the "gold rush" seen by tools that were already available when the shock hit.

### C. Thesis Final Verdict
The software ecosystem is highly resilient to technical artifacts like training cutoffs. While LLMs help developers code faster, they do not "steer" aggregate adoption toward older tools. The LLM training cutoff is not a barrier to diffusion; if anything, the "Freshness Premium" for successful tools suggests that the market continues to value new technology over training-set inclusion.
