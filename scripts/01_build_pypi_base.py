import pandas as pd
import numpy as np
from config import RAW_DIR, INTERM_DIR, CHATGPT_RELEASE, GPT4_RELEASE, GPT4_TURBO_RELEASE
from utils import normalize_name, check_monday_alignment, get_weeks_since

def main() -> None:
    INTERM_DIR.mkdir(parents=True, exist_ok=True)
    pypi_path = RAW_DIR / "pypi_downloads.parquet"

    # Load only needed columns
    df = pd.read_parquet(pypi_path, columns=["project", "week_start", "downloads"])

    # Normalize fields
    df["package"] = normalize_name(df["project"])
    df["week_start"] = pd.to_datetime(df["week_start"])
    df["downloads"] = pd.to_numeric(df["downloads"], errors="coerce").fillna(0).astype("int64")

    # Assert weekly alignment looks Monday-based
    check_monday_alignment(df)

    # First observed positive-download week as release proxy
    valid_downloads = df.loc[df["downloads"] > 0, ["package", "week_start"]].copy()
    release_dates = (
        valid_downloads.groupby("package", as_index=False)["week_start"]
        .min()
        .rename(columns={"week_start": "release_week"})
    )

    # Merge release date back for horizon construction
    df = df.merge(release_dates, on="package", how="inner", validate="many_to_one")
    df["weeks_since_release"] = get_weeks_since(df["week_start"], df["release_week"])

    # Keep post-release observations only
    df_post = df.loc[df["weeks_since_release"] >= 0].copy()

    # 1. Relative Horizons (Age-based)
    def aggregate_relative(max_weeks: int) -> pd.DataFrame:
        sub = df_post.loc[df_post["weeks_since_release"] < max_weeks]
        return sub.groupby("package")["downloads"].sum().reset_index().rename(columns={"downloads": f"cum_downloads_{max_weeks}wk"})

    pypi_52 = aggregate_relative(52)

    # 2. Fixed Model Horizons (Calendar-based)
    def aggregate_until(end_date: pd.Timestamp, col_name: str) -> pd.DataFrame:
        sub = df_post.loc[df_post["week_start"] <= end_date]
        return sub.groupby("package")["downloads"].sum().reset_index().rename(columns={"downloads": col_name})

    pypi_gpt4 = aggregate_until(GPT4_RELEASE, "cum_downloads_gpt4")
    pypi_gpt4turbo = aggregate_until(GPT4_TURBO_RELEASE, "cum_downloads_gpt4turbo")
    pypi_alltime = df_post.groupby("package")["downloads"].sum().reset_index().rename(columns={"downloads": "cum_downloads_alltime"})

    # 3. Post-AI Activation (Time-Adjusted: Growth after Nov 2022)
    pypi_post_ai = (
        df_post.loc[df_post["week_start"] >= CHATGPT_RELEASE]
        .groupby("package")["downloads"].sum().reset_index()
        .rename(columns={"downloads": "post_ai_downloads_alltime"})
    )

    # Merge all
    pypi_base = release_dates.copy()
    for extra in [pypi_52, pypi_gpt4, pypi_gpt4turbo, pypi_alltime, pypi_post_ai]:
        pypi_base = pypi_base.merge(extra, on="package", how="left").fillna(0)

    # Preserve earlier field name for compatibility
    pypi_base["total_downloads_52wk"] = pypi_base["cum_downloads_52wk"].astype("int64")

    # Source-level metadata for censoring checks later
    pypi_meta = pd.DataFrame(
        {
            "source": ["pypi"],
            "max_week_start": [df["week_start"].max()],
            "n_unique_packages_raw": [df["package"].nunique()],
            "n_unique_packages_release_proxy": [pypi_base["package"].nunique()],
        }
    )

    # Save outputs
    pypi_base.to_parquet(INTERM_DIR / "pypi_base.parquet", index=False)
    pypi_meta.to_parquet(INTERM_DIR / "pypi_meta.parquet", index=False)

    print(f"Saved: {INTERM_DIR / 'pypi_base.parquet'}")
    print(f"PyPI packages with release proxy: {pypi_base['package'].nunique():,}")
    print(f"Max PyPI week_start: {df['week_start'].max().date()}")

if __name__ == "__main__":
    main()