import pandas as pd


def calculate_profit(df: pd.DataFrame) -> pd.DataFrame:
    # Compute profit and ROI .
    if not {"budget_musd", "revenue_musd"}.issubset(df.columns):
        raise KeyError("Missing columns: 'budget_musd' or 'revenue_musd'.")
    df["profit_musd"] = df["revenue_musd"] - df["budget_musd"]
    df["roi"] = df.apply(lambda r: r["revenue_musd"] / r["budget_musd"] 
                         if pd.notna(r["budget_musd"]) and r["budget_musd"] >= 10 else pd.NA, axis=1)
    return df


def rank_movies(df: pd.DataFrame, column: str, ascending: bool = False, top_n: int = 5) -> pd.DataFrame:
    # Rank top/bottom movies by a given column.
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")
    return df[["title", column]].dropna(subset=[column]).sort_values(by=column, ascending=ascending).head(top_n)


def movie_performance_kpis(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    # Generate core performance KPIs for movies.
    df = calculate_profit(df)
    roi_df = df.dropna(subset=["roi"])
    rated_df = df[df["vote_count"] >= 10]

    return {
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


def franchise_vs_standalone(df: pd.DataFrame) -> pd.DataFrame:
    # Compare franchise vs standalone movie performance.
    if "belongs_to_collection" not in df.columns:
        raise KeyError("'belongs_to_collection' column missing for franchise analysis.")
    df["is_franchise"] = df["belongs_to_collection"].apply(lambda x: pd.notna(x) and x != "")
    return df.groupby("is_franchise").agg({
        "revenue_musd": "mean", "roi": "median", "budget_musd": "mean",
        "popularity": "mean", "vote_average": "mean"
    }).rename(index={True: "Franchise", False: "Standalone"}).round(2)


def most_successful_franchises(df: pd.DataFrame) -> pd.DataFrame:
    # Identify top franchises by financial & rating metrics.
    if "belongs_to_collection" not in df.columns:
        raise KeyError("'belongs_to_collection' column missing for franchise analysis.")
    return (df.dropna(subset=["belongs_to_collection"])
            .groupby("belongs_to_collection")
            .agg(movie_count=("id", "count"), total_budget=("budget_musd", "sum"),
                 mean_budget=("budget_musd", "mean"), total_revenue=("revenue_musd", "sum"),
                 mean_revenue=("revenue_musd", "mean"), mean_rating=("vote_average", "mean"))
            .sort_values(by="total_revenue", ascending=False).head(5).round(2))


def most_successful_directors(df: pd.DataFrame) -> pd.DataFrame:
    # Find directors with most revenue and best average ratings
    if "director" not in df.columns:
        raise KeyError("'director' column missing for director analysis.")
    return (df.dropna(subset=["director"])
            .groupby("director")
            .agg(movies_directed=("id", "count"), total_revenue=("revenue_musd", "sum"),
                 mean_rating=("vote_average", "mean"))
            .sort_values(by="total_revenue", ascending=False).head(5).round(2))


def advanced_movie_searches(df: pd.DataFrame) -> None:
    # Perform two advanced movie search queries.
    if "cast" not in df.columns or "director" not in df.columns:
        print("\n⚠️ Skipping advanced movie searches (missing 'cast' and/or 'director' columns).")
        return
    
    if "genres" in df.columns:
        sci_fi_action = df[df["genres"].str.contains("Science Fiction", case=False, na=False)
                          & df["genres"].str.contains("Action", case=False, na=False)
                          & df["cast"].str.contains("Bruce Willis", case=False, na=False)
                          ].sort_values(by="vote_average", ascending=False)[["title", "genres", "vote_average"]]
        print("\n🎬 Best-rated Sci-Fi Action movies starring Bruce Willis:")
        print(sci_fi_action if not sci_fi_action.empty else "No results found.")

    uma_tarantino = df[df["cast"].str.contains("Uma Thurman", case=False, na=False)
                      & df["director"].str.contains("Quentin Tarantino", case=False, na=False)
                      ].sort_values(by="runtime", ascending=True)[["title", "runtime", "director"]]
    print("\n🎞️ Movies starring Uma Thurman directed by Quentin Tarantino:")
    print(uma_tarantino if not uma_tarantino.empty else "No results found.")


def print_kpi_results(kpis: dict[str, pd.DataFrame], df: pd.DataFrame) -> None:
    # Print KPI results and additional analysis tables.
    for name, table in kpis.items():
        print(f"\n📊 {name}")
        print(table.to_string(index=False))

    if "belongs_to_collection" in df.columns:
        print("\n🎬 Franchise vs Standalone Performance:")
        print(franchise_vs_standalone(df))
        print("\n🏅 Most Successful Franchises:")
        print(most_successful_franchises(df))
    else:
        print("\n⚠️ Skipping franchise-related analysis (missing column).")

    if "director" in df.columns:
        print("\n🎥 Most Successful Directors:")
        print(most_successful_directors(df))
    else:
        print("\n⚠️ Skipping director analysis (missing column).")
