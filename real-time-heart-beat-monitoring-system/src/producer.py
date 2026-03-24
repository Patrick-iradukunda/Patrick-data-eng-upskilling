import argparse
import logging
import signal
import sys
from typing import Optional

from confluent_kafka import Producer, KafkaException

from config import KAFKA, GENERATOR
from generator import HeartbeatGenerator, HeartbeatReading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("producer")

_running = True


def _delivery_report(err, msg):
    if err:
        logger.error("Delivery failed for %s: %s", msg.key(), err)
    else:
        logger.debug("Delivered %s to %s [%d] @ offset %d", msg.key(), msg.topic(), msg.partition(), msg.offset())


def _shutdown(signum, frame):
    global _running
    logger.info("Shutdown signal received — draining and exiting.")
    _running = False


def run(count: Optional[int] = None, interval: float = GENERATOR.interval_seconds):
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    producer = Producer({"bootstrap.servers": KAFKA.bootstrap_servers})
    gen = HeartbeatGenerator()

    logger.info("Producer started — topic=%s, servers=%s", KAFKA.topic, KAFKA.bootstrap_servers)

    emitted = 0
    try:
        for reading in gen.stream(interval=interval, count=count):
            if not _running:
                break

            producer.produce(
                topic=KAFKA.topic,
                key=reading.customer_id,
                value=reading.to_json(),
                callback=_delivery_report,
            )
            producer.poll(0)
            emitted += 1

            status = reading.classify()
            if status != "NORMAL":
                logger.warning("ANOMALY — %s | %d bpm | %s", reading.customer_id, reading.heart_rate, status)
            else:
                logger.info("Sent — %s | %d bpm | %s", reading.customer_id, reading.heart_rate, status)

    except KafkaException as exc:
        logger.exception("Kafka error: %s", exc)
        sys.exit(1)
    finally:
        logger.info("Flushing remaining messages (%d produced total).", emitted)
        producer.flush()


def _cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=None)
    parser.add_argument("--interval", type=float, default=GENERATOR.interval_seconds)
    args = parser.parse_args()
    run(count=args.count, interval=args.interval)


if __name__ == "__main__":
    _cli()
