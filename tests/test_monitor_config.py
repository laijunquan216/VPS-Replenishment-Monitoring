import json
import tempfile
import unittest
from pathlib import Path

from app.monitor import MonitorService


class MonitorConfigTests(unittest.TestCase):
    def test_save_config_round_trip(self):
        config = {
            "interval_seconds": 30,
            "smtp": {"enabled": False},
            "rules": [
                {
                    "site_name": "TestSite",
                    "url": "https://example.com",
                    "product_name": "PlanA",
                    "product_anchor": "PlanA",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.json"
            p.write_text(json.dumps(config), encoding="utf-8")
            monitor = MonitorService(str(p))

            new_config = {
                "interval_seconds": 45,
                "smtp": {"enabled": False},
                "rules": [
                    {
                        "site_name": "TestSite2",
                        "url": "https://example.org",
                        "product_name": "PlanB",
                        "product_anchor": "PlanB",
                    }
                ],
            }
            monitor.save_config(new_config)
            loaded = json.loads(p.read_text(encoding="utf-8"))
            self.assertEqual(45, monitor.interval_seconds)
            self.assertEqual(new_config["rules"][0]["product_name"], loaded["rules"][0]["product_name"])

    def test_invalid_interval_raises(self):
        config = {
            "interval_seconds": 30,
            "smtp": {"enabled": False},
            "rules": [
                {
                    "site_name": "TestSite",
                    "url": "https://example.com",
                    "product_name": "PlanA",
                    "product_anchor": "PlanA",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.json"
            p.write_text(json.dumps(config), encoding="utf-8")
            monitor = MonitorService(str(p))
            with self.assertRaises(ValueError):
                monitor.save_config({**config, "interval_seconds": 0})


if __name__ == "__main__":
    unittest.main()
