# Finalized Empirical Results: Tables & Evidence

This document provides the definitive tables for the master's thesis, matching the rigorously identified results in the `results/*.csv` data records.

---

## 1. PyPI Diffusion: The "Suppression" Fact
**Model:** Diff-in-RDD (2021 cohort vs. 2018-2020 placebos)  
**Clustering:** Year-by-Week (Standardized across cohorts)

| Success Tier | Outcome Variable | Excess Jump (Causal) | Cluster SE | Robust P-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Broad (min 10)** | Post-AI Downloads | **-9.139** | 4.425 | 0.039* | 88,001 |
| **Successful (min 500)** | Post-AI Downloads | **-12.792** | 4.827 | 0.008** | 75,313 |
| **Superstar (min 1000)** | Post-AI Downloads | **-0.553** | 0.492 | 0.261 | 57,931 |

---

## 2. Main RDD Results (2021 Cohort Only)
**Estimator:** `rdrobust` (Robust Bias-Corrected)  
**Donut:** 9-week (August & September 2021)

### Table 2.1: Package Adoption (PyPI Downloads)
| Tier / Subsample | Outcome Variable | Robust Est. | Robust SE | Robust P-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Broad (min 10)** | 52-week Downloads | 9.572 | 2.670 | 0.000*** | 527,361 |
| **Broad (min 10)** | Post-AI Downloads | 13.103 | 4.494 | 0.004** | 527,361 |
| **Successful (min 500)** | Post-AI Downloads | -0.195 | 3.125 | 0.950 | 407,110 |

### Table 2.2: Library Implementation (GitHub Imports)
| Outcome Variable | Robust Est. | Robust SE | Robust P-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **52-week Imports** | 11.554 | 10.778 | 0.284 | 28,243 |
| **GPT-4 Era Imports** | 23.256 | 11.541 | 0.044* | 28,243 |
| **Post-AI Imports (Total)** | 26.767 | 10.932 | 0.014* | 28,243 |
| **All-Time Imports** | 27.863 | 9.987 | 0.005** | 28,243 |

---

## 3. Mechanism Test: AI Exposure Moderation (Exploratory)
**Model:** Interacted WLS with Week-clustered Standard Errors
**Outcome:** log(1 + 52-week outcome)
**Sample:** 2021 Cohort only (Within-bandwidth h=26)

| Outcome Variable | Diff-in-Discontinuity | Cluster SE | P-value | N |
| :--- | :--- | :--- | :--- | :--- |
| **total_downloads_52wk** | 0.396 | 0.295 | 0.179 | 1,303 |
| **cum_imports_52wk** | 0.257 | 0.292 | 0.380 | 1,303 |

> **Note:** The interaction term `treated:high_ai` identifies whether the discontinuity at the cutoff is statistically different between the High and Low AI exposure groups.

> **Caveat:** This test is exploratory. The AI-exposure moderator (`avg_ai_score_52wk`) is measured post-treatment and may be endogenous to the suppression itself. Additionally, N=1,303 likely provides insufficient power to detect meaningful moderation. The null result is *consistent with* a broad ecosystem effect but cannot confirm it.
