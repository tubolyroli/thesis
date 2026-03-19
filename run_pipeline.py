import subprocess
import sys
import time
from pathlib import Path

# Ordered list of scripts to run (Full reproducible suite)
SCRIPTS = [
    "01_build_pypi_base.py",
    "02_aggregate_github.py",
    "03_merge_and_restrict.py",
    "04_diagnostics.py",
    "05_estimation.py",
    "06_robustness.py",
    "07_multi_cutoff_comparison.py",
    "08_diff_in_rdd.py",
    "09_permutation_inference.py",
    "10_ai_mechanism_split.py",
    "11_visualize_results.py",
    "12_investigate_median.py",
    "13_stacked_rdd.py",
    "14_visualize_long_horizon_trajectories.py",
    "15_bandwidth_sensitivity.py",
    "16_bandwidth_sensitivity_github.py",
    "17_visualize_suppression.py",
    "18_bandwidth_sensitivity_suppression.py"
]

def run_script(script_name):
    # Ensure script is run from the project root
    root_dir = Path(__file__).resolve().parent
    script_path = root_dir / "scripts" / script_name
    print(f"\n>>> Running {script_name}...")
    
    start_time = time.time()
    # Execute with project root in PYTHONPATH to ensure config/utils imports work
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root_dir) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=False, env=env, cwd=str(root_dir))
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print(f">>> {script_name} finished successfully in {elapsed:.1f}s.")
        return True
    else:
        print(f">>> ERROR: {script_name} failed with exit code {result.returncode}.")
        return False

def main():
    root_dir = Path(__file__).resolve().parent
    print("=========================================")
    print("      THESIS ANALYSIS PIPELINE           ")
    print("=========================================")
    print(f"Project Root: {root_dir}")
    
    for script in SCRIPTS:
        success = run_script(script)
        if not success:
            print("\nPipeline stopped due to error.")
            sys.exit(1)
            
    print("\n=========================================")
    print("      PIPELINE COMPLETED SUCCESSFULLY    ")
    print("=========================================")

if __name__ == "__main__":
    main()
