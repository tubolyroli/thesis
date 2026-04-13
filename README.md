# Do LLMs Shape the Diffusion of New Software?

### Training Cutoffs and Adoption Dynamics in the Python Ecosystem

**Author:** Roland Tuboly | **Supervisor:** Johannes Wachs

**Institution:** Corvinus University of Budapest, MSc in Social Data Science

---

<p align="center">
  <img src="results/figures/long_horizon_trajectory_pypi.png" alt="Long Horizon Trajectory of 2021 Cohorts" width="800">
  <br>
  <em>Average weekly PyPI downloads for libraries released just before (July 2021) and just after (October 2021) the GPT-3.5/GPT-4 training cutoff. The gap is dormant at release and opens only after ChatGPT launches in November 2022.</em>
</p>

---

## Summary

This paper investigates whether large language models with dated training cutoffs shape the diffusion of newly released Python libraries. Using a Regression Discontinuity Design around the documented September 2021 GPT-3.5/GPT-4 knowledge cutoff, it estimates the causal effect of training data inclusion on subsequent library adoption. A Difference-in-Discontinuities design using 2018-2020 placebo cohorts isolates the cutoff-specific effect from seasonal confounding.

The main finding is a statistically significant suppression of post-cutoff library adoption (baseline-adjusted Diff-in-RDD, p = 0.002). Before ChatGPT, libraries on either side of the cutoff differed by roughly 28% in weekly downloads; by early 2026, pre-cutoff libraries average approximately five times more weekly downloads, and the gap continues to widen. The suppression is directionally larger in GitHub code imports than in PyPI downloads, consistent with LLM-steered code generation as the operative channel, though the GitHub Diff-in-RDD does not reach conventional significance (p = 0.060) due to the small matched subsample. As of January 2026, the gap shows no evidence of catch-up.

## Key Results

- **Diff-in-RDD suppression:** Statistically significant for Successful libraries (min 500 downloads at 26 weeks), baseline-adjusted p = 0.002, with year-by-week clustered standard errors. Pre-cutoff libraries average roughly five times more weekly downloads by early 2026.
- **Implementation gap (suggestive):** The discontinuity in GitHub code imports is directionally larger than the PyPI download discontinuity, but the GitHub Diff-in-RDD does not reach conventional significance (p = 0.060, ~1,500 libraries per cohort year within bandwidth). The comparison is between different samples (5.3% GitHub-matched subsample vs. full PyPI universe).
- **Activation pattern:** The gap is absent at release and emerges only after November 2022 (ChatGPT launch).
- **Persistence:** No catch-up through January 2026 across any outcome measure.
- **AI exposure moderation (exploratory):** Not statistically significant (p = 0.179, N = 1,303). Likely underpowered; the moderator is post-treatment.

## Repository Structure

```
thesis/
├── thesis.tex                  # Main paper (LaTeX)
├── references.bib              # Bibliography (natbib)
├── scripts/
│   ├── pipeline/               # Data construction (01-03)
│   ├── main/                   # Core results in paper body (04-05, 08, 10-11, 14, 19)
│   ├── appendix/               # Robustness and sensitivity checks (06-07, 09, 12-13, 15-18)
│   ├── config.py               # Shared constants
│   └── utils.py                # Shared helpers
├── data/
│   ├── raw/                    # Source parquet files (not tracked)
│   ├── intermediate/           # Processed aggregates (not tracked)
│   └── final/                  # Analysis-ready CSVs per cohort (not tracked)
├── results/
│   ├── figures/                # Publication-ready visualizations
│   ├── final_results_tables.md # Definitive empirical tables
│   ├── archive/                # Superseded outputs
│   └── *.csv                   # Estimation outputs per script
├── docs/                       # Reference documents, limitations, TDK abstract
├── memos/                      # Research memos and design evolution
├── run_pipeline.py             # Orchestrates all scripts (--skip-pipeline, --appendix)
└── requirements.txt
```

## Reproduction

```bash
pip install -r requirements.txt

# Full pipeline (data construction + main analysis + appendix)
python run_pipeline.py --appendix

# Main analysis only, using existing processed data
python run_pipeline.py --skip-pipeline

# Appendix/robustness only
python run_pipeline.py --appendix-only
```

Requires access to the source data files in `data/raw/`. Scripts 11 and 14 load the full raw PyPI parquet and require sufficient RAM (>8GB).

The pinned versions in `requirements.txt` reflect the exact environment used to produce the results in this repository (Python 3.14, pandas 3.x, numpy 2.x, statsmodels 0.14, rdrobust 1.3). Older Python environments will require relaxing the pins; the analysis itself only relies on standard pandas, numpy, statsmodels, and rdrobust APIs.
