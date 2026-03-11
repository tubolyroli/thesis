import pandas as pd
import numpy as np
from config import RAW_DIR, INTERM_DIR
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

    def aggregate_horizon(max_weeks: int) -> pd.DataFrame:
        sub = df_post.loc[df_post["weeks_since_release"] < max_weeks]
        out = (
            sub.groupby("package", as_index=False)["downloads"]
            .sum()
            .rename(columns={"downloads": f"cum_downloads_{max_weeks}wk"})
        )
        return out

    pypi_12 = aggregate_horizon(12)
    pypi_26 = aggregate_horizon(26)
    pypi_52 = aggregate_horizon(52)

    pypi_base = release_dates.merge(pypi_12, on="package", how="left")
    pypi_base = pypi_base.merge(pypi_26, on="package", how="left")
    pypi_base = pypi_base.merge(pypi_52, on="package", how="left")

    for col in ["cum_downloads_12wk", "cum_downloads_26wk", "cum_downloads_52wk"]:
        pypi_base[col] = pypi_base[col].fillna(0).astype("int64")

    # Preserve earlier field name for compatibility
    pypi_base["total_downloads_52wk"] = pypi_base["cum_downloads_52wk"]

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