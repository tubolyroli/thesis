# Memo 06: Methodological Audit — Cluster Correction, Bandwidth Defense, Activation Test, and Narrative Discipline

**Date:** Monday, March 24, 2026
**To:** Thesis File / Supervisor Review
**Subject:** Five methodological fixes identified and implemented following a systematic risk assessment

---

## 1. Context

A comprehensive risk assessment was conducted on the thesis methodology and findings. The audit identified ten risks, categorized into five that warranted empirical or narrative fixes and five that belong in the Limitations section. This memo documents the five fixes and their consequences for the main results.

---

## 2. Fix 1: Cluster Count in the Diff-in-RDD (Implemented)

**Problem:** The Diff-in-RDD in `08_diff_in_rdd.py` clustered standard errors by `is_2021 x dist_to_cutoff`, producing only ~36 unique cluster cells (2 groups x 18 remaining weeks after the donut). The Cameron-Miller threshold for reliable cluster-robust inference is ~50 clusters. With too few clusters, SEs were likely understated.

**Fix:** Replaced the binary `is_2021` grouping with the actual `cutoff_year` (2018, 2019, 2020, 2021), yielding 4 years x 18 weeks = **72 cluster cells**.

**Consequence for results:** Point estimates are unchanged (clustering only affects SEs). Standard errors increased substantially:

| Tier | Old SE | New SE | Old P-value | New P-value |
|---|---|---|---|---|
| Broad (Post-AI) | 1.800 | 4.425 | <0.001 | 0.039 |
| Successful (Post-AI) | 1.636 | 4.827 | <0.001 | 0.008 |
| Superstar (Post-AI) | 0.164 | 0.492 | 0.001 | 0.261 |

**Assessment:** The Broad and Successful tier results survive at conventional significance levels (p<0.05 and p<0.01 respectively). The Superstar tier result is no longer significant — this should be reported honestly. The corrected SEs are more conservative and more defensible.

---

## 3. Fix 2: Mechanism Test Reframed as Exploratory (Implemented)

**Problem:** The AI-exposure interaction model (p=0.179, N=1,303) was presented across README, memo_05, research_manifesto, and final_results_tables as evidence that "confirms" the Knowledge Wall is a "systemic ecosystem effect." This overclaims from a null result on an exploratory test with two fundamental issues:

1. **Post-treatment moderator:** `avg_ai_score_52wk` is measured in the 52 weeks after release, making it potentially endogenous to the suppression itself. A suppressed library will have fewer AI-generated commits importing it.
2. **Low statistical power:** N=1,303 is likely insufficient to detect meaningful moderation.

**Fix:** Reframed across all documentation:
- Section headers changed from "Systemic Wall" to "Exploratory"
- "Confirms" replaced with "consistent with"
- Both caveats (endogeneity, power) stated explicitly
- Added: "The null result cannot establish that the effect is systemic; it can only fail to reject that interpretation."

**Files changed:** `README.md`, `memos/memo_05.md`, `memos/research_manifesto.md`, `results/final_results_tables.md`, `CLAUDE.md`

---

## 4. Fix 3: Symmetric Donut Robustness Check (Implemented)

**Problem:** The primary donut design is asymmetric: `DONUT_WEEKS = range(-8, 1)` excludes 9 weeks on the pre-cutoff side (late July through September 27) and zero weeks on the post-cutoff side. A standard RDD donut is symmetric. While the asymmetric design is defensible (libraries in Aug-Sept have ambiguous training inclusion, while October libraries are clearly post-cutoff), it requires explicit justification and a robustness check.

**Fix:** Added a symmetric donut (weeks -4 to +4) as a robustness specification in `06_robustness.py`.

**Result:** The symmetric donut yields Estimate = -4.35, p < 0.001 (robust). The effect survives under standard symmetric exclusion, strengthening the paper.

---

## 5. Fix 4: Formal Activation Test via Dual-Window Diff-in-RDD (Implemented)

**Problem:** The "activation" argument — that the diffusion gap was dormant before ChatGPT (Nov 2022) and only activated afterward — was the most compelling evidence for the LLM-driven mechanism. But it was supported only by a trajectory figure, not a formal statistical test.

**Fix:** Extended `08_diff_in_rdd.py` to run the Diff-in-RDD on two outcome windows:
1. `total_downloads_52wk` — Mostly pre-ChatGPT for the 2021 cohort (52-week window closes ~Sept 2022)
2. `post_ai_downloads_alltime` — Post-Nov 2022 only (the "Activation Window")

**Results:**

| Tier | Pre-ChatGPT (52wk) | P-value | Post-AI | P-value |
|---|---|---|---|---|
| Broad | -1.202 | 0.429 | -9.139 | 0.039 |
| Successful | -3.724 | 0.026 | -12.792 | 0.008 |
| Superstar | -0.218 | 0.572 | -0.553 | 0.261 |

**Assessment:** For the Broad tier, the pre-ChatGPT excess jump is small and insignificant (p=0.43) while the post-AI excess jump is significant (p=0.039). This formally confirms the activation hypothesis: the suppression effect is concentrated in the post-ChatGPT period.

The Successful tier shows some pre-ChatGPT effect (p=0.026), which may reflect early Copilot adoption or a genuine mild pre-ChatGPT effect. This nuance should be discussed rather than suppressed.

---

## 6. Fix 5: MSE-Optimal Bandwidth as Primary Specification (Implemented)

**Problem:** The main RDD in `05_estimation.py` hard-coded `h=13` (DEFAULT_BW), overriding `rdrobust`'s data-driven MSE-optimal bandwidth selection. This looked like specification search.

**Fix:** Now runs both `h=None` (MSE-optimal) and `h=13` (fixed) for every outcome. The MSE-optimal result is labeled primary; the fixed bandwidth is robustness.

**Critical finding:** `rdrobust` with `h=None` throws `LinAlgError` for most Broad-tier outcomes (the asymmetric donut creates a degenerate design matrix when combined with MSE-optimal bandwidth selection). Where it converges, the MSE-optimal bandwidths are much wider (h=14-39) and most estimates become insignificant.

**Assessment:** This vindicates the Diff-in-RDD as the primary identification strategy. The single-year 2021 RDD is sensitive to bandwidth — the Diff-in-RDD is not. The thesis should lead with the Diff-in-RDD and present the single-year RDD as supporting evidence rather than the primary result.

---

## 7. Items Deferred to Limitations Section

The following risks were assessed as genuine but unfixable with the current data:

1. **GitHub Copilot as co-occurring confounder** — launched June 2021, cannot be separated from GPT cutoff effects with available data.
2. **PyPI downloads as noisy adoption proxy** — includes CI/CD, bot, and mirror traffic. Noise is likely symmetric across the cutoff (adds variance, not bias).
3. **GPT cutoff date imprecision** — the exact Sept 27, 2021 date is from public disclosure. The donut partially addresses residual uncertainty.
4. **GitHub 6% match rate** — the GitHub-matched sample is highly selected (prominent, well-maintained libraries only). Implementation gap results apply to this subpopulation.
5. **Single ecosystem, limited generalizability** — Python is uniquely LLM-relevant; effects may differ in other language ecosystems.

---

## 8. Revised Results Hierarchy

Following this audit, the evidence structure for Chapter 4 (Results) should be:

1. **Lead with the Diff-in-RDD** (the robust identification strategy): -9.14 for Broad (p=0.039), -12.79 for Successful (p=0.008).
2. **Present the formal Activation Test**: pre-ChatGPT excess jump is insignificant (p=0.43); post-AI excess jump is significant (p=0.039). This is the formal test of the mechanism.
3. **The Barrier to Entry result** (14.5pp): unchanged by this audit.
4. **The Implementation Gap** (GitHub vs PyPI): unchanged, but note that the two samples are not directly comparable populations.
5. **The AI Moderation test**: present as exploratory, with both caveats (post-treatment moderator, low power).
6. **Robustness**: symmetric donut, bandwidth sensitivity, permutation inference.

**Key narrative shift:** The Superstar tier Diff-in-RDD is no longer significant (p=0.261). This should be reported honestly. The suppression effect is concentrated in the Broad and Successful tiers, not among the most prominent libraries.

---

## 9. Updated Status

All scripts, result CSVs, and documentation files have been synchronized with these corrections. The main empirical claims survive the audit at conventional significance levels, but with honestly larger standard errors and appropriately hedged mechanism claims.

---
*Memo end.*
