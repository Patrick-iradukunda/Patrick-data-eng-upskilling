def transform_data(df):
    df = df.copy()

    df["price"] = df["price"].astype(float)
    df["duration"] = df["duration"].astype(float)

    return df
