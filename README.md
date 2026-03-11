# Do LLMs know about new things?

This thesis employs a Regression Discontinuity Design (RDD) to investigate whether LLM training cutoffs (specifically GPT-3.5/4's) create an adoption barrier for new Python libraries. Using a high-frequency panel of PyPI downloads and GitHub usage, we test if libraries present in the model's pre-training data diffuse more widely than those released shortly after the cutoff.

### Headline Findings
- **No Robust "Knowledge Wall":** We find no evidence of a broad post-cutoff adoption penalty in the 2021 main sample; adoption remains resilient to LLM training cutoffs.
- **2021 in Context:** The 2021 effect is not unusually negative when compared to placebo years and random-Monday permutation tests, suggesting the observed discontinuity is indistinguishable from background noise.
- **Seasonality Caution:** Apparent adoption "dips" in 2021 likely reflect recurring seasonal cycles. While Diff-in-RDD against 2020 points toward this, it is treated as a secondary robustness check due to the limited seasonal baseline.
- **Conditional "Freshness Premium":** A possible post-cutoff adoption advantage appears among successful libraries under the primary `rdrobust` specification, but this finding is sensitive to the choice of estimator (e.g., clustered WLS).

### 📍 Read This First
- **[memos/memo_01.md](memos/memo_01.md)**: The definitive guide to the technical evolution, placebo discovery, and final empirical findings.
- **[results/estimation_results.csv](results/estimation_results.csv)**: Main RD coefficients and standard errors (Tables 2–4).
- **[results/diff_in_rdd_summary.txt](results/diff_in_rdd_summary.txt)**: Robustness check via Difference-in-RDD (Table 5).

## Project Structure

- `data/`: Contains raw, intermediate, and final datasets.
  - `raw/`: Original data files (PyPI downloads, GitHub imports).
  - `intermediate/`: Processed files used for merging.
  - `final/`: Analysis-ready CSV files for different cutoff environments.
- `scripts/`: Python scripts for data processing and estimation.
### Core Pipeline
  - `01_build_pypi_base.py`: Processes PyPI download data.
  - `02_aggregate_github.py`: Aggregates GitHub library usage and AI scores.
  - `03_merge_and_restrict.py`: Merges datasets and applies temporal filters.
  - `04_diagnostics.py`: Running variable density and balance checks.
  - `05_estimation.py`: Main RD estimation.
  - `06_robustness.py`: Bandwidth and donut-hole sensitivity.
  - `07_multi_cutoff_comparison.py`: Cross-year coefficient comparison.
  - `08_diff_in_rdd.py`: Secondary Difference-in-RDD analysis for seasonality robustness.

### Appendix & Utilities
  - `09_permutation_inference.py`: Non-parametric distribution of placebos.
  - `10_ai_mechanism_split.py`: Exploratory AI usage heterogeneity.
  - `utils.py`: Shared estimation logic (WLS & rdrobust wrappers).
  - `debug_rdrobust.py`: Utility to verify rdrobust sign/results.
  - `config.py`: Global paths and RD parameters.

- `results/`: Output tables and figures.
- `memos/`: Research notes and exploratory notebooks.
- `papers/`: Reference literature.

## Getting Started

1. **Environment Setup**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Pipeline**:
   You can run the entire analysis pipeline using the main runner script. **Ensure you use the virtual environment's python**:
   ```bash
   ./.venv/bin/python run_pipeline.py
   ```
   Alternatively, execute scripts individually in numerical order:
   ```bash
   ./.venv/bin/python scripts/01_build_pypi_base.py
   ./.venv/bin/python scripts/02_aggregate_github.py
   ...
   ```

## Canonical Outputs
- **Data**: 
  - `data/final/analysis_Main_2021.csv`: Primary dataset for 2021 RD.
  - `data/final/matching_summary.csv`: Summary of PyPI-to-GitHub match rates.
- **Results**:
  - `results/estimation_results.csv`: Table 2, 3, and 4 outcomes.
  - `results/diff_in_rdd_summary.txt`: Table 5 (Diff-in-RDD).
  - `results/figures/`: RDD diagnostic and sensitivity plots.

## Key Parameters
Parameters like `WINDOW_WEEKS`, `MIN_DOWNLOADS_52WK`, and `CUTOFFS` are managed in `scripts/config.py`.
