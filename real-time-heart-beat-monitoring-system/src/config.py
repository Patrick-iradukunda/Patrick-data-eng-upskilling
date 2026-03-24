import os
from dataclasses import dataclass


@dataclass(frozen=True)
class KafkaConfig:
    bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic: str = os.getenv("KAFKA_TOPIC", "heartbeat")
    consumer_group: str = os.getenv("KAFKA_CONSUMER_GROUP", "heartbeat-consumer-group")


@dataclass(frozen=True)
class PostgresConfig:
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    db: str = os.getenv("POSTGRES_DB", "heartbeat_db")
    user: str = os.getenv("POSTGRES_USER", "heartbeat_user")
    password: str = os.getenv("POSTGRES_PASSWORD", "heartbeat_pass")

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


@dataclass(frozen=True)
class GeneratorConfig:
    interval_seconds: float = float(os.getenv("GENERATOR_INTERVAL", "0.5"))
    anomaly_spike_probability: float = float(os.getenv("ANOMALY_SPIKE_PROB", "0.02"))
    anomaly_dip_probability: float = float(os.getenv("ANOMALY_DIP_PROB", "0.02"))


KAFKA = KafkaConfig()
POSTGRES = PostgresConfig()
GENERATOR = GeneratorConfig()

HEART_RATE_LOW = 45
HEART_RATE_HIGH = 130
HEART_RATE_CRITICAL = 160

CUSTOMERS = [
    {"customer_id": "CUST_001", "base_rate": 70},
    {"customer_id": "CUST_002", "base_rate": 75},
    {"customer_id": "CUST_003", "base_rate": 65},
    {"customer_id": "CUST_004", "base_rate": 80},
    {"customer_id": "CUST_005", "base_rate": 72},
    {"customer_id": "CUST_006", "base_rate": 68},
    {"customer_id": "CUST_007", "base_rate": 78},
    {"customer_id": "CUST_008", "base_rate": 76},
    {"customer_id": "CUST_009", "base_rate": 62},
    {"customer_id": "CUST_010", "base_rate": 82},
]
