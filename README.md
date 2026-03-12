# Do LLMs Shape the Diffusion of New Software?
### Training Cutoffs and Adoption Dynamics in the Python Ecosystem

**Author:** Roland Tuboly  
**Supervisor:** Johannes Wachs  

---

## 📍 What to Read First
Reviewing this project for the first time, I recommend this order:
1.  **[memos/research_manifesto.md](memos/research_manifesto.md)**: **The High-Level Map.** Chronological evolution of the research design, from Step 1 (Scoping) to Step 8 (Relative Suppression).
2.  **[memos/memo_02.md](memos/memo_02.md)**: **The Key Result.** Detailed breakdown of the Phase 2 breakthroughs: Median RDD and the "Relative Suppression" framework.
3.  **[master_analysis.ipynb](master_analysis.ipynb)**: **The Analysis Hub.** The primary notebook for visualizing results, comparing horizons, and interpreting the "Catch-up" dynamic.

---

## 1. Research Overview
This project investigates whether the "static" knowledge of Large Language Models (LLMs) creates an adoption barrier for new software tools. Specifically, we test if libraries released shortly **before** a major LLM training cutoff (September 2021 for GPT-3.5/4) diffuse more widely than those released shortly **after**.

**The "Knowledge Wall" Hypothesis:** If LLMs steer developers toward tools they "know" from their training data, then libraries excluded from that data may face a significant discovery tax, leading to reduced collective variety in the software ecosystem.

---

## 2. Empirical Strategy
We employ a **Regression Discontinuity Design (RDD)** at the September 27, 2021 cutoff.

*   **Primary Estimator:** `rdrobust` (local linear regression with bias-corrected inference).
*   **Secondary Estimators:** Clustered WLS and permutation-based inference (using placebo years 2018–2020).
*   **Supportive Analysis:** 
    *   **Donut-RDD:** Excluding a 2-week window to handle release date ambiguity.
    *   **Diff-in-RDD:** Comparing the 2021 discontinuity to historical seasonal averages (2018–2020) to net out potential seasonal effects.
    *   **Quantile RDD:** Using Median RDD to ensure results are robust to the extreme skew characteristic of software adoption.

---

## 3. Key Findings

### 3.1. Main Result: No Robust Evidence of a broad "Knowledge Wall"
In the primary 2021 sample, we do not find robust evidence that the LLM training cutoff significantly suppressed adoption for new libraries.
*   The 2021 discontinuity is statistically null under the primary `rdrobust` specification (p = 0.45) and clustered WLS (p = 0.66).
*   Permutation tests show that the 2021 discontinuity is not unusually negative relative to placebo years.

### 3.2. Seasonality and the "Suppression" Narrative
While naive comparisons suggest a "Relative Suppression" (where 2021 growth is lower than the historical seasonal average), this result is sensitive to the choice of seasonal baseline.
*   Seasonality likely matters and complicates naive 2021 comparisons.
*   Diff-in-RDD against 2020 points toward suppression, but it is treated as a secondary robustness check because it relies on a limited seasonal baseline.

### 3.3. Estimator Sensitivity and the "Freshness Premium"
A "freshness premium" (positive discontinuity) appears among successful libraries under the `rdrobust` estimator, but this finding is not strongly supported by clustered WLS.
*   **Interpretation:** LLM exclusion does not appear to create a uniform "discovery tax" across the entire ecosystem. Any observed effects are likely concentrated among specific subsets of libraries or sensitive to the choice of estimator.

### 3.4. The "Catch-up" Dynamic
Longitudinal analysis suggests that any early adoption "tax" tends to disappear at longer horizons (26 and 52 weeks).
*   **Interpretation:** LLM exclusion may create temporary delays in adoption, but successful libraries eventually overcome the "knowledge gap" through other ecosystem channels.

---

## 4. Repository Structure

### 📂 `data/`
Contains raw, intermediate, and analysis-ready datasets.
*   `data/final/analysis_Main_2021.csv`: The primary dataset for the thesis.

### 📂 `scripts/` (Pipeline Order)
1.  `01_build_pypi_base.py`: Processes PyPI data & constructs 52-week horizons.
2.  `02_aggregate_github.py`: Merges GitHub usage and AI-exposure scores.
3.  `03_merge_and_restrict.py`: Applies temporal filters and release date proxies.
4.  `05_estimation.py`: **The Main Engine.** Estimates RD across all horizons and quantiles.
5.  `06_robustness.py`: Bandwidth sensitivity and placebo tests for Median RDD.
6.  `11_visualize_results.py`: Generates all thesis-ready figures.
7.  `13_stacked_rdd.py`: Implements the Stacked Diff-in-RDD for the "Suppression" finding.

### 📂 `memos/`
Deep-dives and research logs for each phase of the project.
*   **[memos/research_manifesto.md](memos/research_manifesto.md)**: The "Living Document" tracking the evolution of every major research decision.
*   **[memos/memo_02.md](memos/memo_02.md)**: Detailed breakdown of Phase 2 (Median & Suppression) results.

---

## 5. Getting Started

### Prerequisites
*   Python 3.10+
*   Dependencies listed in `requirements.txt` (includes `rdrobust` and `statsmodels`).

### Installation
```bash
# 1. Clone the repository
git clone <repo-url>
cd thesis

# 2. Setup environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Reproducing the Results
To run the full estimation and visualization suite:
```bash
./.venv/bin/python scripts/05_estimation.py
./.venv/bin/python scripts/13_stacked_rdd.py
./.venv/bin/python scripts/11_visualize_results.py
```

---
