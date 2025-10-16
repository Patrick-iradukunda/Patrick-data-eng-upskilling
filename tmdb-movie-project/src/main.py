from utils.config_loader import load_config
from api.fetch_data import fetch_movie_data
from utils.data_cleaner import load_raw_data, clean_movie_data
from analysis.kpi_analysis import (
    movie_performance_kpis,
    print_kpi_results,
    advanced_movie_searches
)


def main():
    """Main entry point for TMDB movie analysis pipeline."""
    # Step 1 – Load API key & fetch movies
    api_key = load_config()
    movie_ids = [
        299534, 19995, 140607, 299536, 597, 135397,
        420818, 24428, 168259, 99861, 284054, 12445,
        181808, 330457, 351286, 109445, 321612, 260513
    ]

    print("🎬 Fetching movie data...")
    movies = fetch_movie_data(api_key, movie_ids)
    print(f"✅ Fetched {len(movies)} movies.")

    # Step 2 – Load & clean raw data
    print("\n🧹 Cleaning movie data...")
    df_raw = load_raw_data()
    df_cleaned = clean_movie_data(df_raw)
    print(f" Cleaning complete. Final dataset shape: {df_cleaned.shape}")

    # Step 3 – KPI Analysis
    print("\n Performing KPI Analysis...")
    kpis = movie_performance_kpis(df_cleaned)
    print_kpi_results(kpis, df_cleaned)

    
    print("\n Advanced Movie Searches:")
    advanced_movie_searches(df_cleaned)

    print("\n Analysis complete! ")


if __name__ == "__main__":
    main()
