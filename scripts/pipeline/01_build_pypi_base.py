import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import pyarrow.parquet as pq
from config import RAW_DIR, INTERM_DIR, CHATGPT_RELEASE, GPT4_RELEASE, GPT4_TURBO_RELEASE
from utils import normalize_name, get_weeks_since

def main() -> None:
    INTERM_DIR.mkdir(parents=True, exist_ok=True)
    pypi_path = RAW_DIR / "pypi_downloads.parquet"
    
    print(f"Starting optimized two-pass processing of {pypi_path.name}...")

    # --- PASS 1: Identify Release Weeks ---
    print("Pass 1: Identifying release weeks...")
    parquet_file = pq.ParquetFile(pypi_path)
    release_weeks = {}

    for batch in parquet_file.iter_batches(batch_size=1_000_000, columns=["project", "week_start", "downloads"]):
        df_chunk = batch.to_pandas()
        # Filter for positive downloads
        valid = df_chunk[df_chunk["downloads"] > 0]
        if valid.empty:
            continue
            
        # Group by project to find min week_start in this chunk
        chunk_min = valid.groupby("project")["week_start"].min()
        
        for project, date in chunk_min.items():
            if project not in release_weeks or date < release_weeks[project]:
                release_weeks[project] = date

    # Convert to DataFrame and normalize
    release_df = pd.DataFrame(list(release_weeks.items()), columns=["project", "release_week"])
    release_df["package"] = normalize_name(release_df["project"])
    
    # Handle multiple project names normalizing to same package
    release_dates = release_df.groupby("package")["release_week"].min().reset_index()
    
    # Mapping for Pass 2 (original project names to release dates)
    pkg_min_map = release_dates.set_index("package")["release_week"].to_dict()

    print(f"Found {len(release_dates):,} unique packages.")

    # --- PASS 2: Aggregate Horizons ---
    print("Pass 2: Aggregating horizons...")
    
    aggs = []
    max_observed_date = pd.Timestamp.min

    for batch in parquet_file.iter_batches(batch_size=2_000_000, columns=["project", "week_start", "downloads"]):
        df_chunk = batch.to_pandas()
        df_chunk["package"] = normalize_name(df_chunk["project"])
        
        # Merge release week
        df_chunk["release_week"] = df_chunk["package"].map(pkg_min_map)
        df_chunk = df_chunk.dropna(subset=["release_week"])
        
        # Calculate weeks since release
        df_chunk["week_start"] = pd.to_datetime(df_chunk["week_start"])
        
        # Track max week_start for metadata
        chunk_max = df_chunk["week_start"].max()
        if chunk_max > max_observed_date:
            max_observed_date = chunk_max

        df_chunk["weeks_since_release"] = get_weeks_since(df_chunk["week_start"], df_chunk["release_week"])
        
        # Filter post-release
        df_chunk = df_chunk[df_chunk["weeks_since_release"] >= 0]
        if df_chunk.empty:
            continue

        # Horizon Columns (Pre-calculated for speed)
        w = df_chunk["weeks_since_release"]
        d = df_chunk["week_start"]
        dl = df_chunk["downloads"]
        
        df_chunk["c26"] = np.where(w < 26, dl, 0)
        df_chunk["c52"] = np.where(w < 52, dl, 0)
        df_chunk["cgpt4"] = np.where(d <= GPT4_RELEASE, dl, 0)
        df_chunk["cgpt4t"] = np.where(d <= GPT4_TURBO_RELEASE, dl, 0)
        df_chunk["cpai"] = np.where(d >= CHATGPT_RELEASE, dl, 0)
        
        # Fast sum-based aggregation
        chunk_agg = df_chunk.groupby("package")[["c26", "c52", "cgpt4", "cgpt4t", "downloads", "cpai"]].sum()
        aggs.append(chunk_agg)

    print("Finalizing aggregation...")
    full_agg = pd.concat(aggs).groupby("package").sum().reset_index()
    
    # Merge with release dates
    pypi_base = release_dates.merge(full_agg, on="package", how="left").fillna(0)
    
    # Rename for compatibility
    pypi_base = pypi_base.rename(columns={
        "c26": "cum_downloads_26wk",
        "c52": "cum_downloads_52wk",
        "cgpt4": "cum_downloads_gpt4",
        "cgpt4t": "cum_downloads_gpt4turbo",
        "downloads": "cum_downloads_alltime",
        "cpai": "post_ai_downloads_alltime"
    })
    pypi_base["total_downloads_52wk"] = pypi_base["cum_downloads_52wk"].astype("int64")

    # Save
    pypi_base.to_parquet(INTERM_DIR / "pypi_base.parquet", index=False)
    
    pypi_meta = pd.DataFrame({
        "source": ["pypi"],
        "max_week_start": [max_observed_date],
        "n_unique_packages_raw": [len(release_dates)],
        "n_unique_packages_release_proxy": [len(pypi_base)]
    })
    pypi_meta.to_parquet(INTERM_DIR / "pypi_meta.parquet", index=False)

    print(f"Success! Saved to {INTERM_DIR / 'pypi_base.parquet'}")

if __name__ == "__main__":
    main()
