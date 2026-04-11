# Finalized Empirical Results: Tables & Evidence

This document provides the definitive tables for the master's thesis, matching the rigorously identified results in the `results/*.csv` data records. All estimates are on the log(1+Y) scale unless otherwise noted.

---

## 1. PyPI Diffusion: The "Suppression" Fact
**Model:** Diff-in-RDD (2021 cohort vs. 2018-2020 placebos)  
**Clustering:** Year-by-Week (Standardized across cohorts)

### Panel A: Pre-ChatGPT Baseline (52-week downloads, unadjusted)
| Success Tier | Outcome Variable | Excess Jump | Cluster SE | p-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Successful (min 500)** | 52-week Downloads | **-3.724** | 1.669 | 0.026* | 75,313 |

### Panel B: Post-ChatGPT Activation (baseline-adjusted, primary)
| Success Tier | Outcome Variable | Excess Jump | Cluster SE | p-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Broad (min 10)** | Post-AI Downloads | **-7.285** | 2.200 | 0.001** | 88,001 |
| **Successful (min 500)** | Post-AI Downloads | **-7.294** | 2.393 | 0.002** | 75,313 |
| **Superstar (min 1000)** | Post-AI Downloads | **-0.251** | 0.349 | 0.473 | 57,931 |

### Panel C: Post-ChatGPT Activation (unadjusted, for comparison)
| Success Tier | Outcome Variable | Excess Jump | Cluster SE | p-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Broad (min 10)** | Post-AI Downloads | **-9.139** | 4.425 | 0.039* | 88,001 |
| **Successful (min 500)** | Post-AI Downloads | **-12.792** | 4.827 | 0.008** | 75,313 |
| **Superstar (min 1000)** | Post-AI Downloads | **-0.553** | 0.492 | 0.261 | 57,931 |

> **Baseline adjustment:** Panel B controls for log(1 + 52-week downloads) as an ANCOVA-style covariate. This absorbs pre-existing level differences and halves the standard errors.

---

## 2. Main RDD Results (2021 Cohort Only)
**Estimator:** `rdrobust` (Robust Bias-Corrected)  
**Donut:** 9-week (August & September 2021)

### Table 2.1: Package Adoption (PyPI Downloads)
| Tier / Subsample | Outcome Variable | Robust Est. | Robust SE | Robust p-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Broad (min 10)** | 52-week Downloads | 9.572 | 2.670 | 0.000*** | 527,361 |
| **Broad (min 10)** | Post-AI Downloads | 13.103 | 4.494 | 0.004** | 527,361 |
| **Successful (min 500)** | Post-AI Downloads | -0.195 | 3.125 | 0.950 | 407,110 |

### Table 2.2: Library Implementation (GitHub Imports)
| Outcome Variable | Robust Est. | Robust SE | Robust p-value | N |
| :--- | :--- | :--- | :--- | :--- |
| **52-week Imports** | 11.554 | 10.778 | 0.284 | 28,243 |
| **GPT-4 Era Imports** | 23.256 | 11.541 | 0.044* | 28,243 |
| **Post-AI Imports (Total)** | 26.767 | 10.932 | 0.014* | 28,243 |
| **All-Time Imports** | 27.863 | 9.987 | 0.005** | 28,243 |

---

## 3. Mechanism Test: AI Exposure Moderation (Exploratory)
**Model:** Interacted WLS with Week-clustered Standard Errors  
**Sample:** 2021 Cohort only (Within-bandwidth h=26)

### Unadjusted
| Outcome Variable | Diff-in-Discontinuity | Cluster SE | p-value | N |
| :--- | :--- | :--- | :--- | :--- |
| **total_downloads_52wk** | 0.396 | 0.295 | 0.179 | 1,303 |
| **cum_imports_52wk** | 0.257 | 0.292 | 0.380 | 1,303 |

### Baseline-adjusted
| Outcome Variable | Diff-in-Discontinuity | Cluster SE | p-value | N |
| :--- | :--- | :--- | :--- | :--- |
| **cum_imports_52wk** | 0.165 | 0.273 | 0.546 | 1,303 |
| **post_ai_downloads_alltime** | -0.312 | 0.469 | 0.505 | 1,303 |
| **post_ai_imports_alltime** | -0.110 | 0.490 | 0.822 | 1,303 |

> **Caveat:** This test is exploratory. The AI-exposure moderator is measured post-treatment and may be endogenous. N=1,303 likely provides insufficient power. The null result is *consistent with* a broad ecosystem effect but cannot confirm it.

---

## 4. DV Summary Statistics (2021 Cohort, Within Bandwidth)

| Tier | Outcome | Mean | SD | N |
| :--- | :--- | :--- | :--- | :--- |
| Broad | 52-week Downloads | 7.44 | 1.86 | 30,450 |
| Broad | Post-AI Downloads | 7.51 | 3.20 | 30,450 |
| Successful (min 500) | 52-week Downloads | 8.32 | 1.16 | 22,477 |
| Successful (min 500) | Post-AI Downloads | 8.98 | 1.96 | 22,477 |
| Superstar (min 1000) | 52-week Downloads | 8.70 | 1.05 | 17,050 |
| Superstar (min 1000) | Post-AI Downloads | 9.44 | 1.85 | 17,050 |

> All values are for log(1+Y) transformed outcomes.

---

## 5. Bandwidth Sensitivity: Diff-in-RDD (Successful Tier, Post-AI Downloads)

| BW (weeks) | Unadjusted | p-value | Adjusted | p-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 13 | -12.792 | 0.008 | -7.294 | 0.002 | 75,313 |
| 15 | -10.804 | 0.001 | -6.301 | <0.001 | 92,291 |
| 18 | -7.786 | <0.001 | -4.498 | <0.001 | 119,296 |
| 26 | -4.274 | 0.003 | -2.372 | 0.001 | 196,602 |

> Baseline adjustment reduces magnitude but preserves sign and significance across all bandwidths.
