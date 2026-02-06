CREATE TABLE IF NOT EXISTS flight_prices_raw (
    airline TEXT,
    source_city TEXT,
    destination_city TEXT,
    departure_time TEXT,
    stops TEXT,
    arrival_time TEXT,
    class TEXT,
    duration FLOAT,
    days_left INT,
    price INT
);
