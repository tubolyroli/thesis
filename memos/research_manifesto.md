# Research Manifesto: The Evolution of the "Knowledge Wall" Thesis

**Project Title:** Do LLMs Know About New Things? Training Cutoffs and the Diffusion of Python Libraries  
**Made by:** Roland Tuboly  
**Supervisor:** Johannes Wachs
**Date:** March 21, 2026

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
*   **Measurement:** Defined the **Running Variable** as the number of weeks relative to the September 27, 2021 cutoff.
*   **Release Date Proxy:** Following standard practice for noisy package metadata, we use the **First Observed Positive PyPI Download Week** as the initial release date.
*   **Unit of Observation:** Library-week level, aggregated to cumulative totals at 12, 26, and 52 weeks post-release.

### Step 3: Establishing the Estimator Hierarchy
*   **Action:** Used a formal Regression Discontinuity Design (RDD).
*   **Primary Estimator:** `rdrobust` (Robust Bias-Corrected Local Linear Regression).
*   **Diagnostics:** Conducted formal **Density Tests** and **Monday Alignment Checks**.

### Step 4: Identifying the "Suppression" Fact
*   **Action:** Observed that libraries released post-cutoff suffered a significant adoption penalty.
*   **Result:** Diff-in-RDD estimates revealed a **-12.79 log point "Excess Jump"** for successful libraries relative to historical seasonal norms.

### Step 5: The Discovery of the "Barrier to Entry" (Success Filter)
*   **Action:** Audited the "Success Filter" (min 500 downloads @ 26w) for selection bias.
*   **Finding:** Libraries released post-cutoff are **14.5 percentage points (p < 0.0001)** less likely to even reach the successful tier.
*   **Logic:** The "Knowledge Wall" doesn't just slow growth; it fundamentally reduces the probability of ecosystem survival.

### Step 6: The "Activation" Smoking Gun
*   **Action:** Visualized trajectories through Jan 2026.
*   **Finding:** The diffusion gap was **dormant** before Nov 2022. It only "activated" once ChatGPT made the dated training knowledge a mass-market interface.

### Step 7: Mechanism Testing (Implementation vs. Discovery)
*   **Action:** Compared PyPI downloads (interest) against GitHub imports (usage).
*   **Finding:** The suppression is **twice as large** in actual code implementation (26.7 log points) as in general interest (13.1 log points).

### Step 8: Refined Heterogeneity (The Systemic Wall)
*   **Action:** Used a formal **Interacted WLS Model** to test if AI exposure moderates the effect.
*   **Finding:** The "AI Shield" effect is directional but **not statistically significant** ($p=0.179$), suggesting the Knowledge Wall is a systemic ecosystem-wide barrier.

---

## 3. Final Thesis Logic & Estimands

### Primary Estimand
The Local Average Treatment Effect (LATE) of being released *after* a documented LLM training cutoff on the probability of reaching a success threshold and on subsequent cumulative adoption.

### Identifying Assumptions
1.  **Continuity:** All other factors affecting adoption vary smoothly across the threshold.
2.  **Activation:** In the absence of LLM steering, there should be no divergence between cohorts until Nov 2022.
3.  **Parallel Discontinuities:** Seasonal adoption patterns in 2021 should follow historical averages (2018-2020) but for the LLM effect.

### Main Threats to Identification
1.  **Seasonality:** Addressed via Placebo Cutoffs and Diff-in-RDD.
2.  **Release-Date Ambiguity:** Addressed via a **9-week Donut-Hole RDD**.
3.  **Selection Bias:** Formally identified and discussed as the "Barrier to Entry" finding.

---

## 4. Final Findings Summary
1.  **The Suppression Fact:** Post-cutoff libraries suffer a **-12.8 log point penalty** in diffusion.
2.  **The Barrier Fact:** Post-cutoff libraries are **14.5% less likely to succeed** at all.
3.  **The Implementation Gap:** LLMs steer actual usage twice as much as general interest.
4.  **The Persistence Fact:** No evidence of catch-up as of early 2026.

---

## 5. Status
The empirical pipeline is finalized, methodologically audited, and fully synchronized across scripts, data, and documentation.
