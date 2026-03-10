import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)


def extract_date_features(df: pd.DataFrame) -> pd.DataFrame:
    date_col = next((c for c in df.columns if "departure_dt" in c), None)
    if not date_col:
        logger.warning("No date column found. Skipping date feature extraction.")
        return df

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["month"]   = df[date_col].dt.month
    df["day"]     = df[date_col].dt.day
    df["weekday"] = df[date_col].dt.weekday
    df["hour"]    = df[date_col].dt.hour

    if "arrival_dt" in df.columns:
        df["arrival_dt"] = pd.to_datetime(df["arrival_dt"], errors="coerce")
        df["flight_duration_min"] = (
            (df["arrival_dt"] - df[date_col])
            .dt.total_seconds()
            .div(60)
            .round(2)
        )

    logger.info("Extracted date features: month, day, weekday, hour, flight_duration_min.")
    return df


def drop_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    datetime_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64"]).columns.tolist()
    if datetime_cols:
        df.drop(columns=datetime_cols, inplace=True)
        logger.info(f"Dropped datetime columns: {datetime_cols}")
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if not cat_cols:
        return df
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    logger.info(f"One-hot encoded columns: {cat_cols}")
    return df


def split_data(df: pd.DataFrame, target: str = "total_fare", test_size: float = 0.2):
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in DataFrame.")

    X = df.drop(columns=[target])
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    logger.info(f"Split data — Train: {X_train.shape}, Test: {X_test.shape}")
    return X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)
    logger.info("Applied StandardScaler to features.")
    return X_train_scaled, X_test_scaled, scaler


def run_feature_pipeline(df: pd.DataFrame):
    df = extract_date_features(df)
    df = drop_datetime_columns(df)
    df = encode_categoricals(df)

    feature_columns = [c for c in df.columns if c != "total_fare"]

    X_train, X_test, y_train, y_test = split_data(df)
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)

    logger.info("Feature pipeline complete.")
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_columns