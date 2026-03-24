import sys
import os
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from generator import HeartbeatGenerator, HeartbeatReading
from consumer import _classify, _validate
from config import HEART_RATE_LOW, HEART_RATE_HIGH, HEART_RATE_CRITICAL


class TestHeartbeatReading(unittest.TestCase):
    def _make(self, bpm: int) -> HeartbeatReading:
        return HeartbeatReading(
            customer_id="CUST_001",
            timestamp="2024-01-01T00:00:00+00:00",
            heart_rate=bpm,
        )

    def test_classify_normal(self):
        self.assertEqual(self._make(75).classify(), "NORMAL")

    def test_classify_high(self):
        self.assertEqual(self._make(HEART_RATE_HIGH + 1).classify(), "HIGH")

    def test_classify_low(self):
        self.assertEqual(self._make(HEART_RATE_LOW - 1).classify(), "LOW")

    def test_classify_critical(self):
        self.assertEqual(self._make(HEART_RATE_CRITICAL + 1).classify(), "CRITICAL")

    def test_to_json_roundtrip(self):
        reading = self._make(72)
        payload = json.loads(reading.to_json())
        self.assertEqual(payload["customer_id"], "CUST_001")
        self.assertEqual(payload["heart_rate"], 72)


class TestGenerator(unittest.TestCase):
    def test_stream_count(self):
        gen = HeartbeatGenerator()
        readings = list(gen.stream(interval=0, count=20))
        self.assertEqual(len(readings), 20)

    def test_all_readings_have_valid_fields(self):
        gen = HeartbeatGenerator()
        for reading in gen.stream(interval=0, count=50):
            self.assertIsInstance(reading.customer_id, str)
            self.assertIsInstance(reading.heart_rate, int)
            self.assertTrue(20 <= reading.heart_rate <= 220)
            self.assertIn("T", reading.timestamp)

    def test_multiple_customers_covered(self):
        gen = HeartbeatGenerator()
        ids = {r.customer_id for r in gen.stream(interval=0, count=200)}
        self.assertGreater(len(ids), 1)


class TestClassify(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(_classify(HEART_RATE_LOW - 1), "LOW")
        self.assertEqual(_classify(HEART_RATE_LOW), "LOW")
        self.assertEqual(_classify(HEART_RATE_LOW + 1), "NORMAL")
        self.assertEqual(_classify(HEART_RATE_HIGH - 1), "NORMAL")
        self.assertEqual(_classify(HEART_RATE_HIGH), "HIGH")
        self.assertEqual(_classify(HEART_RATE_CRITICAL), "CRITICAL")


class TestValidate(unittest.TestCase):
    def _valid_payload(self, bpm=72):
        return {"customer_id": "CUST_001", "timestamp": "2024-01-01T00:00:00+00:00", "heart_rate": bpm}

    def test_valid_payload_passes(self):
        result = _validate(self._valid_payload())
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "NORMAL")

    def test_missing_field_returns_none(self):
        self.assertIsNone(_validate({"customer_id": "CUST_001", "heart_rate": 72}))

    def test_out_of_range_returns_none(self):
        self.assertIsNone(_validate(self._valid_payload(bpm=0)))
        self.assertIsNone(_validate(self._valid_payload(bpm=300)))

    def test_non_integer_heart_rate_returns_none(self):
        payload = self._valid_payload()
        payload["heart_rate"] = "fast"
        self.assertIsNone(_validate(payload))

    def test_anomaly_status_propagated(self):
        result = _validate(self._valid_payload(bpm=HEART_RATE_CRITICAL + 5))
        self.assertEqual(result["status"], "CRITICAL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
