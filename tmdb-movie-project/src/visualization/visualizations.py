import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Optional


def _setup_plot_style() -> None:
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9


def _save_plot(fig: plt.Figure, filename: str, output_dir: Optional[Path] = None) -> None:
    if output_dir is None:
        output_dir = Path(__file__).resolve().parents[2] / "data" / "visualizations"
    output_dir.mkdir(exist_ok=True, parents=True)
    output_path = output_dir / filename
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f" Saved visualization: {output_path}")


def plot_revenue_vs_budget(df: pd.DataFrame) -> None:
    _setup_plot_style()
    plot_df = df.dropna(subset=['budget_musd', 'revenue_musd'])
    
    if plot_df.empty:
        print(" No data available for Revenue vs Budget plot.")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(plot_df['budget_musd'], plot_df['revenue_musd'], 
               alpha=0.6, s=50, c='#3498db', edgecolors='white', linewidth=0.5)
    
    if len(plot_df) > 1:
        z = np.polyfit(plot_df['budget_musd'], plot_df['revenue_musd'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(plot_df['budget_musd'].min(), 
                             plot_df['budget_musd'].max(), 100)
        ax.plot(x_trend, p(x_trend), 'r--', alpha=0.8, linewidth=2, 
                label=f'Trend: y={z[0]:.2f}x+{z[1]:.2f}')
    
    max_val = max(plot_df['budget_musd'].max(), plot_df['revenue_musd'].max())
    ax.plot([0, max_val], [0, max_val], 'g:', alpha=0.5, linewidth=1.5, 
            label='Break-even line')
    
    ax.set_xlabel('Budget (Million USD)', fontweight='bold')
    ax.set_ylabel('Revenue (Million USD)', fontweight='bold')
    ax.set_title('Revenue vs. Budget Analysis', fontweight='bold', pad=20)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    _save_plot(fig, 'revenue_vs_budget.png')
    plt.close(fig)


def plot_roi_by_genre(df: pd.DataFrame) -> None:
    _setup_plot_style()
    plot_df = df.dropna(subset=['roi', 'genres']).copy()
    
    if plot_df.empty:
        print(" No data available for ROI by Genre plot.")
        return
    
    plot_df['genre_list'] = plot_df['genres'].str.split(' | ')
    exploded_df = plot_df.explode('genre_list')
    top_genres = exploded_df['genre_list'].value_counts().head(8).index.tolist()
    genre_df = exploded_df[exploded_df['genre_list'].isin(top_genres)]
    
    if genre_df.empty:
        print(" Insufficient genre data for visualization.")
        return
    
    genre_data = [genre_df[genre_df['genre_list'] == genre]['roi'].values 
                  for genre in top_genres]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bp = ax.boxplot(genre_data, labels=top_genres, patch_artist=True,
                    medianprops=dict(color='red', linewidth=2),
                    boxprops=dict(facecolor='#3498db', alpha=0.7),
                    whiskerprops=dict(linewidth=1.5),
                    capprops=dict(linewidth=1.5))
    
    ax.set_xlabel('Genre', fontweight='bold')
    ax.set_ylabel('ROI (Return on Investment)', fontweight='bold')
    ax.set_title('ROI Distribution by Genre (Top 8 Genres)', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    plt.xticks(rotation=45, ha='right')
    
    _save_plot(fig, 'roi_by_genre.png')
    plt.close(fig)


def plot_popularity_vs_rating(df: pd.DataFrame) -> None:
    _setup_plot_style()
    plot_df = df.dropna(subset=['popularity', 'vote_average'])
    
    if plot_df.empty:
        print(" No data available for Popularity vs Rating plot.")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(plot_df['vote_average'], plot_df['popularity'], 
                        c=plot_df['vote_count'], cmap='viridis', 
                        alpha=0.6, s=50, edgecolors='white', linewidth=0.5)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Vote Count', rotation=270, labelpad=20, fontweight='bold')
    
    ax.set_xlabel('Average Rating', fontweight='bold')
    ax.set_ylabel('Popularity Score', fontweight='bold')
    ax.set_title('Popularity vs. Rating Analysis', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    _save_plot(fig, 'popularity_vs_rating.png')
    plt.close(fig)


def plot_yearly_box_office_trends(df: pd.DataFrame) -> None:
    _setup_plot_style()
    df_copy = df.copy()
    df_copy['year'] = pd.to_datetime(df_copy['release_date'], errors='coerce').dt.year
    plot_df = df_copy.dropna(subset=['year', 'revenue_musd', 'budget_musd'])
    
    if plot_df.empty:
        print(" No data available for Yearly Trends plot.")
        return
    
    yearly_stats = plot_df.groupby('year').agg({
        'revenue_musd': 'mean',
        'budget_musd': 'mean',
        'id': 'count'
    }).rename(columns={'id': 'movie_count'})
    
    yearly_stats = yearly_stats[yearly_stats['movie_count'] >= 2]
    
    if yearly_stats.empty:
        print(" Insufficient data for yearly trends.")
        return
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(yearly_stats.index, yearly_stats['revenue_musd'], 
            marker='o', linewidth=2, color='#2ecc71', label='Avg Revenue')
    ax1.plot(yearly_stats.index, yearly_stats['budget_musd'], 
            marker='s', linewidth=2, color='#e74c3c', label='Avg Budget')
    
    ax1.set_xlabel('Year', fontweight='bold')
    ax1.set_ylabel('Amount (Million USD)', fontweight='bold')
    ax1.set_title('Yearly Box Office Performance Trends', fontweight='bold', pad=20)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    ax2 = ax1.twinx()
    ax2.bar(yearly_stats.index, yearly_stats['movie_count'], 
           alpha=0.3, color='gray', label='Movie Count')
    ax2.set_ylabel('Number of Movies', fontweight='bold')
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    _save_plot(fig, 'yearly_trends.png')
    plt.close(fig)


def plot_franchise_vs_standalone(df: pd.DataFrame) -> None:
    _setup_plot_style()
    
    if 'belongs_to_collection' not in df.columns:
        print(" 'belongs_to_collection' column missing. Skipping franchise analysis.")
        return
    
    df_copy = df.copy()
    df_copy['is_franchise'] = df_copy['belongs_to_collection'].apply(
        lambda x: 'Franchise' if pd.notna(x) and x != '' else 'Standalone'
    )
    
    comparison = df_copy.groupby('is_franchise').agg({
        'revenue_musd': 'mean',
        'budget_musd': 'mean',
        'roi': 'median',
        'vote_average': 'mean'
    }).round(2)
    
    if comparison.empty or len(comparison) < 2:
        print(" Insufficient data for franchise comparison.")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Franchise vs. Standalone Movies Comparison', 
                fontweight='bold', fontsize=14, y=0.995)
    
    metrics = [
        ('revenue_musd', 'Average Revenue (Million USD)', '#2ecc71'),
        ('budget_musd', 'Average Budget (Million USD)', '#e74c3c'),
        ('roi', 'Median ROI', '#3498db'),
        ('vote_average', 'Average Rating', '#f39c12')
    ]
    
    for idx, (metric, title, color) in enumerate(metrics):
        ax = axes[idx // 2, idx % 2]
        categories = comparison.index.tolist()
        values = comparison[metric].values
        
        bars = ax.bar(categories, values, color=color, alpha=0.7, edgecolor='white', linewidth=2)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel(title, fontweight='bold')
        ax.set_title(title, fontweight='bold', pad=10)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    _save_plot(fig, 'franchise_vs_standalone.png')
    plt.close(fig)


def generate_all_visualizations(df: pd.DataFrame) -> None:
    print("\n Generating Data Visualizations...")
    print("=" * 60)
    
    output_dir = Path(__file__).resolve().parents[2] / "data" / "visualizations"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    plot_revenue_vs_budget(df)
    plot_roi_by_genre(df)
    plot_popularity_vs_rating(df)
    plot_yearly_box_office_trends(df)
    plot_franchise_vs_standalone(df)
    
    print("=" * 60)
    print(f"✅ All visualizations saved to: {output_dir}")
    print("=" * 60)
