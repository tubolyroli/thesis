# Final Results Tables: LLM Knowledge Cutoffs & Python Diffusion
**Date:** Thursday, March 19, 2026
**Status:** Finalized Empirical Estimates

---

## Table 1: PyPI Diffusion Results (Package Adoption)
*This table summarizes the impact of the September 2021 knowledge cutoff on library downloads across different success tiers and identification strategies. Estimates are log-transformed (log(1+y)).*

| Specification | Tier / Subsample | Outcome Variable | Robust (BC) | Conv. | Std. Err (Conv) | P-value (Conv) | N |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Main RDD (2021)** | Broad (min 10) | 52-week Downloads | **9.571** | 1.985 | 0.224 | 0.000*** | 527,361 |
| | Broad (min 10) | Post-AI Downloads | **13.103** | 1.980 | 0.352 | 0.000*** | 527,361 |
| | Successful (min 500) | Post-AI Downloads | -0.195 | -0.120 | 0.271 | 0.658 | 407,110 |
| **Diff-in-RDD** | Broad (min 10) | Excess Jump (Post-AI) | **-9.139** | -- | 2.542 | 0.000*** | 88,001 |
| (2021 vs Placebos) | Successful (min 500) | Excess Jump (Post-AI) | **-12.792** | -- | 1.775 | 0.000*** | 75,313 |
| | Superstar (min 1000) | Excess Jump (Post-AI) | **-0.553** | -- | 0.092 | 0.000*** | 57,931 |

*Note: Significance levels for Conventional estimates: *** p<0.001, ** p<0.01, * p<0.05. Main RDD reports both Bias-Corrected 'Robust' and 'Conventional' estimates from rdrobust. The 'Robust' estimate is more sensitive to bandwidth choice but accounts for local linear bias. Diff-in-RDD uses WLS with week-clustered standard errors (coefficient matches Conventional RDD logic).*

---

## Table 2: GitHub Implementation Results (Library Usage)
*This table focuses on the implementation mechanism using the matched GitHub sample, testing whether the effect is stronger in actual code usage and AI-steered implementation.*

| Specification | Outcome Variable | Robust (BC) | Conv. | Std. Err (Conv) | P-value (Conv) | N |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Main RDD (2021)** | 52-week Imports | 11.554 | 0.328 | 0.897 | 0.715 | 28,243 |
| | GPT-4 Era Imports | **23.256** | 0.791 | 0.936 | 0.399 | 28,243 |
| | Post-AI Imports (Total) | **26.767** | 1.158 | 0.873 | 0.185 | 28,243 |
| | All-Time Imports | **27.863** | 1.456 | 0.804 | 0.070 | 28,243 |

*Note: The 'Activation' claim is most visible in the GitHub Imports data, where implementation results are statistically insignificant at the 52-week (pre-ChatGPT) horizon (p > 0.7 for Conventional, p = 0.28 for Robust) but show growing coefficients and decreasing p-values as the AI-mediated period expands.*

*Note: Matched GitHub sample includes libraries identified in both PyPI and the AI-scored GitHub commit panel. All outcomes are log-transformed (log(1+y)).*

---
*End of final results.*
