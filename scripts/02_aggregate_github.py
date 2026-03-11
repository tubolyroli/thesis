import pandas as pd
import numpy as np
from config import RAW_DIR, INTERM_DIR, AI_SCORE_COLS, AI_WEIGHT_COLS
from utils import normalize_name, detect_column, check_monday_alignment, get_weeks_since

def main() -> None:
    INTERM_DIR.mkdir(parents=True, exist_ok=True)

    gh_path = RAW_DIR / "github_library_week_panel.csv"
    pypi_base_path = INTERM_DIR / "pypi_base.parquet"

    # Load GitHub and PyPI release table
    df_gh = pd.read_csv(gh_path)
    pypi_base = pd.read_parquet(pypi_base_path, columns=["package", "release_week"])

    # Basic validation
    required_cols = ["library", "week_start", "import_count"]
    for col in required_cols:
        assert col in df_gh.columns, f"Expected a '{col}' column in GitHub data."

    # Normalize basic fields
    df_gh["package"] = normalize_name(df_gh["library"])
    df_gh["week_start"] = pd.to_datetime(df_gh["week_start"])
    df_gh["import_count"] = pd.to_numeric(df_gh["import_count"], errors="coerce").fillna(0).astype("int64")

    # Assert weekly alignment looks Monday-based
    check_monday_alignment(df_gh)

    # AI score columns detection
    score_col = detect_column(df_gh.columns, AI_SCORE_COLS)
    weight_col = detect_column(df_gh.columns, AI_WEIGHT_COLS)

    # Metadata capture (before inner merge)
    n_unique_raw = df_gh["package"].nunique()

    # Merge release week from PyPI universe
    df_gh = df_gh.merge(
        pypi_base[["package", "release_week"]],
        on="package",
        how="inner",
        validate="many_to_one"
    )

    # Relative time from PyPI release
    df_gh["weeks_since_release"] = get_weeks_since(df_gh["week_start"], df_gh["release_week"])

    # Keep strictly post-release observations only
    df_gh = df_gh.loc[df_gh["weeks_since_release"] >= 0].copy()

    def aggregate_imports(max_weeks: int) -> pd.DataFrame:
        sub = df_gh.loc[df_gh["weeks_since_release"] < max_weeks, ["package", "import_count"]]
        out = (
            sub.groupby("package", as_index=False)["import_count"]
            .sum()
            .rename(columns={"import_count": f"cum_imports_{max_weeks}wk"})
        )
        return out

    gh_12 = aggregate_imports(12)
    gh_26 = aggregate_imports(26)
    gh_52 = aggregate_imports(52)

    gh_out = gh_12.merge(gh_26, on="package", how="outer")
    gh_out = gh_out.merge(gh_52, on="package", how="outer")

    for col in ["cum_imports_12wk", "cum_imports_26wk", "cum_imports_52wk"]:
        gh_out[col] = gh_out[col].fillna(0).astype("int64")

    # Weighted AI score over first 52 weeks
    if score_col is not None:
        tmp = df_gh.loc[df_gh["weeks_since_release"] < 52].copy()
        tmp[score_col] = pd.to_numeric(tmp[score_col], errors="coerce")

        if weight_col is not None:
            tmp[weight_col] = pd.to_numeric(tmp[weight_col], errors="coerce").fillna(0)
            tmp["weighted_score"] = tmp[score_col] * tmp[weight_col]

            ai_agg = (
                tmp.groupby("package", as_index=False)
                .agg(
                    ai_weighted_sum=("weighted_score", "sum"),
                    ai_weight_sum=(weight_col, "sum")
                )
            )
            ai_agg["avg_ai_score_52wk"] = np.where(
                ai_agg["ai_weight_sum"] > 0,
                ai_agg["ai_weighted_sum"] / ai_agg["ai_weight_sum"],
                np.nan
            )
            ai_agg = ai_agg[["package", "avg_ai_score_52wk"]]
        else:
            ai_agg = (
                tmp.groupby("package", as_index=False)[score_col]
                .mean()
                .rename(columns={score_col: "avg_ai_score_52wk"})
            )

        gh_out = gh_out.merge(ai_agg, on="package", how="left")
    else:
        gh_out["avg_ai_score_52wk"] = np.nan

    gh_meta = pd.DataFrame(
        {
            "source": ["github"],
            "max_week_start": [df_gh["week_start"].max()],
            "n_unique_libraries_raw": [n_unique_raw],
            "n_unique_packages_matched_to_pypi_release_table": [df_gh["package"].nunique()],
            "ai_score_column_used": [score_col if score_col is not None else ""],
            "ai_weight_column_used": [weight_col if weight_col is not None else ""],
        }
    )

    gh_out.to_parquet(INTERM_DIR / "github_agg.parquet", index=False)
    gh_meta.to_parquet(INTERM_DIR / "github_meta.parquet", index=False)

    print(f"Saved: {INTERM_DIR / 'github_agg.parquet'}")
    print(f"Matched GitHub packages: {df_gh['package'].nunique():,}")
    if score_col:
        print(f"AI score used: {score_col}")

if __name__ == "__main__":
    main()