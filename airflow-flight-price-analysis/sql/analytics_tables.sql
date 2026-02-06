
CREATE DATABASE flight_analytics;

\c flight_analytics;

CREATE TABLE IF NOT EXISTS airline_kpis (
    airline VARCHAR(100),
    avg_fare DECIMAL(10,2),
    booking_count INT
);

CREATE TABLE IF NOT EXISTS seasonal_fares (
    season VARCHAR(20),
    avg_fare DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS popular_routes (
    source VARCHAR(100),
    destination VARCHAR(100),
    booking_count INT
);
