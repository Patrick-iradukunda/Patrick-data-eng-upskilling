import random
import time
import json
import argparse
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional, Iterator

from config import CUSTOMERS, GENERATOR, HEART_RATE_LOW, HEART_RATE_HIGH, HEART_RATE_CRITICAL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("generator")


@dataclass
class HeartbeatReading:
    customer_id: str
    timestamp: str
    heart_rate: int

    def classify(self) -> str:
        if self.heart_rate >= HEART_RATE_CRITICAL:
            return "CRITICAL"
        if self.heart_rate >= HEART_RATE_HIGH:
            return "HIGH"
        if self.heart_rate <= HEART_RATE_LOW:
            return "LOW"
        return "NORMAL"

    def to_json(self) -> str:
        return json.dumps(asdict(self))


class _CustomerState:
    def __init__(self, customer_id: str, base_rate: int):
        self.customer_id = customer_id
        self.base_rate = base_rate
        self._current = float(base_rate) + random.uniform(-5, 5)
        self._drift = random.choice([-1, 1]) * random.uniform(0.2, 0.8)
        self._drift_ttl = random.randint(10, 30)

    def next_reading(self) -> HeartbeatReading:
        roll = random.random()
        if roll < GENERATOR.anomaly_spike_probability:
            self._current += random.uniform(40, 80)
        elif roll < GENERATOR.anomaly_spike_probability + GENERATOR.anomaly_dip_probability:
            self._current -= random.uniform(20, 35)
        else:
            self._current += self._drift + random.gauss(0, 1.5)

        self._current += (self.base_rate - self._current) * 0.05
        self._current = max(20.0, min(220.0, self._current))

        self._drift_ttl -= 1
        if self._drift_ttl <= 0:
            self._drift = random.choice([-1, 1]) * random.uniform(0.2, 0.8)
            self._drift_ttl = random.randint(10, 30)

        return HeartbeatReading(
            customer_id=self.customer_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            heart_rate=round(self._current),
        )


class HeartbeatGenerator:
    def __init__(self):
        self._states = {
            c["customer_id"]: _CustomerState(c["customer_id"], c["base_rate"])
            for c in CUSTOMERS
        }

    def next(self) -> HeartbeatReading:
        customer_id = random.choice(list(self._states))
        return self._states[customer_id].next_reading()

    def stream(
        self,
        interval: float = GENERATOR.interval_seconds,
        count: Optional[int] = None,
    ) -> Iterator[HeartbeatReading]:
        emitted = 0
        while count is None or emitted < count:
            yield self.next()
            emitted += 1
            time.sleep(interval)


def _cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=None)
    parser.add_argument("--interval", type=float, default=GENERATOR.interval_seconds)
    args = parser.parse_args()

    gen = HeartbeatGenerator()
    for reading in gen.stream(interval=args.interval, count=args.count):
        status = reading.classify()
        logger.info("%s | %s bpm | %s", reading.customer_id, reading.heart_rate, status)


if __name__ == "__main__":
    _cli()
