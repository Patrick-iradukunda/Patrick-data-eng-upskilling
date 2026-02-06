import mysql.connector

def load_to_mysql(df):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="flight_staging"
    )

    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE flight_prices_raw")

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO flight_prices_raw VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            tuple(row)
        )

    conn.commit()
    cursor.close()
    conn.close()
