# Do LLMs Shape the Diffusion of New Software?
### Training Cutoffs and Adoption Dynamics in the Python Ecosystem

**Author:** Roland Tuboly  
**Supervisor:** Johannes Wachs  

---

## 1. Research Overview
This project investigates whether the "static" knowledge of Large Language Models (LLMs) creates an adoption barrier for new software tools. Specifically, we test if libraries released shortly **before** a major LLM training cutoff (September 2021 for GPT-3.5/4) diffuse more widely than those released shortly **after**.

**The "Knowledge Wall" Hypothesis:** If LLMs steer developers toward tools they "know" from their training data, then libraries excluded from that data may face a significant discovery tax, leading to reduced collective variety in the software ecosystem.

---

## 2. Empirical Strategy
We employ a **Regression Discontinuity Design (RDD)** around the September 1, 2021 cutoff.

*   **Running Variable:** Weeks since the September 2021 cutoff.
*   **Treatment:** A library's inclusion in the LLM's pre-training data (proxied by release date).
*   **Outcomes:** Cumulative PyPI downloads and GitHub imports at 12, 26, and 52 weeks post-release.
*   **Identification:** 
    *   **Donut-RDD:** We exclude a 2-week "donut hole" around the cutoff to handle release date ambiguity.
    *   **Diff-in-RDD:** We net out seasonal effects by comparing the 2021 discontinuity to historical "placebo" cutoffs (2018–2020).
    *   **Quantile RDD:** We use Median RDD to ensure results are robust to the "superstar" outliers typical of software adoption.

---

## 3. Key Findings

### 3.1. The "Relative Suppression" Result (Primary Finding)
While a naive RDD shows a positive "freshness bonus" for new libraries in 2021 (+169 downloads at the median), this is a massive **90% suppression** compared to the historical seasonal average of +1,694 downloads.
*   **Interpretation:** The LLM cutoff did not create an absolute "dip" from zero, but it decimated the natural growth momentum that new Python tools typically enjoy in late September.

### 3.2. The "Catch-up" Dynamic
Longitudinal analysis reveals an initial adoption "tax" (-5% at 12 weeks) that recovers to a positive gain (+3.5% at 52 weeks). 
*   **Interpretation:** LLM exclusion creates **temporary delays** in adoption, not permanent exclusion. Successful libraries eventually overcome the "knowledge gap" through other ecosystem channels.

### 3.3. Mechanism Test: AI-Mediated Usage
Exploratory split-sample RDDs on libraries with high vs. low AI-exposure (scored GitHub commits) show no significant difference in the adoption gap. 
*   **Interpretation:** Even libraries heavily used in AI-generated code do not suffer disproportionately from training exclusion.

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
