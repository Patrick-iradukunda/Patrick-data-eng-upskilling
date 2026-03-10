import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def load_raw_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        logger.info(f"Dataset loaded successfully. Shape: {df.shape}")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset not found at path: {path}")


def drop_irrelevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    before = df.shape[1]
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df = df.loc[:, ~df.columns.duplicated()]
    df.dropna(axis=1, how="all", inplace=True)
    logger.info(f"Dropped {before - df.shape[1]} irrelevant/duplicate columns.")
    return df


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[\s&/\-\(\)]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    rename_map = {
        "base_fare_bdt":       "base_fare",
        "tax_surcharge_bdt":   "tax_surcharge",
        "total_fare_bdt":      "total_fare",
        "departure_date_time": "departure_dt",
        "arrival_date_time":   "arrival_dt",
        "duration_hrs":        "duration",
        "tax___surcharge":     "tax_surcharge",
        "airline_name":        "airline",
        "flight_date":         "date",
        "departure_city":      "source",
        "arrival_city":        "destination",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
    logger.info(f"Normalized column names: {list(df.columns)}")
    return df


def fix_data_types(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["base_fare", "tax_surcharge", "total_fare", "duration", "days_before_departure"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            logger.info(f"Converted '{col}' to numeric.")

    for col in ["departure_dt", "arrival_dt", "date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            logger.info(f"Converted '{col}' to datetime.")

    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    threshold = len(df.columns) * 0.5
    before = len(df)
    df.dropna(thresh=threshold, inplace=True)
    logger.info(f"Dropped {before - len(df)} rows with >50% missing values.")

    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        median_val = df[col].median()
        missing = df[col].isnull().sum()
        if missing > 0:
            df[col].fillna(median_val, inplace=True)
            logger.info(f"Imputed {missing} missing values in '{col}' with median ({median_val:.2f}).")

    cat_cols = df.select_dtypes(include=["object"]).columns
    for col in cat_cols:
        mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
        missing = df[col].isnull().sum()
        if missing > 0:
            df[col].fillna(mode_val, inplace=True)
            logger.info(f"Imputed {missing} missing values in '{col}' with mode ('{mode_val}').")

    return df


def remove_invalid_entries(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    for col in ["base_fare", "total_fare", "tax_surcharge"]:
        if col in df.columns:
            df = df[df[col] >= 0]
    if "base_fare" in df.columns and "total_fare" in df.columns:
        df = df[df["base_fare"] <= df["total_fare"]]
    logger.info(f"Removed {before - len(df)} invalid entries.")
    return df


def normalize_categorical_values(df: pd.DataFrame) -> pd.DataFrame:
    city_map = {
        "dacca":       "Dhaka",
        "dhaka":       "Dhaka",
        "chittagong":  "Chittagong",
        "ctg":         "Chittagong",
        "sylhet":      "Sylhet",
        "zyl":         "Sylhet",
        "cox's bazar": "Cox's Bazar",
        "cox bazar":   "Cox's Bazar",
        "jessore":     "Jessore",
        "rajshahi":    "Rajshahi",
    }
    for col in ["source", "destination"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.lower().map(
                lambda x: city_map.get(x, x.title())
            )
            logger.info(f"Normalized city names in '{col}'.")

    if "airline" in df.columns:
        df["airline"] = df["airline"].str.strip().str.title()
        logger.info("Normalized airline names.")

    return df


def derive_total_fare(df: pd.DataFrame) -> pd.DataFrame:
    if "total_fare" not in df.columns:
        if "base_fare" in df.columns and "tax_surcharge" in df.columns:
            df["total_fare"] = df["base_fare"] + df["tax_surcharge"]
            logger.info("Derived 'total_fare' from base_fare + tax_surcharge.")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df.drop_duplicates(inplace=True)
    logger.info(f"Removed {before - len(df)} duplicate rows.")
    return df


def run_cleaning_pipeline(path: str) -> pd.DataFrame:
    logger.info("Starting Data Cleaning Pipeline...")
    df = load_raw_data(path)
    df = drop_irrelevant_columns(df)
    df = normalize_column_names(df)
    df = fix_data_types(df)
    df = derive_total_fare(df)
    df = handle_missing_values(df)
    df = remove_invalid_entries(df)
    df = normalize_categorical_values(df)
    df = remove_duplicates(df)
    logger.info(f"Cleaning complete. Final shape: {df.shape}")
    return df