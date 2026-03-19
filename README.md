# Do LLMs Shape the Diffusion of New Software?
### Training Cutoffs and Adoption Dynamics in the Python Ecosystem

**Author:** Roland Tuboly  
**Supervisor:** Johannes Wachs  

---

## 🚀 Quick Summary: The "Cutoff Tax" & Suppression
The empirical phase of this thesis is now complete. We have established three core facts:
1.  **The Suppression Fact:** Libraries released after the September 2021 cutoff suffer a **-12.79 log point "Excess Jump"** in adoption relative to historical seasonal norms (2018–2020). This "cutoff tax" is heaviest for high-potential "successful" libraries.
2.  **The Activation Mechanism:** The implementation gap (actual code usage) was **dormant** before ChatGPT. It only activated once the model became a mass interface (Nov 2022). While interest-level downloads (PyPI) show a detectable earlier gap, the steering of actual developer tool-choice is strictly a post-AI phenomenon.
3.  **Vulnerability:** Suppression is concentrated in **"Low AI Exposure"** libraries. Tools that are both excluded from the model's training data and "unprotected" by AI-mediated generation suffer the most.

### 📊 Core Empirical Evidence (September 2021 Cutoff)

#### Table 1: PyPI Diffusion Results (Package Adoption)
| Specification | Tier / Subsample | Outcome Variable | Estimate (Log) | P-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Diff-in-RDD** | **Successful (min 500)** | **Excess Jump (Post-AI)** | **-12.792** | **0.000\*\*\*** | **75,313** |
| (2021 vs Placebos) | Broad (min 10) | Excess Jump (Post-AI) | -9.139 | 0.000*** | 88,001 |
| **Main RDD (2021)** | Broad (min 10) | Post-AI Downloads | 13.103 | 0.004** | 527,361 |
| **Mechanism Split**| Low AI Exposure | 52-week Downloads | -1.178 | 0.029* | 602 |

#### Table 2: GitHub Implementation Results (Library Usage)
| Specification | Outcome Variable | Estimate (Log) | P-value | N |
| :--- | :--- | :--- | :--- | :--- |
| **Main RDD (2021)** | **Post-AI Imports (Total)** | **26.767** | **0.014*** | **28,243** |
| | All-Time Imports | 27.863 | 0.005** | 28,243 |
| | GPT-4 Era Imports | 23.256 | 0.044* | 28,243 |

*Note: All outcomes are log-transformed (log(1+y)). Full results available in [results/final_results_tables.md](results/final_results_tables.md).*

---

## 📍 What to Read First
Reviewing this project for the first time, I recommend this order:
1.  **[memos/memo_04.md](memos/memo_04.md)**: **The Final Verdict.** Definitive summary of the "Suppression" framework, success filters, and finalized causal estimates.
2.  **[results/final_results_tables.md](results/final_results_tables.md)**: **The Evidence.** Core tables for PyPI adoption and GitHub implementation.
3.  **[memos/research_manifesto.md](memos/research_manifesto.md)**: **The High-Level Map.** Chronological evolution of the research design, from Step 1 (Scoping) to Step 8 (Relative Suppression).

---

## 1. Research Overview
This project investigates whether the "static" knowledge of Large Language Models (LLMs) creates an adoption barrier for new software tools. Specifically, we test if libraries released shortly **before** a major LLM training cutoff (September 2021 for GPT-3.5/4) diffuse more widely than those released shortly **after**.

**The "Knowledge Wall" Hypothesis:** If LLMs steer developers toward tools they "know" from their training data, then libraries excluded from that data may face a significant discovery tax, leading to reduced collective variety in the software ecosystem.

---

## 2. Empirical Strategy
We employ a **Regression Discontinuity Design (RDD)** at the September 27, 2021 cutoff, refined by a **Difference-in-Discontinuities (Diff-in-RDD)** to isolate the treatment effect from seasonal growth patterns.

*   **Primary Estimator:** `rdrobust` (local linear regression) for the 2021 cohort.
*   **Identification Hub:** **Diff-in-RDD** comparing the 2021 discontinuity to pooled historical placebos (2018–2020).
*   **Success Filters:** Libraries are tiered by their "Pre-GPT Success" (cumulative downloads at 26 weeks, measured strictly before Nov 2022) to isolate high-potential tools.
*   **Mechanism Tests:** AI-scored GitHub commit data is used to test whether the discontinuity is stronger in AI-mediated usage.

---

## 3. Key Findings

### 3.1. The "Suppression" Discovery (Diff-in-RDD)
By differencing out historical norms, we find that the September 2021 cutoff **uniquely suppressed** the seasonal adoption boost usually seen in autumn releases.
*   **Successful Tier (min 500 downloads):** Excess Jump of **-12.79 (p < 0.001)**.
*   **Broad Tier (min 10 downloads):** Excess Jump of **-9.14 (p < 0.001)**.
*   **Interpretation:** The "cutoff tax" is not a uniform penalty; it is **40% larger** for high-potential libraries than for the broad population.

### 3.2. The "Activation" Smoking Gun
The diffusion gap is not an immediate property of the release date; it is an **LLM-driven phenomenon** that only fully activated once the model became a mass interface.
*   **Implementation Gap (GitHub):** Statistically **insignificant** at the 52-week pre-ChatGPT horizon (Conventional p=0.72, Robust p=0.28). Developers were not uniquely biased against post-cutoff tools until they began using LLMs for code generation.
*   **Discovery Gap (PyPI):** More sensitive to estimation; while Bias-Corrected estimates show an earlier gap, the **implementation gap** in GitHub usage (Estimate: 26.8) is **twice as large** as the interest gap in PyPI downloads (Estimate: 13.1), confirming the mechanism of AI-steered implementation.

### 3.3. Mechanism: AI Exposure as a "Protective" Factor
Suppression is concentrated in libraries with **Low AI Exposure** (proxied by the average AI-score of GitHub commits).
*   **Low AI Exposure:** Significant negative discontinuity (p = 0.029).
*   **High AI Exposure:** Statistically null (p = 0.45).
*   **Interpretation:** Libraries "excluded" from LLM knowledge but "unprotected" by AI-mediated discovery suffer the most. High AI-exposure libraries appear to bridge the adoption gap through LLM-steered implementation.

### 3.4. Persistence: No Catch-up
Long-horizon trajectories (2021–2024) confirm that the initial diffusion gap is **persistent**.
*   Post-cutoff libraries show no sign of catching up to their pre-cutoff counterparts as of late 2024.

---

## 4. Repository Structure

### 📂 `data/`
Contains raw, intermediate, and analysis-ready datasets.
*   `data/intermediate/pypi_base.parquet`: Optimized aggregation of 159M PyPI download rows.
*   `data/final/analysis_Main_2021.csv`: The primary merged dataset (PyPI + GitHub).

### 📂 `scripts/` (Pipeline Order)
1.  **`01_build_pypi_base.py`**: Optimized two-pass processing of PyPI downloads.
2.  **`03_merge_and_restrict.py`**: Merges PyPI and GitHub, applies success filters.
3.  **`05_estimation.py`**: Estimates RDD across success tiers and adoption horizons.
4.  **`08_diff_in_rdd.py`**: **The Core Identification.** Estimates the "Suppression" effect using pooled placebos.
5.  **`10_ai_mechanism_split.py`**: Tests for heterogeneity by AI exposure.
6.  **`11_visualize_results.py`**: Generates the "Activation" and "Suppression" visuals.

### 📂 `results/`
*   `final_results_tables.md`: Core empirical tables.
*   `figures/`: Thesis-ready visualizations (Activation trajectories, suppression barplots).

---

## 5. Getting Started

### Prerequisites
*   Python 3.10+
*   Dependencies listed in `requirements.txt`.

### Reproducing the Results
To run the full estimation and visualization suite:
```bash
# 1. Run the estimation suite (Main & Diff-in-RDD)
./.venv/bin/python scripts/05_estimation.py
./.venv/bin/python scripts/08_diff_in_rdd.py

# 2. Run mechanism tests
./.venv/bin/python scripts/10_ai_mechanism_split.py

# 3. Generate visualizations
./.venv/bin/python scripts/11_visualize_results.py
```

---
