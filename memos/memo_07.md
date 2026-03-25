# Memo 07: Thesis Writing, Barrier Sign Correction, Threat Strengthening, and Repository Cleanup

**Date:** Tuesday, March 25, 2026
**To:** Thesis File / Supervisor Review
**Subject:** Advances in thesis.tex, discovery of barrier-to-entry sign error, new threats added, repo cleaned for submission

---

## 1. Thesis Document Progress

The LaTeX document (`thesis.tex`) advanced to a 39-page compilable document (report class, natbib bibliography). Chapters written: Introduction, Data, Empirical Design, Results, Discussion. **Still missing:** Literature Review, Conclusion, Abstract.

### 1.1 Descriptive Statistics Table (Table 1)
Computed from `analysis_Main_2021.csv` and filled into the thesis:

| Variable | N | Mean | Median | SD |
|---|---|---|---|---|
| PyPI 52wk downloads | 527,361 | 25,661 | 2,307 | 1,439,110 |
| PyPI Post-AI downloads | 527,361 | 748,094 | 4,005 | 49,081,592 |
| GitHub 52wk imports | 28,243 | 147.1 | 2.0 | 5,077.0 |
| GitHub Post-AI imports | 28,243 | 318.4 | 7.0 | 6,721.7 |
| AI score (52wk) | 8,566 | 0.272 | 0.232 | 0.391 |

### 1.2 Figures Included
Eight figures inserted across chapters:
1. `density_dist_to_cutoff.png` — Data: McCrary density diagnostic
2. `binscatter_log_imports.png` — Results: Raw RDD visual for GitHub imports
3. `suppression_visual_success_500.png` — Results: Diff-in-RDD (2021 vs placebos)
4. `rdd_horizon_coefficients.png` — Results: Activation across horizons
5. `long_horizon_trajectory_pypi.png` — Results: Persistence (smoking gun)
6. `sensitivity_diff_in_rdd_bandwidth.png` — Results: Bandwidth robustness
7. `permutation_distribution.png` — Results: Permutation test (p=0.344)
8. `long_horizon_cumulative_pypi.png` — Discussion: Cumulative gap persistence

### 1.3 Bibliography
Created `references.bib` with 10 entries: Doshi & Hauser (2024), McCrary (2008), Calonico et al. (2014, 2020), Imbens & Lemieux (2008), Lee & Lemieux (2010), Gelman & Imbens (2019), Cattaneo et al. (2020), Grembi et al. (2016), OpenAI (2023). All inline citations converted to `\citet`/`\citep`.

---

## 2. Critical Finding: Barrier-to-Entry Sign Error

**The -14.5pp claim in memo_05 was wrong.** The coefficient in `debug_selection_bias.py` on `is_pre_cutoff` is -0.145, which means pre-cutoff libraries are 14.5pp LOWER at the boundary — equivalently, post-cutoff libraries are 14.5pp HIGHER. The memo interpreted the sign backwards.

Verification via R's `rdrobust` (with jitter to handle mass points, h=26):
- Bias-corrected estimate: **+28.6pp** (post-cutoff more likely to succeed)
- Robust SE: 3.94, p < 0.001
- Effective N: 78,762

**This makes substantive sense.** The 26-week success window closes ~March 2022, entirely pre-ChatGPT. There is no LLM channel operating in this window. The positive jump likely reflects seasonality (October-December releases may have different early adoption dynamics than spring-summer releases).

**Resolution in thesis:** Section reframed as "Covariate Balance: Pre-AI Success Rates." The pre-AI advantage for post-cutoff libraries makes the post-AI Diff-in-RDD suppression finding *more conservative*, not less.

---

## 3. Threats and Caveats Added to Thesis

### Discussion Section 5.4 (Alternative Mechanisms):
1. **Cutoff date imprecision:** OpenAI documented "September 2021" without specifying a day. September 27 is a researcher choice. The 9-week donut makes estimates robust to any placement within the month. Running variable measurement error biases estimates toward zero (conservative).
2. **GitHub Copilot confounder:** Released June 2021, shares similar training cutoff. Causal claim reframed: the effect is attributable to the *knowledge boundary as a class* shared by the LLM ecosystem, not any single model.

### Results:
3. **Mechanism moderation (Section 4.6):** Reframed from "consistent with systemic effect" to "underpowered (N=1,303, ~650 per group), cannot distinguish between broad and targeted effects."
4. **Implementation gap (Section 4.5):** Added caveat that the 2:1 GitHub/PyPI ratio may partly reflect sample composition (5.3% match rate over-represents prominent libraries).

### Methods Section 3.5 (Outcomes):
5. **Calendar-anchored outcome caveat:** `post_ai_downloads_alltime` is a snapshot that grows over time. The age gradient across the bandwidth is absorbed by local linear slopes but the estimate is time-dependent.

### Limitations Section 5.7:
6. **Multiple testing:** No family-wise correction across outcomes × tiers × designs. Primary specification is pre-designated (Successful Diff-in-RDD, p=0.008), but marginal results (p=0.039) warrant caution.
7. **Secular Python growth:** If Python adoption accelerated 2018-2021, placebo baseline may understate expected 2021 seasonal jump, biasing the excess away from zero. Placebos don't show monotonic trend, but formal test not conducted.

---

## 4. Repository Cleanup

| Action | Details |
|---|---|
| **thesis.tex on GitHub** | Committed for the first time, along with references.bib |
| **Debug scripts archived** | debug_rdrobust.py, debug_selection_bias.py, diagnostic_top_matches.py, compare_match_perspectives.py → archive/ |
| **Root clutter archived** | konzi_1.docx, master_prompt.docx, literature.xlsx, GEMINI.md, master_analysis.ipynb, matching.md → archive/ |
| **Stale results archived** | old_results.ipynb, new_results.md → archive/ |
| **.gitignore updated** | LaTeX artifacts (*.aux, *.bbl, etc.), .claude/, CLAUDE.md, GEMINI.md, limitations.md, notes.txt |
| **README rewritten** | Removed overclaims, corrected barrier error, academic tone, sample composition caveats |

---

## 5. Decisions Made

- **Quantile RDD:** Not included in thesis. The success tier analysis already answers the distributional question with better identification (integrated into Diff-in-RDD). Scripts 12-13 remain in pipeline but their output is not cited.
- **Script refactoring:** Supervisor instructed to separate main/appendix scripts. Deferred to a later session — risk without empirical payoff at this stage, but will be done per supervisor instruction.
- **Implementation gap framing:** Kept as secondary finding (mechanism evidence), not promoted to main result. The 5.3% GitHub match rate doesn't support the weight of a primary claim.

---

## 6. Remaining Work

| Task | Priority | Notes |
|---|---|---|
| Literature review chapter | High | Not yet started |
| Conclusion and abstract | High | Straightforward once lit review exists |
| Script refactoring (main/appendix) | Medium | Supervisor instruction |
| Overleaf Git sync | Low | Waiting for supervisor to share URL |
| Verify full pipeline runs | Low | Debug scripts removed, but pipeline doesn't depend on them |

---

**Status:** Thesis document is structurally complete minus literature review, conclusion, and abstract. All empirical results correctly reported with honest caveats. Repository cleaned and pushed to GitHub.
