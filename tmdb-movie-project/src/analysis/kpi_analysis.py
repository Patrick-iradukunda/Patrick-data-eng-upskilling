import pandas as pd


def calculate_profit(df: pd.DataFrame) -> pd.DataFrame:
   
    # Check budget and revenue columns exist in cleaned DataFrames
    required = {"budget_musd", "revenue_musd"}
    if not required.issubset(df.columns):
        raise KeyError("Missing one or more required columns: 'budget_musd', 'revenue_musd'.")

  
    df["profit_musd"] = df["revenue_musd"] - df["budget_musd"]

    
    df["roi"] = df.apply(
        lambda row: row["revenue_musd"] / row["budget_musd"]
        if pd.notna(row["budget_musd"]) and row["budget_musd"] >= 10
        else pd.NA,
        axis=1,
    )

    return df


def rank_movies(df: pd.DataFrame, column: str, ascending: bool = False, top_n: int = 5) -> pd.DataFrame:
   
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")

    ranked = df[["title", column]].dropna(subset=[column])
    return ranked.sort_values(by=column, ascending=ascending).head(top_n)


def movie_performance_kpis(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
   
    df = calculate_profit(df)

    
    roi_df = df.dropna(subset=["roi"])
    rated_df = df[df["vote_count"] >= 10]

    kpis = {
        "Highest Revenue": rank_movies(df, "revenue_musd", ascending=False),
        "Highest Budget": rank_movies(df, "budget_musd", ascending=False),
        "Highest Profit": rank_movies(df, "profit_musd", ascending=False),
        "Lowest Profit": rank_movies(df, "profit_musd", ascending=True),
        "Highest ROI (Budget ≥10M)": rank_movies(roi_df, "roi", ascending=False),
        "Lowest ROI (Budget ≥10M)": rank_movies(roi_df, "roi", ascending=True),
        "Most Voted Movies": rank_movies(df, "vote_count", ascending=False),
        "Highest Rated (≥10 votes)": rank_movies(rated_df, "vote_average", ascending=False),
        "Lowest Rated (≥10 votes)": rank_movies(rated_df, "vote_average", ascending=True),
        "Most Popular Movies": rank_movies(df, "popularity", ascending=False),
    }

    return kpis


def print_kpi_results(kpis: dict[str, pd.DataFrame]) -> None:
   
    for name, table in kpis.items():
        print(f"\n📊 {name}")
        print(table.to_string(index=False))
