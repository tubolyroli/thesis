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

This thesis investigates whether large language models with dated training cutoffs shape the diffusion of newly released Python libraries. Using a Regression Discontinuity Design around the documented September 2021 GPT-3.5/GPT-4 knowledge cutoff, it estimates the causal effect of training data inclusion on subsequent library adoption. A Difference-in-Discontinuities design using 2018-2020 placebo cohorts isolates the cutoff-specific effect from seasonal confounding.

The main finding is a statistically significant suppression of post-cutoff library adoption: the 2021 cohort shows a -12.8 log point excess penalty in post-AI downloads relative to historical seasonal norms (p = 0.008). The effect is approximately twice as large in a GitHub-matched subsample of code imports as in PyPI downloads, consistent with LLM-steered code generation as the operative channel, though sample composition differences may partly account for the magnitude difference. As of January 2026, the gap shows no evidence of catch-up.

## Key Results

- **Diff-in-RDD suppression:** -12.8 log points for Successful libraries (min 500 downloads at 26 weeks), p = 0.008, with year-by-week clustered standard errors.
- **Implementation gap:** The discontinuity in GitHub imports (+26.8 log points) is roughly double the PyPI download discontinuity (+13.1 log points), though the comparison is between different samples (5.3% GitHub-matched subsample vs. full PyPI universe).
- **Activation pattern:** The gap is absent at release and emerges only after November 2022 (ChatGPT), consistent with the proposed mechanism.
- **Persistence:** No catch-up through January 2026 across any outcome measure.
- **AI exposure moderation (exploratory):** Not statistically significant (p = 0.179, N = 1,303). The test is likely underpowered to detect meaningful moderation; the moderator is post-treatment.

## Repository Structure

```
thesis/
├── thesis.tex                  # Main thesis document (LaTeX)
├── references.bib              # Bibliography (natbib)
├── scripts/                    # Ordered pipeline (01-18)
│   ├── 01-04                   # Data building, aggregation, merging
│   ├── 05-08                   # RDD and Diff-in-RDD estimation
│   ├── 09-10                   # Permutation inference, AI mechanism test
│   ├── 11-18                   # Visualization and sensitivity analysis
│   ├── config.py               # Shared constants
│   └── utils.py                # Shared helpers
├── data/
│   ├── raw/                    # Source parquet files (not tracked)
│   ├── intermediate/           # Processed aggregates (not tracked)
│   └── final/                  # Analysis-ready CSVs per cohort (not tracked)
├── results/
│   ├── figures/                # Thesis-ready visualizations
│   ├── final_results_tables.md # Definitive empirical tables
│   └── *.csv                   # Estimation outputs per script
├── memos/                      # Research memos and design evolution
├── run_pipeline.py             # Orchestrates all 18 scripts
└── requirements.txt
```

## Reproduction

```bash
pip install -r requirements.txt
python run_pipeline.py
```

This executes all 18 scripts in order, from raw data aggregation through final visualizations. Requires access to the source data files in `data/raw/`.
