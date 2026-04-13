import subprocess
import sys
import os
import time
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

# Data construction — must run before any analysis
PIPELINE_SCRIPTS = [
    ("pipeline", "01_build_pypi_base.py"),
    ("pipeline", "02_aggregate_github.py"),
    ("pipeline", "03_merge_and_restrict.py"),
]

# Core results that appear in the paper body
MAIN_SCRIPTS = [
    ("main", "04_diagnostics.py"),
    ("main", "05_estimation.py"),
    ("main", "08_diff_in_rdd.py"),
    ("main", "10_ai_mechanism_split.py"),
    ("main", "11_visualize_results.py"),
    ("main", "14_visualize_long_horizon_trajectories.py"),
    ("main", "19_compute_descriptive_percentages.py"),
]

# Robustness checks and supplementary material
APPENDIX_SCRIPTS = [
    ("appendix", "06_robustness.py"),
    ("appendix", "07_multi_cutoff_comparison.py"),
    ("appendix", "09_permutation_inference.py"),
    ("appendix", "12_investigate_median.py"),
    ("appendix", "13_stacked_rdd.py"),
    ("appendix", "15_bandwidth_sensitivity.py"),
    ("appendix", "16_bandwidth_sensitivity_github.py"),
    ("appendix", "17_visualize_suppression.py"),
    ("appendix", "18_bandwidth_sensitivity_suppression.py"),
]


def run_script(subdir, script_name):
    script_path = ROOT_DIR / "scripts" / subdir / script_name
    print(f"\n>>> Running {subdir}/{script_name}...")
    start_time = time.time()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=False,
        env=env,
        cwd=str(ROOT_DIR),
    )
    elapsed = time.time() - start_time
    if result.returncode == 0:
        print(f">>> {script_name} finished in {elapsed:.1f}s.")
        return True
    else:
        print(f">>> ERROR: {script_name} failed (exit code {result.returncode}).")
        return False


def run_group(scripts, label):
    print(f"\n{'='*45}")
    print(f"  {label}")
    print(f"{'='*45}")
    for subdir, name in scripts:
        if not run_script(subdir, name):
            print(f"\nPipeline stopped at {name}.")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run the analysis pipeline.")
    parser.add_argument(
        "--skip-pipeline", action="store_true",
        help="Skip data construction (01-03); use existing processed data.",
    )
    parser.add_argument(
        "--appendix", action="store_true",
        help="Also run appendix/robustness scripts after main analysis.",
    )
    parser.add_argument(
        "--appendix-only", action="store_true",
        help="Run only the appendix/robustness scripts (requires processed data).",
    )
    args = parser.parse_args()

    print("=========================================")
    print("      ANALYSIS PIPELINE                  ")
    print("=========================================")
    print(f"Project Root: {ROOT_DIR}")

    if args.appendix_only:
        run_group(APPENDIX_SCRIPTS, "APPENDIX / ROBUSTNESS")
    else:
        if not args.skip_pipeline:
            run_group(PIPELINE_SCRIPTS, "DATA PIPELINE")
        run_group(MAIN_SCRIPTS, "MAIN ANALYSIS")
        if args.appendix:
            run_group(APPENDIX_SCRIPTS, "APPENDIX / ROBUSTNESS")

    print("\n=========================================")
    print("      PIPELINE COMPLETED SUCCESSFULLY    ")
    print("=========================================")


if __name__ == "__main__":
    main()
