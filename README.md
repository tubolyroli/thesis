# Thesis: Generative AI and Creative Problem Solving in Software

This thesis employs a Regression Discontinuity Design (RDD) to investigate whether LLM training cutoffs (e.g., GPT-3.5/4) create an adoption barrier for new Python libraries. Using a high-frequency panel of PyPI downloads and GitHub usage, we test if libraries present in the model's pre-training data diffuse more widely than those released shortly after the cutoff.

### Headline Findings
- **No "Knowledge Wall":** We find no evidence that exclusion from LLM training data hinders the diffusion of new libraries; broad adoption remains resilient to training cutoffs.
- **"Freshness Premium":** Among successful libraries, those released *after* the cutoff exhibit a statistically significant adoption advantage, contradicting the "collective narrowing" hypothesis.
- **Seasonality Dominance:** Apparent adoption "dips" in 2021 are primarily driven by recurring seasonal cycles ("September Effect"), as identified through multi-year placebo cutoffs and Diff-in-RDD.

### 📍 Read This First
- **[memos/memo_01.md](memos/memo_01.md)**: The definitive guide to the technical evolution, placebo discovery, and final empirical findings.
- **[results/estimation_results.csv](results/estimation_results.csv)**: Main RD coefficients and standard errors (Tables 2–4).
- **[results/diff_in_rdd_summary.txt](results/diff_in_rdd_summary.txt)**: Summary of the Difference-in-RDD analysis (Table 5).

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
  - `08_diff_in_rdd.py`: Primary Difference-in-RDD analysis.

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
