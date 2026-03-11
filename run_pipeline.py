import subprocess
import sys
import time
from pathlib import Path

# Ordered list of scripts to run
SCRIPTS = [
    "01_build_pypi_base.py",
    "02_aggregate_github.py",
    "03_merge_and_restrict.py",
    "04_diagnostics.py",
    "05_estimation.py",
    "06_robustness.py",
    "07_multi_cutoff_comparison.py",
    "08_diff_in_rdd.py",
    # Appendix / Experimental
    "09_permutation_inference.py",
    "10_ai_mechanism_split.py"
]

def run_script(script_name):
    script_path = Path("scripts") / script_name
    print(f"\n>>> Running {script_name}...")
    
    start_time = time.time()
    result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
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
