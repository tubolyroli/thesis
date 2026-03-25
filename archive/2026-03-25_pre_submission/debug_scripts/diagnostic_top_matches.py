import pandas as pd
from config import RAW_DIR, INTERM_DIR
from utils import normalize_name

def main():
    # 1. Load GitHub raw data and aggregate
    gh_path = RAW_DIR / "github_library_week_panel.csv"
    print(f"Reading {gh_path}...")
    df_gh = pd.read_csv(gh_path)
    
    # Total imports per library name as written in code
    gh_top = (
        df_gh.groupby("library")["import_count"]
        .sum()
        .reset_index()
        .sort_values("import_count", ascending=False)
        .head(100)
    )
    
    # Normalize for matching
    gh_top["normalized_name"] = normalize_name(gh_top["library"])
    
    # 2. Load PyPI base to check matches
    pypi_path = INTERM_DIR / "pypi_base.parquet"
    print(f"Reading {pypi_path}...")
    pypi_base = pd.read_parquet(pypi_path, columns=["package"])
    pypi_packages = set(pypi_base["package"].unique())
    
    # 3. Check match status
    gh_top["matched_to_pypi"] = gh_top["normalized_name"].apply(lambda x: x in pypi_packages)
    
    # 4. Save and Display
    output_path = INTERM_DIR / "top_100_gh_matches.csv"
    gh_top.to_csv(output_path, index=False)
    
    print("\nTop 20 GitHub Libraries and Match Status:")
    print(gh_top.head(20)[["library", "normalized_name", "import_count", "matched_to_pypi"]].to_string(index=False))
    
    n_matched = gh_top["matched_to_pypi"].sum()
    print(f"\nSummary: {n_matched}/100 of the top GitHub libraries matched the PyPI release table.")
    print(f"Full table saved to: {output_path}")

if __name__ == "__main__":
    main()
