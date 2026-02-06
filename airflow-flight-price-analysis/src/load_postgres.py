import psycopg2

def load_to_postgres(df, table):
    conn = psycopg2.connect(
        dbname="flight_analytics",
        user="postgres",
        host="localhost"
    )

    cur = conn.cursor()
    cur.execute(f"TRUNCATE TABLE {table}")

    for _, row in df.iterrows():
        placeholders = ",".join(["%s"] * len(row))
        cur.execute(
            f"INSERT INTO {table} VALUES ({placeholders})",
            tuple(row)
        )

    conn.commit()
    cur.close()
    conn.close()
