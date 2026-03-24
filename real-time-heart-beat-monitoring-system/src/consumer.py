import json
import logging
import signal
import sys
from typing import Optional

import psycopg2
import psycopg2.extras
from confluent_kafka import Consumer, KafkaError, KafkaException

from config import KAFKA, POSTGRES, HEART_RATE_LOW, HEART_RATE_HIGH, HEART_RATE_CRITICAL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("consumer")

_running = True

INSERT_SQL = """
    INSERT INTO heartbeat_readings (customer_id, timestamp, heart_rate, status)
    VALUES (%(customer_id)s, %(timestamp)s, %(heart_rate)s, %(status)s)
"""


def _classify(heart_rate: int) -> str:
    if heart_rate >= HEART_RATE_CRITICAL:
        return "CRITICAL"
    if heart_rate >= HEART_RATE_HIGH:
        return "HIGH"
    if heart_rate <= HEART_RATE_LOW:
        return "LOW"
    return "NORMAL"


def _validate(payload: dict) -> Optional[dict]:
    required = {"customer_id", "timestamp", "heart_rate"}
    if not required.issubset(payload):
        logger.warning("Dropping malformed message — missing fields: %s", required - payload.keys())
        return None

    heart_rate = payload["heart_rate"]
    if not isinstance(heart_rate, int) or not (0 < heart_rate < 300):
        logger.warning("Dropping out-of-range heart rate: %s", heart_rate)
        return None

    return {
        "customer_id": str(payload["customer_id"]),
        "timestamp": str(payload["timestamp"]),
        "heart_rate": heart_rate,
        "status": _classify(heart_rate),
    }


def _connect_db() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(POSTGRES.dsn)
    conn.autocommit = False
    logger.info("Connected to PostgreSQL at %s:%s/%s", POSTGRES.host, POSTGRES.port, POSTGRES.db)
    return conn


def _shutdown(signum, frame):
    global _running
    logger.info("Shutdown signal — stopping consumer loop.")
    _running = False


def run():
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA.bootstrap_servers,
            "group.id": KAFKA.consumer_group,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([KAFKA.topic])

    db = _connect_db()
    cursor = db.cursor()

    logger.info("Consumer started — topic=%s, group=%s", KAFKA.topic, KAFKA.consumer_group)

    processed = 0
    try:
        while _running:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug("Reached end of partition %s/%d", msg.topic(), msg.partition())
                elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    logger.warning("Topic '%s' not yet available — waiting for producer to create it.", KAFKA.topic)
                else:
                    raise KafkaException(msg.error())
                continue

            try:
                raw = json.loads(msg.value().decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                logger.warning("Cannot decode message: %s", exc)
                consumer.commit(msg)
                continue

            record = _validate(raw)
            if record is None:
                consumer.commit(msg)
                continue

            cursor.execute(INSERT_SQL, record)
            db.commit()
            consumer.commit(msg)

            processed += 1
            level = logging.WARNING if record["status"] != "NORMAL" else logging.INFO
            logger.log(level, "Stored — %s | %d bpm | %s", record["customer_id"], record["heart_rate"], record["status"])

    except KafkaException as exc:
        logger.exception("Kafka error: %s", exc)
        sys.exit(1)
    finally:
        logger.info("Shutting down — %d records processed.", processed)
        cursor.close()
        db.close()
        consumer.close()


if __name__ == "__main__":
    run()
