# Do LLMs know about new things?

This thesis employs a Regression Discontinuity Design (RDD) to investigate whether LLM training cutoffs (specifically GPT-3.5/4's) create an adoption barrier for new Python libraries. Using a high-frequency panel of PyPI downloads and GitHub usage, we test if libraries present in the model's pre-training data diffuse more widely than those released shortly after the cutoff.

### 🚀 Phase 2 Breakthroughs (New Findings)
- **Relative Suppression (The "Missing Boost"):** Historically, libraries released in late September enjoy a massive seasonal adoption jump (+1,694 downloads at the median). In 2021, this jump was **suppressed by 90%** (+169 downloads), providing strong evidence that the LLM training cutoff hindered natural growth momentum.
- **The "Catch-up" Dynamic:** We find an initial adoption "discovery tax" (-5% at 12 weeks) that fully recovers to a positive gain (+3.5% at 52 weeks). This suggests that LLM exclusion creates **temporary delays**, not permanent market exclusion.
- **Robust Distributional Gains:** Focus on the "typical" library (Median RDD) reveals a highly significant and consistent **"Post-Cutoff Bonus"** across the adoption spectrum (from Q25 to Q90), which was previously masked by extreme outliers in log-mean models.

### 📍 Read This First
- **[memos/memo_02.md](memos/memo_02.md)**: **Start here.** Detailed results on catch-up, median RDD, and the relative suppression framework.
- **[memos/memo_01.md](memos/memo_01.md)**: Baseline project history, placebo discovery, and initial technical refinements.
- **[memos/research_manifesto.md](memos/research_manifesto.md)**: High-level evolution of the research design from Step 1 to Step 8.
- **[results/estimation_results_final.csv](results/estimation_results_final.csv)**: Final expanded RD coefficients across all horizons and quantiles.

## Project Structure

- `data/`: Contains raw, intermediate, and final datasets.
- `scripts/`: Python scripts for data processing and estimation.
### Core Pipeline
  - `01_build_pypi_base.py`: Processes PyPI download data and constructs horizons.
  - `02_aggregate_github.py`: Aggregates GitHub usage and AI scores.
  - `03_merge_and_restrict.py`: Merges datasets and applies temporal filters.
  - `05_estimation.py`: **Main Suite.** Estimates RD across horizons (12w, 26w, 52w) and quantiles.
  - `06_robustness.py`: Bandwidth sensitivity and placebo tests for Median RDD.
  - `11_visualize_results.py`: Generates horizon coefficient and quantile plots.
  - `13_stacked_rdd.py`: Pools historical cutoffs to estimate the "Relative Suppression" effect.

### Appendix & Utilities
  - `08_diff_in_rdd.py`: Difference-in-RDD analysis (2021 vs 2020).
  - `10_ai_mechanism_split.py`: Exploratory AI usage heterogeneity.
  - `12_investigate_median.py`: Distributional deep-dive (Q25 to Q90).
  - `utils.py`: Shared estimation logic (WLS, rdrobust, and QuantReg wrappers).
  - `config.py`: Global paths and RD parameters.

- `results/`: Output tables and figures.
- `memos/`: Research notes and exploratory notebooks.

## Getting Started

1. **Environment Setup**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Pipeline**:
   ```bash
   ./.venv/bin/python scripts/05_estimation.py
   ./.venv/bin/python scripts/06_robustness.py
   ./.venv/bin/python scripts/11_visualize_results.py
   ./.venv/bin/python scripts/13_stacked_rdd.py
   ```

## Canonical Outputs
- **Results**:
  - `results/estimation_results_final.csv`: Full expanded result suite.
  - `results/stacked_rdd_results.csv`: Comparison of 2021 jump vs. historical average.
  - `results/figures/rdd_horizon_coefficients.png`: Visualization of the catch-up dynamic.
  - `results/figures/rdd_quantile_coefficients.png`: Visualization of distributional robustness.
