# Final Results Tables: LLM Knowledge Cutoffs & Python Diffusion
**Date:** Thursday, March 19, 2026
**Status:** Finalized Empirical Estimates

---

## Table 1: PyPI Diffusion Results (Package Adoption)
*This table summarizes the impact of the September 2021 knowledge cutoff on library downloads across different success tiers and identification strategies.*

| Specification | Tier / Subsample | Outcome Variable | Estimate (Log) | Std. Err | P-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Main RDD (2021)** | Broad (min 10) | 52-week Downloads | **9.571** | 2.670 | 0.000*** | 527,361 |
| | Broad (min 10) | Post-AI Downloads | **13.103** | 4.494 | 0.004** | 527,361 |
| | Successful (min 500) | Post-AI Downloads | -0.195 | 3.125 | 0.950 | 407,110 |
| **Diff-in-RDD** | Broad (min 10) | Excess Jump (Post-AI) | **-9.139** | 2.542 | 0.000*** | 88,001 |
| (2021 vs Placebos) | Successful (min 500) | Excess Jump (Post-AI) | **-12.792** | 1.775 | 0.000*** | 75,313 |
| | Superstar (min 1000) | Excess Jump (Post-AI) | **-0.553** | 0.092 | 0.000*** | 57,931 |
| **Mechanism Split** | Low AI Exposure | 52-week Downloads | **-1.178** | 0.541 | 0.029* | 602 |
| (Exploratory) | High AI Exposure | 52-week Downloads | 0.329 | 0.436 | 0.450 | 521 |

*Note: Significance levels: *** p<0.001, ** p<0.01, * p<0.05. Main RDD uses rdrobust (Robust) inference. Diff-in-RDD uses WLS with week-clustered standard errors.*

---

## Table 2: GitHub Implementation Results (Library Usage)
*This table focuses on the implementation mechanism using the matched GitHub sample, testing whether the effect is stronger in actual code usage and AI-steered implementation.*

| Specification | Outcome Variable | Estimate (Log) | Std. Err | P-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Main RDD (2021)** | 52-week Imports | 11.554 | 10.778 | 0.284 | 28,243 |
| | GPT-4 Era Imports | **23.256** | 11.541 | 0.044* | 28,243 |
| | Post-AI Imports (Total) | **26.767** | 10.932 | 0.014* | 28,243 |
| | All-Time Imports | **27.863** | 9.987 | 0.005** | 28,243 |
| **Mechanism Test** | AI Score Intensity | -0.140 | 5.064 | 0.978 | 8,566 |
| **Mechanism Split** | Low AI Exposure (Imports) | 0.386 | 0.308 | 0.211 | 602 |
| (Exploratory) | High AI Exposure (Imports) | 0.325 | 0.276 | 0.239 | 521 |

*Note: Matched GitHub sample includes libraries identified in both PyPI and the AI-scored GitHub commit panel. All outcomes are log-transformed (log(1+y)).*

---
*End of final results.*
