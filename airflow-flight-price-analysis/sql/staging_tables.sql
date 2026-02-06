
DROP TABLE IF EXISTS flight_prices_raw;


CREATE TABLE IF NOT EXISTS flight_prices_raw (
    airline VARCHAR(255),
    source VARCHAR(50),
    source_city VARCHAR(255),
    destination VARCHAR(50),
    destination_city VARCHAR(255),
    departure_time DATETIME,
    arrival_time DATETIME,
    duration VARCHAR(50),
    stops VARCHAR(50),
    class VARCHAR(50),
    base_fare DECIMAL(15,2),
    tax DECIMAL(15,2),
    price DECIMAL(15,2),
    season VARCHAR(50),
    days_left INT,
    PRIMARY KEY (airline, source, destination, departure_time)
);
