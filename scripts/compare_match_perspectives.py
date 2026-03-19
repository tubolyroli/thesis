import pandas as pd
from config import RAW_DIR, INTERM_DIR
from utils import normalize_name

def main():
    # 1. GitHub Perspective
    gh_path = RAW_DIR / "github_library_week_panel.csv"
    df_gh = pd.read_csv(gh_path)
    all_gh_names = df_gh["library"].unique()
    n_gh_total = len(all_gh_names)
    
    # Normalize
    gh_normalized = normalize_name(pd.Series(all_gh_names)).unique()
    
    # 2. PyPI Perspective
    pypi_path = INTERM_DIR / "pypi_base.parquet"
    pypi_base = pd.read_parquet(pypi_path, columns=["package"])
    pypi_names = set(pypi_base["package"].unique())
    
    # 3. GitHub Match Rate
    matched_names = [name for name in gh_normalized if name in pypi_names]
    n_gh_matched = len(matched_names)
    
    # 4. PyPI Match Rate (for comparison)
    n_pypi_total = len(pypi_names)
    
    print(f"--- GitHub Perspective ---")
    print(f"Unique library names found on GitHub: {n_gh_total:,}")
    print(f"Unique GitHub names that matched PyPI: {n_gh_matched:,}")
    print(f"GitHub Match Rate: {n_gh_matched / n_gh_total:.1%}")
    
    print(f"\n--- PyPI Perspective ---")
    print(f"Unique packages on PyPI: {n_pypi_total:,}")
    print(f"Unique PyPI packages found on GitHub: {n_gh_matched:,}")
    print(f"PyPI Match Rate: {n_gh_matched / n_pypi_total:.1%}")

if __name__ == "__main__":
    main()
