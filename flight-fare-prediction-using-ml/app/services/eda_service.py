import logging
import os
import pandas as pd
import numpy as np
from app.ml.cleaner import run_cleaning_pipeline
from app.config import settings
from app.core.exceptions import DataNotFoundError

logger = logging.getLogger(__name__)


class EDAService:

    def _load(self) -> pd.DataFrame:
       if not os.path.exists(settings.DATA_PATH):
        raise DataNotFoundError(f"Dataset not found at: {settings.DATA_PATH}")
       df = run_cleaning_pipeline(settings.DATA_PATH)

       if "departure_dt" in df.columns:
        df["departure_dt"] = pd.to_datetime(df["departure_dt"], errors="coerce")
        df["month"]        = df["departure_dt"].dt.month
        df["weekday"]      = df["departure_dt"].dt.weekday
        df["season"]       = df["month"].apply(self._assign_season)
        df.drop(columns=["departure_dt", "arrival_dt"], errors="ignore", inplace=True)

       return df

    def get_descriptive_stats(self) -> dict:
        df = self._load()
        numeric_df = df.select_dtypes(include=[np.number])
        return {
            "stats": numeric_df.describe().round(2).to_dict(),
            "skewness": numeric_df.skew().round(4).to_dict(),
            "kurtosis": numeric_df.kurt().round(4).to_dict(),
        }

    def get_fare_distribution(self) -> dict:
        df = self._load()
        if "total_fare" not in df.columns:
            raise ValueError("Column 'total_fare' not found.")

        fare = df["total_fare"]
        return {
            "min": round(float(fare.min()), 2),
            "max": round(float(fare.max()), 2),
            "mean": round(float(fare.mean()), 2),
            "median": round(float(fare.median()), 2),
            "std": round(float(fare.std()), 2),
            "histogram": self._histogram(fare),
        }

    def get_kpis(self) -> dict:
        df = self._load()

        kpis = {}

        if "total_fare" in df.columns and "airline" in df.columns:
            kpis["average_fare_by_airline"] = (
                df.groupby("airline")["total_fare"]
                .mean()
                .round(2)
                .sort_values(ascending=False)
                .to_dict()
            )

        if "source" in df.columns and "destination" in df.columns:
            df["route"] = df["source"] + " → " + df["destination"]
            kpis["most_popular_routes"] = (
                df["route"]
                .value_counts()
                .head(5)
                .to_dict()
            )
            if "total_fare" in df.columns:
                kpis["top_5_expensive_routes"] = (
                    df.groupby("route")["total_fare"]
                    .mean()
                    .round(2)
                    .sort_values(ascending=False)
                    .head(5)
                    .to_dict()
                )

        if "season" in df.columns and "total_fare" in df.columns:
            kpis["average_fare_by_season"] = (
                df.groupby("season")["total_fare"]
                .mean()
                .round(2)
                .to_dict()
            )

        if "month" in df.columns and "total_fare" in df.columns:
            kpis["average_fare_by_month"] = (
                df.groupby("month")["total_fare"]
                .mean()
                .round(2)
                .to_dict()
            )

        return kpis

    def get_correlation(self) -> dict:
        df = self._load()
        numeric_df = df.select_dtypes(include=[np.number])
        corr = numeric_df.corr().round(4)
        return corr.to_dict()

    def get_fare_by_airline(self) -> dict:
        df = self._load()
        if "airline" not in df.columns or "total_fare" not in df.columns:
            raise ValueError("Required columns missing.")

        grouped = df.groupby("airline")["total_fare"].agg(
            mean="mean",
            median="median",
            min="min",
            max="max",
            count="count",
        ).round(2)

        return grouped.to_dict(orient="index")

    def get_fare_by_season(self) -> dict:
        df = self._load()

        if "season" not in df.columns:
            if "month" in df.columns:
                df["season"] = df["month"].apply(self._assign_season)
            else:
                raise ValueError("No season or month column found.")

        grouped = df.groupby("season")["total_fare"].agg(
            mean="mean",
            median="median",
            min="min",
            max="max",
        ).round(2)

        return grouped.to_dict(orient="index")

    def get_fare_by_route(self) -> dict:
        df = self._load()
        if "source" not in df.columns or "destination" not in df.columns:
            raise ValueError("Source or destination column missing.")

        df["route"] = df["source"] + " → " + df["destination"]
        grouped = df.groupby("route")["total_fare"].agg(
            mean="mean",
            count="count",
        ).round(2).sort_values("mean", ascending=False)

        return grouped.head(10).to_dict(orient="index")

    def get_monthly_trend(self) -> dict:
        df = self._load()
        if "month" not in df.columns or "total_fare" not in df.columns:
            raise ValueError("Month or total_fare column missing.")

        trend = (
            df.groupby("month")["total_fare"]
            .mean()
            .round(2)
            .to_dict()
        )
        return {"monthly_average_fare": trend}

    def _histogram(self, series: pd.Series, bins: int = 10) -> list[dict]:
        counts, edges = np.histogram(series.dropna(), bins=bins)
        return [
            {
                "bin_start": round(float(edges[i]), 2),
                "bin_end": round(float(edges[i + 1]), 2),
                "count": int(counts[i]),
            }
            for i in range(len(counts))
        ]

    def _assign_season(self, month: int) -> str:
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        return "autumn"