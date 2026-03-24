# Memo 05: Final Empirical Synthesis — The "Knowledge Wall" and Barriers to Entry

**Date:** Saturday, March 21, 2026  
**To:** Thesis File / Supervisor Review  
**Subject:** Finalized Empirical Evidence after Methodological Audit

---

## 1. Executive Summary: The "Knowledge Wall"
This memo provides the definitive empirical synthesis of the thesis following a rigorous methodological audit. The central finding remains a statistically significant and substantively large "suppression" of Python library diffusion for cohorts released after the September 2021 LLM training cutoff. However, the audit has refined the mechanism: the cutoff acts less like a "speed bump" for growth and more like a **"Knowledge Wall"** that creates a systemic barrier to entry, particularly for high-potential libraries.

## 2. The "Barrier to Entry" Fact: Selection Bias as Substantive Finding
A critical discovery during the final audit is the presence of significant selection bias in the "Success" threshold. Libraries released immediately after the September 2021 cutoff are **14.5 percentage points (p < 0.0001)** less likely to reach the "Successful" tier (min. 500 downloads at 26 weeks) than their pre-cutoff counterparts.

**Thesis Implication:**  
This finding suggests that the "Suppression Fact" reported in earlier memos was an **underestimate**. By conditioning the analysis on "Successful" libraries, we were inadvertently comparing "elite survivors" in the post-cutoff group against a broader distribution in the pre-cutoff group. The cutoff does not merely slow down diffusion; it fundamentally reduces the probability that a new library will ever achieve a meaningful foothold in the ecosystem.

## 3. Definitive Causal Estimates (Post-Audit)
The following estimates employ **Robust Bias-Corrected (BC)** coefficients and **Robust P-values** via `rdrobust`, with **Year-by-Week Clustering** for the Diff-in-RDD to ensure valid inference.

### Table 1: Finalized Diffusion & Suppression Estimates
| Model / Specification | Outcome Variable | Estimate (Log) | SE | P-value | N |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Main RDD (2021)** | 52-week Downloads | 9.572* | 2.670 | 0.000*** | 527,361 |
| **Main RDD (2021)** | Post-AI Downloads | 13.103* | 4.494 | 0.004** | 527,361 |
| **Diff-in-RDD** | Excess Jump (Broad) | -9.139† | 4.425 | 0.039* | 88,001 |
| **Diff-in-RDD** | Excess Jump (Successful) | -12.792† | 4.827 | 0.008** | 75,313 |

*\*) Robust SE (Bias-Corrected). †) Cluster-Robust SE (Year-by-Week).*

**Interpretation:** After differencing out historical seasonal norms, the September 2021 cutoff uniquely suppressed the adoption of "Successful" libraries by **12.79 log points**. This effect is remarkably stable across bandwidths ($h \ge 13$).

## 4. Exploratory Mechanism Test: AI Exposure Moderation
The final audit replaced approximate Z-tests with a formal **Fully Interacted WLS Model** to test if AI exposure (measured via commit AI scores) moderates the suppression effect.

*   **Interaction Coefficient:** 0.396
*   **Standard Error:** 0.295
*   **P-value:** 0.179
*   **N:** 1,303

**Interpretation (with caveats):**
While directionally suggesting that High AI exposure libraries suffer less suppression, the interaction is **not statistically significant** at conventional levels. This result is *consistent with* the Knowledge Wall operating as a broad ecosystem effect, but two important caveats prevent a stronger claim:

1.  **Post-treatment moderator:** The AI exposure variable (`avg_ai_score_52wk`) is measured in the 52 weeks after release and is therefore potentially endogenous to treatment. A library that was suppressed will have fewer AI-generated commits importing it — the moderator may partly reflect the treatment itself rather than serving as an independent channel.
2.  **Low statistical power:** With N=1,303 (the GitHub-matched subsample), the test is likely underpowered to detect meaningful moderation even if it exists.

The null result cannot establish that the effect is systemic; it can only fail to reject that interpretation. The Discussion chapter should present this as exploratory evidence rather than a confirmed mechanism.

## 5. Transition to Thesis Writing: Chapter 4 (Results) Template
When drafting Chapter 4, the evidence should be sequenced as follows:

1.  **Baseline Diffusion (Main RDD):** Establish the raw discontinuity in the 2021 cohort. Use the "Activation" argument: the gap was dormant at release and only emerged after the mass adoption of ChatGPT (Nov 2022).
2.  **Identification (Diff-in-RDD):** Use the placebo-comparison to prove this isn't just "autumn seasonality." The 2021 cohort is uniquely shifted downward relative to 2018-2020.
3.  **The "Barrier to Entry" Result:** Present the 14.5% drop in success probability. Argue that the cutoff suppresses the *emergence* of new quality tools.
4.  **Mechanism (Implementation vs. Discovery):** Show that the gap is **twice as large** in GitHub implementation (26.7 log points) as in PyPI downloads (13.1 log points).
5.  **Robustness & Placebos:** Report the non-significant interaction model and the stable bandwidth sensitivity, acknowledging the limits of identification at extremely narrow windows ($h < 13$).

---
**Status:** All empirical scripts are synchronized with these findings. The repository is ready for a final "Push to Submission."
